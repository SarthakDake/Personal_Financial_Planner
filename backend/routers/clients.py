"""Client CRUD endpoints — multi-client support, no hardcoded data."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.schemas import ClientCreate, ClientOut, ClientUpdate
from database.models import Client, User
from database.session import get_db

router = APIRouter(prefix="/clients", tags=["Clients"])


def _to_out(client: Client) -> ClientOut:
    return ClientOut(
        id=client.id,
        full_name=client.full_name,
        email=client.email,
        phone=client.phone,
        risk_profile=client.risk_profile,
        notes=client.notes,
        profile_data=client.profile_data or {},
        created_at=client.created_at,
        updated_at=client.updated_at,
    )


@router.get("", response_model=list[ClientOut])
def list_clients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    clients = (
        db.query(Client)
        .filter(Client.advisor_id == current_user.id, Client.is_active.is_(True))
        .order_by(Client.updated_at.desc())
        .all()
    )
    return [_to_out(c) for c in clients]


@router.post("", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
def create_client(
    payload: ClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = payload.profile.model_dump()
    client = Client(
        advisor_id=current_user.id,
        full_name=profile["personal"].get("full_name") or "Unnamed Client",
        email=profile["personal"].get("email", ""),
        phone=profile["personal"].get("phone", ""),
        pan=profile["personal"].get("pan", ""),
        profile_data=profile,
        risk_profile=profile.get("risk_profile", "moderate"),
        notes=payload.notes,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return _to_out(client)


@router.get("/{client_id}", response_model=ClientOut)
def get_client(
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
    return _to_out(client)


@router.put("/{client_id}", response_model=ClientOut)
def update_client(
    client_id: str,
    payload: ClientUpdate,
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

    if payload.profile is not None:
        profile = payload.profile.model_dump()
        client.profile_data = profile
        client.full_name = profile["personal"].get("full_name") or client.full_name
        client.email = profile["personal"].get("email", client.email)
        client.phone = profile["personal"].get("phone", client.phone)
        client.pan = profile["personal"].get("pan", client.pan)
        client.risk_profile = profile.get("risk_profile", client.risk_profile)
    if payload.notes is not None:
        client.notes = payload.notes
    if payload.is_active is not None:
        client.is_active = payload.is_active

    db.commit()
    db.refresh(client)
    return _to_out(client)


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
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
    client.is_active = False
    db.commit()
