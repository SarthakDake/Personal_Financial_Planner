FROM python:3.12-slim AS backend

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-postgres.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-postgres.txt

COPY backend ./backend
COPY financial_engine ./financial_engine
COPY excel_generator ./excel_generator
COPY pdf_generator ./pdf_generator
COPY charts ./charts
COPY database ./database
COPY config ./config
COPY utils ./utils
COPY sample_data ./sample_data

RUN mkdir -p data output/reports output/charts

ENV PYTHONPATH=/app
ENV DATABASE_URL=sqlite:///./data/financial_planner.db
ENV REPORTS_DIR=/app/output/reports
ENV CHARTS_DIR=/app/output/charts

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ── Frontend build ────────────────────────────────────────────────────────────
FROM node:22-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

FROM nginx:alpine AS frontend
COPY --from=frontend-build /frontend/dist /usr/share/nginx/html
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
