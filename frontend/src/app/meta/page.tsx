import type { Agent, MapInfo, MapMeta } from "@/lib/types";
import { MetaClient } from "./meta-client";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

async function getJson<T>(path: string): Promise<T | null> {
  const res = await fetch(`${API_URL}${path}`);
  if (!res.ok) return null;
  return res.json();
}

export default async function MetaPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const [agents, allMaps] = await Promise.all([
    getJson<Agent[]>("/api/agents"),
    getJson<MapInfo[]>("/api/maps"),
  ]);
  if (!agents || !allMaps) {
    throw new Error("Backend unavailable — could not load agents/maps");
  }

  // Only maps that actually have tier data belong on this page
  const maps = allMaps.filter((m) => m.has_meta_data);

  let initialMap = maps.find((m) => m.in_active_pool)?.name ?? maps[0]?.name;
  if (typeof params.map === "string") {
    const match = maps.find(
      (m) => m.name.toLowerCase() === (params.map as string).toLowerCase()
    );
    if (match) initialMap = match.name;
  }

  const initialMeta = initialMap
    ? await getJson<MapMeta>(`/api/meta/${encodeURIComponent(initialMap)}`)
    : null;

  return (
    <MetaClient
      agents={agents}
      maps={maps}
      initialMap={initialMap ?? "Ascent"}
      initialMeta={initialMeta}
    />
  );
}
