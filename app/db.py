from sqlalchemy import create_engine, Integer, String, Text, JSON, Column, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.config import settings

DB_URL = (
    f"postgresql+psycopg2://{settings.postgres_user}:"
    f"{settings.postgres_password}@{settings.postgres_host}:"
    f"{settings.postgres_port}/{settings.postgres_db}"
)

engine = create_engine(DB_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String(64), nullable=False)
    source_id = Column(String(256), nullable=False)
    content = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=False)
    embedding = Column(Vector(settings.vector_dim))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Memory(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


def init_db() -> None:
    with engine.begin() as conn:
        conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    Base.metadata.create_all(bind=engine)
