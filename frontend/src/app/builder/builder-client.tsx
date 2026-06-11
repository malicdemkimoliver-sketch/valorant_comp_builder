"use client";

import { useEffect, useMemo, useState } from "react";
import { fetchMeta, fetchScore, fetchSuggestions } from "@/lib/api";
import type {
  Agent,
  MapInfo,
  PresetsResponse,
  RatedMetaEntry,
  ScoreResult,
  Suggestion,
} from "@/lib/types";
import { AgentGrid } from "@/components/builder/agent-grid";
import { CompSlots } from "@/components/builder/comp-slots";
import { ExportImage } from "@/components/builder/export-card";
import { MapSelect } from "@/components/builder/map-select";
import { Presets } from "@/components/builder/presets";
import { ScorePanel } from "@/components/builder/score-panel";
import { Share } from "@/components/builder/share";
import { Suggestions } from "@/components/builder/suggestions";

export function BuilderClient({
  agents,
  maps,
  presets,
  initialMap,
  initialAgents,
}: {
  agents: Agent[];
  maps: MapInfo[];
  presets: PresetsResponse;
  initialMap: string;
  initialAgents: string[];
}) {
  const [mapName, setMapName] = useState(initialMap);
  const [selected, setSelected] = useState<string[]>(initialAgents);
  const [metaByName, setMetaByName] = useState<Record<string, RatedMetaEntry>>(
    {}
  );
  const [score, setScore] = useState<ScoreResult | null>(null);
  const [scoreLoading, setScoreLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [suggestLoading, setSuggestLoading] = useState(false);

  const agentsByName = useMemo(
    () => Object.fromEntries(agents.map((a) => [a.name, a])),
    [agents]
  );
  const selectedAgents = selected
    .map((name) => agentsByName[name])
    .filter(Boolean);
  const currentMap = maps.find((m) => m.name === mapName);

  // Meta badges for the selected map (maps without data 404 -> clear badges)
  useEffect(() => {
    const ctrl = new AbortController();
    fetchMeta(mapName, ctrl.signal)
      .then((meta) => {
        const flat: Record<string, RatedMetaEntry> = {};
        for (const [tier, entries] of Object.entries(meta.tiers)) {
          for (const entry of entries) {
            flat[entry.name] = { ...entry, tier };
          }
        }
        setMetaByName(flat);
      })
      .catch((err) => {
        if ((err as Error).name !== "AbortError") setMetaByName({});
      });
    return () => ctrl.abort();
  }, [mapName]);

  // Debounced live score + suggestions
  useEffect(() => {
    const ctrl = new AbortController();
    const timer = setTimeout(
      () => {
        if (selected.length === 0) {
          setScore(null);
          setSuggestions([]);
          setScoreLoading(false);
          setSuggestLoading(false);
          return;
        }
        setScoreLoading(true);
        setSuggestLoading(selected.length <= 4);
        fetchScore(selected, mapName, ctrl.signal)
          .then((result) => {
            setScore(result);
            setScoreLoading(false);
          })
          .catch((err) => {
            if ((err as Error).name !== "AbortError") setScoreLoading(false);
          });
        if (selected.length <= 4) {
          fetchSuggestions(selected, mapName, ctrl.signal)
            .then((result) => {
              setSuggestions(result);
              setSuggestLoading(false);
            })
            .catch((err) => {
              if ((err as Error).name !== "AbortError")
                setSuggestLoading(false);
            });
        } else {
          setSuggestions([]);
        }
      },
      selected.length === 0 ? 0 : 250
    );
    return () => {
      clearTimeout(timer);
      ctrl.abort();
    };
  }, [selected, mapName]);

  // Keep the URL shareable without triggering server refetches
  useEffect(() => {
    const params = new URLSearchParams({ map: mapName });
    if (selected.length > 0) params.set("agents", selected.join(","));
    window.history.replaceState(null, "", `/builder?${params}`);
  }, [mapName, selected]);

  function toggleAgent(name: string) {
    setSelected((prev) =>
      prev.includes(name)
        ? prev.filter((n) => n !== name)
        : prev.length < 5
          ? [...prev, name]
          : prev
    );
  }

  function loadComp(map: string, agentNames: string[]): boolean {
    const resolvedMap = maps.find(
      (m) => m.name.toLowerCase() === map.toLowerCase()
    );
    if (!resolvedMap || agentNames.some((n) => !agentsByName[n])) {
      return false;
    }
    setMapName(resolvedMap.name);
    setSelected(agentNames.slice(0, 5));
    return true;
  }

  return (
    <main className="mx-auto max-w-7xl px-6 py-8">
      <div className="mb-5 flex items-baseline justify-between">
        <h1 className="font-display text-3xl font-bold tracking-[0.1em]">
          <span className="text-vred">COMP</span>{" "}
          <span className="text-vorange">BUILDER</span>
        </h1>
        <span className="font-display text-sm tracking-[0.2em] text-slate-400">
          {mapName.toUpperCase()}
          {currentMap && !currentMap.has_meta_data && " · NO META DATA"}
        </span>
      </div>

      <MapSelect maps={maps} selected={mapName} onSelect={setMapName} />

      <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_330px]">
        <div>
          <CompSlots
            agents={selectedAgents}
            onRemove={toggleAgent}
            onReset={() => setSelected([])}
          />
          <Presets
            presets={presets.presets[mapName] ?? []}
            mapName={mapName}
            agentsByName={agentsByName}
            onLoad={(agentNames) =>
              setSelected(agentNames.filter((n) => agentsByName[n]).slice(0, 5))
            }
          />
          <AgentGrid
            agents={agents}
            selected={selected}
            metaByName={metaByName}
            onToggle={toggleAgent}
          />
        </div>

        <aside className="space-y-4 lg:sticky lg:top-20 lg:self-start">
          <ScorePanel
            score={score}
            loading={scoreLoading}
            selectedCount={selected.length}
          />
          <Suggestions
            suggestions={selected.length > 0 ? suggestions : []}
            loading={suggestLoading}
            onPick={toggleAgent}
          />
          <Share mapName={mapName} selected={selected} onLoad={loadComp} />
          <ExportImage map={currentMap} agents={selectedAgents} score={score} />
        </aside>
      </div>
    </main>
  );
}
