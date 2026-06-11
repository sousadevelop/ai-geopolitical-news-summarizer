import { Activity, BarChart3, Rss } from "lucide-react";
import type { ReactNode } from "react";
import { useState } from "react";
import { Analyze } from "./pages/Analyze";
import { Dashboard } from "./pages/Dashboard";
import { Sources } from "./pages/Sources";

type Page = "dashboard" | "analyze" | "sources";

const navItems: Array<{ id: Page; label: string; icon: ReactNode }> = [
  { id: "dashboard", label: "Dashboard", icon: <BarChart3 size={18} /> },
  { id: "analyze", label: "Analyze", icon: <Activity size={18} /> },
  { id: "sources", label: "Sources", icon: <Rss size={18} /> },
];

export default function App() {
  const [page, setPage] = useState<Page>("dashboard");

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">G</span>
          <div>
            <strong>GeoPolaris</strong>
            <span>Análise de notícias geopolíticas</span>
          </div>
        </div>

        <nav className="nav-list" aria-label="Principal">
          {navItems.map((item) => (
            <button
              className={`nav-item ${page === item.id ? "is-active" : ""}`}
              type="button"
              key={item.id}
              onClick={() => setPage(item.id)}
            >
              {item.icon}
              <span>{item.label}</span>
            </button>
          ))}
        </nav>
      </aside>

      <main className="main-content">
        {page === "dashboard" ? <Dashboard /> : null}
        {page === "analyze" ? <Analyze /> : null}
        {page === "sources" ? <Sources /> : null}
      </main>
    </div>
  );
}
