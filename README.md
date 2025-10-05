# CV Project Evaluator API

An AI-powered backend service that automates initial screening of job applications. This system evaluates a candidate's CV and project report against job descriptions and scoring rubrics using LLM chaining and RAG (Retrieval-Augmented Generation).

## Features

- ✅ **Multi-stage LLM Pipeline**: CV evaluation → Project evaluation → Final aggregation
- ✅ **RAG-Enhanced Context**: Vector database retrieval for accurate, context-aware scoring
- ✅ **Async Job Processing**: Non-blocking evaluation with Celery + Redis
- ✅ **Structured Scoring**: Weighted rubric-based scoring (1-5 scale per parameter)
- ✅ **Error Resilience**: Automatic retries with exponential backoff for API failures
- ✅ **Production-Ready**: Docker support, comprehensive logging, database persistence

## Architecture

### Tech Stack
- **Backend**: FastAPI (Python)
- **LLM**: OpenAI GPT-4o-mini with JSON mode
- **Vector DB**: Qdrant (in-memory)
- **Task Queue**: Celery + Redis
- **Database**: SQLAlchemy (SQLite for dev, PostgreSQL for prod)
- **PDF Processing**: PyMuPDF + pdfminer.six

### Evaluation Pipeline

```
1. Parse CV & Project Report (PDF → Text)
2. Initialize RAG (Ingest system docs into vector DB)
3. CV Evaluation (LLM + RAG)
   └─ Scores: Technical Skills, Experience, Achievements, Cultural Fit
4. Project Evaluation (LLM + RAG)
   └─ Scores: Correctness, Code Quality, Resilience, Documentation, Creativity
5. Final Aggregation (LLM)
   └─ Overall Score, Summary, Recommendation
```

## Quickstart

### Prerequisites
- Python 3.10+
- Docker & Docker Compose (optional but recommended)
- OpenAI API key

### Setup

1. **Clone and navigate to the project**
```bash
cd CV-Project-Evaluator-API
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

3. **Option A: Using Docker (Recommended)**
```bash
docker compose up -d
```

4. **Option B: Local Development**
```bash
# Install dependencies
pip install -r requirements.txt

# Start Redis (required for Celery)
# On Windows with WSL: wsl redis-server
# On Mac: brew services start redis
# On Linux: sudo systemctl start redis

# Start Celery worker (in separate terminal)
celery -A app.workers.celery_app worker --loglevel=info

# Start API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. **Access the API**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Running Document Ingestion

Before evaluating candidates, ingest the system documents into the vector database:

```bash
python -m app.rag.ingest
```

This will process:
- Job descriptions from `data/system_docs/job_descriptions/`
- Case study brief from `data/system_docs/case_study_brief.txt`
- Scoring rubrics from `data/system_docs/*_rubric.txt`

## API Endpoints

### 1. Upload Documents
**POST** `/upload`

Upload candidate CV and project report (PDF files).

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "cv=@candidate_cv.pdf" \
  -F "report=@project_report.pdf"
```

**Response:**
```json
{
  "cv_id": "uuid-1",
  "report_id": "uuid-2"
}
```

### 2. Trigger Evaluation
**POST** `/evaluate`

Start asynchronous evaluation process.

```bash
curl -X POST "http://localhost:8000/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Backend Engineer",
    "cv_id": "uuid-1",
    "report_id": "uuid-2"
  }'
