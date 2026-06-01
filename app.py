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
BK_INIT  = 70213

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
    "🇵🇾 Paraguay - Div Prof": {"src":"wiki_tabla","wiki_url":"https://en.wikipedia.org/wiki/2026_Paraguayan_Primera_Divisi%C3%B3n","avg":1.25,"odds_key":None,"use_odds_fixtures":False,"sportsdb_id":4687,"hist_fallback":"Paraguay"},
    "🇵🇪 Perú - Liga 1":       {"src":"wiki_tabla","wiki_url":"https://en.wikipedia.org/wiki/2026_Liga_1_(Peru)","avg":1.20,"odds_key":None,"use_odds_fixtures":False,"sportsdb_id":4688,"hist_fallback":"Peru"},
    "🇪🇨 Ecuador - LigaPro":   {"src":"wiki_tabla","wiki_url":"https://en.wikipedia.org/wiki/2026_LigaPro_Serie_A","avg":1.25,"odds_key":None,"use_odds_fixtures":False,"sportsdb_id":4686,"hist_fallback":"Ecuador"},
    "🇧🇴 Bolivia - Div Prof":  {"src":"wiki_tabla","wiki_url":"https://en.wikipedia.org/wiki/2026_Bolivian_Football_Championship","avg":1.30,"odds_key":None,"use_odds_fixtures":False,"sportsdb_id":4347,"hist_fallback":"Bolivia"},
    "🇻🇪 Venezuela - 1ª Div":  {"src":"wiki_tabla","wiki_url":"https://en.wikipedia.org/wiki/2025%E2%80%9326_Venezuelan_Primera_Divisi%C3%B3n","avg":1.20,"odds_key":None,"use_odds_fixtures":False,"sportsdb_id":4339,"hist_fallback":"Venezuela"},
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
        ("Nacional",               30, 10, 14), ("Peñarol",               28, 12, 14),
        ("Liverpool",              22, 15, 14), ("Defensor Sporting",      20, 16, 14),
        ("Danubio",                18, 17, 14), ("Montevideo City Torque", 17, 17, 14),
        ("Rentistas",              16, 18, 14), ("Fénix",                  15, 19, 14),
        ("Miramar Misiones",       14, 20, 14), ("Deportivo Maldonado",    13, 20, 14),
        ("Cerro Largo",            12, 21, 13), ("Cerro",                  11, 22, 13),
        ("Plaza Colonia",          10, 23, 13), ("Racing",                  9, 24, 13),
        ("Boston River",            8, 25, 13), ("Progreso",                7, 26, 13),
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
        ("Bolívar",               30, 10, 14), ("Always Ready",          26, 12, 14),
        ("The Strongest",         24, 14, 14), ("Oriente Petrolero",     20, 16, 14),
        ("Blooming",              18, 17, 14), ("Royal Pari",            16, 18, 14),
        ("Wilstermann",           15, 19, 14), ("Nacional Potosí",       13, 21, 14),
        ("Aurora",                12, 22, 13), ("Universitario de Sucre",11, 23, 13),
        ("Real Tomayapo",         10, 24, 13), ("Guabirá",                9, 25, 12),
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
# MÓDULO TENIS — Elo por superficie
# ─────────────────────────────────────────────
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
    if "bankroll" not in st.session_state: st.session_state.bankroll=70213
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
    rf_key=st.text_input("API Key — API-Football",type="password",
                          placeholder="Ligas de Suramérica y Colombia",
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

tab1,tab2,tab3,tab4,tab5=st.tabs(["⚽ Partidos","📈 Equipos","💰 Mis apuestas","📋 Casos de estudio","🎾 Tenis"])

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
        # Próximos: The Odds API si disponible, sino TheSportsDB
        if li.get("use_odds_fixtures") and li.get("odds_key") and odds_api_key:
            prox,e2=odds_fixtures(li["odds_key"],odds_api_key)
        elif li.get("sportsdb_id"):
            prox,e2=sportsdb_next(li["sportsdb_id"])
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
            # Semifinales Liga BetPlay hardcoded
            if "Liga BetPlay" in liga_n and not prox_wiki:
                import hashlib
                semis = [
                    ("Atletico Nacional","Deportes Tolima","2026-05-23","06:00 PM"),
                    ("Junior","Independiente Santa Fe","2026-05-23","08:30 PM"),
                ]
                prox_wiki = []
                for loc,vis,fecha,hora in semis:
                    uid=hashlib.md5(f"{loc}{vis}".encode()).hexdigest()[:8]
                    fecha_dt=datetime.datetime.strptime(fecha,"%Y-%m-%d").replace(tzinfo=TZ_COL)
                    prox_wiki.append({"id":uid,"dt":fecha_dt,"fecha":fecha,"hora":hora,
                                      "local":loc,"visit":vis,"jornada":"Semifinal",
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
    else:
        # Modo manual
        st.markdown("### 🖊️ Análisis manual de partido")
        st.caption("Conecta una API key para carga automática, o ingresa los datos manualmente.")
        c1,c2=st.columns(2)
        with c1: eql=st.text_input("Equipo local",   placeholder="Ej: Atlético Nacional")
        with c2: eqv=st.text_input("Equipo visitante",placeholder="Ej: Millonarios")
        c1,c2,c3=st.columns(3)
        with c1: ql=st.number_input("Cuota local",   1.01,50.0,2.00,0.05,format="%.2f",key="m_ql")
        with c2: qe=st.number_input("Cuota empate",  1.01,50.0,3.30,0.05,format="%.2f",key="m_qe")
        with c3: qv=st.number_input("Cuota visit",   1.01,50.0,3.80,0.05,format="%.2f",key="m_qv")
        c1,c2,c3=st.columns(3)
        with c1: pl=st.number_input("P(local) %",  1.0,99.0,45.0,0.5)/100
        with c2: pe=st.number_input("P(empate) %", 1.0,99.0,28.0,0.5)/100
        with c3: pv=st.number_input("P(visit) %",  1.0,99.0,27.0,0.5)/100
        if eql and eqv:
            im=impl({"local":ql,"empate":qe,"visit":qv})
            vig=im["vig"]
            if vig<=7:    st.markdown(f'<div class="vig-ok">✓ Vig: {vig}%</div>',unsafe_allow_html=True)
            elif vig<=12: st.markdown(f'<div class="vig-warn">⚠️ Vig: {vig}%</div>',unsafe_allow_html=True)
            else:         st.markdown(f'<div class="vig-bad">✗ Vig: {vig}%</div>',unsafe_allow_html=True)
            for nm,pm,cu,et in [("local",pl,ql,eql),("empate",pe,qe,"Empate"),("visit",pv,qv,eqv)]:
                pi=im["p"].get(nm,0); k=kelly_calc(pm,cu,kf,bank,ue)
                if k["value"]: st.markdown(f'<div class="vbet"><span class="vbet-badge">✓ VALUE BET</span><div class="vbet-title">{et} · cuota {cu}</div><div class="vbet-grid"><div class="vbet-item"><label>EDGE</label><span style="color:#4ade80">+{k["edge"]:.1f}%</span></div><div class="vbet-item"><label>APOSTAR</label><span class="highlight">${k["s"]:,}</span></div><div class="vbet-item"><label>RETORNO</label><span>${k["r"]:,}</span></div></div></div>',unsafe_allow_html=True)
                else: st.markdown(f'<div class="nobet"><span class="nobet-badge">✗ SIN VALUE</span><span class="nobet-text">{et} · edge {k["edge"]:+.1f}%</span></div>',unsafe_allow_html=True)

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
