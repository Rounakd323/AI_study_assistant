from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.pdf_service import similarity_search
from services.llm import invoke_llm

router = APIRouter()


class QuizRequest(BaseModel):
    topic: str
    context: str | None = None


class QuizResponse(BaseModel):
    topic: str
    quiz: str


@router.post("/", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest):
    topic = request.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")

    # Use provided context or retrieve fresh
    if request.context:
        context = request.context
    else:
        try:
            docs = similarity_search(topic, k=5)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

        if not docs:
            raise HTTPException(status_code=404, detail="No relevant content found.")

        context = "\n\n".join([doc.page_content for doc in docs])

    quiz_prompt = f"""You are a teacher creating a quiz.

Based on the context below, generate 5 quiz questions:
- 3 short answer questions
- 2 MCQs with 4 options each (label them A, B, C, D)

Format each question clearly with numbering.
Include answers at the end under "--- ANSWERS ---".

Context:
{context}

Topic: {topic}
"""

    quiz = invoke_llm(quiz_prompt)

    return QuizResponse(topic=topic, quiz=quiz)
