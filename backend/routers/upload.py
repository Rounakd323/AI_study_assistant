from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from services.pdf_service import process_pdf
import os
import shutil

router = APIRouter()

UPLOAD_PATH = "uploads"


@router.post("/")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    os.makedirs(UPLOAD_PATH, exist_ok=True)
    file_path = os.path.join(UPLOAD_PATH, "current.pdf")

    # Save uploaded file
    with open(file_path, "wb") as f:
        contents = await file.read()
        f.write(contents)

    try:
        db, pages, chunks = process_pdf(file_path)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

    return JSONResponse({
        "message": "PDF processed successfully",
        "filename": file.filename,
        "pages": pages,
        "chunks": chunks
    })


@router.get("/status")
async def upload_status():
    from services.embeddings import get_db
    db = get_db()
    pdf_exists = os.path.exists(os.path.join(UPLOAD_PATH, "current.pdf"))
    return {
        "has_document": db is not None,
        "pdf_on_disk": pdf_exists
    }
