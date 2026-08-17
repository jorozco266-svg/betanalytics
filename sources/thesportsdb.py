"""
TheSportsDB — API gratuita (key pública = 3)
Cubre: BetPlay, La Liga, Bundesliga, Liga Argentina, Brasileirão, MLS, Liga MX, etc.
Docs: https://www.thesportsdb.com/free_sports_api
"""
import requests
import datetime
import logging

API_BASE = "https://www.thesportsdb.com/api/v1/json/3"
log = logging.getLogger("fetcher.thesportsdb")


def fetch_results(league_id: int, season: str) -> list[dict]:
    """Obtiene resultados (partidos terminados) de una liga/temporada."""
    url = f"{API_BASE}/eventsseason.php"
    params = {"id": league_id, "s": season}
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        events = r.json().get("events") or []
    except Exception as e:
        log.error(f"Error fetching results for league {league_id}: {e}")
        return []

    results = []
    for ev in events:
        hs = ev.get("intHomeScore")
        aws = ev.get("intAwayScore")
        if hs is None or aws is None:
            continue
        try:
            hg, ag = int(hs), int(aws)
        except (ValueError, TypeError):
            continue

        results.append({
            "date": ev.get("dateEvent", ""),
            "home": ev.get("strHomeTeam", ""),
            "away": ev.get("strAwayTeam", ""),
            "hg": hg,
            "ag": ag,
            "matchday": ev.get("intRound", ""),
        })

    results.sort(key=lambda x: x["date"])
    return results


def fetch_fixtures(league_id: int, season: str, days_ahead: int = 10) -> list[dict]:
    """Obtiene próximos partidos (sin resultado aún)."""
    url = f"{API_BASE}/eventsseason.php"
    params = {"id": league_id, "s": season}
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        events = r.json().get("events") or []
    except Exception as e:
        log.error(f"Error fetching fixtures for league {league_id}: {e}")
        return []

    today = datetime.date.today()
    limit = today + datetime.timedelta(days=days_ahead)
    fixtures = []

    for ev in events:
        # Solo partidos sin resultado
        if ev.get("intHomeScore") is not None:
            continue
        date_str = ev.get("dateEvent", "")
        try:
            match_date = datetime.date.fromisoformat(date_str)
        except ValueError:
            continue
        if match_date < today or match_date > limit:
            continue

        time_str = ev.get("strTime", "")
        if time_str:
            # Convertir de UTC "HH:MM:SS" a hora Colombia (UTC-5)
            try:
                h, m = int(time_str[:2]), int(time_str[3:5])
                utc_dt = datetime.datetime(match_date.year, match_date.month, match_date.day, h, m)
                col_dt = utc_dt - datetime.timedelta(hours=5)
                time_col = col_dt.strftime("%I:%M %p")
                # Si cruzó medianoche, ajustar fecha
                if col_dt.date() != match_date:
                    date_str = col_dt.date().isoformat()
            except (ValueError, IndexError):
                time_col = time_str
        else:
            time_col = "TBD"

        fixtures.append({
            "date": date_str,
            "time": time_col,
            "home": ev.get("strHomeTeam", ""),
            "away": ev.get("strAwayTeam", ""),
            "matchday": ev.get("intRound", ""),
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

    standings = sorted(teams.values(), key=lambda x: (-x["pts"], -(x["gf"] - x["ga"]), -x["gf"]))
    return standings
