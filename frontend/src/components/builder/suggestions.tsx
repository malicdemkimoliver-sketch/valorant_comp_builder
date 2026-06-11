import type { ReactNode } from "react";
import type { Suggestion } from "@/lib/types";
import { ROLE_COLORS } from "@/lib/types";

/** The API embeds markdown-style **bold** markers in pros/cons text. */
function renderBold(text: string): ReactNode[] {
  return text.split("**").map((part, i) =>
    i % 2 === 1 ? <strong key={i}>{part}</strong> : part
  );
}

export function Suggestions({
  suggestions,
  loading,
  onPick,
}: {
  suggestions: Suggestion[];
  loading: boolean;
  onPick: (name: string) => void;
}) {
  if (!loading && suggestions.length === 0) return null;

  return (
    <div className="rounded-xl border border-navy-700 bg-navy-800/40 p-5">
      <h3 className="mb-3 font-display text-sm font-bold tracking-[0.2em] text-slate-400 uppercase">
        💡 Suggested Picks
      </h3>
      {loading && suggestions.length === 0 ? (
        <p className="animate-pulse py-4 text-center text-sm text-slate-500">
          Analyzing…
        </p>
      ) : (
        <div className={`space-y-3 ${loading ? "opacity-60" : ""}`}>
          {suggestions.map((s) => {
            const color = ROLE_COLORS[s.role] ?? "#94a3b8";
            return (
              <div
                key={s.name}
                className="rounded-lg border border-navy-700 p-3"
                style={{ borderTop: `3px solid ${color}` }}
              >
                <div className="flex items-center justify-between">
                  <span className="font-display text-base font-bold">
                    {s.name}
                  </span>
                  <button
                    type="button"
                    onClick={() => onPick(s.name)}
                    className="rounded bg-vred/15 px-2 py-0.5 text-[11px] font-bold text-vred transition-colors hover:bg-vred hover:text-white"
                  >
                    + ADD
                  </button>
                </div>
                <div className="text-[11px]" style={{ color }}>
                  {s.role}
                  {s.tier ? ` · ${s.tier} tier` : ""}
                  {s.wr != null ? ` · ${s.wr}% WR` : ""}
                </div>
                <ul className="mt-1.5 space-y-0.5 text-[11px] leading-snug text-slate-300">
                  {s.pros.slice(0, 3).map((pro, i) => (
                    <li key={i}>✅ {renderBold(pro)}</li>
                  ))}
                  {s.cons.slice(0, 1).map((con, i) => (
                    <li key={i} className="text-slate-400">
                      ⚠️ {renderBold(con)}
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
