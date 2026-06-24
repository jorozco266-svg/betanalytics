# ═══════════════════════════════════════════════════════════════
# MÓDULO MUNDIAL 2026 — BetAnalytics
# ═══════════════════════════════════════════════════════════════
import datetime, requests
from zoneinfo import ZoneInfo

TZ_COL = ZoneInfo("America/Bogota")

GRUPOS_MUNDIAL = {
    "A": ["Mexico","South Africa","South Korea","Czechia"],
    "B": ["Canada","Bosnia","Qatar","Switzerland"],
    "C": ["Brazil","Morocco","Haiti","Scotland"],
    "D": ["USA","Paraguay","Australia","Turkey"],
    "E": ["Germany","Curacao","Ivory Coast","Ecuador"],
    "F": ["Netherlands","Japan","Sweden","Tunisia"],
    "G": ["Belgium","Egypt","Iran","New Zealand"],
    "H": ["Spain","Cape Verde","Saudi Arabia","Uruguay"],
    "I": ["France","Senegal","Iraq","Norway"],
    "J": ["Argentina","Algeria","Austria","Jordan"],
    "K": ["Portugal","DR Congo","Uzbekistan","Colombia"],
    "L": ["England","Croatia","Ghana","Panama"],
}

BANDERAS_MUNDIAL = {
    "Mexico":"🇲🇽","South Africa":"🇿🇦","South Korea":"🇰🇷","Czechia":"🇨🇿",
    "Canada":"🇨🇦","Bosnia":"🇧🇦","Qatar":"🇶🇦","Switzerland":"🇨🇭",
    "Brazil":"🇧🇷","Morocco":"🇲🇦","Haiti":"🇭🇹","Scotland":"🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "USA":"🇺🇸","Paraguay":"🇵🇾","Australia":"🇦🇺","Turkey":"🇹🇷",
    "Germany":"🇩🇪","Curacao":"🇨🇼","Ivory Coast":"🇨🇮","Ecuador":"🇪🇨",
    "Netherlands":"🇳🇱","Japan":"🇯🇵","Sweden":"🇸🇪","Tunisia":"🇹🇳",
    "Belgium":"🇧🇪","Egypt":"🇪🇬","Iran":"🇮🇷","New Zealand":"🇳🇿",
    "Spain":"🇪🇸","Cape Verde":"🇨🇻","Saudi Arabia":"🇸🇦","Uruguay":"🇺🇾",
    "France":"🇫🇷","Senegal":"🇸🇳","Iraq":"🇮🇶","Norway":"🇳🇴",
    "Argentina":"🇦🇷","Algeria":"🇩🇿","Austria":"🇦🇹","Jordan":"🇯🇴",
    "Portugal":"🇵🇹","DR Congo":"🇨🇩","Uzbekistan":"🇺🇿","Colombia":"🇨🇴",
    "England":"🏴󠁧󠁢󠁥󠁮󠁧󠁿","Croatia":"🇭🇷","Ghana":"🇬🇭","Panama":"🇵🇦",
}

