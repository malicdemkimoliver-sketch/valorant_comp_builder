import type { Agent } from "@/lib/types";
import { ROLE_COLORS, ROLE_ORDER } from "@/lib/types";

export function CompSlots({
  agents,
  onRemove,
  onReset,
}: {
  agents: Agent[];
  onRemove: (name: string) => void;
  onReset: () => void;
}) {
  const roleCounts = ROLE_ORDER.map((role) => ({
    role,
    count: agents.filter((a) => a.role === role).length,
  })).filter((r) => r.count > 0);

  return (
    <div className="mb-6 flex flex-wrap items-center gap-4 rounded-xl border border-navy-700 bg-navy-800/40 p-4">
      <div className="flex gap-2">
        {Array.from({ length: 5 }, (_, i) => {
          const agent = agents[i];
          return agent ? (
            <button
              key={agent.name}
              type="button"
              onClick={() => onRemove(agent.name)}
              title={`Remove ${agent.name}`}
              className="group relative"
            >
              {agent.display_icon ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={agent.display_icon}
                  alt={agent.name}
                  className="h-12 w-12 rounded-full border-2 transition-opacity group-hover:opacity-50"
                  style={{ borderColor: ROLE_COLORS[agent.role] ?? "#64748b" }}
                />
              ) : (
                <span className="flex h-12 w-12 items-center justify-center rounded-full border-2 border-navy-700 text-xl">
                  {agent.icon}
                </span>
              )}
              <span className="absolute inset-0 hidden items-center justify-center text-lg font-bold text-vred group-hover:flex">
                ✕
              </span>
            </button>
          ) : (
            <span
              key={`empty-${i}`}
              className="flex h-12 w-12 items-center justify-center rounded-full border-2 border-dashed border-navy-700 text-slate-600"
            >
              {i + 1}
            </span>
          );
        })}
      </div>
      <div className="flex flex-wrap gap-1.5">
        {roleCounts.map(({ role, count }) => (
          <span
            key={role}
            className="rounded-full border px-2 py-0.5 text-[10px] font-bold tracking-wide"
            style={{
              color: ROLE_COLORS[role],
              borderColor: `color-mix(in srgb, ${ROLE_COLORS[role]} 50%, transparent)`,
            }}
          >
            {count} {role}
            {count > 1 ? "s" : ""}
          </span>
        ))}
      </div>
      {agents.length > 0 && (
        <button
          type="button"
          onClick={onReset}
          className="ml-auto rounded-lg border border-navy-700 px-3 py-1.5 text-xs font-semibold text-slate-400 transition-colors hover:border-vred hover:text-vred"
        >
          🔄 Reset
        </button>
      )}
    </div>
  );
}
