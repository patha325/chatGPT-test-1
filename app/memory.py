from typing import List
from sqlalchemy import select
from app.db import SessionLocal, Memory


def add_memory(user_id: str, text: str) -> None:
    with SessionLocal() as session:
        mem = Memory(user_id=user_id, content=text)
        session.add(mem)
        session.commit()


def get_recent_memories(user_id: str, limit: int = 5) -> List[str]:
    with SessionLocal() as session:
        stmt = (
            select(Memory)
            .where(Memory.user_id == user_id)
            .order_by(Memory.created_at.desc())
            .limit(limit)
        )
        rows = session.execute(stmt).scalars().all()
        return [m.content for m in rows]


def get_preference_summary(user_id: str) -> str:
    # Placeholder: in a more advanced setup, summarise explicit preference records.
    # Here we just say nothing.
    return ""
