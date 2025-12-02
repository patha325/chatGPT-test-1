import json
from typing import List, Dict, Any
from googleapiclient.discovery import build
from ingestion.gmail_auth import get_gmail_creds
from ingestion.gmail_loader import extract_text_from_message, headers_to_dict


def search_gmail_impl(query: str, max_results: int = 10) -> List[Dict[str, Any]]:
    creds = get_gmail_creds()
    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=max_results,
    ).execute()

    msgs = results.get("messages", [])
    out: List[Dict[str, Any]] = []

    for m in msgs:
        msg_id = m["id"]
        full = service.users().messages().get(
            userId="me", id=msg_id, format="full"
        ).execute()
        payload = full.get("payload", {})
        headers_list = payload.get("headers", [])
        headers = headers_to_dict(headers_list)

        text = extract_text_from_message(payload)
        snippet = " ".join(text.split())[:500]

        out.append(
            {
                "message_id": full.get("id"),
                "thread_id": full.get("threadId"),
                "from": headers.get("from"),
                "to": headers.get("to"),
                "subject": headers.get("subject"),
                "date": headers.get("date"),
                "snippet": snippet,
            }
        )

    return out
