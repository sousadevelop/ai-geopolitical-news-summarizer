import { afterEach, describe, expect, it, vi } from "vitest";

describe("apiClient", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  async function loadClient(baseUrl?: string) {
    vi.resetModules();
    if (baseUrl) {
      vi.stubEnv("VITE_API_BASE_URL", baseUrl);
    }
    return import("./client");
  }

  it("builds requests with VITE_API_BASE_URL and query parameters", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ items: [], total: 0 }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const { apiClient } = await loadClient("https://api.example.test/v1/");

    await apiClient.listLatestNews({ limit: 5, region: "global", entity: "NATO" });

    expect(apiClient.baseUrl).toBe("https://api.example.test/v1");
    expect(fetchMock).toHaveBeenCalledWith(
      "https://api.example.test/v1/news/latest?limit=5&region=global&entity=NATO",
      expect.objectContaining({
        headers: expect.objectContaining({
          Accept: "application/json",
          "Content-Type": "application/json",
        }),
      }),
    );
  });

  it("serializes analyze payloads and raises structured API errors", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ code: "invalid_url", message: "URL invalida." }), {
        status: 400,
        statusText: "Bad Request",
        headers: { "Content-Type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    const { ApiError, apiClient } = await loadClient();

    await expect(
      apiClient.analyze({
        input_type: "feed",
        url: "ftp://example.com/feed.xml",
        language: "pt",
        max_items: 2,
      }),
    ).rejects.toMatchObject({
      name: "ApiError",
      code: "invalid_url",
      status: 400,
      message: "URL invalida.",
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/analyze",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          input_type: "feed",
          url: "ftp://example.com/feed.xml",
          language: "pt",
          max_items: 2,
        }),
      }),
    );
    expect(ApiError).toBeDefined();
  });
});
