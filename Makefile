.PHONY: install backend frontend test test-api test-manual seed docker

install:
	pip install -r requirements.txt
	cd frontend && npm install

backend:
	PYTHONPATH=. uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd frontend && npm run dev

test:
	PYTHONPATH=. pytest -q

test-api:
	PYTHONPATH=. pytest tests/test_api_integration.py -q

test-manual:
	PYTHONPATH=. python3 scripts/run_manual_checks.py

seed:
	PYTHONPATH=. python3 scripts/seed_demo_client.py

docker:
	docker compose up --build
