from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from typing import Optional
import os

DB_PATH = "db"
UPLOAD_PATH = "uploads"

# Singleton embeddings instance
_embeddings: Optional[HuggingFaceEmbeddings] = None
_db: Optional[FAISS] = None


def get_embeddings() -> HuggingFaceEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"}  # change to "cuda" if GPU available
        )
    return _embeddings


def get_db() -> Optional[FAISS]:
    global _db
    if _db is None and os.path.exists(DB_PATH):
        _db = FAISS.load_local(
            DB_PATH,
            get_embeddings(),
            allow_dangerous_deserialization=True
        )
    return _db


def set_db(db: FAISS):
    global _db
    _db = db


def clear_db():
    global _db
    _db = None
