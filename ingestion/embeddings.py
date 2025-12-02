from typing import List
from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.openai_api_key)


def embed_texts(texts: List[str]) -> List[list[float]]:
    resp = client.embeddings.create(
        model=settings.openai_embedding_model,
        input=texts,
    )
    return [d.embedding for d in resp.data]