FIXTURE_GRUPOS = [
    # JORNADA 1
    ("A","Mexico","South Africa","2026-06-11","14:00","Mexico City"),
    ("A","South Korea","Czechia","2026-06-11","21:00","Guadalajara"),
    ("B","Canada","Bosnia","2026-06-12","14:00","Toronto"),
    ("D","USA","Paraguay","2026-06-12","20:00","Los Angeles"),
    ("B","Qatar","Switzerland","2026-06-13","14:00","San Francisco"),
    ("C","Brazil","Morocco","2026-06-13","17:00","New York"),
    ("C","Haiti","Scotland","2026-06-13","20:00","Boston"),
    ("D","Australia","Turkey","2026-06-13","23:00","Dallas"),
    ("E","Germany","Curacao","2026-06-14","12:00","Houston"),
    ("F","Netherlands","Japan","2026-06-14","15:00","Dallas"),
    ("E","Ivory Coast","Ecuador","2026-06-14","18:00","Kansas City"),
    ("F","Sweden","Tunisia","2026-06-14","21:00","Seattle"),
    ("G","Belgium","Egypt","2026-06-15","17:00","Vancouver"),
    ("H","Spain","Cape Verde","2026-06-15","13:00","Atlanta"),
    ("H","Saudi Arabia","Uruguay","2026-06-15","19:00","Miami"),
    ("G","Iran","New Zealand","2026-06-15","22:00","Los Angeles"),
    ("I","France","Senegal","2026-06-16","14:00","New York"),
    ("I","Iraq","Norway","2026-06-16","17:00","Boston"),
    ("J","Argentina","Algeria","2026-06-16","20:00","Kansas City"),
    ("J","Austria","Jordan","2026-06-16","23:00","San Francisco"),
    ("K","Portugal","DR Congo","2026-06-17","13:00","Houston"),
    ("L","England","Croatia","2026-06-17","16:00","Dallas"),
    ("L","Ghana","Panama","2026-06-17","19:00","Toronto"),
    ("K","Uzbekistan","Colombia","2026-06-17","22:00","Mexico City"),
    # JORNADA 2
    ("A","Mexico","South Korea","2026-06-18","14:00","Guadalajara"),
    ("A","South Africa","Czechia","2026-06-18","17:00","Atlanta"),
    ("B","Canada","Qatar","2026-06-18","20:00","Toronto"),
    ("B","Switzerland","Bosnia","2026-06-18","23:00","Seattle"),
    ("C","Brazil","Haiti","2026-06-19","16:00","Boston"),
    ("C","Scotland","Morocco","2026-06-19","19:00","New York"),
    ("D","USA","Australia","2026-06-19","14:00","Los Angeles"),
    ("D","Turkey","Paraguay","2026-06-19","23:00","Dallas"),
    ("E","Germany","Ivory Coast","2026-06-20","15:00","Kansas City"),
    ("F","Netherlands","Sweden","2026-06-20","12:00","Dallas"),
    ("E","Ecuador","Curacao","2026-06-20","18:00","San Francisco"),
    ("F","Japan","Tunisia","2026-06-20","21:00","Los Angeles"),
    ("H","Spain","Saudi Arabia","2026-06-21","13:00","Atlanta"),
    ("G","Belgium","Iran","2026-06-21","15:00","Los Angeles"),
    ("H","Uruguay","Cape Verde","2026-06-21","19:00","Miami"),
    ("G","New Zealand","Egypt","2026-06-21","22:00","Vancouver"),
    ("J","Argentina","Austria","2026-06-22","13:00","Dallas"),
    ("I","France","Iraq","2026-06-22","17:00","Philadelphia"),
    ("I","Norway","Senegal","2026-06-22","20:00","New York"),
    ("J","Jordan","Algeria","2026-06-22","23:00","San Francisco"),
    ("K","Portugal","Uzbekistan","2026-06-23","13:00","Houston"),
    ("L","England","Ghana","2026-06-23","16:00","Boston"),
    ("L","Panama","Croatia","2026-06-23","19:00","Toronto"),
    ("K","Colombia","DR Congo","2026-06-23","22:00","Guadalajara"),
    # JORNADA 3
    ("A","Mexico","Czechia","2026-06-24","15:00","Mexico City"),
    ("A","South Africa","South Korea","2026-06-24","15:00","Kansas City"),
    ("B","Canada","Switzerland","2026-06-24","21:00","Vancouver"),
    ("B","Bosnia","Qatar","2026-06-24","21:00","Seattle"),
    ("C","Brazil","Scotland","2026-06-25","16:00","Boston"),
    ("C","Morocco","Haiti","2026-06-25","16:00","New York"),
    ("D","USA","Turkey","2026-06-25","22:00","Dallas"),
    ("D","Paraguay","Australia","2026-06-25","22:00","Los Angeles"),
    ("E","Germany","Ecuador","2026-06-26","16:00","Kansas City"),
    ("E","Curacao","Ivory Coast","2026-06-26","16:00","San Francisco"),
    ("F","Japan","Sweden","2026-06-26","19:00","Los Angeles"),
    ("F","Tunisia","Netherlands","2026-06-26","19:00","Dallas"),
    ("G","Belgium","New Zealand","2026-06-27","16:00","Vancouver"),
    ("G","Egypt","Iran","2026-06-27","16:00","Seattle"),
    ("H","Spain","Uruguay","2026-06-27","22:00","Guadalajara"),
    ("H","Cape Verde","Saudi Arabia","2026-06-27","22:00","Houston"),
    ("I","France","Norway","2026-06-28","15:00","Boston"),
    ("I","Senegal","Iraq","2026-06-28","15:00","Toronto"),
    ("J","Argentina","Jordan","2026-06-28","21:00","Dallas"),
    ("J","Algeria","Austria","2026-06-28","21:00","Kansas City"),
    ("K","Portugal","Colombia","2026-06-29","19:30","Miami"),
    ("K","DR Congo","Uzbekistan","2026-06-29","19:30","Atlanta"),
    ("L","England","Panama","2026-06-29","22:00","New York"),
    ("L","Croatia","Ghana","2026-06-29","22:00","Philadelphia"),
]

