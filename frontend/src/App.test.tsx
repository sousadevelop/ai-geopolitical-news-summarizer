import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import App from "./App";

vi.mock("./api/client", () => ({
  apiClient: { baseUrl: "https://api.example.test" },
}));

vi.mock("./pages/Dashboard", () => ({ Dashboard: () => <div>Dashboard content</div> }));
vi.mock("./pages/Analyze", () => ({ Analyze: () => <div>Analyze content</div> }));
vi.mock("./pages/Sources", () => ({ Sources: () => <div>Sources content</div> }));

describe("App", () => {
  it("shows the GeoPolaris branding and current subtitle", () => {
    render(<App />);

    expect(screen.getByText("GeoPolaris")).toBeVisible();
    expect(screen.getByText("Análise de notícias geopolíticas")).toBeVisible();
    expect(screen.queryByText("GeoNews")).not.toBeInTheDocument();
  });
});
