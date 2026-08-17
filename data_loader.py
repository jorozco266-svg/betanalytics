"""
data_loader.py — Módulo para app.py
Reemplaza la lectura de HIST_CONMEBOL, fd_hist(), sportsdb_hist(), etc.
por lectura directa de los JSONs generados por el agente.

USO EN app.py:
    from data_loader import load_league_data, build_model_from_json

    data = load_league_data("laliga")
    hist = build_model_from_json(data, avg=1.35, blend_threshold=30)
    prox = data.get("fixtures", [])
"""
import json
import os
import datetime

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def load_league_data(league_key: str) -> dict | None:
    """Carga el JSON de una liga. Retorna None si no existe."""
    path = os.path.join(DATA_DIR, f"{league_key}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def build_model_from_json(data: dict, avg: float, blend_threshold: int = 30) -> dict:
    """
    Construye el modelo Poisson (dict de coeficientes atk/def) desde un JSON de liga.

    Lógica:
    1. Si hay suficientes resultados en la temporada actual → modelo dinámico
    2. Si hay pocos resultados pero existe hist_season → modelo histórico
    3. Si hay ambos y resultados >= blend_threshold → blend automático
    """
    results = data.get("results", [])
    standings = data.get("standings", [])
    hist_season = data.get("hist_season")

    n_matches = len(results)

    # ── Caso 1: Suficientes partidos → modelo dinámico ──
    if n_matches >= blend_threshold:
        model = _standings_to_model(standings, avg)
        if hist_season:
            hist_model = _hist_to_model(hist_season, avg)
            # Blend: peso dinámico crece con más partidos
            decay = min(0.7, n_matches / 200)
            model = _blend(hist_model, model, decay_base=decay)
            model["_info"] = f"Blend: {n_matches} partidos actuales + hist {hist_season['season']} (decay={decay:.2f})"
        else:
            model["_info"] = f"Modelo dinámico: {n_matches} partidos"
        return model

    # ── Caso 2: Pocos partidos + hist_season → hist como base ──
    if hist_season and hist_season.get("teams"):
        model = _hist_to_model(hist_season, avg)
        if n_matches > 0 and standings:
            model["_info"] = (
                f"Modelo histórico ({hist_season['season']}) — "
                f"solo {n_matches} partidos actuales (necesita ≥{blend_threshold} para blend)"
            )
        else:
            model["_info"] = f"Modelo histórico ({hist_season['season']}) — temporada aún no inicia o sin datos"
        return model

    # ── Caso 3: Datos dinámicos insuficientes pero algo hay ──
    if standings and len(standings) >= 5:
        model = _standings_to_model(standings, avg)
        model["_info"] = f"Modelo parcial: {n_matches} partidos, {len(standings)} equipos"
        return model

    return {"_avg": avg, "_info": "Sin datos suficientes"}


def get_fixtures_for_display(data: dict, days_ahead: int = 7) -> list[dict]:
    """
    Filtra fixtures para mostrar en la app (próximos N días).
    Convierte al formato que espera render_partido().
    """
    fixtures = data.get("fixtures", [])
    today = datetime.date.today()
    limit = today + datetime.timedelta(days=days_ahead)
    tz_col = datetime.timezone(datetime.timedelta(hours=-5))

    out = []
    for f in fixtures:
        try:
            match_date = datetime.date.fromisoformat(f["date"])
        except (ValueError, KeyError):
            continue
        if match_date < today or match_date > limit:
            continue

        # Construir datetime para is_hoy / is_manana
        time_str = f.get("time", "TBD")
        try:
            dt = datetime.datetime.strptime(f"{f['date']} {time_str}", "%Y-%m-%d %I:%M %p")
            dt = dt.replace(tzinfo=tz_col)
        except ValueError:
            dt = datetime.datetime(match_date.year, match_date.month, match_date.day, tzinfo=tz_col)

        out.append({
            "id": hash(f"{f['home']}{f['away']}{f['date']}") & 0xFFFFFFFF,
            "dt": dt,
            "fecha": f["date"],
            "hora": time_str,
            "local": f["home"],
            "visit": f["away"],
            "jornada": f.get("matchday", "?"),
            "hoy": match_date == today,
            "manana": match_date == today + datetime.timedelta(days=1),
        })

    out.sort(key=lambda x: x["dt"])
    return out


# ── Funciones internas ──────────────────────────────

def _standings_to_model(standings: list[dict], avg: float) -> dict:
    """Convierte standings JSON a modelo {equipo: {atk, def}, _avg}."""
    total_gf = sum(t["gf"] for t in standings)
    total_ga = sum(t["ga"] for t in standings)
    total_pj = sum(t["pj"] for t in standings)

    if total_pj == 0:
        return {"_avg": avg}

    avg_gf = total_gf / total_pj  # promedio de goles por equipo por partido
    avg_ga = total_ga / total_pj

    model = {"_avg": avg}
    for t in standings:
        pj = t["pj"]
        if pj == 0:
            continue
        atk = round((t["gf"] / pj) / avg_gf, 3) if avg_gf > 0 else 1.0
        dfn = round((t["ga"] / pj) / avg_ga, 3) if avg_ga > 0 else 1.0

        # Suavizado bayesiano (mínimo 0.30 atk, máximo 3.0)
        atk = max(0.30, min(3.0, atk))
        dfn = max(0.30, min(3.0, dfn))

        model[t["team"]] = {"atk": atk, "def": dfn, "_pj": pj, "_gf": t["gf"], "_ga": t["ga"]}

    return model


def _hist_to_model(hist: dict, avg: float) -> dict:
    """Convierte hist_season del config a modelo."""
    teams = hist.get("teams", [])
    pj_per_team = hist.get("pj_per_team", 38)

    total_gf = sum(t["gf"] for t in teams)
    total_pj = len(teams) * pj_per_team

    if total_pj == 0:
        return {"_avg": avg}

    avg_gf = total_gf / total_pj

    model = {"_avg": avg}
    for t in teams:
        pj = pj_per_team
        atk = round((t["gf"] / pj) / avg_gf, 3) if avg_gf > 0 else 1.0
        dfn = round((t["ga"] / pj) / avg_gf, 3) if avg_gf > 0 else 1.0
        atk = max(0.30, min(3.0, atk))
        dfn = max(0.30, min(3.0, dfn))
        model[t["team"]] = {"atk": atk, "def": dfn, "_pj": pj, "_gf": t["gf"], "_ga": t["ga"]}

    return model


def _blend(base: dict, recent: dict, decay_base: float = 0.5) -> dict:
    """Mezcla modelo histórico (base) con modelo reciente."""
    blended = {"_avg": recent.get("_avg", base.get("_avg", 1.35))}

    all_teams = set(k for k in base if not k.startswith("_")) | set(k for k in recent if not k.startswith("_"))

    for team in all_teams:
        b = base.get(team, {"atk": 1.0, "def": 1.0})
        r = recent.get(team, None)

        if r is None:
            # Solo en base (ej: equipo descendido) — usar con decay
            blended[team] = {"atk": b["atk"], "def": b["def"]}
        elif team not in base:
            # Solo en reciente (ej: ascendido) — usar directo
            blended[team] = {"atk": r["atk"], "def": r["def"]}
        else:
            # En ambos → blend ponderado
            w_recent = 1 - decay_base
            w_base = decay_base
            blended[team] = {
                "atk": round(b["atk"] * w_base + r["atk"] * w_recent, 3),
                "def": round(b["def"] * w_base + r["def"] * w_recent, 3),
            }

    return blended
