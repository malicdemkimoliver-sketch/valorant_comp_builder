import type { MapInfo } from "@/lib/types";

function mapTag(map: MapInfo): { label: string; className: string } {
  if (map.attack_sided) return { label: "ATTACK", className: "text-duelist" };
  if (map.defense_sided)
    return { label: "DEFENSE", className: "text-initiator" };
  return { label: "BALANCED", className: "text-sentinel" };
}

export function MapSelect({
  maps,
  selected,
  onSelect,
}: {
  maps: MapInfo[];
  selected: string;
  onSelect: (name: string) => void;
}) {
  const sorted = [...maps].sort(
    (a, b) => Number(b.in_active_pool) - Number(a.in_active_pool)
  );

  return (
    <div className="flex gap-3 overflow-x-auto pb-2">
      {sorted.map((map) => {
        const isSelected = map.name === selected;
        const tag = mapTag(map);
        return (
          <button
            key={map.name}
            type="button"
            onClick={() => onSelect(map.name)}
            className={`relative h-24 w-40 shrink-0 overflow-hidden rounded-lg border-2 text-left transition-all ${
              isSelected
                ? "border-vred shadow-[0_0_18px_rgba(255,70,85,0.45)]"
                : "border-navy-700 opacity-80 hover:opacity-100"
            }`}
            style={{
              backgroundImage: map.splash
                ? isSelected
                  ? `linear-gradient(rgba(255,70,85,0.22), rgba(15,25,35,0.82)), url('${map.splash}')`
                  : `linear-gradient(rgba(15,25,35,0.55), rgba(15,25,35,0.8)), url('${map.splash}')`
                : undefined,
              backgroundSize: "cover",
              backgroundPosition: "center",
            }}
          >
            <div className="absolute inset-0 flex flex-col justify-between p-2">
              <div className="flex items-start justify-between">
                <span className={`text-[10px] font-bold tracking-wider ${tag.className}`}>
                  {tag.label}
                </span>
                <span className="flex items-center gap-1">
                  {map.in_active_pool && (
                    <span className="rounded bg-vred px-1 py-px text-[9px] font-bold tracking-wider text-white">
                      ACTIVE
                    </span>
                  )}
                  {isSelected && (
                    <span className="flex h-4 w-4 items-center justify-center rounded-full bg-vred text-[10px] font-bold text-white shadow-[0_0_8px_rgba(255,70,85,0.6)]">
                      ✓
                    </span>
                  )}
                </span>
              </div>
              <div>
                <div
                  className={`font-display text-base font-bold tracking-wider ${
                    isSelected ? "text-vred" : ""
                  }`}
                >
                  {map.name.toUpperCase()}
                </div>
                {map.sites && (
                  <div className="text-[10px] text-slate-400">{map.sites}</div>
                )}
              </div>
            </div>
          </button>
        );
      })}
    </div>
  );
}
