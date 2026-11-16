# analyse_macro.py
import requests
from datetime import datetime, timezone
from config_macro import FRED_API_KEY

def get_fred_events():
    events = []
    annee_actuelle = datetime.now(timezone.utc).year
    
    fred_releases = {
        "50": "Nonfarm Payrolls (NFP)",
        "10": "US CPI (Inflation)",
        "101": "FOMC Meeting (Taux d'intérêt)"
    }

    for release_id, nom in fred_releases.items():
        url = f"https://api.stlouisfed.org/fred/release/dates?release_id={release_id}&api_key={FRED_API_KEY}&file_type=json&realtime_start={annee_actuelle}-01-01&realtime_end={annee_actuelle}-12-31&include_release_dates_with_no_data=true"
        try:
            response = requests.get(url, timeout=10)
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

def get_all_macro_events():
    events = get_fred_events()
    events.sort(key=lambda x: x["time"])
    return events

def check_alerts():
    now = datetime.now(timezone.utc)
    events = get_all_macro_events()
    alertes_a_envoyer = []
    
    for e in events:
        time_diff = e["time"] - now
        minutes_diff = time_diff.total_seconds() / 60
        
        if 0 < minutes_diff <= 120:
            alertes_a_envoyer.append({"type": "PRE", "event": e, "minutes_restantes": int(minutes_diff)})
            
        elif -45 <= minutes_diff < -30:
            alertes_a_envoyer.append({"type": "POST", "event": e, "minutes_ecoulees": int(abs(minutes_diff))})
            
    return alertes_a_envoyer
