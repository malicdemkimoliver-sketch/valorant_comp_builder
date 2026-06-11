import type { VodLink } from "./types";

/**
 * Comp tier from its measured winrate — same thresholds the old
 * Streamlit preset_vods used (S >= 75, A >= 65, B >= 55, else C).
 */
export function compTier(winrate: number): {
  tier: "S" | "A" | "B" | "C";
  color: string;
  label: string;
} {
  if (winrate >= 75) return { tier: "S", color: "#ff4655", label: "Dominant comp" };
  if (winrate >= 65) return { tier: "A", color: "#ff8c42", label: "Strong comp" };
  if (winrate >= 55) return { tier: "B", color: "#ffd700", label: "Solid comp" };
  return { tier: "C", color: "#64748b", label: "Situational comp" };
}

/**
 * Always-valid search links for finding more footage of a team's comp —
 * the fallback when no direct VOD is curated (and a "find more" row
 * even when one is).
 */
export function searchLinks(
  team: string,
  map: string,
  event: string,
  twitch?: string
): VodLink[] {
  const q = encodeURIComponent;
  return [
    {
      label: `▶️ YouTube — ${team} ${map} highlights`,
      url: `https://www.youtube.com/results?search_query=${q(`${team} ${map} ${event} highlights`)}`,
    },
    {
      label: "🎬 YouTube — full match VODs",
      url: `https://www.youtube.com/results?search_query=${q(`${team} ${map} ${event} full match VOD`)}`,
    },
    {
      label: `📊 VLR.gg — ${team} matches`,
      url: `https://www.vlr.gg/search/?q=${q(team)}`,
    },
    twitch
      ? { label: "🟣 Twitch — official broadcast", url: twitch }
      : {
          label: `🟣 Twitch — search ${team}`,
          url: `https://www.twitch.tv/search?term=${q(`${team} valorant`)}`,
        },
  ];
}
