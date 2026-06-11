import { useState } from "react";
import { decodeComp, encodeComp } from "@/lib/comp-code";

export function Share({
  mapName,
  selected,
  onLoad,
}: {
  mapName: string;
  selected: string[];
  onLoad: (map: string, agents: string[]) => boolean;
}) {
  const [copied, setCopied] = useState<"code" | "url" | null>(null);
  const [input, setInput] = useState("");
  const [error, setError] = useState<string | null>(null);

  const code = selected.length === 5 ? encodeComp(mapName, selected) : null;

  async function copy(text: string, kind: "code" | "url") {
    await navigator.clipboard.writeText(text);
    setCopied(kind);
    setTimeout(() => setCopied(null), 1500);
  }

  function loadFromInput() {
    const decoded = decodeComp(input);
    if (!decoded) {
      setError("Invalid code — expected VAL-2-MAP-A1-A2-A3-A4-A5");
      return;
    }
    if (!onLoad(decoded.map, decoded.agents)) {
      setError("Code references agents or a map not in the roster");
      return;
    }
    setError(null);
    setInput("");
  }

  return (
    <div className="rounded-xl border border-navy-700 bg-navy-800/40 p-5">
      <h3 className="mb-3 font-display text-sm font-bold tracking-[0.2em] text-slate-400 uppercase">
        🔗 Share
      </h3>

      {code ? (
        <div className="space-y-2">
          <div className="rounded bg-navy-900 px-2 py-1.5 text-center font-mono text-xs text-slate-300">
            {code}
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => copy(code, "code")}
              className="flex-1 rounded bg-vred/15 py-1.5 text-[11px] font-bold text-vred transition-colors hover:bg-vred hover:text-white"
            >
              {copied === "code" ? "COPIED!" : "COPY CODE"}
            </button>
            <button
              type="button"
              onClick={() =>
                copy(`${window.location.origin}/builder?code=${code}`, "url")
              }
              className="flex-1 rounded bg-vred/15 py-1.5 text-[11px] font-bold text-vred transition-colors hover:bg-vred hover:text-white"
            >
              {copied === "url" ? "COPIED!" : "COPY LINK"}
            </button>
          </div>
        </div>
      ) : (
        <p className="text-[11px] text-slate-500">
          Pick 5 agents to get a shareable comp code.
        </p>
      )}

      <div className="mt-3 flex gap-2">
        <input
          value={input}
          onChange={(e) => {
            setInput(e.target.value);
            setError(null);
          }}
          onKeyDown={(e) => e.key === "Enter" && loadFromInput()}
          placeholder="Paste a VAL-2-… code"
          className="min-w-0 flex-1 rounded border border-navy-700 bg-navy-900 px-2 py-1.5 text-xs text-slate-300 placeholder:text-slate-600 focus:border-vred focus:outline-none"
        />
        <button
          type="button"
          onClick={loadFromInput}
          disabled={!input.trim()}
          className="rounded border border-navy-700 px-3 text-[11px] font-bold text-slate-300 transition-colors hover:border-vred hover:text-vred disabled:opacity-40"
        >
          LOAD
        </button>
      </div>
      {error && <p className="mt-1.5 text-[11px] text-vred">{error}</p>}
    </div>
  );
}
