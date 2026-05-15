"""
app.py — Dashboard de apuestas deportivas v2
Mejoras: horarios en hora Colombia (UTC-5), tracker de bankroll dinámico.
"""

import math
import datetime
from itertools import product as iproduct
from zoneinfo import ZoneInfo

import streamlit as st
import requests

st.set_page_config(page_title="BetAnalytics", page_icon="⚽", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');
html, body, [class*="css"] { font-family: 'Syne', sans-serif; }
.stApp { background: #0a0f1e; color: #e8eaf0; }
.main-title { font-family:'Syne',sans-serif; font-weight:800; font-size:2.4rem; background:linear-gradient(135deg,#00d4ff,#7b2fff); -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:0; line-height:1.1; }
.subtitle { font-family:'Space Mono',monospace; font-size:0.75rem; color:#4a5568; letter-spacing:0.15em; text-transform:uppercase; margin-top:4px; }
.metric-card { background:#111827; border:1px solid #1e2d40; border-radius:12px; padding:14px 18px; margin-bottom:10px; }
.metric-label { font-size:0.7rem; color:#4a5568; text-transform:uppercase; letter-spacing:0.1em; font-family:'Space Mono',monospace; }
.metric-value { font-size:1.6rem; font-weight:800; color:#e8eaf0; line-height:1.2; }
.value-yes { background:linear-gradient(135deg,#0d2818,#0a3d1f); border:1px solid #16a34a; border-radius:12px; padding:16px 20px; margin-bottom:10px; }
.value-no { background:#111827; border:1px solid #1e2d40; border-radius:12px; padding:14px 18px; margin-bottom:8px; }
.badge-value { background:#16a34a; color:white; font-size:0.7rem; font-weight:700; padding:3px 10px; border-radius:20px; font-family:'Space Mono',monospace; }
.badge-no { background:#374151; color:#9ca3af; font-size:0.7rem; font-weight:700; padding:3px 10px; border-radius:20px; font-family:'Space Mono',monospace; }
.prob-bar-container { background:#1e2d40; border-radius:6px; height:8px; margin-top:6px; overflow:hidden; }
.vig-warning { background:#1a1000; border:1px solid #d97706; border-radius:8px; padding:8px 14px; font-size:0.8rem; color:#d97706; font-family:'Space Mono',monospace; margin:8px 0; }
.vig-ok { background:#0d1a0d; border:1px solid #16a34a; border-radius:8px; padding:8px 14px; font-size:0.8rem; color:#16a34a; font-family:'Space Mono',monospace; margin:8px 0; }
.day-header { font-family:'Space Mono',monospace; font-size:0.75rem; color:#00d4ff; text-transform:uppercase; letter-spacing:0.12em; padding:6px 0; border-bottom:1px solid #1e2d40; margin:20px 0 10px; }
.today-badge { background:#00d4ff; color:#0a0f1e; font-size:0.65rem; font-weight:700; padding:2px 8px; border-radius:10px; margin-left:8px; }
.bet-row { background:#111827; border:1px solid #1e2d40; border-radius:10px; padding:12px 16px; margin-bottom:8px; font-size:0.85rem; }
.bet-won { border-left:3px solid #16a34a; }
.bet-lost { border-left:3px solid #ef4444; }
.bet-pending { border-left:3px solid #d97706; }
.case-study { background:#0d1520; border-left:3px solid #00d4ff; border-radius:0 8px 8px 0; padding:12px 16px; margin-bottom:10px; font-size:0.82rem; }
div[data-testid="stSidebar"] { background:#080d1a; border-right:1px solid #1e2d40; }
</style>
""", unsafe_allow_html=True)

# ── Constantes ──────────────────────────────
API_BASE      = "https://api.football-data.org/v4"
TZ_COL        = ZoneInfo("America/Bogota")
FACTOR_LOCAL  = 1.15
MAX_GOLES     = 8
BANKROLL_INIT = 35000

LIGAS = {
    "🇪🇸 La Liga":         {"code":"PD",  "avg_goles":1.35},
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League":  {"code":"PL",  "avg_goles":1.40},
    "🇩🇪 Bundesliga":       {"code":"BL1", "avg_goles":1.55},
    "🇮🇹 Serie A":          {"code":"SA",  "avg_goles":1.30},
    "🇫🇷 Ligue 1":          {"code":"FL1", "avg_goles":1.35},
    "🇵🇹 Primeira Liga":    {"code":"PPL", "avg_goles":1.30},
    "🏆 Champions League":  {"code":"CL",  "avg_goles":1.45},
}

# ── Utilidades de tiempo ────────────────────
def utc_a_col(s):
    try:
        dt = datetime.datetime.fromisoformat(s.replace("Z","+00:00"))
        return dt.astimezone(TZ_COL)
    except:
        return None

def es_hoy(dt): return dt.date() == datetime.datetime.now(TZ_COL).date()
def es_manana(dt): return dt.date() == (datetime.datetime.now(TZ_COL)+datetime.timedelta(days=1)).date()

# ── Modelo Poisson ──────────────────────────
def fact(n):
    r=1
    for i in range(2,n+1): r*=i
    return r

def pmf(k,lam):
    if lam<=0: return 1.0 if k==0 else 0.0
    return (math.exp(-lam)*(lam**k))/fact(k)

def poisson(lam_l, lam_v):
    pl=pe=pv=0.0; M={}
    for gl,gv in iproduct(range(MAX_GOLES+1),repeat=2):
        p=pmf(gl,lam_l)*pmf(gv,lam_v); M[(gl,gv)]=p
        if gl>gv: pl+=p
        elif gl==gv: pe+=p
        else: pv+=p
    top=sorted(M.items(),key=lambda x:-x[1])[:5]
    return {"pl":round(pl,4),"pe":round(pe,4),"pv":round(pv,4),
            "top":[{"m":f"{k[0]}-{k[1]}","p":round(v*100,1)} for k,v in top]}

def modelo(partidos, avg):
    eq=set()
    for l,v,_,_ in partidos: eq.add(l);eq.add(v)
    S={e:{"gf":[],"gc":[]} for e in eq}
    for l,v,gl,gv in partidos:
        S[l]["gf"].append(gl);S[l]["gc"].append(gv)
        S[v]["gf"].append(gv);S[v]["gc"].append(gl)
    return {e:{"ataque":round((sum(d["gf"])/max(len(d["gf"]),1))/avg,3),
               "defensa":round((sum(d["gc"])/max(len(d["gc"]),1))/avg,3),
               "partidos":len(d["gf"])} for e,d in S.items()}

def lambdas(loc,vis,M,avg):
    ml=M.get(loc,{"ataque":1.0,"defensa":1.0})
    mv=M.get(vis,{"ataque":1.0,"defensa":1.0})
    return round(ml["ataque"]*mv["defensa"]*avg*FACTOR_LOCAL,3), round(mv["ataque"]*ml["defensa"]*avg,3)

def impl(cuotas):
    raw={k:1/v for k,v in cuotas.items() if v>1}
    t=sum(raw.values())
    if t==0: return {"p":{},"vig":0}
    return {"p":{k:round(v/t,4) for k,v in raw.items()},"vig":round((t-1)*100,2)}

def kelly(p,cuota,frac,bank,umbral):
    b=cuota-1;q=1-p;fc=(p*b-q)/b
    fu=fc*frac if fc>0 else 0
    s=round(bank*fu)
    return {"ku":round(fu*100,2),"s":s,"r":round(s*cuota),"g":round(s*cuota-s),
            "ev":round(p*b-q,4),"value":fc>umbral,"edge":round((p-1/cuota)*100,2)}

# ── API ─────────────────────────────────────
@st.cache_data(ttl=3600)
def get_hist(code, key):
    try:
        r=requests.get(f"{API_BASE}/competitions/{code}/matches?status=FINISHED",headers={"X-Auth-Token":key},timeout=10)
        r.raise_for_status()
        out=[]
        for m in r.json().get("matches",[]):
            s=m.get("score",{}).get("fullTime",{})
            if s.get("home") is None: continue
            out.append((m["homeTeam"]["name"],m["awayTeam"]["name"],s["home"],s["away"]))
        return out,None
    except Exception as e: return [],str(e)

@st.cache_data(ttl=900)
def get_next(code, key):
    try:
        r=requests.get(f"{API_BASE}/competitions/{code}/matches?status=SCHEDULED",headers={"X-Auth-Token":key},timeout=10)
        r.raise_for_status()
        out=[]
        for m in r.json().get("matches",[]):
            dt=utc_a_col(m["utcDate"])
            if dt is None: continue
            out.append({"id":m["id"],"dt":dt,"fecha":dt.strftime("%Y-%m-%d"),
                        "hora":dt.strftime("%I:%M %p"),"local":m["homeTeam"]["name"],
                        "visit":m["awayTeam"]["name"],"jornada":m.get("matchday","?"),
                        "hoy":es_hoy(dt),"manana":es_manana(dt)})
        out.sort(key=lambda x:x["dt"])
        hoy_d=datetime.datetime.now(TZ_COL).date()
        limite=hoy_d+datetime.timedelta(days=3)
        return [p for p in out if p["dt"].date()<=limite],None
    except Exception as e: return [],str(e)

# ── Session state ────────────────────────────
def init():
    if "bankroll" not in st.session_state: st.session_state.bankroll=51982
    if "wins"     not in st.session_state: st.session_state.wins=5
    if "losses"   not in st.session_state: st.session_state.losses=0
    if "apuestas" not in st.session_state:
        st.session_state.apuestas=[
            {"partido":"Nacional vs Inter Bogotá","apuesta":"Local","cuota":2.85,"stake":6754,"resultado":"won","ganancia":13195},
            {"partido":"Santa Fe vs América","apuesta":"Local","cuota":2.23,"stake":2405,"resultado":"won","ganancia":2958},
            {"partido":"Valencia vs Rayo","apuesta":"Empate","cuota":3.05,"stake":1060,"resultado":"won","ganancia":2183},
            {"partido":"Girona vs Real Sociedad","apuesta":"Empate","cuota":3.65,"stake":1142,"resultado":"won","ganancia":3026},
            {"partido":"Real Madrid vs Oviedo","apuesta":"Local","cuota":1.24,"stake":3336,"resultado":"won","ganancia":801},
            {"partido":"Aston Villa vs Liverpool","apuesta":"Visitante","cuota":2.40,"stake":1000,"resultado":"pending","ganancia":0},
        ]
init()

# ── SIDEBAR ─────────────────────────────────
with st.sidebar:
    st.markdown('<p class="main-title">BetAnalytics</p>',unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Sistema de apuestas basado en datos</p>',unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### ⚙️ Configuración")
    api_key=st.text_input("API Key (football-data.org)",type="password",placeholder="Pega tu API key aquí")
    liga_n=st.selectbox("Liga",list(LIGAS.keys()),index=0)
    li=LIGAS[liga_n]
    st.markdown("---")
    st.markdown("### 💰 Capital")
    bi=st.number_input("Bankroll actual (COP)",1000,10000000,st.session_state.bankroll,500,format="%d",
                        help="Se actualiza automáticamente al registrar resultados")
    if bi!=st.session_state.bankroll: st.session_state.bankroll=bi
    bank=st.session_state.bankroll
    kf=st.select_slider("Fracción Kelly",[0.25,0.5,0.75,1.0],value=0.5,
                         format_func=lambda x:{0.25:"¼ Kelly",0.5:"½ Kelly",0.75:"¾ Kelly",1.0:"Kelly completo"}[x])
    ue=st.slider("Edge mínimo (%)",1,10,3)/100
    st.markdown("---")
    st.markdown("### 📊 Rendimiento")
    rend=round((bank/BANKROLL_INIT-1)*100,1)
    color="#16a34a" if rend>=0 else "#ef4444"
    st.markdown(f"""
    <div class="metric-card"><div class="metric-label">Bankroll inicial</div><div class="metric-value" style="font-size:1rem">${BANKROLL_INIT:,}</div></div>
    <div class="metric-card"><div class="metric-label">Bankroll actual</div><div class="metric-value" style="font-size:1rem;color:#16a34a">${bank:,}</div></div>
    <div class="metric-card"><div class="metric-label">Rendimiento</div><div class="metric-value" style="font-size:1rem;color:{color}">{rend:+.1f}%</div></div>
    <div class="metric-card"><div class="metric-label">Record</div><div class="metric-value" style="font-size:1rem">{st.session_state.wins}W / {st.session_state.losses}L</div></div>
    """,unsafe_allow_html=True)

# ── MAIN ────────────────────────────────────
ahora=datetime.datetime.now(TZ_COL)
st.markdown(f'<p class="subtitle">{liga_n} · {ahora.strftime("%A %d %b %Y · %I:%M %p")} hora Colombia</p>',unsafe_allow_html=True)
st.markdown('<p class="main-title">BetAnalytics</p>',unsafe_allow_html=True)
st.markdown("")

if not api_key: st.info("👈 Ingresa tu API key para cargar partidos reales.")

tab1,tab2,tab3,tab4=st.tabs(["⚽ Partidos","📈 Equipos","💰 Mis apuestas","📋 Casos de estudio"])

# ══ TAB 1: PARTIDOS ═════════════════════════
with tab1:
    hist,prox=[],[]
    if api_key:
        with st.spinner("Cargando datos..."):
            hist,e1=get_hist(li["code"],api_key)
            prox,e2=get_next(li["code"],api_key)
        if e1: st.warning(f"Error historial: {e1}")
        if e2: st.warning(f"Error próximos: {e2}")
        if hist: st.success(f"✓ {len(hist)} partidos cargados · {len(prox)} próximos (hasta 3 días)")

    if prox and hist:
        M=modelo(hist,li["avg_goles"])
        fechas=sorted(set(p["fecha"] for p in prox))
        for fecha in fechas:
            pf=[p for p in prox if p["fecha"]==fecha]
            if not pf: continue
            dt0=pf[0]["dt"]
            if es_hoy(dt0):    label=f"HOY · {dt0.strftime('%A %d de %B').upper()}"; badge='<span class="today-badge">HOY</span>'
            elif es_manana(dt0): label=f"MAÑANA · {dt0.strftime('%A %d de %B').upper()}"; badge=""
            else:               label=dt0.strftime('%A %d de %B').upper(); badge=""
            st.markdown(f'<div class="day-header">{label}{badge}</div>',unsafe_allow_html=True)

            for p in pf:
                loc,vis,hora=p["local"],p["visit"],p["hora"]
                ll,lv=lambdas(loc,vis,M,li["avg_goles"])
                pr=poisson(ll,lv)
                with st.expander(f"⚽  {loc}  vs  {vis}   ·   {hora} Col",expanded=p["hoy"]):
                    c1,c2,c3=st.columns(3)
                    for col,lbl,val,clr in [(c1,"Local gana",pr["pl"]*100,"#00d4ff"),(c2,"Empate",pr["pe"]*100,"#4a5568"),(c3,"Visitante gana",pr["pv"]*100,"#7b2fff")]:
                        with col:
                            st.markdown(f'<div class="metric-card"><div class="metric-label">{lbl}</div><div class="metric-value">{val:.1f}%</div><div class="prob-bar-container"><div style="width:{val}%;height:8px;background:{clr};border-radius:6px;"></div></div></div>',unsafe_allow_html=True)

                    st.markdown("**Marcadores más probables:**")
                    cols=st.columns(5)
                    for i,s in enumerate(pr["top"]):
                        with cols[i]: st.markdown(f'<div class="metric-card" style="text-align:center;padding:10px"><div style="font-size:1rem;font-weight:800">{s["m"]}</div><div class="metric-label">{s["p"]}%</div></div>',unsafe_allow_html=True)

                    st.markdown("**Cuotas (actualiza con las de tu casa de apuestas):**")
                    c1,c2,c3=st.columns(3)
                    with c1: ql=st.number_input("Local",1.01,50.0,2.00,0.05,key=f"ql_{p['id']}",format="%.2f")
                    with c2: qe=st.number_input("Empate",1.01,50.0,3.30,0.05,key=f"qe_{p['id']}",format="%.2f")
                    with c3: qv=st.number_input("Visitante",1.01,50.0,3.80,0.05,key=f"qv_{p['id']}",format="%.2f")

                    im=impl({"local":ql,"empate":qe,"visit":qv})
                    vig=im["vig"]
                    st.markdown(f'<div class="{"vig-warning" if vig>8 else "vig-ok"}">{"⚠️ Vig alto" if vig>8 else "✓ Vig aceptable"}: {vig}%</div>',unsafe_allow_html=True)

                    st.markdown("**Veredicto:**")
                    hay=False
                    for nm,pm,cu,et in [("local",pr["pl"],ql,loc),("empate",pr["pe"],qe,"Empate"),("visit",pr["pv"],qv,vis)]:
                        pi=im["p"].get(nm,0)
                        k=kelly(pm,cu,kf,bank,ue)
                        if k["value"]:
                            hay=True
                            st.markdown(f'<div class="value-yes"><span class="badge-value">✓ VALUE BET</span><div style="margin-top:8px;font-weight:700;font-size:1.05rem">{et} · cuota {cu}</div><div style="display:flex;gap:18px;margin-top:8px;flex-wrap:wrap;"><div><span style="color:#4a5568;font-size:0.72rem">P MODELO</span><br><b>{pm*100:.1f}%</b></div><div><span style="color:#4a5568;font-size:0.72rem">P IMPLÍCITA</span><br><b>{pi*100:.1f}%</b></div><div><span style="color:#4a5568;font-size:0.72rem">EDGE</span><br><b style="color:#16a34a">+{k["edge"]:.1f}%</b></div><div><span style="color:#4a5568;font-size:0.72rem">KELLY</span><br><b>{k["ku"]:.1f}%</b></div><div><span style="color:#4a5568;font-size:0.72rem">APOSTAR</span><br><b style="color:#00d4ff;font-size:1.1rem">${k["s"]:,}</b></div><div><span style="color:#4a5568;font-size:0.72rem">RETORNO</span><br><b>${k["r"]:,}</b></div><div><span style="color:#4a5568;font-size:0.72rem">EV/$1</span><br><b>+{k["ev"]:.3f}</b></div></div></div>',unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="value-no"><span class="badge-no">✗ SIN VALUE</span> <span style="color:#6b7280">{et} · cuota {cu} · edge {k["edge"]:+.1f}%</span></div>',unsafe_allow_html=True)
                    if not hay:
                        st.markdown('<div style="background:#0d1520;border:1px solid #1e2d40;border-radius:8px;padding:10px 14px;color:#6b7280;font-size:0.85rem;margin-top:6px;">🔇 Sin value bets con estas cuotas. No apostar.</div>',unsafe_allow_html=True)

    elif api_key:
        st.info("No se encontraron partidos próximos para esta liga.")
    else:
        st.markdown("### Análisis manual")
        c1,c2=st.columns(2)
        with c1: eql=st.text_input("Equipo local",placeholder="Ej: Real Madrid")
        with c2: eqv=st.text_input("Equipo visitante",placeholder="Ej: Barcelona")
        c1,c2,c3=st.columns(3)
        with c1: ql=st.number_input("Cuota local",1.01,50.0,2.00,0.05,format="%.2f",key="m_ql")
        with c2: qe=st.number_input("Cuota empate",1.01,50.0,3.30,0.05,format="%.2f",key="m_qe")
        with c3: qv=st.number_input("Cuota visitante",1.01,50.0,3.80,0.05,format="%.2f",key="m_qv")
        c1,c2,c3=st.columns(3)
        with c1: pl=st.number_input("P(local) %",1.0,99.0,45.0,0.5)/100
        with c2: pe=st.number_input("P(empate) %",1.0,99.0,28.0,0.5)/100
        with c3: pv=st.number_input("P(visit) %",1.0,99.0,27.0,0.5)/100
        if eql and eqv:
            im=impl({"local":ql,"empate":qe,"visit":qv})
            st.markdown(f'<div class="{"vig-warning" if im["vig"]>8 else "vig-ok"}">Vig: {im["vig"]}%</div>',unsafe_allow_html=True)
            for nm,pm,cu,et in [("local",pl,ql,eql),("empate",pe,qe,"Empate"),("visit",pv,qv,eqv)]:
                k=kelly(pm,cu,kf,bank,ue)
                if k["value"]: st.markdown(f'<div class="value-yes"><span class="badge-value">✓ VALUE BET</span><div style="margin-top:8px;font-weight:700">{et} · cuota {cu}</div><div style="display:flex;gap:16px;margin-top:8px;flex-wrap:wrap;"><div><span style="color:#4a5568;font-size:0.72rem">EDGE</span><br><b style="color:#16a34a">+{k["edge"]:.1f}%</b></div><div><span style="color:#4a5568;font-size:0.72rem">APOSTAR</span><br><b style="color:#00d4ff">${k["s"]:,}</b></div><div><span style="color:#4a5568;font-size:0.72rem">RETORNO</span><br><b>${k["r"]:,}</b></div></div></div>',unsafe_allow_html=True)
                else: st.markdown(f'<div class="value-no"><span class="badge-no">✗ SIN VALUE</span> <span style="color:#6b7280">{et} · edge {k["edge"]:+.1f}%</span></div>',unsafe_allow_html=True)

# ══ TAB 2: EQUIPOS ══════════════════════════
with tab2:
    st.markdown("### Fuerza relativa de equipos")
    if api_key and hist:
        M=modelo(hist,li["avg_goles"])
        for eq,v in sorted([(e,d) for e,d in M.items() if d["partidos"]>=3],key=lambda x:-x[1]["ataque"]):
            c1,c2,c3,c4=st.columns([3,2,2,1])
            with c1: st.markdown(f"**{eq}**")
            with c2: st.markdown(f'<span style="color:{"#16a34a" if v["ataque"]>1 else "#ef4444"}">Ataque: {v["ataque"]:.3f}</span>',unsafe_allow_html=True)
            with c3: st.markdown(f'<span style="color:{"#16a34a" if v["defensa"]<1 else "#ef4444"}">Defensa: {v["defensa"]:.3f}</span>',unsafe_allow_html=True)
            with c4: st.markdown(f'<span style="color:#4a5568">{v["partidos"]}p</span>',unsafe_allow_html=True)
        st.caption("Ataque > 1.0 = mejor que la media · Defensa < 1.0 = mejor que la media")
    else: st.info("Conecta tu API key para ver el modelo de equipos.")

# ══ TAB 3: MIS APUESTAS ═════════════════════
with tab3:
    st.markdown("### 💰 Tracker de apuestas")

    with st.expander("➕ Registrar nueva apuesta",expanded=False):
        r1,r2=st.columns(2)
        with r1:
            np=st.text_input("Partido",placeholder="Ej: Barcelona vs Real Madrid",key="np")
            na=st.text_input("Apuesta",placeholder="Local / Empate / Visitante",key="na")
        with r2:
            nc=st.number_input("Cuota",1.01,50.0,2.00,0.05,format="%.2f",key="nc")
            ns=st.number_input("Stake (COP)",100,1000000,1000,100,key="ns")
        nr=st.selectbox("Resultado",["pending","won","lost"],key="nr",
                         format_func=lambda x:{"pending":"⏳ Pendiente","won":"✓ Ganó","lost":"✗ Perdió"}[x])
        if st.button("Registrar",type="primary"):
            if np and na:
                g=round(ns*nc-ns) if nr=="won" else (-ns if nr=="lost" else 0)
                st.session_state.apuestas.append({"partido":np,"apuesta":na,"cuota":nc,"stake":ns,"resultado":nr,"ganancia":g})
                if nr=="won": st.session_state.bankroll+=g; st.session_state.wins+=1
                elif nr=="lost": st.session_state.bankroll-=ns; st.session_state.losses+=1
                st.success(f"✓ Registrada. Bankroll: ${st.session_state.bankroll:,}")
                st.rerun()

    # Pendientes
    pend=[(i,a) for i,a in enumerate(st.session_state.apuestas) if a["resultado"]=="pending"]
    if pend:
        st.markdown("---")
        st.markdown("**⏳ Pendientes — actualiza el resultado:**")
        for i,ap in pend:
            c1,c2,c3=st.columns([4,1,1])
            with c1: st.markdown(f'<div class="bet-row bet-pending"><b>{ap["partido"]}</b> · {ap["apuesta"]} · cuota {ap["cuota"]}<br><span style="color:#4a5568;font-size:0.8rem">Stake ${ap["stake"]:,} · Retorno si gana ${round(ap["stake"]*ap["cuota"]):,}</span></div>',unsafe_allow_html=True)
            with c2:
                if st.button("✓ Ganó",key=f"w_{i}",type="primary"):
                    g=round(ap["stake"]*ap["cuota"]-ap["stake"])
                    st.session_state.apuestas[i].update({"resultado":"won","ganancia":g})
                    st.session_state.bankroll+=g; st.session_state.wins+=1; st.rerun()
            with c3:
                if st.button("✗ Perdió",key=f"l_{i}"):
                    st.session_state.apuestas[i].update({"resultado":"lost","ganancia":-ap["stake"]})
                    st.session_state.bankroll-=ap["stake"]; st.session_state.losses+=1; st.rerun()

    # Historial
    st.markdown("---")
    st.markdown("**📋 Historial completo:**")
    tw=sum(a["ganancia"] for a in st.session_state.apuestas if a["resultado"]=="won")
    tl=sum(a["stake"] for a in st.session_state.apuestas if a["resultado"]=="lost")
    ta=sum(a["stake"] for a in st.session_state.apuestas)
    for ap in reversed(st.session_state.apuestas):
        cl={"won":"bet-won","lost":"bet-lost","pending":"bet-pending"}.get(ap["resultado"],"")
        ic={"won":"✓","lost":"✗","pending":"⏳"}.get(ap["resultado"],"")
        co={"won":"#16a34a","lost":"#ef4444","pending":"#d97706"}.get(ap["resultado"],"")
        gs=f'+${ap["ganancia"]:,}' if ap["resultado"]=="won" else (f'-${ap["stake"]:,}' if ap["resultado"]=="lost" else "pendiente")
        st.markdown(f'<div class="bet-row {cl}"><div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px;"><div><b>{ap["partido"]}</b> · {ap["apuesta"]} · cuota {ap["cuota"]}</div><span style="color:{co};font-weight:700">{ic} {gs}</span></div><div style="color:#4a5568;font-size:0.8rem;margin-top:4px">Stake: ${ap["stake"]:,}</div></div>',unsafe_allow_html=True)

    roi=round((tw-tl)/max(ta,1)*100,1)
    st.markdown(f'<div class="metric-card" style="margin-top:16px"><div style="display:flex;gap:24px;flex-wrap:wrap;"><div><div class="metric-label">Total apostado</div><div class="metric-value" style="font-size:1rem">${ta:,}</div></div><div><div class="metric-label">Total ganado</div><div class="metric-value" style="font-size:1rem;color:#16a34a">+${tw:,}</div></div><div><div class="metric-label">Total perdido</div><div class="metric-value" style="font-size:1rem;color:#ef4444">-${tl:,}</div></div><div><div class="metric-label">ROI</div><div class="metric-value" style="font-size:1rem;color:#00d4ff">{roi}%</div></div></div></div>',unsafe_allow_html=True)

# ══ TAB 4: CASOS DE ESTUDIO ═════════════════
with tab4:
    st.markdown("### Registro de casos de estudio")
    casos=[
        {"num":1,"partido":"Atlético Nacional 5-1 Inter Bogotá","fecha":"12 mayo 2026","liga":"Liga BetPlay","apuesta":"Local","cuota":2.85,"edge":"+29.1%","stake":6754,"resultado":"✓ GANÓ","leccion":"El 0-1 al min 15 era ruido estadístico. No dejarse llevar por el marcador en vivo.","ganancia":"+$13,195"},
        {"num":2,"partido":"Santa Fe 2-1 América de Cali","fecha":"12 mayo 2026","liga":"Liga BetPlay","apuesta":"Local","cuota":2.23,"edge":"+8.1%","stake":2405,"resultado":"✓ GANÓ","leccion":"Edge moderado con muestra confiable y vig bajo es más sólido que edge alto con poca muestra.","ganancia":"+$2,958"},
        {"num":3,"partido":"Valencia 0-0 Rayo Vallecano","fecha":"14 mayo 2026","liga":"La Liga","apuesta":"Empate","cuota":3.05,"edge":"+5.1%","stake":1060,"resultado":"✓ GANÓ","leccion":"Partido cerrado. El 0-0 fue el marcador más probable del modelo.","ganancia":"+$2,183"},
        {"num":4,"partido":"Girona 1-1 Real Sociedad","fecha":"14 mayo 2026","liga":"La Liga","apuesta":"Empate","cuota":3.65,"edge":"+8.9%","stake":1142,"resultado":"✓ GANÓ","leccion":"Se rechazó cash out de $2,000 con marcador 0-1. Empate llegó y se cobró $4,168.","ganancia":"+$3,026"},
        {"num":5,"partido":"Real Madrid vs Real Oviedo","fecha":"14 mayo 2026","liga":"La Liga","apuesta":"Local","cuota":1.24,"edge":"+10.7%","stake":3336,"resultado":"✓ GANÓ","leccion":"¼ Kelly fue la decisión correcta para no inmovilizar capital en cuota baja.","ganancia":"+$801"},
        {"num":6,"partido":"Aston Villa vs Liverpool","fecha":"15 mayo 2026","liga":"Premier League","apuesta":"Visitante","cuota":2.40,"edge":"-3.7% modelo / +H2H","stake":1000,"resultado":"⏳ PENDIENTE","leccion":"Primera apuesta basada en H2H (Liverpool 34-11 sobre Villa) por encima del modelo. Caso de estudio: modelo vs contexto.","ganancia":"pendiente"},
    ]
    for c in casos:
        co="#16a34a" if "GANÓ" in c["resultado"] else ("#d97706" if "PENDIENTE" in c["resultado"] else "#ef4444")
        st.markdown(f'<div class="case-study"><div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;"><div><span style="color:#00d4ff;font-family:\'Space Mono\',monospace;font-size:0.72rem">CASO #{c["num"]} · {c["fecha"]} · {c["liga"]}</span><br><span style="font-weight:700">{c["partido"]}</span></div><span style="color:{co};font-weight:700">{c["resultado"]} · {c["ganancia"]}</span></div><div style="display:flex;gap:14px;margin-top:8px;flex-wrap:wrap;font-size:0.8rem;"><span>🎯 {c["apuesta"]}</span><span>📊 {c["cuota"]}</span><span>📈 {c["edge"]}</span><span>💰 ${c["stake"]:,}</span></div><div style="margin-top:8px;color:#6b7280;font-size:0.8rem;font-style:italic">💡 {c["leccion"]}</div></div>',unsafe_allow_html=True)
