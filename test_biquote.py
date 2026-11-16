# test_biquote.py
# Script de test pour vérifier si biquote retourne les données macro nécessaires.

from biquote import Biquote

def main():
    bq = Biquote()

    print("=== Test 1 : Récupération des événements à fort impact US + EU ===")
    try:
        events = bq.calendar(importance="high", countries="US,EU")
    except Exception as e:
        print(f"ERREUR lors de l'appel calendar : {e}")
        return

    print(f"Nombre d'événements retournés : {len(events)}\n")

    if len(events) == 0:
        print("Aucun événement retourné. Vérifiez la connexion ou les paramètres.")
        return

    # Chercher spécifiquement NFP, CPI, FOMC
    keywords = ["Nonfarm", "Non-Farm", "CPI", "Consumer Price", "FOMC", "Federal Funds"]
    found_keywords = {kw: False for kw in keywords}

    print("=== Test 2 : Analyse des 15 premiers événements ===")
    for i, e in enumerate(events[:15]):
        name = e.get("name", "SANS NOM")
        forecast = e.get("forecast")
        actual = e.get("actual")
        previous = e.get("previous")

        print(f"[{i+1}] {name}")
        print(f"    time     : {e.get('time')}")
        print(f"    country  : {e.get('countryCode')}")
        print(f"    importance: {e.get('importance')}")
        print(f"    actual   : {actual}")
        print(f"    forecast : {forecast}")
        print(f"    previous : {previous}")
        print()

        # Vérifier si un mot-clé est présent dans le nom
        for kw in keywords:
            if kw.lower() in name.lower():
                found_keywords[kw] = True

    print("=== Test 3 : Présence des événements clés ===")
    for kw, found in found_keywords.items():
        status = "TROUVÉ" if found else "non trouvé dans cet échantillon"
        print(f"  {kw} : {status}")

    print("\n=== Test 4 : Vérification critique du champ 'forecast' ===")
    events_with_forecast = [e for e in events if e.get("forecast") is not None]
    print(f"Événements avec une valeur forecast non-null : {len(events_with_forecast)} / {len(events)}")
    if len(events_with_forecast) == 0:
        print("ALERTE : Aucun forecast disponible. Cette source ne permet PAS de comparer le résultat au consensus.")
    else:
        print("OK : Des valeurs forecast sont présentes.")
        # Afficher un exemple
        example = events_with_forecast[0]
        print(f"Exemple : {example.get('name')} -> forecast = {example.get('forecast')}, actual = {example.get('actual')}")

if __name__ == "__main__":
    main()