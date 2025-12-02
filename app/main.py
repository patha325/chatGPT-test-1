import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models import ChatRequest, ChatResponse, RetrievedDoc
from app.db import init_db
from app.rag import build_context_bundle
from app.llm_client import build_system_prompt, call_llm
from app.memory import add_memory
from app.tools import get_tools
from app.tools_impl import search_gmail_impl

app = FastAPI(title="Second Brain – Gmail + pgvector")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    context = build_context_bundle(user_id=req.user_id, query=req.message)

    context_text_parts = []
    for i, doc in enumerate(context["retrieved_docs"][:5]):
        meta = doc["metadata"]
        if meta.get("source") == "gmail":
            header = (
                f"[EMAIL {i}] Subject: {meta.get('subject')} "
                f"From: {meta.get('from')} To: {meta.get('to')} "
                f"Date: {meta.get('date')}"
            )
        else:
            header = f"[DOC {i}] Source: {meta.get('source')}"
        context_text_parts.append(f"{header}\n{doc['content']}\n")

    if context["memories"]:
        context_text_parts.append(
            "Relevant memories:\n" + "\n".join(context["memories"])
        )

    context_text = "\n\n".join(context_text_parts)

    system_prompt = build_system_prompt(context["preference_summary"])

    user_message = {
        "role": "user",
        "content": (
            "User query:\n"
            f"{req.message}\n\n"
            "Context from your knowledge base and memories:\n"
            f"{context_text}"
        ),
    }

    tools = get_tools()
    completion = call_llm(system_prompt, [user_message], tools=tools)
    msg = completion.choices[0].message

    reply_text: str

    if msg.tool_calls:
        # For simplicity we handle a single tool call
        tool_call = msg.tool_calls[0]
        if tool_call.function.name == "search_gmail":
            args = json.loads(tool_call.function.arguments)
            results = search_gmail_impl(
                query=args["query"],
                max_results=args.get("max_results", 10),
            )
            tool_msg = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": "search_gmail",
                "content": json.dumps(results),
            }
            completion2 = call_llm(
                system_prompt,
                [user_message, msg, tool_msg],
                tools=tools,
            )
            reply_text = completion2.choices[0].message.content
        else:
            reply_text = msg.content or ""
    else:
        reply_text = msg.content or ""

    add_memory(
        user_id=req.user_id,
        text=f"Q: {req.message}\nA: {reply_text}",
    )

    used_docs = [
        RetrievedDoc(**d, score=d.get("score", 0.0))
        for d in context["retrieved_docs"]
    ]

    return ChatResponse(reply=reply_text, used_docs=used_docs)
