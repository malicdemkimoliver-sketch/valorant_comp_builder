export type Ability = {
  slot: string;
  name: string;
  description: string;
  icon: string | null;
};

export type Agent = {
  uuid: string | null;
  name: string;
  description: string;
  role: string;
  display_icon: string | null;
  full_portrait: string | null;
  background_colors: string[];
  abilities: Ability[];
  icon: string;
  strengths: string[];
  weaknesses: string[];
  good_maps: string[];
  synergy_tags: string[];
  utility: string[];
  curated: boolean;
};

export type MapInfo = {
  name: string;
  icon: string;
  description?: string;
  attack_sided?: boolean;
  defense_sided?: boolean;
  balanced?: boolean;
  key_features?: string[];
  preferred_roles?: string[];
  uuid: string | null;
  splash: string | null;
  list_view_icon: string | null;
  sites: string | null;
  in_active_pool: boolean;
  has_meta_data: boolean;
};

export type ScoreAgent = {
  name: string;
  role: string;
  on_meta: boolean;
  tier: string | null;
};

export type ScoreResult = {
  map: string;
  score: number;
  grade: string;
  grade_color: string;
  label: string;
  breakdown: Record<string, number>;
  agents: ScoreAgent[];
};

export type Suggestion = {
  name: string;
  role: string;
  tier: string | null;
  wr: number | null;
  pr: number | null;
  score: number;
  pros: string[];
  cons: string[];
};

export type MetaEntry = {
  name: string;
  win_rate: number | null;
  pick_rate: number | null;
  composite: number | null;
  on_meta: boolean;
  meta_pick: boolean;
};

/** MetaEntry flattened out of the tier groups, tagged with its tier key. */
export type RatedMetaEntry = MetaEntry & { tier: string };

export type MapMeta = {
  map: string;
  thin_data: boolean;
  last_updated: string | null;
  series: string | null;
  tiers: Record<string, MetaEntry[]>;
};

export type Preset = {
  name: string;
  agents: string[];
  description: string;
  source: string;
  score: number;
  grade: string;
};

export type PresetsResponse = {
  generated: string | null;
  series: string | null;
  presets: Record<string, Preset[]>;
};

export type VodLink = {
  label: string;
  url: string;
};

export type TeamComp = {
  team: string;
  region?: string;
  agents: string[];
  wins: number;
  losses: number;
  winrate: number;
  event: string;
  note: string;
  vods: VodLink[];
  twitch?: string;
  source_url?: string;
};

export type TeamCompsResponse = {
  generated: string | null;
  event_window: string | null;
  patch: string | null;
  comps: Record<string, TeamComp[]>;
};

export const ROLE_ORDER = ["Duelist", "Initiator", "Controller", "Sentinel"];

export const ROLE_COLORS: Record<string, string> = {
  Duelist: "var(--color-duelist)",
  Initiator: "var(--color-initiator)",
  Controller: "var(--color-controller)",
  Sentinel: "var(--color-sentinel)",
};

export const BREAKDOWN_MAX: Record<string, number> = {
  "Role Balance": 25,
  "Map Fit": 20,
  "Agent Synergy": 20,
  "Utility Coverage": 15,
  "Attack Strength": 10,
  "Defense Strength": 10,
};
