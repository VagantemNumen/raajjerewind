import os
import logging
from typing import Literal
from google import genai
from pydantic import BaseModel
from ingest import get_collection, embed

logger = logging.getLogger("uvicorn.error")

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-3.1-flash-lite"
TOP_K = 6
HISTORY_TURNS = 6  # Last N user/assistant turns to send to the model.

client = genai.Client(api_key=GEMINI_API_KEY)


class HistoryTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


SYSTEM_PROMPT = """You are a friendly tutor for 7th-grade students. Answer the question using the information in the CONTEXT section of the latest user message. Do not invent facts that aren't supported by the context.

You will often see prior turns of the conversation. Use them to understand what the user is referring to in follow-up questions (e.g. resolve "he", "that", "then", "after that"). Treat the conversation as continuous — a follow-up like "When did he die?" refers to whoever was just discussed.

Rules:
- Answer directly. Do NOT preface answers with phrases like "The provided documents say...", "According to the context...", "Based on the passages...", "It is mentioned that...". Just give the answer.
- Do NOT include inline citations like "[Source: ...]" in your answer. Source attribution is handled separately by the interface.
- If the context clearly addresses the question, answer based on it — even if you have to combine information across the passages.
- ONLY if the context truly does not contain the information needed (not even partially), reply exactly with: "I'm not sure — that's not in what I've read so far."
- Keep answers concise and clear. Use short paragraphs, bold for key terms, and bullet lists where they help.
"""


REWRITE_PROMPT = """You rewrite a student's question into a search query for a database of Maldivian social-studies textbooks (English).

Given the conversation so far and the student's latest question, produce a single, self-contained search query.
- Fix spelling and capitalization of names and places (e.g. "shamsudeen" -> "Shamsuddeen", "thakurufan" -> "Thakurufaanu").
- Expand partial names or titles to the most likely full form when the textbook context makes it clear (e.g. "shamsuddeen" -> "Sultan Shamsuddeen III").
- Resolve pronouns and references ("he", "that", "then", "after that") using the conversation so the query stands on its own.
- Keep it short — just the key terms a search would need, no extra words.

Output ONLY the rewritten search query, with no quotes, labels, or explanation."""


def _rewrite_query(question: str, history: list[HistoryTurn]) -> str | None:
    """Use the model to normalize the question into a clean search query:
    fix spelling/casing, expand partial names, resolve pronouns. Returns None
    on any failure so retrieval can fall back to the raw question."""
    convo = "\n".join(f"{turn.role}: {turn.content}" for turn in history)
    prompt = (
        f"Conversation so far:\n{convo}\n\n" if convo else ""
    ) + f"Latest question: {question}"
    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[{"role": "user", "parts": [{"text": prompt}]}],
            config={
                "system_instruction": REWRITE_PROMPT,
                "temperature": 0,
            },
        )
        rewritten = (response.text or "").strip()
        return rewritten or None
    except Exception:
        logger.exception("query rewrite failed; falling back to raw question")
        return None


def _retrieval_queries(question: str, history: list[HistoryTurn]) -> list[str]:
    """Return the raw question plus a model-rewritten search query (spelling
    fixed, names expanded, pronouns resolved). Both are merged downstream so a
    terse or misspelled question still finds its topic, while the raw text is
    kept as a safety net if the rewrite drifts."""
    queries = [question]
    rewritten = _rewrite_query(question, history)
    if rewritten and rewritten.lower() != question.lower():
        queries.append(rewritten)
    return queries


def _retrieve(queries: list[str]) -> tuple[list[str], list[dict]]:
    """Run each query, merge results, dedupe by chunk id, preserve order."""
    collection = get_collection()
    seen_ids: set[str] = set()
    chunks: list[str] = []
    metadatas: list[dict] = []
    for q in queries:
        result = collection.query(
            query_embeddings=[embed(q)],
            n_results=TOP_K,
            include=["documents", "metadatas"],
        )
        ids = result.get("ids", [[]])[0]
        docs = result["documents"][0]
        metas = result["metadatas"][0]
        for doc_id, doc, meta in zip(ids, docs, metas):
            if doc_id in seen_ids:
                continue
            seen_ids.add(doc_id)
            chunks.append(doc)
            metadatas.append(meta)
    return chunks, metadatas


def answer_question(question: str, history: list[HistoryTurn] | None = None) -> dict:
    history = (history or [])[-HISTORY_TURNS:]

    queries = _retrieval_queries(question, history)
    chunks, metadatas = _retrieve(queries)

    logger.info(
        "ask: q=%r queries=%r history=%d chunks=%d sources=%s",
        question,
        queries,
        len(history),
        len(chunks),
        sorted({m.get("source", "?") for m in metadatas}),
    )

    if not chunks:
        return {
            "answer": "I'm not sure — that's not in what I've read so far.",
            "sources": [],
        }

    context = "\n\n---\n\n".join(
        f"[Source: {meta['source']}]\n{chunk}"
        for chunk, meta in zip(chunks, metadatas)
    )

    contents: list[dict] = [
        {"role": "user" if turn.role == "user" else "model", "parts": [{"text": turn.content}]}
        for turn in history
    ]
    contents.append({
        "role": "user",
        "parts": [{"text": f"CONTEXT:\n{context}\n\nQUESTION: {question}"}],
    })

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config={"system_instruction": SYSTEM_PROMPT},
    )

    sources = list({meta["source"] for meta in metadatas})
    return {
        "answer": response.text,
        "sources": sources,
        "chunks_used": len(chunks),
    }
