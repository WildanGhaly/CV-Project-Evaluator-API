from pathlib import Path
from typing import Optional

def extract_text(path: str) -> str:
    """Extract text from a PDF using PyMuPDF, fallback to pdfminer if needed."""
    p = Path(path)
    if not p.exists():
        return ""
    try:
        import fitz  # PyMuPDF
        text_parts = []
        with fitz.open(path) as doc:
            for page in doc:
                text_parts.append(page.get_text("text"))
        return "\n".join(text_parts)
    except Exception:
        try:
            from pdfminer.high_level import extract_text as pm_extract
            return pm_extract(path) or ""
        except Exception:
            return ""