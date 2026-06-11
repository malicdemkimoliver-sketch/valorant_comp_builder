import { useState } from "react";
import type { Agent, Preset } from "@/lib/types";

export function Presets({
  presets,
  mapName,
  agentsByName,
  onLoad,
}: {
  presets: Preset[];
  mapName: string;
  agentsByName: Record<string, Agent>;
  onLoad: (agents: string[]) => void;
}) {
  const [open, setOpen] = useState(false);

  if (presets.length === 0) return null;

  return (
    <div className="mb-6 rounded-xl border border-navy-700 bg-navy-800/40">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between px-4 py-3 font-display text-sm font-bold tracking-[0.15em] text-slate-300 uppercase"
      >
        <span>
          📋 Meta Presets — {mapName}{" "}
          <span className="text-slate-500">({presets.length})</span>
        </span>
        <span className="text-vred">{open ? "▲" : "▼"}</span>
      </button>
      {open && (
        <div className="grid gap-3 px-4 pb-4 sm:grid-cols-2">
          {presets.map((preset) => (
            <div
              key={preset.name}
              className="rounded-lg border border-navy-700 p-3"
            >
              <div className="flex items-center justify-between">
                <span className="font-display text-sm font-bold tracking-wide">
                  {preset.name}
                </span>
                <span className="rounded bg-navy-700 px-1.5 py-0.5 text-[10px] font-bold text-vorange">
                  {preset.score} · {preset.grade}
                </span>
              </div>
              <div className="mt-2 flex gap-1">
                {preset.agents.map((name) => {
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
              <p className="mt-2 text-[11px] leading-snug text-slate-400">
                {preset.description}
              </p>
              <p className="mt-1 text-[10px] text-slate-500">{preset.source}</p>
              <button
                type="button"
                onClick={() => onLoad(preset.agents)}
                className="mt-2 w-full rounded bg-vred/15 py-1 text-[11px] font-bold text-vred transition-colors hover:bg-vred hover:text-white"
              >
                LOAD COMP
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
