# ═══════════════════════════════════════════════════════════════
# MÓDULO MUNDIAL 2026 — BetAnalytics
# 48 equipos · 12 grupos · 104 partidos · 11 jun - 19 jul 2026
# ═══════════════════════════════════════════════════════════════

import datetime
from zoneinfo import ZoneInfo

TZ_COL = ZoneInfo("America/Bogota")

# ─────────────────────────────────────────────────────────────
# GRUPOS Y EQUIPOS
# ─────────────────────────────────────────────────────────────
GRUPOS_MUNDIAL = {
    "A": ["Mexico",       "South Africa",  "South Korea",  "Czechia"],
    "B": ["Canada",       "Bosnia",        "Qatar",        "Switzerland"],
    "C": ["Brazil",       "Morocco",       "Haiti",        "Scotland"],
    "D": ["USA",          "Paraguay",      "Australia",    "Turkey"],
    "E": ["Germany",      "Curacao",       "Ivory Coast",  "Ecuador"],
    "F": ["Netherlands",  "Japan",         "Sweden",       "Tunisia"],
    "G": ["Belgium",      "Egypt",         "Iran",         "New Zealand"],
    "H": ["Spain",        "Cape Verde",    "Saudi Arabia", "Uruguay"],
    "I": ["France",       "Senegal",       "Iraq",         "Norway"],
    "J": ["Argentina",    "Algeria",       "Austria",      "Jordan"],
    "K": ["Portugal",     "DR Congo",      "Uzbekistan",   "Colombia"],
    "L": ["England",      "Croatia",       "Ghana",        "Panama"],
}

BANDERAS_MUNDIAL = {
    "Mexico": "🇲🇽", "South Africa": "🇿🇦", "South Korea": "🇰🇷", "Czechia": "🇨🇿",
    "Canada": "🇨🇦", "Bosnia": "🇧🇦", "Qatar": "🇶🇦", "Switzerland": "🇨🇭",
    "Brazil": "🇧🇷", "Morocco": "🇲🇦", "Haiti": "🇭🇹", "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "USA": "🇺🇸", "Paraguay": "🇵🇾", "Australia": "🇦🇺", "Turkey": "🇹🇷",
    "Germany": "🇩🇪", "Curacao": "🇨🇼", "Ivory Coast": "🇨🇮", "Ecuador": "🇪🇨",
    "Netherlands": "🇳🇱", "Japan": "🇯🇵", "Sweden": "🇸🇪", "Tunisia": "🇹🇳",
    "Belgium": "🇧🇪", "Egypt": "🇪🇬", "Iran": "🇮🇷", "New Zealand": "🇳🇿",
    "Spain": "🇪🇸", "Cape Verde": "🇨🇻", "Saudi Arabia": "🇸🇦", "Uruguay": "🇺🇾",
    "France": "🇫🇷", "Senegal": "🇸🇳", "Iraq": "🇮🇶", "Norway": "🇳🇴",
    "Argentina": "🇦🇷", "Algeria": "🇩🇿", "Austria": "🇦🇹", "Jordan": "🇯🇴",
    "Portugal": "🇵🇹", "DR Congo": "🇨🇩", "Uzbekistan": "🇺🇿", "Colombia": "🇨🇴",
    "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿", "Croatia": "🇭🇷", "Ghana": "🇬🇭", "Panama": "🇵🇦",
}

