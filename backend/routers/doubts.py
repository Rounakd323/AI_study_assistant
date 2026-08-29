from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.pdf_service import similarity_search
from services.llm import invoke_llm

router = APIRouter()


class DoubtRequest(BaseModel):
    question: str
    topic: str | None = None


class DoubtResponse(BaseModel):
    question: str
    answer: str


@router.post("/", response_model=DoubtResponse)
async def answer_doubt(request: DoubtRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    search_query = request.topic or question

    try:
        docs = similarity_search(search_query, k=5)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if not docs:
        raise HTTPException(status_code=404, detail="No relevant content found.")

    context = "\n\n".join([doc.page_content for doc in docs])

    doubt_prompt = f"""You are a helpful teacher.

Answer the question clearly using only the context provided.
If the answer is not found in the context, say "This information is not covered in the document."
Keep your answer focused and well-structured.

Context:
{context}

Question: {question}
"""

    answer = invoke_llm(doubt_prompt)

    return DoubtResponse(question=question, answer=answer)
