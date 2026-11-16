# test_macro.py
import requests
from datetime import datetime, timezone
from config_macro import FRED_API_KEY
from biquote import Biquote

def test_fred():
    print("=== TEST 1 : FRED (Dates NFP & CPI) ===")
    # ID des séries : 50 = Nonfarm Payrolls, 10 = CPI
    # On demande les dates de sortie pour l'année 2026
    url = f"https://api.stlouisfed.org/fred/release/dates?release_id=50&api_key={FRED_API_KEY}&file_type=json&realtime_start=2026-01-01&realtime_end=2026-12-31&include_release_dates_with_no_data=true"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # On affiche les 3 prochaines dates de NFP
        dates = [d['date'] for d in data.get('release_dates', [])]
        print(f"Prochaines dates NFP (Release 50) :")
        for d in dates[:3]:
            print(f"  - {d}")
            
    except Exception as e:
        print(f"Erreur avec FRED : {e}")
    print()

def test_biquote():
    print("=== TEST 2 : biquote (Événements à fort impact) ===")
    bq = Biquote()
    try:
        events = bq.calendar(importance="high", countries="US,EU")
        
        # On filtre pour ne garder que les événements qui nous intéressent
        keywords = ["CPI", "Retail", "Fed", "ECB", "Rate"]
        filtered = []
        for e in events:
            name = e.get("name", "")
            if any(kw.lower() in name.lower() for kw in keywords):
                filtered.append(e)

        print(f"Événements biquote retenus : {len(filtered)}")
        for e in filtered[:5]:
            print(f"  [{e.get('time')}] {e.get('name')}")
            print(f"     Forecast: {e.get('forecast')} | Previous: {e.get('previous')}")

    except Exception as e:
        print(f"Erreur avec biquote : {e}")

if __name__ == "__main__":
    test_fred()
    test_biquote()