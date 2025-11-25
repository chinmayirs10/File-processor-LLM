import requests

class OllamaClient:
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def generate(self, prompt: str, temperature: float = 0.2, timeout: int = 120) -> str:
        url = f"{self.base_url}/api/generate"
        payload = {"model": self.model, "prompt": prompt, "stream": False, "options": {"temperature": temperature}}
        r = requests.post(url, json=payload, timeout=timeout)
        r.raise_for_status()
        return r.json().get("response", "").strip()

def build_prompt(question: str, hits: list) -> str:
    ctx = []
    for h in hits:
        ctx.append(f"[{h['path']} – chunk {h['chunk_id']}, score={h['score']:.3f}]\n{h['text']}")
    context = "\n\n---\n\n".join(ctx)
    return f"""You are a helpful assistant. Answer the user's question using ONLY the context below.
If the answer is not in the context, say you don't know.

# Context
{context}

# Question
{question}

# Answer
"""
