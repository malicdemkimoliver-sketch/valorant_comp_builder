import type { Agent, RatedMetaEntry } from "@/lib/types";

const TIER_COLORS: Record<string, string> = {
  S: "text-vorange",
  A: "text-sentinel",
  B: "text-initiator",
  C: "text-slate-400",
};

export function AgentCard({
  agent,
  selected,
  disabled,
  meta,
  onToggle,
}: {
  agent: Agent;
  selected: boolean;
  disabled: boolean;
  meta?: RatedMetaEntry;
  onToggle: (name: string) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onToggle(agent.name)}
      disabled={disabled}
      className={`relative flex flex-col items-center gap-1.5 rounded-lg border p-2.5 transition-all ${
        selected
          ? "border-sentinel bg-sentinel/15 ring-2 ring-sentinel/60 shadow-[0_0_16px_rgba(16,185,129,0.4)]"
          : disabled
            ? "border-navy-700 bg-navy-800/30 opacity-40"
            : "border-navy-700 bg-navy-800/50 hover:border-vred/60"
      }`}
    >
      {selected && (
        <span className="absolute -top-2 -right-2 z-10 flex h-5 w-5 items-center justify-center rounded-full bg-sentinel text-[11px] font-bold text-white shadow-[0_0_8px_rgba(16,185,129,0.6)]">
          ✓
        </span>
      )}
      {agent.display_icon ? (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={agent.display_icon}
          alt={agent.name}
          className={`h-12 w-12 rounded-full border-2 ${
            selected ? "border-sentinel brightness-110" : "border-navy-700"
          }`}
        />
      ) : (
        <span className="text-2xl leading-12">{agent.icon}</span>
      )}
      <span
        className={`text-xs font-semibold ${selected ? "text-sentinel" : ""}`}
      >
        {agent.name}
      </span>
      <span className="flex items-center gap-1">
        {meta &&
          (meta.meta_pick ? (
            <span className="rounded bg-sentinel/15 px-1 py-px text-[9px] font-bold tracking-wide text-sentinel">
              ✓ META
            </span>
          ) : (
            <span className="rounded bg-vorange/10 px-1 py-px text-[9px] font-bold tracking-wide text-vorange">
              OFF
            </span>
          ))}
        {meta && meta.tier !== "NR" && (
          <span
            className={`rounded bg-navy-700 px-1 py-px text-[9px] font-bold ${TIER_COLORS[meta.tier] ?? "text-slate-300"}`}
          >
            {meta.tier}
          </span>
        )}
        {!agent.curated && (
          <span className="rounded bg-navy-700 px-1 py-px text-[9px] text-slate-400">
            NEW
          </span>
        )}
      </span>
    </button>
  );
}
