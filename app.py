import os
import requests
from datetime import datetime, timedelta
from flask import Flask, jsonify
app = Flask(__name__)
API_KEY = "TA_CLE_ICI"
H = {"x-apisports-key": API_KEY}
B = "https://v3.football.api-sports.io"
CACHE = {}

def get_all():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    tom = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
    for d in [today, tom]:
        try:
            r = requests.get(B + "/fixtures", headers=H, params={"date": d}, timeout=20)
            data = r.json().get("response", [])
            if data:
                return data
        except:
            pass
    return []

def get_stand(lid, season):
    if lid in CACHE:
        return CACHE[lid]
    try:
        r = requests.get(B + "/standings", headers=H, params={"league": lid, "season": season}, timeout=15)
        cr = r.json().get("response", [])
        st = cr[0]["league"]["standings"][0] if cr else []
        d = {}
        for t in st:
            p = t["all"]["played"] or 1
            tid = t["team"]["id"]
            d[tid] = {}
            d[tid]["ppg"] = t["points"] / p
            d[tid]["gf"] = t["all"]["goals"]["for"] / p
            d[tid]["ga"] = t["all"]["goals"]["against"] / p
        CACHE[lid] = d
        return d
    except:
        return {}

def vrai_prono(m):
    hid = m["teams"]["home"]["id"]
    aid = m["teams"]["away"]["id"]
    lid = m["league"]["id"]
    season = m["league"]["season"]
    st = get_stand(lid, season)
    if hid not in st or aid not in st:
        return "1X", 1.50, 67
    h = st[hid]
    a = st[aid]
    fh = h["ppg"] + (h["gf"] - h["ga"]) * 0.3 + 0.45
    fa = a["ppg"] + (a["gf"] - a["ga"]) * 0.3
    total = fh + fa + 0.9
    p1 = (fh + 0.3) / total * 100
    p2 = (fa + 0.2) / total * 100
    px = 100 - p1 - p2
    if p1 >= p2 and p1 >= px:
        pct = int(p1 + px * 0.6)
        if pct > 88:
            pct = 88
        if pct < 55:
            pct = 55
        return "1X", round(100 / pct, 2), pct
    if p2 > p1 and p2 >= px:
        pct = int(p2 + px * 0.6)
        if pct > 88:
            pct = 88
        if pct < 55:
            pct = 55
        return "X2", round(100 / pct, 2), pct
    pct = int(px + min(p1, p2) * 0.4)
    if pct > 75:
        pct = 75
    if pct < 50:
        pct = 50
    return "12", round(100 / pct, 2), pct

def statut(m):
    s = m["fixture"]["status"]["short"]
    el = m["fixture"]["status"]["elapsed"]
    if s in ["FT", "AET", "PEN"]:
        return "FT"
    if s in ["1H", "2H", "HT", "ET", "BT", "P"]:
        if el:
            return str(el) + "'"
        return "LIVE"
    return m["fixture"]["date"][11:16]

@app.route("/")
def index():
    ms = get_all()
    h = "<html><head><meta name='viewport' content='width=device-width, initial-scale=1'>"
    h += "<style>body{background:#0a0a0a;color:#fff;font-family:Arial;margin:0;padding-bottom:70px}"
    h += ".hd{background:#111;padding:12px;text-align:center;font-weight:bold;font-size:20px}"
    h += ".lg{background:#1c1c1c;padding:8px 12px;font-weight:bold}"
    h += ".mt{display:flex;justify-content:space-between;background:#141414;padding:10px 12px;border-bottom:1px solid #222}"
    h += ".pr{background:#00c853;border-radius:6px;padding:6px 10px;text-align:center;min-width:65px;margin-left:10px}"
    h += ".st{color:#ff3333;font-weight:bold;font-size:12px}.ft{color:#aaa}"
    h += ".pub{background:#fff;color:#000;margin:12px;border-radius:10px;padding:15px;text-align:center}"
    h += ".bt{position:fixed;bottom:0;left:0;right:0;background:#111;display:flex;justify-content:space-around;padding:10px 0;border-top:1px solid #333;font-size:12px}"
    h += "a{color:#fff;text-decoration:none}</style></head><body>"
    h += "<div class='hd'>BET MOS - PRONOSTICS<br><small style='font-size:13px;color:#aaa'>MONDE ENTIER - VRAI CALCUL - LIVE</small></div>"
    for i, m in enumerate(ms):
        if i % 10 == 0 and i != 0:
            h += "<div class='pub'><b>VOTRE PUB ICI - MONDE ENTIER</b><br>"
            h += "<b>Ta Boutique Ici - 5$ / semaine</b><br>Contact WhatsApp</div>"
        st = statut(m)
        p, cote, pct = vrai_prono(m)
        cls = "ft" if st == "FT" else "st"
        gh = m["goals"]["home"]
        if gh is None:
            gh = ""
        ga = m["goals"]["away"]
        if ga is None:
            ga = ""
        hn = m["teams"]["home"]["name"]
        an = m["teams"]["away"]["name"]
        ln = m["league"]["name"]
        cn = m["league"]["country"]
        fid = str(m["fixture"]["id"])
        h += "<div class='lg'>" + ln + " - " + cn + "</div>"
        h += "<a href='/match/" + fid + "'>"
        h += "<div class='mt'><div style='flex:1'>"
        h += "<div>" + hn + " <span style='float:right;font-weight:bold'>" + str(gh) + "</span></div>"
        h += "<div><span class='" + cls + "'>" + st + "</span> " + an
        h += " <span style='float:right;font-weight:bold'>" + str(ga) + "</span></div>"
        h += "</div><div class='pr'><b>" + p + "</b><br><small>" + str(cote) + "<br>" + str(pct) + "%</small></div></div></a>"
    h += "<div class='pub'><b>VOTRE PUB ICI - MONDE ENTIER</b><br>"
    h += "<b>Ta Boutique Ici - 5$ / semaine</b><br>Contact WhatsApp</div>"
    h += "<div class='bt'><div style='color:#00e676'>Matchs</div><div>Pronostics</div>"
    h += "<div>Favoris</div><div>Filtre</div><div>Machine</div><div>Paris</div></div></body></html>"
    return h

