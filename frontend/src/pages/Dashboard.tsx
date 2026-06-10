import { RefreshCw } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { apiClient } from "../api/client";
import type { HealthResponse, NewsAnalysis } from "../api/types";
import { ApiStatus } from "../components/ApiStatus";
import { ErrorBanner } from "../components/ErrorBanner";
import { LoadingState } from "../components/LoadingState";
import { NewsDetail } from "../components/NewsDetail";
import { NewsList } from "../components/NewsList";
import { getErrorMessage } from "../utils/errors";

export function Dashboard() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [news, setNews] = useState<NewsAnalysis[]>([]);
  const [selected, setSelected] = useState<NewsAnalysis | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState({ limit: 20, region: "", entity: "" });

  const loadDashboard = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [healthResponse, latestResponse] = await Promise.all([
        apiClient.getHealth(),
        apiClient.listLatestNews({
          limit: filters.limit,
          region: filters.region,
          entity: filters.entity,
        }),
      ]);

      setHealth(healthResponse);
      setNews(latestResponse.items);
      setSelected((current) => {
        if (current && latestResponse.items.some((item) => item.id === current.id)) {
          return current;
        }
        return latestResponse.items[0] || null;
      });
    } catch (err) {
      setError(getErrorMessage(err));
      setHealth(null);
      setNews([]);
      setSelected(null);
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    void loadDashboard();
  }, [loadDashboard]);

  return (
    <div className="page-stack">
      <div className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p>Saude da API e ultimas noticias processadas.</p>
        </div>
        <button className="button button-secondary" type="button" onClick={loadDashboard}>
          <RefreshCw size={16} />
          Atualizar
        </button>
      </div>

      {error ? <ErrorBanner message={error} onRetry={loadDashboard} /> : null}

      <ApiStatus health={health} />

      <section className="panel">
        <div className="panel-title panel-title-row">
          <h2>Ultimas noticias</h2>
          <div className="compact-filters">
            <input
              aria-label="Filtrar por regiao"
              placeholder="Regiao"
              value={filters.region}
              onChange={(event) => setFilters((current) => ({ ...current, region: event.target.value }))}
            />
            <input
              aria-label="Filtrar por entidade"
              placeholder="Entidade"
              value={filters.entity}
              onChange={(event) => setFilters((current) => ({ ...current, entity: event.target.value }))}
            />
            <select
              aria-label="Limite"
              value={filters.limit}
              onChange={(event) =>
                setFilters((current) => ({ ...current, limit: Number(event.target.value) }))
              }
            >
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
        </div>

        {isLoading ? (
          <LoadingState />
        ) : (
          <div className="dashboard-grid">
            <NewsList items={news} selectedId={selected?.id} onSelect={setSelected} />
            <NewsDetail item={selected} />
          </div>
        )}
      </section>
    </div>
  );
}
