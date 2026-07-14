# API Documentation

Base URL: `/api/v1`  
Interactive docs: `/docs` (Swagger UI) · `/redoc`

## Authentication

All planning and client endpoints require:

```
Authorization: Bearer <access_token>
```

### Register

`POST /auth/register`

```json
{ "email": "advisor@firm.com", "password": "SecurePass1", "full_name": "Advisor Name" }
```

### Login

`POST /auth/login`

```json
{ "email": "advisor@firm.com", "password": "SecurePass1" }
```

Response:

```json
{ "access_token": "...", "refresh_token": "...", "token_type": "bearer" }
```

## Clients

| Method | Path | Body |
|--------|------|------|
| GET | `/clients` | — |
| POST | `/clients` | `{ "profile": { ...ClientProfile }, "notes": "" }` |
| GET | `/clients/{id}` | — |
| PUT | `/clients/{id}` | `{ "profile": {...}, "notes": "", "is_active": true }` |
| DELETE | `/clients/{id}` | soft-delete |

`ClientProfile` mirrors the planner form sections: `personal`, `income`, `expenses`, `loans[]`, `assets`, `insurance`, `investments[]`, `goals[]`, `tax`, `risk_profile`, `risk_answers`, `assumptions`.

## Planning

### Preview

`POST /planning/preview` — body: full `ClientProfile` — returns plan JSON without files.

### Generate (one-click)

`POST /planning/generate`

```json
{
  "client_id": "uuid-optional",
  "profile": { },
  "generate_excel": true,
  "generate_pdf": true,
  "generate_charts": true,
  "save": true
}
```

Provide either `client_id` or `profile`.

### What-If

`POST /planning/what-if`

```json
{
  "profile": { },
  "income_change_percent": 10,
  "expense_change_percent": -5,
  "sip_change_absolute": 10000,
  "inflation_override": 0.06,
  "returns_override": 0.12,
  "loan_interest_change_percent": 0,
  "retirement_age_override": 58
}
```

### Risk

- `GET /planning/risk-questionnaire`
- `POST /planning/risk-score` — body: `{ "q1": "c", "q2": "b", ... }`

### Downloads

- `GET /planning/download/excel/{client_id}`
- `GET /planning/download/pdf/{client_id}`

## Configuration Endpoints

- `GET /planning/assumptions`
- `GET /planning/recommendations-config`
