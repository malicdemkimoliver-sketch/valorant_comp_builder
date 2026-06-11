import json, os, re, sys
from datetime import date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META_PATH = os.path.join(BASE_DIR, "data", "vct_meta.json")
ACTIVE_MAPS = ["Ascent","Breeze","Fracture","Haven","Lotus","Pearl","Split"]
THIN_MAPS = ["Ascent","Fracture","Lotus"]
AGENT_NAMES = {"Jett","Raze","Neon","Reyna","Phoenix","Yoru","Iso","Waylay",
 "Omen","Brimstone","Viper","Astra","Clove","Harbor","Miks","Sova","Fade",
 "Breach","Skye","Gekko","KAY/O","Tejo","Killjoy","Cypher","Sage","Deadlock",
 "Chamber","Vyse","Veto"}
NAME_FIXES = {"KAYO":"KAY/O","Kayo":"KAY/O","KAY/0":"KAY/O"}

def norm(raw):
    raw = NAME_FIXES.get(raw.strip(), raw.strip())
    for c in AGENT_NAMES:
        if raw.lower() == c.lower():
            return c
    return None

def parse(path):
    data = {}
    for line in open(path, encoding="utf-8"):
        pcts = re.findall(r"(\d+(?:[.,]\d+)?)\s*%", line)
        if len(pcts) < 3:
            continue
        name = None
        for token in re.split(r"[\t]+|\s{2,}|\s", line):
            n = norm(re.sub(r"[\d.%,()]", "", token).strip())
            if n:
                name = n
                break
        if not name or name in data:
            continue
        data[name] = {"win_rate": float(pcts[1].replace(",",".")),
                      "pick_rate": float(pcts[2].replace(",","."))}
    return data

def main():
    if len(sys.argv) < 3:
        print("Usage: python tools/vstats_paste_to_json.py <file.txt> <MapName> [--dry-run]")
        sys.exit(1)
    path, map_name = sys.argv[1], sys.argv[2]
    dry = "--dry-run" in sys.argv
    data = parse(path)
    if not data:
        print("No rows parsed. File needs full rows (name + 3 percentages).")
        sys.exit(1)
    print("Parsed", len(data), "agents for", map_name)
    for nm in list(data)[:3]:
        print(" ", nm, "WR", data[nm]["win_rate"], "PR", data[nm]["pick_rate"])
    existing = {}
    if os.path.exists(META_PATH):
        try:
            existing = json.load(open(META_PATH, encoding="utf-8")).get("meta_by_map", {})
        except Exception:
            pass
    existing[map_name] = data
    out = {"last_updated": date.today().isoformat(),
           "series": "vstats.gg Season 26 Act 3 London pool",
           "active_maps": ACTIVE_MAPS, "thin_maps": THIN_MAPS,
           "meta_by_map": existing}
    if dry:
        print("--dry-run: not writing.")
        return
    json.dump(out, open(META_PATH, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print("Written. Maps:", [m for m in ACTIVE_MAPS if m in existing])

if __name__ == "__main__":
    main()