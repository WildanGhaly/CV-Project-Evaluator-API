# API Description
- **POST** /upload â†’ returns { cv_id, report_id }
- **POST** /evaluate â†’ body { job_title, cv_id, report_id } â†’ { id, status }
- **GET** /result/{id} â†’ { id, status, result? }
