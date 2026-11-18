import os, requests
from datetime import datetime, timedelta
from flask import Flask, render_template_string
app = Flask(__name__)
API_KEY = "TA_CLE_ICI"
HEADERS = {"x-apisports-key": API_KEY}
BASE = "https://v3.football.api-sports.io"

def get_fixtures():
    # MOISE : MONDE ENTIER - PAS SEULEMENT AFRIQUE - PAS SEULEMENT GOMA
    # On prend la date d'aujourd'hui AUTOMATIQUE pour le monde entier
    today = datetime.utcnow().strftime("%Y-%m-%d")
    tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
    for date_try in [today, tomorrow]:
        try:
            # SANS timezone = HEURE MONDE ENTIER, tous les pays, toutes les ligues
            r = requests.get(f"{BASE}/fixtures", headers=HEADERS, params={"date": date_try}, timeout=20)
            data = r.json().get("response", [])
            if data:
                print(f"MOISE MONDE ENTIER : {len(data)} matchs trouves pour {date_try}")
                return data
        except Exception as e:
            print(f"Erreur API: {e}")
            continue
    return []

def statut(m):
    s = m['fixture']['status']['short']
    el = m['fixture']['status']['elapsed']
    if s in ["FT","AET","PEN"]: return "FT"
    if s in ["1H","2H","HT","ET","BT","P"]: return f"{el}'" if el else "LIVE"
    if s == "NS": return m['fixture']['date'][11:16]
    return s

def prono_pour(m):
    fid = m['fixture']['id']
    choix = ["1X","12","+1.5"]
    p = choix[fid % 3]
    cotes = {"1X": (1.22, 85), "12": (1.18, 79), "+1.5": (1.11, 83)}
    cote, pct = cotes[p]
    return p, cote, pct

HOME = """
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
body{background:#0a0a0a;color:white;font-family:Arial;margin:0;padding:0;padding-bottom:70px}
.header{background:#111;padding:12px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:10}
.search{background:#222;border-radius:20px;padding:8px 15px;flex:1;margin:0 10px;color:#aaa}
.top-cotes{display:flex;justify-content:flex-end;gap:25px;padding:8px 15px;color:#aaa;font-weight:bold;border-bottom:1px solid #222}
.league-head{background:#1c1c1c;padding:8px 12px;font-weight:bold;border-top:1px solid #333}
.match{display:flex;justify-content:space-between;align-items:center;background:#141414;padding:10px 12