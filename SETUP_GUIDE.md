# Setup Guide - CV Project Evaluator API

## ✅ What Has Been Implemented

I've completed the full implementation of your CV and Project Evaluator API according to the case study requirements. Here's what's been built:

### 1. System Documents ✅
All reference documents have been created in `data/system_docs/`:
- **Job Description**: `job_descriptions/backend_engineer_2025.txt`
- **Case Study Brief**: `case_study_brief.txt`
- **CV Scoring Rubric**: `cv_scoring_rubric.txt`
- **Project Scoring Rubric**: `project_scoring_rubric.txt`

### 2. LLM Integration ✅
- Complete OpenAI client with retry logic and error handling
- Exponential backoff for API failures (3 attempts)
- Low temperature (0.3) for consistent scoring
- Structured JSON output mode

### 3. RAG System ✅
- Vector database using Qdrant (in-memory)
- Document chunking with overlap for better retrieval
- Semantic search with OpenAI embeddings
- Automatic ingestion on first evaluation

### 4. Evaluation Pipeline ✅
Complete 3-stage LLM chaining:
- **Stage 1**: CV evaluation with weighted scoring (4 parameters)
- **Stage 2**: Project evaluation with weighted scoring (5 parameters)
- **Stage 3**: Final aggregation with overall assessment

### 5. API Endpoints ✅
- `POST /upload` - Upload CV and project report PDFs
- `POST /evaluate` - Trigger async evaluation
- `GET /result/{id}` - Get evaluation status and results
- `GET /health` - Health check

### 6. Error Handling ✅
- Robust retry mechanisms for LLM API failures
- Graceful error messages in results
- Comprehensive logging throughout
- Failed job status tracking

## 🚀 Quick Start Instructions

### Step 1: Set Up Environment

1. Create `.env` file from the example:
```bash
cp .env.example .env
```

2. **IMPORTANT**: Edit `.env` and add your OpenAI API key:
```env
OPENAI_API_KEY=sk-your-actual-api-key-here
```

You can get an API key from: https://platform.openai.com/api-keys

### Step 2: Choose Your Deployment Method

#### Option A: Docker (Recommended)
```bash
docker compose up -d
```

This will start:
- FastAPI application (port 8000)
- Redis (for Celery)
- Celery worker

#### Option B: Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Terminal 1: Start Redis
# Windows: wsl redis-server
# Mac: brew services start redis
# Linux: sudo systemctl start redis

# Terminal 2: Start Celery worker
celery -A app.workers.celery_app worker --loglevel=info

# Terminal 3: Start API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Test the API

1. **Check health endpoint**:
```bash
curl http://localhost:8000/health
```

2. **Upload documents** (replace with your actual CV and report PDFs):
```bash
curl -X POST http://localhost:8000/upload \
  -F "cv=@your_cv.pdf" \
  -F "report=@your_project_report.pdf"
```

This will return:
```json
{
  "cv_id": "some-uuid-1",
  "report_id": "some-uuid-2"
}
```

3. **Trigger evaluation**:
```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Backend Engineer",
    "cv_id": "some-uuid-1",
    "report_id": "some-uuid-2"
  }'
```

This will return:
```json
{
  "id": "job-uuid",
  "status": "queued"
}
```

4. **Check results** (poll this endpoint):
```bash
curl http://localhost:8000/result/job-uuid
```

First few calls will show:
```json
{
  "id": "job-uuid",
  "status": "processing"
}
```

After completion (typically 30-60 seconds):
```json
{
  "id": "job-uuid",
  "status": "completed",
  "result": {
    "cv_match_rate": 0.82,
    "cv_feedback": "...",
    "project_score": 4.5,
    "project_feedback": "...",
    "overall_score": 4.3,
    "overall_summary": "...",
    "recommendation": "strong fit",
    "cv_details": { ... },
    "project_details": { ... }
  }
}
```

## 📝 What You Need to Provide

