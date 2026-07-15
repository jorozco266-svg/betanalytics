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
    "Mexico":         {"gf":2.57,"gc":0.71,"over25":0.71,"btts":0.43,"elo":2000, "fuente":"2026: 5-1 Serbia · 4-0 Nicaragua · 2-0 Ecuador | 2025: Copa Oro (4V fase grupos)"},
    "South Africa":   {"gf":1.29,"gc":1.14,"over25":0.57,"btts":0.43,"elo":1312, "fuente":"2026: amistosos de preparación | 2025: AFCON + clasificatorias CAF"},
    "South Korea":    {"gf":1.71,"gc":0.86,"over25":0.57,"btts":0.29,"elo":1789, "fuente":"2026: 1-0 El Salvador | 2025: clasificatorias AFC (eliminó a Iraq en playoff)"},
    "Czechia":        {"gf":1.57,"gc":1.29,"over25":0.57,"btts":0.57,"elo":1748, "fuente":"2026: playoff vs Irlanda 2-2 (4-3 pen) · vs Dinamarca 2-2 (3-1 pen) | 2025: Nations League"},
    "Canada":         {"gf":1.57,"gc":0.86,"over25":0.57,"btts":0.43,"elo":1469, "fuente":"2026: 2-1 Irlanda · 1-1 Irlanda | 2025: Copa Oro campeón · Concacaf Nations League"},
    "Bosnia":         {"gf":1.43,"gc":1.29,"over25":0.57,"btts":0.43,"elo":1571, "fuente":"2026: playoff ganado | 2025: Nations League UEFA — Džeko retirado"},
    "Qatar":          {"gf":1.14,"gc":1.29,"over25":0.43,"btts":0.43,"elo":1365, "fuente":"2026: 0-0 El Salvador | 2025: Copa Árabe + clasificatorias AFC"},
    "Switzerland":    {"gf":1.71,"gc":0.86,"over25":0.57,"btts":0.43,"elo":1897, "fuente":"2026: 1-1 Australia | 2025: Nations League — Shaqiri, Xhaka, Akanji"},
    "Brazil":         {"gf":2.43,"gc":0.86,"over25":0.86,"btts":0.43,"elo":1979, "fuente":"2026: 2-1 Egipto · 6-2 Panamá · 1-2 Francia | 2025: eliminatorias CONMEBOL (5°)"},
    "Morocco":        {"gf":2.57,"gc":0.43,"over25":0.71,"btts":0.14,"elo":1845, "fuente":"2026: 5-0 Madagascar · 2-1 Noruega | 2025: clasificatorias CAF invicto"},
    "Haiti":          {"gf":1.57,"gc":1.29,"over25":0.57,"btts":0.57,"elo":1415, "fuente":"2026: 4-0 Nueva Zelanda · 2-1 Perú | 2025: Concacaf Nations League"},
    "Scotland":       {"gf":2.43,"gc":0.86,"over25":0.71,"btts":0.29,"elo":1638, "fuente":"2026: 4-0 Bolivia · 1-0 Costa de Marfil | 2025: playoffs UEFA — McTominay, Shankland"},
    "USA":            {"gf":1.57,"gc":1.43,"over25":0.57,"btts":0.57,"elo":1821, "fuente":"2026: 1-2 Alemania · 2-0 Portugal | 2025: Copa Oro — Pulisic, Reyna, Weah"},
    "Paraguay":       {"gf":1.29,"gc":1.14,"over25":0.43,"btts":0.43,"elo":1712, "fuente":"2026: 4-0 Nicaragua | 2025: eliminatorias CONMEBOL (6°) — Sanabria, Enciso"},
    "Australia":      {"gf":1.29,"gc":1.00,"over25":0.43,"btts":0.43,"elo":1812, "fuente":"2026: 1-1 Suiza | 2025: clasificatorias AFC — Hrustic, Leckie, Irvine"},
    "Turkey":         {"gf":1.86,"gc":1.14,"over25":0.71,"btts":0.57,"elo":1880, "fuente":"2026: playoff ganado vs Kosovo | 2025: Nations League — Calhanoglu, Güler"},
    "Germany":        {"gf":2.14,"gc":0.86,"over25":0.71,"btts":0.43,"elo":1910, "fuente":"2026: 2-1 USA · 4-0 Finlandia | 2025: Nations League — Musiala, Wirtz, Havertz"},
    "Curacao":        {"gf":0.86,"gc":1.71,"over25":0.43,"btts":0.29,"elo":1388, "fuente":"2026: 0-4 Escocia | 2025: Concacaf Nations League + playoffs"},
    "Ivory Coast":    {"gf":1.71,"gc":1.14,"over25":0.57,"btts":0.57,"elo":1771, "fuente":"2026: 0-1 Escocia | 2025: AFCON campeón — Zaha, Pepe, Gradel"},
    "Ecuador":        {"gf":1.71,"gc":1.00,"over25":0.57,"btts":0.43,"elo":1933, "fuente":"2026: 1-1 Países Bajos · vs México | 2025: eliminatorias CONMEBOL (2°) — Caicedo, Plata"},
    "Netherlands":    {"gf":2.00,"gc":0.86,"over25":0.71,"btts":0.43,"elo":1959, "fuente":"2026: 0-1 Argelia · 1-1 Ecuador | 2025: Nations League — Van Dijk, Gakpo, Dumfries"},
    "Japan":          {"gf":2.00,"gc":0.71,"over25":0.71,"btts":0.29,"elo":1879, "fuente":"2026: amistosos Asia | 2025: clasificatorias AFC campeón — Minamino, Endo, Kamada"},
    "Sweden":         {"gf":1.57,"gc":1.14,"over25":0.57,"btts":0.57,"elo":1565, "fuente":"2026: 2-2 Grecia · 1-2 Noruega | 2025: Nations League — Isak, Kulusevski"},
    "Tunisia":        {"gf":1.33,"gc":1.17,"over25":0.50,"btts":0.50,"elo":1508, "fuente":"2026: 0-5 Bélgica · 0-1 Austria | 2025: AFCON + clasificatorias CAF"},
    "Belgium":        {"gf":3.20,"gc":0.80,"over25":1.00,"btts":0.40,"elo":1849, "fuente":"2026: 5-0 Túnez · 2-0 Croacia | 2025: Nations League — De Bruyne, Lukaku, Doku"},
    "Egypt":          {"gf":1.43,"gc":1.14,"over25":0.57,"btts":0.57,"elo":1531, "fuente":"2026: 2-1 Brasil | 2025: AFCON + clasificatorias CAF — Salah"},
    "Iran":           {"gf":1.29,"gc":0.86,"over25":0.43,"btts":0.29,"elo":1489, "fuente":"2026: clasificatorias AFC | 2025: campeón de grupo AFC — Taremi, Jahanbakhsh"},
    "New Zealand":    {"gf":1.14,"gc":1.71,"over25":0.57,"btts":0.43,"elo":1408, "fuente":"2026: 4-0 Haití · 0-1 Inglaterra | 2025: clasificatorias OFC — Wood, Smeltz"},
    "Spain":        {"gf":1.86,"gc":0.14,"over25":0.43,"btts":0.14,"elo":2171, "fuente":"MUNDIAL 2026 (7 PJ, 13GF/1GC): 0-0 Cabo Verde · 4-0 Arabia S. · 1-0 Uruguay · 3-0 Austria · 1-0 Portugal · 2-1 Bélgica · 2-0 Francia (semi) — FINALISTA"},
    "Cape Verde":     {"gf":1.43,"gc":1.29,"over25":0.57,"btts":0.57,"elo":1312, "fuente":"2026: 2-4 Chile | 2025: AFCON + clasificatorias CAF — Tavares, Bebé"},
    "Saudi Arabia":   {"gf":1.43,"gc":1.14,"over25":0.43,"btts":0.43,"elo":1476, "fuente":"2026: 3-0 Puerto Rico | 2025: Copa Árabe: 3-1 Comoras · 0-1 Marruecos"},
    "Uruguay":        {"gf":1.71,"gc":0.86,"over25":0.57,"btts":0.43,"elo":1890, "fuente":"2026: amistosos | 2025: eliminatorias CONMEBOL (4°) — Valverde, Núñez, Araújo"},
    "France":       {"gf":2.29,"gc":0.43,"over25":0.57,"btts":0.29,"elo":2063, "fuente":"MUNDIAL 2026 (7 PJ): 3-1 Senegal · 5-0 Irak · 4-1 Noruega · 1-0 Paraguay · 2-0 Marruecos · 0-2 España (semi) — ELIMINADA, juega 3er puesto"},
    "Senegal":        {"gf":1.29,"gc":1.57,"over25":0.57,"btts":0.43,"elo":1869, "fuente":"2026: 2-3 USA | 2025: AFCON semis + clasificatorias CAF — Mané, Koulibaly"},
    "Iraq":           {"gf":1.29,"gc":1.14,"over25":0.43,"btts":0.43,"elo":1482, "fuente":"2026: playoff ganado vs Bolivia | 2025: Copa Árabe + clasificatorias AFC"},
    "Norway":         {"gf":1.71,"gc":1.14,"over25":0.57,"btts":0.57,"elo":1922, "fuente":"2026: 1-2 Marruecos · 2-1 Suecia | 2025: clasificatorias UEFA — Haaland, Strand Larsen"},
    "Argentina":    {"gf":2.57,"gc":1.00,"over25":0.71,"btts":0.71,"elo":2113, "fuente":"MUNDIAL 2026 (7 PJ, 18GF/7GC): 2-0 Argelia · 2-0 Austria · 3-1 Jordania · 3-2 Cabo Verde · 3-2 Egipto · 3-1 Suiza · 2-1 Inglaterra (semi) — FINALISTA"},
    "Algeria":        {"gf":1.43,"gc":0.86,"over25":0.43,"btts":0.29,"elo":1738, "fuente":"2026: 1-0 Países Bajos | 2025: AFCON + clasificatorias CAF — Mahrez, Benrahma"},
    "Austria":        {"gf":1.71,"gc":0.86,"over25":0.57,"btts":0.43,"elo":1795, "fuente":"2026: 1-0 Túnez | 2025: Nations League — Sabitzer, Gregoritsch, Arnautovic"},
    "Jordan":         {"gf":1.43,"gc":1.14,"over25":0.57,"btts":0.57,"elo":1421, "fuente":"2026: 2-2 Nigeria | 2025: Copa Árabe (buen torneo) — Al-Tamari"},
    "Portugal":       {"gf":2.71,"gc":0.71,"over25":0.86,"btts":0.43,"elo":1976, "fuente":"2026: 2-1 RD Congo · 0-0 Chile · 2-0 USA | 2025: Nations League — Ronaldo, Félix, Trincão"},
    "DR Congo":       {"gf":1.14,"gc":0.29,"over25":0.29,"btts":0.14,"elo":1501, "fuente":"2026: 0-0 Dinamarca · 1-0 Jamaica · 2-0 Bermudas | AFCON: 0-1 Arg · 3-0 Bot · 1-1 Sen · 1-0 Ben"},
    "Uzbekistan":     {"gf":1.00,"gc":1.43,"over25":0.43,"btts":0.43,"elo":1495, "fuente":"2026: 0-2 Canadá | 2025: clasificatorias AFC — Shomurodov, Tursunov"},
    "Colombia":       {"gf":1.80,"gc":1.20,"over25":0.80,"btts":0.60,"elo":1998, "fuente":"2026: 3-1 Costa Rica · 1-3 Francia · 1-2 Croacia | 2025: eliminatorias CONMEBOL (3°) — Díaz, James"},
    "England":      {"gf":2.00,"gc":1.00,"over25":0.71,"btts":0.57,"elo":2042, "fuente":"MUNDIAL 2026 (7 PJ): 3-2 México (oct) · vs Noruega (cuartos) · 1-2 Argentina (semi) — ELIMINADA, juega 3er puesto"},
    "Croatia":        {"gf":1.71,"gc":1.29,"over25":0.71,"btts":0.57,"elo":1933, "fuente":"2026: 2-1 Colombia · 0-2 Bélgica | 2025: eliminatorias UEFA — Modrić, Kovačić, Gvardiol"},
    "Ghana":          {"gf":1.43,"gc":1.43,"over25":0.57,"btts":0.57,"elo":1776, "fuente":"2026: sin Kudus (lesión) | 2025: AFCON + clasificatorias CAF — Partey, Ayew"},
    "Panama":         {"gf":1.29,"gc":1.14,"over25":0.43,"btts":0.43,"elo":1699, "fuente":"2026: 1-1 Bosnia · 4-2 Rep. Dominicana | 2025: Concacaf Nations League — Fajardo, Davis"},
}


# ─────────────────────────────────────────────────────────────
# FASE FINAL — Mundial 2026
# Estado al 15-jul-2026: semifinales jugadas, falta la final
# ─────────────────────────────────────────────────────────────
FIXTURE_FINAL = [
    ("3er puesto", "France",  "England",   "2026-07-18", "15:00", "Miami"),
    ("FINAL",      "Spain",   "Argentina", "2026-07-19", "14:00", "MetLife (Nueva Jersey)"),
]

RESULTADOS_SEMIS = {
    ("France", "Spain"):        (0, 2),   # España a la final
    ("England", "Argentina"):   (1, 2),   # Argentina a la final
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
