"""
CONMEBOL Cups — Multi-source scraper
Combina Wikipedia (cross-tables de grupos + resultados de knockout)
con TheSportsDB (resultados que Wikipedia aún no tiene).
"""
import re
import requests
import logging
from bs4 import BeautifulSoup
from sources.thesportsdb import fetch_results as sdb_results, build_standings

log = logging.getLogger("fetcher.conmebol")

HEADERS = {"User-Agent": "BetAnalytics/1.0 (educational project)"}
SCORE_RE = re.compile(r"^(\d{1,2})\s*[-–—:]\s*(\d{1,2})$")


def fetch_all_results(cfg: dict) -> list[dict]:
    """
    Obtiene resultados de una copa CONMEBOL combinando:
    1. Wikipedia (cross-tables de fase de grupos + tablas de knockouts)
    2. TheSportsDB (captura partidos que Wikipedia aún no tiene)
    Retorna lista unificada de resultados.
    """
    all_results = []

    # ── Fuente 1: Wikipedia ──
    wiki_urls = cfg.get("wiki_urls", [])
    if wiki_urls:
        wiki_results = _scrape_wikipedia(wiki_urls)
        log.info(f"  Wikipedia: {len(wiki_results)} matches from {len(wiki_urls)} pages")
        all_results.extend(wiki_results)

    # ── Fuente 2: TheSportsDB ──
    sdb_ids = cfg.get("sportsdb_ids", [])
    season = cfg.get("season", "2026")
    for sid in sdb_ids:
        sdb = sdb_results(sid, season)
        if sdb:
            log.info(f"  TheSportsDB (id={sid}): {len(sdb)} matches")
            all_results.extend(sdb)

    # ── Merge: eliminar duplicados por key (home+away+score) ──
    merged = _deduplicate(all_results)
    log.info(f"  Total after dedup: {len(merged)} unique matches")

    return merged


def _scrape_wikipedia(wiki_urls: list[str]) -> list[dict]:
    """Scrape cross-tables y tablas de resultados individuales de Wikipedia."""
    results = []
    excluir = ["walkover", "void", "tbd", "bye"]

    for url in wiki_urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status()
        except Exception as e:
            log.warning(f"  Wikipedia error ({url}): {e}")
            continue

        soup = BeautifulSoup(r.text, "html.parser")
        for tabla in soup.find_all("table", class_="wikitable"):
            tabla_text = tabla.get_text()
            is_cross = "—" in tabla_text or "\u2014" in tabla_text or "\u2015" in tabla_text

            if is_cross:
                # Cross-table (fase de grupos)
                for loc, vis, g1, g2 in _parse_cross_table(tabla):
                    if _valid_name(loc) and _valid_name(vis):
                        if not any(e in loc.lower() or e in vis.lower() for e in excluir):
                            results.append({
                                "date": "", "home": loc.strip(), "away": vis.strip(),
                                "hg": g1, "ag": g2, "matchday": "group",
                                "_source": "wikipedia",
                            })
            else:
                # Tablas de knockouts (filas: Local | Score | Visitante)
                for fila in tabla.find_all("tr"):
                    celdas = [td.get_text(strip=True) for td in fila.find_all(["td", "th"])]
                    if len(celdas) < 3:
                        continue

                    match = _extract_match_from_row(celdas)
                    if match:
                        loc, vis, g1, g2 = match
                        if _valid_name(loc) and _valid_name(vis):
                            if not any(e in loc.lower() or e in vis.lower() for e in excluir):
                                results.append({
                                    "date": "", "home": loc.strip(), "away": vis.strip(),
                                    "hg": g1, "ag": g2, "matchday": "knockout",
                                    "_source": "wikipedia",
                                })

    return results


