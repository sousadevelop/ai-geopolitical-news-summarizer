from __future__ import annotations

import re

from app.models.schemas import Entity


COUNTRIES = {
    "Afghanistan",
    "Brazil",
    "Brasil",
    "China",
    "France",
    "Franca",
    "França",
    "Germany",
    "India",
    "Iran",
    "Iraq",
    "Israel",
    "Japan",
    "Palestine",
    "Palestina",
    "Russia",
    "Rússia",
    "Syria",
    "Síria",
    "Taiwan",
    "Turkey",
    "Turquia",
    "Ukraine",
    "Ucrania",
    "Ucrânia",
    "United Kingdom",
    "United States",
    "Estados Unidos",
}

REGIONS = {
    "Africa",
    "África",
    "Asia",
    "Ásia",
    "Europe",
    "Europa",
    "Gaza",
    "Latin America",
    "Middle East",
    "Oriente Medio",
    "Oriente Médio",
}

ORG_PATTERNS = (
    r"\b(?:UN|ONU|NATO|OTAN|EU|UE|G7|G20|BRICS|OPEC|OPEP)\b",
    r"\b[A-Z][A-Za-zÀ-ÿ&.-]+(?:\s+[A-Z][A-Za-zÀ-ÿ&.-]+)*\s+(?:Ministry|Council|Agency|Party|Forces|Government)\b",
    r"\b(?:Ministerio|Ministério|Conselho|Agencia|Agência|Partido|Forcas|Forças|Governo)\s+(?:[A-Z][A-Za-zÀ-ÿ&.-]+(?:\s+|$)){1,4}",
)

PERSON_PATTERN = re.compile(
    r"\b(?:President|Prime Minister|Minister|Presidente|Ministro|Chanceler)\s+([A-ZÀ-Ý][A-Za-zÀ-ÿ'-]+(?:\s+[A-ZÀ-Ý][A-Za-zÀ-ÿ'-]+){0,3})"
)


class LightNerService:
    def extract(self, text: str) -> list[Entity]:
        found: dict[tuple[str, str], Entity] = {}
        for country in COUNTRIES:
            if self._contains_phrase(text, country):
                found[(country, "GPE")] = Entity(text=country, label="GPE", confidence=0.86)
        for region in REGIONS:
            if self._contains_phrase(text, region):
                found[(region, "LOC")] = Entity(text=region, label="LOC", confidence=0.82)
        for pattern in ORG_PATTERNS:
            for match in re.finditer(pattern, text):
                value = self._clean(match.group(0))
                if value:
                    found[(value, "ORG")] = Entity(text=value, label="ORG", confidence=0.72)
        for match in PERSON_PATTERN.finditer(text):
            value = self._clean(match.group(1))
            if value and not self._looks_like_place(value):
                found[(value, "PERSON")] = Entity(text=value, label="PERSON", confidence=0.68)
        return sorted(found.values(), key=lambda entity: (entity.label, entity.text))[:40]

    def _contains_phrase(self, text: str, phrase: str) -> bool:
        return re.search(rf"\b{re.escape(phrase)}\b", text, flags=re.IGNORECASE) is not None

    def _clean(self, value: str) -> str:
        return re.sub(r"\s+", " ", value).strip(" ,.;:")

    def _looks_like_place(self, value: str) -> bool:
        lowered = value.lower()
        return any(item.lower() == lowered for item in COUNTRIES | REGIONS)