@app.route("/match/<int:fid>")
def detail(fid):
    try:
        r = requests.get(B + "/fixtures", headers=H, params={"id": fid}, timeout=15)
        m = r.json().get("response", [])[0]
        p, cote, pct = vrai_prono(m)
        hn = m["teams"]["home"]["name"]
        an = m["teams"]["away"]["name"]
        ln = m["league"]["name"]
        cn = m["league"]["country"]
        gh = m["goals"]["home"]
        ga = m["goals"]["away"]
        sl = m["fixture"]["status"]["long"]
        s = "<body style='background:#111;color:#fff;font-family:Arial;padding:12px'>"
        s += "<a href='/' style='background:#ffcc00;color:#000;padding:8px 15px;border-radius:8px;text-decoration:none;font-weight:bold'>RETOUR</a>"
        s += "<h2>" + hn + " vs " + an + "</h2>"
        s += "<div style='background:#00c853;padding:12px;border-radius:10px'>"
        s += "<b>VRAI PRONO BET MOS: " + p + " - Cote " + str(cote) + " - " + str(pct) + "%</b>"
        s += "<br>Calcule avec classement + buts + domicile</div>"
        s += "<div style='background:#222;padding:12px;border-radius:10px;margin-top:10px'>"
        s += "<b>" + ln + " - " + cn + "</b><br>"
        s += "Score: " + str(gh) + " - " + str(ga) + " - " + sl + "</div>"
        s += "<div style='background:#222;padding:12px;border-radius:10px;margin-top:10px'>"
        s += "<h3>CLASSEMENT</h3>"
        rc = requests.get(B + "/standings", headers=H, params={"league": m["league"]["id"], "season": m["league"]["season"]}, timeout=15)
        cr = rc.json().get("response", [])
        cl = cr[0]["league"]["standings"][0] if cr else []
        for t in cl:
            s += str(t["rank"]) + ". " + t["team"]["name"] + " - " + str(t["points"]) + " pts<br>"
        if not cl:
            s += "Classement non dispo pour cette ligue."
        s += "</div></body>"
        return s
    except Exception as e:
        return "Erreur " + str(e) + " <a href='/'>Retour</a>"

@app.route("/api/matches")
def api_matches():
    ms = get_all()
    out = []
    for m in ms:
        p, cote, pct = vrai_prono(m)
        gh = m["goals"]["home"]
        if gh is None:
            gh = ""
        ga = m["goals"]["away"]
        if ga is None:
            ga = ""
        item = {}
        item["id"] = m["fixture"]["id"]
        item["league"] = m["league"]["name"]
        item["country"] = m["league"]["country"]
        item["home"] = m["teams"]["home"]["name"]
        item["away"] = m["teams"]["away"]["name"]
        item["status"] = statut(m)
        item["gh"] = gh
        item["ga"] = ga
        item["prono"] = p
        item["cote"] = cote
        item["pct"] = pct
        out.append(item)
    return jsonify(out)

@app.route("/api/match/<int:fid>")
def api_match(fid):
    try:
        r = requests.get(B + "/fixtures", headers=H, params={"id": fid}, timeout=15)
        m = r.json().get("response", [])[0]
        p, cote, pct = vrai_prono(m)
        item = {}
        item["id"] = fid
        item["home"] = m["teams"]["home"]["name"]
        item["away"] = m["teams"]["away"]["name"]
        item["league"] = m["league"]["name"]
        item["country"] = m["league"]["country"]
        item["gh"] = m["goals"]["home"]
        item["ga"] = m["goals"]["away"]
        item["status"] = m["fixture"]["status"]["long"]
        item["prono"] = p
        item["cote"] = cote
        item["pct"] = pct
        return jsonify(item)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)