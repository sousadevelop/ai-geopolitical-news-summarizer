import type { BiasReport, GeopoliticalAnalysis } from "../api/types";

export function formatDate(value?: string | null) {
  if (!value) {
    return "Sem data";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(date);
}

export function riskLabel(value: GeopoliticalAnalysis["risk_level"]) {
  const labels: Record<GeopoliticalAnalysis["risk_level"], string> = {
    low: "Baixo",
    medium: "Medio",
    high: "Alto",
    unknown: "Indefinido",
  };

  return labels[value];
}

export function biasLabel(value: BiasReport["label"]) {
  const labels: Record<BiasReport["label"], string> = {
    low: "Baixo",
    moderate: "Moderado",
    high: "Alto",
    unknown: "Indefinido",
  };

  return labels[value];
}