```

**Response:**
```json
{
  "id": "job-uuid",
  "status": "queued"
}
```

### 3. Get Results
**GET** `/result/{job_id}`

Retrieve evaluation status and results.

```bash
curl "http://localhost:8000/result/job-uuid"
```

**Response (Processing):**
```json
{
  "id": "job-uuid",
  "status": "processing"
}
```

**Response (Completed):**
```json
{
  "id": "job-uuid",
  "status": "completed",
  "result": {
    "cv_match_rate": 0.82,
    "cv_feedback": "Strong backend skills with solid cloud experience...",
    "project_score": 4.5,
    "project_feedback": "Excellent implementation of LLM chaining and RAG...",
    "overall_score": 4.3,
    "overall_summary": "Strong candidate with excellent technical skills...",
    "recommendation": "strong fit",
    "cv_details": { ... },
    "project_details": { ... }
  }
}
```

## Scoring System

### CV Evaluation (0-1 scale)
- **Technical Skills Match** (40%): Backend, databases, APIs, cloud, AI/LLM
- **Experience Level** (25%): Years and project complexity
- **Relevant Achievements** (20%): Impact and measurable outcomes
- **Cultural Fit** (15%): Communication and learning mindset

### Project Evaluation (1-5 scale)
- **Correctness** (30%): Prompt design, LLM chaining, RAG implementation
- **Code Quality** (25%): Clean, modular, tested
- **Resilience** (20%): Error handling, retries, robustness
- **Documentation** (15%): README clarity, setup instructions
- **Creativity** (10%): Extra features beyond requirements

### Final Score (1-5 scale)
- CV Evaluation: 30% weight
- Project Evaluation: 70% weight

## Configuration

Key environment variables (see `.env.example` for all options):

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4o-mini` |
| `REDIS_URL` | Redis connection URL | `redis://redis:6379/0` |
| `DATABASE_URL` | Database connection URL | `sqlite:///./app.db` |
| `UPLOAD_DIR` | Directory for uploaded files | `./data/uploads` |

## Development

### Project Structure
```
app/
├── api/           # API routes and schemas
├── llm/           # LLM client and evaluation logic
├── rag/           # Vector DB and retrieval
├── services/      # Business logic
├── persistence/   # Database models and repository
├── workers/       # Celery tasks
└── utils/         # Helper functions

data/
├── system_docs/   # Reference documents for RAG
└── uploads/       # Uploaded candidate files
```

### Running Tests
```bash
pytest tests/
```

### Ingestion Script
```bash
# Re-ingest documents (useful after updating reference docs)
python -m app.rag.ingest
```

## Error Handling

The system implements robust error handling:

1. **LLM API Failures**: Automatic retries with exponential backoff (3 attempts)
2. **Temperature Control**: Low temperature (0.3) for consistent scoring
3. **JSON Validation**: Structured output mode ensures valid responses
4. **Timeout Handling**: Graceful degradation on API timeouts
5. **Rate Limiting**: Automatic backoff on rate limit errors

## Trade-offs & Design Decisions

### 1. In-Memory Vector DB
- ✅ **Pro**: Fast, no external dependencies, easy setup
- ❌ **Con**: Data lost on restart (requires re-ingestion)
- 📝 **Note**: For production, consider persistent Qdrant or Pinecone

### 2. SQLite Database
- ✅ **Pro**: Zero configuration, perfect for development
- ❌ **Con**: Limited concurrency
- 📝 **Note**: Switch to PostgreSQL for production

### 3. Synchronous RAG Initialization
- ✅ **Pro**: Ensures documents are ready before evaluation
- ❌ **Con**: First evaluation takes longer
- 📝 **Note**: Could be moved to startup or background task

### 4. OpenAI API
- ✅ **Pro**: High-quality, reliable, supports JSON mode
- ❌ **Con**: Costs money, external dependency
- 📝 **Note**: Could support alternative providers (Anthropic, Groq)

## Troubleshooting

**Problem**: `LLM client not available`  
**Solution**: Ensure `OPENAI_API_KEY` is set in `.env`

**Problem**: `Collection not found`  
**Solution**: Run ingestion script: `python -m app.rag.ingest`

**Problem**: Celery worker not processing jobs  
**Solution**: Check Redis is running and `REDIS_URL` is correct

**Problem**: Empty or no evaluation results  
**Solution**: Check logs for API errors, verify PDF files are readable

## License

MIT License - see LICENSE file for details
