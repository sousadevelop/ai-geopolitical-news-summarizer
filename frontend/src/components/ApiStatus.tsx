import { Activity, Database } from "lucide-react";
import type { HealthResponse } from "../api/types";

type ApiStatusProps = {
  health: HealthResponse | null;
};

export function ApiStatus({ health }: ApiStatusProps) {
  if (!health) {
    return (
      <section className="panel status-panel">
        <div className="panel-title">
          <Activity size={18} />
          <h2>Status da API</h2>
        </div>
        <p className="muted">Sem status disponivel.</p>
      </section>
    );
  }

  return (
    <section className="panel status-panel">
      <div className="panel-title">
        <Activity size={18} />
        <h2>Status da API</h2>
      </div>
      <div className="status-grid">
        <div>
          <span className="label">Estado</span>
          <strong className="status-ok">{health.status}</strong>
        </div>
        <div>
          <span className="label">Ambiente</span>
          <strong>{health.environment}</strong>
        </div>
        <div>
          <span className="label">Versao</span>
          <strong>{health.version}</strong>
        </div>
        <div>
          <span className="label">Cache</span>
          <strong className="inline-metric">
            <Database size={16} />
            {health.cache.backend} - {health.cache.items}
          </strong>
        </div>
      </div>
    </section>
  );
}
