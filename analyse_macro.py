# analyse_macro.py
import requests
from datetime import datetime, timezone
from config_macro import FRED_API_KEY, BIQUOTE_KEYWORDS
from biquote import Biquote

def get_fred_events():
    """Récupère les dates NFP et CPI depuis FRED et les formate comme Biquote."""
    events = []
    annee_actuelle = datetime.now(timezone.utc).year
    
    # Dictionnaire des séries FRED : ID -> Nom lisible
    fred_releases = {
        "50": "Nonfarm Payrolls (NFP)",
        "10": "US CPI (Inflation)"
    }

    for release_id, nom in fred_releases.items():
        url = f"https://api.stlouisfed.org/fred/release/dates?release_id={release_id}&api_key={FRED_API_KEY}&file_type=json&realtime_start={annee_actuelle}-01-01&realtime_end={annee_actuelle}-12-31&include_release_dates_with_no_data=true"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            for d in data.get('release_dates', []):
                dt = datetime.strptime(d['date'], "%Y-%m-%d").replace(hour=13, minute=30, tzinfo=timezone.utc)
                
                events.append({
                    "name": nom,
                    "time": dt,
                    "countryCode": "US",
                    "forecast": None,
                    "actual": None,
                    "previous": None,
                    "source": "FRED"
                })
        except Exception as e:
            print(f"Erreur FRED pour {nom}: {e}")
            
    return events

def get_biquote_events():
    """Récupère les événements depuis Biquote."""
    bq = Biquote()
    events = []
    try:
        raw_events = bq.calendar(importance="high", countries="US,EU")
        
        for e in raw_events:
            name = e.get("name", "")
            if any(kw.lower() in name.lower() for kw in BIQUOTE_KEYWORDS):
                dt = datetime.fromisoformat(e.get("time").replace("Z", "+00:00"))
                events.append({
                    "name": name,
                    "time": dt,
                    "countryCode": e.get("countryCode"),
                    "forecast": e.get("forecast"),
                    "actual": e.get("actual"),
                    "previous": e.get("previous"),
                    "source": "Biquote"
                })
    except Exception as e:
        print(f"Erreur Biquote: {e}")
        
    return events

def get_all_macro_events():
    """Fusionne les événements FRED et Biquote sans faire de doublons."""
    fred_events = get_fred_events()
    biquote_events = get_biquote_events()
    
    all_events = []
    all_events.extend(biquote_events)
    
    for fe in fred_events:
        is_duplicate = False
        for be in biquote_events:
            if fe["name"].lower() in be["name"].lower() and abs((fe["time"] - be["time"]).total_seconds()) < 3600:
                is_duplicate = True
                break
        if not is_duplicate:
            all_events.append(fe)
            
    all_events.sort(key=lambda x: x["time"])
    return all_events

def check_alerts():
    """Vérifie s'il y a des alertes à envoyer maintenant."""
    now = datetime.now(timezone.utc)
    events = get_all_macro_events()
    
    alertes_a_envoyer = []
    
    for e in events:
        time_diff = e["time"] - now
        minutes_diff = time_diff.total_seconds() / 60
        
        if 0 < minutes_diff <= 120:
            alertes_a_envoyer.append({
                "type": "PRE",
                "event": e,
                "minutes_restantes": int(minutes_diff)
            })
            
        elif -45 <= minutes_diff < -30:
            alertes_a_envoyer.append({
                "type": "POST",
                "event": e,
                "minutes_ecoulees": int(abs(minutes_diff))
            })
            
    return alertes_a_envoyer