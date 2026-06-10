import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiClient } from "../api/client";
import type { NewsAnalysis } from "../api/types";
import { Dashboard } from "./Dashboard";

vi.mock("../api/client", () => ({
  ApiError: class ApiError extends Error {},
  apiClient: {
    getHealth: vi.fn(),
    listLatestNews: vi.fn(),
  },
}));

const mockedApi = vi.mocked(apiClient);

function makeNews(overrides: Partial<NewsAnalysis> = {}): NewsAnalysis {
  return {
    id: "news-1",
    source: {
      id: "src-1",
      name: "Global Feed",
      url: "https://feeds.example.com/global.xml",
      region: "global",
    },
    title: "Border talks resume in Geneva",
    url: "https://news.example.com/border-talks",
    published_at: "2026-06-09T12:00:00Z",
    summary: "Diplomats resumed talks after sanctions and border tension.",
    analysis: {
      key_points: ["Diplomats resumed talks."],
      actors: ["United Nations"],
      regions: ["Geneva"],
      risk_level: "medium",
      context: "Regional talks continued.",
    },
    bias: { label: "low", score: 0.2, signals: [] },
    entities: [{ text: "United Nations", label: "ORG", confidence: 0.9 }],
    processed_at: "2026-06-09T12:05:00Z",
    ...overrides,
  };
}

describe("Dashboard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows loading state and then renders health plus latest news", async () => {
    mockedApi.getHealth.mockResolvedValue({
      status: "ok",
      version: "0.1.0",
      environment: "test",
      cache: { backend: "memory", items: 1 },
    });
    mockedApi.listLatestNews.mockResolvedValue({ items: [makeNews()], total: 1 });

    render(<Dashboard />);

    expect(screen.getByRole("status").textContent).toContain("Carregando dados");
    expect((await screen.findAllByText("Border talks resume in Geneva")).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Diplomats resumed talks after sanctions and border tension.")).toBeTruthy();
    await waitFor(() => expect(mockedApi.listLatestNews).toHaveBeenCalledWith({ limit: 20, region: "", entity: "" }));
  });

  it("renders API errors and clears the news list", async () => {
    mockedApi.getHealth.mockRejectedValue(new Error("API indisponivel"));
    mockedApi.listLatestNews.mockResolvedValue({ items: [makeNews()], total: 1 });

    render(<Dashboard />);

    expect(await screen.findByRole("alert")).toHaveTextContent("API indisponivel");
    expect(screen.getByText("Nenhuma noticia encontrada")).toBeTruthy();
  });
});
