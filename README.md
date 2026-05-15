# BetAnalytics — Dashboard de apuestas deportivas

Sistema de análisis estadístico para apuestas deportivas basado en el modelo de Poisson y el criterio de Kelly.

## Características

- Análisis automático de partidos de La Liga, Premier League, Bundesliga, Serie A, Ligue 1, Champions League
- Modelo de Poisson para estimar probabilidades de resultado
- Criterio de Kelly para calcular el stake óptimo
- Detección automática de value bets
- Registro de casos de estudio
- Modo manual para ligas sin API

## Instalación local

```bash
pip install streamlit requests
streamlit run app.py
```

## Despliegue en Streamlit Cloud

1. Sube este repositorio a GitHub
2. Ve a share.streamlit.io
3. Conecta tu repositorio
4. ¡Listo! Tu dashboard estará disponible en una URL pública

## API Key

Regístrate gratis en [football-data.org](https://www.football-data.org/client/register) para obtener acceso a datos reales.

## Uso

1. Ingresa tu API key en el panel izquierdo
2. Selecciona la liga
3. Configura tu bankroll y fracción Kelly
4. El sistema muestra automáticamente los próximos partidos con análisis de value bets
