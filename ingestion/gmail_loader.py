from __future__ import annotations
from typing import List, Dict
from base64 import urlsafe_b64decode
from googleapiclient.discovery import build
from bs4 import BeautifulSoup

from ingestion.gmail_auth import get_gmail_creds


def extract_text_from_message(msg_payload: dict) -> str:
    """Extract the plain text body from a Gmail message payload."""

    def walk_parts(parts):
        texts = []
        for part in parts:
            mime_type = part.get("mimeType", "")
            body = part.get("body", {})
            data = body.get("data")
            if data:
                raw_bytes = urlsafe_b64decode(data.encode("utf-8"))
                if mime_type == "text/plain":
                    texts.append(raw_bytes.decode("utf-8", errors="ignore"))
                elif mime_type == "text/html":
                    html = raw_bytes.decode("utf-8", errors="ignore")
                    soup = BeautifulSoup(html, "html.parser")
                    texts.append(soup.get_text(separator="\n"))
            if "parts" in part:
                texts.extend(walk_parts(part["parts"]))
        return texts

    mime_type = msg_payload.get("mimeType", "")
    body = msg_payload.get("body", {})

    if mime_type == "text/plain" and "data" in body:
        raw_bytes = urlsafe_b64decode(body["data"].encode("utf-8"))
        return raw_bytes.decode("utf-8", errors="ignore")

    if "parts" in msg_payload:
        texts = walk_parts(msg_payload["parts"])
        if texts:
            return "\n\n".join(texts)

    return ""


def headers_to_dict(headers: list[dict]) -> dict:
    hmap = {}
    for h in headers:
        name = h.get("name", "").lower()
        value = h.get("value", "")
        hmap[name] = value
    return hmap


def load_gmail_messages(
    max_messages: int = 200,
    query: str = "-category:social -category:promotions",
) -> List[Dict]:
    """Fetch messages via Gmail API and normalize them into {id, content, metadata}."""
    creds = get_gmail_creds()
    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=max_messages,
    ).execute()

    msgs = results.get("messages", [])
    docs: List[Dict] = []

    for m in msgs:
        msg_id = m["id"]
        full = service.users().messages().get(
            userId="me", id=msg_id, format="full"
        ).execute()

        payload = full.get("payload", {})
        headers_list = payload.get("headers", [])
        headers = headers_to_dict(headers_list)

        body_text = extract_text_from_message(payload)
        if not body_text.strip():
            continue

        metadata = {
            "source": "gmail",
            "source_type": "gmail",
            "message_id": full.get("id"),
            "thread_id": full.get("threadId"),
            "from": headers.get("from"),
            "to": headers.get("to"),
            "subject": headers.get("subject"),
            "date": headers.get("date"),
            "label_ids": full.get("labelIds", []),
        }

        doc = {
            "id": f"gmail::{full['id']}",
            "content": body_text,
            "metadata": metadata,
        }
        docs.append(doc)

    return docs
