import type { ScoreResult } from "@/lib/types";
import { BREAKDOWN_MAX } from "@/lib/types";

function barColor(value: number, max: number): string {
  const ratio = max > 0 ? value / max : 0;
  if (ratio >= 0.7) return "var(--color-sentinel)";
  if (ratio >= 0.4) return "var(--color-vorange)";
  return "var(--color-vred)";
}

export function ScorePanel({
  score,
  loading,
  selectedCount,
}: {
  score: ScoreResult | null;
  loading: boolean;
  selectedCount: number;
}) {
  return (
    <div className="rounded-xl border border-navy-700 bg-navy-800/40 p-5">
      <h3 className="mb-3 font-display text-sm font-bold tracking-[0.2em] text-slate-400 uppercase">
        Comp Score
      </h3>

      {selectedCount === 0 ? (
        <p className="py-6 text-center text-sm text-slate-500">
          Pick agents to see your live score.
        </p>
      ) : score === null ? (
        <p className="animate-pulse py-6 text-center text-sm text-slate-500">
          Scoring…
        </p>
      ) : (
        <div className={loading ? "opacity-60 transition-opacity" : ""}>
          <div className="flex items-end justify-center gap-3">
            <span className="font-display text-6xl font-bold leading-none">
              {score.score}
            </span>
            <span
              className="font-display text-4xl font-bold leading-none"
              style={{ color: score.grade_color }}
            >
              {score.grade}
            </span>
          </div>
          <p
            className="mt-1 text-center font-display text-sm font-semibold tracking-wider"
            style={{ color: score.grade_color }}
          >
            {score.label.toUpperCase()}
          </p>
          {selectedCount < 5 && (
            <p className="mt-1 text-center text-[11px] text-slate-500">
              {selectedCount}/5 agents — score updates as you pick
            </p>
          )}

          <div className="mt-4 space-y-2.5">
            {Object.entries(BREAKDOWN_MAX).map(([category, max]) => {
              const value = score.breakdown[category] ?? 0;
              return (
                <div key={category}>
                  <div className="mb-0.5 flex justify-between text-[11px]">
                    <span className="text-slate-300">{category}</span>
                    <span className="text-slate-400">
                      {value}/{max}
                    </span>
                  </div>
                  <div className="h-1.5 overflow-hidden rounded-full bg-navy-700">
                    <div
                      className="h-full rounded-full transition-all duration-300"
                      style={{
                        width: `${Math.max(0, (value / max) * 100)}%`,
                        background: barColor(value, max),
                      }}
                    />
                  </div>
                </div>
              );
            })}
            {(score.breakdown["Penalties"] ?? 0) < 0 && (
              <div className="flex justify-between text-[11px]">
                <span className="text-vred">Penalties</span>
                <span className="font-bold text-vred">
                  {score.breakdown["Penalties"]}
                </span>
              </div>
            )}
          </div>

          <div className="mt-4 flex flex-wrap gap-1.5">
            {score.agents.map((agent) => (
              <span
                key={agent.name}
                className={`rounded px-1.5 py-0.5 text-[10px] font-semibold ${
                  agent.on_meta
                    ? "bg-sentinel/15 text-sentinel"
                    : "bg-vorange/10 text-vorange"
                }`}
              >
                {agent.name} {agent.on_meta ? "✓" : "⚠"}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
