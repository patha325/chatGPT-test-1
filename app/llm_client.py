from typing import List, Dict, Any, Optional
from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.openai_api_key)

BASE_PERSONA = """
You are the personal second brain of the user.
You know their background: data science, particle physics, and data engineering.
You must:
- Be precise and technical when appropriate.
- Prefer step-by-step reasoning and explicit assumptions.
- Use the user's own notes and documents when available.
- If unsure, say so and propose what data is missing.
"""


def build_system_prompt(preference_summary: str = "") -> str:
    if preference_summary:
        return BASE_PERSONA + "\n\n" + preference_summary
    return BASE_PERSONA


def call_llm(
    system_prompt: str,
    messages: List[Dict[str, str]],
    tools: Optional[List[Dict[str, Any]]] = None,
) -> Any:
    kwargs: Dict[str, Any] = {
        "model": settings.openai_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            *messages,
        ],
    }
    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = "auto"

    resp = client.chat.completions.create(**kwargs)
    return resp
