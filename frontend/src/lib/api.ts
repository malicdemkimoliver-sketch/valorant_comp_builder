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
