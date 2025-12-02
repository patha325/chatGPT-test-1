# Second Brain – Gmail + pgvector Example

This repository is a reference implementation of a personal "second brain":

- **FastAPI** backend exposing a `/chat` endpoint.
- **PostgreSQL + pgvector** for semantic search over documents (including Gmail).
- **OpenAI** for embeddings and LLM chat.
- **Gmail integration** for ingesting email content into the knowledge base.
- **Docker + docker-compose** for local development.
- **GitHub Actions CI** for linting / basic checks.

## Architecture

- `ingestion/`
  - Ingestion pipeline for Gmail.
  - Chunking and embedding.
  - Upsert into Postgres/pgvector.
- `app/`
  - FastAPI app, RAG logic, memory store.
  - LLM client wrapper.

## Quickstart

1. Create and fill a `.env` file from `.env.example`.
2. Provide Google API credentials for Gmail in `secrets/credentials.json` (see Gmail API docs).
3. Build and start the stack:

   ```bash
   docker-compose up --build
   ```

4. In another terminal (with the same `.env`), run ingestion locally (outside Docker for the OAuth browser flow):

   ```bash
   python -m ingestion.ingest_gmail
   ```

   The first run will open a browser window to authorize Gmail access. It will store `secrets/token.json`.

5. Once emails are ingested, you can query the second brain:

   ```bash
   curl -X POST http://localhost:8000/chat \

     -H "Content-Type: application/json" \

     -d '{"user_id":"default","message":"Summarise my recent emails about project X"}'
   ```

## Database schema

Tables are created on startup:

- `documents` – content chunks with embeddings and metadata.
- `memories` – conversation-level long-term memory.

The `documents.embedding` column uses the `vector` type provided by the `pgvector` extension.

## Development without Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# set env vars defined in .env.example
uvicorn app.main:app --reload
```

## Notes

- This is a reference implementation, not production-hardened.
- Error handling, auth, and security should be extended before exposing this publicly.