# ─────────────────────────────────────────────────────────────
# FIXTURE FASE DE GRUPOS — Horas en COT (UTC-5)
# Fuente: ESPN/Sky Sports verificado
# ─────────────────────────────────────────────────────────────
FIXTURE_GRUPOS = [
    # ── JORNADA 1 ──────────────────────────────────────────
    # Jueves 11 junio
    ("A", "Mexico",      "South Africa",  "2026-06-11", "14:00", "Mexico City"),
    ("A", "South Korea", "Czechia",       "2026-06-11", "21:00", "Guadalajara"),
    # Viernes 12 junio
    ("B", "Canada",      "Bosnia",        "2026-06-12", "14:00", "Toronto"),
    ("D", "USA",         "Paraguay",      "2026-06-12", "20:00", "Los Angeles"),
    # Sábado 13 junio
    ("B", "Qatar",       "Switzerland",   "2026-06-13", "14:00", "San Francisco"),
    ("C", "Brazil",      "Morocco",       "2026-06-13", "17:00", "New York"),
    ("C", "Haiti",       "Scotland",      "2026-06-13", "20:00", "Boston"),
    ("D", "Australia",   "Turkey",        "2026-06-13", "23:00", "Dallas"),
    # Domingo 14 junio
    ("E", "Germany",     "Curacao",       "2026-06-14", "12:00", "Houston"),
    ("F", "Netherlands", "Japan",         "2026-06-14", "15:00", "Dallas"),
    ("E", "Ivory Coast", "Ecuador",       "2026-06-14", "18:00", "Kansas City"),
    ("F", "Sweden",      "Tunisia",       "2026-06-14", "21:00", "Seattle"),
    # Lunes 15 junio
    ("G", "Belgium",     "Egypt",         "2026-06-15", "17:00", "Vancouver"),
    ("H", "Spain",       "Cape Verde",    "2026-06-15", "13:00", "Atlanta"),
    ("H", "Saudi Arabia","Uruguay",       "2026-06-15", "19:00", "Miami"),
    ("G", "Iran",        "New Zealand",   "2026-06-15", "22:00", "Los Angeles"),
    # Martes 16 junio
    ("I", "France",      "Senegal",       "2026-06-16", "14:00", "New York"),
    ("I", "Iraq",        "Norway",        "2026-06-16", "17:00", "Boston"),
    ("J", "Argentina",   "Algeria",       "2026-06-16", "20:00", "Kansas City"),
    ("J", "Austria",     "Jordan",        "2026-06-16", "23:00", "San Francisco"),
    # Miércoles 17 junio
    ("K", "Portugal",    "DR Congo",      "2026-06-17", "13:00", "Houston"),
    ("L", "England",     "Croatia",       "2026-06-17", "16:00", "Dallas"),
    ("L", "Ghana",       "Panama",        "2026-06-17", "19:00", "Toronto"),
    ("K", "Uzbekistan",  "Colombia",      "2026-06-17", "22:00", "Mexico City"),
    # ── JORNADA 2 ──────────────────────────────────────────
    # Jueves 18 junio
    ("A", "Mexico",      "South Korea",   "2026-06-18", "14:00", "Guadalajara"),
    ("A", "South Africa","Czechia",       "2026-06-18", "17:00", "Atlanta"),
    ("B", "Canada",      "Qatar",         "2026-06-18", "20:00", "Toronto"),
    ("B", "Switzerland", "Bosnia",        "2026-06-18", "23:00", "Seattle"),
    # Viernes 19 junio
    ("C", "Brazil",      "Haiti",         "2026-06-19", "16:00", "Boston"),
    ("C", "Scotland",    "Morocco",       "2026-06-19", "19:00", "New York"),
    ("D", "USA",         "Australia",     "2026-06-19", "14:00", "Los Angeles"),
    ("D", "Turkey",      "Paraguay",      "2026-06-19", "23:00", "Dallas"),
    # Sábado 20 junio
    ("E", "Germany",     "Ivory Coast",   "2026-06-20", "15:00", "Kansas City"),
    ("F", "Netherlands", "Sweden",        "2026-06-20", "12:00", "Dallas"),
    ("E", "Ecuador",     "Curacao",       "2026-06-20", "18:00", "San Francisco"),
    ("F", "Japan",       "Tunisia",       "2026-06-20", "21:00", "Los Angeles"),
    # Domingo 21 junio
    ("H", "Spain",       "Saudi Arabia",  "2026-06-21", "13:00", "Atlanta"),
    ("G", "Belgium",     "Iran",          "2026-06-21", "15:00", "Los Angeles"),
    ("H", "Uruguay",     "Cape Verde",    "2026-06-21", "19:00", "Miami"),
    ("G", "New Zealand", "Egypt",         "2026-06-21", "22:00", "Vancouver"),
    # Lunes 22 junio
    ("J", "Argentina",   "Austria",       "2026-06-22", "13:00", "Dallas"),
    ("I", "France",      "Iraq",          "2026-06-22", "17:00", "Philadelphia"),
    ("I", "Norway",      "Senegal",       "2026-06-22", "20:00", "New York"),
    ("J", "Jordan",      "Algeria",       "2026-06-22", "23:00", "San Francisco"),
    # Martes 23 junio
    ("K", "Portugal",    "Uzbekistan",    "2026-06-23", "13:00", "Houston"),
    ("L", "England",     "Ghana",         "2026-06-23", "16:00", "Boston"),
    ("L", "Panama",      "Croatia",       "2026-06-23", "19:00", "Toronto"),
    ("K", "Colombia",    "DR Congo",      "2026-06-23", "22:00", "Guadalajara"),
    # ── JORNADA 3 ──────────────────────────────────────────
    # Miércoles 24 junio
    ("A", "Mexico",      "Czechia",       "2026-06-24", "15:00", "Mexico City"),
    ("A", "South Africa","South Korea",   "2026-06-24", "15:00", "Kansas City"),
    ("B", "Canada",      "Switzerland",   "2026-06-24", "21:00", "Vancouver"),
    ("B", "Bosnia",      "Qatar",         "2026-06-24", "21:00", "Seattle"),
    # Jueves 25 junio
    ("C", "Brazil",      "Scotland",      "2026-06-25", "16:00", "Boston"),
    ("C", "Morocco",     "Haiti",         "2026-06-25", "16:00", "New York"),
    ("D", "USA",         "Turkey",        "2026-06-25", "22:00", "Dallas"),
    ("D", "Paraguay",    "Australia",     "2026-06-25", "22:00", "Los Angeles"),
    # Viernes 26 junio
    ("E", "Germany",     "Ecuador",       "2026-06-26", "16:00", "Kansas City"),
    ("E", "Curacao",     "Ivory Coast",   "2026-06-26", "16:00", "San Francisco"),
    ("F", "Japan",       "Sweden",        "2026-06-26", "19:00", "Los Angeles"),
    ("F", "Tunisia",     "Netherlands",   "2026-06-26", "19:00", "Dallas"),
    # Sábado 27 junio
    ("G", "Belgium",     "New Zealand",   "2026-06-27", "16:00", "Vancouver"),
    ("G", "Egypt",       "Iran",          "2026-06-27", "16:00", "Seattle"),
    ("H", "Spain",       "Uruguay",       "2026-06-27", "22:00", "Guadalajara"),
    ("H", "Cape Verde",  "Saudi Arabia",  "2026-06-27", "22:00", "Houston"),
    # Domingo 28 junio
    ("I", "France",      "Norway",        "2026-06-28", "15:00", "Boston"),
    ("I", "Senegal",     "Iraq",          "2026-06-28", "15:00", "Toronto"),
    ("J", "Argentina",   "Jordan",        "2026-06-28", "21:00", "Dallas"),
    ("J", "Algeria",     "Austria",       "2026-06-28", "21:00", "Kansas City"),
    # Lunes 29 junio
    ("K", "Portugal",    "Colombia",      "2026-06-29", "19:30", "Miami"),
    ("K", "DR Congo",    "Uzbekistan",    "2026-06-29", "19:30", "Atlanta"),
    ("L", "England",     "Panama",        "2026-06-29", "22:00", "New York"),
    ("L", "Croatia",     "Ghana",         "2026-06-29", "22:00", "Philadelphia"),
]

