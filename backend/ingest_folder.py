from pathlib import Path
from ingest import ingest_pdf

PDF_FOLDER = Path(__file__).resolve().parent / "pdf"

# Look for all PDFs inside the directory
for pdf_path in PDF_FOLDER.glob("*.pdf"):
    n = ingest_pdf(str(pdf_path))
    print(f"{pdf_path.name} → {n} chunks")