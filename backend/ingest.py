import fitz  # PyMuPDF
import chromadb
import ollama
from pathlib import Path

CHROMA_PATH = str(Path(__file__).resolve().parent / "chroma_db")
COLLECTION_NAME = "documents"
CHUNK_SIZE = 500       # characters per chunk
CHUNK_OVERLAP = 50     # overlap between consecutive chunks
EMBED_MODEL = "nomic-embed-text"  # pull with: ollama pull nomic-embed-text

def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(COLLECTION_NAME)

def extract_text(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    return "\n".join(page.get_text() for page in doc)

def chunk_text(text: str) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end].strip())
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return [c for c in chunks if c]  # drop empty chunks

def embed(text: str) -> list[float]:
    response = ollama.embeddings(model=EMBED_MODEL, prompt=text)
    return response["embedding"]

def ingest_pdf(pdf_path: str, source: str | None = None) -> int:
    collection = get_collection()
    text = extract_text(pdf_path)
    chunks = chunk_text(text)

    base_name = source or Path(pdf_path).stem

    # Wipe any prior chunks for this source so re-uploads don't leave stale chunks
    # behind if the new PDF has fewer chunks than the old one.
    collection.delete(where={"source": base_name})

    ids = [f"{base_name}_chunk_{i}" for i, _ in enumerate(chunks)]
    embeddings = [embed(chunk) for chunk in chunks]
    metadatas = [{"source": base_name, "chunk_index": i} for i in range(len(chunks))]

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )

    return len(chunks)
