# analyse_macro.py
import requests
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from config_macro import FRED_API_KEY

def get_fred_events():
    events = []
    annee_actuelle = datetime.now(timezone.utc).year
    fred_releases = {"50": "Nonfarm Payrolls (NFP)", "10": "US CPI (Inflation)"}
    for release_id, nom in fred_releases.items():
        url = f"https://api.stlouisfed.org/fred/release/dates?release_id={release_id}&api_key={FRED_API_KEY}&file_type=json&realtime_start={annee_actuelle}-01-01&realtime_end={annee_actuelle}-12-31&include_release_dates_with_no_data=true"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            for d in data.get('release_dates', []):
                dt = datetime.strptime(d['date'], "%Y-%m-%d").replace(hour=13, minute=30, tzinfo=timezone.utc)
                events.append({
                    "name": nom, "time": dt, "countryCode": "US",
                    "forecast": None, "actual": None, "previous": None, "source": "FRED"
                })
        except Exception as e:
            print(f"Erreur FRED pour {nom}: {e}")
    return events

def get_forexfactory_events():
    """Récupère les événements via le flux RSS de Forex Factory."""
    events = []
    url = "https://www.forexfactory.com/ffcal_week_this.xml"
    try:
        # On demande le flux XML avec un timeout de 10s
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        
        # On parcourt les événements
        for item in root.findall('.//event'):
            impact = item.findtext('impact', '')
            # On ne garde que les événements à fort impact (High)
            if impact.lower() == 'high':
                name = item.findtext('title', '')
                date_str = item.findtext('date', '')
                country = item.findtext('country', '')
                forecast = item.findtext('forecast', '')
                previous = item.findtext('previous', '')
                
                # Conversion de la date (format ForexFactory : ex "11-17-2026 13:30:00")
                if date_str:
                    dt = datetime.strptime(date_str, "%m-%d-%Y %H:%M:%S").replace(tzinfo=timezone.utc)
                    events.append({
                        "name": name, "time": dt, "countryCode": country,
                        "forecast": forecast if forecast else None,
                        "actual": None, "previous": previous if previous else None, "source": "ForexFactory"
                    })
    except Exception as e:
        print(f"Erreur ForexFactory: {e}")
    return events

def get_all_macro_events():
    fred_events = get_fred_events()
    ff_events = get_forexfactory_events()
    
    all_events = []
    all_events.extend(ff_events)
    
    # On fusionne et on évite les doublons
    for fe in fred_events:
        is_duplicate = False
        for be in ff_events:
            if fe["name"].lower() in be["name"].lower() and abs((fe["time"] - be["time"]).total_seconds()) < 3600:
                is_duplicate = True
                break
        if not is_duplicate:
            all_events.append(fe)
            
    all_events.sort(key=lambda x: x["time"])
    return all_events

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
