import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiClient } from "../api/client";
import type { NewsAnalysis } from "../api/types";
import { Analyze } from "./Analyze";

vi.mock("../api/client", () => ({
  ApiError: class ApiError extends Error {},
  apiClient: {
    analyze: vi.fn(),
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

describe("Analyze", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("submits feed analysis payloads and renders the result", async () => {
    const user = userEvent.setup();
    mockedApi.analyze.mockResolvedValue({
      items: [makeNews()],
      processed_count: 1,
      cached_count: 0,
    });

    render(<Analyze />);

    await user.selectOptions(screen.getByLabelText("Tipo"), "feed");
    await user.type(screen.getByLabelText("URL"), "https://feeds.example.com/global.xml");
    await user.clear(screen.getByLabelText("Max. itens"));
    await user.type(screen.getByLabelText("Max. itens"), "2");
    await user.click(screen.getByRole("button", { name: /Analisar/i }));

    expect(mockedApi.analyze).toHaveBeenCalledWith({
      input_type: "feed",
      url: "https://feeds.example.com/global.xml",
      language: "auto",
      max_items: 2,
      include_entities: true,
      force_refresh: false,
    });
    expect((await screen.findAllByText("Border talks resume in Geneva")).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("1 processadas - 0 cache")).toBeTruthy();
  });

  it("shows errors returned by the API client", async () => {
    const user = userEvent.setup();
    mockedApi.analyze.mockRejectedValue(new Error("URL invalida."));

    render(<Analyze />);

    await user.type(screen.getByLabelText("URL"), "https://bad.example.com/article");
    await user.click(screen.getByRole("button", { name: /Analisar/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent("URL invalida.");
  });
});
