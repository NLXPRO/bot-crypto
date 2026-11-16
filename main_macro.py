# main_macro.py
import time
import requests
from datetime import datetime, timezone
from config_macro import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from analyse_macro import check_alerts

def envoyer_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Message Telegram envoyé avec succès.")
    except Exception as e:
        print(f"Erreur d'envoi Telegram : {e}")

def formater_alerte_pre(event, minutes):
    nom = event['name']
    heure_locale = event['time'].astimezone().strftime('%H:%M')
    
    msg = f"⚠️ <b>ALERTE MACRO : ANNONCE IMMINENTE</b> ⚠️\n\n"
    msg += f"📊 <b>Événement :</b> {nom}\n"
    msg += f"⏰ <b>Heure :</b> {heure_locale} (dans {minutes} min)\n"
    msg += f"🌍 <b>Zone :</b> {event['countryCode']}\n\n"
    if event.get('forecast') is not None:
        msg += f"📈 <b>Prévision :</b> {event['forecast']}\n"
        msg += f"📉 <b>Précédent :</b> {event['previous']}\n\n"
    
    msg += "🛑 <b>CONSEIL :</b> Ne prenez pas de nouvelle position maintenant. La volatilité va exploser. Protégez vos stops."
    return msg

def formater_alerte_post(event, minutes):
    nom = event['name']
    
    msg = f"✅ <b>RÉSULTAT MACRO</b> ✅\n\n"
    msg += f"📊 <b>Événement :</b> {nom}\n"
    msg += f"🌍 <b>Zone :</b> {event['countryCode']}\n\n"
    
    actual = event.get('actual')
    forecast = event.get('forecast')
    
    if actual is not None:
        msg += f"🎯 <b>Résultat (Actual) :</b> {actual}\n"
        if forecast is not None:
            msg += f"📈 <b>Prévision :</b> {forecast}\n"
            try:
                act_val = float(str(actual).replace('%', ''))
                fc_val = float(str(forecast).replace('%', ''))
                if act_val > fc_val:
                    msg += "\n🟢 <i>Meilleur que prévu (Haussier pour la monnaie).</i>\n"
                elif act_val < fc_val:
                    msg += "\n🔴 <i>Moins bon que prévu (Baissier pour la monnaie).</i>\n"
                else:
                    msg += "\n⚪ <i>Conforme aux attentes.</i>\n"
            except ValueError:
                pass
    else:
        msg += "⏳ <i>Donnée réelle pas encore disponible dans notre source.</i>\n"
        
    msg += "\n💡 <b>Action :</b> Surveillez la réaction des marchés. La tendance crypto (ex: BTC) peut réagir violemment."
    return msg

def boucle_principale():
    print("Démarrage du bot Macro. En attente d'événements...")
    alertes_deja_envoyees = set()
    
    while True:
        try:
            alertes = check_alerts()
            
            for a in alertes:
                event = a["event"]
                event_id = f"{a['type']}_{event['name']}_{event['time']}"
                
                if event_id not in alertes_deja_envoyees:
                    print(f"Nouvelle alerte détectée : {a['type']} pour {event['name']}")
                    
                    if a["type"] == "PRE":
                        message = formater_alerte_pre(event, a["minutes_restantes"])
                    else:
                        message = formater_alerte_post(event, a["minutes_ecoulees"])
                        
                    envoyer_telegram(message)
                    alertes_deja_envoyees.add(event_id)
            
        except Exception as e:
            print(f"Erreur dans la boucle principale : {e}")
            
        time.sleep(300)

if __name__ == "__main__":
    boucle_principale()