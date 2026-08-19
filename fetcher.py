#!/usr/bin/env python3
"""
BetAnalytics — Agente de Datos v2 (incremental)
Ejecutado diariamente por GitHub Actions.
- NUNCA sobrescribe resultados: mergea nuevos con existentes.
- Preserva hist_season entre corridas.
- Detecta fin de temporada y archiva la tabla final automáticamente.
"""
import json
import os
import datetime
import logging

from sources.thesportsdb import (
    fetch_results as sdb_results,
    fetch_fixtures as sdb_fixtures,
    build_standings as sdb_standings,
)
from sources.footballdata import (
    fetch_results as fd_results,
    fetch_fixtures as fd_fixtures,
    build_standings as fd_standings,
)
from sources.wikipedia import fetch_standings as wiki_standings
from sources.conmebol import fetch_all_results as conmebol_results

# ── Config ──────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config", "leagues.json")

FD_KEY = os.environ.get("FOOTBALL_DATA_KEY", "")
ODDS_KEY = os.environ.get("ODDS_API_KEY", "")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("fetcher")


def load_config() -> dict:
    with open(CONFIG_FILE) as f:
        return json.load(f)


def load_existing(league_key: str) -> dict | None:
    path = os.path.join(DATA_DIR, f"{league_key}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


def save_data(league_key: str, data: dict):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, f"{league_key}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    log.info(f"  ✓ Saved {path}")


def resolve_names(items: list[dict], aliases: dict, field_keys=("home", "away")) -> list[dict]:
    """Aplica aliases a nombres de equipos en results/fixtures."""
    for item in items:
        for key in field_keys:
            if key in item and item[key] in aliases:
                item[key] = aliases[item[key]]
    return items


def match_key(r: dict) -> str:
    """Clave única para un resultado: fecha+local+visitante."""
    return f"{r['date']}|{r['home']}|{r['away']}"


def merge_results(existing_results: list[dict], new_results: list[dict]) -> list[dict]:
    """
    Mergea resultados nuevos con existentes SIN perder datos.
    - Si un partido ya existe (misma fecha+local+visit), actualiza el score.
    - Si es nuevo, lo agrega.
    - NUNCA borra partidos existentes (aunque la API ya no los devuelva).
    """
    by_key = {match_key(r): r for r in existing_results}

    added = 0
    updated = 0
    for r in new_results:
        k = match_key(r)
        if k not in by_key:
            by_key[k] = r
            added += 1
        else:
            # Actualizar score si cambió (ej: partido en vivo → final)
            old = by_key[k]
            if old.get("hg") != r.get("hg") or old.get("ag") != r.get("ag"):
                by_key[k] = r
                updated += 1

    if added or updated:
        log.info(f"  Merge: +{added} nuevos, ~{updated} actualizados, {len(by_key)} total")

    merged = sorted(by_key.values(), key=lambda x: x.get("date", ""))
    return merged


def detect_season_end(existing: dict, new_results: list[dict], cfg: dict) -> dict | None:
    """
    Detecta fin de temporada: si la temporada existente tiene muchos partidos
    y no hay nuevos resultados por >14 días, archiva la tabla como hist_season.
    Retorna el hist_season a guardar, o None.
    """
    if not existing:
        return None

    old_results = existing.get("results", [])
    old_standings = existing.get("standings", [])
    old_season = existing.get("meta", {}).get("season", "")
    new_season = cfg.get("season", "")

    # Si la temporada cambió en config, archivar la anterior
    if old_season and new_season and old_season != new_season and len(old_standings) >= 10:
        log.info(f"  🔄 Temporada cambió: {old_season} → {new_season}. Archivando tabla como hist_season.")
        pj_max = max((t.get("pj", 0) for t in old_standings), default=0)
        return {
            "season": old_season,
            "pj_per_team": pj_max,
            "teams": [{"team": t["team"], "gf": t["gf"], "ga": t["ga"]} for t in old_standings],
            "_archived_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }

    # Si no hay resultados nuevos y ya hay muchos partidos, podría haber terminado
    if len(old_results) >= 100 and len(new_results) == 0:
        last_date = max((r.get("date", "") for r in old_results), default="")
        if last_date:
            try:
                last = datetime.date.fromisoformat(last_date)
                days_since = (datetime.date.today() - last).days
                if days_since > 21:
                    log.info(f"  ⚠ {days_since} días sin resultados nuevos. Posible fin de temporada.")
            except ValueError:
                pass

    return None


# ── Processors ──────────────────────────────────────

def process_thesportsdb(key: str, cfg: dict, existing: dict | None) -> dict:
    """Procesa una liga de TheSportsDB con merge incremental."""
    lid = cfg["sportsdb_id"]
    season = cfg["season"]
    aliases = cfg.get("aliases", {})

    log.info(f"  TheSportsDB: league={lid} season={season}")
    api_results = sdb_results(lid, season)
    fixtures = sdb_fixtures(lid, season)

    # Aplicar aliases
    api_results = resolve_names(api_results, aliases)
    fixtures = resolve_names(fixtures, aliases)

    # ── MERGE incremental ──
    existing_results = existing.get("results", []) if existing else []
    all_results = merge_results(existing_results, api_results)

    # Standings desde TODOS los resultados acumulados
    standings = sdb_standings(all_results) if all_results else []

    total_goals = sum(r["hg"] + r["ag"] for r in all_results)
    total_matches = len(all_results)

    # ── Preservar hist_season ──
    hist_season = None
    # 1. Detectar si la temporada terminó y archivar
    archived = detect_season_end(existing, api_results, cfg)
    if archived:
        hist_season = archived
    # 2. Si ya existía hist_season en el JSON, preservarlo
    elif existing and "hist_season" in existing:
        hist_season = existing["hist_season"]
    # 3. Si está en config (primera corrida), usar ese
    elif "hist_season" in cfg:
        hist_season = cfg["hist_season"]

    data = {
        "meta": {
            "league": cfg["name"],
            "league_key": key,
            "season": season,
            "source": "thesportsdb",
            "last_updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "avg_goals": cfg["avg"],
            "total_matches": total_matches,
            "total_goals": total_goals,
            "avg_real": round(total_goals / (total_matches * 2), 3) if total_matches > 0 else 0,
        },
        "standings": standings,
        "results": all_results,
        "fixtures": fixtures,
    }

    if hist_season:
        data["hist_season"] = hist_season

    return data


def process_footballdata(key: str, cfg: dict, existing: dict | None) -> dict:
    """Procesa una liga de football-data.org con merge incremental."""
    code = cfg["fd_code"]
    aliases = cfg.get("aliases", {})

    if not FD_KEY:
        log.warning(f"  ⚠ No FOOTBALL_DATA_KEY — skipping {key}")
        return {}

    log.info(f"  football-data.org: code={code}")
    api_results = fd_results(code, FD_KEY)
    fixtures = fd_fixtures(code, FD_KEY)

    api_results = resolve_names(api_results, aliases)
    fixtures = resolve_names(fixtures, aliases)

    # ── MERGE incremental ──
    existing_results = existing.get("results", []) if existing else []
    all_results = merge_results(existing_results, api_results)

    standings = fd_standings(all_results) if all_results else []

    total_goals = sum(r["hg"] + r["ag"] for r in all_results)
    total_matches = len(all_results)

    # ── Preservar hist_season ──
    hist_season = None
    archived = detect_season_end(existing, api_results, cfg)
    if archived:
        hist_season = archived
    elif existing and "hist_season" in existing:
        hist_season = existing["hist_season"]
    elif "hist_season" in cfg:
        hist_season = cfg["hist_season"]

    data = {
        "meta": {
            "league": cfg["name"],
            "league_key": key,
            "season": cfg.get("season", "current"),
            "source": "footballdata",
            "last_updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "avg_goals": cfg["avg"],
            "total_matches": total_matches,
            "total_goals": total_goals,
            "avg_real": round(total_goals / (total_matches * 2), 3) if total_matches > 0 else 0,
        },
        "standings": standings,
        "results": all_results,
        "fixtures": fixtures,
    }

    if hist_season:
        data["hist_season"] = hist_season

    return data


def process_wikipedia(key: str, cfg: dict, existing: dict | None) -> dict:
    """Procesa una liga de Wikipedia con preservación de datos."""
    wiki_url = cfg.get("wiki_url")
    if not wiki_url:
        log.warning(f"  ⚠ No wiki_url for {key} — skipping")
        return {}

    log.info(f"  Wikipedia: {wiki_url}")
    standings = wiki_standings(wiki_url)

    # Si Wikipedia no devolvió nada, preservar standings existentes
    if not standings and existing and existing.get("standings"):
        log.info(f"  Wikipedia sin datos — preservando standings anteriores ({len(existing['standings'])} equipos)")
        standings = existing["standings"]

    # Fixtures desde TheSportsDB si tiene sportsdb_id
    fixtures = []
    if cfg.get("sportsdb_id"):
        season = cfg.get("season", "2026")
        fixtures = sdb_fixtures(cfg["sportsdb_id"], season)

    # Preservar resultados existentes (Wikipedia no da resultados individuales)
    existing_results = existing.get("results", []) if existing else []

    total_goals = sum(t.get("gf", 0) + t.get("ga", 0) for t in standings)
    total_matches = sum(t.get("pj", 0) for t in standings) // 2 if standings else 0

    # ── Preservar hist_season ──
    hist_season = None
    if existing and "hist_season" in existing:
        hist_season = existing["hist_season"]
    elif "hist_season" in cfg:
        hist_season = cfg["hist_season"]

    data = {
        "meta": {
            "league": cfg["name"],
            "league_key": key,
            "season": cfg.get("season", "2026"),
            "source": "wikipedia",
            "last_updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "avg_goals": cfg["avg"],
            "total_matches": total_matches,
            "total_goals": total_goals // 2 if total_goals else 0,
            "avg_real": round(total_goals / (total_matches * 4), 3) if total_matches > 0 else 0,
        },
        "standings": standings,
        "results": existing_results,
        "fixtures": fixtures,
    }

    if hist_season:
        data["hist_season"] = hist_season

    return data


# ── Dispatcher ──────────────────────────────────────

def process_conmebol(key: str, cfg: dict, existing: dict | None) -> dict:
    """Procesa una copa CONMEBOL (Libertadores/Sudamericana) con multi-source."""
    aliases = cfg.get("aliases", {})

    log.info(f"  CONMEBOL multi-source")
    api_results = conmebol_results(cfg)

    # Aplicar aliases
    api_results = resolve_names(api_results, aliases)

    # ── MERGE incremental ──
    existing_results = existing.get("results", []) if existing else []
    all_results = merge_results(existing_results, api_results)

    # Standings desde todos los resultados
    standings = sdb_standings(all_results) if all_results else []

    total_goals = sum(r["hg"] + r["ag"] for r in all_results)
    total_matches = len(all_results)

    # Fixtures desde TheSportsDB
    fixtures = []
    for sid in cfg.get("sportsdb_ids", []):
        fx = sdb_fixtures(sid, cfg.get("season", "2026"))
        if fx:
            fixtures.extend(fx)
    fixtures = resolve_names(fixtures, aliases)

    # Preservar hist_season (copas no suelen tener, pero por consistencia)
    hist_season = None
    if existing and "hist_season" in existing:
        hist_season = existing["hist_season"]
    elif "hist_season" in cfg:
        hist_season = cfg["hist_season"]

    data = {
        "meta": {
            "league": cfg["name"],
            "league_key": key,
            "season": cfg.get("season", "2026"),
            "source": "conmebol_multi",
            "last_updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "avg_goals": cfg["avg"],
            "total_matches": total_matches,
            "total_goals": total_goals,
            "avg_real": round(total_goals / (total_matches * 2), 3) if total_matches > 0 else 0,
            "sources_used": ["wikipedia", "thesportsdb"],
        },
        "standings": standings,
        "results": all_results,
        "fixtures": fixtures,
    }

    if hist_season:
        data["hist_season"] = hist_season

    return data


PROCESSORS = {
    "thesportsdb": process_thesportsdb,
    "footballdata": process_footballdata,
    "wikipedia": process_wikipedia,
    "conmebol": process_conmebol,
}


def main():
    config = load_config()
    log.info(f"BetAnalytics Fetcher v2 (incremental) — {len(config)} leagues configured")
    log.info(f"FD_KEY: {'✓' if FD_KEY else '✗'}  ODDS_KEY: {'✓' if ODDS_KEY else '✗'}")

    updated = 0
    errors = 0

    for key, cfg in config.items():
        source = cfg.get("source", "")
        processor = PROCESSORS.get(source)

        if not processor:
            log.warning(f"⚠ Unknown source '{source}' for {key} — skipping")
            continue

        log.info(f"▸ {cfg['name']} ({key})")
        try:
            existing = load_existing(key)
            data = processor(key, cfg, existing)

            if not data:
                continue

            # Comparar con datos existentes para evitar commits innecesarios
            if existing:
                old_n = existing.get("meta", {}).get("total_matches", 0)
                new_n = data.get("meta", {}).get("total_matches", 0)
                old_fix = len(existing.get("fixtures", []))
                new_fix = len(data.get("fixtures", []))
                old_has_hist = "hist_season" in existing
                new_has_hist = "hist_season" in data

                if new_n == old_n and new_fix == old_fix and new_n > 0 and old_has_hist == new_has_hist:
                    log.info(f"  — No changes (matches={new_n}, fixtures={new_fix})")
                    continue

            save_data(key, data)
            n_res = len(data.get("results", []))
            n_fix = len(data.get("fixtures", []))
            n_std = len(data.get("standings", []))
            has_hist = "hist_season" in data
            log.info(f"  ✓ {n_res} results, {n_fix} fixtures, {n_std} teams, hist={'✓' if has_hist else '✗'}")
            updated += 1

        except Exception as e:
            log.error(f"  ✗ Error processing {key}: {e}")
            errors += 1

    log.info(f"\n{'='*50}")
    log.info(f"Done: {updated} updated, {errors} errors, {len(config) - updated - errors} unchanged")

    registry = {
        "last_run": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "updated": updated,
        "errors": errors,
        "total": len(config),
    }
    save_data("_registry", registry)


if __name__ == "__main__":
    main()
