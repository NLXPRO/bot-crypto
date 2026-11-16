# main_crypto.py
import ccxt
import time
from config_crypto import EXCHANGE_ID, PAIRES, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from analyse_crypto import analyser_paire
import requests

def envoyer_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML"}
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"⚠️ Erreur Telegram ({response.status_code}) : {response.text}")
        else:
            print("✅ Bulletin envoyé sur Telegram.")
    except Exception as e:
        print(f"Erreur réseau Telegram : {e}")

def generer_bulletin(analyse):
    if analyse is None:
        return None
        
    msg = f"🚨 <b>ALERTE TRADE : {analyse['symbole']}</b> 🚨\n"
    msg += "━━━━━━━━━━━━━━━━━━\n"
    msg += f"🌍 <b>Tendance de fond :</b> {analyse['tendance_fond']}\n"
    msg += f"⏱️ <b>Situation actuelle :</b> {analyse['situation']}\n\n"
    
    msg += f"💡 <b>ACTION RECOMMANDÉE</b>\n"
    msg += f"<b>{analyse['action']}</b>\n"
    msg += f"Montant à investir : {analyse['montant']:.2f} €\n"
    msg += f"Stop-Loss : {analyse['stop_loss']:.2f} €\n"
    msg += f"Objectif : {analyse['objectif']:.2f} €\n\n"
    msg += f"⏳ <b>Horizon de temps :</b> {analyse['horizon']}\n"
    msg += f"📊 <b>Probabilité historique :</b> {analyse['proba']} (basé sur le passé)\n"
    msg += f"<i>{analyse['note']}</i>\n"
        
    msg += "\n🔄 <i>Rappel : Alignement=Continuation | Rebond=Risqué | Vente=Short</i>"
    
    return msg

def main():
    print("Démarrage du bot Crypto (Mode Silence Activé)...")
    exchange = getattr(ccxt, EXCHANGE_ID)()
    
    derniers_statuts = {}

    # Temps d'attente en secondes (3600 = 1 heure, 900 = 15 minutes)
    TEMPS_ATTENTE = 3600 

    while True:
        try:
            for paire in PAIRES:
                print(f"Analyse de {paire}...")
                analyse = analyser_paire(exchange, paire)
                
                if analyse:
                    empreinte_actuelle = f"{analyse['action']}_{analyse['situation']}"
                    
                    if paire not in derniers_statuts or derniers_statuts[paire] != empreinte_actuelle:
                        
                        if "Attente" not in analyse['action']:
                            bulletin = generer_bulletin(analyse)
                            envoyer_telegram(bulletin)
                        else:
                            print(f"Signal 'Attente' pour {paire}. Pas de notification envoyée.")
                            
                        derniers_statuts[paire] = empreinte_actuelle
                    else:
                        print(f"Pas de changement pour {paire}.")
                        
        except Exception as e:
            print(f"Erreur dans la boucle crypto : {e}")
            
        print(f"Attente de {TEMPS_ATTENTE // 60} minutes avant la prochaine analyse...")
        try:
            time.sleep(TEMPS_ATTENTE)
        except KeyboardInterrupt:
            # Permet de quitter proprement avec Ctrl+C
            print("\nArrêt du bot demandé par l'utilisateur. Au revoir !")
            break

if __name__ == "__main__":
    main()