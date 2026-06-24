"""
BetAnalytics v3.1
- Fix: @st.cache_data duplicado en wiki_next eliminado
- Fix: BK_INIT y bankroll inicial sincronizados a $70,213 COP
- Fix: Horas semifinales Liga BetPlay corregidas (6PM / 8:30PM)
- Fix: Liga Argentina y Liga MX migradas a Wikipedia inglés + use_odds_fixtures (mismo fix que Brasileirao)
- Paleta mejorada para PC: dark mode legible con buen contraste
- Ligas de Suramérica via API-Football (RapidAPI)
- Ligas europeas via football-data.org
- Bankroll dinámico: se descuenta al apostar, se acredita al ganar
"""

import math, datetime
from itertools import product as iproduct
from zoneinfo import ZoneInfo
import streamlit as st
import requests

st.set_page_config(page_title="BetAnalytics", page_icon="⚽", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Outfit:wght@400;500;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }

/* Fondo y texto base — más claros para mejor contraste en PC */
.stApp { background: #0f1623; color: #dde3f0; }
section[data-testid="stSidebar"] { background: #0b1018 !important; border-right: 1px solid #1f2d42; }

/* Títulos */
.brand { font-family:'Outfit',sans-serif; font-weight:800; font-size:2rem;
    background:linear-gradient(120deg,#38bdf8,#818cf8); -webkit-background-clip:text;
    -webkit-text-fill-color:transparent; line-height:1.1; margin:0; }
.eyebrow { font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:#64748b;
    letter-spacing:0.14em; text-transform:uppercase; margin-top:3px; }

/* Cards — fondo más visible */
.card { background:#1a2540; border:1px solid #253352; border-radius:14px; padding:16px 20px; margin-bottom:10px; }
.card-label { font-family:'JetBrains Mono',monospace; font-size:0.68rem; color:#7a8aaa;
    text-transform:uppercase; letter-spacing:0.1em; margin-bottom:4px; }
.card-value { font-size:1.7rem; font-weight:800; color:#e8eeff; line-height:1.2; }

/* Probabilidades */
.prob-wrap { background:#1a2540; border:1px solid #253352; border-radius:12px; padding:14px 16px; margin-bottom:8px; }
.prob-bar { background:#253352; border-radius:6px; height:10px; margin-top:8px; overflow:hidden; }

/* VALUE BET — verde brillante legible */
.vbet { background:#0d2a1a; border:1.5px solid #22c55e; border-radius:14px; padding:18px 22px; margin-bottom:10px; }
.vbet-badge { background:#22c55e; color:#021a0c; font-size:0.7rem; font-weight:700;
    padding:3px 12px; border-radius:20px; font-family:'JetBrains Mono',monospace; letter-spacing:0.05em; }
.vbet-title { font-size:1.1rem; font-weight:700; color:#f0fff4; margin-top:10px; }
.vbet-grid { display:flex; gap:20px; margin-top:12px; flex-wrap:wrap; }
.vbet-item label { font-family:'JetBrains Mono',monospace; font-size:0.65rem; color:#4ade80; display:block; }
.vbet-item span { font-size:1rem; font-weight:700; color:#f0fff4; }
.vbet-item span.highlight { color:#38bdf8; font-size:1.2rem; }

/* SIN VALUE */
.nobet { background:#151f33; border:1px solid #253352; border-radius:10px;
    padding:12px 16px; margin-bottom:8px; display:flex; align-items:center; gap:10px; }
.nobet-badge { background:#253352; color:#7a8aaa; font-size:0.68rem; font-weight:600;
    padding:3px 10px; border-radius:12px; font-family:'JetBrains Mono',monospace; white-space:nowrap; }
.nobet-text { color:#94a3b8; font-size:0.9rem; }

/* VIG */
.vig-ok   { background:#0d2a1a; border:1px solid #22c55e; border-radius:8px; padding:8px 14px;
    font-size:0.82rem; color:#86efac; font-family:'JetBrains Mono',monospace; margin:10px 0; }
.vig-warn { background:#2a1a00; border:1px solid #f59e0b; border-radius:8px; padding:8px 14px;
    font-size:0.82rem; color:#fcd34d; font-family:'JetBrains Mono',monospace; margin:10px 0; }
.vig-bad  { background:#2a0d0d; border:1px solid #ef4444; border-radius:8px; padding:8px 14px;
    font-size:0.82rem; color:#fca5a5; font-family:'JetBrains Mono',monospace; margin:10px 0; }

/* Day headers */
.day-hdr { font-family:'JetBrains Mono',monospace; font-size:0.72rem; color:#38bdf8;
    text-transform:uppercase; letter-spacing:0.12em; padding:8px 0 6px;
    border-bottom:1px solid #1f2d42; margin:20px 0 12px; }
.hoy-pill { background:#38bdf8; color:#0b1018; font-size:0.62rem; font-weight:700;
    padding:2px 9px; border-radius:10px; margin-left:8px; vertical-align:middle; }

/* Apuestas tracker */
.bet-row { background:#1a2540; border:1px solid #253352; border-radius:10px;
    padding:12px 16px; margin-bottom:8px; font-size:0.88rem; color:#dde3f0; }
.bet-won  { border-left:3px solid #22c55e; }
.bet-lost { border-left:3px solid #ef4444; }
.bet-pend { border-left:3px solid #f59e0b; }

/* Casos de estudio */
.caso { background:#131e30; border-left:3px solid #38bdf8; border-radius:0 10px 10px 0;
    padding:14px 18px; margin-bottom:12px; }
.caso-meta { font-family:'JetBrains Mono',monospace; font-size:0.68rem; color:#38bdf8;
    letter-spacing:0.08em; }
.caso-title { font-size:1rem; font-weight:700; color:#e8eeff; margin:4px 0; }
.caso-chips { display:flex; gap:12px; flex-wrap:wrap; font-size:0.8rem; color:#94a3b8; margin-top:6px; }
.caso-lesson { font-size:0.82rem; color:#7a8aaa; font-style:italic; margin-top:8px; }

/* Marcadores */
.score-card { background:#1a2540; border:1px solid #253352; border-radius:10px;
    text-align:center; padding:12px 8px; }
.score-num { font-size:1.1rem; font-weight:800; color:#e8eeff; }
.score-pct { font-size:0.72rem; color:#64748b; font-family:'JetBrains Mono',monospace; }

/* Inputs overrides */
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input { background:#1a2540 !important; color:#e8eeff !important; border-color:#253352 !important; }
div[data-testid="stSelectbox"] > div { background:#1a2540 !important; color:#e8eeff !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────
API_FD   = "https://api.football-data.org/v4"
API_ODDS = "https://api.the-odds-api.com/v4"
API_RF   = "https://v3.football.api-sports.io"
API_TSDB = "https://www.thesportsdb.com/api/v1/json/3"
TZ_COL   = ZoneInfo("America/Bogota")
FL       = 1.15
MG       = 8
BK_INIT  = 119613

# Liga: source indica de dónde se obtienen los datos
# fd = football-data.org | rf = api-football (RapidAPI)
LIGAS = {
    "🇪🇸 La Liga":            {"src":"fd","code":"PD",  "avg":1.35, "odds_key":"soccer_spain_la_liga"},
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League":    {"src":"fd","code":"PL",  "avg":1.40, "odds_key":"soccer_epl"},
    "🇩🇪 Bundesliga":          {"src":"fd","code":"BL1", "avg":1.55, "odds_key":"soccer_germany_bundesliga"},
    "🇮🇹 Serie A":             {"src":"fd","code":"SA",  "avg":1.30, "odds_key":"soccer_italy_serie_a"},
    "🇫🇷 Ligue 1":             {"src":"fd","code":"FL1", "avg":1.35, "odds_key":"soccer_france_ligue_one"},
    "🇵🇹 Primeira Liga":       {"src":"fd","code":"PPL", "avg":1.30, "odds_key":None},
    "🏆 Champions League":     {"src":"fd","code":"CL",  "avg":1.45, "odds_key":"soccer_uefa_champs_league"},
    "🏆 Europa League":        {"src":"wiki_multi","wiki_urls":["https://en.wikipedia.org/wiki/2025%E2%80%9326_UEFA_Europa_League_league_phase","https://en.wikipedia.org/wiki/2025%E2%80%9326_UEFA_Europa_League_knockout_phase"],"wiki_fmt":"uel","avg":1.35,"odds_key":"soccer_uefa_europa_league","use_odds_fixtures":True},
    "🇨🇴 Liga BetPlay":        {"src":"wiki","wiki_url":"https://es.wikipedia.org/wiki/Torneo_Apertura_2026_(Colombia)",       "wiki_fmt":"betplay",  "avg":1.20, "odds_key":None,
                                "equipos_excluir":["Villavicencio","Tigres","Real Cartagena","Bogota FC","Union Magdalena","Deportes Quindio","Real Cundinamarca","Independiente Yumbo","Atletico Huila","Barranquilla","Leones","Orsomarso","Real Santander","Universitario de Popayan"]},
    "🇨🇴 Torneo BetPlay B":    {"src":"wiki","wiki_url":"https://es.wikipedia.org/wiki/Primera_B_2026_(Colombia)",            "wiki_fmt":"betplay",  "avg":1.10, "odds_key":None},
    "🏆 Copa Libertadores":    {"src":"wiki","wiki_url":"https://es.wikipedia.org/wiki/Copa_Libertadores_2026",                  "wiki_fmt":"conmebol", "avg":1.25, "odds_key":"soccer_conmebol_copa_libertadores"},
    "🏆 Copa Sudamericana":    {"src":"wiki","wiki_url":"https://es.wikipedia.org/wiki/Copa_Sudamericana_2026",                  "wiki_fmt":"conmebol", "avg":1.20, "odds_key":"soccer_conmebol_copa_sudamericana"},
    "🇦🇷 Liga Argentina":      {"src":"sportsdb","sportsdb_id":4406,"sportsdb_season":"2026","avg":1.30,"odds_key":"soccer_argentina_primera_division","use_odds_fixtures":True},
    "🇧🇷 Brasileirao":         {"src":"sportsdb","sportsdb_id":4351,"sportsdb_season":"2026-2027","avg":1.35,"odds_key":"soccer_brazil_campeonato","use_odds_fixtures":True},
    "🇨🇱 Chile - Liga 1ª":    {"src":"wiki_tabla","wiki_url":"https://en.wikipedia.org/wiki/2026_Liga_de_Primera","avg":1.25,"odds_key":"soccer_chile_campeonato","use_odds_fixtures":True,"sportsdb_id":4627,"hist_fallback":"Chile"},
    "🇺🇾 Uruguay - Clausura":  {"src":"wiki_tabla","wiki_url":"https://en.wikipedia.org/wiki/2026_Uruguayan_Primera_Divisi%C3%B3n","avg":1.30,"odds_key":None,"use_odds_fixtures":False,"sportsdb_id":4432,"hist_fallback":"Uruguay"},
    "🇵🇾 Paraguay - Div Prof": {"src":"wiki_tabla","wiki_url":"https://en.wikipedia.org/wiki/2026_Copa_de_Primera","avg":1.25,"odds_key":None,"use_odds_fixtures":False,"sportsdb_id":4687,"hist_fallback":"Paraguay"},
    "🇵🇪 Perú - Liga 1":       {"src":"wiki_tabla","wiki_url":"https://en.wikipedia.org/wiki/2026_Liga_1_(Peru)","avg":1.20,"odds_key":None,"use_odds_fixtures":False,"sportsdb_id":4688,"hist_fallback":"Peru"},
    "🇪🇨 Ecuador - LigaPro":   {"src":"wiki_tabla","wiki_url":"https://en.wikipedia.org/wiki/2026_LigaPro_Serie_A","avg":1.25,"odds_key":None,"use_odds_fixtures":False,"sportsdb_id":4686,"hist_fallback":"Ecuador"},
    "🇧🇴 Bolivia - Div Prof":  {"src":"wiki_tabla","wiki_url":"https://en.wikipedia.org/wiki/2026_Bolivian_Football_Championship","avg":1.30,"odds_key":None,"use_odds_fixtures":False,"sportsdb_id":4685,"hist_fallback":"Bolivia"},
    "🇻🇪 Venezuela - 1ª Div":  {"src":"wiki_tabla","wiki_url":"https://en.wikipedia.org/wiki/2025%E2%80%9326_Venezuelan_Primera_Divisi%C3%B3n","avg":1.20,"odds_key":None,"use_odds_fixtures":False,"sportsdb_id":4513,"hist_fallback":"Venezuela"},
    "🇲🇽 Liga MX":             {"src":"sportsdb","sportsdb_id":4350,"sportsdb_season":"2025-2026","avg":1.25,"odds_key":"soccer_mexico_ligamx","use_odds_fixtures":True},
    "🇪🇸 Liga F (Femenina)":   {"src":"sportsdb","sportsdb_id":5106,"sportsdb_season":"2025-2026","avg":1.20,"odds_key":"soccer_spain_la_liga_women","use_odds_fixtures":True},
    "🇮🇪 Irlanda - Div":       {"src":"wiki_tabla","wiki_url":"https://en.wikipedia.org/wiki/2026_League_of_Ireland_First_Division","avg":1.35,"odds_key":"soccer_league_of_ireland","use_odds_fixtures":True,"sportsdb_id":4757},
}

# ─────────────────────────────────────────────
# TIEMPO
# ─────────────────────────────────────────────
def to_col(s):
    try: return datetime.datetime.fromisoformat(s.replace("Z","+00:00")).astimezone(TZ_COL)
    except: return None

def es_hoy(dt):    return dt.date()==datetime.datetime.now(TZ_COL).date()
def es_manana(dt): return dt.date()==(datetime.datetime.now(TZ_COL)+datetime.timedelta(days=1)).date()

# ─────────────────────────────────────────────
# MODELO POISSON
# ─────────────────────────────────────────────
def build_model_desde_tabla(tabla_goles, avg):
    """
    Construye modelo Poisson directamente desde tabla de posiciones (GF, GC, PJ).
    Evita partidos sintéticos que contaminan el modelo con un equipo ficticio.
    """
    modelo = {}
    for equipo, gf, gc, pj in tabla_goles:
        if pj == 0: continue
        gf_avg = gf / pj
        gc_avg = gc / pj
        modelo[equipo] = {
            "atk":    round(gf_avg / avg, 3),
            "def":    round(gc_avg / avg, 3),
            "n":      pj,
            "gf_avg": round(gf_avg, 2),
            "gc_avg": round(gc_avg, 2),
            "partidos": [],
        }
    modelo["_avg"] = avg
    return modelo

# Tabla de posiciones Brasileirao Serie A 2026 (al 24-mayo-2026, jornada 16-17)
# Fuente: Wikipedia. Formato: (equipo, GF, GC, PJ)
HIST_BRASILEIRAO_2026 = [
    ("Palmeiras",            23, 10, 13),
    ("Flamengo",             24, 10, 12),
    ("Fluminense",           23, 16, 13),
    ("Sao Paulo",            17, 11, 13),
    ("Athletico Paranaense", 20, 15, 13),
    ("Bahia",                17, 14, 12),
    ("Coritiba",             15, 13, 13),
    ("Botafogo",             24, 24, 12),
    ("Red Bull Bragantino",  15, 15, 13),
    ("Vasco da Gama",        18, 19, 13),
    ("Gremio",               15, 16, 13),
    ("Cruzeiro",             17, 21, 13),
    ("Vitoria",              12, 17, 12),
    ("Corinthians",           9, 11, 13),
    ("Atletico Mineiro",     14, 19, 13),
    ("Internacional",        12, 14, 13),
    ("Santos",               18, 21, 13),
    ("Mirassol",             13, 18, 12),
    ("Remo",                 13, 23, 13),
    ("Chapecoense",          12, 24, 12),
]
# Fuente: Wikipedia / ESPN. Formato: (equipo, GF, GC, PJ)
HIST_ARGENTINA_2026 = [
    ("River Plate",          38, 18, 18),
    ("Boca Juniors",         33, 17, 18),
    ("Racing",               31, 19, 18),
    ("Independiente",        28, 22, 18),
    ("Estudiantes (LP)",     27, 20, 18),
    ("Talleres (C)",         26, 21, 18),
    ("Huracán",              25, 22, 18),
    ("San Lorenzo",          24, 24, 18),
    ("Belgrano",             23, 25, 18),
    ("Defensa y Justicia",   22, 23, 18),
    ("Lanús",                30, 24, 18),
    ("Rosario Central",      24, 26, 18),
    ("Gimnasia y Esgrima (LP)", 21, 27, 18),
    ("Atlético Tucumán",     20, 26, 18),
    ("Platense",             19, 25, 18),
    ("Banfield",             18, 27, 18),
    ("Vélez Sarsfield",      22, 28, 18),
    ("Newell's Old Boys",    17, 28, 18),
    ("Instituto",            18, 30, 18),
    ("Tigre",                17, 29, 18),
    ("Barracas Central",     16, 29, 18),
    ("Sarmiento (J)",        15, 31, 18),
    ("Argentinos Juniors",   19, 28, 18),
    ("Unión",                20, 30, 18),
    ("Central Córdoba (SdE)", 14, 32, 18),
    ("Aldosivi",             13, 33, 18),
    ("Deportivo Riestra",    12, 35, 18),
    ("Estudiantes (RC)",     11, 36, 18),
    ("Gimnasia y Esgrima (M)", 13, 34, 18),
    ("Independiente Rivadavia", 14, 33, 18),
]

# Tabla de posiciones Liga MX Clausura 2026 (fase regular completa — 17 jornadas)
# Fuente: Wikipedia / El Universal. Formato: (equipo, GF, GC, PJ)
HIST_LIGAMX_2026 = [
    ("Pumas UNAM",        32, 14, 17),  # Pumas — 1ro 36 pts
    ("Guadalajara",       28, 15, 17),  # Chivas — 2do 36 pts
    ("Cruz Azul",         27, 18, 17),  # 3ro 33 pts
    ("Pachuca",           29, 19, 17),  # 4to 31 pts
    ("Toluca",            26, 18, 17),  # 5to 30 pts
    ("Atlas",             22, 20, 17),  # 6to 26 pts
    ("Tigres UANL",       24, 21, 17),  # Tigres — 7mo 25 pts
    ("Club America",      21, 22, 17),  # América — 8vo 25 pts
    ("Leon",              20, 23, 17),
    ("Queretaro",         18, 22, 17),
    ("Monterrey",         19, 24, 17),
    ("Atletico San Luis", 17, 23, 17),
    ("Necaxa",            16, 22, 17),
    ("Juarez",            15, 25, 17),
    ("Mazatlan",          14, 26, 17),
    ("Puebla",            13, 27, 17),
    ("Santos Laguna",     12, 26, 17),
    ("Tijuana",           13, 28, 17),
]

# ─────────────────────────────────────────────
# TABLAS ESTÁTICAS CONMEBOL — Fallback cuando Wikipedia no tiene formato estándar
# Fuente: Wikipedia / ESPN al 31-mayo-2026. Formato: (equipo, GF, GC, PJ)
# ─────────────────────────────────────────────
HIST_CONMEBOL = {
    "Chile": [
        ("Colo-Colo",            28, 12, 15), ("Universidad de Chile",  24, 14, 15),
        ("Universidad Católica", 22, 15, 15), ("Coquimbo Unido",        20, 15, 14),
        ("Huachipato",           19, 16, 15), ("Audax Italiano",        18, 17, 14),
        ("O'Higgins",            17, 18, 15), ("Ñublense",              16, 17, 14),
        ("Cobresal",             15, 18, 14), ("Palestino",             14, 18, 15),
        ("Everton",              13, 19, 14), ("Cobreloa",              12, 20, 14),
        ("Deportes Iquique",     11, 21, 14), ("Deportes Antofagasta",  10, 22, 14),
        ("Rangers",               9, 23, 14), ("Unión La Calera",        8, 24, 14),
    ],
    "Uruguay": [
        # Fuente: Tabla Apertura 2026 — 15 jornadas completas (datos verificados)
        ("Racing Montevideo",      23, 14, 15), ("Deportivo Maldonado",    24, 16, 15),
        ("Albion",                 26, 16, 15), ("Peñarol",                23, 16, 15),
        ("Central Español",        23, 22, 15), ("Montevideo City Torque", 22, 16, 15),
        ("Nacional",               26, 21, 15), ("Defensor Sporting",      13, 11, 15),
        ("Liverpool Montevideo",   20, 18, 15), ("Montevideo Wanderers",   16, 21, 15),
        ("Danubio",                17, 21, 15), ("Cerro Largo",            16, 19, 15),
        ("Boston River",           14, 20, 15), ("Juventud",               17, 22, 15),
        ("Progreso",               12, 23, 15), ("Cerro",                   8, 24, 15),
    ],
    "Paraguay": [
        ("Libertad",              32, 10, 14), ("Olimpia",               28, 13, 14),
        ("Cerro Porteño",         26, 14, 14), ("Guaraní",               22, 16, 14),
        ("Sol de América",        20, 17, 14), ("Nacional",              18, 18, 14),
        ("Sportivo Luqueño",      16, 19, 14), ("General Caballero JLM", 15, 20, 14),
        ("12 de Octubre",         14, 21, 14), ("Resistencia",           13, 22, 13),
        ("Tacuary",               12, 23, 13), ("Sportivo Ameliano",     11, 24, 13),
    ],
    "Peru": [
        ("Universitario",         30, 12, 15), ("Sporting Cristal",      27, 14, 15),
        ("Alianza Lima",          25, 15, 15), ("Cusco FC",              22, 16, 14),
        ("Melgar",                20, 17, 14), ("Municipal",             18, 18, 14),
        ("Cienciano",             17, 19, 14), ("Sport Huancayo",        16, 19, 14),
        ("Binacional",            15, 20, 14), ("ADT",                   14, 21, 14),
        ("UTC Cajamarca",         13, 22, 13), ("Vallejo",               12, 23, 13),
        ("Cesar Vallejo",         11, 24, 13), ("Deportivo Garcilaso",   10, 25, 13),
        ("Sport Boys",             9, 26, 13), ("Carlos Stein",           8, 27, 13),
        ("Los Chankas",            7, 28, 13), ("Unión Comercio",         6, 29, 12),
    ],
    "Ecuador": [
        ("Liga de Quito",           28, 14, 15), ("Independiente del Valle", 26, 17, 15),
        ("Barcelona SC",            24, 16, 15), ("Emelec",                  22, 14, 15),
        ("Universidad Católica",    21, 15, 15), ("Aucas",                   20, 18, 15),
        ("Delfín",                  19, 19, 15), ("Orense",                  17, 20, 15),
        ("Técnico Universitario",   16, 21, 15), ("Macará",                  14, 20, 15),
        ("Mushuc Runa",             13, 22, 15), ("Deportivo Cuenca",        12, 21, 15),
        ("Guayaquil City",          11, 24, 15), ("Libertad",                10, 25, 15),
        ("Manta FC",                 9, 26, 15), ("Leones",                   8, 27, 15),
    ],
    "Bolivia": [
        ("Bolívar",                30, 10, 14), ("Always Ready",           26, 12, 14),
        ("The Strongest",          24, 14, 14), ("Oriente Petrolero",      20, 16, 14),
        ("Blooming",               18, 17, 14), ("Nacional Potosí",        17, 18, 14),
        ("San Antonio Bulo Bulo",  16, 18, 14), ("Independence",           15, 19, 14),
        ("GV San José",            14, 19, 14), ("Royal Pari",             13, 20, 14),
        ("Wilstermann",            13, 20, 14), ("Real Oruro",             12, 22, 13),
        ("Real Tomayapo",          10, 24, 13), ("Aurora",                 12, 22, 13),
        ("Universitario de Vinto", 11, 23, 13), ("Guabirá",                 9, 25, 12),
    ],
    "Venezuela": [
        ("Deportivo La Guaira",      28, 10, 14), ("Caracas FC",             26, 12, 14),
        ("Monagas",                  24, 13, 14), ("Estudiantes de Merida",  22, 15, 14),
        ("Universidad Central",      20, 16, 14), ("Academia Puerto Cabello",18, 17, 14),
        ("Metropolitanos",           16, 18, 14), ("Deportivo Táchira",      15, 19, 14),
        ("Zamora",                   14, 20, 13), ("Mineros de Guayana",     12, 21, 13),
        ("Inter de Barquisimeto",    10, 23, 13), ("Rayo Zuliano",            9, 24, 12),
    ],
}


# ─────────────────────────────────────────────
# EQUIVALENCIAS DE NOMBRES entre fuentes
# Wikipedia / AUF → nombre en HIST_CONMEBOL (que coincide con TheSportsDB)
# Estable durante la temporada — solo cambia entre temporadas
# ─────────────────────────────────────────────
NOMBRES_EQUIV = {
    "Uruguay": {
        # Código AUF → nombre en modelo
        "RAC": "Racing Montevideo", "Racing": "Racing Montevideo",
        "Racing Club": "Racing Montevideo",
        "CDM": "Deportivo Maldonado",
        "ALB": "Albion",
        "PEÑ": "Peñarol", "Peñarol": "Peñarol",
        "CES": "Central Español", "Central": "Central Español",
        "MCT": "Montevideo City Torque", "Torque": "Montevideo City Torque",
        "City Torque": "Montevideo City Torque",
        "NAC": "Nacional", "Nacional": "Nacional",
        "DEF": "Defensor Sporting", "Defensor": "Defensor Sporting",
        "LIV": "Liverpool Montevideo", "Liverpool": "Liverpool Montevideo",
        "WAN": "Montevideo Wanderers", "Wanderers": "Montevideo Wanderers",
        "DAN": "Danubio",
        "CRL": "Cerro Largo",
        "BRI": "Boston River",
        "JUV": "Juventud", "Juventud": "Juventud",
        "PRO": "Progreso",
        "CRR": "Cerro", "Cerro": "Cerro",
        "Miramar Misiones": "Central Español",  # nombre anterior incorrecto
    },
    "Chile": {
        "U. de Chile": "Universidad de Chile",
        "U. Católica": "Universidad Católica",
        "Univ. de Chile": "Universidad de Chile",
        "Univ. Católica": "Universidad Católica",
        "O'Higgins": "O'Higgins",
        "Iquique": "Deportes Iquique",
        "Antofagasta": "Deportes Antofagasta",
        "La Calera": "Unión La Calera",
    },
    "Ecuador": {
        "LDU": "Liga de Quito", "Liga de Quito": "Liga de Quito",
        "IDV": "Independiente del Valle",
        "Barcelona": "Barcelona SC",
        "Técnico": "Técnico Universitario",
        "U. Católica": "Universidad Católica",
    },
    "Paraguay": {
        "Olimpia": "Olimpia",
        "Cerro": "Cerro Porteño",
        "Sol": "Sol de América",
        "Luqueño": "Sportivo Luqueño",
        "Ameliano": "Sportivo Ameliano",
        "Gral. Caballero": "General Caballero JLM",
    },
    "Bolivia": {
        "The Strongest": "The Strongest",
        "Always Ready": "Always Ready",
        "Bolívar": "Bolívar",
        "Oriente": "Oriente Petrolero",
        "San José": "GV San José",
        "Nacional Potosí": "Nacional Potosí",
        "Tomayapo": "Real Tomayapo",
        "Vinto": "Universitario de Vinto",
    },
}

def resolver_nombre(nombre, liga, modelo):
    """
    Resuelve el nombre de un equipo usando el diccionario de equivalencias.
    Si no hay equivalencia, usa el matcher flexible existente.
    """
    equiv = NOMBRES_EQUIV.get(liga, {})
    # Buscar equivalencia directa
    if nombre in equiv:
        nombre_equiv = equiv[nombre]
        if nombre_equiv in modelo:
            return nombre_equiv
    # Búsqueda parcial en equivalencias
    import unicodedata
    def norm(s): return unicodedata.normalize("NFKD",s).encode("ascii","ignore").decode().lower()
    nombre_n = norm(nombre)
    for k, v in equiv.items():
        if norm(k) == nombre_n:
            if v in modelo: return v
    # Fallback al matcher normal
    return nombre if nombre in modelo else None


def fact(n):
    r=1
    for i in range(2,n+1): r*=i
    return r

def pmf(k,lam):
    if lam<=0: return 1.0 if k==0 else 0.0
    return (math.exp(-lam)*(lam**k))/fact(k)

def poisson(ll,lv):
    pl=pe=pv=0.0; M={}
    for gl,gv in iproduct(range(MG+1),repeat=2):
        p=pmf(gl,ll)*pmf(gv,lv); M[(gl,gv)]=p
        if gl>gv: pl+=p
        elif gl==gv: pe+=p
        else: pv+=p
    top=sorted(M.items(),key=lambda x:-x[1])[:5]
    return {"pl":round(pl,4),"pe":round(pe,4),"pv":round(pv,4),
            "top":[{"m":f"{k[0]}-{k[1]}","p":round(v*100,1)} for k,v in top]}

def build_model(partidos, avg):
    eq=set()
    for l,v,_,_ in partidos: eq.add(l);eq.add(v)
    S={e:{"gf":[],"gc":[],"partidos":[]} for e in eq}
    for l,v,gl,gv in partidos:
        S[l]["gf"].append(gl);S[l]["gc"].append(gv)
        S[l]["partidos"].append((l,v,gl,gv))
        S[v]["gf"].append(gv);S[v]["gc"].append(gl)
        S[v]["partidos"].append((l,v,gl,gv))
    modelo = {}
    for e,d in S.items():
        n = max(len(d["gf"]),1)
        gf_avg = sum(d["gf"])/n
        gc_avg = sum(d["gc"])/n
        # Floor mínimo en defensa: ningún equipo tiene GC=0 sostenible
        # Con pocos partidos (≤6), aplicar regresión hacia la media
        if n <= 6:
            gc_avg = (gc_avg * n + avg * 2) / (n + 2)  # Bayesian smoothing hacia avg
        def_coef = max(round(gc_avg/avg, 3), 0.30)  # nunca menor a 0.30
        modelo[e] = {
            "atk":   round(gf_avg/avg, 3),
            "def":   def_coef,
            "n":     len(d["gf"]),
            "gf_avg": round(gf_avg, 2),
            "gc_avg": round(gc_avg, 2),
            "partidos": d["partidos"],
        }
    modelo["_avg"] = avg
    return modelo

def buscar_equipo_info(nombre, M):
    """Retorna info completa del equipo incluyendo partidos para la memoria de calculo."""
    import unicodedata
    def norm(s): return unicodedata.normalize("NFKD",s).encode("ascii","ignore").decode().lower()
    nombre_n = norm(nombre)
    # Buscar equipo en el modelo
    equipo_key = None
    if nombre in M:
        equipo_key = nombre
    else:
        for k in M:
            if norm(k) == nombre_n:
                equipo_key = k; break
        if not equipo_key:
            for k in M:
                if nombre_n.split()[0] in norm(k) or norm(k).split()[0] in nombre_n:
                    equipo_key = k; break
    if not equipo_key:
        return {"atk":1.0,"def":1.0,"n":0,"gf_avg":0,"gc_avg":0,"partidos":[]}
    v = M[equipo_key]
    return {
        "atk": v["atk"],
        "def": v["def"],
        "n": v["n"],
        "gf_avg": round(v.get("gf_avg", v["atk"] * M.get("_avg", 1.20)), 2),
        "gc_avg": round(v.get("gc_avg", v["def"] * M.get("_avg", 1.20)), 2),
        "partidos": v.get("partidos", []),
    }

def lams(loc,vis,M,avg):
    import unicodedata
    def norm(s): return unicodedata.normalize("NFKD",s).encode("ascii","ignore").decode().lower()
    # Aliases conocidos: nombre API → nombre en modelo
    ALIASES = {
        "pumas": "pumas unam", "unam": "pumas unam",
        "tigres": "tigres uanl", "uanl": "tigres uanl",
        "america": "club america", "club america": "club america",
        "chivas": "guadalajara",
        "atletico mineiro": "atletico mineiro", "atletico-mg": "atletico mineiro",
        "atletico paranaense": "athletico paranaense", "athletico-pr": "athletico paranaense",
        "red bull bragantino": "red bull bragantino", "bragantino": "red bull bragantino",
        "estudiantes": "estudiantes (lp)", "estudiantes lp": "estudiantes (lp)",
        "racing club": "racing", "racing de avellaneda": "racing",
        "belgrano": "belgrano", "belgrano cordoba": "belgrano",
        "san martin": "san martin (t)",
    }
    def buscar(nombre):
        if nombre in M: return M[nombre]
        nombre_n = norm(nombre)
        # Chequear aliases
        for alias, target in ALIASES.items():
            if alias in nombre_n:
                target_n = norm(target)
                for k,v in M.items():
                    if k == "_avg": continue
                    if norm(k) == target_n: return v
        # Exacto normalizado
        for k,v in M.items():
            if k == "_avg": continue
            if norm(k) == nombre_n: return v
        # Quitar sufijos de ciudad "de Córdoba", "de Buenos Aires", etc.
        nombre_base = nombre_n.split(" de ")[0].split(" fc")[0].strip()
        for k,v in M.items():
            if k == "_avg": continue
            k_n = norm(k)
            k_base = k_n.split(" de ")[0].strip()
            if nombre_base == k_base: return v
        # Parcial por primera palabra
        primera = nombre_base.split()[0] if nombre_base.split() else nombre_base
        for k,v in M.items():
            if k == "_avg": continue
            k_n = norm(k)
            if primera in k_n or k_n.split()[0] in nombre_base: return v
        return {"atk":1.0,"def":1.0}
    ml=buscar(loc); mv=buscar(vis)
    return round(ml["atk"]*mv["def"]*avg*FL,3), round(mv["atk"]*ml["def"]*avg,3)

def impl(cuotas):
    raw={k:1/v for k,v in cuotas.items() if v>1}
    t=sum(raw.values())
    if t==0: return {"p":{},"vig":0}
    return {"p":{k:round(v/t,4) for k,v in raw.items()},"vig":round((t-1)*100,2)}

def kelly_calc(p,cuota,frac,bank,umbral):
    b=cuota-1;q=1-p;fc=(p*b-q)/b
    fu=fc*frac if fc>0 else 0
    s=round(bank*fu)
    return {"ku":round(fu*100,2),"s":s,"r":round(s*cuota),"g":round(s*cuota-s),
            "ev":round(p*b-q,4),"value":fc>umbral,"edge":round((p-1/cuota)*100,2)}


# ─────────────────────────────────────────────
# THE ODDS API — cuotas automaticas
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def get_cuotas_automaticas(odds_key, odds_api_key):
    if not odds_key or not odds_api_key:
        return {}
    url = f"{API_ODDS}/sports/{odds_key}/odds/"
    params = {"apiKey":odds_api_key,"regions":"eu","markets":"h2h","oddsFormat":"decimal"}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        cuotas_map = {}
        for p in r.json():
            home = p.get("home_team","")
            away = p.get("away_team","")
            totales = {"home":[],"draw":[],"away":[]}
            for bm in p.get("bookmakers",[]):
                for mkt in bm.get("markets",[]):
                    if mkt["key"] != "h2h": continue
                    for o in mkt.get("outcomes",[]):
                        if o["name"] == home:       totales["home"].append(o["price"])
                        elif o["name"] == "Draw":   totales["draw"].append(o["price"])
                        elif o["name"] == away:     totales["away"].append(o["price"])
            if totales["home"] and totales["draw"] and totales["away"]:
                avg = lambda lst: round(sum(lst)/len(lst),2)
                cuotas_map[f"{home}|{away}"] = {
                    "local":  avg(totales["home"]),
                    "empate": avg(totales["draw"]),
                    "visit":  avg(totales["away"]),
                    "n_casas": len(totales["home"]),
                }
        return cuotas_map
    except:
        return {}

def buscar_cuotas(local, visit, cuotas_map):
    key = f"{local}|{visit}"
    if key in cuotas_map:
        return cuotas_map[key]
    for k, v in cuotas_map.items():
        h, a = k.split("|")
        if (local.split()[0].lower() in h.lower() or h.split()[0].lower() in local.lower()) and            (visit.split()[0].lower() in a.lower() or a.split()[0].lower() in visit.lower()):
            return v
    return None

# ─────────────────────────────────────────────
# TheSportsDB — API gratuita (key=123), resultados partido a partido
# Documentación: https://www.thesportsdb.com/documentation
# Liga Argentina id=4406 · Brasileirao id=4351 · Liga MX id=4350
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def sportsdb_hist(league_id, season="2026"):
    """
    Obtiene resultados partido a partido desde TheSportsDB (gratuito, sin registro).
    Retorna lista de (local, visitante, goles_local, goles_visit) como build_model espera.
    """
    url = f"https://www.thesportsdb.com/api/v1/json/123/eventsseason.php?id={league_id}&s={season}"
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        data = r.json()
        eventos = data.get("events") or []
        partidos = []
        for e in eventos:
            gl = e.get("intHomeScore")
            gv = e.get("intAwayScore")
            loc = e.get("strHomeTeam","").strip()
            vis = e.get("strAwayTeam","").strip()
            if gl is None or gv is None: continue  # partido no jugado aún
            if not loc or not vis: continue
            try:
                partidos.append((loc, vis, int(gl), int(gv)))
            except (ValueError, TypeError):
                continue
        return partidos, None
    except Exception as ex:
        return [], str(ex)

# ─────────────────────────────────────────────
# API — football-data.org
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fd_hist(code, key):
    try:
        r=requests.get(f"{API_FD}/competitions/{code}/matches?status=FINISHED",
                       headers={"X-Auth-Token":key},timeout=10)
        r.raise_for_status()
        out=[]
        for m in r.json().get("matches",[]):
            s=m.get("score",{}).get("fullTime",{})
            if s.get("home") is None: continue
            out.append((m["homeTeam"]["name"],m["awayTeam"]["name"],s["home"],s["away"]))
        return out,None
    except Exception as e: return [],str(e)

@st.cache_data(ttl=900)
def fd_next(code, key):
    try:
        r=requests.get(f"{API_FD}/competitions/{code}/matches?status=SCHEDULED,TIMED",
                       headers={"X-Auth-Token":key},timeout=10)
        r.raise_for_status()
        out=[]
        for m in r.json().get("matches",[]):
            dt=to_col(m["utcDate"])
            if dt is None: continue
            out.append({"id":m["id"],"dt":dt,"fecha":dt.strftime("%Y-%m-%d"),
                        "hora":dt.strftime("%I:%M %p"),"local":m["homeTeam"]["name"],
                        "visit":m["awayTeam"]["name"],"jornada":m.get("matchday","?"),
                        "hoy":es_hoy(dt),"manana":es_manana(dt)})
        out.sort(key=lambda x:x["dt"])
        lim=(datetime.datetime.now(TZ_COL)+datetime.timedelta(days=3)).date()
        return [p for p in out if p["dt"].date()<=lim],None
    except Exception as e: return [],str(e)

# ─────────────────────────────────────────────
# SCRAPER WIKIPEDIA — Suramérica (sin API key)
# ─────────────────────────────────────────────
from bs4 import BeautifulSoup


@st.cache_data(ttl=900)
def odds_fixtures(odds_key, odds_api_key):
    """Obtiene proximos partidos con hora real desde The Odds API."""
    url = f"{API_ODDS}/sports/{odds_key}/odds/"
    params = {"apiKey":odds_api_key,"regions":"eu","markets":"h2h","oddsFormat":"decimal"}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        out = []
        ahora = datetime.datetime.now(TZ_COL)
        lim = (ahora + datetime.timedelta(days=7)).date()
        import hashlib
        for p in r.json():
            dt_utc = datetime.datetime.fromisoformat(p["commence_time"].replace("Z","+00:00"))
            dt = dt_utc.astimezone(TZ_COL)
            if dt < ahora or dt.date() > lim: continue
            uid = hashlib.md5(f"{p['home_team']}{p['away_team']}".encode()).hexdigest()[:8]
            out.append({"id":uid,"dt":dt,
                        "fecha":dt.strftime("%Y-%m-%d"),"hora":dt.strftime("%I:%M %p"),
                        "local":p["home_team"],"visit":p["away_team"],
                        "jornada":"Final","hoy":es_hoy(dt),"manana":es_manana(dt)})
        out.sort(key=lambda x:x["dt"])
        return out, None
    except Exception as ex:
        return [], str(ex)


@st.cache_data(ttl=60)
def wiki_tabla_hist(wiki_url, avg):
    """
    Extrae modelo desde la tabla de posiciones de Wikipedia.
    Busca columnas: Equipo, PJ, GF, GC — funciona para cualquier liga con tabla estándar.
    Dinámico: se actualiza solo cuando Wikipedia actualiza la tabla (ttl=1h).
    """
    import re
    headers_req = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(wiki_url, headers=headers_req, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        equipos = []
        for tabla in soup.find_all("table", class_=re.compile("wikitable")):
            filas = tabla.find_all("tr")
            if len(filas) < 3: continue
            cabecera = [th.get_text(strip=True).upper() for th in filas[0].find_all(["th","td"])]
            def idx(opciones):
                for op in opciones:
                    for i,c in enumerate(cabecera):
                        if op in c: return i
                return None
            i_eq = idx(["TEAM","CLUB","EQUIPO"])
            i_pj = idx(["PLD","PJ","MP","PLAYED"])
            i_gf = idx(["GF","GS","FOR"])
            i_gc = idx(["GA","GC","AGAINST"])
            if any(x is None for x in [i_eq, i_pj, i_gf, i_gc]): continue
            for fila in filas[1:]:
                celdas = fila.find_all(["td","th"])
                if len(celdas) <= max(i_eq, i_pj, i_gf, i_gc): continue
                try:
                    equipo = celdas[i_eq].get_text(strip=True)
                    pj = int(re.sub(r'\D','', celdas[i_pj].get_text(strip=True)) or 0)
                    gf = int(re.sub(r'\D','', celdas[i_gf].get_text(strip=True)) or 0)
                    gc = int(re.sub(r'\D','', celdas[i_gc].get_text(strip=True)) or 0)
                    if pj > 0 and len(equipo) > 2:
                        equipos.append((equipo, gf, gc, pj))
                except: continue
            if len(equipos) >= 5: break
        if not equipos:
            return [], "No se encontró tabla de posiciones en Wikipedia"
        return build_model_desde_tabla(equipos, avg), None
    except Exception as ex:
        return [], str(ex)

@st.cache_data(ttl=1800)
def sportsdb_next(league_id, season="2026"):
    """
    Obtiene próximos partidos desde TheSportsDB usando eventsday por fecha.
    Fallback a eventsnextleague si eventsday no retorna resultados.
    """
    TZ_COL = ZoneInfo("America/Bogota")
    ahora = datetime.datetime.now(TZ_COL)
    proximos = []
    vistos = set()
    import hashlib

    for dias in range(5):
        fecha = (ahora + datetime.timedelta(days=dias)).strftime("%Y-%m-%d")
        url = f"https://www.thesportsdb.com/api/v1/json/123/eventsday.php?d={fecha}&l={league_id}"
        try:
            r = requests.get(url, timeout=10)
            if r.status_code != 200: continue
            data = r.json()
            for e in (data.get("events") or []):
                gl = e.get("intHomeScore")
                gv = e.get("intAwayScore")
                if gl is not None and gv is not None: continue
                loc = e.get("strHomeTeam","").strip()
                vis = e.get("strAwayTeam","").strip()
                if not loc or not vis: continue
                uid_raw = f"{loc}{vis}{fecha}"
                if uid_raw in vistos: continue
                vistos.add(uid_raw)
                hora_str = e.get("strTime","00:00:00") or "00:00:00"
                try:
                    dt = datetime.datetime.strptime(f"{fecha} {hora_str[:5]}", "%Y-%m-%d %H:%M")
                    dt = dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(TZ_COL)
                except:
                    dt = datetime.datetime.strptime(fecha, "%Y-%m-%d").replace(tzinfo=TZ_COL)
                dias_diff = (dt.date() - ahora.date()).days
                proximos.append({
                    "id": hashlib.md5(uid_raw.encode()).hexdigest()[:8],
                    "dt": dt, "fecha": fecha,
                    "hora": dt.strftime("%I:%M %p"),
                    "local": loc, "visit": vis,
                    "jornada": e.get("intRound",""),
                    "hoy": dias_diff == 0,
                    "manana": dias_diff == 1,
                })
        except: continue

    # Fallback a eventsnextleague si no hay resultados
    if not proximos:
        try:
            url = f"https://www.thesportsdb.com/api/v1/json/123/eventsnextleague.php?id={league_id}"
            r = requests.get(url, timeout=10)
            data = r.json()
            for e in (data.get("events") or []):
                gl = e.get("intHomeScore")
                gv = e.get("intAwayScore")
                if gl is not None and gv is not None: continue
                loc = e.get("strHomeTeam","").strip()
                vis = e.get("strAwayTeam","").strip()
                if not loc or not vis: continue
                fecha_str = e.get("dateEvent","")
                hora_str  = e.get("strTime","00:00:00") or "00:00:00"
                try:
                    dt = datetime.datetime.strptime(f"{fecha_str} {hora_str[:5]}", "%Y-%m-%d %H:%M")
                    dt = dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(TZ_COL)
                except:
                    continue
                dias_diff = (dt.date() - ahora.date()).days
                if dias_diff < 0 or dias_diff > 4: continue
                uid_raw = f"{loc}{vis}{fecha_str}"
                proximos.append({
                    "id": hashlib.md5(uid_raw.encode()).hexdigest()[:8],
                    "dt": dt, "fecha": fecha_str,
                    "hora": dt.strftime("%I:%M %p"),
                    "local": loc, "visit": vis,
                    "jornada": e.get("intRound",""),
                    "hoy": dias_diff == 0,
                    "manana": dias_diff == 1,
                })
        except: pass

    proximos.sort(key=lambda x: x["dt"])
    return proximos, None

@st.cache_data(ttl=1800)
def apifootball_next(league_id, season, api_key):
    """
    Obtiene próximos partidos desde API-Football.
    Usa búsqueda por fecha para evitar restricción de temporada en plan gratuito.
    """
    TZ_COL = ZoneInfo("America/Bogota")
    ahora = datetime.datetime.now(TZ_COL)
    headers = {"x-apisports-key": api_key}
    proximos = []
    vistos = set()
    import hashlib

    for dias in range(5):
        fecha = (ahora + datetime.timedelta(days=dias)).strftime("%Y-%m-%d")
        url = "https://v3.football.api-sports.io/fixtures"
        params = {
            "league": league_id,
            "date": fecha,
            "timezone": "America/Bogota",
        }
        try:
            r = requests.get(url, headers=headers, params=params, timeout=15)
            r.raise_for_status()
            data = r.json()
            errs = data.get("errors", {})
            if errs and errs != []:
                return [], str(errs)
            for f in data.get("response", []):
                fixture = f.get("fixture", {})
                teams   = f.get("teams", {})
                status  = fixture.get("status", {}).get("short","")
                if status not in ("NS", "TBD"): continue  # solo no iniciados
                loc = teams.get("home", {}).get("name", "")
                vis = teams.get("away", {}).get("name", "")
                if not loc or not vis: continue
                uid_raw = f"{loc}{vis}{fecha}"
                if uid_raw in vistos: continue
                vistos.add(uid_raw)
                try:
                    dt = datetime.datetime.fromisoformat(
                        fixture.get("date","").replace("Z","+00:00")
                    ).astimezone(TZ_COL)
                except:
                    dt = datetime.datetime.strptime(fecha, "%Y-%m-%d").replace(tzinfo=TZ_COL)
                dias_diff = (dt.date() - ahora.date()).days
                proximos.append({
                    "id": hashlib.md5(uid_raw.encode()).hexdigest()[:8],
                    "dt": dt, "fecha": fecha,
                    "hora": dt.strftime("%I:%M %p"),
                    "local": loc, "visit": vis,
                    "jornada": f.get("league",{}).get("round",""),
                    "hoy": dias_diff == 0,
                    "manana": dias_diff == 1,
                })
        except Exception as ex:
            return proximos, str(ex)

    proximos.sort(key=lambda x: x["dt"])
    return proximos, None


    """
    Obtiene próximos partidos desde TheSportsDB buscando por los próximos 4 días.
    Usa eventsday.php para capturar todas las jornadas completas.
    """
    TZ_COL = ZoneInfo("America/Bogota")
    ahora = datetime.datetime.now(TZ_COL)
    proximos = []
    vistos = set()

    for dias in range(5):  # hoy + 4 días
        fecha = (ahora + datetime.timedelta(days=dias)).strftime("%Y-%m-%d")
        url = f"https://www.thesportsdb.com/api/v1/json/123/eventsday.php?d={fecha}&l={league_id}"
        try:
            r = requests.get(url, timeout=10)
            if r.status_code != 200: continue
            data = r.json()
            eventos = data.get("events") or []
            for e in eventos:
                fecha_str = e.get("dateEvent","")
                hora_str  = e.get("strTime","00:00:00") or "00:00:00"
                gl = e.get("intHomeScore")
                gv = e.get("intAwayScore")
                if gl is not None and gv is not None: continue  # ya jugado
                loc = e.get("strHomeTeam","").strip()
                vis = e.get("strAwayTeam","").strip()
                if not loc or not vis: continue
                uid = f"{loc}{vis}{fecha_str}"
                if uid in vistos: continue
                vistos.add(uid)
                try:
                    dt = datetime.datetime.strptime(f"{fecha_str} {hora_str[:5]}", "%Y-%m-%d %H:%M")
                    dt = dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(TZ_COL)
                except:
                    dt = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").replace(tzinfo=TZ_COL)
                dias_diff = (dt.date() - ahora.date()).days
                import hashlib
                uid_hash = hashlib.md5(uid.encode()).hexdigest()[:8]
                proximos.append({
                    "id": uid_hash, "dt": dt,
                    "fecha": fecha_str,
                    "hora": dt.strftime("%I:%M %p"),
                    "local": loc, "visit": vis,
                    "jornada": e.get("intRound",""),
                    "hoy": dias_diff == 0,
                    "manana": dias_diff == 1,
                })
        except: continue

    # Si eventsday no retornó nada, fallback a eventsnextleague
    if not proximos:
        try:
            url = f"https://www.thesportsdb.com/api/v1/json/123/eventsnextleague.php?id={league_id}"
            r = requests.get(url, timeout=10)
            data = r.json()
            eventos = data.get("events") or []
            for e in eventos:
                fecha_str = e.get("dateEvent","")
                hora_str  = e.get("strTime","00:00:00") or "00:00:00"
                gl = e.get("intHomeScore")
                gv = e.get("intAwayScore")
                if gl is not None and gv is not None: continue
                loc = e.get("strHomeTeam","").strip()
                vis = e.get("strAwayTeam","").strip()
                if not loc or not vis: continue
                try:
                    dt = datetime.datetime.strptime(f"{fecha_str} {hora_str[:5]}", "%Y-%m-%d %H:%M")
                    dt = dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(TZ_COL)
                except:
                    dt = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").replace(tzinfo=TZ_COL)
                dias_diff = (dt.date() - ahora.date()).days
                if dias_diff < 0 or dias_diff > 4: continue
                import hashlib
                uid_hash = hashlib.md5(f"{loc}{vis}{fecha_str}".encode()).hexdigest()[:8]
                proximos.append({
                    "id": uid_hash, "dt": dt,
                    "fecha": fecha_str,
                    "hora": dt.strftime("%I:%M %p"),
                    "local": loc, "visit": vis,
                    "jornada": e.get("intRound",""),
                    "hoy": dias_diff == 0,
                    "manana": dias_diff == 1,
                })
        except: pass

    proximos.sort(key=lambda x: x["dt"])
    return proximos, None


    """Extrae historial combinando multiples paginas de Wikipedia."""
    import re
    headers_req = {"User-Agent": "Mozilla/5.0"}
    excluir = equipos_excluir or []
    partidos = []
    for url in wiki_urls:
        try:
            r = requests.get(url, headers=headers_req, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")
            for tabla in soup.find_all("table", class_="wikitable"):
                for fila in tabla.find_all("tr"):
                    celdas = [td.get_text(strip=True) for td in fila.find_all(["td","th"])]
                    if wiki_fmt == "uel":
                        # Formato Wikipedia ingles: buscar X-Y entre equipos
                        for i, celda in enumerate(celdas):
                            m = re.search(r"^(\d+)\s*[–\-]\s*(\d+)$", celda.strip())
                            if m and i > 0 and i < len(celdas)-1:
                                loc = celdas[i-1].strip()
                                vis = celdas[i+1].strip()
                                if len(loc)>2 and len(vis)>2:
                                    if not any(e in loc or e in vis for e in excluir):
                                        partidos.append((loc, vis, int(m.group(1)), int(m.group(2))))
                    elif wiki_fmt == "conmebol":
                        if len(celdas)<5: continue
                        m = re.search(r"(\d+)\s*[:\-]\s*(\d+)", celdas[3])
                        if not m: continue
                        loc, vis = celdas[2].strip(), celdas[4].strip()
                        if loc and vis and len(loc)>2 and len(vis)>2:
                            if not any(e in loc or e in vis for e in excluir):
                                partidos.append((loc, vis, int(m.group(1)), int(m.group(2))))
                    else:
                        if len(celdas)<3: continue
                        m = re.search(r"(\d+)\s*:\s*(\d+)", " ".join(celdas))
                        if not m: continue
                        loc, vis = celdas[0].strip(), celdas[2].strip()
                        if loc and vis and len(loc)>2 and len(vis)>2:
                            if not any(e in loc or e in vis for e in excluir):
                                partidos.append((loc, vis, int(m.group(1)), int(m.group(2))))
        except:
            continue
    return partidos, None

@st.cache_data(ttl=3600)
def wiki_hist(wiki_url, wiki_fmt, equipos_excluir=None):
    """Extrae historial de resultados desde Wikipedia."""
    headers={"User-Agent":"Mozilla/5.0"}
    try:
        r=requests.get(wiki_url,headers=headers,timeout=15)
        soup=BeautifulSoup(r.text,"html.parser")
        partidos=[]
        import re
        for tabla in soup.find_all("table",class_="wikitable"):
            for fila in tabla.find_all("tr"):
                celdas=[td.get_text(strip=True) for td in fila.find_all(["td","th"])]
                if wiki_fmt=="conmebol":
                    if len(celdas)<5: continue
                    m=re.search(r"(\d+)\s*[:\-]\s*(\d+)",celdas[3])
                    if not m: continue
                    loc,vis=celdas[2].strip(),celdas[4].strip()
                else:
                    if len(celdas)<3: continue
                    m=re.search(r"(\d+)\s*:\s*(\d+)"," ".join(celdas))
                    if not m: continue
                    loc,vis=celdas[0].strip(),celdas[2].strip()
                if loc and vis and len(loc)>2 and len(vis)>2:
                    partidos.append((loc,vis,int(m.group(1)),int(m.group(2))))
        return partidos,None
    except Exception as ex: return [],str(ex)

@st.cache_data(ttl=900)
def wiki_next(wiki_url, wiki_fmt, equipos_excluir=None):
    """Extrae proximos partidos desde Wikipedia con fechas reales."""
    MESES = {"enero":1,"febrero":2,"marzo":3,"abril":4,"mayo":5,"junio":6,
             "julio":7,"agosto":8,"septiembre":9,"octubre":10,"noviembre":11,"diciembre":12}
    headers_req={"User-Agent":"Mozilla/5.0"}
    try:
        import re, hashlib
        r=requests.get(wiki_url,headers=headers_req,timeout=15)
        soup=BeautifulSoup(r.text,"html.parser")
        out=[]; ahora=datetime.datetime.now(TZ_COL)
        lim=(ahora+datetime.timedelta(days=7)).date()
        anio=ahora.year
        for tabla in soup.find_all("table",class_="wikitable"):
            for fila in tabla.find_all("tr"):
                celdas=[td.get_text(strip=True) for td in fila.find_all(["td","th"])]
                if wiki_fmt=="conmebol":
                    if len(celdas)<5: continue
                    if celdas[3].strip() != "-": continue
                    loc,vis,fecha_str=celdas[2].strip(),celdas[4].strip(),celdas[0].strip()
                else:
                    if len(celdas)<3: continue
                    m=re.search(r"(\d+)\s*:\s*(\d+)"," ".join(celdas))
                    if m: continue  # ya jugado
                    loc,vis=celdas[0].strip(),celdas[2].strip()
                    fecha_str=celdas[3] if len(celdas)>3 else ""
                    import unicodedata
                    def norm(s): return unicodedata.normalize("NFKD",s).encode("ascii","ignore").decode().lower()
                    # Filtro de equipos colombianos solo si la URL es de Colombia
                    es_colombia = "colombia" in wiki_url.lower() or "betplay" in wiki_url.lower() or "torneo_apertura" in wiki_url.lower() or "primera_b" in wiki_url.lower()
                    if es_colombia:
                        EQUIPOS_NORM = ["nacional","santa fe","millonarios","junior",
                                        "america","tolima","bucaramanga","pereira",
                                        "once caldas","pasto","deportivo cali","medellin",
                                        "jaguares","cucuta","boyaca","aguilas",
                                        "fortaleza","alianza","internacional","llaneros"]
                        loc_n,vis_n=norm(loc),norm(vis)
                        if not any(e in loc_n for e in EQUIPOS_NORM): continue
                        if not any(e in vis_n for e in EQUIPOS_NORM): continue
                        CIUDADES = ["medellin","bogota","cali","barranquilla","bucaramanga",
                                    "manizales","armenia","pereira","pasto","ibague",
                                    "monteria","cucuta","tunja","valledupar","villavicencio"]
                        loc_n,vis_n=norm(loc),norm(vis)
                        if vis_n.strip() in CIUDADES: continue
                        if loc_n.strip() in CIUDADES: continue
                        palabras_loc = set(loc_n.split())
                        palabras_vis = set(vis_n.split())
                        if palabras_loc.issubset(palabras_vis) or palabras_vis.issubset(palabras_loc): continue
                    else:
                        # Para Brasileirao, Argentina, Mexico, etc: filtro genérico mínimo
                        loc_n,vis_n=norm(loc),norm(vis)
                        if len(loc)<3 or len(vis)<3: continue
                        # Evitar filas de encabezado o datos no-equipo
                        if loc_n in ["local","home","equipo","club","team"]: continue
                if not loc or not vis or len(loc)<3: continue

                # Parsear fecha tipo "19 de mayo"
                dt=None
                m_fecha=re.search(r"(\d+)\s+de\s+(\w+)",fecha_str.lower())
                if m_fecha:
                    dia=int(m_fecha.group(1))
                    mes=MESES.get(m_fecha.group(2))
                    if mes:
                        try:
                            dt=datetime.datetime(anio,mes,dia,12,0,tzinfo=TZ_COL)
                        except: dt=None
                if dt is None:
                    dt=ahora
                if dt.date()>lim: continue
                uid=hashlib.md5(f"{loc}{vis}{dt.date()}".encode()).hexdigest()[:8]
                out.append({"id":uid,"dt":dt,
                            "fecha":dt.strftime("%Y-%m-%d"),"hora":"Ver en RushBet",
                            "local":loc,"visit":vis,"jornada":"?",
                            "hoy":es_hoy(dt),"manana":es_manana(dt)})
        out.sort(key=lambda x:x["dt"])
        # Deduplicar
        seen=set(); final=[]
        for p in out:
            k=f"{p['local']}{p['visit']}"
            if k not in seen: seen.add(k); final.append(p)
        return final,None
    except Exception as ex: return [],str(ex)

def rf_hist(league_id, rf_key):
    """Historial de partidos via API-Football."""
    season=datetime.datetime.now(TZ_COL).year
    url=f"{API_RF}/fixtures?league={league_id}&season={season}&status=FT"
    headers={"x-apisports-key":rf_key}
    try:
        r=requests.get(url,headers=headers,timeout=15)
        r.raise_for_status()
        out=[]
        for m in r.json().get("response",[]):
            h=m["teams"]["home"]["name"]; a=m["teams"]["away"]["name"]
            gh=m["goals"]["home"];       ga=m["goals"]["away"]
            if gh is None or ga is None: continue
            out.append((h,a,gh,ga))
        return out,None
    except Exception as e: return [],str(e)

@st.cache_data(ttl=900)
def rf_next(league_id, rf_key):
    """Próximos partidos via API-Football."""
    season=datetime.datetime.now(TZ_COL).year
    url=f"{API_RF}/fixtures?league={league_id}&season={season}&status=NS"
    headers={"x-apisports-key":rf_key}
    try:
        r=requests.get(url,headers=headers,timeout=15)
        r.raise_for_status()
        out=[]
        for m in r.json().get("response",[]):
            raw=m["fixture"]["date"]
            dt=to_col(raw)
            if dt is None: continue
            out.append({"id":m["fixture"]["id"],"dt":dt,
                        "fecha":dt.strftime("%Y-%m-%d"),"hora":dt.strftime("%I:%M %p"),
                        "local":m["teams"]["home"]["name"],"visit":m["teams"]["away"]["name"],
                        "jornada":m.get("league",{}).get("round","?"),
                        "hoy":es_hoy(dt),"manana":es_manana(dt)})
        out.sort(key=lambda x:x["dt"])
        lim=(datetime.datetime.now(TZ_COL)+datetime.timedelta(days=3)).date()
        return [p for p in out if p["dt"].date()<=lim],None
    except Exception as e: return [],str(e)


# ─────────────────────────────────────────────
# MÓDULO AMISTOSOS — Elo selecciones + Poisson + API-Football
# ─────────────────────────────────────────────

@st.cache_data(ttl=3600)
def cargar_elo_selecciones():
    """
    Carga ratings Elo de selecciones desde eloratings.net.
    Retorna dict: {nombre_seleccion: elo_rating}
    """
    import re
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get("http://www.eloratings.net/World.tsv", headers=headers, timeout=15)
        if r.status_code == 200 and "\t" in r.text:
            elo = {}
            for linea in r.text.strip().split("\n"):
                partes = linea.strip().split("\t")
                if len(partes) >= 3:
                    nombre = partes[1].strip()
                    try:
                        rating = int(partes[2].strip())
                        elo[nombre] = rating
                    except: continue
            if len(elo) > 50:
                return elo, None
    except: pass

    # Fallback: ratings hardcodeados actualizados al 3-junio-2026
    # Fuente: eloratings.net top 50 + selecciones relevantes
    ELO_2026 = {
        "Spain": 2171, "Argentina": 2113, "France": 2063, "England": 2042,
        "Colombia": 1998, "Brazil": 1979, "Portugal": 1976, "Netherlands": 1959,
        "Croatia": 1933, "Ecuador": 1933, "Norway": 1922, "Germany": 1910,
        "Switzerland": 1897, "Uruguay": 1890, "Turkey": 1880, "Japan": 1879,
        "Senegal": 1869, "Denmark": 1864, "Italy": 1859, "Belgium": 1849,
        "Morocco": 1845, "Mexico": 1832, "USA": 1821, "Australia": 1812,
        "Serbia": 1808, "Poland": 1803, "Ukraine": 1798, "Austria": 1795,
        "South Korea": 1789, "Ghana": 1776, "Ivory Coast": 1771, "Nigeria": 1768,
        "Hungary": 1754, "Czech Republic": 1748, "Romania": 1742, "Algeria": 1738,
        "Chile": 1731, "Peru": 1724, "Venezuela": 1718, "Paraguay": 1712,
        "Costa Rica": 1706, "Panama": 1699, "Jamaica": 1688, "Bolivia": 1672,
        "Georgia": 1668, "Albania": 1652, "Israel": 1641, "Scotland": 1638,
        "Wales": 1629, "Finland": 1618, "Slovakia": 1612, "Greece": 1608,
        "Slovenia": 1598, "Montenegro": 1587, "North Macedonia": 1576,
        "Bosnia": 1571, "Sweden": 1565, "Ireland": 1558, "Northern Ireland": 1547,
        "Cyprus": 1489, "Luxembourg": 1467, "Haiti": 1458, "New Zealand": 1441,
        "DR Congo": 1438, "Congo DR": 1438, "Senegal": 1869,
        "Uzbekistan": 1412, "Iran": 1428, "Iraq": 1398, "Saudi Arabia": 1389,
        "Pakistan": 1102, "Bangladesh": 1089,
        "Gibraltar": 902, "British Virgin Islands": 847,
        "Azerbaijan": 1382, "Armenia": 1398, "Belarus": 1412,
        "Moldova": 1321, "Kosovo": 1489, "Estonia": 1398,
        "Latvia": 1412, "Lithuania": 1387, "Faroe Islands": 1356,
        "Malta": 1298, "Andorra": 1089, "Liechtenstein": 1023,
        "San Marino": 876, "Montenegro": 1521, "Slovakia": 1598,
        "North Macedonia": 1534, "Bosnia": 1571,
        "Bahrain": 1312, "Saudi Arabia": 1389, "Jordan": 1356,
        "UAE": 1334, "Kuwait": 1289, "Oman": 1298,
        "Egypt": 1612, "Tunisia": 1589, "Algeria": 1738,
        "Morocco": 1845, "Senegal": 1869, "Ivory Coast": 1771,
        "Ghana": 1776, "Nigeria": 1768, "Cameroon": 1698,
        "DR Congo": 1438, "Congo DR": 1438,
        "Zambia": 1398, "Zimbabwe": 1312, "Kenya": 1298,
        "Haiti": 1458, "Jamaica": 1521, "Panama": 1612,
        "Costa Rica": 1638, "Honduras": 1489, "El Salvador": 1423,
        "Guatemala": 1398, "Cuba": 1312, "Trinidad and Tobago": 1445,
        "Peru": 1698, "Bolivia": 1612, "Ecuador": 1798,
        "Venezuela": 1634, "Paraguay": 1656,
        "New Zealand": 1441, "Australia": 1756,
        "Japan": 1834, "South Korea": 1756, "Iran": 1698,
        "Uzbekistan": 1534, "Saudi Arabia": 1456,
    }
    return ELO_2026, "Usando ratings fallback (eloratings.net no disponible)"

def prob_elo_selecciones(elo_local, elo_visit, es_neutral=True):
    """
    Calcula probabilidades usando Elo de selecciones.
    Incluye ventaja de local si no es cancha neutral.
    Retorna (p_local, p_empate, p_visit)
    """
    ventaja_local = 0 if es_neutral else 100
    diff = elo_local - elo_visit + ventaja_local
    # Probabilidad de no perder (win + draw) para local
    p_no_pierde = 1 / (1 + 10 ** (-diff / 400))
    # Distribución aproximada usando método de Maher/Dixon-Coles
    # p_empate es función del diff — menor diferencia = más empates
    p_empate = max(0.22 - abs(diff) * 0.0003, 0.08)
    p_local = p_no_pierde * (1 - p_empate)
    p_visit = (1 - p_no_pierde) * (1 - p_empate)
    # Normalizar
    total = p_local + p_empate + p_visit
    return round(p_local/total, 4), round(p_empate/total, 4), round(p_visit/total, 4)

@st.cache_data(ttl=1800)
def get_amistosos_hoy(api_key, dias=3):
    """
    Obtiene amistosos internacionales desde TheSportsDB (gratuito).
    League ID 4562 = International Friendlies, temporada 2026.
    API-Football como fallback si TheSportsDB falla.
    """
    TZ_COL = ZoneInfo("America/Bogota")
    ahora = datetime.datetime.now(TZ_COL)
    partidos = []
    vistos = set()
    import hashlib

    # Intentar TheSportsDB primero — gratuito y sin restricciones
    for d in range(dias + 1):
        fecha = (ahora + datetime.timedelta(days=d)).strftime("%Y-%m-%d")
        url = f"https://www.thesportsdb.com/api/v1/json/123/eventsday.php?d={fecha}&l=4562"
        try:
            r = requests.get(url, timeout=10)
            if r.status_code != 200: continue
            data = r.json()
            for e in (data.get("events") or []):
                gl = e.get("intHomeScore")
                gv = e.get("intAwayScore")
                loc = e.get("strHomeTeam","").strip()
                vis = e.get("strAwayTeam","").strip()
                if not loc or not vis: continue
                uid_raw = f"{loc}{vis}{fecha}"
                if uid_raw in vistos: continue
                vistos.add(uid_raw)
                ya_jugado = gl is not None and gv is not None
                hora_str = e.get("strTime","00:00:00") or "00:00:00"
                try:
                    dt = datetime.datetime.strptime(f"{fecha} {hora_str[:5]}", "%Y-%m-%d %H:%M")
                    dt = dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(TZ_COL)
                except:
                    dt = datetime.datetime.strptime(fecha, "%Y-%m-%d").replace(tzinfo=TZ_COL)
                dias_diff = (dt.date() - ahora.date()).days
                partidos.append({
                    "id": hashlib.md5(uid_raw.encode()).hexdigest()[:8],
                    "dt": dt, "fecha": fecha,
                    "hora": dt.strftime("%I:%M %p"),
                    "local": loc, "visit": vis,
                    "ya_jugado": ya_jugado,
                    "gol_loc": int(gl) if ya_jugado else None,
                    "gol_vis": int(gv) if ya_jugado else None,
                    "hoy": dias_diff == 0,
                    "manana": dias_diff == 1,
                    "venue": e.get("strVenue",""),
                    "city": e.get("strCity",""),
                    "liga": "International Friendlies",
                })
        except: continue

    # Fallback: eventsnextleague de TheSportsDB
    if not partidos:
        try:
            url = "https://www.thesportsdb.com/api/v1/json/123/eventsnextleague.php?id=4562"
            r = requests.get(url, timeout=10)
            data = r.json()
            for e in (data.get("events") or []):
                loc = e.get("strHomeTeam","").strip()
                vis = e.get("strAwayTeam","").strip()
                fecha_str = e.get("dateEvent","")
                hora_str = e.get("strTime","00:00:00") or "00:00:00"
                if not loc or not vis or not fecha_str: continue
                uid_raw = f"{loc}{vis}{fecha_str}"
                if uid_raw in vistos: continue
                vistos.add(uid_raw)
                try:
                    dt = datetime.datetime.strptime(f"{fecha_str} {hora_str[:5]}", "%Y-%m-%d %H:%M")
                    dt = dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(TZ_COL)
                except:
                    continue
                dias_diff = (dt.date() - ahora.date()).days
                if dias_diff < 0 or dias_diff > dias: continue
                partidos.append({
                    "id": hashlib.md5(uid_raw.encode()).hexdigest()[:8],
                    "dt": dt, "fecha": fecha_str,
                    "hora": dt.strftime("%I:%M %p"),
                    "local": loc, "visit": vis,
                    "ya_jugado": False,
                    "gol_loc": None, "gol_vis": None,
                    "hoy": dias_diff == 0,
                    "manana": dias_diff == 1,
                    "venue": e.get("strVenue",""),
                    "city": e.get("strCity",""),
                    "liga": "International Friendlies",
                })
        except: pass

    partidos.sort(key=lambda x: x["dt"])
    return partidos, None

@st.cache_data(ttl=3600)
def get_historial_seleccion(team_id, api_key, n=10):
    """
    Obtiene últimos N partidos de una selección desde API-Football.
    Retorna lista de (rival, gf, gc, resultado, fecha, importancia)
    """
    headers = {"x-apisports-key": api_key}
    url = "https://v3.football.api-sports.io/fixtures"
    params = {
        "team": team_id,
        "last": n,
        "status": "FT",
    }
    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)
        data = r.json()
        partidos = []
        for f in data.get("response", []):
            teams = f.get("teams", {})
            goals = f.get("goals", {})
            league = f.get("league", {})
            es_local = teams.get("home", {}).get("id") == team_id
            rival = teams.get("away" if es_local else "home", {}).get("name","")
            gf = goals.get("home" if es_local else "away", 0) or 0
            gc = goals.get("away" if es_local else "home", 0) or 0
            resultado = "W" if gf > gc else ("D" if gf == gc else "L")
            partidos.append({
                "rival": rival, "gf": gf, "gc": gc,
                "resultado": resultado,
                "fecha": f.get("fixture",{}).get("date","")[:10],
                "liga": league.get("name",""),
                "es_local": es_local,
            })
        return partidos, None
    except Exception as ex:
        return [], str(ex)

@st.cache_data(ttl=3600)
def get_team_id_seleccion(nombre, api_key):
    """Busca el ID de una selección en API-Football."""
    headers = {"x-apisports-key": api_key}
    url = "https://v3.football.api-sports.io/teams"
    params = {"name": nombre, "type": "national"}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=10)
        data = r.json()
        resp = data.get("response", [])
        if resp:
            return resp[0].get("team", {}).get("id"), None
        return None, f"No encontrado: {nombre}"
    except Exception as ex:
        return None, str(ex)

def buscar_elo(nombre, elo_dict):
    """Busca el Elo de una selección con matching flexible — soporta español e inglés."""
    import unicodedata
    def norm(s): return unicodedata.normalize("NFKD",s).encode("ascii","ignore").decode().lower()

    # Aliases: nombre en español/variante → nombre en diccionario Elo
    ALIASES = {
        # Español → Inglés
        "azerbaiyan": "Azerbaijan", "azerbaiyán": "Azerbaijan",
        "belgica": "Belgium", "bélgica": "Belgium",
        "dinamarca": "Denmark",
        "escocia": "Scotland",
        "eslovakia": "Slovakia", "eslovaquia": "Slovakia",
        "eslovenia": "Slovenia",
        "espana": "Spain", "españa": "Spain",
        "finlandia": "Finland",
        "francia": "France",
        "gales": "Wales",
        "georgia": "Georgia",
        "grecia": "Greece",
        "hungria": "Hungary", "hungría": "Hungary",
        "irlanda": "Republic of Ireland", "republica de irlanda": "Republic of Ireland",
        "irlanda del norte": "Northern Ireland",
        "islandia": "Iceland",
        "italia": "Italy",
        "noruega": "Norway",
        "paises bajos": "Netherlands", "países bajos": "Netherlands",
        "polonia": "Poland",
        "portugal": "Portugal",
        "rumania": "Romania", "rumanía": "Romania",
        "rusia": "Russia",
        "serbia": "Serbia",
        "suecia": "Sweden",
        "suiza": "Switzerland",
        "turquia": "Turkey", "turquía": "Turkey",
        "ucrania": "Ukraine",
        "alemania": "Germany",
        "austria": "Austria",
        "croacia": "Croatia",
        "chipre": "Cyprus",
        "luxemburgo": "Luxembourg",
        "armenia": "Armenia",
        "bielorrusia": "Belarus",
        "estonia": "Estonia",
        "letonia": "Latvia",
        "lituania": "Lithuania",
        "moldavia": "Moldova",
        "islas feroe": "Faroe Islands",
        "andorra": "Andorra",
        "san marino": "San Marino",
        "gibraltar": "Gibraltar",
        "malta": "Malta",
        "kosovo": "Kosovo",
        "albania": "Albania",
        "israel": "Israel",
        "macedonia del norte": "North Macedonia",
        "bosnia": "Bosnia and Herzegovina",
        "montenegro": "Montenegro",
        # América
        "estados unidos": "USA", "eeuu": "USA",
        "canada": "Canada", "canadá": "Canada",
        "mexico": "Mexico", "méxico": "Mexico",
        "brasil": "Brazil",
        "argentina": "Argentina",
        "colombia": "Colombia",
        "chile": "Chile",
        "peru": "Peru", "perú": "Peru",
        "uruguay": "Uruguay",
        "ecuador": "Ecuador",
        "venezuela": "Venezuela",
        "paraguay": "Paraguay",
        "bolivia": "Bolivia",
        "costa rica": "Costa Rica",
        "panama": "Panama", "panamá": "Panama",
        "jamaica": "Jamaica",
        "haiti": "Haiti", "haití": "Haiti",
        "honduras": "Honduras",
        "el salvador": "El Salvador",
        "guatemala": "Guatemala",
        "cuba": "Cuba",
        "nicaragua": "Nicaragua",
        "trinidad y tobago": "Trinidad and Tobago",
        "republica dominicana": "Dominican Republic",
        "república dominicana": "Dominican Republic",
        "puerto rico": "Puerto Rico",
        "curazao": "Curacao",
        "islas virgenes britanicas": "British Virgin Islands",
        "islas vírgenes británicas": "British Virgin Islands",
        # África
        "marruecos": "Morocco",
        "argelia": "Algeria",
        "egipto": "Egypt",
        "tunez": "Tunisia", "túnez": "Tunisia",
        "nigeria": "Nigeria",
        "ghana": "Ghana",
        "costa de marfil": "Ivory Coast",
        "camerun": "Cameroon", "camerún": "Cameroon",
        "senegal": "Senegal",
        "mali": "Mali", "malí": "Mali",
        "burkina faso": "Burkina Faso",
        "rd congo": "DR Congo", "rep dem congo": "DR Congo",
        "congo dr": "DR Congo",
        "angola": "Angola",
        "benin": "Benin", "benín": "Benin",
        "niger": "Niger", "níger": "Niger",
        "mauritania": "Mauritania",
        "cabo verde": "Cape Verde",
        "zimbabue": "Zimbabwe",
        "zambia": "Zambia",
        "uganda": "Uganda",
        "kenia": "Kenya",
        "etiopia": "Ethiopia", "etiopía": "Ethiopia",
        "guinea": "Guinea",
        "guinea bissau": "Guinea-Bissau",
        "guinea ecuatorial": "Equatorial Guinea",
        "gabon": "Gabon", "gabón": "Gabon",
        "mozambique": "Mozambique",
        "tanzania": "Tanzania",
        "ruanda": "Rwanda",
        "namibia": "Namibia",
        "botswana": "Botswana",
        "liberia": "Liberia",
        "togo": "Togo",
        "sierra leona": "Sierra Leone",
        "gambia": "Gambia",
        "sudan": "Sudan", "sudán": "Sudan",
        "libia": "Libya",
        "madagascar": "Madagascar",
        "comoras": "Comoros",
        "mauricio": "Mauritius",
        "seychelles": "Seychelles",
        "suazilandia": "Eswatini",
        "lesoto": "Lesotho",
        "somalia": "Somalia",
        "yibuti": "Djibouti",
        "eritrea": "Eritrea",
        "republica centroafricana": "Central African Republic",
        "chad": "Chad",
        "burundi": "Burundi",
        "sudan del sur": "South Sudan",
        "sudafrica": "South Africa", "sudáfrica": "South Africa",
        # Asia
        "japon": "Japan", "japón": "Japan",
        "corea del sur": "South Korea",
        "iran": "Iran", "irán": "Iran",
        "arabia saudi": "Saudi Arabia", "arabia saudita": "Saudi Arabia",
        "uzbekistan": "Uzbekistan",
        "irak": "Iraq",
        "jordania": "Jordan",
        "barein": "Bahrain", "baréin": "Bahrain",
        "emiratos arabes unidos": "UAE",
        "catar": "Qatar",
        "oman": "Oman", "omán": "Oman",
        "kuwait": "Kuwait",
        "siria": "Syria",
        "libano": "Lebanon", "líbano": "Lebanon",
        "palestina": "Palestine",
        "afganistan": "Afghanistan", "afganistán": "Afghanistan",
        "filipinas": "Philippines",
        "vietnam": "Vietnam",
        "tailandia": "Thailand",
        "indonesia": "Indonesia",
        "malasia": "Malaysia",
        "singapur": "Singapore",
        "india": "India",
        "pakistan": "Pakistan", "pakistán": "Pakistan",
        "bangladesh": "Bangladesh",
        "myanmar": "Myanmar",
        "camboya": "Cambodia",
        "china": "China",
        "corea del norte": "North Korea",
        # Oceanía
        "australia": "Australia",
        "nueva zelanda": "New Zealand",
        "fiyi": "Fiji",
        "papua nueva guinea": "Papua New Guinea",
        "islas salomon": "Solomon Islands", "islas salomón": "Solomon Islands",
        "vanuatu": "Vanuatu",
        "tahiti": "Tahiti", "tahití": "Tahiti",
        # Otros alias comunes
        "dr congo": "DR Congo",
        "ivory coast": "Ivory Coast",
        "cote d ivoire": "Ivory Coast",
        "korea republic": "South Korea",
        "united states": "USA",
        "republic of ireland": "Republic of Ireland",
    }

    if nombre in elo_dict: return elo_dict[nombre]
    nombre_n = norm(nombre)

    # Chequear aliases
    if nombre_n in ALIASES:
        target = ALIASES[nombre_n]
        if target in elo_dict: return elo_dict[target]

    # Exacto normalizado
    for k, v in elo_dict.items():
        if norm(k) == nombre_n: return v

    # Parcial — primera palabra
    primera = nombre_n.split()[0] if nombre_n.split() else nombre_n
    if len(primera) > 3:
        for k, v in elo_dict.items():
            if primera in norm(k) or norm(k).split()[0] == primera:
                return v

    return None

def poisson_seleccion(gf_avg_loc, gc_avg_loc, gf_avg_vis, gc_avg_vis, avg_goles=2.5):
    """Calcula probabilidades Poisson para selecciones con avg dinámico."""
    if gf_avg_loc <= 0 or gf_avg_vis <= 0:
        return None, None, None
    # Usar promedio dinámico de los 4 valores para evitar aplastamiento
    # cuando los equipos tienen estadísticas por debajo de 2.5
    avg_din = max((gf_avg_loc + gc_avg_loc + gf_avg_vis + gc_avg_vis) / 4, 0.8)
    ll = round((gf_avg_loc / avg_din) * (gc_avg_vis / avg_din) * avg_din * 1.1, 3)
    lv = round((gf_avg_vis / avg_din) * (gc_avg_loc / avg_din) * avg_din, 3)
    ll = max(ll, 0.3); lv = max(lv, 0.3)
    pl = pe = pv = 0
    for gl in range(9):
        for gv in range(9):
            p = pmf(gl, ll) * pmf(gv, lv)
            if gl > gv: pl += p
            elif gl == gv: pe += p
            else: pv += p
    return round(pl,4), round(pe,4), round(pv,4)


import csv, io

@st.cache_data(ttl=86400)
def cargar_partidos_tenis(tour="atp"):
    """Descarga partidos ATP o WTA desde GitHub (Jeff Sackmann)."""
    anio = datetime.datetime.now(TZ_COL).year
    base = "tennis_atp" if tour=="atp" else "tennis_wta"
    prefix = "atp" if tour=="atp" else "wta"
    url = f"https://raw.githubusercontent.com/JeffSackmann/{base}/master/{prefix}_matches_{anio}.csv"
    try:
        r = requests.get(url, headers={"User-Agent":"Mozilla/5.0"}, timeout=15)
        r.raise_for_status()
        return list(csv.DictReader(io.StringIO(r.text))), None
    except Exception as e:
        return [], str(e)

@st.cache_data(ttl=86400)
def calcular_elo_tenis(tour="atp", k=32):
    """Calcula Elo general y por superficie para todos los jugadores."""
    partidos, err = cargar_partidos_tenis(tour)
    if not partidos: return {}, {}, err
    elo_g = {}
    elo_s = {}
    def prob(a,b): return 1/(1+10**((b-a)/400))
    for p in partidos:
        gan = p.get("winner_name","")
        per = p.get("loser_name","")
        sup = p.get("surface","Hard")
        if not gan or not per: continue
        for j in [gan,per]:
            if j not in elo_g: elo_g[j]=1500
            if j not in elo_s: elo_s[j]={"Hard":1500,"Clay":1500,"Grass":1500}
        ea = prob(elo_g[gan],elo_g[per])
        elo_g[gan] += k*(1-ea); elo_g[per] += k*(0-(1-ea))
        if sup in ["Hard","Clay","Grass"]:
            ea_s = prob(elo_s[gan][sup],elo_s[per][sup])
            elo_s[gan][sup] += k*(1-ea_s)
            elo_s[per][sup] += k*(0-(1-ea_s))
    return elo_g, elo_s, None

def prob_elo(elo_a, elo_b):
    return round(1/(1+10**((elo_b-elo_a)/400)), 4)

def buscar_jugador(nombre, elo_g):
    """Busca jugador en el modelo por nombre parcial."""
    nombre_l = nombre.lower()
    exacto = [j for j in elo_g if nombre_l == j.lower()]
    if exacto: return exacto[0]
    parcial = [j for j in elo_g if nombre_l in j.lower()]
    if parcial: return sorted(parcial, key=lambda x:-elo_g[x])[0]
    return None

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
def init():
    if "bankroll" not in st.session_state: st.session_state.bankroll=119613
    if "wins"     not in st.session_state: st.session_state.wins=5
    if "losses"   not in st.session_state: st.session_state.losses=0
    if "apuestas" not in st.session_state:
        st.session_state.apuestas=[
            {"partido":"Nacional vs Inter Bogotá","apuesta":"Local","cuota":2.85,"stake":6754,"resultado":"won","ganancia":13195},
            {"partido":"Santa Fe vs América",      "apuesta":"Local","cuota":2.23,"stake":2405,"resultado":"won","ganancia":2958},
            {"partido":"Valencia vs Rayo",         "apuesta":"Empate","cuota":3.05,"stake":1060,"resultado":"won","ganancia":2183},
            {"partido":"Girona vs Real Sociedad",  "apuesta":"Empate","cuota":3.65,"stake":1142,"resultado":"won","ganancia":3026},
            {"partido":"Real Madrid vs Oviedo",    "apuesta":"Local","cuota":1.24,"stake":3336,"resultado":"won","ganancia":801},
            {"partido":"Aston Villa vs Liverpool", "apuesta":"Visitante","cuota":2.40,"stake":1000,"resultado":"pending","ganancia":0},
        ]
init()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="brand">BetAnalytics</p>',unsafe_allow_html=True)
    st.markdown('<p class="eyebrow">Sistema de apuestas basado en datos</p>',unsafe_allow_html=True)
    st.divider()

    st.markdown("### ⚙️ Fuentes de datos")
    _fd_secret = st.secrets.get("FOOTBALL_DATA_KEY", "")
    if _fd_secret:
        fd_key = _fd_secret
        st.success("✓ API key europea cargada automáticamente")
    else:
        fd_key = st.text_input("API Key — football-data.org",type="password",
                               placeholder="Ligas europeas",
                               help="Gratis en football-data.org/client/register")
    rf_key = st.secrets.get("API_FOOTBALL_KEY", "")
    if rf_key:
        st.success("✓ API-Football activada (Venezuela, Bolivia, Paraguay)")
    else:
        rf_key = st.text_input("API Key — API-Football", type="password",
                               placeholder="Venezuela, Bolivia, Paraguay",
                               help="Gratis en api-football.com")
    # Cuotas automaticas via The Odds API
    _odds_secret = st.secrets.get("ODDS_API_KEY", "")
    if _odds_secret:
        odds_api_key = _odds_secret
        st.success("✓ Cuotas automaticas activadas")
    else:
        odds_api_key = st.text_input("API Key — The Odds API",type="password",
                                     placeholder="Cuotas automaticas",
                                     help="Gratis en the-odds-api.com")

    st.divider()
    liga_n=st.selectbox("🏟️ Liga",list(LIGAS.keys()),index=0)
    li=LIGAS[liga_n]

    st.divider()
    st.markdown("### 💰 Capital")
    bi=st.number_input("Bankroll disponible (COP)",1000,10000000,
                        st.session_state.bankroll,500,format="%d",
                        help="Se descuenta al registrar apuesta, se acredita al ganar")
    if bi!=st.session_state.bankroll: st.session_state.bankroll=bi
    bank=st.session_state.bankroll

    kf=st.select_slider("Fracción Kelly",[0.25,0.5,0.75,1.0],value=0.5,
        format_func=lambda x:{0.25:"¼ Kelly",0.5:"½ Kelly",0.75:"¾ Kelly",1.0:"Kelly completo"}[x])
    ue=st.slider("Edge mínimo (%)",1,10,3)/100

    st.divider()
    rend=round((bank/BK_INIT-1)*100,1)
    cr="#22c55e" if rend>=0 else "#ef4444"
    st.markdown(f"""
    <div class="card"><div class="card-label">Bankroll inicial</div><div class="card-value" style="font-size:1.1rem">${BK_INIT:,}</div></div>
    <div class="card"><div class="card-label">Bankroll disponible</div><div class="card-value" style="font-size:1.1rem;color:#22c55e">${bank:,}</div></div>
    <div class="card"><div class="card-label">Rendimiento total</div><div class="card-value" style="font-size:1.1rem;color:{cr}">{rend:+.1f}%</div></div>
    <div class="card"><div class="card-label">Record</div><div class="card-value" style="font-size:1.1rem">{st.session_state.wins}W / {st.session_state.losses}L</div></div>
    """,unsafe_allow_html=True)

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
ahora=datetime.datetime.now(TZ_COL)
st.markdown(f'<p class="eyebrow">{liga_n} · {ahora.strftime("%A %d %b %Y · %I:%M %p")} hora Colombia</p>',unsafe_allow_html=True)
st.markdown('<p class="brand" style="font-size:2.4rem">BetAnalytics</p>',unsafe_allow_html=True)
st.markdown("")

# Validación de keys según liga
necesita_fd = li["src"]=="fd"
necesita_rf = li["src"]=="rf"
tiene_fd = bool(fd_key)
tiene_rf = bool(rf_key)

if necesita_fd and not tiene_fd:
    st.info("👈 Ingresa tu API key de **football-data.org** para cargar esta liga.")
if necesita_rf and not tiene_rf:
    st.info("👈 Ingresa tu API key de **API-Football (RapidAPI)** para cargar ligas de Suramérica y Colombia.")

tab1,tab2,tab3,tab4,tab5,tab6=st.tabs(["⚽ Partidos","📈 Equipos","💰 Mis apuestas","📋 Casos de estudio","🎾 Tenis","🌍 Amistosos"])

# ─────────────────────────────────────────────
# FUNCIÓN AUXILIAR: RENDER DE PARTIDO
# ─────────────────────────────────────────────
def render_partido(p, M, avg, bank, kf, ue, cuotas_auto=None):
    loc,vis,hora=p["local"],p["visit"],p["hora"]
    ll,lv=lams(loc,vis,M,avg)
    pr=poisson(ll,lv)

    with st.expander(f"⚽  {loc}  vs  {vis}   ·   {hora} Col", expanded=p["hoy"]):
        # Probabilidades
        c1,c2,c3=st.columns(3)
        for col,lbl,val,clr in [
            (c1,"Local gana",pr["pl"]*100,"#38bdf8"),
            (c2,"Empate",    pr["pe"]*100,"#94a3b8"),
            (c3,"Visit gana",pr["pv"]*100,"#818cf8"),
        ]:
            with col:
                st.markdown(f"""
                <div class="prob-wrap">
                    <div class="card-label">{lbl}</div>
                    <div class="card-value">{val:.1f}%</div>
                    <div class="prob-bar"><div style="width:{val}%;height:10px;background:{clr};border-radius:6px;"></div></div>
                </div>""",unsafe_allow_html=True)

        # Marcadores
        st.markdown("**Marcadores más probables:**")
        cols=st.columns(5)
        for i,s in enumerate(pr["top"]):
            with cols[i]:
                st.markdown(f'<div class="score-card"><div class="score-num">{s["m"]}</div><div class="score-pct">{s["p"]}%</div></div>',unsafe_allow_html=True)

        st.markdown("")
        # ── Memoria de cálculo ──────────────────
        with st.expander("📊 Memoria de cálculo del modelo", expanded=False):
            ml_info = buscar_equipo_info(loc, M)
            mv_info = buscar_equipo_info(vis, M)
            ll_show, lv_show = lams(loc, vis, M, avg)

            # Partidos del equipo local
            st.markdown(f"**{loc} (local) — {ml_info['n']} partidos**")
            st.markdown(f"Ataque: `{ml_info['atk']:.3f}` · Defensa: `{ml_info['def']:.3f}` · Goles/partido: `{ml_info['gf_avg']:.2f}` a favor, `{ml_info['gc_avg']:.2f}` en contra")
            if ml_info['partidos']:
                for l2,v2,gl2,gv2 in ml_info['partidos']:
                    icono = "✓" if (l2==loc and gl2>gv2) or (v2==loc and gv2>gl2) else ("=" if gl2==gv2 else "✗")
                    st.markdown(f"&nbsp;&nbsp;{icono} {l2} **{gl2}-{gv2}** {v2}", unsafe_allow_html=True)
            else:
                gf_tot = round(ml_info['gf_avg'] * ml_info['n'])
                gc_tot = round(ml_info['gc_avg'] * ml_info['n'])
                st.markdown(f"&nbsp;&nbsp;📊 *Modelo basado en totales de temporada: {gf_tot} GF · {gc_tot} GC en {ml_info['n']} partidos. Resultados individuales no disponibles.*")

            st.divider()

            # Partidos del equipo visitante
            st.markdown(f"**{vis} (visitante) — {mv_info['n']} partidos**")
            st.markdown(f"Ataque: `{mv_info['atk']:.3f}` · Defensa: `{mv_info['def']:.3f}` · Goles/partido: `{mv_info['gf_avg']:.2f}` a favor, `{mv_info['gc_avg']:.2f}` en contra")
            if mv_info['partidos']:
                for l2,v2,gl2,gv2 in mv_info['partidos']:
                    icono = "✓" if (l2==vis and gl2>gv2) or (v2==vis and gv2>gl2) else ("=" if gl2==gv2 else "✗")
                    st.markdown(f"&nbsp;&nbsp;{icono} {l2} **{gl2}-{gv2}** {v2}", unsafe_allow_html=True)
            else:
                gf_tot = round(mv_info['gf_avg'] * mv_info['n'])
                gc_tot = round(mv_info['gc_avg'] * mv_info['n'])
                st.markdown(f"&nbsp;&nbsp;📊 *Modelo basado en totales de temporada: {gf_tot} GF · {gc_tot} GC en {mv_info['n']} partidos. Resultados individuales no disponibles.*")

            st.divider()

            # Proyección
            st.markdown("**Proyección de goles (Poisson)**")
            st.markdown(f"Goles esperados **{loc}** (local): `{ll_show}`")
            st.markdown(f"&nbsp;&nbsp;= Ataque({ml_info['atk']:.3f}) × Defensa_visit({mv_info['def']:.3f}) × Liga({avg}) × Factor_local(1.15)", unsafe_allow_html=True)
            st.markdown(f"Goles esperados **{vis}** (visit): `{lv_show}`")
            st.markdown(f"&nbsp;&nbsp;= Ataque({mv_info['atk']:.3f}) × Defensa_local({ml_info['def']:.3f}) × Liga({avg})", unsafe_allow_html=True)

            st.divider()
            st.markdown("**Distribución de probabilidades (Poisson)**")
            st.markdown(f"Para cada marcador (0-0, 1-0, 0-1, 1-1, 2-0...): `P = Poisson(gl, {ll_show}) × Poisson(gv, {lv_show})`")
            st.markdown(f"**{loc} gana** (gl > gv): suma de P donde local marca más = **{pr['pl']*100:.1f}%**")
            st.markdown(f"**Empate** (gl = gv): suma de P donde marcan igual = **{pr['pe']*100:.1f}%**")
            st.markdown(f"**{vis} gana** (gl < gv): suma de P donde visitante marca más = **{pr['pv']*100:.1f}%**")

        # Cuotas — automáticas si disponibles, manual si no
        cuotas_encontradas = buscar_cuotas(loc, vis, cuotas_auto) if cuotas_auto else None
        if cuotas_encontradas:
            ql_def = cuotas_encontradas["local"]
            qe_def = cuotas_encontradas["empate"]
            qv_def = cuotas_encontradas["visit"]
            n_casas = cuotas_encontradas.get("n_casas", 1)
            st.markdown(f"**Cuotas automáticas** (promedio de {n_casas} casas de apuestas):")
        else:
            ql_def, qe_def, qv_def = 2.00, 3.30, 3.80
            st.markdown("**Cuotas — actualiza con las de tu casa de apuestas:**")
        c1,c2,c3=st.columns(3)
        with c1: ql=st.number_input("Local",   1.01,200.0,float(min(ql_def,199.0)),0.05,key=f"ql_{p['id']}",format="%.2f")
        with c2: qe=st.number_input("Empate",  1.01,200.0,float(min(qe_def,199.0)),0.05,key=f"qe_{p['id']}",format="%.2f")
        with c3: qv=st.number_input("Visit",   1.01,200.0,float(min(qv_def,199.0)),0.05,key=f"qv_{p['id']}",format="%.2f")

        im=impl({"local":ql,"empate":qe,"visit":qv})
        vig=im["vig"]
        if vig<=7:    st.markdown(f'<div class="vig-ok">✓ Vig: {vig}% — mercado limpio</div>',unsafe_allow_html=True)
        elif vig<=12: st.markdown(f'<div class="vig-warn">⚠️ Vig: {vig}% — margen alto, precaución</div>',unsafe_allow_html=True)
        else:         st.markdown(f'<div class="vig-bad">✗ Vig: {vig}% — margen muy alto, evitar</div>',unsafe_allow_html=True)

        st.markdown("**Veredicto del modelo:**")
        hay=False
        for nm,pm,cu,et in [("local",pr["pl"],ql,loc),("empate",pr["pe"],qe,"Empate"),("visit",pr["pv"],qv,vis)]:
            pi=im["p"].get(nm,0)
            k=kelly_calc(pm,cu,kf,bank,ue)
            if k["value"]:
                hay=True
                st.markdown(f"""
                <div class="vbet">
                    <span class="vbet-badge">✓ VALUE BET</span>
                    <div class="vbet-title">{et} · cuota {cu}</div>
                    <div class="vbet-grid">
                        <div class="vbet-item"><label>P MODELO</label><span>{pm*100:.1f}%</span></div>
                        <div class="vbet-item"><label>P IMPLÍCITA</label><span>{pi*100:.1f}%</span></div>
                        <div class="vbet-item"><label>EDGE</label><span style="color:#4ade80">+{k['edge']:.1f}%</span></div>
                        <div class="vbet-item"><label>KELLY</label><span>{k['ku']:.1f}%</span></div>
                        <div class="vbet-item"><label>APOSTAR</label><span class="highlight">${k['s']:,}</span></div>
                        <div class="vbet-item"><label>RETORNO</label><span>${k['r']:,}</span></div>
                        <div class="vbet-item"><label>EV/$1</label><span>+{k['ev']:.3f}</span></div>
                    </div>
                </div>""",unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="nobet">
                    <span class="nobet-badge">✗ SIN VALUE</span>
                    <span class="nobet-text">{et} · cuota {cu} · edge {k['edge']:+.1f}%</span>
                </div>""",unsafe_allow_html=True)

        if not hay:
            st.markdown('<div style="background:#131e30;border:1px solid #1f2d42;border-radius:8px;padding:12px 16px;color:#64748b;font-size:0.88rem;margin-top:4px;">🔇 Sin value bets con estas cuotas. No apostar este partido.</div>',unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TAB 1: PARTIDOS
# ─────────────────────────────────────────────
with tab1:
    hist,prox=[],[]
    cargado=False

    if li["src"]=="fd" and tiene_fd:
        with st.spinner("Cargando datos..."):
            hist,e1=fd_hist(li["code"],fd_key)
            prox,e2=fd_next(li["code"],fd_key)
        if e1: st.warning(f"Error historial: {e1}")
        if e2: st.warning(f"Error próximos: {e2}")
        cargado=True

    elif li["src"]=="wiki_tabla":
        e1, e2, prox = None, None, []
        fb = li.get("hist_fallback")
        # Para ligas con tabla estática actualizada, usarla directamente
        if fb and fb in HIST_CONMEBOL:
            hist = build_model_desde_tabla(HIST_CONMEBOL[fb], li["avg"])
            st.info(f"📊 Modelo basado en tabla de posiciones actualizada ({fb} 2026).")
        else:
            with st.spinner("Cargando tabla de posiciones desde Wikipedia..."):
                hist,e1=wiki_tabla_hist(li["wiki_url"], li["avg"])
            if not isinstance(hist, dict) or len([k for k in hist if k!="_avg"]) < 5:
                st.warning(f"Error Wikipedia: {e1}")
            else:
                n_eq = len([k for k in hist if k!="_avg"])
                st.success(f"✓ Modelo cargado ({n_eq} equipos desde tabla Wikipedia)")
        # Próximos: API-Football primero si disponible, sino The Odds API, sino TheSportsDB
        if li.get("apif_id") and rf_key:
            prox,e2 = apifootball_next(li["apif_id"], li.get("apif_season",2026), rf_key)
        elif li.get("use_odds_fixtures") and li.get("odds_key") and odds_api_key:
            prox,e2 = odds_fixtures(li["odds_key"], odds_api_key)
        elif li.get("sportsdb_id"):
            prox,e2 = sportsdb_next(li["sportsdb_id"])
        if e2: st.warning(f"Error próximos: {e2}")
        cargado=True

    elif li["src"]=="sportsdb":
        e1, e2, prox = None, None, []
        with st.spinner("Cargando resultados desde TheSportsDB..."):
            hist,e1=sportsdb_hist(li["sportsdb_id"], li.get("sportsdb_season","2026"))
        # Fallback con tabla estática si TheSportsDB retorna pocos partidos
        if len(hist) < 30:
            fb = li.get("hist_fallback")
            if "Argentina" in liga_n:
                hist = build_model_desde_tabla(HIST_ARGENTINA_2026, li["avg"])
                st.info("📊 Modelo basado en tabla de posiciones del Apertura 2026.")
            elif "Brasileirao" in liga_n or "Brasil" in liga_n:
                hist = build_model_desde_tabla(HIST_BRASILEIRAO_2026, li["avg"])
                st.info("📊 Modelo basado en tabla de posiciones del Brasileirao 2026.")
            elif "Liga MX" in liga_n or "Mexico" in liga_n:
                hist = build_model_desde_tabla(HIST_LIGAMX_2026, li["avg"])
                st.info("📊 Modelo basado en tabla del Clausura 2026. Liga MX en receso hasta julio.")
            elif fb and fb in HIST_CONMEBOL:
                hist = build_model_desde_tabla(HIST_CONMEBOL[fb], li["avg"])
                st.info(f"📊 Modelo basado en tabla estática ({fb} 2026).")
        if li.get("use_odds_fixtures") and li.get("odds_key") and odds_api_key:
            prox,e2=odds_fixtures(li["odds_key"],odds_api_key)
        else:
            prox,e2=sportsdb_next(li["sportsdb_id"], li.get("sportsdb_season","2026"))
        if e1: st.warning(f"Error historial TheSportsDB: {e1}")
        if e2: st.warning(f"Error próximos: {e2}")
        cargado=True

    elif li["src"] in ("wiki", "wiki_multi"):
        e1, e2, prox = None, None, []
        # Para Liga Argentina: usar modelo estático directo, no depender del scraper
        if "Argentina" in liga_n:
            hist = build_model_desde_tabla(HIST_ARGENTINA_2026, li["avg"])
            e1 = None
        else:
            with st.spinner("Cargando datos..."):
                if li["src"]=="wiki_multi":
                    hist,e1=wiki_hist_multi(li["wiki_urls"],li["wiki_fmt"],li.get("equipos_excluir",[]))
                else:
                    hist,e1=wiki_hist(li["wiki_url"],li["wiki_fmt"],li.get("equipos_excluir",[]))
                # Fallback si el scraper retorna vacío
                if not isinstance(hist, dict) and len(hist) < 10:
                    hist = []
        # Mostrar info fuera del spinner
        if isinstance(hist, dict) and "Argentina" in liga_n:
            st.info("📊 Modelo basado en tabla de posiciones del Apertura 2026.")
        # Cargar próximos partidos
        if li.get("use_odds_fixtures") and li.get("odds_key") and odds_api_key:
            prox,e2=odds_fixtures(li["odds_key"],odds_api_key)
        elif li["src"]=="wiki":
            prox_wiki,e2=wiki_next(li["wiki_url"],li["wiki_fmt"],li.get("equipos_excluir",[]))
            # Final Liga BetPlay I-2026 hardcoded
            if "Liga BetPlay" in liga_n and not prox_wiki:
                import hashlib
                final = [
                    ("Junior","Atletico Nacional","2026-06-02","07:30 PM"),
                    ("Atletico Nacional","Junior","2026-06-08","05:00 PM"),
                ]
                prox_wiki = []
                for loc,vis,fecha,hora in final:
                    uid=hashlib.md5(f"{loc}{vis}{fecha}".encode()).hexdigest()[:8]
                    fecha_dt=datetime.datetime.strptime(fecha,"%Y-%m-%d").replace(tzinfo=TZ_COL)
                    prox_wiki.append({"id":uid,"dt":fecha_dt,"fecha":fecha,"hora":hora,
                                      "local":loc,"visit":vis,"jornada":"Final",
                                      "hoy":es_hoy(fecha_dt),"manana":es_manana(fecha_dt)})
            prox=prox_wiki
        if e1: st.warning(f"Error historial: {e1}")
        if e2: st.warning(f"Error próximos: {e2}")
        cargado=True

    elif li["src"]=="rf" and tiene_rf:
        with st.spinner("Cargando datos de Suramérica..."):
            hist,e1=rf_hist(li["rf_id"],rf_key)
            prox,e2=rf_next(li["rf_id"],rf_key)
        if e1: st.warning(f"Error historial: {e1}")
        if e2: st.warning(f"Error próximos: {e2}")
        cargado=True

    if cargado and hist:
        # hist puede ser lista de partidos o modelo pre-construido (dict) según el fallback
        if isinstance(hist, dict):
            M = hist  # ya es modelo (ej: build_model_desde_tabla)
            n_partidos = sum(v.get("n",0) for k,v in hist.items() if k != "_avg") // 2
            st.success(f"✓ Modelo cargado ({len([k for k in hist if k!='_avg'])} equipos) · {len(prox)} próximos")
        else:
            st.success(f"✓ {len(hist)} partidos históricos · {len(prox)} próximos (próximos 3 días · hora Colombia)")
            M=build_model(hist,li["avg"])
        # Cargar cuotas automaticas si hay odds_key configurado
        cuotas_auto = {}
        if li.get("odds_key") and odds_api_key:
            with st.spinner("Cargando cuotas automaticas..."):
                cuotas_auto = get_cuotas_automaticas(li["odds_key"], odds_api_key)
            if cuotas_auto:
                st.success(f"✓ Cuotas automaticas cargadas: {len(cuotas_auto)} partidos")
        fechas=sorted(set(p["fecha"] for p in prox))
        if not fechas:
            if li.get("src") in ("wiki_tabla",) or (li.get("src")=="sportsdb" and not li.get("use_odds_fixtures")):
                st.warning(f"⚠️ TheSportsDB tiene cobertura limitada para esta liga. Solo muestra {len(prox)} partido(s) registrado(s). Ingresa el partido manualmente abajo si no aparece.")
            else:
                st.info("No hay partidos en los próximos 3 días para esta liga.")
        elif len(prox) < 4 and li.get("src") in ("wiki_tabla",):
            st.info(f"ℹ️ TheSportsDB solo tiene {len(prox)} partido(s) registrado(s) para esta jornada. Pueden faltar partidos — usa el análisis manual para los que no aparezcan.")
        for fecha in fechas:
            pf=[p for p in prox if p["fecha"]==fecha]
            if not pf: continue
            dt0=pf[0]["dt"]
            if es_hoy(dt0):    lbl=f"HOY · {dt0.strftime('%A %d de %B').upper()}"; badge='<span class="hoy-pill">HOY</span>'
            elif es_manana(dt0): lbl=f"MAÑANA · {dt0.strftime('%A %d de %B').upper()}"; badge=""
            else:               lbl=dt0.strftime('%A %d de %B').upper(); badge=""
            st.markdown(f'<div class="day-hdr">{lbl}{badge}</div>',unsafe_allow_html=True)
            for p in pf:
                render_partido(p,M,li["avg"],bank,kf,ue,cuotas_auto)

    elif cargado:
        st.info("No se encontraron partidos históricos suficientes para construir el modelo.")

    # ── Análisis manual — siempre visible cuando hay modelo cargado ──
    if cargado and hist:
        st.markdown("---")
        st.markdown("### 🖊️ Análisis de partido")
        st.caption("Selecciona equipos del modelo o escribe cualquier nombre.")

        # Obtener lista de equipos del modelo actual
        equipos_modelo = []
        if hist and isinstance(hist, dict):
            equipos_modelo = sorted([k for k in hist.keys() if k != "_avg" and isinstance(hist[k], dict)])
        elif hist and isinstance(hist, list):
            M_tmp = build_model(hist, li["avg"])
            equipos_modelo = sorted([k for k in M_tmp.keys() if k != "_avg" and isinstance(M_tmp[k], dict)])

        c1, c2 = st.columns(2)
        with c1:
            if equipos_modelo:
                opciones_l = ["✏️ Escribir nombre..."] + equipos_modelo
                sel_l = st.selectbox("Equipo local", opciones_l, key="sel_local")
                if sel_l == "✏️ Escribir nombre...":
                    eql = st.text_input("Nombre local", placeholder="Ej: Deportivo La Guaira", key="txt_local")
                else:
                    eql = sel_l
            else:
                eql = st.text_input("Equipo local", placeholder="Ej: Deportivo La Guaira", key="txt_local_only")

        with c2:
            if equipos_modelo:
                opciones_v = ["✏️ Escribir nombre..."] + equipos_modelo
                sel_v = st.selectbox("Equipo visitante", opciones_v, key="sel_visit")
                if sel_v == "✏️ Escribir nombre...":
                    eqv = st.text_input("Nombre visitante", placeholder="Ej: Caracas FC", key="txt_visit")
                else:
                    eqv = sel_v
            else:
                eqv = st.text_input("Equipo visitante", placeholder="Ej: Caracas FC", key="txt_visit_only")

        # Cuotas
        c1, c2, c3 = st.columns(3)
        with c1: ql = st.number_input("Cuota local",  1.01, 50.0, 2.00, 0.05, format="%.2f", key="m_ql")
        with c2: qe = st.number_input("Cuota empate", 1.01, 50.0, 3.30, 0.05, format="%.2f", key="m_qe")
        with c3: qv = st.number_input("Cuota visit",  1.01, 50.0, 3.80, 0.05, format="%.2f", key="m_qv")

        if eql and eqv and eql != eqv:
            # Calcular probabilidades desde el modelo Poisson si hay datos
            M_actual = hist if isinstance(hist, dict) else (build_model(hist, li["avg"]) if hist else None)
            usa_modelo = False
            pl, pe, pv = 0.45, 0.28, 0.27  # defaults

            if M_actual:
                ll, lv = lams(eql, eqv, M_actual, li["avg"])
                if ll > 0 and lv > 0:
                    pl_m, pe_m, pv_m = poisson(ll, lv)
                    pl, pe, pv = pl_m, pe_m, pv_m
                    usa_modelo = True
                    st.success(f"✓ Modelo Poisson aplicado — λ local: {ll:.2f} · λ visit: {lv:.2f}")
                    # Mostrar memoria de cálculo compacta
                    with st.expander("📊 Memoria de cálculo del modelo", expanded=False):
                        ml_info = M_actual.get(eql) or {}
                        mv_info = M_actual.get(eqv) or {}
                        # Buscar con matching
                        if not ml_info:
                            import unicodedata
                            def norm2(s): return unicodedata.normalize("NFKD",s).encode("ascii","ignore").decode().lower()
                            for k,v in M_actual.items():
                                if k != "_avg" and isinstance(v, dict) and norm2(k) == norm2(eql):
                                    ml_info = v; break
                        if not mv_info:
                            import unicodedata
                            def norm2(s): return unicodedata.normalize("NFKD",s).encode("ascii","ignore").decode().lower()
                            for k,v in M_actual.items():
                                if k != "_avg" and isinstance(v, dict) and norm2(k) == norm2(eqv):
                                    mv_info = v; break
                        if ml_info:
                            st.markdown(f"**{eql} (local) — {ml_info.get('n',0)} partidos**")
                            st.markdown(f"Ataque: `{ml_info.get('atk',1):.3f}` · Defensa: `{ml_info.get('def',1):.3f}` · GF/partido: `{ml_info.get('gf_avg',0):.2f}` · GC/partido: `{ml_info.get('gc_avg',0):.2f}`")
                        if mv_info:
                            st.markdown(f"**{eqv} (visitante) — {mv_info.get('n',0)} partidos**")
                            st.markdown(f"Ataque: `{mv_info.get('atk',1):.3f}` · Defensa: `{mv_info.get('def',1):.3f}` · GF/partido: `{mv_info.get('gf_avg',0):.2f}` · GC/partido: `{mv_info.get('gc_avg',0):.2f}`")
                        st.markdown(f"**Proyección:** λ_local = Atk({ml_info.get('atk',1):.3f}) × Def_visit({mv_info.get('def',1):.3f}) × Liga({li['avg']}) × Factor_local(1.15) = **{ll:.3f}**")
                        st.markdown(f"**Proyección:** λ_visit = Atk({mv_info.get('atk',1):.3f}) × Def_local({ml_info.get('def',1):.3f}) × Liga({li['avg']}) = **{lv:.3f}**")

            if not usa_modelo:
                st.info("⚠️ Equipos no encontrados en el modelo — ingresa las probabilidades manualmente.")
                c1, c2, c3 = st.columns(3)
                with c1: pl = st.number_input("P(local) %",  1.0, 99.0, 45.0, 0.5, key="m_pl") / 100
                with c2: pe = st.number_input("P(empate) %", 1.0, 99.0, 28.0, 0.5, key="m_pe") / 100
                with c3: pv = st.number_input("P(visit) %",  1.0, 99.0, 27.0, 0.5, key="m_pv") / 100

            # Veredicto
            im = impl({"local": ql, "empate": qe, "visit": qv})
            vig = im["vig"]
            if vig <= 7:    st.markdown(f'<div class="vig-ok">✓ Vig: {vig}% — mercado limpio</div>', unsafe_allow_html=True)
            elif vig <= 12: st.markdown(f'<div class="vig-warn">⚠️ Vig: {vig}%</div>', unsafe_allow_html=True)
            else:           st.markdown(f'<div class="vig-bad">✗ Vig: {vig}% — mercado caro</div>', unsafe_allow_html=True)

            st.markdown("**Veredicto del modelo:**")
            for nm, pm, cu, et in [("local", pl, ql, eql), ("empate", pe, qe, "Empate"), ("visit", pv, qv, eqv)]:
                k = kelly_calc(pm, cu, kf, bank, ue)
                if k["value"]:
                    st.markdown(f'<div class="vbet"><span class="vbet-badge">✓ VALUE BET</span><div class="vbet-title">{et} · cuota {cu}</div><div class="vbet-grid"><div class="vbet-item"><label>P MODELO</label><span>{pm*100:.1f}%</span></div><div class="vbet-item"><label>P IMPLÍCITA</label><span>{im["p"].get(nm,0)*100:.1f}%</span></div><div class="vbet-item"><label>EDGE</label><span style="color:#4ade80">+{k["edge"]:.1f}%</span></div><div class="vbet-item"><label>KELLY</label><span>{k["ku"]:.1f}%</span></div><div class="vbet-item"><label>APOSTAR</label><span class="highlight">${k["s"]:,}</span></div><div class="vbet-item"><label>RETORNO</label><span>${k["r"]:,}</span></div></div></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="nobet"><span class="nobet-badge">✗ SIN VALUE</span><span class="nobet-text">{et} · cuota {cu} · edge {k["edge"]:+.1f}%</span></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TAB 2: EQUIPOS
# ─────────────────────────────────────────────
with tab2:
    st.markdown("### 📈 Fuerza relativa de equipos")
    if hist:
        M2 = hist if isinstance(hist, dict) else build_model(hist, li["avg"])
        data=sorted([(e,v) for e,v in M2.items() if e!="_avg" and isinstance(v,dict) and v.get("n",0)>=1],key=lambda x:-x[1]["atk"])
        for eq,v in data:
            c1,c2,c3,c4=st.columns([3,2,2,1])
            with c1: st.markdown(f"**{eq}**")
            with c2: st.markdown(f'<span style="color:{"#22c55e" if v["atk"]>1 else "#f87171"}">Ataque: {v["atk"]:.3f}</span>',unsafe_allow_html=True)
            with c3: st.markdown(f'<span style="color:{"#22c55e" if v["def"]<1 else "#f87171"}">Defensa: {v["def"]:.3f}</span>',unsafe_allow_html=True)
            with c4: st.markdown(f'<span style="color:#64748b">{v["n"]}p</span>',unsafe_allow_html=True)
        st.caption("Ataque > 1.0 = mejor que la media · Defensa < 1.0 = mejor que la media")
    else:
        st.info("Conecta tu API key y selecciona una liga para ver el modelo de equipos.")

# ─────────────────────────────────────────────
# TAB 3: MIS APUESTAS
# ─────────────────────────────────────────────
with tab3:
    st.markdown("### 💰 Tracker de apuestas")
    st.caption("El stake se descuenta del bankroll al registrar. Al ganar se acredita el retorno completo.")

    with st.expander("➕ Registrar nueva apuesta",expanded=False):
        r1,r2=st.columns(2)
        with r1:
            np=st.text_input("Partido",placeholder="Ej: Nacional vs Millonarios",key="np")
            na=st.text_input("Apuesta",placeholder="Local / Empate / Visitante",key="na")
        with r2:
            nc=st.number_input("Cuota",1.01,50.0,2.00,0.05,format="%.2f",key="nc")
            ns=st.number_input("Stake (COP)",100,1000000,1000,100,key="ns")
        nr=st.selectbox("Resultado",["pending","won","lost"],key="nr",
            format_func=lambda x:{"pending":"⏳ Pendiente","won":"✓ Ganó","lost":"✗ Perdió"}[x])
        if st.button("Registrar apuesta",type="primary"):
            if np and na:
                # Stake sale del bankroll al apostar
                st.session_state.bankroll-=ns
                if nr=="won":
                    ret=round(ns*nc); st.session_state.bankroll+=ret
                    st.session_state.wins+=1; ganancia=ret-ns
                elif nr=="lost":
                    st.session_state.losses+=1; ganancia=-ns
                else:
                    ganancia=0  # pendiente — retorno por confirmar
                st.session_state.apuestas.append({"partido":np,"apuesta":na,"cuota":nc,"stake":ns,"resultado":nr,"ganancia":ganancia})
                st.success(f"✓ Registrada. Bankroll disponible: ${st.session_state.bankroll:,} COP")
                st.rerun()

    # Pendientes
    pend=[(i,a) for i,a in enumerate(st.session_state.apuestas) if a["resultado"]=="pending"]
    if pend:
        st.divider()
        st.markdown("**⏳ Pendientes — confirma el resultado:**")
        for i,ap in pend:
            c1,c2,c3=st.columns([4,1,1])
            with c1:
                ret_pot=round(ap["stake"]*ap["cuota"])
                st.markdown(f'<div class="bet-row bet-pend"><b>{ap["partido"]}</b> · {ap["apuesta"]} · cuota {ap["cuota"]}<br><span style="color:#94a3b8;font-size:0.8rem">Stake descontado: ${ap["stake"]:,} · Retorno si gana: ${ret_pot:,}</span></div>',unsafe_allow_html=True)
            with c2:
                if st.button("✓ Ganó",key=f"w_{i}",type="primary"):
                    ret=round(ap["stake"]*ap["cuota"]); g=ret-ap["stake"]
                    st.session_state.apuestas[i].update({"resultado":"won","ganancia":g})
                    st.session_state.bankroll+=ret; st.session_state.wins+=1; st.rerun()
            with c3:
                if st.button("✗ Perdió",key=f"l_{i}"):
                    # Stake ya descontado al registrar
                    st.session_state.apuestas[i].update({"resultado":"lost","ganancia":-ap["stake"]})
                    st.session_state.losses+=1; st.rerun()

    st.divider()
    st.markdown("**📋 Historial:**")
    tw=sum(a["ganancia"] for a in st.session_state.apuestas if a["resultado"]=="won")
    tl=sum(a["stake"] for a in st.session_state.apuestas if a["resultado"]=="lost")
    ta=sum(a["stake"] for a in st.session_state.apuestas)
    for ap in reversed(st.session_state.apuestas):
        cl={"won":"bet-won","lost":"bet-lost","pending":"bet-pend"}.get(ap["resultado"],"")
        ic={"won":"✓","lost":"✗","pending":"⏳"}.get(ap["resultado"],"")
        co={"won":"#22c55e","lost":"#f87171","pending":"#f59e0b"}.get(ap["resultado"],"")
        gs=f'+${ap["ganancia"]:,}' if ap["resultado"]=="won" else (f'-${ap["stake"]:,}' if ap["resultado"]=="lost" else "pendiente")
        st.markdown(f'<div class="bet-row {cl}"><div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;"><div><b>{ap["partido"]}</b> · {ap["apuesta"]} · cuota {ap["cuota"]}</div><span style="color:{co};font-weight:700">{ic} {gs}</span></div><div style="color:#64748b;font-size:0.8rem;margin-top:4px">Stake: ${ap["stake"]:,}</div></div>',unsafe_allow_html=True)

    roi=round((tw-tl)/max(ta,1)*100,1)
    st.markdown(f'<div class="card" style="margin-top:16px"><div style="display:flex;gap:28px;flex-wrap:wrap;"><div><div class="card-label">Total apostado</div><div class="card-value" style="font-size:1rem">${ta:,}</div></div><div><div class="card-label">Total ganado</div><div class="card-value" style="font-size:1rem;color:#22c55e">+${tw:,}</div></div><div><div class="card-label">Total perdido</div><div class="card-value" style="font-size:1rem;color:#f87171">-${tl:,}</div></div><div><div class="card-label">ROI</div><div class="card-value" style="font-size:1rem;color:#38bdf8">{roi}%</div></div></div></div>',unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TAB 4: CASOS DE ESTUDIO
# ─────────────────────────────────────────────
with tab4:
    st.markdown("### 📋 Registro de casos de estudio")
    casos=[
        {"n":1,"partido":"Atlético Nacional 5-1 Inter Bogotá","fecha":"12 mayo 2026","liga":"Liga BetPlay","ap":"Local","cuota":2.85,"edge":"+29.1%","stake":"$6,754","res":"✓ GANÓ","gan":"+$13,195","lec":"El 0-1 al min 15 era ruido estadístico. El modelo mantuvo su señal y acertó. No dejarse llevar por el marcador en vivo."},
        {"n":2,"partido":"Santa Fe 2-1 América de Cali","fecha":"12 mayo 2026","liga":"Liga BetPlay","ap":"Local","cuota":2.23,"edge":"+8.1%","stake":"$2,405","res":"✓ GANÓ","gan":"+$2,958","lec":"Edge moderado con muestra confiable y vig bajo (4.56%) es más sólido que edge alto con poca muestra."},
        {"n":3,"partido":"Valencia 0-0 Rayo Vallecano","fecha":"14 mayo 2026","liga":"La Liga","ap":"Empate","cuota":3.05,"edge":"+5.1%","stake":"$1,060","res":"✓ GANÓ","gan":"+$2,183","lec":"Partido cerrado. El 0-0 fue el marcador más probable del modelo (22.1%)."},
        {"n":4,"partido":"Girona 1-1 Real Sociedad","fecha":"14 mayo 2026","liga":"La Liga","ap":"Empate","cuota":3.65,"edge":"+8.9%","stake":"$1,142","res":"✓ GANÓ","gan":"+$3,026","lec":"Se rechazó cash out de $2,000 con marcador 0-1. El empate llegó y se cobró $4,168. No hacer cash out cuando el modelo sigue siendo válido."},
        {"n":5,"partido":"Real Madrid vs Real Oviedo","fecha":"14 mayo 2026","liga":"La Liga","ap":"Local","cuota":1.24,"edge":"+10.7%","stake":"$3,336","res":"✓ GANÓ","gan":"+$801","lec":"¼ Kelly fue la decisión correcta para no inmovilizar capital en cuota baja con poco retorno por dólar."},
        {"n":6,"partido":"Aston Villa vs Liverpool","fecha":"15 mayo 2026","liga":"Premier League","ap":"Visitante","cuota":2.40,"edge":"-3.7% modelo / +H2H","stake":"$1,000","res":"⏳ PENDIENTE","gan":"pendiente","lec":"Primera apuesta basada en H2H (Liverpool 34-11 sobre Villa históricamente) por encima del modelo. Caso de estudio: modelo vs contexto."},
    ]
    for c in casos:
        co="#22c55e" if "GANÓ" in c["res"] else ("#f59e0b" if "PENDIENTE" in c["res"] else "#f87171")
        st.markdown(f"""
        <div class="caso">
            <div class="caso-meta">CASO #{c['n']} · {c['fecha']} · {c['liga']}</div>
            <div class="caso-title">{c['partido']}</div>
            <div class="caso-chips">
                <span>🎯 {c['ap']}</span>
                <span>📊 Cuota {c['cuota']}</span>
                <span>📈 Edge {c['edge']}</span>
                <span>💰 Stake {c['stake']}</span>
                <span style="color:{co};font-weight:700">{c['res']} · {c['gan']}</span>
            </div>
            <div class="caso-lesson">💡 {c['lec']}</div>
        </div>""",unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TENIS — Fixtures Roland Garros desde The Odds API
# ─────────────────────────────────────────────
@st.cache_data(ttl=1800)
def roland_garros_fixtures(odds_api_key, tour="atp"):
    """
    Obtiene partidos de Roland Garros desde The Odds API.
    odds_key: tennis_atp_french_open | tennis_wta_french_open
    """
    odds_key = f"tennis_{tour}_french_open"
    url = f"https://api.the-odds-api.com/v4/sports/{odds_key}/odds/"
    params = {
        "apiKey": odds_api_key,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal",
        "dateFormat": "iso",
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        TZ_COL = ZoneInfo("America/Bogota")
        ahora = datetime.datetime.now(TZ_COL)
        partidos = []
        for evento in data:
            dt_utc = datetime.datetime.fromisoformat(evento["commence_time"].replace("Z","+00:00"))
            dt_col = dt_utc.astimezone(TZ_COL)
            # Mostrar partidos de hoy y mañana
            dias_diff = (dt_col.date() - ahora.date()).days
            if dias_diff < 0 or dias_diff > 1: continue
            j1 = evento.get("home_team","")
            j2 = evento.get("away_team","")
            # Extraer cuotas
            q1, q2 = None, None
            for bm in evento.get("bookmakers",[]):
                for mkt in bm.get("markets",[]):
                    if mkt["key"]=="h2h":
                        outs = {o["name"]:o["price"] for o in mkt.get("outcomes",[])}
                        q1 = outs.get(j1)
                        q2 = outs.get(j2)
                        break
                if q1: break
            hoy = dias_diff == 0
            partidos.append({
                "j1": j1, "j2": j2,
                "dt": dt_col,
                "hora": dt_col.strftime("%I:%M %p"),
                "q1": q1, "q2": q2,
                "hoy": hoy,
                "tour": tour.upper(),
            })
        partidos.sort(key=lambda x: x["dt"])
        return partidos, None
    except Exception as ex:
        return [], str(ex)


with tab5:
    st.markdown("### 🎾 Análisis de tenis — Modelo Elo por superficie")

    t1, t2 = st.columns(2)
    with t1:
        tour = st.selectbox("Tour", ["ATP (masculino)", "WTA (femenino)"], key="tour_sel")
        tour_key = "atp" if "ATP" in tour else "wta"
    with t2:
        sup_index = ["Hard","Clay","Grass"].index(st.session_state.pop("forzar_clay_val","Hard")) if "forzar_clay_val" in st.session_state else 0
        if st.session_state.pop("forzar_clay", False):
            sup_index = 1  # Clay
        superficie = st.selectbox("Superficie", ["Hard", "Clay", "Grass"], index=sup_index, key="sup_sel",
                                   format_func=lambda x:{"Hard":"Pista dura","Clay":"Arcilla","Grass":"Hierba"}[x])

    with st.spinner(f"Cargando datos {tour} 2026 desde GitHub..."):
        elo_g, elo_s, err_elo = calcular_elo_tenis(tour_key)

    if err_elo:
        st.warning(f"Error cargando datos: {err_elo}")
    elif elo_g:
        st.success(f"✓ {len(elo_g)} jugadores cargados · Elo calculado con partidos 2026")

        # ── Fixtures Roland Garros ──────────────────────────────
        st.markdown("---")
        st.markdown("#### 🇫🇷 Roland Garros 2026 — Partidos hoy y mañana")
        if odds_api_key:
            with st.spinner("Cargando partidos Roland Garros..."):
                rg_partidos, rg_err = roland_garros_fixtures(odds_api_key, tour_key)
            if rg_err:
                st.warning(f"Error cargando fixtures: {rg_err}")
            elif not rg_partidos:
                st.info("No hay partidos programados para hoy/mañana en Roland Garros o la API no tiene datos aún.")
            else:
                # Aviso superficie
                if superficie != "Clay":
                    st.warning("⚠️ Roland Garros se juega en **Arcilla (Clay)**. Cambia la superficie arriba para resultados correctos.")
                TZ_COL = ZoneInfo("America/Bogota")
                ahora = datetime.datetime.now(TZ_COL)
                for p in rg_partidos:
                    etiqueta = "HOY" if p["hoy"] else "MAÑANA"
                    color = "#22c55e" if p["hoy"] else "#f59e0b"
                    q1_str = f"{p['q1']:.2f}" if p.get("q1") else "—"
                    q2_str = f"{p['q2']:.2f}" if p.get("q2") else "—"
                    # Buscar Elo de ambos jugadores SIEMPRE en arcilla
                    j1_elo = buscar_jugador(p["j1"], elo_g)
                    j2_elo = buscar_jugador(p["j2"], elo_g)
                    if j1_elo and j2_elo:
                        e1 = elo_s.get(j1_elo,{}).get("Clay", elo_g.get(j1_elo,1500))
                        e2 = elo_s.get(j2_elo,{}).get("Clay", elo_g.get(j2_elo,1500))
                        pr1 = prob_elo(e1, e2)
                        pr2 = 1 - pr1
                        elo_badge = f"🎯 Elo arcilla: **{p['j1'].split()[-1]} {pr1*100:.0f}%** / **{p['j2'].split()[-1]} {pr2*100:.0f}%**"
                    else:
                        elo_badge = "Jugadores no encontrados en base Elo"
                    with st.expander(f"🎾 {p['j1']} vs {p['j2']} · {p['hora']} COT · {etiqueta}", expanded=False):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.markdown(f"**{p['j1']}**")
                            st.markdown(f"Cuota: `{q1_str}`")
                        with col2:
                            st.markdown(f"<span style='color:{color};font-weight:700'>{etiqueta}</span>", unsafe_allow_html=True)
                            st.markdown(elo_badge)
                        with col3:
                            st.markdown(f"**{p['j2']}**")
                            st.markdown(f"Cuota: `{q2_str}`")
                        # Botón para cargar en el analizador — fuerza Clay
                        if st.button(f"Analizar con modelo Elo →", key=f"rg_{p['j1']}_{p['j2']}"):
                            st.session_state["j1"] = p["j1"].split()[-1]
                            st.session_state["j2"] = p["j2"].split()[-1]
                            if p.get("q1"): st.session_state["tq1"] = p["q1"]
                            if p.get("q2"): st.session_state["tq2"] = p["q2"]
                            st.session_state["forzar_clay"] = True
                            st.rerun()
        else:
            st.info("Configura tu The Odds API key en el sidebar para ver los partidos de Roland Garros.")

        # ── Analizador manual ──────────────────────────────────
        st.markdown("---")
        st.markdown("#### Ingresa los dos jugadores a analizar")
        c1, c2 = st.columns(2)
        with c1:
            j1_input = st.text_input("Jugador 1 (local/favorito)", placeholder="Ej: Sinner", key="j1")
        with c2:
            j2_input = st.text_input("Jugador 2 (visitante)", placeholder="Ej: Alcaraz", key="j2")

        st.markdown("#### Cuotas de tu casa de apuestas")
        c1, c2 = st.columns(2)
        with c1:
            q1 = st.number_input("Cuota jugador 1", 1.01, 50.0, 2.00, 0.05, format="%.2f", key="tq1")
        with c2:
            q2 = st.number_input("Cuota jugador 2", 1.01, 50.0, 2.00, 0.05, format="%.2f", key="tq2")

        if j1_input and j2_input:
            j1 = buscar_jugador(j1_input, elo_g)
            j2 = buscar_jugador(j2_input, elo_g)

            if not j1:
                st.error(f"No se encontró '{j1_input}' en los datos 2026. Verifica el nombre.")
            elif not j2:
                st.error(f"No se encontró '{j2_input}' en los datos 2026. Verifica el nombre.")
            else:
                e1 = elo_s.get(j1,{}).get(superficie, elo_g.get(j1,1500))
                e2 = elo_s.get(j2,{}).get(superficie, elo_g.get(j2,1500))
                p1 = prob_elo(e1, e2)
                p2 = 1 - p1

                # Probabilidades
                st.markdown("---")
                st.markdown(f"#### {j1} vs {j2} — {{'Hard':'Pista dura','Clay':'Arcilla','Grass':'Hierba'}}[superficie]")
                ca, cb = st.columns(2)
                with ca:
                    st.markdown(f"""<div class="prob-wrap">
                        <div class="card-label">{j1}</div>
                        <div class="card-value">{p1*100:.1f}%</div>
                        <div class="prob-bar"><div style="width:{p1*100}%;height:10px;background:#38bdf8;border-radius:6px;"></div></div>
                    </div>""", unsafe_allow_html=True)
                with cb:
                    st.markdown(f"""<div class="prob-wrap">
                        <div class="card-label">{j2}</div>
                        <div class="card-value">{p2*100:.1f}%</div>
                        <div class="prob-bar"><div style="width:{p2*100}%;height:10px;background:#818cf8;border-radius:6px;"></div></div>
                    </div>""", unsafe_allow_html=True)

                # Memoria de calculo
                with st.expander("📊 Memoria de cálculo Elo", expanded=False):
                    st.markdown(f"**Elo {j1}** — General: `{elo_g[j1]:.0f}` | {superficie}: `{e1:.0f}`")
                    st.markdown(f"**Elo {j2}** — General: `{elo_g[j2]:.0f}` | {superficie}: `{e2:.0f}`")
                    st.markdown("---")
                    st.markdown(f"**Fórmula:** `P({j1}) = 1 / (1 + 10^((Elo_{j2} - Elo_{j1}) / 400))`")
                    st.markdown(f"**Cálculo:** `1 / (1 + 10^(({e2:.0f} - {e1:.0f}) / 400))` = **{p1*100:.1f}%**")
                    st.markdown("---")
                    st.markdown("**Todos los ratings por superficie:**")
                    for j,e in [(j1,elo_s.get(j1,{})),(j2,elo_s.get(j2,{}))]:
                        st.markdown(f"  {j}: Pista dura `{e.get('Hard',1500):.0f}` · Arcilla `{e.get('Clay',1500):.0f}` · Hierba `{e.get('Grass',1500):.0f}`")

                # Veredicto Kelly
                st.markdown("#### Veredicto del modelo")
                vig = round(((1/q1 + 1/q2) - 1)*100, 2)
                if vig <= 7:
                    st.markdown(f'<div class="vig-ok">✓ Vig: {vig}% — mercado limpio</div>', unsafe_allow_html=True)
                elif vig <= 12:
                    st.markdown(f'<div class="vig-warn">⚠️ Vig: {vig}% — margen alto</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="vig-bad">✗ Vig: {vig}% — evitar</div>', unsafe_allow_html=True)

                for nombre, prob, cuota in [(j1,p1,q1),(j2,p2,q2)]:
                    b = cuota-1; fc = (prob*b-(1-prob))/b
                    fu = fc*kf if fc>0 else 0
                    s = round(bank*fu)
                    edge = round((prob - 1/cuota)*100, 2)
                    ev = round(prob*b-(1-prob), 4)
                    if fc > ue:
                        st.markdown(f"""<div class="vbet">
                            <span class="vbet-badge">✓ VALUE BET</span>
                            <div class="vbet-title">{nombre} · cuota {cuota}</div>
                            <div class="vbet-grid">
                                <div class="vbet-item"><label>P ELO</label><span>{prob*100:.1f}%</span></div>
                                <div class="vbet-item"><label>P IMPLÍCITA</label><span>{round(1/cuota*100,1)}%</span></div>
                                <div class="vbet-item"><label>EDGE</label><span style="color:#4ade80">+{edge:.1f}%</span></div>
                                <div class="vbet-item"><label>KELLY</label><span>{round(fu*100,2):.1f}%</span></div>
                                <div class="vbet-item"><label>APOSTAR</label><span class="highlight">${s:,}</span></div>
                                <div class="vbet-item"><label>RETORNO</label><span>${round(s*cuota):,}</span></div>
                                <div class="vbet-item"><label>EV/$1</label><span>+{ev:.3f}</span></div>
                            </div>
                        </div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""<div class="nobet">
                            <span class="nobet-badge">✗ SIN VALUE</span>
                            <span class="nobet-text">{nombre} · cuota {cuota} · edge {edge:+.1f}%</span>
                        </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### Top 15 jugadores por Elo 2026")
        top15 = sorted([(j,v) for j,v in elo_g.items()], key=lambda x:-x[1])[:15]
        for i,(j,eg) in enumerate(top15,1):
            hard = elo_s.get(j,{}).get("Hard",1500)
            clay = elo_s.get(j,{}).get("Clay",1500)
            grass = elo_s.get(j,{}).get("Grass",1500)
            c1,c2,c3,c4,c5 = st.columns([3,2,2,2,1])
            with c1: st.markdown(f"**{i}. {j}**")
            with c2: st.markdown(f'<span style="color:#e8eeff">General: {eg:.0f}</span>', unsafe_allow_html=True)
            with c3: st.markdown(f'<span style="color:#f59e0b">Arcilla: {clay:.0f}</span>', unsafe_allow_html=True)
            with c4: st.markdown(f'<span style="color:#38bdf8">Dura: {hard:.0f}</span>', unsafe_allow_html=True)
            with c5: st.markdown(f'<span style="color:#86efac">H: {grass:.0f}</span>', unsafe_allow_html=True)

# ════════════════════════════════════════════
# TAB 6 — AMISTOSOS INTERNACIONALES FIFA
# ════════════════════════════════════════════
with tab6:
    st.markdown("### 🌍 Amistosos Internacionales FIFA")
    st.caption("Modelo Elo de selecciones + Modelo Poisson histórico. Tú decides cuál usar.")

    if not rf_key:
        st.warning("⚠️ Configura tu API-Football key en Streamlit Secrets para ver los partidos automáticamente.")
    else:
        # Cargar Elo de selecciones
        with st.spinner("Cargando ratings Elo de selecciones..."):
            elo_sel, err_elo_sel = cargar_elo_selecciones()

        if err_elo_sel:
            st.info(f"ℹ️ {err_elo_sel}")

        col_e1, col_e2 = st.columns(2)
        with col_e1:
            st.metric("Selecciones en base Elo", len(elo_sel))
        with col_e2:
            st.metric("Fuente", "eloratings.net")

        # Cargar partidos del día
        st.markdown("---")
        dias_vista = st.slider("Días hacia adelante", 1, 5, 3, key="ami_dias")

        with st.spinner("Cargando amistosos desde API-Football..."):
            amistosos, err_ami = get_amistosos_hoy(rf_key, dias_vista)

        if err_ami:
            st.warning(f"Error cargando amistosos: {err_ami}")

        if not amistosos:
            st.info("No hay amistosos internacionales programados en los próximos días.")
        else:
            # Separar por día
            TZ_COL = ZoneInfo("America/Bogota")
            ahora_ami = datetime.datetime.now(TZ_COL)
            fechas_ami = sorted(set(p["fecha"] for p in amistosos))

            st.success(f"✓ {len(amistosos)} amistosos encontrados")

            for fecha_ami in fechas_ami:
                partidos_dia = [p for p in amistosos if p["fecha"] == fecha_ami]
                dias_diff_ami = (datetime.datetime.strptime(fecha_ami, "%Y-%m-%d").date() - ahora_ami.date()).days
                if dias_diff_ami == 0:
                    label_ami = f"🔴 HOY · {fecha_ami}"
                elif dias_diff_ami == 1:
                    label_ami = f"🟡 MAÑANA · {fecha_ami}"
                else:
                    label_ami = f"📅 {fecha_ami}"

                st.markdown(f'<div style="font-family:var(--mono);font-size:11px;color:var(--text3);letter-spacing:0.1em;text-transform:uppercase;margin:1.5rem 0 0.5rem;border-bottom:1px solid var(--border);padding-bottom:6px;">{label_ami}</div>', unsafe_allow_html=True)

                for p in partidos_dia:
                    loc_name = p["local"]
                    vis_name = p["visit"]

                    # Buscar Elo de cada selección
                    elo_loc = buscar_elo(loc_name, elo_sel)
                    elo_vis = buscar_elo(vis_name, elo_sel)

                    # Calcular probabilidades Elo
                    if elo_loc and elo_vis:
                        pl_elo, pe_elo, pv_elo = prob_elo_selecciones(elo_loc, elo_vis, es_neutral=True)
                        elo_ok = True
                    else:
                        pl_elo = pe_elo = pv_elo = None
                        elo_ok = False

                    titulo = f"⚽ {loc_name} vs {vis_name} · {p['hora']} COT"
                    if p.get("ya_jugado") and p.get("gol_loc") is not None:
                        titulo += f" · {p['gol_loc']}-{p['gol_vis']}"

                    with st.expander(titulo, expanded=p["hoy"]):
                        # Info del partido
                        if p.get("venue"):
                            st.caption(f"📍 {p['venue']}, {p['city']}")

                        # Cuotas manuales
                        st.markdown("**Cuotas de tu casa de apuestas:**")
                        cq1, cq2, cq3 = st.columns(3)
                        with cq1: ql_ami = st.number_input(f"Local ({loc_name[:12]})", 1.01, 50.0, 2.00, 0.05, format="%.2f", key=f"ami_ql_{p['id']}")
                        with cq2: qe_ami = st.number_input("Empate", 1.01, 50.0, 3.20, 0.05, format="%.2f", key=f"ami_qe_{p['id']}")
                        with cq3: qv_ami = st.number_input(f"Visit ({vis_name[:12]})", 1.01, 50.0, 3.80, 0.05, format="%.2f", key=f"ami_qv_{p['id']}")

                        st.markdown("---")

                        # ── MODELO ELO ──────────────────────────────
                        st.markdown("#### 🎯 Modelo Elo (eloratings.net)")
                        if elo_ok:
                            ce1, ce2, ce3, ce4 = st.columns(4)
                            with ce1:
                                st.markdown(f"**{loc_name[:15]}**")
                                st.markdown(f"Elo: `{elo_loc}`")
                            with ce2:
                                color_l = "#22c55e" if pl_elo > 0.45 else "#94a3b8"
                                st.markdown(f'<div style="text-align:center"><div style="font-size:11px;color:var(--text3);">LOCAL GANA</div><div style="font-size:28px;font-weight:700;color:{color_l};">{pl_elo*100:.1f}%</div></div>', unsafe_allow_html=True)
                            with ce3:
                                st.markdown(f'<div style="text-align:center"><div style="font-size:11px;color:var(--text3);">EMPATE</div><div style="font-size:28px;font-weight:700;color:#f59e0b;">{pe_elo*100:.1f}%</div></div>', unsafe_allow_html=True)
                            with ce4:
                                color_v = "#22c55e" if pv_elo > 0.45 else "#94a3b8"
                                st.markdown(f'<div style="text-align:center"><div style="font-size:11px;color:var(--text3);">VISIT GANA</div><div style="font-size:28px;font-weight:700;color:{color_v};">{pv_elo*100:.1f}%</div></div>', unsafe_allow_html=True)

                            st.markdown(f"**{vis_name[:15]}**")
                            st.markdown(f"Elo: `{elo_vis}`")

                            # Diferencia de Elo
                            diff_elo = elo_loc - elo_vis
                            ventaja = loc_name if diff_elo > 0 else vis_name
                            st.caption(f"Diferencia Elo: {abs(diff_elo)} pts → {ventaja} es más fuerte históricamente")
                        else:
                            st.info(f"⚠️ Elo no disponible para: {'' if elo_loc else loc_name} {'' if elo_vis else vis_name}")

                        # ── MODELO POISSON ──────────────────────────
                        st.markdown("#### 📊 Modelo Poisson (últimos partidos)")

                        # Inputs manuales de estadísticas si no hay API
                        cp1, cp2 = st.columns(2)
                        with cp1:
                            st.markdown(f"**{loc_name[:20]}**")
                            gf_loc_p = st.number_input("Goles/partido (ataque)", 0.1, 5.0, 1.5, 0.1, key=f"gf_loc_{p['id']}", help="Promedio goles a favor últimos 10 partidos")
                            gc_loc_p = st.number_input("Goles recibidos/partido", 0.1, 5.0, 1.2, 0.1, key=f"gc_loc_{p['id']}", help="Promedio goles en contra últimos 10 partidos")
                        with cp2:
                            st.markdown(f"**{vis_name[:20]}**")
                            gf_vis_p = st.number_input("Goles/partido (ataque)", 0.1, 5.0, 1.3, 0.1, key=f"gf_vis_{p['id']}", help="Promedio goles a favor últimos 10 partidos")
                            gc_vis_p = st.number_input("Goles recibidos/partido", 0.1, 5.0, 1.3, 0.1, key=f"gc_vis_{p['id']}", help="Promedio goles en contra últimos 10 partidos")

                        pl_poi, pe_poi, pv_poi = poisson_seleccion(gf_loc_p, gc_loc_p, gf_vis_p, gc_vis_p)

                        if pl_poi:
                            cp1b, cp2b, cp3b = st.columns(3)
                            with cp1b:
                                color_lp = "#22c55e" if pl_poi > 0.45 else "#94a3b8"
                                st.markdown(f'<div style="text-align:center"><div style="font-size:11px;color:var(--text3);">LOCAL</div><div style="font-size:24px;font-weight:700;color:{color_lp};">{pl_poi*100:.1f}%</div></div>', unsafe_allow_html=True)
                            with cp2b:
                                st.markdown(f'<div style="text-align:center"><div style="font-size:11px;color:var(--text3);">EMPATE</div><div style="font-size:24px;font-weight:700;color:#f59e0b;">{pe_poi*100:.1f}%</div></div>', unsafe_allow_html=True)
                            with cp3b:
                                color_vp = "#22c55e" if pv_poi > 0.45 else "#94a3b8"
                                st.markdown(f'<div style="text-align:center"><div style="font-size:11px;color:var(--text3);">VISITANTE</div><div style="font-size:24px;font-weight:700;color:{color_vp};">{pv_poi*100:.1f}%</div></div>', unsafe_allow_html=True)

                        # ── VEREDICTO COMBINADO ─────────────────────
                        st.markdown("---")
                        st.markdown("#### ⚖️ Tu decisión")

                        modelo_usar = st.radio(
                            "¿Con qué modelo quieres calcular el value?",
                            ["Elo", "Poisson", "Promedio de ambos"],
                            horizontal=True,
                            key=f"modelo_{p['id']}"
                        )

                        if modelo_usar == "Elo" and elo_ok:
                            pl_f, pe_f, pv_f = pl_elo, pe_elo, pv_elo
                        elif modelo_usar == "Poisson" and pl_poi:
                            pl_f, pe_f, pv_f = pl_poi, pe_poi, pv_poi
                        elif elo_ok and pl_poi:
                            pl_f = round((pl_elo + pl_poi)/2, 4)
                            pe_f = round((pe_elo + pe_poi)/2, 4)
                            pv_f = round((pv_elo + pv_poi)/2, 4)
                        elif elo_ok:
                            pl_f, pe_f, pv_f = pl_elo, pe_elo, pv_elo
                        elif pl_poi:
                            pl_f, pe_f, pv_f = pl_poi, pe_poi, pv_poi
                        else:
                            pl_f = pe_f = pv_f = None

                        if pl_f:
                            im_ami = impl({"local": ql_ami, "empate": qe_ami, "visit": qv_ami})
                            vig_ami = im_ami["vig"]
                            if vig_ami <= 7:
                                st.markdown(f'<div class="vig-ok">✓ Vig: {vig_ami}% — mercado limpio</div>', unsafe_allow_html=True)
                            elif vig_ami <= 12:
                                st.markdown(f'<div class="vig-warn">⚠️ Vig: {vig_ami}%</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="vig-bad">✗ Vig: {vig_ami}% — mercado caro</div>', unsafe_allow_html=True)

                            st.markdown("**Veredicto:**")
                            for nm, pm_f, cu, et in [
                                ("local", pl_f, ql_ami, loc_name),
                                ("empate", pe_f, qe_ami, "Empate"),
                                ("visit", pv_f, qv_ami, vis_name)
                            ]:
                                k = kelly_calc(pm_f, cu, kf, bank, ue)
                                if k["value"]:
                                    st.markdown(f'<div class="vbet"><span class="vbet-badge">✓ VALUE BET</span><div class="vbet-title">{et} · cuota {cu}</div><div class="vbet-grid"><div class="vbet-item"><label>P MODELO</label><span>{pm_f*100:.1f}%</span></div><div class="vbet-item"><label>P IMPLÍCITA</label><span>{im_ami["p"].get(nm,0)*100:.1f}%</span></div><div class="vbet-item"><label>EDGE</label><span style="color:#4ade80">+{k["edge"]:.1f}%</span></div><div class="vbet-item"><label>KELLY</label><span>{k["ku"]:.1f}%</span></div><div class="vbet-item"><label>APOSTAR</label><span class="highlight">${k["s"]:,}</span></div><div class="vbet-item"><label>RETORNO</label><span>${k["r"]:,}</span></div></div></div>', unsafe_allow_html=True)
                                else:
                                    st.markdown(f'<div class="nobet"><span class="nobet-badge">✗ SIN VALUE</span><span class="nobet-text">{et} · cuota {cu} · edge {k["edge"]:+.1f}%</span></div>', unsafe_allow_html=True)

        # ── Analizador manual de selecciones ────────────────────
        st.markdown("---")
        st.markdown("### 🔍 Analizar cualquier partido manualmente")
        st.caption("Busca la selección escribiendo su nombre — el desplegable filtra automáticamente.")

        # Lista completa de selecciones ordenadas por nombre
        sel_lista = sorted(elo_sel.keys())
        opciones = ["— Selecciona —"] + sel_lista

        cm1, cm2 = st.columns(2)
        with cm1:
            sel_local_m = st.selectbox(
                "🏠 Selección local",
                opciones,
                index=0,
                key="man_loc",
                help="Escribe para filtrar"
            )
            if sel_local_m == "— Selecciona —":
                sel_local_m = ""
        with cm2:
            sel_visit_m = st.selectbox(
                "✈️ Selección visitante",
                opciones,
                index=0,
                key="man_vis",
                help="Escribe para filtrar"
            )
            if sel_visit_m == "— Selecciona —":
                sel_visit_m = ""

        es_neutral_m = st.checkbox("Cancha neutral", value=True, key="man_neutral")

        cqm1, cqm2, cqm3 = st.columns(3)
        with cqm1: ql_m = st.number_input("Cuota local",  1.01, 50.0, 2.00, 0.05, format="%.2f", key="man_ql")
        with cqm2: qe_m = st.number_input("Cuota empate", 1.01, 50.0, 3.20, 0.05, format="%.2f", key="man_qe")
        with cqm3: qv_m = st.number_input("Cuota visit",  1.01, 50.0, 3.80, 0.05, format="%.2f", key="man_qv")

        if sel_local_m and sel_visit_m:
            elo_loc_m = buscar_elo(sel_local_m, elo_sel)
            elo_vis_m = buscar_elo(sel_visit_m, elo_sel)

            if elo_loc_m and elo_vis_m:
                pl_m, pe_m, pv_m = prob_elo_selecciones(elo_loc_m, elo_vis_m, es_neutral=es_neutral_m)
                diff_m = elo_loc_m - elo_vis_m

                st.markdown("---")
                # Ratings
                c1m, c2m = st.columns(2)
                with c1m:
                    st.metric(f"Elo {sel_local_m}", elo_loc_m)
                with c2m:
                    st.metric(f"Elo {sel_visit_m}", elo_vis_m,
                              delta=f"{abs(diff_m)} pts {'favor local' if diff_m>0 else 'favor visit'}")

                # Probabilidades Elo
                ca, cb, cc = st.columns(3)
                with ca:
                    color = "#22c55e" if pl_m > 0.45 else "#94a3b8"
                    st.markdown(f'<div style="text-align:center"><div style="font-size:11px;color:var(--text3);">LOCAL GANA</div><div style="font-size:32px;font-weight:700;color:{color};">{pl_m*100:.1f}%</div><div style="font-size:11px;color:var(--text3);">Elo</div></div>', unsafe_allow_html=True)
                with cb:
                    st.markdown(f'<div style="text-align:center"><div style="font-size:11px;color:var(--text3);">EMPATE</div><div style="font-size:32px;font-weight:700;color:#f59e0b;">{pe_m*100:.1f}%</div><div style="font-size:11px;color:var(--text3);">Elo</div></div>', unsafe_allow_html=True)
                with cc:
                    color = "#22c55e" if pv_m > 0.45 else "#94a3b8"
                    st.markdown(f'<div style="text-align:center"><div style="font-size:11px;color:var(--text3);">VISIT GANA</div><div style="font-size:32px;font-weight:700;color:{color};">{pv_m*100:.1f}%</div><div style="font-size:11px;color:var(--text3);">Elo</div></div>', unsafe_allow_html=True)

                # Veredicto Kelly
                st.markdown("**Veredicto:**")
                im_m = impl({"local": ql_m, "empate": qe_m, "visit": qv_m})
                vig_m = im_m["vig"]
                if vig_m <= 7:    st.markdown(f'<div class="vig-ok">✓ Vig: {vig_m}%</div>', unsafe_allow_html=True)
                elif vig_m <= 12: st.markdown(f'<div class="vig-warn">⚠️ Vig: {vig_m}%</div>', unsafe_allow_html=True)
                else:             st.markdown(f'<div class="vig-bad">✗ Vig: {vig_m}% — mercado caro</div>', unsafe_allow_html=True)

                for nm, pm_v, cu, et in [
                    ("local", pl_m, ql_m, sel_local_m),
                    ("empate", pe_m, qe_m, "Empate"),
                    ("visit", pv_m, qv_m, sel_visit_m)
                ]:
                    k = kelly_calc(pm_v, cu, kf, bank, ue)
                    if k["value"]:
                        st.markdown(f'<div class="vbet"><span class="vbet-badge">✓ VALUE BET</span><div class="vbet-title">{et} · cuota {cu}</div><div class="vbet-grid"><div class="vbet-item"><label>P ELO</label><span>{pm_v*100:.1f}%</span></div><div class="vbet-item"><label>P IMPLÍCITA</label><span>{im_m["p"].get(nm,0)*100:.1f}%</span></div><div class="vbet-item"><label>EDGE</label><span style="color:#4ade80">+{k["edge"]:.1f}%</span></div><div class="vbet-item"><label>KELLY</label><span>{k["ku"]:.1f}%</span></div><div class="vbet-item"><label>APOSTAR</label><span class="highlight">${k["s"]:,}</span></div><div class="vbet-item"><label>RETORNO</label><span>${k["r"]:,}</span></div></div></div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="nobet"><span class="nobet-badge">✗ SIN VALUE</span><span class="nobet-text">{et} · cuota {cu} · edge {k["edge"]:+.1f}%</span></div>', unsafe_allow_html=True)

            else:
                if not elo_loc_m:
                    st.warning(f"⚠️ '{sel_local_m}' no encontrado. Revisa el nombre en la lista de selecciones disponibles.")
                if not elo_vis_m:
                    st.warning(f"⚠️ '{sel_visit_m}' no encontrado. Revisa el nombre en la lista de selecciones disponibles.")
