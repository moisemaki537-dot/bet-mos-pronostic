import os, requests
from datetime import date
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# --- CLE DANS LE SERVEUR, MOISE ---
# On ne met PAS la cle ici, Moise ! On la met dans Render -> Environment Variables
# Nom: API_FOOTBALL_KEY / Valeur: ta cle
API_KEY = os.environ.get("API_FOOTBALL_KEY", "")
VIP_CODE = os.environ.get("VIP_CODE", "MOSVIP2026")

# --- MATCHS EXEMPLE, MOISE, SI PAS DE CLE ---
DEMO_MATCHS = [
    {"league": "Linafoot - RDC", "home": "TP Mazembe", "away": "AS Vita Club", "time": "15:30", "prono": "1X - Victoire Mazembe ou Nul", "cote": "1.45", "vip": False},
    {"league": "Premier League", "home": "Arsenal", "away": "Chelsea", "time": "17:30", "prono": "Plus de 1.5 Buts", "cote": "1.35", "vip": False},
    {"league": "La Liga", "home": "Real Madrid", "away": "Sevilla", "time": "20:00", "prono": "Victoire Real Madrid", "cote": "1.55", "vip": True},
    {"league": "Serie A", "home": "Inter", "away": "Napoli", "time": "20:45", "prono": "BTTS - Les 2 equipes marquent", "cote": "1.80", "vip": True},
]

def get_matchs_reels():
    if not API_KEY:
        return DEMO_MATCHS, False
    try:
        today = date.today().isoformat()
        r = requests.get(
            "https://v3.football.api-sports.io/fixtures",
            params={"date": today, "status": "NS"},
            headers={"x-apisports-key": API_KEY},
            timeout=10
        )
        data = r.json().get("response", [])[:10]
        matchs = []
        for m in data:
            matchs.append({
                "league": m["league"]["name"],
                "home": m["teams"]["home"]["name"],
                "away": m["teams"]["away"]["name"],
                "time": m["fixture"]["date"][11:16],
                "prono": "1X - Analyse en cours",
                "cote": "1.50",
                "vip": False
            })
        if not matchs:
            return DEMO_MATCHS, False
        return matchs, True
    except Exception:
        return DEMO_MATCHS, False

HTML = """
<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BET MOS - Pronostics Reels</title>
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#0a7a42">
<style>
body{margin:0;font-family:Arial;background:#0b1f14;color:white}
.header{background:#0a7a42;padding:14px;text-align:center;font-weight:900;font-size:22px}
.pub{background:#ffcc00;color:black;padding:10px;text-align:center;font-weight:800;margin:10px;border-radius:10px}
.pub small{display:block;font-weight:400}
.card{background:#162e21;margin:10px;padding:12px;border-radius:12px}
.badge{background:#ffcc00;color:black;padding:2px 8px;border-radius:20px;font-size:12px;font-weight:800}
.btn{background:#ffcc00;color:black;border:0;padding:12px;width:100%;border-radius:10px;font-weight:900;font-size:16px;margin-top:10px}
input{width:100%;padding:12px;border-radius:10px;border:0;margin-top:8px;box-sizing:border-box}
.vip-lock{background:#2a1a00;border:2px dashed #ffcc00}
.install{background:white;color:#0a7a42;padding:10px;text-align:center;font-weight:800;margin:10px;border-radius:10px}
</style></head><body>
<div class="header">BET MOS - PRONOSTICS REELS</div>
<div class="pub">VOTRE PUB ICI - GOMA<br><small>Contact WhatsApp pour mettre ta boutique ici - 5$ / semaine</small></div>
<div class="install" id="installBox" style="display:none"><button onclick="installer()" style="border:0;background:#0a7a42;color:white;padding:8px 14px;border-radius:8px;font-weight:800">INSTALLER L'APPLICATION SUR MON TELEPHONE</button></div>
<div style="padding:0 10px">Statut: {% if reel %}MATCHS REELS - API Connectee{% else %}MODE DEMO - Mets ta cle API dans Render pour les vrais matchs{% endif %}</div>
{% for m in matchs %}
{% if not m.vip %}
<div class="card"><span class="badge">{{m.league}}</span> <b style="float:right">{{m.time}}</b><br><br><b>{{m.home}} vs {{m.away}}</b><br>Prono: {{m.prono}}<br>Cote: {{m.cote}}</div>
{% endif %}
{% endfor %}
<div class="card vip-lock">
<h2>ZONE VIP - PRONOSTICS SURS</h2>
<p>Entre ton CODE VIP apres paiement Airtel Money / Orange Money</p>
<form method="POST" action="/vip"><input name="code" placeholder="Entre ton CODE VIP ici"><button class="btn">DEBLOQUER LE VIP</button></form>
{% if msg %}<p><b>{{msg}}</b></p>{% endif %}
{% if vip_matchs %}
{% for m in vip_matchs %}<div style="background:#3a2a00;padding:10px;border-radius:10px;margin-top:8px"><b>VIP: {{m.home}} vs {{m.away}}</b><br>{{m.prono}} - Cote {{m.cote}}</div>{% endfor %}
{% endif %}
</div>
<div class="pub">VOTRE PUB ICI<br><small>Ton restaurant, ton salon, ta boutique a Goma - Contacte BET MOS</small></div>
<p style="text-align:center;opacity:.7">BET MOS - Goma, RDC | WhatsApp pour VIP</p>
<script>
let deferredPrompt;
window.addEventListener('beforeinstallprompt', e=>{e.preventDefault();deferredPrompt=e;document.getElementById('installBox').style.display='block'});
function installer(){if(deferredPrompt){deferredPrompt.prompt()}}
if('serviceWorker' in navigator){navigator.serviceWorker.register('/sw.js')}
</script></body></html>
"""

@app.route("/", methods=["GET"])
def home():
    matchs, reel = get_matchs_reels()
    return render_template_string(HTML, matchs=matchs, reel=reel, vip_matchs=[], msg="")

@app.route("/vip", methods=["POST"])
def vip():
    code = request.form.get("code", "").strip()
    matchs, reel = get_matchs_reels()
    if code == VIP_CODE:
        vip_matchs = [m for m in matchs if m["vip"]] or DEMO_MATCHS[2:]
        return render_template_string(HTML, matchs=matchs, reel=reel, vip_matchs=vip_matchs, msg="VIP DEBLOQUE, MOISE ! Bienvenue !")
    return render_template_string(HTML, matchs=matchs, reel=reel, vip_matchs=[], msg="Mauvais code, Moise ! Paie d'abord sur WhatsApp !")

@app.route("/manifest.json")
def manifest():
    return jsonify({"name": "BET MOS", "short_name": "BET MOS", "start_url": "/", "display": "standalone", "background_color": "#0a7a42", "theme_color": "#0a7a42", "icons": []})

@app.route("/sw.js")
def sw():
    return "self.addEventListener('fetch', e=>{})", 200, {"Content-Type": "application/javascript"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))