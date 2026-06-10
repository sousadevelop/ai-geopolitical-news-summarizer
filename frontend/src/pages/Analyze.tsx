import { useState } from "react";
import { apiClient } from "../api/client";
import type { AnalyzeRequest, AnalyzeResponse, NewsAnalysis } from "../api/types";
import { AnalyzeForm } from "../components/AnalyzeForm";
import { ErrorBanner } from "../components/ErrorBanner";
import { LoadingState } from "../components/LoadingState";
import { NewsDetail } from "../components/NewsDetail";
import { NewsList } from "../components/NewsList";
import { getErrorMessage } from "../utils/errors";

export function Analyze() {
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [selected, setSelected] = useState<NewsAnalysis | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAnalyze(payload: AnalyzeRequest) {
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await apiClient.analyze(payload);
      setResult(response);
      setSelected(response.items[0] || null);
    } catch (err) {
      setError(getErrorMessage(err));
      setResult(null);
      setSelected(null);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="page-stack">
      <div className="page-header">
        <div>
          <h1>Analyze</h1>
          <p>Processamento sob demanda de URL ou feed RSS.</p>
        </div>
      </div>

      {error ? <ErrorBanner message={error} /> : null}

      <div className="two-column">
        <AnalyzeForm onSubmit={handleAnalyze} isSubmitting={isSubmitting} />

        <section className="panel">
          <div className="panel-title panel-title-row">
            <h2>Resultado</h2>
            {result ? (
              <span className="result-count">
                {result.processed_count} processadas - {result.cached_count || 0} cache
              </span>
            ) : null}
          </div>
          {isSubmitting ? (
            <LoadingState label="Analisando conteudo" />
          ) : result ? (
            <div className="dashboard-grid">
              <NewsList items={result.items} selectedId={selected?.id} onSelect={setSelected} />
              <NewsDetail item={selected} />
            </div>
          ) : (
            <NewsDetail item={null} />
          )}
        </section>
      </div>
    </div>
  );
}
