from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from routers import upload, study, quiz, doubts


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("db", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)
    yield


app = FastAPI(
    title="AI Study Assistant",
    description="RAG-powered study assistant — FastAPI + FAISS + Ollama",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")),
    name="static"
)

templates = Jinja2Templates(directory=os.path.join(FRONTEND_DIR, "templates"))

app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(study.router,  prefix="/api/study",  tags=["Study"])
app.include_router(quiz.router,   prefix="/api/quiz",   tags=["Quiz"])
app.include_router(doubts.router, prefix="/api/doubts", tags=["Doubts"])


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