WC_STATS = {
    "Mexico":       {"gf":2.57,"gc":0.71,"over25":0.71,"btts":0.43,"elo":2000},
    "South Africa": {"gf":1.29,"gc":1.14,"over25":0.57,"btts":0.43,"elo":1312},
    "South Korea":  {"gf":1.71,"gc":0.86,"over25":0.57,"btts":0.29,"elo":1789},
    "Czechia":      {"gf":1.57,"gc":1.29,"over25":0.57,"btts":0.57,"elo":1748},
    "Canada":       {"gf":1.57,"gc":0.86,"over25":0.57,"btts":0.43,"elo":1469},
    "Bosnia":       {"gf":1.43,"gc":1.29,"over25":0.57,"btts":0.43,"elo":1571},
    "Qatar":        {"gf":1.14,"gc":1.29,"over25":0.43,"btts":0.43,"elo":1365},
    "Switzerland":  {"gf":1.71,"gc":0.86,"over25":0.57,"btts":0.43,"elo":1897},
    "Brazil":       {"gf":2.43,"gc":0.86,"over25":0.86,"btts":0.43,"elo":1979},
    "Morocco":      {"gf":2.57,"gc":0.43,"over25":0.71,"btts":0.14,"elo":1845},
    "Haiti":        {"gf":1.57,"gc":1.29,"over25":0.57,"btts":0.57,"elo":1415},
    "Scotland":     {"gf":2.43,"gc":0.86,"over25":0.71,"btts":0.29,"elo":1638},
    "USA":          {"gf":1.57,"gc":1.43,"over25":0.57,"btts":0.57,"elo":1821},
    "Paraguay":     {"gf":1.29,"gc":1.14,"over25":0.43,"btts":0.43,"elo":1712},
    "Australia":    {"gf":1.29,"gc":1.00,"over25":0.43,"btts":0.43,"elo":1812},
    "Turkey":       {"gf":1.86,"gc":1.14,"over25":0.71,"btts":0.57,"elo":1880},
    "Germany":      {"gf":2.14,"gc":0.86,"over25":0.71,"btts":0.43,"elo":1910},
    "Curacao":      {"gf":0.86,"gc":1.71,"over25":0.43,"btts":0.29,"elo":1388},
    "Ivory Coast":  {"gf":1.71,"gc":1.14,"over25":0.57,"btts":0.57,"elo":1771},
    "Ecuador":      {"gf":1.71,"gc":1.00,"over25":0.57,"btts":0.43,"elo":1933},
    "Netherlands":  {"gf":2.00,"gc":0.86,"over25":0.71,"btts":0.43,"elo":1959},
    "Japan":        {"gf":2.00,"gc":0.71,"over25":0.71,"btts":0.29,"elo":1879},
    "Sweden":       {"gf":1.57,"gc":1.14,"over25":0.57,"btts":0.57,"elo":1565},
    "Tunisia":      {"gf":1.33,"gc":1.17,"over25":0.50,"btts":0.50,"elo":1508},
    "Belgium":      {"gf":3.20,"gc":0.80,"over25":1.00,"btts":0.40,"elo":1849},
    "Egypt":        {"gf":1.43,"gc":1.14,"over25":0.57,"btts":0.57,"elo":1531},
    "Iran":         {"gf":1.29,"gc":0.86,"over25":0.43,"btts":0.29,"elo":1489},
    "New Zealand":  {"gf":1.14,"gc":1.71,"over25":0.57,"btts":0.43,"elo":1408},
    "Spain":        {"gf":3.14,"gc":0.43,"over25":1.00,"btts":0.14,"elo":2171},
    "Cape Verde":   {"gf":1.43,"gc":1.29,"over25":0.57,"btts":0.57,"elo":1312},
    "Saudi Arabia": {"gf":1.43,"gc":1.14,"over25":0.43,"btts":0.43,"elo":1476},
    "Uruguay":      {"gf":1.71,"gc":0.86,"over25":0.57,"btts":0.43,"elo":1890},
    "France":       {"gf":2.71,"gc":0.86,"over25":1.00,"btts":0.43,"elo":2063},
    "Senegal":      {"gf":1.29,"gc":1.57,"over25":0.57,"btts":0.43,"elo":1869},
    "Iraq":         {"gf":1.29,"gc":1.14,"over25":0.43,"btts":0.43,"elo":1482},
    "Norway":       {"gf":1.71,"gc":1.14,"over25":0.57,"btts":0.57,"elo":1922},
    "Argentina":    {"gf":3.00,"gc":0.14,"over25":0.86,"btts":0.00,"elo":2113},
    "Algeria":      {"gf":1.43,"gc":0.86,"over25":0.43,"btts":0.29,"elo":1738},
    "Austria":      {"gf":1.71,"gc":0.86,"over25":0.57,"btts":0.43,"elo":1795},
    "Jordan":       {"gf":1.43,"gc":1.14,"over25":0.57,"btts":0.57,"elo":1421},
    "Portugal":     {"gf":2.71,"gc":0.71,"over25":0.86,"btts":0.43,"elo":1976},
    "DR Congo":     {"gf":1.14,"gc":0.29,"over25":0.29,"btts":0.14,"elo":1501},
    "Uzbekistan":   {"gf":1.00,"gc":1.43,"over25":0.43,"btts":0.43,"elo":1495},
    "Colombia":     {"gf":1.80,"gc":1.20,"over25":0.80,"btts":0.60,"elo":1998},
    "England":      {"gf":2.57,"gc":0.43,"over25":0.86,"btts":0.14,"elo":2042},
    "Croatia":      {"gf":1.71,"gc":1.29,"over25":0.71,"btts":0.57,"elo":1933},
    "Ghana":        {"gf":1.43,"gc":1.43,"over25":0.57,"btts":0.57,"elo":1776},
    "Panama":       {"gf":1.29,"gc":1.14,"over25":0.43,"btts":0.43,"elo":1699},
}

