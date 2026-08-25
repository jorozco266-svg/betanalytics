#!/usr/bin/env python3
"""
BetAnalytics — Verify Agent v2 (Google Gemini)
1. Verifica resultados faltantes
2. Busca fixtures (próximos partidos) que no están en el JSON
Usa Gemini 2.0 Flash con Google Search grounding (gratis).
"""
import json
import os
import datetime
import logging
import time
import re
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [verify] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("verify")

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config", "leagues.json")

MAX_LEAGUES_PER_RUN = 5
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

PRIORITY_ORDER = [
    "betplay", "argentina", "libertadores", "sudamericana",
    "brasileirao", "laliga", "bundesliga", "premier",
    "seriea", "ligue1", "champions", "mls",
    "chile", "ecuador", "uruguay", "argfem",
    "frauenbundesliga",
]


def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)


def call_gemini(prompt):
    if not GEMINI_KEY:
        return ""
    try:
        resp = requests.post(
            f"{GEMINI_URL}?key={GEMINI_KEY}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "tools": [{"google_search": {}}],
                "generationConfig": {"temperature": 0.1, "maxOutputTokens": 3000},
            },
            timeout=90,
        )
        if resp.status_code != 200:
            log.error(f"Gemini error {resp.status_code}: {resp.text[:300]}")
            return ""
        data = resp.json()
        parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
        return "\n".join(p.get("text", "") for p in parts if "text" in p)
    except Exception as e:
        log.error(f"Gemini call failed: {e}")
        return ""


# ── RESULTS VERIFICATION ──────────────────────────

def build_results_prompt(league_name, standings, results):
    recent = results[-8:] if results else []
    recent_str = "\n".join(
        f"  {r.get('date','?')} | {r['home']} {r['hg']}-{r['ag']} {r['away']}"
        for r in recent
    ) if recent else "  (none)"
    teams = [t["team"] for t in standings[:15]] if standings else ["(none)"]

    return f"""You are a sports data verifier. Find RECENT match results MISSING from our database.

LEAGUE: {league_name}
TODAY: {datetime.date.today().isoformat()}

OUR LATEST RESULTS:
{recent_str}

TEAMS IN MODEL: {', '.join(teams)}

TASK: Search the web for {league_name} results from the LAST 7 DAYS.
Report ONLY completed matches NOT in our list above.

Respond with ONLY a JSON array (no markdown, no explanation):
[{{"date":"2026-08-25","home":"Team A","away":"Team B","hg":2,"ag":1}}]

If all results are up to date: []

RULES: Only verified web results. Never invent. JSON only."""


def parse_json_array(response):
    if not response:
        return []
    response = response.replace("```json", "").replace("```", "").strip()
    match = re.search(r'\[\s*(?:\{.*?\}\s*,?\s*)*\]', response, re.DOTALL)
    if match:
        try:
            items = json.loads(match.group())
            return [r for r in items if isinstance(r, dict)]
        except json.JSONDecodeError:
            pass
    if "[]" in response:
        return []
    return []


