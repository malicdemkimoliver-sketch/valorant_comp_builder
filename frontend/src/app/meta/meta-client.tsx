"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { fetchMeta } from "@/lib/api";
import type { Agent, MapInfo, MapMeta, MetaEntry } from "@/lib/types";
import { ROLE_COLORS, ROLE_ORDER } from "@/lib/types";
import { MapSelect } from "@/components/builder/map-select";

const TIER_STYLE: Record<string, { color: string; label: string; desc: string }> = {
  S: { color: "#ff4655", label: "S TIER", desc: "Pro-meta essential" },
  A: { color: "#ff8c42", label: "A TIER", desc: "Strong meta pick" },
  B: { color: "#ffd700", label: "B TIER", desc: "Viable choice" },
  C: { color: "#64748b", label: "C TIER", desc: "Niche pick" },
  NR: { color: "#3a4a5a", label: "NOT RATED", desc: "No data on this map" },
};

const TIER_ORDER = ["S", "A", "B", "C", "NR"];

function wrColor(wr: number): string {
  if (wr >= 52) return "#10b981";
  if (wr >= 48) return "#ffd700";
  return "#ff6b6b";
}

function prColor(pr: number): string {
  if (pr >= 50) return "#10b981";
  if (pr >= 25) return "#ff8c42";
  return "#64748b";
}

