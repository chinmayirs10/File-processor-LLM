📄 Local Document Q&A (RAG + OCR + Local LLM)

A simple backend application that lets you **ask questions about your local documents** (PDF, TXT, MD) using a **Retrieval-Augmented Generation (RAG)** pipeline with:

* **FastAPI**
* **FAISS vector search**
* **SentenceTransformer embeddings**
* **Ollama (local LLMs like Qwen, Llama, Phi)**
* **OCR (Tesseract) for scanned PDFs**

---

## 🚀 Features

* Ask questions about any file you drop into the `data/` folder
* Supports text PDFs and **scanned/image PDFs**
* Runs completely **offline**
* Easy to swap LLMs (e.g., Qwen, Phi, Llama)

---

## 📦 Setup

### 1) Clone and create virtual environment

```bash
git clone <your-repo-url>
cd rag_service
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Install Ollama + LLM

Download from: [https://ollama.ai](https://ollama.ai)

Then run:

```bash
ollama serve
ollama pull qwen2.5:3b-instruct     # or any model you prefer
```

### 4) Install Tesseract OCR (for scanned PDFs)

Download (Windows):
[https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)

Verify:

```bash
tesseract --version
```

---

## ▶️ Run the API

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 📥 Ingest Your Documents

Place files in:

```
rag_service/data/
```

Then run:

```powershell
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8000/ingest
```

---

## ❓ Ask a Question

```powershell
$body = @{ question = 'What is the total work experience in the CV?' } | ConvertTo-Json
Invoke-RestMethod -Method POST -Uri 'http://127.0.0.1:8000/query' -ContentType 'application/json' -Body $body
```

---

## 🧪 Check System Status

```bash
Invoke-RestMethod http://127.0.0.1:8000/stats
```

---

## 📁 Project Structure

```
app/
  main.py          # API endpoints
  ingest.py        # document loader + OCR + chunking
  vectorstore.py   # embeddings + FAISS
  llm.py           # LLM generation via Ollama
data/              # place your documents here
store/             # FAISS index + metadata
```
