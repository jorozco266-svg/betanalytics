"""
football-data.org — API gratuita (10 req/min)
Cubre: Premier League, Serie A, Ligue 1, Primeira Liga, Champions League
Docs: https://www.football-data.org/documentation/quickstart
"""
import requests
import datetime
import logging

API_BASE = "https://api.football-data.org/v4"
log = logging.getLogger("fetcher.footballdata")


def fetch_results(code: str, api_key: str) -> list[dict]:
    """Obtiene partidos terminados de la temporada actual."""
    url = f"{API_BASE}/competitions/{code}/matches"
    params = {"status": "FINISHED"}
    headers = {"X-Auth-Token": api_key}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        matches = r.json().get("matches", [])
    except Exception as e:
        log.error(f"Error fetching results for {code}: {e}")
        return []

    results = []
    for m in matches:
        score = m.get("score", {}).get("fullTime", {})
        hg = score.get("home")
        ag = score.get("away")
        if hg is None or ag is None:
            continue
        results.append({
            "date": m.get("utcDate", "")[:10],
            "home": m["homeTeam"]["name"],
            "away": m["awayTeam"]["name"],
            "hg": hg,
            "ag": ag,
            "matchday": m.get("matchday", ""),
        })

    results.sort(key=lambda x: x["date"])
    return results


def fetch_fixtures(code: str, api_key: str, days_ahead: int = 10) -> list[dict]:
    """Obtiene próximos partidos programados."""
    url = f"{API_BASE}/competitions/{code}/matches"
    params = {"status": "SCHEDULED,TIMED"}
    headers = {"X-Auth-Token": api_key}
    try:
        r = requests.get(url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        matches = r.json().get("matches", [])
    except Exception as e:
        log.error(f"Error fetching fixtures for {code}: {e}")
        return []

    today = datetime.date.today()
    limit = today + datetime.timedelta(days=days_ahead)
    fixtures = []

    for m in matches:
        utc_str = m.get("utcDate", "")
        try:
            utc_dt = datetime.datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
            col_dt = utc_dt - datetime.timedelta(hours=5)
            match_date = col_dt.date()
        except (ValueError, AttributeError):
            continue

        if match_date < today or match_date > limit:
            continue

        fixtures.append({
            "date": match_date.isoformat(),
            "time": col_dt.strftime("%I:%M %p"),
            "home": m["homeTeam"]["name"],
            "away": m["awayTeam"]["name"],
            "matchday": m.get("matchday", ""),
        })

    fixtures.sort(key=lambda x: (x["date"], x["time"]))
    return fixtures


def build_standings(results: list[dict]) -> list[dict]:
    """Construye tabla de posiciones a partir de resultados."""
    teams = {}
    for r in results:
        for side, gf, ga in [("home", r["hg"], r["ag"]), ("away", r["ag"], r["hg"])]:
            name = r[side]
            if name not in teams:
                teams[name] = {"team": name, "pj": 0, "gf": 0, "ga": 0, "w": 0, "d": 0, "l": 0, "pts": 0}
            t = teams[name]
            t["pj"] += 1
            t["gf"] += gf
            t["ga"] += ga
            if gf > ga:
                t["w"] += 1; t["pts"] += 3
            elif gf == ga:
                t["d"] += 1; t["pts"] += 1
            else:
                t["l"] += 1

    return sorted(teams.values(), key=lambda x: (-x["pts"], -(x["gf"] - x["ga"]), -x["gf"]))