def merge_results(existing, new_results):
    keys = {f"{r.get('date','')}|{r['home']}|{r['away']}" for r in existing}
    added = 0
    for r in new_results:
        if not all(k in r for k in ("date", "home", "away", "hg", "ag")):
            continue
        if not isinstance(r["hg"], int) or not isinstance(r["ag"], int):
            continue
        key = f"{r['date']}|{r['home']}|{r['away']}"
        if key not in keys:
            r["_source"] = "verify_agent"
            r["_verified_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            existing.append(r)
            keys.add(key)
            added += 1
            log.info(f"    +R {r['date']} {r['home']} {r['hg']}-{r['ag']} {r['away']}")
    existing.sort(key=lambda x: x.get("date", ""))
    return existing, added


# ── FIXTURES VERIFICATION ──────────────────────────

def build_fixtures_prompt(league_name, standings, existing_fixtures):
    fix_str = "\n".join(
        f"  {f.get('date','?')} | {f.get('home','?')} vs {f.get('away','?')}"
        for f in existing_fixtures[:10]
    ) if existing_fixtures else "  (none)"
    teams = [t["team"] for t in standings[:15]] if standings else ["(none)"]

    return f"""You are a sports fixture finder. Find UPCOMING matches for this league.

LEAGUE: {league_name}
TODAY: {datetime.date.today().isoformat()}

FIXTURES WE ALREADY HAVE:
{fix_str}

TEAMS: {', '.join(teams)}

TASK: Search the web for {league_name} fixtures/schedule for the NEXT 7 DAYS.
Report matches NOT already in our list above.

Respond with ONLY a JSON array (no markdown, no explanation):
[{{"date":"2026-08-25","time":"19:00","home":"Team A","away":"Team B"}}]

Time should be in 24h format, local time of the country. If you can't find the time, use "TBD".
If no missing fixtures: []

RULES: Only verified web data. Never invent. JSON only."""


def merge_fixtures(existing, new_fixtures):
    keys = set()
    for f in existing:
        h = f.get("home", f.get("local", ""))
        a = f.get("away", f.get("visit", ""))
        keys.add(f"{f.get('date','')}|{h}|{a}")

    added = 0
    for f in new_fixtures:
        if not all(k in f for k in ("date", "home", "away")):
            continue
        key = f"{f['date']}|{f['home']}|{f['away']}"
        if key not in keys:
            f["_source"] = "verify_agent"
            # Convert 24h time to 12h format for consistency
            time_str = f.get("time", "TBD")
            if time_str != "TBD":
                try:
                    h, m = int(time_str.split(":")[0]), int(time_str.split(":")[1])
                    period = "AM" if h < 12 else "PM"
                    h12 = h % 12 or 12
                    time_str = f"{h12:02d}:{m:02d} {period}"
                except:
                    pass
            f["time"] = time_str
            existing.append(f)
            keys.add(key)
            added += 1
            log.info(f"    +F {f['date']} {f.get('time','TBD')} {f['home']} vs {f['away']}")
    existing.sort(key=lambda x: x.get("date", ""))
    return existing, added


# ── STANDINGS REBUILD ──────────────────────────

def rebuild_standings(results):
    teams = {}
    for r in results:
        if not all(k in r for k in ("home", "away", "hg", "ag")):
            continue
        for side, gf, ga in [("home", r["hg"], r["ag"]), ("away", r["ag"], r["hg"])]:
            name = r[side]
            if name not in teams:
                teams[name] = {"team": name, "pj": 0, "gf": 0, "ga": 0,
                              "w": 0, "d": 0, "l": 0, "pts": 0}
            t = teams[name]
            t["pj"] += 1; t["gf"] += gf; t["ga"] += ga
            if gf > ga: t["w"] += 1; t["pts"] += 3
            elif gf == ga: t["d"] += 1; t["pts"] += 1
            else: t["l"] += 1
    return sorted(teams.values(), key=lambda x: (-x["pts"], -(x["gf"]-x["ga"]), -x["gf"]))


# ── LEAGUE SELECTION ──────────────────────────

def select_leagues(config):
    day = datetime.date.today().timetuple().tm_yday
    all_keys = [k for k in PRIORITY_ORDER if k in config]
    always = all_keys[:3]
    rest = all_keys[3:]
    if rest:
        start = (day * 2) % len(rest)
        rotated = rest[start:] + rest[:start]
        extra = rotated[:MAX_LEAGUES_PER_RUN - len(always)]
    else:
        extra = []
    return always + extra


# ── MAIN ──────────────────────────

def main():
    if not GEMINI_KEY:
        log.info("No GEMINI_API_KEY — verify agent disabled (get free key at aistudio.google.com/apikey)")
        return

    config = load_config()
    to_check = select_leagues(config)
    log.info(f"Verify Agent v2 (Gemini) — {len(to_check)} leagues: {', '.join(to_check)}")

    total_results_added = 0
    total_fixtures_added = 0

    for key in to_check:
        cfg = config.get(key, {})
        path = os.path.join(DATA_DIR, f"{key}.json")
        if not os.path.exists(path):
            continue

        with open(path) as f:
            data = json.load(f)

        name = cfg.get("name", key)
        standings = data.get("standings", [])
        results = data.get("results", [])
        fixtures = data.get("fixtures", [])
        changed = False

        log.info(f"▸ {name} ({len(results)}R, {len(fixtures)}F)")

        # ── Step 1: Verify results ──
        prompt_r = build_results_prompt(name, standings, results)
        response_r = call_gemini(prompt_r)
        missing_r = parse_json_array(response_r)
        missing_r = [r for r in missing_r if all(k in r for k in ("date","home","away","hg","ag"))
                     and isinstance(r.get("hg"), int) and isinstance(r.get("ag"), int)]

        if missing_r:
            log.info(f"  Results: {len(missing_r)} missing")
            data["results"], added_r = merge_results(data["results"], missing_r)
            total_results_added += added_r
            if added_r > 0:
                data["standings"] = rebuild_standings(data["results"])
                changed = True
        else:
            log.info(f"  Results: ✓ up to date")

        time.sleep(3)

        # ── Step 2: Verify fixtures ──
        prompt_f = build_fixtures_prompt(name, standings, fixtures)
        response_f = call_gemini(prompt_f)
        missing_f = parse_json_array(response_f)
        missing_f = [f for f in missing_f if all(k in f for k in ("date","home","away"))]

        if missing_f:
            log.info(f"  Fixtures: {len(missing_f)} missing")
            data["fixtures"], added_f = merge_fixtures(data["fixtures"], missing_f)
            total_fixtures_added += added_f
            if added_f > 0:
                changed = True
        else:
            log.info(f"  Fixtures: ✓ up to date")

        # ── Save if changed ──
        if changed:
            data["meta"]["total_matches"] = len(data["results"])
            data["meta"]["total_goals"] = sum(r.get("hg",0)+r.get("ag",0) for r in data["results"])
            data["meta"]["last_verified"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

            with open(path, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            log.info(f"  ✓ Saved")

        time.sleep(4)

    log.info(f"\nDone: +{total_results_added} results, +{total_fixtures_added} fixtures")


if __name__ == "__main__":
    main()
