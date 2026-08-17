# BetAnalytics — Agente de Datos Automatizado

## Problema actual
- 29 ligas/copas con datos hardcodeados en `app.py` (~4,995 líneas)
- Cada actualización de tabla, fixture o inicio de temporada requiere editar código manualmente
- Las fuentes de datos son heterogéneas (TheSportsDB, football-data.org, Wikipedia, AFA, The Odds API)
- Roturas frecuentes al inicio de temporadas europeas (La Liga, Bundesliga, etc.)

## Solución: GitHub Action + JSON como base de datos

### Arquitectura

```
┌──────────────────────────────────────────────────┐
│  GitHub Actions (CRON diario 6:00 AM COT)        │
│                                                  │
│  fetcher.py                                      │
│  ├── fetch_thesportsdb(league_id, season)        │
│  ├── fetch_football_data(code, api_key)          │
│  ├── fetch_wikipedia(url)                        │
│  ├── fetch_odds_api(key, api_key)                │
│  └── fetch_afa(url)                              │
│                                                  │
│  Si hay cambios → commit + push automático       │
└──────────────────┬───────────────────────────────┘
                   │ escribe
                   ▼
┌──────────────────────────────────────────────────┐
│  data/                                           │
│  ├── laliga.json                                 │
│  ├── premier.json                                │
│  ├── bundesliga.json                             │
│  ├── betplay.json                                │
│  ├── argfem.json                                 │
│  ├── libertadores.json                           │
│  └── ... (1 archivo por liga)                    │
└──────────────────┬───────────────────────────────┘
                   │ lee
                   ▼
┌──────────────────────────────────────────────────┐
│  app.py (Streamlit)                              │
│  ├── Lee JSON → construye modelo Poisson         │
│  ├── Muestra fixtures desde JSON                 │
│  ├── Modelo, Kelly, odds → sin cambios           │
│  └── Fallback: si JSON vacío → HIST_ hardcoded   │
└──────────────────────────────────────────────────┘
```

### Estructura de cada JSON

```json
{
  "meta": {
    "league": "La Liga",
    "league_key": "laliga",
    "season": "2026-2027",
    "source": "thesportsdb",
    "last_updated": "2026-08-17T06:00:00-05:00",
    "avg_goals": 1.35,
    "total_matches": 12,
    "total_goals": 31
  },
  "standings": [
    {"team": "Barcelona", "gf": 4, "ga": 1, "pj": 2, "pts": 6, "w": 2, "d": 0, "l": 0}
  ],
  "results": [
    {"date": "2026-08-15", "home": "Alavés", "away": "Getafe", "hg": 1, "ag": 0, "matchday": 1}
  ],
  "fixtures": [
    {"date": "2026-08-23", "time": "02:00 PM", "home": "Barcelona", "away": "Villarreal", "matchday": 2}
  ],
  "hist_season": {
    "season": "2025-26",
    "note": "Tabla final para fallback inicio de temporada",
    "teams": [
      {"team": "Barcelona", "gf": 95, "ga": 36, "pj": 38}
    ]
  }
}
```

### Mapeo de ligas a fuentes

| Liga | Fuente primaria | Fuente fixtures | Key requerida |
|------|----------------|-----------------|---------------|
| La Liga | TheSportsDB (4335) | Odds API / SportsDB | ODDS_API_KEY |
| Premier League | football-data.org (PL) | football-data.org | FOOTBALL_DATA_KEY |
| Bundesliga | TheSportsDB (4331) | Odds API / SportsDB | ODDS_API_KEY |
| 2. Bundesliga | TheSportsDB (4399) | Odds API / SportsDB | ODDS_API_KEY |
| Serie A | football-data.org (SA) | football-data.org | FOOTBALL_DATA_KEY |
| Ligue 1 | football-data.org (FL1) | football-data.org | FOOTBALL_DATA_KEY |
| Primeira Liga | football-data.org (PPL) | football-data.org | FOOTBALL_DATA_KEY |
| Champions League | football-data.org (CL) | football-data.org | FOOTBALL_DATA_KEY |
| Liga BetPlay | TheSportsDB (4497) | TheSportsDB | — |
| Torneo B | TheSportsDB (4951) | TheSportsDB | — |
| Copa Dimayor | TheSportsDB (5183) | TheSportsDB | — |
| Copa Libertadores | Wikipedia scraper | Odds API | ODDS_API_KEY |
| Copa Sudamericana | Wikipedia scraper | Odds API | ODDS_API_KEY |
| Liga Argentina | TheSportsDB (4406) | Odds API | ODDS_API_KEY |
| Brasileirão A | TheSportsDB (4351) | Odds API | ODDS_API_KEY |
| Brasileirão B | Wikipedia tabla | Odds API | ODDS_API_KEY |
| Chile Liga 1ª | Wikipedia tabla | Odds API / SportsDB | ODDS_API_KEY |
| Uruguay | Wikipedia tabla | TheSportsDB | — |
| Paraguay | Wikipedia tabla | TheSportsDB | — |
| Perú Liga 1 | Wikipedia tabla | TheSportsDB | — |
| Ecuador LigaPro | Wikipedia tabla | TheSportsDB | — |
| Bolivia | Wikipedia tabla | TheSportsDB | — |
| Venezuela | Wikipedia tabla | TheSportsDB | — |
| Liga MX | TheSportsDB (4350) | Odds API | ODDS_API_KEY |
| MLS | TheSportsDB (4346) | Odds API | ODDS_API_KEY |
| K-League 1 | Wikipedia tabla | Odds API | ODDS_API_KEY |
| Arg Femenina | Wikipedia tabla | AFA scraper | — |
| Liga F | TheSportsDB (5106) | TheSportsDB | — |
| Copa Argentina | Tabla estática | — | — |

