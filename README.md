
# AI Study Assistant — FastAPI + RAG

A RAG-powered study assistant built with FastAPI, FAISS, HuggingFace Embeddings, and Ollama (llama3).

---

## File Structure

```
ai-study-assistant/
│
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── upload.py              # PDF upload & processing endpoint
│   │   ├── study.py               # Topic summary generation
│   │   ├── quiz.py                # Quiz generation
│   │   └── doubts.py              # Q&A / doubt answering
│   ├── services/
│   │   ├── __init__.py
│   │   ├── embeddings.py          # FAISS DB + HuggingFace embeddings (singleton)
│   │   ├── llm.py                 # Ollama LLM wrapper (singleton)
│   │   └── pdf_service.py         # PDF loading, chunking, indexing
│   └── utils/                     # (reserved for future helpers)
│
├── frontend/
│   ├── templates/
│   │   └── index.html             # Jinja2 HTML template (served by FastAPI)
│   └── static/
│       ├── css/
│       │   └── style.css          # Dark academic design system
│       └── js/
│           └── app.js             # All frontend logic & API calls
│
├── requirements.txt
└── README.md
```

---
## Architecutre
                    ┌──────────────────────┐
                    │     Web Frontend     │
                    │      HTML/CSS/JS     │
                    └──────────┬───────────┘
                               │
                               │ HTTP Requests
                               ▼
                    ┌──────────────────────┐
                    │       FastAPI        │
                    │      REST API        │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
            PDF Upload                  User Query
                 │                           │
                 ▼                           ▼
        ┌─────────────────┐        ┌─────────────────┐
        │  PyPDFLoader    │        │ Query Embedding │
        │ Text Extraction │        │ Hugging Face    │
        └────────┬────────┘        └────────┬────────┘
                 │                          │
                 ▼                          │
        ┌─────────────────┐                 │
        │ Text Chunking   │                 │
        │ 500 / overlap 50│                 │
        └────────┬────────┘                 │
                 │                          │
                 ▼                          ▼
        ┌─────────────────┐        ┌─────────────────┐
        │ Hugging Face    │        │      FAISS      │
        │ Embeddings      │───────►│ Vector Search   │
        │ all-MiniLM-L6-v2│        └────────┬────────┘
        └────────┬────────┘                 │
                 │                     Top 5 chunks
                 ▼                          │
        ┌─────────────────┐                 │
        │      FAISS      │◄────────────────┘
        │  Vector Index   │
        └─────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Ollama / Llama 3   │
                    │      Local LLM       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Generated Result   │
                    │ Summary / Quiz / Q&A │
                    └──────────────────────┘

---
## Prerequisites

1. **Python 3.11+**
2. **Ollama** installed and running with llama3:
   ```bash
   ollama serve
   ollama pull llama3
   ```

---

## Setup

```bash
# 1. Clone / navigate to project
cd ai-study-assistant

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server (from the backend/ directory)
cd backend
python main.py
```

Visit → **http://localhost:8000**

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/upload/` | Upload PDF, builds FAISS index |
| GET  | `/api/upload/status` | Check if a document is loaded |
| POST | `/api/study/` | Generate topic summary |
| POST | `/api/quiz/` | Generate 5-question quiz |
| POST | `/api/doubts/` | Answer a question from document |
| GET  | `/docs` | FastAPI Swagger UI |

### Request/Response Examples

**Upload PDF**
```
POST /api/upload/
Content-Type: multipart/form-data
Body: file=<pdf>
→ { "message": "...", "filename": "...", "pages": 42, "chunks": 186 }
```

**Study Summary**
```
POST /api/study/
{ "topic": "Photosynthesis" }
→ { "topic": "...", "summary": "...", "context_snippets": [...] }
```

**Quiz**
```
POST /api/quiz/
{ "topic": "Photosynthesis" }
→ { "topic": "...", "quiz": "1. ..." }
```

**Doubts**
```
POST /api/doubts/
{ "question": "What is ATP?", "topic": "Photosynthesis" }
→ { "question": "...", "answer": "..." }
```

---

## Configuration

- **GPU**: In `services/embeddings.py`, change `"device": "cpu"` → `"device": "cuda"` if you have a GPU.
- **LLM Model**: In `services/llm.py`, change `model="llama3"` to any Ollama model.
- **Chunk Size**: Adjust `chunk_size` and `chunk_overlap` in `services/pdf_service.py`.
