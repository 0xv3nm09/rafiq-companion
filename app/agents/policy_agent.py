"""Policy agent — grounded RAG answers with inline citations."""
from __future__ import annotations

from app.core.guardrails import trust_gate
from app.core.llm import complete
from app.core.rag import extractive_answer, get_index, to_citations
from app.schemas.ask import AskRequest, AskResponse, LowConfidenceInfo
from app.config import get_settings


@trust_gate
async def answer_policy(req: AskRequest, store) -> AskResponse:
    settings = get_settings()
    index = get_index(store)
    hits = index.search(req.message, lang=req.lang.value, top_k=settings.top_k)
    low = LowConfidenceInfo(retrieval_score=hits[0].confidence if hits else 0.0,
                            threshold=settings.min_score)

    if not hits or hits[0].confidence < settings.min_score:
        return AskResponse(answer="", confidence=round(low.retrieval_score, 3), citations=[],
                           kind="policy", low_confidence=low)

    context = "\n\n".join(f"[{h.chunk.policy_id} · {h.chunk.title} · {h.chunk.section}]\n{h.chunk.text}"
                          for h in hits)
    text = complete(req.message, context, req.lang.value)
    if text is None or "I am not sure" in text:
        text = extractive_answer(req.message, hits, req.lang.value)

    return AskResponse(answer=text, confidence=round(hits[0].confidence, 3),
                       citations=to_citations(hits), kind="policy", low_confidence=low)