def _parse_cross_table(tabla) -> list[tuple]:
    """Extrae partidos de una cross-table (formato CONMEBOL grupos)."""
    filas = tabla.find_all("tr")
    if len(filas) < 3:
        return []

    equipo_filas = []
    for fila in filas:
        celdas = [td.get_text(strip=True) for td in fila.find_all(["td", "th"])]
        if "—" in celdas or "\u2014" in celdas or "\u2015" in celdas:
            equipo = celdas[1].strip() if len(celdas) > 1 else None
            dash_pos = None
            for i, c in enumerate(celdas):
                if c in ("—", "\u2014", "\u2015"):
                    dash_pos = i
                    break
            if equipo and dash_pos is not None and len(equipo) > 2:
                equipo_filas.append((equipo, celdas, dash_pos))

    if len(equipo_filas) < 2:
        return []

    first_dash = equipo_filas[0][2]
    n_teams = len(equipo_filas)
    equipos_orden = [ef[0] for ef in equipo_filas]

    resultados = []
    for row_idx, (equipo_local, celdas, dash_pos) in enumerate(equipo_filas):
        score_start = first_dash
        for col_offset in range(n_teams):
            col_idx = score_start + col_offset
            if col_idx >= len(celdas):
                continue
            if col_offset == row_idx:
                continue
            celda = celdas[col_idx]
            m = SCORE_RE.match(celda)
            if m:
                g1, g2 = int(m.group(1)), int(m.group(2))
                if g1 <= 9 and g2 <= 9:
                    equipo_visit = equipos_orden[col_offset]
                    resultados.append((equipo_local, equipo_visit, g1, g2))

    return resultados


def _extract_match_from_row(celdas: list[str]) -> tuple | None:
    """Intenta extraer Local, Visit, goles de una fila de tabla Wikipedia."""
    # Formato 1: Local | Score | Visitante (celdas[0], celdas[1], celdas[2])
    if len(celdas) >= 3:
        m = SCORE_RE.match(celdas[1])
        if m:
            g1, g2 = int(m.group(1)), int(m.group(2))
            if g1 <= 9 and g2 <= 9 and len(celdas[0]) > 2 and len(celdas[2]) > 2:
                return (celdas[0], celdas[2], g1, g2)

    # Formato 2: ... | Local | ... | Score | ... | Visitante (posiciones variables)
    if len(celdas) >= 5:
        m = SCORE_RE.match(celdas[3])
        if m:
            g1, g2 = int(m.group(1)), int(m.group(2))
            if g1 <= 9 and g2 <= 9:
                loc = celdas[2].strip() if len(celdas[2]) > 2 else celdas[0].strip()
                vis = celdas[4].strip() if len(celdas) > 4 and len(celdas[4]) > 2 else ""
                if len(loc) > 2 and len(vis) > 2:
                    return (loc, vis, g1, g2)

    return None


def _valid_name(name: str) -> bool:
    """Verifica que un nombre de equipo sea válido."""
    if not name or len(name) < 3:
        return False
    if name.isdigit():
        return False
    # Excluir headers de tabla
    if name.lower() in ("team", "club", "pos", "pld", "w", "d", "l", "gf", "ga", "gd", "pts",
                         "home", "away", "agg", "1st leg", "2nd leg", "score"):
        return False
    return True


def _normalize_for_dedup(name: str) -> str:
    """Normaliza nombre para comparación en dedup."""
    import unicodedata
    name = unicodedata.normalize("NFKD", name)
    name = "".join(c for c in name if not unicodedata.combining(c))
    return name.lower().strip().replace("fc ", "").replace(" fc", "").replace(".", "")


def _deduplicate(results: list[dict]) -> list[dict]:
    """
    Elimina duplicados entre Wikipedia y TheSportsDB.
    Prioriza TheSportsDB (tiene fechas) sobre Wikipedia (sin fechas).
    Un match se considera duplicado si home+away+score coinciden (normalizado).
    """
    seen = {}
    for r in results:
        h = _normalize_for_dedup(r["home"])
        a = _normalize_for_dedup(r["away"])
        key = f"{h}|{a}|{r['hg']}-{r['ag']}"

        if key not in seen:
            seen[key] = r
        else:
            # Si el existente es de Wikipedia (sin fecha) y el nuevo de SDB (con fecha), reemplazar
            existing = seen[key]
            if not existing.get("date") and r.get("date"):
                seen[key] = r

    return sorted(seen.values(), key=lambda x: x.get("date", "") or "9999")
