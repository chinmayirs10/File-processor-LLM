from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .config import settings
from .ingest import collect_documents
from .vectorstore import VectorStore
from .llm import OllamaClient, build_prompt

app = FastAPI(title="RAG Service", version="0.1.0")

store = VectorStore(settings.STORE_DIR, settings.EMBED_MODEL)
llm = OllamaClient(settings.OLLAMA_URL, settings.OLLAMA_MODEL)

class IngestResponse(BaseModel):
    files_indexed: int
    chunks: int

class QueryRequest(BaseModel):
    question: str
    top_k: int | None = None

class QueryResponse(BaseModel):
    answer: str
    sources: list

@app.get("/stats")
def stats():
    return {
        "index_ready": store.is_ready(),
        "vector_stats": store.stats(),
        "config": {
            "embed_model": settings.EMBED_MODEL,
            "ollama_model": settings.OLLAMA_MODEL,
            "top_k_default": settings.TOP_K
        }
    }

@app.post("/ingest", response_model=IngestResponse)
def ingest():
    docs = collect_documents(settings.DATA_DIR, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
    if not docs:
        raise HTTPException(400, detail=f"No .txt/.md/.pdf files found in {settings.DATA_DIR.resolve()}")
    store.rebuild(docs)
    return IngestResponse(files_indexed=len({d['path'] for d in docs}), chunks=len(docs))

@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    if not store.is_ready():
        raise HTTPException(400, detail="Index not built. Call /ingest first.")
    k = req.top_k or settings.TOP_K
    hits = store.search(req.question, k=k)
    if not hits:
        return QueryResponse(answer="I don't know.", sources=[])
    prompt = build_prompt(req.question, hits)
    answer = llm.generate(prompt)
    sources = [{"path": h["path"], "chunk_id": h["chunk_id"], "score": round(h["score"], 3)} for h in hits]
    return QueryResponse(answer=answer, sources=sources)


@app.get("/search")
def search(q: str):
    hits = store.search(q, k=settings.TOP_K)
    return hits