def get_resultados_wc_hoy():
    resultados = {}
    try:
        TZ = ZoneInfo("America/Bogota")
        hoy = datetime.datetime.now(TZ).strftime("%Y-%m-%d")
        url = f"https://www.thesportsdb.com/api/v1/json/123/eventsday.php?d={hoy}&l=4659"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            for e in (r.json().get("events") or []):
                gl = e.get("intHomeScore")
                gv = e.get("intAwayScore")
                if gl is None or gv is None: continue
                resultados[(e.get("strHomeTeam",""), e.get("strAwayTeam",""))] = (int(gl), int(gv))
    except: pass
    return resultados

def calcular_tabla(grupo, resultados_dict):
    equipos = GRUPOS_MUNDIAL[grupo]
    tabla = {e: {"pts":0,"pj":0,"pg":0,"pe":0,"pp":0,"gf":0,"gc":0,"dif":0} for e in equipos}
    partidos_grupo = [(loc,vis,f,h,s) for (g,loc,vis,f,h,s) in FIXTURE_GRUPOS if g==grupo]
    for loc,vis,fecha,hora,sede in partidos_grupo:
        if (loc,vis) in resultados_dict:
            gl,gv = resultados_dict[(loc,vis)]
            tabla[loc]["pj"]+=1; tabla[vis]["pj"]+=1
            tabla[loc]["gf"]+=gl; tabla[loc]["gc"]+=gv
            tabla[vis]["gf"]+=gv; tabla[vis]["gc"]+=gl
            tabla[loc]["dif"]=tabla[loc]["gf"]-tabla[loc]["gc"]
            tabla[vis]["dif"]=tabla[vis]["gf"]-tabla[vis]["gc"]
            if gl>gv: tabla[loc]["pts"]+=3; tabla[loc]["pg"]+=1; tabla[vis]["pp"]+=1
            elif gl==gv: tabla[loc]["pts"]+=1; tabla[loc]["pe"]+=1; tabla[vis]["pts"]+=1; tabla[vis]["pe"]+=1
            else: tabla[vis]["pts"]+=3; tabla[vis]["pg"]+=1; tabla[loc]["pp"]+=1
    return sorted(tabla.items(), key=lambda x:(-x[1]["pts"],-x[1]["dif"],-x[1]["gf"]))
