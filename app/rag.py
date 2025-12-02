from typing import Any, List, Dict
from sqlalchemy import select
from pgvector.sqlalchemy import cosine_distance
from app.db import SessionLocal, Document
from app.memory import get_recent_memories, get_preference_summary
from ingestion.embeddings import embed_texts


def retrieve_docs(query: str, k: int = 8) -> List[Dict[str, Any]]:
    [query_vec] = embed_texts([query])
    with SessionLocal() as session:
        stmt = (
            select(Document)
            .order_by(cosine_distance(Document.embedding, query_vec))
            .limit(k)
        )
        docs = session.execute(stmt).scalars().all()
        out: List[Dict[str, Any]] = []
        for d in docs:
            out.append(
                {
                    "content": d.content,
                    "metadata": {
                        "source": d.source,
                        "source_id": d.source_id,
                        **(d.metadata or {}),
                    },
                    "score": 0.0,  # distance can be added if needed
                }
            )
        return out


def build_context_bundle(user_id: str, query: str) -> Dict[str, Any]:
    docs = retrieve_docs(query)
    memories = get_recent_memories(user_id=user_id)
    pref_summary = get_preference_summary(user_id=user_id)
    return {
        "retrieved_docs": docs,
        "memories": memories,
        "preference_summary": pref_summary,
    }
