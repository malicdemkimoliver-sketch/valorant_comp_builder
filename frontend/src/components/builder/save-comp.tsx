import { useState } from "react";
import { encodeComp } from "@/lib/comp-code";
import type { ScoreResult } from "@/lib/types";

export function SaveComp({
  mapName,
  selected,
  score,
  signedIn,
}: {
  mapName: string;
  selected: string[];
  score: ScoreResult | null;
  signedIn: boolean;
}) {
  const [name, setName] = useState("");
  const [notes, setNotes] = useState("");
  const [status, setStatus] = useState<"idle" | "saving" | "saved" | "error">(
    "idle"
  );
  const [error, setError] = useState<string | null>(null);

  const ready = selected.length === 5;

  async function save() {
    setStatus("saving");
    setError(null);
    try {
      const res = await fetch("/api/saved", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: name.trim() || `${mapName} comp`,
          map: mapName,
          agents: selected,
          code: encodeComp(mapName, selected),
          score: score?.score ?? null,
          grade: score?.grade ?? null,
          notes: notes.trim(),
        }),
      });
      if (res.status === 401) {
        setStatus("error");
        setError("Sign in (top right) to save comps.");
        return;
      }
      if (!res.ok) {
        throw new Error(`save failed: ${res.status}`);
      }
      setStatus("saved");
      setName("");
      setNotes("");
      setTimeout(() => setStatus("idle"), 1500);
    } catch {
      setStatus("error");
      setError("Couldn't save — is the backend running?");
    }
  }

  return (
    <div className="rounded-xl border border-navy-700 bg-navy-800/40 p-5">
      <h3 className="mb-3 font-display text-sm font-bold tracking-[0.2em] text-slate-400 uppercase">
        💾 Save
      </h3>

      {!signedIn ? (
        <p className="text-[11px] text-slate-500">
          Sign in (top right) to save comps to your account.
        </p>
      ) : !ready ? (
        <p className="text-[11px] text-slate-500">
          Pick 5 agents to save this comp.
        </p>
      ) : (
        <div className="space-y-2">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && status !== "saving" && save()}
            maxLength={80}
            placeholder={`${mapName} comp`}
            className="w-full rounded border border-navy-700 bg-navy-900 px-2 py-1.5 text-xs text-slate-300 placeholder:text-slate-600 focus:border-vred focus:outline-none"
          />
          <input
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Notes (optional)"
            className="w-full rounded border border-navy-700 bg-navy-900 px-2 py-1.5 text-xs text-slate-300 placeholder:text-slate-600 focus:border-vred focus:outline-none"
          />
          <button
            type="button"
            onClick={save}
            disabled={status === "saving"}
            className="w-full rounded bg-vred/15 py-1.5 text-[11px] font-bold text-vred transition-colors hover:bg-vred hover:text-white disabled:opacity-40"
          >
            {status === "saving"
              ? "SAVING…"
              : status === "saved"
                ? "SAVED!"
                : "SAVE COMP"}
          </button>
        </div>
      )}
      {error && <p className="mt-1.5 text-[11px] text-vred">{error}</p>}
    </div>
  );
}