export function MetaClient({
  agents,
  maps,
  initialMap,
  initialMeta,
}: {
  agents: Agent[];
  maps: MapInfo[];
  initialMap: string;
  initialMeta: MapMeta | null;
}) {
  const [mapName, setMapName] = useState(initialMap);
  const [meta, setMeta] = useState<MapMeta | null>(initialMeta);
  const [roleFilter, setRoleFilter] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  const agentsByName = useMemo(
    () => Object.fromEntries(agents.map((a) => [a.name, a])),
    [agents]
  );

  useEffect(() => {
    if (meta?.map === mapName) return;
    const ctrl = new AbortController();
    fetchMeta(mapName, ctrl.signal)
      .then(setMeta)
      .catch((err) => {
        if ((err as Error).name !== "AbortError") setMeta(null);
      });
    return () => ctrl.abort();
  }, [mapName, meta?.map]);

  useEffect(() => {
    window.history.replaceState(null, "", `/meta?map=${mapName}`);
  }, [mapName]);

  const loading = meta?.map !== mapName;

  function matches(entry: MetaEntry): boolean {
    const agent = agentsByName[entry.name];
    if (roleFilter && agent?.role !== roleFilter) return false;
    if (search && !entry.name.toLowerCase().includes(search.toLowerCase()))
      return false;
    return true;
  }

  return (
    <main className="mx-auto max-w-6xl px-6 py-8">
      <div className="mb-1 flex items-baseline justify-between">
        <h1 className="font-display text-3xl font-bold tracking-[0.1em]">
          <span className="text-vred">META</span>{" "}
          <span className="text-vorange">TRACKER</span>
        </h1>
        {meta && (
          <span className="text-xs text-slate-500">
            {meta.series} · updated {meta.last_updated}
          </span>
        )}
      </div>
      <p className="mb-5 text-sm text-slate-400">
        Tiers blend <strong>win rate</strong>, <strong>pick rate</strong>, and
        each agent&apos;s <strong>map profile</strong> — a stable measure of
        meta strength.
      </p>

      <MapSelect
        maps={maps}
        selected={mapName}
        onSelect={(name) => setMapName(name)}
      />

      {meta?.thin_data && !loading && (
        <div className="mt-4 rounded-lg border border-vorange/40 bg-vorange/10 px-4 py-2.5 text-sm text-vorange">
          ⚠️ {mapName} recently rotated into the pool — ranked data is limited
          and tiers may be unreliable.
        </div>
      )}

      <div className="mt-5 flex flex-wrap items-center gap-2">
        <button
          type="button"
          onClick={() => setRoleFilter(null)}
          className={`rounded-full border px-3 py-1 text-xs font-bold tracking-wide transition-colors ${
            roleFilter === null
              ? "border-vred bg-vred/15 text-vred"
              : "border-navy-700 text-slate-400 hover:text-slate-200"
          }`}
        >
          ALL ROLES
        </button>
        {ROLE_ORDER.map((role) => (
          <button
            key={role}
            type="button"
            onClick={() => setRoleFilter(roleFilter === role ? null : role)}
            className="rounded-full border px-3 py-1 text-xs font-bold tracking-wide transition-colors"
            style={{
              color: roleFilter === role ? ROLE_COLORS[role] : "#94a3b8",
              borderColor:
                roleFilter === role
                  ? ROLE_COLORS[role]
                  : "var(--color-navy-700)",
              background:
                roleFilter === role
                  ? `color-mix(in srgb, ${ROLE_COLORS[role]} 12%, transparent)`
                  : undefined,
            }}
          >
            {role.toUpperCase()}S
          </button>
        ))}
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search agent…"
          className="ml-auto w-44 rounded-lg border border-navy-700 bg-navy-900 px-3 py-1.5 text-xs text-slate-300 placeholder:text-slate-600 focus:border-vred focus:outline-none"
        />
      </div>

      {loading ? (
        <p className="animate-pulse py-16 text-center text-sm text-slate-500">
          Loading {mapName} meta…
        </p>
      ) : meta === null ? (
        <p className="py-16 text-center text-sm text-slate-500">
          No meta data available for {mapName}.
        </p>
      ) : (
        TIER_ORDER.map((tier) => {
          const entries = (meta.tiers[tier] ?? []).filter(matches);
          if (entries.length === 0) return null;
          const style = TIER_STYLE[tier];
          return (
            <section key={tier} className="mt-7">
              <div className="mb-3 flex items-center gap-3">
                <span
                  className="rounded-md px-4 py-1 font-display text-base font-bold text-navy-950"
                  style={{ background: style.color }}
                >
                  {style.label}
                </span>
                <span className="text-xs text-slate-500">
                  {style.desc} · {entries.length} agent
                  {entries.length > 1 ? "s" : ""}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2.5 sm:grid-cols-3 lg:grid-cols-5">
                {entries.map((entry) => {
                  const agent = agentsByName[entry.name];
                  const hasData =
                    entry.win_rate != null && entry.pick_rate != null;
                  return (
                    <Link
                      key={entry.name}
                      href={`/builder?map=${encodeURIComponent(mapName)}&agents=${encodeURIComponent(entry.name)}`}
                      title={`Build a ${mapName} comp around ${entry.name}`}
                      className={`rounded-lg border bg-white/[0.02] p-3 transition-all hover:-translate-y-0.5 hover:bg-white/[0.05] ${
                        hasData ? "" : "opacity-60"
                      }`}
                      style={{
                        borderColor: `${style.color}33`,
                        borderLeft: `3px solid ${style.color}`,
                      }}
                    >
                      <div className="flex items-center gap-2">
                        {agent?.display_icon ? (
                          // eslint-disable-next-line @next/next/no-img-element
                          <img
                            src={agent.display_icon}
                            alt=""
                            className="h-9 w-9 rounded-full border border-navy-700"
                          />
                        ) : null}
                        <div className="min-w-0">
                          <div className="truncate text-sm font-bold">
                            {entry.name}
                          </div>
                          {agent && (
                            <div
                              className="text-[10px] font-semibold"
                              style={{ color: ROLE_COLORS[agent.role] }}
                            >
                              {agent.role}
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="mt-2 text-xs text-slate-400">
                        {hasData ? (
                          <>
                            WR{" "}
                            <span
                              className="font-bold"
                              style={{ color: wrColor(entry.win_rate!) }}
                            >
                              {entry.win_rate}%
                            </span>{" "}
                            · PR{" "}
                            <span
                              className="font-bold"
                              style={{ color: prColor(entry.pick_rate!) }}
                            >
                              {entry.pick_rate}%
                            </span>
                          </>
                        ) : (
                          <span className="text-slate-600">
                            No data this map
                          </span>
                        )}
                      </div>
                    </Link>
                  );
                })}
              </div>
            </section>
          );
        })
      )}
    </main>
  );
}
