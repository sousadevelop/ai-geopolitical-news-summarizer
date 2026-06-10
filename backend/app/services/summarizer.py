from __future__ import annotations

import math
import re
from collections import Counter


STOPWORDS = {
    "a",
    "about",
    "and",
    "ao",
    "aos",
    "as",
    "com",
    "da",
    "das",
    "de",
    "do",
    "dos",
    "e",
    "em",
    "for",
    "from",
    "in",
    "is",
    "na",
    "nas",
    "no",
    "nos",
    "o",
    "of",
    "on",
    "os",
    "para",
    "por",
    "que",
    "the",
    "to",
    "um",
    "uma",
    "with",
}


class LocalSummarizer:
    def summarize(self, text: str, language: str = "auto", length: str = "medium") -> str:
        sentences = self._sentences(text)
        if not sentences:
            return ""
        target = {"short": 2, "medium": 4, "long": 7}.get(length, 4)
        selected = self._rank_sentences(sentences, target)
        return " ".join(selected)

    def key_points(self, text: str, limit: int = 4) -> list[str]:
        sentences = self._sentences(text)
        return self._rank_sentences(sentences, limit)

    def _sentences(self, text: str) -> list[str]:
        normalized = re.sub(r"\s+", " ", text).strip()
        if not normalized:
            return []
        parts = re.split(r"(?<=[.!?])\s+", normalized)
        sentences = [part.strip() for part in parts if len(part.strip()) >= 35]
        if sentences:
            return sentences
        return [normalized[:600]]

    def _rank_sentences(self, sentences: list[str], limit: int) -> list[str]:
        if len(sentences) <= limit:
            return sentences
        words = [
            word
            for sentence in sentences
            for word in self._words(sentence)
            if word not in STOPWORDS and len(word) > 2
        ]
        frequencies = Counter(words)
        if not frequencies:
            return sentences[:limit]
        scored: list[tuple[int, float, str]] = []
        for index, sentence in enumerate(sentences):
            sentence_words = self._words(sentence)
            score = sum(frequencies[word] for word in sentence_words) / math.sqrt(len(sentence_words) or 1)
            if index < 2:
                score *= 1.15
            scored.append((index, score, sentence))
        top = sorted(scored, key=lambda item: item[1], reverse=True)[:limit]
        return [sentence for index, _, sentence in sorted(top, key=lambda item: item[0])]

    def _words(self, sentence: str) -> list[str]:
        return re.findall(r"[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'-]{2,}", sentence.lower())

