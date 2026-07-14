"""Financial plan generation, what-if, risk, and report endpoints."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.schemas import ClientProfileSchema, PlanGenerateRequest, PlanOut, WhatIfRequest
from charts.generator import ChartGenerator
from config.settings import get_settings
from database.models import Client, FinancialPlan, User
from database.session import get_db
from excel_generator.workbook import ExcelReportGenerator
from financial_engine.engine import FinancialPlanningEngine
from financial_engine.models import ClientFinancialProfile
from pdf_generator.report import PDFReportGenerator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/planning", tags=["Planning"])
settings = get_settings()


def _engine() -> FinancialPlanningEngine:
    return FinancialPlanningEngine(config_dir=settings.config_dir)


def _profile_from_request(
    payload: PlanGenerateRequest,
    db: Session,
    current_user: User,
) -> tuple[ClientFinancialProfile, Client | None]:
    client = None
    if payload.client_id:
        client = (
            db.query(Client)
            .filter(Client.id == payload.client_id, Client.advisor_id == current_user.id)
            .first()
        )
        if not client:
            raise HTTPException(status_code=404, detail="Client not found")
        data = client.profile_data
        data["client_id"] = client.id
        return ClientFinancialProfile.from_dict(data), client

    if payload.profile is None:
        raise HTTPException(status_code=400, detail="Provide client_id or profile")
    data = payload.profile.model_dump()
    return ClientFinancialProfile.from_dict(data), None


@router.post("/generate", response_model=PlanOut)
def generate_plan(
    payload: PlanGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """One-click generation: dashboard data + Excel + PDF + charts."""
    engine = _engine()
    profile, client = _profile_from_request(payload, db, current_user)
    plan = engine.generate_plan(profile)
    plan_dict = engine.plan_to_dict(plan)

    excel_path = ""
    pdf_path = ""
    chart_paths: list[str] = []

    report_id = client.id if client else "adhoc"
    out_dir = Path(settings.reports_dir) / report_id
    chart_dir = Path(settings.charts_dir) / report_id
    out_dir.mkdir(parents=True, exist_ok=True)
    chart_dir.mkdir(parents=True, exist_ok=True)

    firm = {
        "name": settings.advisor_firm_name,
        "tagline": settings.advisor_firm_tagline,
        "email": settings.advisor_contact_email,
        "phone": settings.advisor_contact_phone,
    }

    if payload.generate_charts:
        try:
            chart_paths = ChartGenerator(chart_dir).generate_all(plan_dict)
        except Exception as exc:
            logger.exception("Chart generation failed: %s", exc)

    if payload.generate_excel:
        try:
            excel_file = out_dir / "Financial_Plan.xlsx"
            ExcelReportGenerator(firm).generate(plan_dict, profile, excel_file, chart_paths)
            excel_path = str(excel_file)
        except Exception as exc:
            logger.exception("Excel generation failed: %s", exc)

    if payload.generate_pdf:
        try:
            pdf_file = out_dir / "Financial_Plan.pdf"
            PDFReportGenerator(firm).generate(plan_dict, profile, pdf_file, chart_paths)
            pdf_path = str(pdf_file)
        except Exception as exc:
            logger.exception("PDF generation failed: %s", exc)

    plan_record = None
    if payload.save and client:
        version = (
            db.query(FinancialPlan)
            .filter(FinancialPlan.client_id == client.id)
            .count()
            + 1
        )
        plan_record = FinancialPlan(
            client_id=client.id,
            version=version,
            plan_data=plan_dict,
            health_score=plan.health_score.get("score", 0),
            net_worth=plan.net_worth.get("net_worth", 0),
            excel_path=excel_path,
            pdf_path=pdf_path,
            status="final",
        )
        db.add(plan_record)
        # Persist latest profile risk
        client.risk_profile = profile.risk_profile.value
        db.commit()
        db.refresh(plan_record)

    return PlanOut(
        id=plan_record.id if plan_record else None,
        client_id=client.id if client else None,
        plan=plan_dict,
        excel_path=excel_path or None,
        pdf_path=pdf_path or None,
        chart_paths=chart_paths,
    )


@router.post("/preview")
def preview_plan(
    profile: ClientProfileSchema,
    current_user: User = Depends(get_current_user),
):
    """Calculate plan without generating reports."""
    engine = _engine()
    fp = ClientFinancialProfile.from_dict(profile.model_dump())
    plan = engine.generate_plan(fp)
    return engine.plan_to_dict(plan)


@router.post("/what-if")
def what_if(
    payload: WhatIfRequest,
    current_user: User = Depends(get_current_user),
):
    engine = _engine()
    fp = ClientFinancialProfile.from_dict(payload.profile.model_dump())
    plan = engine.what_if(
        fp,
        {
            "income_change_percent": payload.income_change_percent,
            "expense_change_percent": payload.expense_change_percent,
            "sip_change_absolute": payload.sip_change_absolute,
            "inflation_override": payload.inflation_override,
            "returns_override": payload.returns_override,
            "loan_interest_change_percent": payload.loan_interest_change_percent,
            "retirement_age_override": payload.retirement_age_override,
        },
    )
    return engine.plan_to_dict(plan)


@router.get("/risk-questionnaire")
def risk_questionnaire(current_user: User = Depends(get_current_user)):
    return _engine().risk_profiler.get_questionnaire()


@router.post("/risk-score")
def risk_score(
    answers: dict[str, str],
    current_user: User = Depends(get_current_user),
):
    return _engine().risk_profiler.score(answers)


@router.get("/assumptions")
def get_assumptions(current_user: User = Depends(get_current_user)):
    return _engine().assumptions


@router.get("/recommendations-config")
def recommendations_config(current_user: User = Depends(get_current_user)):
    import json
    from pathlib import Path

    path = Path(settings.config_dir) / "investment_recommendations.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@router.get("/plans/{client_id}")
def list_plans(
    client_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = (
        db.query(Client)
        .filter(Client.id == client_id, Client.advisor_id == current_user.id)
        .first()
    )
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    plans = (
        db.query(FinancialPlan)
        .filter(FinancialPlan.client_id == client_id)
        .order_by(FinancialPlan.created_at.desc())
        .all()
    )
    return [
        {
            "id": p.id,
            "version": p.version,
            "health_score": p.health_score,
            "net_worth": p.net_worth,
            "excel_path": p.excel_path,
            "pdf_path": p.pdf_path,
            "status": p.status,
            "created_at": p.created_at,
        }
        for p in plans
    ]


@router.get("/download/excel/{client_id}")
def download_excel(
    client_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = (
        db.query(Client)
        .filter(Client.id == client_id, Client.advisor_id == current_user.id)
        .first()
    )
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    plan = (
        db.query(FinancialPlan)
        .filter(FinancialPlan.client_id == client_id)
        .order_by(FinancialPlan.created_at.desc())
        .first()
    )
    if not plan or not plan.excel_path or not Path(plan.excel_path).exists():
        raise HTTPException(status_code=404, detail="Excel report not found")
    return FileResponse(
        plan.excel_path,
        filename=f"Financial_Plan_{client.full_name.replace(' ', '_')}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.get("/download/pdf/{client_id}")
def download_pdf(
    client_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    client = (
        db.query(Client)
        .filter(Client.id == client_id, Client.advisor_id == current_user.id)
        .first()
    )
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    plan = (
        db.query(FinancialPlan)
        .filter(FinancialPlan.client_id == client_id)
        .order_by(FinancialPlan.created_at.desc())
        .first()
    )
    if not plan or not plan.pdf_path or not Path(plan.pdf_path).exists():
        raise HTTPException(status_code=404, detail="PDF report not found")
    return FileResponse(
        plan.pdf_path,
        filename=f"Financial_Plan_{client.full_name.replace(' ', '_')}.pdf",
        media_type="application/pdf",
    )
