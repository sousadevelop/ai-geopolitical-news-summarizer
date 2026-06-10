import type {
  AnalyzeRequest,
  AnalyzeResponse,
  CreateSourceRequest,
  ErrorResponse,
  HealthResponse,
  LatestNewsFilters,
  LatestNewsResponse,
  NewsAnalysis,
  Source,
  SourceFilters,
  SourceListResponse,
} from "./types";

const DEFAULT_API_BASE_URL = "http://localhost:8000";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, "") || DEFAULT_API_BASE_URL;

export class ApiError extends Error {
  code: string;
  status: number;
  details?: Record<string, unknown>;

  constructor(status: number, error: ErrorResponse) {
    super(error.message);
    this.name = "ApiError";
    this.status = status;
    this.code = error.code;
    this.details = error.details;
  }
}

function appendQuery(path: string, params: Record<string, string | number | boolean | undefined>) {
  const query = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== "") {
      query.set(key, String(value));
    }
  });

  const suffix = query.toString();
  return suffix ? `${path}?${suffix}` : path;
}

async function parseApiError(response: Response): Promise<ErrorResponse> {
  try {
    const payload = (await response.json()) as Partial<ErrorResponse>;
    return {
      code: payload.code || `HTTP_${response.status}`,
      message: payload.message || response.statusText || "Erro ao acessar a API.",
      details: payload.details,
    };
  } catch {
    return {
      code: `HTTP_${response.status}`,
      message: response.statusText || "Erro ao acessar a API.",
    };
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...init?.headers,
    },
    ...init,
  });

  if (!response.ok) {
    throw new ApiError(response.status, await parseApiError(response));
  }

  return response.json() as Promise<T>;
}

export const apiClient = {
  baseUrl: API_BASE_URL,

  getHealth() {
    return request<HealthResponse>("/health");
  },

  listLatestNews(filters: LatestNewsFilters = {}) {
    return request<LatestNewsResponse>(
      appendQuery("/news/latest", {
        limit: filters.limit,
        region: filters.region,
        source_id: filters.source_id,
        entity: filters.entity,
      }),
    );
  },

  getNews(id: string) {
    return request<NewsAnalysis>(`/news/${encodeURIComponent(id)}`);
  },

  listSources(filters: SourceFilters = {}) {
    return request<SourceListResponse>(
      appendQuery("/sources", {
        enabled: filters.enabled,
        region: filters.region,
      }),
    );
  },

  createSource(payload: CreateSourceRequest) {
    return request<Source>("/sources", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  analyze(payload: AnalyzeRequest) {
    return request<AnalyzeResponse>("/analyze", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },
};
