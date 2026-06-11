import type { MapMeta, ScoreResult, Suggestion } from "./types";

// Client-side calls go through the /api/* rewrite proxy (same origin).

async function post<T>(
  path: string,
  body: unknown,
  signal?: AbortSignal
): Promise<T> {
  const res = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });
  if (!res.ok) {
    throw new Error(`${path} failed: ${res.status}`);
  }
  return res.json();
}

export function fetchScore(
  agents: string[],
  map: string,
  signal?: AbortSignal
): Promise<ScoreResult> {
  return post("/api/score", { agents, map }, signal);
}

export async function fetchSuggestions(
  agents: string[],
  map: string,
  signal?: AbortSignal
): Promise<Suggestion[]> {
  const data = await post<{ map: string; suggestions: Suggestion[] }>(
    "/api/suggest",
    { agents, map, top_n: 3 },
    signal
  );
  return data.suggestions;
}

export async function fetchMeta(
  map: string,
  signal?: AbortSignal
): Promise<MapMeta> {
  const res = await fetch(`/api/meta/${encodeURIComponent(map)}`, { signal });
  if (!res.ok) {
    throw new Error(`/api/meta/${map} failed: ${res.status}`);
  }
  return res.json();
}

export type RefreshStatus = {
  running: boolean;
  last_error: string | null;
  last_updated: string | null;
  series: string | null;
  stale: boolean;
};

export async function triggerMetaRefresh(): Promise<RefreshStatus> {
  const res = await fetch("/api/meta/refresh", { method: "POST" });
  if (!res.ok) throw new Error(`refresh failed: ${res.status}`);
  return res.json();
}

export async function fetchMetaStatus(): Promise<RefreshStatus> {
  const res = await fetch("/api/meta/status");
  if (!res.ok) throw new Error(`status failed: ${res.status}`);
  return res.json();
}
