from __future__ import annotations

import re

from app.models.schemas import BiasReport


LOADED_WORDS = {
    "allegedly",
    "atrocity",
    "brutal",
    "catastrophic",
    "clearly",
    "cruel",
    "devastating",
    "evil",
    "falsely",
    "inaceitavel",
    "inaceitável",
    "massacre",
    "obviously",
    "regime",
    "supostamente",
    "terrorist",
    "terrorista",
    "tyrant",
    "unprovoked",
}

ATTRIBUTION_WORDS = {
    "according",
    "afirmou",
    "alegou",
    "conforme",
    "de acordo",
    "disse",
    "relatou",
    "reported",
    "said",
    "segundo",
}


class BiasAnalyzer:
    def analyze(self, text: str) -> BiasReport:
        lowered = text.lower()
        signals: list[str] = []
        loaded_hits = sorted({word for word in LOADED_WORDS if word in lowered})
        if loaded_hits:
            signals.append(f"linguagem carregada: {', '.join(loaded_hits[:6])}")
        attribution_count = sum(lowered.count(word) for word in ATTRIBUTION_WORDS)
        sentence_count = max(1, len(re.findall(r"[.!?]", text)))
        attribution_ratio = attribution_count / sentence_count
        if attribution_ratio < 0.08 and sentence_count >= 4:
            signals.append("baixa atribuicao explicita a fontes")
        if self._has_one_sided_markers(lowered):
            signals.append("marcadores de enquadramento unilateral")
        score = min(1.0, (len(loaded_hits) * 0.08) + (0.25 if attribution_ratio < 0.08 else 0) + (0.2 if signals else 0))
        if not text.strip():
            return BiasReport(label="unknown", score=0, signals=[])
        if score >= 0.6:
            label = "high"
        elif score >= 0.3:
            label = "moderate"
        else:
            label = "low"
        return BiasReport(label=label, score=round(score, 3), signals=signals)

    def _has_one_sided_markers(self, text: str) -> bool:
        markers = ("only ", "sempre ", "nunca ", "todos ", "none ", "without evidence", "sem evidencias")
        return any(marker in text for marker in markers)

