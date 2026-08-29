from langchain_community.llms import Ollama
from typing import Optional

_llm: Optional[Ollama] = None


def get_llm() -> Ollama:
    global _llm
    if _llm is None:
        _llm = Ollama(model="llama3")
    return _llm


def invoke_llm(prompt: str) -> str:
    llm = get_llm()
    return llm.invoke(prompt)
