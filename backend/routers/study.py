from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.pdf_service import similarity_search
from services.llm import invoke_llm
from services.embeddings import get_embeddings
import numpy as np

router = APIRouter()   # ← must come first


class StudyRequest(BaseModel):
    topic: str


class StudyResponse(BaseModel):
    topic: str
    summary: str
    context_snippets: list[str]


@router.post("/", response_model=StudyResponse)
async def get_study_summary(request: StudyRequest):
    topic = request.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")

    try:
        docs = similarity_search(topic, k=5)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    if not docs:
        raise HTTPException(status_code=404, detail="No relevant content found for this topic.")

    context = "\n\n".join([doc.page_content for doc in docs])
    snippets = [doc.page_content[:300] for doc in docs]

    summary_prompt = f"""You are a study assistant.

Explain the topic clearly in simple language.
Use headings and bullet points.
Be concise but thorough.

Context:
{context}

Topic: {topic}
"""

    summary = invoke_llm(summary_prompt)
    return StudyResponse(topic=topic, summary=summary, context_snippets=snippets)


@router.post("/embedding")
async def get_summary_embedding(request: StudyRequest):
    topic = request.topic.strip()

    docs = similarity_search(topic, k=5)
    context = "\n\n".join([doc.page_content for doc in docs])
    summary = invoke_llm(f"Summarise this: {context}")

    embeddings = get_embeddings()
    summary_vector = np.array(embeddings.embed_query(summary))
    chunk_vectors  = np.array(embeddings.embed_documents([doc.page_content for doc in docs]))

    def cosine(a, b):
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    scores = [
        {
            "chunk_index": i,
            "score": round(cosine(summary_vector, chunk_vectors[i]), 4),
            "preview": docs[i].page_content[:120]
        }
        for i in range(len(docs))
    ]
    scores.sort(key=lambda x: x["score"], reverse=True)

    return {"topic": topic, "summary": summary, "scores": scores}