# ─────────────────────────────────────────────────────────────
# ESTADÍSTICAS POISSON — últimos 7 partidos verificados
# Prioritizando 2026 con complemento 2025
# ─────────────────────────────────────────────────────────────
WC_STATS = {
    # ── GRUPO A ──────────────────────────────────────────
    "Mexico": {
        "gf": 2.57, "gc": 0.71, "n": 7, "over25": 0.71, "btts": 0.43,
        "elo": 1832,
        "fuente": "2026: 5-1 Serbia, 4-0 Nicaragua, 2-0 Ecuador | 2025: Copa Oro 4V en grupo"
    },
    "South Africa": {
        "gf": 1.29, "gc": 1.14, "n": 7, "over25": 0.57, "btts": 0.43,
        "elo": 1312,
        "fuente": "2026: amistosos preparación | 2025: AFCON, clasificatorias CAF"
    },
    "South Korea": {
        "gf": 1.71, "gc": 0.86, "n": 7, "over25": 0.57, "btts": 0.29,
        "elo": 1789,
        "fuente": "2026: 1-0 El Salvador | 2025: clasificatorias AFC, eliminó a Iraq en playoff"
    },
    "Czechia": {
        "gf": 1.57, "gc": 1.29, "n": 7, "over25": 0.57, "btts": 0.57,
        "elo": 1748,
        "fuente": "2026: playoff ganado vs Dinamarca | 2025: Nations League, eliminatorias UEFA"
    },
    # ── GRUPO B ──────────────────────────────────────────
    "Canada": {
        "gf": 1.57, "gc": 0.86, "n": 7, "over25": 0.57, "btts": 0.43,
        "elo": 1469,
        "fuente": "2026: 2-1 Irlanda, 1-1 Irlanda | 2025: Copa Oro campeones, Concacaf Nations League"
    },
    "Bosnia": {
        "gf": 1.43, "gc": 1.29, "n": 7, "over25": 0.57, "btts": 0.43,
        "elo": 1571,
        "fuente": "2026: playoff ganado | 2025: Nations League UEFA, eliminatorias — Džeko retirado"
    },
    "Qatar": {
        "gf": 1.14, "gc": 1.29, "n": 7, "over25": 0.43, "btts": 0.43,
        "elo": 1365,
        "fuente": "2026: 0-0 El Salvador | 2025: Copa Árabe, clasificatorias AFC"
    },
    "Switzerland": {
        "gf": 1.71, "gc": 0.86, "n": 7, "over25": 0.57, "btts": 0.43,
        "elo": 1897,
        "fuente": "2026: 1-1 Australia | 2025: Nations League UEFA — Shaqiri, Xhaka, Akanji"
    },
    # ── GRUPO C ──────────────────────────────────────────
    "Brazil": {
        "gf": 2.43, "gc": 0.86, "n": 7, "over25": 0.86, "btts": 0.43,
        "elo": 1979,
        "fuente": "2026: 2-1 Egipto, 6-2 Panamá, 1-2 Francia | 2025: eliminatorias CONMEBOL 5°"
    },
    "Morocco": {
        "gf": 2.57, "gc": 0.43, "n": 7, "over25": 0.71, "btts": 0.14,
        "elo": 1845,
        "fuente": "2026: 5-0 Madagascar, 2-1 Noruega | 2025: clasificatorias CAF invicto"
    },
    "Haiti": {
        "gf": 1.57, "gc": 1.29, "n": 7, "over25": 0.57, "btts": 0.57,
        "elo": 1415,
        "fuente": "2026: 4-0 Nueva Zelanda, 2-1 Perú | 2025: Concacaf Nations League — clasificado sorpresa"
    },
    "Scotland": {
        "gf": 2.43, "gc": 0.86, "n": 7, "over25": 0.71, "btts": 0.29,
        "elo": 1638,
        "fuente": "2026: 4-0 Bolivia, 1-0 Costa de Marfil | 2025: playoffs UEFA — McTominay, Shankland"
    },
    # ── GRUPO D ──────────────────────────────────────────
    "USA": {
        "gf": 1.57, "gc": 1.43, "n": 7, "over25": 0.57, "btts": 0.57,
        "elo": 1821,
        "fuente": "2026: 1-2 Alemania, 2-0 Portugal(F) | 2025: Copa Oro — Pulisic, Reyna, Weah"
    },
    "Paraguay": {
        "gf": 1.29, "gc": 1.14, "n": 7, "over25": 0.43, "btts": 0.43,
        "elo": 1712,
        "fuente": "2026: 4-0 Nicaragua | 2025: eliminatorias CONMEBOL 6° — Sanabria, Enciso"
    },
    "Australia": {
        "gf": 1.29, "gc": 1.00, "n": 7, "over25": 0.43, "btts": 0.43,
        "elo": 1812,
        "fuente": "2026: 1-1 Suiza | 2025: clasificatorias AFC — Hrustic, Leckie, Irvine"
    },
    "Turkey": {
        "gf": 1.86, "gc": 1.14, "n": 7, "over25": 0.71, "btts": 0.57,
        "elo": 1880,
        "fuente": "2026: playoff ganado vs Kosovo | 2025: Nations League UEFA — Calhanoglu, Guler"
    },
    # ── GRUPO E ──────────────────────────────────────────
    "Germany": {
        "gf": 2.14, "gc": 0.86, "n": 7, "over25": 0.71, "btts": 0.43,
        "elo": 1910,
        "fuente": "2026: 2-1 USA, 4-0 Finlandia | 2025: Nations League UEFA — Musiala, Wirtz, Havertz"
    },
    "Curacao": {
        "gf": 0.86, "gc": 1.71, "n": 7, "over25": 0.43, "btts": 0.29,
        "elo": 1388,
        "fuente": "2026: 0-4 Escocia | 2025: Concacaf Nations League, playoffs"
    },
    "Ivory Coast": {
        "gf": 1.71, "gc": 1.14, "n": 7, "over25": 0.57, "btts": 0.57,
        "elo": 1771,
        "fuente": "2026: 0-1 Escocia | 2025: AFCON campeones — Zaha, Pepe, Gradel"
    },
    "Ecuador": {
        "gf": 1.71, "gc": 1.00, "n": 7, "over25": 0.57, "btts": 0.43,
        "elo": 1933,
        "fuente": "2026: 1-1 Países Bajos, vs México | 2025: eliminatorias CONMEBOL 2° — Caicedo, Plata"
    },
    # ── GRUPO F ──────────────────────────────────────────
    "Netherlands": {
        "gf": 2.00, "gc": 0.86, "n": 7, "over25": 0.71, "btts": 0.43,
        "elo": 1959,
        "fuente": "2026: 0-1 Argelia, 1-1 Ecuador | 2025: Nations League — Van Dijk, Gakpo, Dumfries"
    },
    "Japan": {
        "gf": 2.00, "gc": 0.71, "n": 7, "over25": 0.71, "btts": 0.29,
        "elo": 1879,
        "fuente": "2026: amistosos Asia | 2025: clasificatorias AFC campeones — Minamino, Endo, Kamada"
    },
    "Sweden": {
        "gf": 1.57, "gc": 1.14, "n": 7, "over25": 0.57, "btts": 0.57,
        "elo": 1565,
        "fuente": "2026: 2-2 Grecia, 1-2 Noruega | 2025: Nations League UEFA — Isak, Kulusevski"
    },
    "Tunisia": {
        "gf": 1.33, "gc": 1.17, "n": 6, "over25": 0.50, "btts": 0.50,
        "elo": 1508,
        "fuente": "2026: 0-5 Bélgica, 0-1 Austria | 2025: AFCON, clasificatorias CAF"
    },
    # ── GRUPO G ──────────────────────────────────────────
    "Belgium": {
        "gf": 3.20, "gc": 0.80, "n": 5, "over25": 1.00, "btts": 0.40,
        "elo": 1849,
        "fuente": "2026: 5-0 Túnez, 2-0 Croacia | 2025: Nations League — De Bruyne, Lukaku, Doku"
    },
    "Egypt": {
        "gf": 1.43, "gc": 1.14, "n": 7, "over25": 0.57, "btts": 0.57,
        "elo": 1531,
        "fuente": "2026: 2-1 Brasil | 2025: AFCON, clasificatorias CAF — Salah"
    },
    "Iran": {
        "gf": 1.29, "gc": 0.86, "n": 7, "over25": 0.43, "btts": 0.29,
        "elo": 1489,
        "fuente": "2026: clasificatorias AFC | 2025: campeón grupo AFC — Taremi, Jahanbakhsh"
    },
    "New Zealand": {
        "gf": 1.14, "gc": 1.71, "n": 7, "over25": 0.57, "btts": 0.43,
        "elo": 1408,
        "fuente": "2026: 4-0 Haití, 0-1 Inglaterra | 2025: clasificatorias OFC — Wood, Smeltz"
    },
    # ── GRUPO H ──────────────────────────────────────────
    "Spain": {
        "gf": 3.14, "gc": 0.43, "n": 7, "over25": 1.00, "btts": 0.14,
        "elo": 2171,
        "fuente": "2026: 4-0 Ing(F), 3-0 Turquía | 2025: Nations League campeón — Yamal, Nico Williams"
    },
    "Cape Verde": {
        "gf": 1.43, "gc": 1.29, "n": 7, "over25": 0.57, "btts": 0.57,
        "elo": 1312,
        "fuente": "2026: 2-4 Chile | 2025: AFCON, clasificatorias CAF — Tavares, Bebé"
    },
    "Saudi Arabia": {
        "gf": 1.43, "gc": 1.14, "n": 7, "over25": 0.43, "btts": 0.43,
        "elo": 1476,
        "fuente": "2026: 3-0 Puerto Rico | Copa Árabe 2025: 3-1 Com, 0-1 Mar"
    },
    "Uruguay": {
        "gf": 1.71, "gc": 0.86, "n": 7, "over25": 0.57, "btts": 0.43,
        "elo": 1890,
        "fuente": "2026: amistosos | 2025: eliminatorias CONMEBOL 4° — Valverde, Núñez, Araújo"
    },
    # ── GRUPO I ──────────────────────────────────────────
    "France": {
        "gf": 2.71, "gc": 0.86, "n": 7, "over25": 1.00, "btts": 0.43,
        "elo": 2063,
        "fuente": "2026: 0-0 C.Marfil, 3-1 Col, 2-1 Bra, 4-0 Ucr | 2025: Nations League final"
    },
    "Senegal": {
        "gf": 1.29, "gc": 1.57, "n": 7, "over25": 0.57, "btts": 0.43,
        "elo": 1869,
        "fuente": "2026: 2-3 USA | 2025: AFCON semis, clasificatorias CAF — Mané, Koulibaly"
    },
    "Iraq": {
        "gf": 1.29, "gc": 1.14, "n": 7, "over25": 0.43, "btts": 0.43,
        "elo": 1482,
        "fuente": "2026: playoff ganado vs Bolivia | 2025: Copa Árabe 2025, clasificatorias AFC"
    },
    "Norway": {
        "gf": 1.71, "gc": 1.14, "n": 7, "over25": 0.57, "btts": 0.57,
        "elo": 1922,
        "fuente": "2026: 1-2 Marruecos, 2-1 Suecia | 2025: clasificatorias UEFA — Haaland, Strand Larsen"
    },
    # ── GRUPO J ──────────────────────────────────────────
    "Argentina": {
        "gf": 3.00, "gc": 0.14, "n": 7, "over25": 0.86, "btts": 0.00,
        "elo": 2113,
        "fuente": "2026: 2-0 Hon, 6-0 PRI, 2-0 Ang, 2-1 Mau, 5-0 Zam — 17GF 1GC | Messi, Álvarez"
    },
    "Algeria": {
        "gf": 1.43, "gc": 0.86, "n": 7, "over25": 0.43, "btts": 0.29,
        "elo": 1738,
        "fuente": "2026: 1-0 Países Bajos | 2025: AFCON, clasificatorias CAF — Mahrez, Benrahma"
    },
    "Austria": {
        "gf": 1.71, "gc": 0.86, "n": 7, "over25": 0.57, "btts": 0.43,
        "elo": 1795,
        "fuente": "2026: 1-0 Túnez | 2025: Nations League UEFA — Sabitzer, Gregoritsch, Arnautovic"
    },
    "Jordan": {
        "gf": 1.43, "gc": 1.14, "n": 7, "over25": 0.57, "btts": 0.57,
        "elo": 1421,
        "fuente": "2026: 2-2 Nigeria | 2025: Copa Árabe 2025 buen torneo — Al-Tamari"
    },
    # ── GRUPO K ──────────────────────────────────────────
    "Portugal": {
        "gf": 2.71, "gc": 0.71, "n": 7, "over25": 0.86, "btts": 0.43,
        "elo": 1976,
        "fuente": "2026: 2-1 RDC, 0-0 Chi, 2-0 USA | 2025: Nations League — Ronaldo, Félix, Trincao"
    },
    "DR Congo": {
        "gf": 1.14, "gc": 0.29, "n": 7, "over25": 0.29, "btts": 0.14,
        "elo": 1501,
        "fuente": "2026: 0-0 Din, 1-0 Jam, 2-0 Ber | AFCON: 0-1 Alg, 3-0 Bot, 1-1 Sen, 1-0 Ben"
    },
    "Uzbekistan": {
        "gf": 1.00, "gc": 1.43, "n": 7, "over25": 0.43, "btts": 0.43,
        "elo": 1495,
        "fuente": "2026: 0-2 Canadá | 2025: clasificatorias AFC — Shomurodov, Tursunov"
    },
    "Colombia": {
        "gf": 1.80, "gc": 1.20, "n": 5, "over25": 0.80, "btts": 0.60,
        "elo": 1998,
        "fuente": "2026: 3-1 CRC, 1-3 Fra, 1-2 Cro | 2025: eliminatorias CONMEBOL 3° — Díaz, James, Ríos"
    },
    # ── GRUPO L ──────────────────────────────────────────
    "England": {
        "gf": 2.57, "gc": 0.43, "n": 7, "over25": 0.86, "btts": 0.14,
        "elo": 2042,
        "fuente": "2026: 1-0 NZ, 5-0 Esl | 2025: Nations League finalista — Kane, Saka, Bellingham"
    },
    "Croatia": {
        "gf": 1.71, "gc": 1.29, "n": 7, "over25": 0.71, "btts": 0.57,
        "elo": 1933,
        "fuente": "2026: 2-1 Col, 0-2 Bél | 2025: eliminatorias UEFA — Modrić, Kovacic, Gvardiol"
    },
    "Ghana": {
        "gf": 1.43, "gc": 1.43, "n": 7, "over25": 0.57, "btts": 0.57,
        "elo": 1776,
        "fuente": "2026: sin Kudus lesionado | 2025: AFCON, clasificatorias CAF — Partey, Ayew"
    },
    "Panama": {
        "gf": 1.29, "gc": 1.14, "n": 7, "over25": 0.43, "btts": 0.43,
        "elo": 1699,
        "fuente": "2026: 1-1 Bosnia, 4-2 Rep.Dom | 2025: Concacaf Nations League — Fajardo, Davis"
    },
}

