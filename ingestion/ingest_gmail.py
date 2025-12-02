from ingestion.gmail_loader import load_gmail_messages
from ingestion.chunking import chunk_document
from ingestion.embeddings import embed_texts
from app.db import SessionLocal, Document
from app.config import settings


def ingest_gmail(max_messages: int = 200) -> None:
    docs = load_gmail_messages(max_messages=max_messages)
    all_chunks = []
    for doc in docs:
        all_chunks.extend(chunk_document(doc))

    if not all_chunks:
        print("No Gmail chunks to ingest.")
        return

    texts = [c["content"] for c in all_chunks]
    vectors = embed_texts(texts)

    with SessionLocal() as session:
        for chunk, vec in zip(all_chunks, vectors):
            meta = chunk["metadata"]
            doc_row = Document(
                source="gmail",
                source_id=chunk["id"],
                content=chunk["content"],
                metadata=meta,
                embedding=vec,
            )
            session.add(doc_row)
        session.commit()

    print(f"Ingested {len(all_chunks)} Gmail chunks.")


if __name__ == "__main__":
    ingest_gmail(max_messages=200)
