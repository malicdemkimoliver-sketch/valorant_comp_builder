/**
 * Comp share codes — TypeScript port of app/services/comp_encoder.py.
 * Format: VAL-2-<MAP>-<A1>-<A2>-<A3>-<A4>-<A5>, same letter codes as the
 * Streamlit app for backward compatibility, extended with the 2025-26 roster.
 */

const AGENT_CODES: Record<string, string> = {
  Astra: "AT",
  Breach: "BR",
  Brimstone: "BM",
  Chamber: "CH",
  Clove: "CL",
  Cypher: "CY",
  Deadlock: "DL",
  Fade: "FD",
  Gekko: "GK",
  Harbor: "HB",
  Iso: "IS",
  Jett: "JT",
  "KAY/O": "KO",
  Killjoy: "KJ",
  Miks: "MK",
  Neon: "NE",
  Omen: "OM",
  Phoenix: "PX",
  Raze: "RZ",
  Reyna: "RN",
  Sage: "SG",
  Skye: "SK",
  Sova: "SV",
  Tejo: "TJ",
  Veto: "VT",
  Viper: "VP",
  Vyse: "VY",
  Waylay: "WL",
  Yoru: "YR",
};

const MAP_CODES: Record<string, string> = {
  Abyss: "AB",
  Ascent: "AC",
  Bind: "BD",
  Breeze: "BZ",
  Corrode: "CR",
  Fracture: "FR",
  Haven: "HV",
  Icebox: "IB",
  Lotus: "LT",
  Pearl: "PL",
  Split: "SP",
  Sunset: "SN",
};

const CODE_TO_AGENT = Object.fromEntries(
  Object.entries(AGENT_CODES).map(([name, code]) => [code, name])
);
const CODE_TO_MAP = Object.fromEntries(
  Object.entries(MAP_CODES).map(([name, code]) => [code, name])
);

const PREFIX = "VAL";
const VERSION = "2";

/** Returns the share code, or null if the comp isn't encodable (needs 5 known agents + known map). */
export function encodeComp(mapName: string, agents: string[]): string | null {
  if (agents.length !== 5) return null;
  const mapCode = MAP_CODES[mapName];
  if (!mapCode) return null;
  const agentCodes = agents.map((a) => AGENT_CODES[a]);
  if (agentCodes.some((c) => !c)) return null;
  return [PREFIX, VERSION, mapCode, ...agentCodes].join("-");
}

/** Parses a share code. Returns null for anything malformed or unknown. */
export function decodeComp(
  code: string
): { map: string; agents: string[] } | null {
  const parts = code.trim().toUpperCase().split("-");
  if (parts.length !== 8 || parts[0] !== PREFIX) return null;
  const map = CODE_TO_MAP[parts[2]];
  if (!map) return null;
  const agents: string[] = [];
  for (const part of parts.slice(3)) {
    const agent = CODE_TO_AGENT[part];
    if (!agent) return null;
    agents.push(agent);
  }
  if (new Set(agents).size !== 5) return null;
  return { map, agents };
}