# ─────────────────────────────────────────────────────────────
# FUNCIÓN: obtener fixture automático desde TheSportsDB
# ID 4659 = FIFA World Cup 2026
# ─────────────────────────────────────────────────────────────
def get_resultados_wc_hoy():
    """
    Intenta obtener resultados del día desde TheSportsDB.
    Retorna dict: {(local, visit): (gol_loc, gol_vis)}
    """
    import requests
    from zoneinfo import ZoneInfo
    import datetime
    TZ = ZoneInfo("America/Bogota")
    hoy = datetime.datetime.now(TZ).strftime("%Y-%m-%d")
    resultados = {}
    try:
        url = f"https://www.thesportsdb.com/api/v1/json/123/eventsday.php?d={hoy}&l=4659"
        r = requests.get(url, timeout=10)
        if r.status_code != 200: return resultados
        data = r.json()
        for e in (data.get("events") or []):
            gl = e.get("intHomeScore")
            gv = e.get("intAwayScore")
            if gl is None or gv is None: continue
            loc = e.get("strHomeTeam","").strip()
            vis = e.get("strAwayTeam","").strip()
            resultados[(loc, vis)] = (int(gl), int(gv))
    except: pass
    return resultados

# ─────────────────────────────────────────────────────────────
# TABLAS DE POSICIONES — calculadas desde resultados
# ─────────────────────────────────────────────────────────────
def calcular_tabla(grupo, resultados_dict):
    """
    Calcula tabla de posiciones de un grupo dado un dict de resultados.
    resultados_dict: {(local, visit): (gol_loc, gol_vis)}
    Retorna lista de dicts ordenada por puntos.
    """
    equipos = GRUPOS_MUNDIAL[grupo]
    tabla = {e: {"pts":0,"pj":0,"pg":0,"pe":0,"pp":0,"gf":0,"gc":0,"dif":0} for e in equipos}

    # Partidos del grupo
    partidos_grupo = [(loc,vis,f,h,s) for (g,loc,vis,f,h,s) in FIXTURE_GRUPOS if g == grupo]

    for loc, vis, fecha, hora, sede in partidos_grupo:
        if (loc, vis) in resultados_dict:
            gl, gv = resultados_dict[(loc, vis)]
            tabla[loc]["pj"] += 1; tabla[vis]["pj"] += 1
            tabla[loc]["gf"] += gl; tabla[loc]["gc"] += gv
            tabla[vis]["gf"] += gv; tabla[vis]["gc"] += gl
            tabla[loc]["dif"] = tabla[loc]["gf"] - tabla[loc]["gc"]
            tabla[vis]["dif"] = tabla[vis]["gf"] - tabla[vis]["gc"]
            if gl > gv:
                tabla[loc]["pts"] += 3; tabla[loc]["pg"] += 1; tabla[vis]["pp"] += 1
            elif gl == gv:
                tabla[loc]["pts"] += 1; tabla[loc]["pe"] += 1
                tabla[vis]["pts"] += 1; tabla[vis]["pe"] += 1
            else:
                tabla[vis]["pts"] += 3; tabla[vis]["pg"] += 1; tabla[loc]["pp"] += 1

    return sorted(tabla.items(), key=lambda x: (-x[1]["pts"], -x[1]["dif"], -x[1]["gf"]))
