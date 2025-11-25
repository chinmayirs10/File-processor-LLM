import os
from pathlib import Path

class Settings:
    EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/multi-qa-MiniLM-L6-cos-v1")
    OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b-instruct")
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 800))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 120))
    TOP_K = int(os.getenv("TOP_K", 5))
    DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
    STORE_DIR = Path(os.getenv("STORE_DIR", "./store"))

settings = Settings()
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.STORE_DIR.mkdir(parents=True, exist_ok=True)
