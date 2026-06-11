import { decodeComp } from "@/lib/comp-code";
import type {
  Agent,
  MapInfo,
  PresetsResponse,
  TeamCompsResponse,
} from "@/lib/types";
import { BuilderClient } from "./builder-client";

const API_URL = process.env.API_URL ?? "http://localhost:8000";

async function getJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_URL}${path}`);
  if (!res.ok) {
    throw new Error(`${path} failed: ${res.status}`);
  }
  return res.json();
}

export default async function BuilderPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const params = await searchParams;
  const [agents, maps, presets, teamComps] = await Promise.all([
    getJson<Agent[]>("/api/agents"),
    getJson<MapInfo[]>("/api/maps"),
    getJson<PresetsResponse>("/api/presets"),
    getJson<TeamCompsResponse>("/api/team-comps"),
  ]);

  const agentNames = new Set(agents.map((a) => a.name));
  const defaultMap =
    maps.find((m) => m.in_active_pool)?.name ?? maps[0]?.name ?? "Ascent";

  let initialMap = defaultMap;
  let initialAgents: string[] = [];

  const code = typeof params.code === "string" ? decodeComp(params.code) : null;
  if (code && maps.some((m) => m.name === code.map)) {
    initialMap = code.map;
    initialAgents = code.agents.filter((n) => agentNames.has(n));
  } else {
    if (typeof params.map === "string") {
      const match = maps.find(
        (m) => m.name.toLowerCase() === (params.map as string).toLowerCase()
      );
      if (match) initialMap = match.name;
    }
    if (typeof params.agents === "string") {
      initialAgents = params.agents
        .split(",")
        .map((n) => n.trim())
        .filter((n) => agentNames.has(n))
        .slice(0, 5);
    }
  }

  return (
    <BuilderClient
      agents={agents}
      maps={maps}
      presets={presets}
      teamComps={teamComps}
      initialMap={initialMap}
      initialAgents={initialAgents}
    />
  );
}
