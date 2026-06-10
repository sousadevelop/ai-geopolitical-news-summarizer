export type CacheStatus = {
  backend: "memory" | "json_file";
  items: number;
};

export type HealthResponse = {
  status: "ok";
  version: string;
  environment: string;
  cache: CacheStatus;
};

export type Source = {
  id: string;
  name: string;
  url: string;
  region?: string | null;
  language?: string | null;
  enabled: boolean;
  created_at: string;
};

export type CreateSourceRequest = {
  name: string;
  url: string;
  region?: string;
  language?: string;
  enabled?: boolean;
};

export type SourceListResponse = {
  items: Source[];
};

export type AnalyzeRequest = {
  input_type: "url" | "feed";
  url: string;
  language?: string;
  max_items?: number;
  include_entities?: boolean;
  force_refresh?: boolean;
};

export type AnalyzeResponse = {
  items: NewsAnalysis[];
  processed_count: number;
  cached_count?: number;
};

export type LatestNewsResponse = {
  items: NewsAnalysis[];
  total: number;
};

export type SourceRef = {
  id: string;
  name: string;
  url: string;
  region?: string | null;
};

export type GeopoliticalAnalysis = {
  key_points: string[];
  actors: string[];
  regions: string[];
  risk_level: "low" | "medium" | "high" | "unknown";
  context?: string;
};

export type BiasReport = {
  label: "low" | "moderate" | "high" | "unknown";
  score: number;
  signals: string[];
};

export type Entity = {
  text: string;
  label: string;
  confidence?: number | null;
};

export type NewsAnalysis = {
  id: string;
  source?: SourceRef | null;
  title: string;
  url: string;
  published_at?: string | null;
  summary: string;
  analysis: GeopoliticalAnalysis;
  bias: BiasReport;
  entities: Entity[];
  processed_at: string;
};

export type ErrorResponse = {
  code: string;
  message: string;
  details?: Record<string, unknown>;
};

export type LatestNewsFilters = {
  limit?: number;
  region?: string;
  source_id?: string;
  entity?: string;
};

export type SourceFilters = {
  enabled?: boolean;
  region?: string;
};
