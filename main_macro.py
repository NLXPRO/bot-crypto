# main_macro.py
import requests
from config_macro import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from analyse_macro import check_alerts

def envoyer_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"Erreur Telegram ({response.status_code}) : {response.text}")
        else:
            print("Message Macro envoyé.")
    except Exception as e:
        print(f"Erreur réseau Telegram : {e}")

def formater_alerte_pre(event, minutes):
    nom = event['name']
    heure_locale = event['time'].astimezone().strftime('%H:%M')
    msg = f"⚠️ <b>ALERTE MACRO : ANNONCE IMMINENTE</b> ⚠️\n\n"
    msg += f"📊 <b>Événement :</b> {nom}\n"
    msg += f"⏰ <b>Heure :</b> {heure_locale} (dans {minutes} min)\n"
    msg += f"🌍 <b>Zone :</b> {event['countryCode']}\n\n"
    msg += "🛑 <b>CONSEIL :</b> Ne prenez pas de nouvelle position maintenant. La volatilité va exploser. Protégez vos stops."
    return msg

def formater_alerte_post(event, minutes):
    nom = event['name']
    msg = f"✅ <b>RÉSULTAT MACRO</b> ✅\n\n"
    msg += f"📊 <b>Événement :</b> {nom}\n"
    msg += f"🌍 <b>Zone :</b> {event['countryCode']}\n\n"
    msg += "⏳ <i>Consultez votre plateforme pour voir le résultat exact (FRED ne fournit pas le consensus en temps réel).</i>\n"
    msg += "\n💡 <b>Action :</b> Surveillez la réaction des marchés."
    return msg

def main():
    print("Vérification Macro (exécution unique)...")
    try:
        alertes = check_alerts()
        for a in alertes:
            event = a["event"]
            print(f"Alerte détectée : {a['type']} pour {event['name']}")
            if a["type"] == "PRE":
                message = formater_alerte_pre(event, a["minutes_restantes"])
            else:
                message = formater_alerte_post(event, a["minutes_ecoulees"])
            envoyer_telegram(message)
    except Exception as e:
        print(f"Erreur globale : {e}")

if __name__ == "__main__":
    main()
