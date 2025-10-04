# API Description

## POST /upload
multipart/form-data: cv (pdf), report (pdf)
→ { "cv_id": "...", "report_id": "..." }

## POST /evaluate
{ "job_title": "Backend Engineer", "cv_id": "...", "report_id": "..." }
→ { "id": "job-uuid", "status": "queued" }

## GET /result/{id}
→ { "id": "job-uuid", "status": "processing|completed|failed", "result": { ... } }