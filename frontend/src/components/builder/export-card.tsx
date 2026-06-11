import { useRef, useState } from "react";
import { toPng } from "html-to-image";
import type { Agent, MapInfo, ScoreResult } from "@/lib/types";
import { BREAKDOWN_MAX, ROLE_COLORS } from "@/lib/types";

export function ExportImage({
  map,
  agents,
  score,
}: {
  map: MapInfo | undefined;
  agents: Agent[];
  score: ScoreResult | null;
}) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(false);

  const ready = map && agents.length === 5 && score !== null;

  async function download() {
    if (!cardRef.current) return;
    setBusy(true);
    setError(false);
    try {
      const dataUrl = await toPng(cardRef.current, {
        cacheBust: true,
        pixelRatio: 2,
      });
      const link = document.createElement("a");
      link.download = `comp-${map!.name.toLowerCase()}-${score!.score}.png`;
      link.href = dataUrl;
      link.click();
    } catch {
      setError(true);
    } finally {
      setBusy(false);
    }
  }

  if (!ready) return null;

  return (
    <>
      <button
        type="button"
        onClick={download}
        disabled={busy}
        className="w-full rounded-xl border border-navy-700 bg-navy-800/40 py-2.5 font-display text-sm font-bold tracking-[0.15em] text-slate-300 transition-colors hover:border-vred hover:text-vred disabled:opacity-50"
      >
        {busy ? "RENDERING…" : "🖼️ SAVE AS IMAGE"}
      </button>
      {error && (
        <p className="text-center text-[11px] text-vred">
          Export failed — try again.
        </p>
      )}

      {/* Off-screen card rendered to PNG */}
      <div className="pointer-events-none fixed -left-[2000px] top-0">
        <div
          ref={cardRef}
          className="flex h-[600px] w-[960px] flex-col justify-between p-10"
          style={{
            backgroundImage: map.splash
              ? `linear-gradient(135deg, rgba(15,25,35,0.92), rgba(26,35,50,0.88)), url('${map.splash}')`
              : "linear-gradient(135deg, #0f1923, #1a2332)",
            backgroundSize: "cover",
            backgroundPosition: "center",
          }}
        >
          <div className="flex items-start justify-between">
            <div>
              <div className="font-display text-3xl font-bold tracking-[0.15em]">
                <span className="text-vred">GYD&apos;S VLR</span>{" "}
                <span className="text-vorange">COMP BUILDER</span>
              </div>
              <div className="mt-1 font-display text-xl tracking-[0.3em] text-slate-300">
                {map.name.toUpperCase()}
              </div>
            </div>
            <div className="text-right">
              <div className="font-display text-6xl font-bold leading-none">
                {score.score}
                <span className="ml-2" style={{ color: score.grade_color }}>
                  {score.grade}
                </span>
              </div>
              <div
                className="mt-1 font-display text-sm font-semibold tracking-wider"
                style={{ color: score.grade_color }}
              >
                {score.label.toUpperCase()}
              </div>
            </div>
          </div>

          <div className="flex justify-center gap-6">
            {agents.map((agent) => (
              <div key={agent.name} className="flex flex-col items-center">
                {agent.display_icon ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img
                    src={agent.display_icon}
                    alt={agent.name}
                    crossOrigin="anonymous"
                    className="h-24 w-24 rounded-full border-4"
                    style={{
                      borderColor: ROLE_COLORS[agent.role] ?? "#64748b",
                    }}
                  />
                ) : (
                  <span className="flex h-24 w-24 items-center justify-center rounded-full border-4 border-navy-700 text-4xl">
                    {agent.icon}
                  </span>
                )}
                <span className="mt-2 font-display text-lg font-bold">
                  {agent.name}
                </span>
                <span
                  className="text-xs font-semibold"
                  style={{ color: ROLE_COLORS[agent.role] }}
                >
                  {agent.role}
                </span>
              </div>
            ))}
          </div>

          <div className="flex items-end justify-between">
            <div className="flex gap-5">
              {Object.entries(BREAKDOWN_MAX).map(([category, max]) => (
                <div key={category} className="text-center">
                  <div className="font-display text-lg font-bold text-slate-200">
                    {score.breakdown[category] ?? 0}
                    <span className="text-xs text-slate-500">/{max}</span>
                  </div>
                  <div className="text-[9px] tracking-wide text-slate-400 uppercase">
                    {category}
                  </div>
                </div>
              ))}
            </div>
            <div className="text-xs text-slate-500">
              gyd&apos;s vlr comp builder · data: valorant-api.com + vstats
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