### Required:
1. **OpenAI API Key** - Add to `.env` file
2. **Your CV** - PDF format
3. **Your Project Report** - PDF format documenting your implementation of this system

### Optional:
If you want to test with different job descriptions, add PDF or TXT files to:
- `data/system_docs/job_descriptions/`

Then re-run ingestion:
```bash
python -m app.rag.ingest
```

## 📊 Understanding the Results

### CV Match Rate (0.00 - 1.00)
Weighted average based on:
- Technical Skills (40%)
- Experience Level (25%)
- Achievements (20%)
- Cultural Fit (15%)

### Project Score (1.00 - 5.00)
Weighted average based on:
- Correctness (30%)
- Code Quality (25%)
- Resilience (20%)
- Documentation (15%)
- Creativity (10%)

### Overall Score (1.00 - 5.00)
- CV: 30% weight
- Project: 70% weight

### Recommendation
- "strong fit" - Score 4.0+
- "moderate fit" - Score 3.0-3.9
- "needs development" - Score 2.0-2.9
- "not recommended" - Score < 2.0

## 🐛 Troubleshooting

### "LLM client not available"
- Ensure `OPENAI_API_KEY` is set in `.env`
- Verify the API key is valid
- Check you have credits in your OpenAI account

### "Collection not found"
- The RAG system will auto-initialize on first evaluation
- If issues persist, manually run: `python -m app.rag.ingest`

### Celery worker not processing
- Check Redis is running: `redis-cli ping` (should return PONG)
- Verify `REDIS_URL` in `.env` is correct
- Check worker logs for errors

### Empty evaluation results
- Check API server logs: `docker compose logs api`
- Verify PDF files are readable
- Try with different/smaller PDF files first

### Rate limit errors
- The system has automatic retry with exponential backoff
- If persistent, you may need to upgrade your OpenAI plan
- Consider reducing concurrency or adding delays

## 📁 Project Structure Reference

```
CV-Project-Evaluator-API/
├── app/
│   ├── api/
│   │   ├── routers/          # API endpoints
│   │   └── schemas/          # Pydantic models
│   ├── llm/
│   │   ├── client.py         # OpenAI client with retry logic
│   │   ├── prompts.py        # Prompt templates
│   │   ├── cv_eval.py        # CV evaluation logic
│   │   ├── project_eval.py   # Project evaluation logic
│   │   └── final_agg.py      # Final aggregation logic
│   ├── rag/
│   │   ├── chunking.py       # Text chunking utilities
│   │   ├── ingest.py         # Document ingestion script
│   │   └── retrieve.py       # Vector search and retrieval
│   ├── services/
│   │   └── evaluation.py     # Main evaluation pipeline
│   ├── persistence/          # Database models and repository
│   └── workers/              # Celery tasks
├── data/
│   ├── system_docs/          # Reference documents (RAG sources)
│   └── uploads/              # Uploaded candidate files
├── .env                      # Your environment configuration
├── .env.example              # Environment template
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Docker orchestration
└── README.md                 # Comprehensive documentation
```

## 💡 Next Steps for Your Submission

1. **Test the system** with your own CV and project report
2. **Take screenshots** of:
   - POST /evaluate response
   - GET /result response (completed status)
3. **Document your experience**:
   - What worked well
   - What challenges you faced
   - Design decisions you made
4. **Review the README.md** - it contains detailed architecture explanation

## 🎯 Key Features Implemented

✅ Multi-stage LLM chaining (CV → Project → Final)  
✅ RAG with vector database for context retrieval  
✅ Async job processing with Celery  
✅ Robust error handling with retries  
✅ Structured scoring based on rubrics  
✅ Comprehensive logging  
✅ Docker support  
✅ Complete API documentation  
✅ Production-ready architecture  

## 📞 Support

If you encounter any issues:
1. Check the logs: `docker compose logs api` or `docker compose logs worker`
2. Review the troubleshooting section above
3. Ensure all environment variables are set correctly
4. Verify PDFs are valid and readable

---

Good luck with your submission! 🚀

