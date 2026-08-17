#!/usr/bin/env python3
"""
BetAnalytics — Agente de Datos
Ejecutado diariamente por GitHub Actions.
Consulta todas las fuentes y escribe data/{league_key}.json.
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


def process_thesportsdb(key: str, cfg: dict) -> dict:
    """Procesa una liga de TheSportsDB."""
    lid = cfg["sportsdb_id"]
    season = cfg["season"]
    aliases = cfg.get("aliases", {})

    log.info(f"  TheSportsDB: league={lid} season={season}")
    results = sdb_results(lid, season)
    fixtures = sdb_fixtures(lid, season)

    # Aplicar aliases
    results = resolve_names(results, aliases)
    fixtures = resolve_names(fixtures, aliases)

    # Standings desde resultados
    standings = sdb_standings(results) if results else []

    # Calcular avg real
    total_goals = sum(r["hg"] + r["ag"] for r in results)
    total_matches = len(results)

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
        "results": results,
        "fixtures": fixtures,
    }

    # Incluir hist_season si está en config (para fallback inicio de temporada)
    if "hist_season" in cfg:
        data["hist_season"] = cfg["hist_season"]

    return data


def process_footballdata(key: str, cfg: dict) -> dict:
    """Procesa una liga de football-data.org."""
    code = cfg["fd_code"]
    aliases = cfg.get("aliases", {})

    if not FD_KEY:
        log.warning(f"  ⚠ No FOOTBALL_DATA_KEY — skipping {key}")
        return {}

    log.info(f"  football-data.org: code={code}")
    results = fd_results(code, FD_KEY)
    fixtures = fd_fixtures(code, FD_KEY)

    results = resolve_names(results, aliases)
    fixtures = resolve_names(fixtures, aliases)
    standings = fd_standings(results) if results else []

    total_goals = sum(r["hg"] + r["ag"] for r in results)
    total_matches = len(results)

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
        "results": results,
        "fixtures": fixtures,
    }

    if "hist_season" in cfg:
        data["hist_season"] = cfg["hist_season"]

    return data


def process_wikipedia(key: str, cfg: dict) -> dict:
    """Procesa una liga de Wikipedia (solo standings, no fixtures)."""
    wiki_url = cfg.get("wiki_url")
    if not wiki_url:
        log.warning(f"  ⚠ No wiki_url for {key} — skipping")
        return {}

    log.info(f"  Wikipedia: {wiki_url}")
    standings = wiki_standings(wiki_url)

    # Intentar fixtures desde TheSportsDB si tiene sportsdb_id
    fixtures = []
    if cfg.get("sportsdb_id"):
        season = cfg.get("season", "2026")
        fixtures = sdb_fixtures(cfg["sportsdb_id"], season)

    total_goals = sum(t.get("gf", 0) + t.get("ga", 0) for t in standings)
    total_matches = sum(t.get("pj", 0) for t in standings) // 2 if standings else 0

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
        "results": [],
        "fixtures": fixtures,
    }

    if "hist_season" in cfg:
        data["hist_season"] = cfg["hist_season"]

    return data


# ── Dispatcher ──────────────────────────────────────

PROCESSORS = {
    "thesportsdb": process_thesportsdb,
    "footballdata": process_footballdata,
    "wikipedia": process_wikipedia,
}


def main():
    config = load_config()
    log.info(f"BetAnalytics Fetcher — {len(config)} leagues configured")
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
            data = processor(key, cfg)
            if data:
                # Comparar con datos existentes para evitar commits innecesarios
                existing = load_existing(key)
                if existing:
                    # Solo actualizar si hay cambios en resultados o fixtures
                    old_n = existing.get("meta", {}).get("total_matches", 0)
                    new_n = data.get("meta", {}).get("total_matches", 0)
                    old_fix = len(existing.get("fixtures", []))
                    new_fix = len(data.get("fixtures", []))

                    if new_n == old_n and new_fix == old_fix and new_n > 0:
                        log.info(f"  — No changes (matches={new_n}, fixtures={new_fix})")
                        continue

                save_data(key, data)
                n_res = len(data.get("results", []))
                n_fix = len(data.get("fixtures", []))
                n_std = len(data.get("standings", []))
                log.info(f"  ✓ {n_res} results, {n_fix} fixtures, {n_std} teams in standings")
                updated += 1
        except Exception as e:
            log.error(f"  ✗ Error processing {key}: {e}")
            errors += 1

    log.info(f"\n{'='*50}")
    log.info(f"Done: {updated} updated, {errors} errors, {len(config) - updated - errors} unchanged")

    # Escribir registro de ejecución
    registry = {
        "last_run": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "updated": updated,
        "errors": errors,
        "total": len(config),
    }
    save_data("_registry", registry)


if __name__ == "__main__":
    main()
