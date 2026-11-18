from flask import Flask, render_template_string, request
import random

app = Flask(__name__)

MATCHS = [
    {"equipe1": "TP Mazembe", "equipe2": "AS Vita Club", "ligue": "Linafoot - RD Congo", "heure": "15:30"},
    {"equipe1": "Real Madrid", "equipe2": "FC Barcelone", "ligue": "La Liga - Espagne", "heure": "20:00"},
    {"equipe1": "Man City", "equipe2": "Arsenal", "ligue": "Premier League", "heure": "17:30"},
    {"equipe1": "PSG", "equipe2": "Marseille", "ligue": "Ligue 1 - France", "heure": "20:45"},
    {"equipe1": "AS Maniema", "equipe2": "FC Lupopo", "ligue": "Linafoot - RD Congo", "heure": "15:00"},
]

HTML = """
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bet Mos Pronostic</title>
<style>
body{font-family:Arial;background:#0a1a0a;color:white;margin:0;padding:15px}
h1{text-align:center;color:#FFD700}
.card{background:#1a2a1a;border:2px solid #FFD700;border-radius:15px;padding:15px;margin:12px 0}
button{background:#FFD700;border:none;padding:12px 20px;border-radius:10px;font-weight:bold;width:100%;font-size:16px}
input,select{width:100%;padding:12px;margin:8px 0;border-radius:10px;border:none}
.badge{background:green;padding:5px 10px;border-radius:20px;font-size:12px}
.confiance{color:#FFD700;font-weight:bold}
</style></head>
<body>
<h1>⚽ BET MOS PRONOSTIC ⚽</h1>
<p style="text-align:center">Pronostics gratuits - Goma, RD Congo 🇨🇩</p>
<form method="post">
<label>Choisis ton match :</label>
<select name="match">
{% for m in matchs %}
<option value="{{ loop.index0 }}">{{ m.equipe1 }} vs {{ m.equipe2 }} - {{ m.heure }}</option>
{% endfor %}
</select>
<button type="submit">VOIR MON PRONOSTIC 🔥</button>
</form>
{% if resultat %}
<div class="card">
<h2>{{ resultat.match.equipe1 }} vs {{ resultat.match.equipe2 }}</h2>
<p>{{ resultat.match.ligue }} - {{ resultat.match.heure }}</p>
<p><span class="badge">{{ resultat.choix }}</span></p>
<p class="confiance">Confiance : {{ resultat.confiance }}% ⭐</p>
<p>Score probable : <b>{{ resultat.score }}</b></p>
<p>Conseil : {{ resultat.conseil }}</p>
</div>
{% endif %}
<h2>📅 Matchs du jour</h2>
{% for m in matchs %}
<div class="card"><b>{{ m.equipe1 }} vs {{ m.equipe2 }}</b><br>{{ m.ligue }}<br>Heure : {{ m.heure }}</div>
{% endfor %}
<p style="text-align:center;font-size:12px">Joue responsable. 18+ - Bet Mos Pronostic</p>
</body></html>
"""

@app.route("/", methods=["GET","POST"])
def index():
    resultat = None
    if request.method == "POST":
        try:
            idx = int(request.form.get("match", 0))
        except:
            idx = 0
        m = MATCHS[idx]
        choix = random.choice(["Victoire " + m["equipe1"], "Match Nul", "Victoire " + m["equipe2"], "Plus de 1.5 buts", "Les 2 équipes marquent"])
        resultat = {
            "match": m,
            "choix": choix,
            "confiance": random.randint(65, 92),
            "score": random.choice(["2-1", "1-0", "1-1", "2-0", "1-2"]),
            "conseil": "Mise petit, analyse d'abord. Ne mise jamais tout ton argent."
        }
    return render_template_string(HTML, matchs=MATCHS, resultat=resultat)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
