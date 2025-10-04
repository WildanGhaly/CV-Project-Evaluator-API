# cv-project-evaluator-api

FastAPI backend that ingests CV & project PDFs, runs RAG+LLM scoring against job descriptions & rubrics, and exposes async endpoints for upload, evaluate, and results.

## Quickstart
1. \cp .env.example .env\ and fill in values.
2. \docker compose up -d\
3. Open Swagger at \http://localhost:8000/docs\

## Endpoints
- **POST** /upload â€“ upload CV & project report (PDF)
- **POST** /evaluate â€“ trigger async evaluation (returns job id)
- **GET** /result/{id} â€“ poll for status/results
