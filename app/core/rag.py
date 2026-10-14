"""Grounded retrieval over the policy corpus — BM25 with Arabic-aware
normalization, title boosts and a calibrated confidence score.

Deliberately dependency-free (the corpus is ~15 short policies; hybrid search
and cross-encoders are pilot-stage per the engineering workbook).
"""
from __future__ import annotations

import math
import re
import unicodedata
from dataclasses import dataclass

from app.schemas.common import Citation
from app.services.data import PolicyChunk

_K1, _B, _SATURATION = 1.5, 0.75, 3.0  # BM25 params; saturation: raw score 3 -> conf 0.5

_AR_DIACRITICS = re.compile(r"[\u064B-\u0652\u0640]")
_STOP = {
    "the", "a", "an", "is", "are", "do", "does", "i", "my", "me", "for", "of", "to", "in", "on",
    "and", "or", "it", "at", "be", "can", "how", "what", "when", "where", "who", "why", "get",
    "have", "has", "with", "if", "you", "your", "we", "us", "this", "that", "am", "still", "no",
    "not", "yet", "day", "days",
    "من", "في", "على", "عن", "الى", "إلى", "هل", "ما", "هذا", "هذه", "ان", "أن", "انا", "أنا",
    "لي", "مع", "او", "أو", "كيف", "متى", "اين", "أين", "ماذا", "ليوم", "يوم", "الاو", "ثم",
}


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    text = _AR_DIACRITICS.sub("", text)
    for src, dst in (("أ", "ا"), ("إ", "ا"), ("آ", "ا"), ("ى", "ي"), ("ة", "ه"), ("ؤ", "و"), ("ئ", "ي")):
        text = text.replace(src, dst)
    return text


def tokenize(text: str) -> list[str]:
    return [t for t in re.split(r"[^\w]+", normalize(text)) if len(t) >= 2 and t not in _STOP]


@dataclass
class Hit:
    chunk: PolicyChunk
    score: float            # raw BM25 (with boosts)
    confidence: float       # calibrated 0..1


class PolicyIndex:
    def __init__(self, chunks: list[PolicyChunk]) -> None:
        self.chunks = chunks
        self._docs: list[list[str]] = []
        self._meta: list[tuple[list[str], list[str]]] = []  # (title tokens, section tokens)
        for c in chunks:
            body = tokenize(c.text)
            self._docs.append(body)
            self._meta.append((tokenize(c.title), tokenize(c.section)))
        self._build_idf()

    def _build_idf(self) -> None:
        n = len(self._docs)
        self.avg_len = sum(len(d) for d in self._docs) / max(1, n)
        df: dict[str, int] = {}
        for d in self._docs:
            for t in set(d):
                df[t] = df.get(t, 0) + 1
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def _bm25(self, query: list[str], doc: list[str]) -> float:
        if not doc:
            return 0.0
        freq: dict[str, int] = {}
        for t in doc:
            freq[t] = freq.get(t, 0) + 1
        dl = len(doc)
        score = 0.0
        for t in query:
            if t in freq and t in self.idf:
                tf = freq[t]
                score += self.idf[t] * tf * (_K1 + 1) / (tf + _K1 * (1 - _B + _B * dl / self.avg_len))
        return score

    def search(self, question: str, lang: str, top_k: int = 4) -> list[Hit]:
        q = tokenize(question)
        if not q:
            return []
        scored: list[tuple[float, float, int]] = []  # (anchor_hit, boosted, index)
        for i, doc in enumerate(self._docs):
            if self.chunks[i].lang != lang:
                continue
            base = self._bm25(q, doc)
            if base <= 0:
                continue
            title_tokens, section_tokens = self._meta[i]
            anchor_tokens = set(title_tokens) | set(section_tokens)
            anchor_hit = sum(1 for t in q if t in anchor_tokens) / len(q)
            boosted = base * (1 + 0.5 * anchor_hit)
            scored.append((anchor_hit, boosted, i))
        # a heading match is a precise navigational anchor — rank it first
        scored.sort(key=lambda x: (-x[0], -x[1]))
        return [Hit(chunk=self.chunks[i], score=b, confidence=b / (b + _SATURATION))
                for _, b, i in scored[:top_k]]


_INDEX: PolicyIndex | None = None


def get_index(store) -> PolicyIndex:
    global _INDEX
    if _INDEX is None:
        _INDEX = PolicyIndex(store.policy_chunks)
    return _INDEX


def reset_index() -> None:
    global _INDEX
    _INDEX = None


def extractive_answer(question: str, hits: list[Hit], lang: str) -> str:
    """Answer composed strictly from retrieved policy text — zero hallucination."""
    best = hits[0]
    sentences = [s.strip() for s in re.split(r"(?<=[.!?؟])\s+", best.chunk.text) if s.strip()]
    q_tokens = set(tokenize(question))
    scored = [(sum(1 for t in tokenize(s) if t in q_tokens), s) for s in sentences]
    scored.sort(key=lambda x: -x[0])
    picked = [s for n, s in scored[:2] if n > 0] or sentences[:2]
    body = " ".join(picked)
    if lang == "ar":
        return f"حسب سياسة «{best.chunk.title}» ({best.chunk.policy_id}): {body}"
    return f"Per the {best.chunk.title} policy ({best.chunk.policy_id}): {body}"


def to_citations(hits: list[Hit], max_cites: int = 2) -> list[Citation]:
    """One chip per policy (first section wins) — the drill-down shows all sections."""
    seen: set[str] = set()
    out: list[Citation] = []
    for h in hits:
        if h.chunk.policy_id in seen:
            continue
        seen.add(h.chunk.policy_id)
        out.append(Citation(policy_id=h.chunk.policy_id, title=h.chunk.title,
                            section=h.chunk.section or None, lang=h.chunk.lang))
        if len(out) >= max_cites:
            break
    return out
