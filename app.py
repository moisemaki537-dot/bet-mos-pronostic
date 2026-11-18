import os, requests
from datetime import datetime, timedelta
from flask import Flask, jsonify
app = Flask(__name__)
API_KEY = "TA_CLE_ICI"
H = {"x-apisports-key": API_KEY}
B = "https://v3.football.api-sports.io"
CACHE = {}
def get_all():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    tom = (datetime.utcnow()+timedelta(days=1)).strftime("%Y-%m-%d")
    for d in [today, tom]:
        try:
            r = requests.get(B+"/fixtures", headers=H, params={"date": d}, timeout=20)
            data = r.json().get("response", [])
            if data: return data
        except: pass
    return []
def get_stand(league_id, season):
    if league_id in CACHE: return CACHE[league_id]
    try:
        r = requests.get(B+"/standings", headers=H, params={"league": league_id, "season": season}, timeout=15)
        cr = r.json().get("response", [])
        st = cr[0]['league']['standings'][0] if cr else []
        d = {}
        for t in st:
            p = t['all']['played'] or 1
            d[t['team']['id']] = {"ppg": t['points']/p, "gf": t['all']['goals']['for']/p, "ga": t['all']['goals']['against']/p, "pts": t['points'], "rank": t['rank']}
        CACHE[league_id] = d
        return d
    except: return {}
def vrai_prono(m):
    hid = m['teams']['home']['id']; aid = m['teams']['away']['id']
    st = get_stand(m['league']['id'], m['league']['season'])
    if hid not in st or aid not in st:
        return "1X", 1.50, 67
    h = st[hid]; a = st[aid]
    fh = h["ppg"]*1.0 + (h["gf"]-h["ga"])*0.3 + 0.45
    fa = a["ppg"]*1.0 + (a["gf"]-a["ga"])*0.3
    total = fh + fa + 0.9
    p1 = (fh+0.3)/total*100
    p2 = (fa+0.2)/total*100
    px = 100 - p1 - p2
    if p1 >= p2 and p1 >= px:
        pct = int(p1+px*0.6)
        if pct > 88: pct = 88
        if pct < 55: pct = 55
        return "1X", round(100/pct, 2), pct
    if p2 > p1 and p2 >= px:
        pct = int(p2+px*0.6)
        if pct > 88: pct = 88
        if pct < 55: pct = 55
        return "X2", round(100/pct, 2), pct
    pct = int(px+min(p1,p2)*0.4)
    if pct > 75: pct = 75
    if pct < 50: pct = 50
    return "12", round(100/pct, 2), pct
def statut(m):
    s = m['fixture']['status']['short']; el = m['fixture']['status']['elapsed']
    if s in ["FT","AET","PEN"]: return "FT"
    if s in ["1H","2H","HT","ET","BT","P"]: return f"{el}'" if el else "LIVE"
    return m['fixture']['date'][11:16]
@app.route("/")
def index():
    ms = get_all()
    h = '<html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>body{background:#0a0a0a;color:#fff;font-family:Arial;margin:0;padding-bottom:70px}.hd{background:#111;padding:12px;text-align:center;font-weight:bold;font-size:20px}.lg{background:#1c1c1c;padding:8px 12px;font-weight:bold}.mt{display:flex;justify-content:space-between;background:#141414;padding:10px 12px;border-bottom:1px solid #222}.pr{background:#00c853;border-radius:6px;padding:6px 10px;text-align:center;min-width:65px;margin-left:10px}.st{color:#ff3333;font-weight:bold;font-size:12px}.ft{color:#aaa}.pub{background:#fff;color:#000;margin:12px;border-radius:10px;padding:15px;text-align:center}.bt{position:fixed;bottom:0;left:0;right:0;background:#111;display:flex;justify-content:space-around;padding:10px 0;border-top:1px solid #333;font-size:12px}a{color:#fff;text-decoration:none}</style></head><body>'
    h += '<div class="hd">BET MOS - PRONOSTICS<br><small style="font-size:13px;color:#aaa">🌍 MONDE ENTIER - VRAI CALCUL - LIVE</small></div>'
    for i, m in enumerate(ms):
        if i % 10 == 0 and i != 0:
            h += '<div class="pub"><b>VOTRE PUB ICI - MONDE ENTIER</b><br><b>Ta Boutique Ici - 5$ / semaine</b><br>Contact WhatsApp</div>'
        st = statut(m); p, cote, pct = vrai_prono(m)
        cls = "ft" if st == "FT" else "st"
        gh = m['goals']['home'] if m['goals']['home'] is not None else ''
        ga = m['goals']['away'] if m['goals']['away'] is not None else ''
        h += f'<div class="lg">🏳️ {m["league"]["name"]} - {m["league"]["country"]}</div>'
        h += f'<a href="/match/{m["fixture"]["id"]}"><div class="mt"><div style="flex:1"><div>⭐ {m["teams"]["home"]["name"]} <span style="float:right;font-weight:bold">{gh}</span></div><div><span class="{cls}">{st}</span> {m["teams"]["away"]["name"]} <span style="float:right;font-weight:bold">{ga}</span></div></div><div class="pr"><b>{p}</b><br><small>{cote}<br>{pct}%</small></div></div></a>'
    h += '<div class="pub"><b>VOTRE PUB ICI - MONDE ENTIER</b><br><b>Ta Boutique Ici - 5$ / semaine</b><br>Contact WhatsApp</div>'
    h += '<div class="bt"><div style="color:#00e676">⚽<br>Matchs</div><div>🔮<br>Pronostics</div><div>⭐<br>Favoris</div><div>🔍<br>Filtre</div><div>💎<br>Machine</div><div>🎫<br>Paris</div></div></body></html>'
    return h
@app.route("/match/<int:fid>")
def detail(fid):
    try:
        r = requests.get(B+"/fixtures", headers=H, params={"id": fid}, timeout=15)
        m = r.json().get("response", [])[0]
        p, cote, pct = vrai_prono(m)
        rs = requests.get(B+"/fixtures/statistics", headers=H, params={"fixture": fid}, timeout=15)
        stats = rs.json().get("response", [])
        rc = requests.get(B+"/standings", headers=H, params={"league": m['league']['id'], "season": m['league']['season']}, timeout=15)
        cr = rc.json().get("response", [])
        cl = cr[0]['league']['standings'][0] if cr else []
        s = f'<body style="background:#111;color:#fff;font-family:Arial;padding:12px"><a href="/" style="background:#ffcc00;color:#000;padding:8px 15px;border-radius:8px;text-decoration:none;font-weight:bold">⬅ RETOUR</a><h2>{m["teams"]["home"]["name"]} vs {m["teams"]["away"]["name"]}</h2><div style="background:#00c853;padding:12px;border-radius:10px"><b>💡 VRAI PRONO BET MOS: {p}