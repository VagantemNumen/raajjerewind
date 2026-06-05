from dotenv import load_dotenv
load_dotenv()  # Must run before importing modules that read env vars at import time.

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.genai import errors as genai_errors
from pathlib import Path
import shutil, os, tempfile, logging
from ingest import ingest_pdf
from query import answer_question, HistoryTurn
from admin import router as admin_router, verify_token

logger = logging.getLogger("uvicorn.error")

# Comma-separated list of allowed frontend origins.
# In dev the Vite proxy makes this irrelevant; set it in prod.
_origins_env = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
ALLOWED_ORIGINS = [o.strip() for o in _origins_env.split(",") if o.strip()]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)

class QuestionRequest(BaseModel):
    question: str
    history: list[HistoryTurn] = []

# POST /upload  — accepts a PDF, ingests it into ChromaDB. Admin-only.
@app.post("/upload", dependencies=[Depends(verify_token)])
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    source_name = Path(file.filename).stem
    try:
        num_chunks = ingest_pdf(tmp_path, source=source_name)
    except Exception:
        logger.exception("Ingestion failed for %s", file.filename)
        raise HTTPException(status_code=503, detail="The server is experiencing some issues. Please try again later.")
    finally:
        os.remove(tmp_path)

    return {"message": f"Ingested '{file.filename}' as {num_chunks} chunks.", "source": source_name}


# POST /ask  — takes a question, returns an answer grounded in the PDFs
@app.post("/ask")
async def ask(req: QuestionRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        return answer_question(req.question, history=req.history)
    except genai_errors.APIError as e:
        logger.warning("Gemini API error: %s", e)
        raise HTTPException(status_code=503, detail="The server is experiencing some issues. Please try again later.")
    except Exception:
        logger.exception("Unexpected error answering question")
        raise HTTPException(status_code=500, detail="The server is experiencing some issues. Please try again later.")


# GET /health  — simple liveness check
@app.get("/health")
def health():
    return {"status": "ok"}
