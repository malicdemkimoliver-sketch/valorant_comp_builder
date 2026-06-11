import { useState } from "react";
import type { Agent, TeamComp } from "@/lib/types";
import { compTier, searchLinks } from "@/lib/vod-links";

export function TeamComps({
  comps,
  mapName,
  eventWindow,
  patch,
  agentsByName,
  onLoad,
}: {
  comps: TeamComp[];
  mapName: string;
  eventWindow: string | null;
  patch: string | null;
  agentsByName: Record<string, Agent>;
  onLoad: (agents: string[]) => void;
}) {
  const [open, setOpen] = useState(false);
  const [expandedTeam, setExpandedTeam] = useState<string | null>(null);

  if (comps.length === 0) return null;

  const sorted = [...comps].sort((a, b) => b.winrate - a.winrate);

  return (
    <div className="mb-6 rounded-xl border border-navy-700 bg-navy-800/40">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between px-4 py-3 font-display text-sm font-bold tracking-[0.15em] text-slate-300 uppercase"
      >
        <span>
          🏆 Pro Team Comps — {mapName}{" "}
          <span className="text-slate-500">({comps.length})</span>
        </span>
        <span className="text-vred">{open ? "▲" : "▼"}</span>
      </button>
      {open && (
        <>
          {(eventWindow || patch) && (
            <p className="-mt-1 px-4 pb-2 text-[10px] text-slate-500">
              {eventWindow}
              {patch && ` · Patch ${patch}`} · comp winrates from vlr.gg
            </p>
          )}
          <div className="grid gap-3 px-4 pb-4 sm:grid-cols-2">
            {sorted.map((comp) => {
              const tier = compTier(comp.winrate);
              const expanded = expandedTeam === comp.team;
              return (
                <div
                  key={comp.team}
                  className="rounded-lg border border-navy-700 p-3"
                  style={{ borderLeft: `3px solid ${tier.color}` }}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="truncate font-display text-sm font-bold tracking-wide">
                      {comp.team}
                      {comp.region && (
                        <span className="ml-1.5 text-[9px] font-semibold tracking-wider text-slate-500">
                          {comp.region.toUpperCase()}
                        </span>
                      )}
                    </span>
                    <span
                      className="shrink-0 rounded bg-navy-700 px-1.5 py-0.5 text-[10px] font-bold"
                      style={{ color: tier.color }}
                      title={tier.label}
                    >
                      {tier.tier} TIER
                    </span>
                  </div>
                  <div className="mt-1 text-[10px] text-slate-500">
                    {comp.event} ·{" "}
                    <span className="font-bold text-slate-300">
                      {comp.wins}-{comp.losses}
                    </span>{" "}
                    ·{" "}
                    <span className="font-bold" style={{ color: tier.color }}>
                      {comp.winrate}% WR
                    </span>
                  </div>
                  <div className="mt-2 flex gap-1">
                    {comp.agents.map((name) => {
                      const agent = agentsByName[name];
                      return agent?.display_icon ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img
                          key={name}
                          src={agent.display_icon}
                          alt={name}
                          title={name}
                          className="h-8 w-8 rounded-full border border-navy-700"
                        />
                      ) : (
                        <span key={name} className="text-xs">
                          {name}
                        </span>
                      );
                    })}
                  </div>
                  <div className="mt-2 flex gap-2">
                    <button
                      type="button"
                      onClick={() => onLoad(comp.agents)}
                      className="flex-1 rounded bg-vred/15 py-1 text-[11px] font-bold text-vred transition-colors hover:bg-vred hover:text-white"
                    >
                      LOAD COMP
                    </button>
                    <button
                      type="button"
                      onClick={() =>
                        setExpandedTeam(expanded ? null : comp.team)
                      }
                      className={`flex-1 rounded py-1 text-[11px] font-bold transition-colors ${
                        expanded
                          ? "bg-vorange text-navy-950"
                          : "bg-vorange/15 text-vorange hover:bg-vorange hover:text-navy-950"
                      }`}
                    >
                      📺 VODS {expanded ? "▴" : "▾"}
                    </button>
                  </div>
                  {expanded && (
                    <div className="mt-2 rounded bg-navy-900/70 p-2.5">
                      <p className="text-[11px] leading-snug text-slate-400">
                        {comp.note}
                      </p>
                      {comp.vods.length > 0 ? (
                        <ul className="mt-2 space-y-1">
                          {comp.vods.map((vod) => (
                            <li key={vod.url}>
                              <a
                                href={vod.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-[11px] font-semibold text-vred hover:underline"
                              >
                                {vod.label} ↗
                              </a>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="mt-2 text-[10px] text-slate-500">
                          No direct VOD curated yet — these searches find the
                          matches:
                        </p>
                      )}
                      <p className="mt-2 text-[10px] font-bold tracking-wider text-slate-500 uppercase">
                        Find more
                      </p>
                      <ul className="mt-1 space-y-1">
                        {searchLinks(
                          comp.team,
                          mapName,
                          comp.event,
                          comp.twitch
                        ).map((link) => (
                          <li key={link.url}>
                            <a
                              href={link.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-[11px] text-slate-400 hover:text-slate-200 hover:underline"
                            >
                              {link.label} ↗
                            </a>
                          </li>
                        ))}
                      </ul>
                      {comp.source_url && (
                        <a
                          href={comp.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="mt-2 block text-[10px] text-slate-600 hover:text-slate-400 hover:underline"
                        >
                          Record source: vlr.gg ↗
                        </a>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
