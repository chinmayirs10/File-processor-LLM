from pathlib import Path
import re
from typing import List, Dict
from pypdf import PdfReader
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def _load_text(path: Path) -> str:
    if path.suffix.lower() in (".txt", ".md"):
        return path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix.lower() == ".pdf":
        text = []
        with path.open("rb") as f:
            reader = PdfReader(f)
            for page in reader.pages:
                text.append(page.extract_text() or "")
        return "\n".join(text)
    return ""

def _clean(s: str) -> str:
    s = s.replace("\r", "\n")
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def chunk_text(text: str, size: int, overlap: int) -> List[str]:
    tokens = text.split()
    chunks, start = [], 0
    while start < len(tokens):
        end = min(len(tokens), start + size)
        chunks.append(" ".join(tokens[start:end]))
        if end == len(tokens): break
        start = max(0, end - overlap)
    return chunks

def collect_documents(data_dir: Path, size: int, overlap: int) -> List[Dict]:
    docs = []
    for p in data_dir.glob("**/*"):
        if p.is_file() and p.suffix.lower() in (".txt", ".md", ".pdf"):
            raw = _load_text(p)
            if not raw: continue
            text = _clean(raw)
            for i, chunk in enumerate(chunk_text(text, size=size, overlap=overlap)):
                docs.append({"path": str(p.resolve()), "chunk_id": i, "text": chunk})
    return docs
