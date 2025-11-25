from pathlib import Path
import json
import numpy as np
import faiss
from typing import List, Dict
from sentence_transformers import SentenceTransformer

class VectorStore:
    def __init__(self, store_dir: Path, embed_model_name: str):
        self.store_dir = store_dir
        self.vec_file = store_dir / "vectors.npy"
        self.meta_file = store_dir / "metadata.json"
        self.index_file = store_dir / "index.faiss"
        self.embedder = SentenceTransformer(embed_model_name)

        self.index = None
        self.metadata = None

        if self.index_file.exists() and self.meta_file.exists() and self.vec_file.exists():
            self._load()

    def _save(self, vectors: np.ndarray, metadata: List[Dict]):
        np.save(self.vec_file, vectors)
        with self.meta_file.open("w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        faiss.write_index(self.index, str(self.index_file))

    def _load(self):
        _ = np.load(self.vec_file)  # not needed directly, but ensures file present
        self.index = faiss.read_index(str(self.index_file))
        with self.meta_file.open("r", encoding="utf-8") as f:
            self.metadata = json.load(f)

    def rebuild(self, docs: List[Dict]):
        texts = [d["text"] for d in docs]
        vectors = self.embedder.encode(texts, convert_to_numpy=True, batch_size=64, show_progress_bar=True)
        faiss.normalize_L2(vectors)  # cosine similarity trick
        self.index = faiss.IndexFlatIP(vectors.shape[1])
        self.index.add(vectors)
        self.metadata = docs
        self._save(vectors, docs)

    def is_ready(self) -> bool:
        return self.index is not None and self.metadata is not None

    def search(self, query: str, k: int) -> List[Dict]:
        q = self.embedder.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(q)
        D, I = self.index.search(q, k)
        hits = []
        for score, idx in zip(D[0], I[0]):
            if idx == -1: continue
            md = self.metadata[int(idx)]
            hits.append({"score": float(score), **md})
        return hits

    def stats(self) -> Dict:
        n = self.index.ntotal if self.index else 0
        dim = self.index.d if self.index else 0
        return {"chunks": int(n), "dim": int(dim)}
