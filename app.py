import os
import requests
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
app = Flask(__name__)
API_KEY = os.environ.get("API_KEY", "").strip()
H = {"x-apisports-key": API_KEY}
B = "https://v3.football.api-sports.io"
CACHE = {}

def get_all(date_demande=None):
    if date_demande:
        dates = [date_demande]
    else:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        tom = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
        dates = [today, tom]
    for d in dates:
        try:
            r = requests.get(B + "/fixtures", headers=H, params={"date": d, "timezone": "Africa/Lubumbashi"}, timeout=15)
            j = r.json()
            # Si API dit erreur, on l'affiche dans les logs
            if "errors" in j and j["errors"]:
                print("API ERROR:", j["errors"], "status:", r.status_code)
                continue
            data = j.get("response", [])
            print(f"DATE {d} -> {len(data)} matchs - status {r.status_code}")
            if data:
                # MOISE: on prend seulement 40 matchs pour ne pas finir les 100 requetes gratuites
                return data[:40]
        except Exception as e:
            print("ERREUR get_all:", e)
            pass
    return []

def get_stand(lid, season):
    if lid in CACHE:
        return CACHE[lid]
    try:
        r = requests.get(B + "/standings", headers=H, params={"league": lid, "season": season}, timeout=10)
        cr = r.json().get("response", [])
        st = cr[0]["league"]["standings"][0] if cr else []
        d = {}
        for t in st:
            p = t["all"]["played"] or 1
            tid = t["team"]["id"]
            d[tid] = {"ppg": t["points"] / p, "gf": t["all"]["goals"]["for"] / p, "ga": t["all"]["goals"]["against"] / p}
        CACHE[lid] = d
        return d
    except Exception as e:
        print("ERREUR standings:", e)
        CACHE[lid] = {}
        return {}

def vrai_prono(m):
    try:
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
            pct = max(55, min(88, pct))
            return "1X", round(100 / pct, 2), pct
        if p2 > p1 and p2 >= px:
            pct = int(p2 + px * 0.6)
            pct = max(55, min(88, pct))
            return "X2", round(100 / pct, 2), pct
        pct = int(px + min(p1, p2) * 0.4)
        pct = max(50, min(75, pct))
        return "12", round(100 / pct, 2), pct
    except:
        return "1X", 1.50, 67

def statut(m):
    s = m["fixture"]["status"]["short"]
    el = m["fixture"]["status"]["elapsed"]
    if s in ["FT", "AET", "PEN"]:
        return "TERMINÉ"
    if s in ["1H", "2H", "HT", "ET", "BT", "P"]:
        return "LIVE " + str(el) + "'" if el else "LIVE"
    return m["fixture"]["date"][11:16]

@app.route("/debug")
def debug():
    # MOISE: pour tester si ta cle marche
    try:
        r = requests.get(B + "/status", headers=H, timeout=10)
        return jsonify({"key_len": len(API_KEY), "key_start": API_KEY[:4] + "****" if API_KEY else "VIDE", "status_code": r.status_code, "api_response": r.json()})
    except Exception as e:
        return jsonify({"error": str(e), "key_len": len(API_KEY)})

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
    if not ms:
        h += "<div style='padding:30px;text-align:center'><h3>Aucun match pour le moment</h3><p>Reviens dans 10 minutes.<br>API en cours de chargement.</p></div>"
    for i, m in enumerate(ms):
        if i % 10 == 0 and i != 0:
            h += "<div class='pub'><b>VOTRE PUB ICI - MONDE ENTIER</b><br><b>Ta Boutique Ici - 5$ / semaine</b><br>Contact WhatsApp</div>"
        st = statut(m)
        p, cote, pct = vrai_prono(m)
        cls = "ft" if st == "TERMINÉ" else "st"
        gh = m["goals"]["home"] if m["goals"]["home"] is not None else ""
        ga = m["goals"]["away"] if m["goals"]["away"] is not None else ""
        hn = m["teams"]["home"]["name"]
        an = m["teams"]["away"]["name"]
        ln = m["league"]["name"]
        cn = m["league"]["country"]
        fid = str(m["fixture"]["id"])
        h += "<div class='lg'>" + ln + " - " + cn + "</div>"
        h += "<a href='/match/" + fid + "'>"
        h += "<div class='mt'><div style='flex:1'>"
        h += "<div>" + hn + " <span style='float:right;font-weight:bold'>" + str(gh) + "</span></div>"
        h += "<div><span class='" + cls + "'>" + st + "</span> " + an + " <span style='float:right;font-weight:bold'>" + str(ga) + "</span></div>"
        h += "</div><div class='pr'><b>" + p + "</b><br><small>" + str(cote) + "<br>" + str(pct) + "%</small></div></div></a>"
    h += "<div class='pub'><b>VOTRE PUB ICI - MONDE ENTIER</b><br><b>Ta Boutique Ici - 5$ / semaine</b><br>Contact WhatsApp</div>"
    h += "<div class='bt'><div style='color:#00e676'>Matchs</div><div>Pronostics</div><div>Favoris</div><div>Filtre</div><div>Machine</div><div>Paris</div></div></body></html>"
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
        s += "<div style='background:#00c853;padding:12px;border-radius:10px'><b>VRAI PRONO BET MOS: " + p + " - Cote " + str(cote) + " - " + str(pct) + "%</b><br>Calcule avec classement + buts + domicile</div>"
        s += "<div style='background:#222;padding:12px;border-radius:10px;margin-top:10px'><b>" + ln + " - " + cn + "</b><br>Score: " + str(gh) + " - " + str(ga) + " - " + sl + "</div>"
        s += "<div style='background:#222;padding:12px;border-radius:10px;margin-top:10px'><h3>CLASSEMENT</h3>"
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
    date_demande = request.args.get("date")
    ms = get_all(date_demande)
    out = []
    for m in ms:
        p, cote, pct = vrai_prono(m)
        gh = m["goals"]["home"] if m["goals"]["home"] is not None else ""
        ga = m["goals"]["away"] if m["goals"]["away"] is not None else ""
        score = str(gh) + " - " + str(ga) if gh != "" else " - "
        out.append({"id": m["fixture"]["id"], "league": m["league"]["name"] + " - " + m["league"]["country"], "country": m["league"]["country"], "home": m["teams"]["home"]["name"], "away": m["teams"]["away"]["name"], "status": statut(m), "score": score, "gh": gh, "ga": ga, "prono": p, "cote": cote, "pct": pct})
    return jsonify({"matchs": out})

@app.route("/api/match/<int:fid>")
def api_match(fid):
    try:
        r = requests.get(B + "/fixtures", headers=H, params={"id": fid}, timeout=15)
        m = r.json().get("response", [])[0]
        p, cote, pct = vrai_prono(m)
        return jsonify({"id": fid, "home": m["teams"]["home"]["name"], "away": m["teams"]["away"]["name"], "league": m["league"]["name"], "country": m["league"]["country"], "gh": m["goals"]["home"], "ga": m["goals"]["away"], "status": m["fixture"]["status"]["long"], "prono": p, "cote": cote, "pct": pct})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)