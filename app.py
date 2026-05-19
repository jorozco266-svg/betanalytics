"""
BetAnalytics v3
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
API_RF   = "https://v3.football.api-sports.io"
API_TSDB = "https://www.thesportsdb.com/api/v1/json/3"
TZ_COL   = ZoneInfo("America/Bogota")
FL       = 1.15
MG       = 8
BK_INIT  = 35000

# Liga: source indica de dónde se obtienen los datos
# fd = football-data.org | rf = api-football (RapidAPI)
LIGAS = {
    "🇪🇸 La Liga":            {"src":"fd","code":"PD",   "rf_id":140, "avg":1.35},
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League":    {"src":"fd","code":"PL",   "rf_id":39,  "avg":1.40},
    "🇩🇪 Bundesliga":          {"src":"fd","code":"BL1",  "rf_id":78,  "avg":1.55},
    "🇮🇹 Serie A":             {"src":"fd","code":"SA",   "rf_id":135, "avg":1.30},
    "🇫🇷 Ligue 1":             {"src":"fd","code":"FL1",  "rf_id":61,  "avg":1.35},
    "🇵🇹 Primeira Liga":       {"src":"fd","code":"PPL",  "rf_id":94,  "avg":1.30},
    "🏆 Champions League":     {"src":"fd","code":"CL",   "rf_id":2,   "avg":1.45},
    "🇨🇴 Liga BetPlay":        {"src":"tsdb","code":None, "rf_id":239, "tsdb_id":"4497", "avg":1.20},
    "🇨🇴 Torneo BetPlay":      {"src":"tsdb","code":None, "rf_id":240, "tsdb_id":"4951", "avg":1.10},
    "🏆 Copa Libertadores":    {"src":"tsdb","code":None, "rf_id":13,  "tsdb_id":"4351", "avg":1.25},
    "🏆 Copa Sudamericana":    {"src":"tsdb","code":None, "rf_id":11,  "tsdb_id":"4352", "avg":1.20},
    "🇦🇷 Liga Argentina":      {"src":"tsdb","code":None, "rf_id":128, "tsdb_id":"4406", "avg":1.30},
    "🇧🇷 Brasileirao":         {"src":"tsdb","code":None, "rf_id":71,  "tsdb_id":"4351", "avg":1.35},
    "🇲🇽 Liga MX":             {"src":"tsdb","code":None, "rf_id":262, "tsdb_id":"4406", "avg":1.25},
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
    S={e:{"gf":[],"gc":[]} for e in eq}
    for l,v,gl,gv in partidos:
        S[l]["gf"].append(gl);S[l]["gc"].append(gv)
        S[v]["gf"].append(gv);S[v]["gc"].append(gl)
    return {e:{"atk":round((sum(d["gf"])/max(len(d["gf"]),1))/avg,3),
               "def":round((sum(d["gc"])/max(len(d["gc"]),1))/avg,3),
               "n":len(d["gf"])} for e,d in S.items()}

def lams(loc,vis,M,avg):
    ml=M.get(loc,{"atk":1.0,"def":1.0}); mv=M.get(vis,{"atk":1.0,"def":1.0})
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
        r=requests.get(f"{API_FD}/competitions/{code}/matches?status=SCHEDULED",
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
# API — API-Football (RapidAPI) para Suramérica
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600)

@st.cache_data(ttl=900)
def tsdb_hist(tsdb_id):
    """Historial via TheSportsDB (gratuito, sin key)."""
    season=datetime.datetime.now(TZ_COL).year
    url=f"{API_TSDB}/eventsseason.php?id={tsdb_id}&s={season}"
    try:
        r=requests.get(url,timeout=15); r.raise_for_status()
        eventos=r.json().get("events") or []
        out=[]
        for e in eventos:
            if e.get("strStatus")!="Match Finished": continue
            gh=e.get("intHomeScore"); ga=e.get("intAwayScore")
            if gh is None or ga is None: continue
            out.append((e["strHomeTeam"],e["strAwayTeam"],int(gh),int(ga)))
        return out,None
    except Exception as ex: return [],str(ex)

@st.cache_data(ttl=900)
def tsdb_next(tsdb_id):
    """Proximos partidos via TheSportsDB."""
    season=datetime.datetime.now(TZ_COL).year
    url=f"{API_TSDB}/eventsseason.php?id={tsdb_id}&s={season}"
    try:
        r=requests.get(url,timeout=15); r.raise_for_status()
        eventos=r.json().get("events") or []
        out=[]; ahora=datetime.datetime.now(TZ_COL)
        for e in eventos:
            if e.get("strStatus")=="Match Finished": continue
            fs=e.get("dateEvent",""); hs=e.get("strTime","00:00:00")
            if not fs: continue
            try:
                dt_utc=datetime.datetime.strptime(f"{fs} {hs[:5]}","%Y-%m-%d %H:%M").replace(tzinfo=ZoneInfo("UTC"))
                dt=dt_utc.astimezone(TZ_COL)
            except: continue
            if dt<ahora: continue
            lim=(ahora+datetime.timedelta(days=3)).date()
            if dt.date()>lim: continue
            out.append({"id":e.get("idEvent","?"),"dt":dt,"fecha":dt.strftime("%Y-%m-%d"),
                        "hora":dt.strftime("%I:%M %p"),"local":e["strHomeTeam"],"visit":e["strAwayTeam"],
                        "jornada":e.get("intRound","?"),"hoy":es_hoy(dt),"manana":es_manana(dt)})
        out.sort(key=lambda x:x["dt"])
        return out,None
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
# SESSION STATE
# ─────────────────────────────────────────────
def init():
    if "bankroll" not in st.session_state: st.session_state.bankroll=51982
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

tab1,tab2,tab3,tab4=st.tabs(["⚽ Partidos","📈 Equipos","💰 Mis apuestas","📋 Casos de estudio"])

# ─────────────────────────────────────────────
# FUNCIÓN AUXILIAR: RENDER DE PARTIDO
# ─────────────────────────────────────────────
def render_partido(p, M, avg, bank, kf, ue):
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
        # Cuotas
        st.markdown("**Cuotas — actualiza con las de tu casa de apuestas:**")
        c1,c2,c3=st.columns(3)
        with c1: ql=st.number_input("Local",   1.01,50.0,2.00,0.05,key=f"ql_{p['id']}",format="%.2f")
        with c2: qe=st.number_input("Empate",  1.01,50.0,3.30,0.05,key=f"qe_{p['id']}",format="%.2f")
        with c3: qv=st.number_input("Visit",   1.01,50.0,3.80,0.05,key=f"qv_{p['id']}",format="%.2f")

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

    elif li["src"]=="tsdb":
        with st.spinner("Cargando datos de Suramérica y Colombia..."):
            hist,e1=tsdb_hist(li["tsdb_id"])
            prox,e2=tsdb_next(li["tsdb_id"])
        if e1: st.warning(f"Error historial: {e1}")
        if e2: st.warning(f"Error proximos: {e2}")
        cargado=True

    elif li["src"]=="rf" and tiene_rf:
        with st.spinner("Cargando datos de Suramérica..."):
            hist,e1=rf_hist(li["rf_id"],rf_key)
            prox,e2=rf_next(li["rf_id"],rf_key)
        if e1: st.warning(f"Error historial: {e1}")
        if e2: st.warning(f"Error próximos: {e2}")
        cargado=True

    if cargado and hist:
        st.success(f"✓ {len(hist)} partidos históricos · {len(prox)} próximos (próximos 3 días · hora Colombia)")
        M=build_model(hist,li["avg"])
        fechas=sorted(set(p["fecha"] for p in prox))
        if not fechas:
            st.info("No hay partidos en los próximos 3 días para esta liga.")
        for fecha in fechas:
            pf=[p for p in prox if p["fecha"]==fecha]
            if not pf: continue
            dt0=pf[0]["dt"]
            if es_hoy(dt0):    lbl=f"HOY · {dt0.strftime('%A %d de %B').upper()}"; badge='<span class="hoy-pill">HOY</span>'
            elif es_manana(dt0): lbl=f"MAÑANA · {dt0.strftime('%A %d de %B').upper()}"; badge=""
            else:               lbl=dt0.strftime('%A %d de %B').upper(); badge=""
            st.markdown(f'<div class="day-hdr">{lbl}{badge}</div>',unsafe_allow_html=True)
            for p in pf:
                render_partido(p,M,li["avg"],bank,kf,ue)

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
        M=build_model(hist,li["avg"])
        data=sorted([(e,v) for e,v in M.items() if v["n"]>=3],key=lambda x:-x[1]["atk"])
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
