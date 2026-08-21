#!/usr/bin/env python3
"""
BetAnalytics — Verify Agent (Google Gemini)
Usa Gemini 2.0 Flash con Google Search grounding para verificar datos.
Tier gratuito: 15 req/min, 1M tokens/min.
API Key: https://aistudio.google.com/apikey
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
]


def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)


def call_gemini(prompt):
    """Llama a Gemini 2.0 Flash con Google Search grounding."""
    if not GEMINI_KEY:
        return ""
    try:
        resp = requests.post(
            f"{GEMINI_URL}?key={GEMINI_KEY}",
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "tools": [{"google_search": {}}],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 2000,
                },
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


def build_prompt(league_name, standings, results, fixtures):
    recent = results[-8:] if results else []
    recent_str = "\n".join(
        f"  {r.get('date','?')} | {r['home']} {r['hg']}-{r['ag']} {r['away']}"
        for r in recent
    ) if recent else "  (sin resultados)"
    teams = [t["team"] for t in standings[:15]] if standings else ["(sin equipos)"]

    return f"""You are a sports data verification assistant. Find RECENT match results that are MISSING from our database.

LEAGUE: {league_name}
TODAY: {datetime.date.today().isoformat()}

OUR LATEST RESULTS:
{recent_str}

TEAMS IN MODEL (first 15):
{', '.join(teams)}

UPCOMING FIXTURES: {len(fixtures)} scheduled

TASK:
1. Search the web for {league_name} results from the LAST 7 DAYS
2. Compare with our list above
3. Report ONLY completed matches NOT in our database

Respond with ONLY a JSON array (no markdown, no explanation):

[{{"date":"2026-08-19","home":"Team A","away":"Team B","hg":2,"ag":1}}]

If all results are up to date, respond exactly: []

CRITICAL RULES:
- ONLY verified results from the web. NEVER invent scores.
- Use team names matching our list as closely as possible.
- Only FINISHED matches with confirmed final scores.
- JSON only, nothing else."""


def parse_response(response):
    if not response:
        return []
    # Clean markdown fences
    response = response.replace("```json", "").replace("```", "").strip()
    match = re.search(r'\[\s*(?:\{.*?\}\s*,?\s*)*\]', response, re.DOTALL)
    if match:
        try:
            results = json.loads(match.group())
            return [r for r in results
                    if all(k in r for k in ("date","home","away","hg","ag"))
                    and isinstance(r["hg"], int) and isinstance(r["ag"], int)]
        except json.JSONDecodeError:
            pass
    if "[]" in response:
        return []
    log.warning(f"Could not parse: {response[:200]}")
    return []


def merge_results(existing, new_results):
    keys = {f"{r.get('date','')}|{r['home']}|{r['away']}" for r in existing}
    added = 0
    for r in new_results:
        key = f"{r['date']}|{r['home']}|{r['away']}"
        if key not in keys:
            r["_source"] = "verify_agent"
            r["_verified_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
            existing.append(r)
            keys.add(key)
            added += 1
            log.info(f"    + {r['date']} {r['home']} {r['hg']}-{r['ag']} {r['away']}")
    existing.sort(key=lambda x: x.get("date", ""))
    return existing, added


def rebuild_standings(results):
    teams = {}
    for r in results:
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


def main():
    if not GEMINI_KEY:
        log.info("No GEMINI_API_KEY — verify agent disabled (get free key at aistudio.google.com/apikey)")
        return

    config = load_config()
    to_check = select_leagues(config)
    log.info(f"Verify Agent (Gemini) — {len(to_check)} leagues: {', '.join(to_check)}")

    total_added = 0

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

        log.info(f"▸ {name} ({len(results)} results)")

        prompt = build_prompt(name, standings, results, fixtures)
        response = call_gemini(prompt)
        missing = parse_response(response)

        if not missing:
            log.info(f"  ✓ Up to date")
            continue

        log.info(f"  Found {len(missing)} missing:")
        data["results"], added = merge_results(data["results"], missing)
        total_added += added

        if added > 0:
            if data["results"]:
                data["standings"] = rebuild_standings(data["results"])
            data["meta"]["total_matches"] = len(data["results"])
            data["meta"]["total_goals"] = sum(r["hg"]+r["ag"] for r in data["results"])
            data["meta"]["last_verified"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

            with open(path, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            log.info(f"  ✓ Saved (+{added})")

        time.sleep(4)  # Rate limit: 15 req/min = 1 cada 4 seg

    log.info(f"\nDone: +{total_added} results across {len(to_check)} leagues")


if __name__ == "__main__":
    main()
