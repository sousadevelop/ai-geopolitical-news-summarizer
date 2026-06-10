import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { apiClient } from "../api/client";
import type { Source } from "../api/types";
import { Sources } from "./Sources";

vi.mock("../api/client", () => ({
  ApiError: class ApiError extends Error {},
  apiClient: {
    listSources: vi.fn(),
    createSource: vi.fn(),
  },
}));

const mockedApi = vi.mocked(apiClient);

function makeSource(overrides: Partial<Source> = {}): Source {
  return {
    id: "src-1",
    name: "Global Feed",
    url: "https://feeds.example.com/global.xml",
    region: "global",
    language: "en",
    enabled: true,
    created_at: "2026-06-09T12:00:00Z",
    ...overrides,
  };
}

describe("Sources", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("lists sources returned by the API", async () => {
    mockedApi.listSources.mockResolvedValue({ items: [makeSource()] });

    render(<Sources />);

    expect(await screen.findByText("Global Feed")).toBeTruthy();
    expect(screen.getByText("https://feeds.example.com/global.xml")).toBeTruthy();
    expect(screen.getAllByText("Ativa").length).toBeGreaterThanOrEqual(1);
  });

  it("shows create-source errors without replacing the current list", async () => {
    const user = userEvent.setup();
    mockedApi.listSources.mockResolvedValue({ items: [makeSource()] });
    mockedApi.createSource.mockRejectedValue(new Error("Fonte ja cadastrada."));

    render(<Sources />);

    expect(await screen.findByText("Global Feed")).toBeTruthy();
    await user.type(screen.getByLabelText("Nome"), "Global Feed");
    await user.type(screen.getByLabelText("RSS"), "https://feeds.example.com/global.xml");
    await user.click(screen.getByRole("button", { name: /Salvar fonte/i }));

    expect(mockedApi.createSource).toHaveBeenCalledWith({
      name: "Global Feed",
      url: "https://feeds.example.com/global.xml",
      region: undefined,
      language: undefined,
      enabled: true,
    });
    expect(await screen.findByRole("alert")).toHaveTextContent("Fonte ja cadastrada.");
    expect(screen.getByText("Global Feed")).toBeTruthy();
  });
});