### GitHub Action: `.github/workflows/fetch_data.yml`

```yaml
name: Fetch BetAnalytics Data
on:
  schedule:
    - cron: '0 11 * * *'   # 6:00 AM Colombia (UTC-5)
  workflow_dispatch:         # Permite ejecución manual

jobs:
  fetch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install requests beautifulsoup4

      - name: Run data fetcher
        env:
          FOOTBALL_DATA_KEY: ${{ secrets.FOOTBALL_DATA_KEY }}
          ODDS_API_KEY: ${{ secrets.ODDS_API_KEY }}
        run: python fetcher.py

      - name: Commit and push if changed
        run: |
          git config user.name "BetAnalytics Bot"
          git config user.email "bot@betanalytics.app"
          git add data/
          git diff --staged --quiet || (git commit -m "📊 Data update $(date -u +%Y-%m-%d)" && git push)
```

### Estructura del repo (nueva)

```
betanalytics/
├── app.py                    # Streamlit app (lee de data/)
├── fetcher.py                # Agente: obtiene datos y escribe JSONs
├── sources/                  # Módulos de scraping por fuente
│   ├── __init__.py
│   ├── thesportsdb.py        # TheSportsDB API (gratis, sin key)
│   ├── footballdata.py       # football-data.org API (key gratis)
│   ├── wikipedia.py          # Scraper tablas Wikipedia
│   ├── odds_api.py           # The Odds API (fixtures + cuotas)
│   └── afa.py                # AFA scraper (femenino argentino)
├── data/                     # JSONs generados automáticamente
│   ├── laliga.json
│   ├── premier.json
│   ├── bundesliga.json
│   ├── ...
│   └── _registry.json        # Índice de ligas + última actualización
├── config/
│   └── leagues.json          # Configuración de ligas (reemplaza LIGAS dict)
├── .github/
│   └── workflows/
│       └── fetch_data.yml    # GitHub Action (cron diario)
└── requirements.txt
```

### Fases de implementación

**Fase 1 — Fundación (hoy)**
- Crear `fetcher.py` con módulos para TheSportsDB + football-data.org
- Generar JSONs para las 5 ligas más usadas: BetPlay, La Liga, Bundesliga, Liga Argentina, Brasileirão
- Modificar `app.py` para leer de JSON con fallback a hardcoded
- GitHub Action básico

**Fase 2 — Wikipedia + Sudamérica**
- Módulo `wikipedia.py` para tablas de posiciones (Chile, Uruguay, Perú, Ecuador, Bolivia, etc.)
- Migrar todas las ligas `wiki_tabla` a JSON

**Fase 3 — Fixtures + Odds**
- Módulo `odds_api.py` para fixtures con cuotas
- Módulo `afa.py` para ArgFem
- Integrar cuotas automáticas en el análisis

**Fase 4 — Inteligencia**
- Detección automática de inicio de temporada (cambio de season)
- Alertas cuando una fuente deja de funcionar
- Log de cambios (qué se actualizó cada día)

### Beneficios

| Antes | Después |
|-------|---------|
| Editar app.py cada vez | Solo leer JSON |
| Roturas al inicio de temporada | hist_season en JSON como fallback automático |
| Fixtures manuales | Fixtures actualizados diariamente |
| ~5,000 líneas en app.py | app.py enfocado en modelo + UI |
| Depender de Claude para cada update | Bot actualiza solo, 365 días al año |

### Secrets necesarios en GitHub

| Secret | Fuente | Costo |
|--------|--------|-------|
| `FOOTBALL_DATA_KEY` | football-data.org/client/register | Gratis (10 req/min) |
| `ODDS_API_KEY` | the-odds-api.com | Gratis (500 req/mes) |

Ya los tienes configurados en Streamlit Secrets — solo hay que duplicarlos como GitHub Secrets.
