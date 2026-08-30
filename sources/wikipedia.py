"""
Wikipedia — Scraper de tablas de posiciones
Cubre: Chile, Uruguay, Paraguay, Perú, Ecuador, Bolivia, Venezuela, ArgFem, K-League, etc.
"""
import requests
import re
import logging
from bs4 import BeautifulSoup

log = logging.getLogger("fetcher.wikipedia")

HEADERS = {"User-Agent": "BetAnalytics/1.0 (educational project)"}


def fetch_standings(wiki_url: str, table_index: int | None = None) -> list[dict]:
    """
    Extrae la tabla de posiciones estándar de una página de Wikipedia.
    Busca columnas: Equipo/Team, PJ/Pld/MP, GF/GS, GC/GA.
    """
    try:
        r = requests.get(wiki_url, headers=HEADERS, timeout=15)
        r.raise_for_status()
    except Exception as e:
        log.error(f"Error fetching Wikipedia page {wiki_url}: {e}")
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    tables = soup.find_all("table", class_="wikitable")

    # Buscar TODAS las tablas válidas de standings
    all_valid = []

    for table in tables:
        headers_row = table.find("tr")
        if not headers_row:
            continue
        header_texts = [th.get_text(strip=True).lower() for th in headers_row.find_all(["th", "td"])]

        # Verificar que tiene las columnas necesarias
        has_pts = any(h in header_texts for h in ["pts", "points", "puntos"])
        has_gf = any(h in header_texts for h in ["gf", "gs", "goles a favor", "goals for", "f"])
        has_ga = any(h in header_texts for h in ["gc", "ga", "goles en contra", "goals against", "a"])

        if not (has_pts and has_gf and has_ga):
            continue

        # Mapear índices de columnas
        col_map = {}
        for i, h in enumerate(header_texts):
            if h in ("pj", "pld", "mp", "played", "j") and "pj" not in col_map:
                col_map["pj"] = i
            elif h in ("gf", "gs", "f") and "gf" not in col_map:
                col_map["gf"] = i
            elif h in ("gc", "ga", "a") and "ga" not in col_map:
                col_map["ga"] = i
            elif h in ("pts", "points", "puntos") and "pts" not in col_map:
                col_map["pts"] = i
            elif h in ("w", "g", "won", "ganados") and "w" not in col_map:
                col_map["w"] = i
            elif h in ("d", "e", "drawn", "empatados") and "d" not in col_map:
                col_map["d"] = i
            elif h in ("l", "p", "lost", "perdidos") and "l" not in col_map:
                col_map["l"] = i

        if "gf" not in col_map or "ga" not in col_map:
            continue

        # Extraer filas de datos
        rows = table.find_all("tr")[1:]  # skip header
        standings = []

        for row in rows:
            cells = row.find_all(["td", "th"])
            if len(cells) < max(col_map.values()) + 1:
                continue

            # Encontrar nombre del equipo (primera celda con link o texto largo)
            team_name = None
            for cell in cells[:4]:
                link = cell.find("a")
                text = (link or cell).get_text(strip=True)
                # Filtrar números y textos cortos (posición, etc)
                if text and not text.isdigit() and len(text) > 2:
                    # Limpiar sufijos como (C), (R), (P)
                    text = re.sub(r"\s*\([CRPQS]\)\s*$", "", text).strip()
                    if text:
                        team_name = text
                        break

            if not team_name:
                continue

            def safe_int(idx):
                try:
                    return int(cells[idx].get_text(strip=True).replace(",", ""))
                except (ValueError, IndexError):
                    return 0

            entry = {
                "team": team_name,
                "gf": safe_int(col_map["gf"]),
                "ga": safe_int(col_map["ga"]),
                "pj": safe_int(col_map.get("pj", 0)),
            }
            if "pts" in col_map:
                entry["pts"] = safe_int(col_map["pts"])
            if "w" in col_map:
                entry["w"] = safe_int(col_map["w"])
            if "d" in col_map:
                entry["d"] = safe_int(col_map["d"])
            if "l" in col_map:
                entry["l"] = safe_int(col_map["l"])

            if entry["pj"] > 0:
                standings.append(entry)

        if len(standings) >= 5:
            all_valid.append(standings)

    if not all_valid:
        log.warning(f"Wikipedia: could not find standings table in {wiki_url}")
        return []

    # Seleccionar tabla: por índice explícito, o la más grande (para Overall tables)
    if table_index is not None:
        try:
            selected = all_valid[table_index]
        except IndexError:
            selected = all_valid[-1]  # fallback to last
    else:
        # Por defecto: la tabla con más equipos (Overall > Conference)
        selected = max(all_valid, key=len)

    log.info(f"Wikipedia: extracted {len(selected)} teams from {wiki_url} (selected from {len(all_valid)} valid tables)")
    return selected
