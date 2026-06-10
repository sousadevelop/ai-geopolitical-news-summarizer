import { Play } from "lucide-react";
import type { FormEvent } from "react";
import type { AnalyzeRequest } from "../api/types";

type AnalyzeFormProps = {
  onSubmit: (payload: AnalyzeRequest) => void;
  isSubmitting: boolean;
};

export function AnalyzeForm({ onSubmit, isSubmitting }: AnalyzeFormProps) {
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const inputType = String(form.get("input_type")) as "url" | "feed";

    onSubmit({
      input_type: inputType,
      url: String(form.get("url") || ""),
      language: String(form.get("language") || "auto"),
      max_items: inputType === "feed" ? Number(form.get("max_items") || 10) : undefined,
      include_entities: form.get("include_entities") === "on",
      force_refresh: form.get("force_refresh") === "on",
    });
  }

  return (
    <form className="panel form-panel" onSubmit={handleSubmit}>
      <div className="panel-title">
        <Play size={18} />
        <h2>Nova analise</h2>
      </div>

      <label className="field">
        <span>Tipo</span>
        <select name="input_type" defaultValue="url">
          <option value="url">URL</option>
          <option value="feed">Feed RSS</option>
        </select>
      </label>

      <label className="field">
        <span>URL</span>
        <input name="url" type="url" placeholder="https://..." required />
      </label>

      <div className="form-grid">
        <label className="field">
          <span>Idioma</span>
          <input name="language" defaultValue="auto" minLength={2} maxLength={8} />
        </label>
        <label className="field">
          <span>Max. itens</span>
          <input name="max_items" type="number" defaultValue={10} min={1} max={20} />
        </label>
      </div>

      <div className="check-row">
        <label>
          <input name="include_entities" type="checkbox" defaultChecked />
          Incluir entidades
        </label>
        <label>
          <input name="force_refresh" type="checkbox" />
          Reprocessar
        </label>
      </div>

      <button className="button button-primary" type="submit" disabled={isSubmitting}>
        <Play size={16} />
        {isSubmitting ? "Analisando" : "Analisar"}
      </button>
    </form>
  );
}
