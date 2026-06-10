import { ExternalLink } from "lucide-react";
import type { NewsAnalysis } from "../api/types";
import { biasLabel, formatDate, riskLabel } from "../utils/format";
import { EmptyState } from "./EmptyState";

type NewsDetailProps = {
  item: NewsAnalysis | null;
};

export function NewsDetail({ item }: NewsDetailProps) {
  if (!item) {
    return (
      <section className="panel detail-panel">
        <EmptyState title="Selecione uma noticia" message="O detalhe aparece neste painel." />
      </section>
    );
  }

  return (
    <section className="panel detail-panel">
      <div className="detail-header">
        <div>
          <span className="label">{item.source?.name || "Fonte nao informada"}</span>
          <h2>{item.title}</h2>
        </div>
        <a className="icon-link" href={item.url} target="_blank" rel="noreferrer">
          <ExternalLink size={18} />
          Abrir
        </a>
      </div>

      <div className="meta-strip">
        <span>{formatDate(item.published_at || item.processed_at)}</span>
        <span>Risco: {riskLabel(item.analysis.risk_level)}</span>
        <span>Vies: {biasLabel(item.bias.label)} ({Math.round(item.bias.score * 100)}%)</span>
      </div>

      <p className="summary">{item.summary}</p>

      <div className="detail-section">
        <h3>Pontos-chave</h3>
        <ul>
          {item.analysis.key_points.map((point) => (
            <li key={point}>{point}</li>
          ))}
        </ul>
      </div>

      {item.analysis.context ? (
        <div className="detail-section">
          <h3>Contexto</h3>
          <p>{item.analysis.context}</p>
        </div>
      ) : null}

      <div className="tag-grid">
        <TagGroup title="Atores" items={item.analysis.actors} />
        <TagGroup title="Regioes" items={item.analysis.regions} />
        <TagGroup title="Sinais de vies" items={item.bias.signals} />
      </div>

      <div className="detail-section">
        <h3>Entidades</h3>
        {item.entities.length > 0 ? (
          <div className="entity-list">
            {item.entities.map((entity) => (
              <span className="entity-chip" key={`${entity.label}-${entity.text}`}>
                <strong>{entity.text}</strong>
                <span>{entity.label}</span>
              </span>
            ))}
          </div>
        ) : (
          <p className="muted">Sem entidades retornadas.</p>
        )}
      </div>
    </section>
  );
}

function TagGroup({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="tag-group">
      <h3>{title}</h3>
      {items.length > 0 ? (
        <div className="tags">
          {items.map((item) => (
            <span className="tag" key={item}>
              {item}
            </span>
          ))}
        </div>
      ) : (
        <p className="muted">Sem dados.</p>
      )}
    </div>
  );
}
