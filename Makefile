run:
	uvicorn app.main:app --reload
up:
	docker compose up -d
down:
	docker compose down
ingest:
	python -m app.rag.ingest
test:
	pytest -q
fmt:
	ruff check --fix . && ruff format .
