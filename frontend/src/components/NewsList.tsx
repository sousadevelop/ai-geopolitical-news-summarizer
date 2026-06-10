import type { NewsAnalysis } from "../api/types";
import { formatDate, riskLabel } from "../utils/format";
import { EmptyState } from "./EmptyState";

type NewsListProps = {
  items: NewsAnalysis[];
  selectedId?: string;
  onSelect: (item: NewsAnalysis) => void;
};

export function NewsList({ items, selectedId, onSelect }: NewsListProps) {
  if (items.length === 0) {
    return (
      <EmptyState
        title="Nenhuma noticia encontrada"
        message="Ajuste filtros ou execute uma nova analise."
      />
    );
  }

  return (
    <div className="news-list" aria-label="Ultimas noticias">
      {items.map((item) => (
        <button
          className={`news-row ${selectedId === item.id ? "is-selected" : ""}`}
          type="button"
          key={item.id}
          onClick={() => onSelect(item)}
        >
          <span className={`risk-dot risk-${item.analysis.risk_level}`} aria-hidden="true" />
          <span className="news-row-body">
            <strong>{item.title}</strong>
            <span>
              {item.source?.name || "Fonte nao informada"} -{" "}
              {formatDate(item.published_at || item.processed_at)}
            </span>
          </span>
          <span className="pill">{riskLabel(item.analysis.risk_level)}</span>
        </button>
      ))}
    </div>
  );
}
