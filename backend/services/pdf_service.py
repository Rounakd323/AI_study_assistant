from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from services.embeddings import get_embeddings, set_db, DB_PATH
from typing import Tuple
import shutil
import os


def process_pdf(file_path: str) -> Tuple[FAISS, int, int]:
    """
    Load, chunk, embed a PDF and return (db, page_count, chunk_count).
    Clears any existing FAISS DB first.
    """
    # Remove old DB
    if os.path.exists(DB_PATH):
        shutil.rmtree(DB_PATH)

    # Load PDF
    loader = PyPDFLoader(file_path)
    docs = loader.load()
    docs = [doc for doc in docs if doc.page_content.strip()]

    if not docs:
        raise ValueError("No readable text found in the PDF.")

    # Chunk
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(docs)

    if not chunks:
        raise ValueError("Chunking produced no results.")

    # Embed + save
    embeddings = get_embeddings()
    db = FAISS.from_documents(chunks, embeddings)
    db.save_local(DB_PATH)
    set_db(db)

    return db, len(docs), len(chunks)


def similarity_search(topic: str, k: int = 5) -> list[Document]:
    from services.embeddings import get_db
    db = get_db()
    if db is None:
        raise ValueError("No document index loaded. Please upload a PDF first.")
    return db.similarity_search(topic, k=k)
