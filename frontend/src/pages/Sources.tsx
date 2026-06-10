import { Rss } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { apiClient } from "../api/client";
import type { CreateSourceRequest, Source } from "../api/types";
import { EmptyState } from "../components/EmptyState";
import { ErrorBanner } from "../components/ErrorBanner";
import { LoadingState } from "../components/LoadingState";
import { SourceForm } from "../components/SourceForm";
import { formatDate } from "../utils/format";
import { getErrorMessage } from "../utils/errors";

export function Sources() {
  const [sources, setSources] = useState<Source[]>([]);
  const [region, setRegion] = useState("");
  const [enabled, setEnabled] = useState<"all" | "true" | "false">("all");
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSources = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.listSources({
        region,
        enabled: enabled === "all" ? undefined : enabled === "true",
      });
      setSources(response.items);
    } catch (err) {
      setError(getErrorMessage(err));
      setSources([]);
    } finally {
      setIsLoading(false);
    }
  }, [enabled, region]);

  useEffect(() => {
    void loadSources();
  }, [loadSources]);

  async function handleCreateSource(payload: CreateSourceRequest) {
    setIsSubmitting(true);
    setError(null);

    try {
      await apiClient.createSource(payload);
      await loadSources();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="page-stack">
      <div className="page-header">
        <div>
          <h1>Sources</h1>
          <p>Cadastro e consulta de fontes RSS.</p>
        </div>
      </div>

      {error ? <ErrorBanner message={error} onRetry={loadSources} /> : null}

      <div className="two-column sources-layout">
        <SourceForm onSubmit={handleCreateSource} isSubmitting={isSubmitting} />

        <section className="panel">
          <div className="panel-title panel-title-row">
            <div className="panel-title">
              <Rss size={18} />
              <h2>Fontes</h2>
            </div>
            <div className="compact-filters">
              <input
                aria-label="Filtrar por regiao"
                placeholder="Regiao"
                value={region}
                onChange={(event) => setRegion(event.target.value)}
              />
              <select
                aria-label="Filtrar por status"
                value={enabled}
                onChange={(event) => setEnabled(event.target.value as "all" | "true" | "false")}
              >
                <option value="all">Todas</option>
                <option value="true">Ativas</option>
                <option value="false">Inativas</option>
              </select>
            </div>
          </div>

          {isLoading ? (
            <LoadingState />
          ) : sources.length === 0 ? (
            <EmptyState title="Nenhuma fonte encontrada" message="Cadastre uma fonte RSS." />
          ) : (
            <div className="source-list">
              {sources.map((source) => (
                <article className="source-row" key={source.id}>
                  <div>
                    <div className="source-heading">
                      <strong>{source.name}</strong>
                      <span className={`status-badge ${source.enabled ? "active" : "inactive"}`}>
                        {source.enabled ? "Ativa" : "Inativa"}
                      </span>
                    </div>
                    <a href={source.url} target="_blank" rel="noreferrer">
                      {source.url}
                    </a>
                  </div>
                  <div className="source-meta">
                    <span>{source.region || "sem regiao"}</span>
                    <span>{source.language || "auto"}</span>
                    <span>{formatDate(source.created_at)}</span>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
