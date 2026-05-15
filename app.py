"""
app.py — Dashboard de apuestas deportivas
Desarrollado con Streamlit. Desplegable en Streamlit Cloud.
"""

import math
import datetime
from itertools import product as iproduct

import streamlit as st
import requests

# ──────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="BetAnalytics",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# ESTILOS
# ──────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
}
.stApp {
    background: #0a0f1e;
    color: #e8eaf0;
}
.main-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 2.8rem;
    background: linear-gradient(135deg, #00d4ff, #7b2fff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
    line-height: 1.1;
}
.subtitle {
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    color: #4a5568;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-top: 4px;
}
.metric-card {
    background: #111827;
    border: 1px solid #1e2d40;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 12px;
}
.metric-label {
    font-size: 0.72rem;
    color: #4a5568;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-family: 'Space Mono', monospace;
}
.metric-value {
    font-size: 1.8rem;
    font-weight: 800;
    color: #e8eaf0;
    line-height: 1.2;
}
.value-yes {
    background: linear-gradient(135deg, #0d2818, #0a3d1f);
    border: 1px solid #16a34a;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 10px;
}
.value-no {
    background: #111827;
    border: 1px solid #1e2d40;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 10px;
}
.badge-value {
    background: #16a34a;
    color: white;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.05em;
}
.badge-no {
    background: #374151;
    color: #9ca3af;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    font-family: 'Space Mono', monospace;
}
.prob-bar-container {
    background: #1e2d40;
    border-radius: 6px;
    height: 8px;
    margin-top: 6px;
    overflow: hidden;
}
.match-header {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.4rem;
    color: #e8eaf0;
}
.league-tag {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: #00d4ff;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.vig-warning {
    background: #1a1000;
    border: 1px solid #d97706;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 0.8rem;
    color: #d97706;
    font-family: 'Space Mono', monospace;
}
.vig-ok {
    background: #0d1a0d;
    border: 1px solid #16a34a;
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 0.8rem;
    color: #16a34a;
    font-family: 'Space Mono', monospace;
}
.separator {
    border: none;
    border-top: 1px solid #1e2d40;
    margin: 20px 0;
}
.stSelectbox > div > div {
    background: #111827 !important;
    border-color: #1e2d40 !important;
    color: #e8eaf0 !important;
}
.stNumberInput > div > div > input {
    background: #111827 !important;
    border-color: #1e2d40 !important;
    color: #e8eaf0 !important;
}
.stSlider > div > div > div {
    background: #00d4ff !important;
}
div[data-testid="stSidebar"] {
    background: #080d1a;
    border-right: 1px solid #1e2d40;
}
.case-study {
    background: #0d1520;
    border-left: 3px solid #00d4ff;
    border-radius: 0 8px 8px 0;
    padding: 12px 16px;
    margin-bottom: 10px;
    font-size: 0.82rem;
}
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# CONSTANTES
# ──────────────────────────────────────────────

API_BASE = "https://api.football-data.org/v4"

LIGAS = {
    "🇪🇸 La Liga":           {"code": "PD",  "avg_goles": 1.35},
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League":    {"code": "PL",  "avg_goles": 1.40},
    "🇩🇪 Bundesliga":         {"code": "BL1", "avg_goles": 1.55},
    "🇮🇹 Serie A":            {"code": "SA",  "avg_goles": 1.30},
    "🇫🇷 Ligue 1":            {"code": "FL1", "avg_goles": 1.35},
    "🇵🇹 Primeira Liga":      {"code": "PPL", "avg_goles": 1.30},
    "🏆 Champions League":    {"code": "CL",  "avg_goles": 1.45},
}

FACTOR_LOCAL = 1.15
MAX_GOLES    = 8

# ──────────────────────────────────────────────
# MODELO DE POISSON (sin dependencias externas)
# ──────────────────────────────────────────────

def fact(n):
    r = 1
    for i in range(2, n + 1):
        r *= i
    return r

def poisson_pmf(k, lam):
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return (math.exp(-lam) * (lam ** k)) / fact(k)

def probabilidades_poisson(lam_l, lam_v):
    p_local = p_empate = p_visit = 0.0
    matriz = {}
    for gl, gv in iproduct(range(MAX_GOLES + 1), repeat=2):
        p = poisson_pmf(gl, lam_l) * poisson_pmf(gv, lam_v)
        matriz[(gl, gv)] = p
        if gl > gv:   p_local  += p
        elif gl == gv: p_empate += p
        else:          p_visit  += p
    top = sorted(matriz.items(), key=lambda x: x[1], reverse=True)[:5]
    return {
        "p_local":    round(p_local, 4),
        "p_empate":   round(p_empate, 4),
        "p_visit":    round(p_visit, 4),
        "top_scores": [{"marcador": f"{k[0]}-{k[1]}", "prob": round(v*100,1)} for k,v in top],
    }

def construir_modelo(partidos, avg_goles):
    equipos = set()
    for local, visit, _, _ in partidos:
        equipos.add(local); equipos.add(visit)
    stats = {eq: {"gf": [], "gc": []} for eq in equipos}
    for local, visit, gl, gv in partidos:
        stats[local]["gf"].append(gl); stats[local]["gc"].append(gv)
        stats[visit]["gf"].append(gv); stats[visit]["gc"].append(gl)
    modelo = {}
    for eq, v in stats.items():
        n = len(v["gf"])
        if n == 0:
            modelo[eq] = {"ataque": 1.0, "defensa": 1.0, "partidos": 0}
            continue
        modelo[eq] = {
            "ataque":   round((sum(v["gf"]) / n) / avg_goles, 3),
            "defensa":  round((sum(v["gc"]) / n) / avg_goles, 3),
            "partidos": n,
        }
    return modelo

def lambda_esperado(local, visit, modelo, avg_goles):
    ml = modelo.get(local, {"ataque": 1.0, "defensa": 1.0})
    mv = modelo.get(visit,  {"ataque": 1.0, "defensa": 1.0})
    lam_l = ml["ataque"] * mv["defensa"] * avg_goles * FACTOR_LOCAL
    lam_v = mv["ataque"] * ml["defensa"] * avg_goles
    return round(lam_l, 3), round(lam_v, 3)

def prob_implicita(cuotas):
    raw   = {k: 1/v for k, v in cuotas.items() if v > 1}
    total = sum(raw.values())
    if total == 0:
        return {"probabilidades": {}, "vig_pct": 0}
    vig  = round((total - 1) * 100, 2)
    norm = {k: round(v/total, 4) for k, v in raw.items()}
    return {"probabilidades": norm, "vig_pct": vig}

def kelly(p, cuota, fraccion, bankroll, umbral):
    b = cuota - 1
    q = 1 - p
    f_completo = (p * b - q) / b
    f_usado    = f_completo * fraccion if f_completo > 0 else 0.0
    stake      = round(bankroll * f_usado)
    ev         = round(p * b - q, 4)
    return {
        "kelly_completo_pct": round(f_completo * 100, 2),
        "kelly_usado_pct":    round(f_usado * 100, 2),
        "stake":              stake,
        "retorno":            round(stake * cuota),
        "ganancia":           round(stake * cuota - stake),
        "ev_por_dolar":       ev,
        "tiene_value":        f_completo > umbral,
        "edge":               round((p - 1/cuota) * 100, 2),
    }

# ──────────────────────────────────────────────
# API DE DATOS
# ──────────────────────────────────────────────

@st.cache_data(ttl=3600)
def obtener_partidos_api(liga_code, api_key):
    """Descarga partidos finalizados de la temporada actual."""
    url = f"{API_BASE}/competitions/{liga_code}/matches?status=FINISHED"
    headers = {"X-Auth-Token": api_key}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        matches = resp.json().get("matches", [])
        partidos = []
        for m in matches:
            score = m.get("score", {}).get("fullTime", {})
            if score.get("home") is None:
                continue
            partidos.append((
                m["homeTeam"]["name"],
                m["awayTeam"]["name"],
                score["home"],
                score["away"],
            ))
        return partidos, None
    except Exception as e:
        return [], str(e)

@st.cache_data(ttl=1800)
def obtener_proximos_partidos(liga_code, api_key):
    """Descarga los próximos partidos programados."""
    url = f"{API_BASE}/competitions/{liga_code}/matches?status=SCHEDULED"
    headers = {"X-Auth-Token": api_key}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        matches = resp.json().get("matches", [])
        proximos = []
        for m in matches:
            proximos.append({
                "id":        m["id"],
                "fecha":     m["utcDate"][:10],
                "hora":      m["utcDate"][11:16],
                "local":     m["homeTeam"]["name"],
                "visitante": m["awayTeam"]["name"],
                "jornada":   m.get("matchday", "?"),
            })
        # Ordenar por fecha y tomar la jornada más próxima
        proximos.sort(key=lambda x: x["fecha"])
        if proximos:
            primera_fecha = proximos[0]["fecha"]
            proximos = [p for p in proximos if p["fecha"] == primera_fecha]
        return proximos, None
    except Exception as e:
        return [], str(e)

# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────

with st.sidebar:
    st.markdown('<p class="main-title">BetAnalytics</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Sistema de apuestas basado en datos</p>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### ⚙️ Configuración")

    api_key = st.text_input(
        "API Key (football-data.org)",
        type="password",
        placeholder="Pega tu API key aquí",
        help="Regístrate gratis en football-data.org"
    )

    liga_nombre = st.selectbox(
        "Liga",
        list(LIGAS.keys()),
        index=0,
    )
    liga_info = LIGAS[liga_nombre]

    st.markdown("---")
    st.markdown("### 💰 Gestión de capital")

    bankroll = st.number_input(
        "Bankroll (COP)",
        min_value=1000,
        max_value=10000000,
        value=51982,
        step=1000,
        format="%d",
    )

    kelly_fraccion = st.select_slider(
        "Fracción Kelly",
        options=[0.25, 0.5, 0.75, 1.0],
        value=0.5,
        format_func=lambda x: {0.25: "¼ Kelly", 0.5: "½ Kelly", 0.75: "¾ Kelly", 1.0: "Kelly completo"}[x],
    )

    umbral_edge = st.slider(
        "Edge mínimo (%)",
        min_value=1,
        max_value=10,
        value=3,
        step=1,
    ) / 100

    st.markdown("---")
    st.markdown("### 📊 Historial")
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Bankroll inicial</div>
        <div class="metric-value" style="font-size:1.1rem">$35,000</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Bankroll actual</div>
        <div class="metric-value" style="font-size:1.1rem; color:#16a34a">${bankroll:,}</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Rendimiento</div>
        <div class="metric-value" style="font-size:1.1rem; color:#00d4ff">+{round((bankroll/35000-1)*100,1)}%</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">Record</div>
        <div class="metric-value" style="font-size:1.1rem">6 ✓ / 0 ✗</div>
    </div>
    """, unsafe_allow_html=True)

# ──────────────────────────────────────────────
# CONTENIDO PRINCIPAL
# ──────────────────────────────────────────────

st.markdown(f'<p class="league-tag">{liga_nombre} · Próxima jornada</p>', unsafe_allow_html=True)
st.markdown('<p class="main-title">Análisis de partidos</p>', unsafe_allow_html=True)
st.markdown("")

if not api_key:
    st.info("👈 Ingresa tu API key en el panel izquierdo para cargar los partidos reales. Mientras tanto puedes usar el modo manual.")
    modo = "manual"
else:
    modo = "api"

# ── TABS ─────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["⚽ Partidos", "📈 Modelo de equipos", "📋 Casos de estudio"])

# ══════════════════════════════════════════════
# TAB 1: PARTIDOS
# ══════════════════════════════════════════════

with tab1:

    partidos_historicos = []
    proximos = []

    if modo == "api":
        with st.spinner("Cargando datos de la temporada..."):
            partidos_historicos, err1 = obtener_partidos_api(liga_info["code"], api_key)
            proximos, err2 = obtener_proximos_partidos(liga_info["code"], api_key)

        if err1:
            st.warning(f"Error cargando historial: {err1}")
        if err2:
            st.warning(f"Error cargando próximos partidos: {err2}")

        if partidos_historicos:
            st.success(f"✓ {len(partidos_historicos)} partidos cargados · {len(proximos)} partidos próximos encontrados")

    # ── Si hay partidos via API ───────────────
    if proximos and partidos_historicos:
        modelo = construir_modelo(partidos_historicos, liga_info["avg_goles"])

        st.markdown(f"### Jornada {proximos[0].get('jornada','?')} · {proximos[0]['fecha']}")
        st.markdown("")

        for partido in proximos:
            local    = partido["local"]
            visitante = partido["visitante"]
            hora     = partido["hora"]

            lam_l, lam_v = lambda_esperado(local, visitante, modelo, liga_info["avg_goles"])
            probs = probabilidades_poisson(lam_l, lam_v)

            with st.expander(f"⚽ {local} vs {visitante}  ·  {hora} UTC", expanded=True):
                col1, col2, col3 = st.columns([2, 2, 2])

                with col1:
                    p_l = probs["p_local"] * 100
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Local gana</div>
                        <div class="metric-value">{p_l:.1f}%</div>
                        <div class="prob-bar-container">
                            <div style="width:{p_l}%; height:8px; background:linear-gradient(90deg,#00d4ff,#7b2fff); border-radius:6px;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    p_e = probs["p_empate"] * 100
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Empate</div>
                        <div class="metric-value">{p_e:.1f}%</div>
                        <div class="prob-bar-container">
                            <div style="width:{p_e}%; height:8px; background:#4a5568; border-radius:6px;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    p_v = probs["p_visit"] * 100
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Visitante gana</div>
                        <div class="metric-value">{p_v:.1f}%</div>
                        <div class="prob-bar-container">
                            <div style="width:{p_v}%; height:8px; background:linear-gradient(90deg,#7b2fff,#00d4ff); border-radius:6px;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("**Marcadores más probables:**")
                cols = st.columns(5)
                for i, s in enumerate(probs["top_scores"]):
                    with cols[i]:
                        st.markdown(f"""
                        <div class="metric-card" style="text-align:center; padding:10px">
                            <div style="font-size:1.1rem; font-weight:800">{s['marcador']}</div>
                            <div class="metric-label">{s['prob']}%</div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("**Ingresa las cuotas de tu casa de apuestas:**")
                c1, c2, c3 = st.columns(3)
                with c1:
                    q_local  = st.number_input(f"Local ({local[:12]})", min_value=1.01, max_value=50.0, value=2.00, step=0.05, key=f"ql_{partido['id']}", format="%.2f")
                with c2:
                    q_empate = st.number_input("Empate", min_value=1.01, max_value=50.0, value=3.30, step=0.05, key=f"qe_{partido['id']}", format="%.2f")
                with c3:
                    q_visit  = st.number_input(f"Visitante ({visitante[:12]})", min_value=1.01, max_value=50.0, value=3.80, step=0.05, key=f"qv_{partido['id']}", format="%.2f")

                cuotas = {"local": q_local, "empate": q_empate, "visit": q_visit}
                impl   = prob_implicita(cuotas)
                vig    = impl["vig_pct"]

                if vig > 8:
                    st.markdown(f'<div class="vig-warning">⚠️ Margen de la casa (vig): {vig}% — alto, precaución</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="vig-ok">✓ Margen de la casa (vig): {vig}% — aceptable</div>', unsafe_allow_html=True)

                st.markdown("")
                st.markdown("**Veredicto del modelo:**")

                opciones = [
                    ("local",  probs["p_local"],  q_local,  local),
                    ("empate", probs["p_empate"], q_empate, "Empate"),
                    ("visit",  probs["p_visit"],  q_visit,  visitante),
                ]

                hay_value = False
                for nombre, p_mod, cuota, etiqueta in opciones:
                    p_impl = impl["probabilidades"].get(nombre, 0)
                    k = kelly(p_mod, cuota, kelly_fraccion, bankroll, umbral_edge)

                    if k["tiene_value"]:
                        hay_value = True
                        retorno_total = round(k["stake"] * cuota)
                        st.markdown(f"""
                        <div class="value-yes">
                            <span class="badge-value">✓ VALUE BET</span>
                            <div style="margin-top:8px; font-weight:700; font-size:1.05rem">{etiqueta} · cuota {cuota}</div>
                            <div style="display:flex; gap:24px; margin-top:8px; flex-wrap:wrap;">
                                <div><span style="color:#4a5568; font-size:0.75rem">P MODELO</span><br><b>{p_mod*100:.1f}%</b></div>
                                <div><span style="color:#4a5568; font-size:0.75rem">P IMPLÍCITA</span><br><b>{p_impl*100:.1f}%</b></div>
                                <div><span style="color:#4a5568; font-size:0.75rem">EDGE</span><br><b style="color:#16a34a">+{k['edge']:.1f}%</b></div>
                                <div><span style="color:#4a5568; font-size:0.75rem">KELLY USADO</span><br><b>{k['kelly_usado_pct']:.1f}%</b></div>
                                <div><span style="color:#4a5568; font-size:0.75rem">APOSTAR</span><br><b style="color:#00d4ff; font-size:1.1rem">${k['stake']:,}</b></div>
                                <div><span style="color:#4a5568; font-size:0.75rem">RETORNO</span><br><b>${retorno_total:,}</b></div>
                                <div><span style="color:#4a5568; font-size:0.75rem">EV/$1</span><br><b>+{k['ev_por_dolar']:.3f}</b></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="value-no">
                            <span class="badge-no">✗ SIN VALUE</span>
                            <span style="margin-left:10px; color:#6b7280">{etiqueta} · cuota {cuota} · edge {k['edge']:+.1f}%</span>
                        </div>
                        """, unsafe_allow_html=True)

                if not hay_value:
                    st.markdown("""
                    <div style="background:#0d1520; border:1px solid #1e2d40; border-radius:8px; padding:12px 16px; color:#6b7280; font-size:0.85rem; margin-top:8px;">
                        🔇 Sin value bets en este partido con las cuotas actuales. No apostar.
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown('<hr class="separator">', unsafe_allow_html=True)

    # ── MODO MANUAL ──────────────────────────
    else:
        st.markdown("### Análisis manual de partido")
        st.markdown("Ingresa los datos del partido que quieres analizar:")

        col1, col2 = st.columns(2)
        with col1:
            equipo_local = st.text_input("Equipo local", placeholder="Ej: Real Madrid")
        with col2:
            equipo_visit = st.text_input("Equipo visitante", placeholder="Ej: Barcelona")

        st.markdown("**Cuotas:**")
        c1, c2, c3 = st.columns(3)
        with c1:
            q_local  = st.number_input("Local", min_value=1.01, max_value=50.0, value=2.00, step=0.05, format="%.2f", key="man_ql")
        with c2:
            q_empate = st.number_input("Empate", min_value=1.01, max_value=50.0, value=3.30, step=0.05, format="%.2f", key="man_qe")
        with c3:
            q_visit  = st.number_input("Visitante", min_value=1.01, max_value=50.0, value=3.80, step=0.05, format="%.2f", key="man_qv")

        st.markdown("**Probabilidades del modelo (Poisson manual):**")
        m1, m2, m3 = st.columns(3)
        with m1:
            p_local_man = st.number_input("P(local) %", min_value=1.0, max_value=99.0, value=45.0, step=0.5) / 100
        with m2:
            p_emp_man   = st.number_input("P(empate) %", min_value=1.0, max_value=99.0, value=28.0, step=0.5) / 100
        with m3:
            p_vis_man   = st.number_input("P(visitante) %", min_value=1.0, max_value=99.0, value=27.0, step=0.5) / 100

        if equipo_local and equipo_visit:
            cuotas = {"local": q_local, "empate": q_empate, "visit": q_visit}
            impl   = prob_implicita(cuotas)
            vig    = impl["vig_pct"]

            if vig > 8:
                st.markdown(f'<div class="vig-warning">⚠️ Vig: {vig}% — alto</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="vig-ok">✓ Vig: {vig}% — aceptable</div>', unsafe_allow_html=True)

            st.markdown("**Veredicto:**")
            opciones = [
                ("local",  p_local_man, q_local,  equipo_local),
                ("empate", p_emp_man,   q_empate, "Empate"),
                ("visit",  p_vis_man,   q_visit,  equipo_visit),
            ]
            for nombre, p_mod, cuota, etiqueta in opciones:
                p_impl = impl["probabilidades"].get(nombre, 0)
                k = kelly(p_mod, cuota, kelly_fraccion, bankroll, umbral_edge)
                if k["tiene_value"]:
                    st.markdown(f"""
                    <div class="value-yes">
                        <span class="badge-value">✓ VALUE BET</span>
                        <div style="margin-top:8px; font-weight:700">{etiqueta} · cuota {cuota}</div>
                        <div style="display:flex; gap:20px; margin-top:8px; flex-wrap:wrap;">
                            <div><span style="color:#4a5568; font-size:0.75rem">EDGE</span><br><b style="color:#16a34a">+{k['edge']:.1f}%</b></div>
                            <div><span style="color:#4a5568; font-size:0.75rem">APOSTAR</span><br><b style="color:#00d4ff">${k['stake']:,}</b></div>
                            <div><span style="color:#4a5568; font-size:0.75rem">RETORNO</span><br><b>${round(k['stake']*cuota):,}</b></div>
                            <div><span style="color:#4a5568; font-size:0.75rem">EV/$1</span><br><b>+{k['ev_por_dolar']:.3f}</b></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="value-no">
                        <span class="badge-no">✗ SIN VALUE</span>
                        <span style="margin-left:10px; color:#6b7280">{etiqueta} · edge {k['edge']:+.1f}%</span>
                    </div>
                    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TAB 2: MODELO DE EQUIPOS
# ══════════════════════════════════════════════

with tab2:
    st.markdown("### Fuerza relativa de equipos")
    st.markdown("Carga la API key para ver el modelo completo de la liga seleccionada.")

    if modo == "api" and partidos_historicos:
        modelo = construir_modelo(partidos_historicos, liga_info["avg_goles"])
        equipos_ordenados = sorted(
            [(eq, v) for eq, v in modelo.items() if v["partidos"] >= 3],
            key=lambda x: -x[1]["ataque"]
        )

        for eq, v in equipos_ordenados:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            with col1:
                st.markdown(f"**{eq}**")
            with col2:
                color = "#16a34a" if v["ataque"] > 1 else "#ef4444"
                st.markdown(f'<span style="color:{color}">Ataque: {v["ataque"]:.3f}</span>', unsafe_allow_html=True)
            with col3:
                color = "#16a34a" if v["defensa"] < 1 else "#ef4444"
                st.markdown(f'<span style="color:{color}">Defensa: {v["defensa"]:.3f}</span>', unsafe_allow_html=True)
            with col4:
                st.markdown(f'<span style="color:#4a5568">{v["partidos"]}p</span>', unsafe_allow_html=True)
        st.markdown("*Ataque > 1.0 = mejor que la media · Defensa < 1.0 = mejor que la media*")
    else:
        st.info("Conecta tu API key para ver el modelo de equipos.")

# ══════════════════════════════════════════════
# TAB 3: CASOS DE ESTUDIO
# ══════════════════════════════════════════════

with tab3:
    st.markdown("### Registro de casos de estudio")
    st.markdown("Historial de apuestas realizadas con el sistema.")

    casos = [
        {
            "num": 1,
            "partido": "Atlético Nacional 5-1 Inter Bogotá",
            "fecha": "12 mayo 2026",
            "liga": "Liga BetPlay",
            "apuesta": "Local (Nacional)",
            "cuota": 2.85,
            "edge": "+29.1%",
            "stake": 6754,
            "resultado": "✓ GANÓ",
            "leccion": "El marcador parcial 0-1 al min 15 era ruido estadístico. El modelo mantuvo su señal y acertó. No dejarse llevar por el marcador en vivo.",
            "ganancia": "+$13,195",
        },
        {
            "num": 2,
            "partido": "Santa Fe 2-1 América de Cali",
            "fecha": "12 mayo 2026",
            "liga": "Liga BetPlay",
            "apuesta": "Local (Santa Fe)",
            "cuota": 2.23,
            "edge": "+8.1%",
            "stake": 2405,
            "resultado": "✓ GANÓ",
            "leccion": "Edge moderado con muestra confiable y vig bajo es más sólido que edge alto con poca muestra.",
            "ganancia": "+$2,958",
        },
        {
            "num": 3,
            "partido": "Valencia 0-0 Rayo Vallecano",
            "fecha": "14 mayo 2026",
            "liga": "La Liga",
            "apuesta": "Empate",
            "cuota": 3.05,
            "edge": "+5.1%",
            "stake": 1060,
            "resultado": "✓ GANÓ",
            "leccion": "Partido cerrado de pocas oportunidades. El 0-0 fue el marcador más probable del modelo.",
            "ganancia": "+$2,183",
        },
        {
            "num": 4,
            "partido": "Girona 1-1 Real Sociedad",
            "fecha": "14 mayo 2026",
            "liga": "La Liga",
            "apuesta": "Empate",
            "cuota": 3.65,
            "edge": "+8.9%",
            "stake": 1142,
            "resultado": "✓ GANÓ",
            "leccion": "Se rechazó cash out de $2,000 cuando el marcador era 0-1. El empate llegó y se cobró $4,168. No hacer cash out cuando el modelo sigue siendo válido.",
            "ganancia": "+$3,026",
        },
        {
            "num": 5,
            "partido": "Real Madrid vs Real Oviedo",
            "fecha": "14 mayo 2026",
            "liga": "La Liga",
            "apuesta": "Local (Madrid)",
            "cuota": 1.24,
            "edge": "+10.7%",
            "stake": 3336,
            "resultado": "✓ GANÓ",
            "leccion": "Cuota baja pero edge confirmado. ¼ Kelly fue la decisión correcta para no inmovilizar demasiado capital.",
            "ganancia": "+$801",
        },
    ]

    for c in casos:
        color_res = "#16a34a" if "GANÓ" in c["resultado"] else "#ef4444"
        st.markdown(f"""
        <div class="case-study">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;">
                <div>
                    <span style="color:#00d4ff; font-family:'Space Mono',monospace; font-size:0.75rem">CASO #{c['num']} · {c['fecha']} · {c['liga']}</span><br>
                    <span style="font-weight:700; font-size:1rem">{c['partido']}</span>
                </div>
                <span style="color:{color_res}; font-weight:700">{c['resultado']} · {c['ganancia']}</span>
            </div>
            <div style="display:flex; gap:16px; margin-top:8px; flex-wrap:wrap; font-size:0.8rem;">
                <span>🎯 {c['apuesta']}</span>
                <span>📊 Cuota {c['cuota']}</span>
                <span>📈 Edge {c['edge']}</span>
                <span>💰 Stake ${c['stake']:,}</span>
            </div>
            <div style="margin-top:8px; color:#6b7280; font-size:0.8rem; font-style:italic">💡 {c['leccion']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total apostado", "$14,697", delta=None)
    with col2:
        st.metric("Total ganado", "+$22,163", delta="+150.8%")
    with col3:
        st.metric("Record", "6W / 0L", delta="100% efectividad")
