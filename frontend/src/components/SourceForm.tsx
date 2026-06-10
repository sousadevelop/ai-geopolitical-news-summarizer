import { Plus } from "lucide-react";
import type { FormEvent } from "react";
import type { CreateSourceRequest } from "../api/types";

type SourceFormProps = {
  onSubmit: (payload: CreateSourceRequest) => void;
  isSubmitting: boolean;
};

export function SourceForm({ onSubmit, isSubmitting }: SourceFormProps) {
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);

    onSubmit({
      name: String(form.get("name") || ""),
      url: String(form.get("url") || ""),
      region: String(form.get("region") || "") || undefined,
      language: String(form.get("language") || "") || undefined,
      enabled: form.get("enabled") === "on",
    });
  }

  return (
    <form className="panel form-panel" onSubmit={handleSubmit}>
      <div className="panel-title">
        <Plus size={18} />
        <h2>Adicionar fonte</h2>
      </div>

      <label className="field">
        <span>Nome</span>
        <input name="name" maxLength={120} required />
      </label>

      <label className="field">
        <span>RSS</span>
        <input name="url" type="url" placeholder="https://..." required />
      </label>

      <div className="form-grid">
        <label className="field">
          <span>Regiao</span>
          <input name="region" maxLength={80} placeholder="global" />
        </label>
        <label className="field">
          <span>Idioma</span>
          <input name="language" minLength={2} maxLength={8} placeholder="pt" />
        </label>
      </div>

      <label className="single-check">
        <input name="enabled" type="checkbox" defaultChecked />
        Ativa
      </label>

      <button className="button button-primary" type="submit" disabled={isSubmitting}>
        <Plus size={16} />
        {isSubmitting ? "Salvando" : "Salvar fonte"}
      </button>
    </form>
  );
}
