# analyse_crypto.py
import ccxt
import pandas as pd
import ta
from datetime import datetime
from config_crypto import (
    EXCHANGE_ID, CAPITAL_TOTAL, RISQUE_PAR_TRADE,
    TIMEFRAME_LT, TIMEFRAME_CT, PERIODE_MM200,
    PERIODE_MA9, PERIODE_MA50, PERIODE_RSI
)

def recuperer_donnees(exchange, symbole, timeframe, limite=200):
    try:
        ohlcv = exchange.fetch_ohlcv(symbole, timeframe, limit=limite)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f"Erreur lors de la récupération des données pour {symbole} ({timeframe}): {e}")
        return None

def analyser_paire(exchange, symbole):
    df_lt = recuperer_donnees(exchange, symbole, TIMEFRAME_LT, limite=PERIODE_MM200 + 10)
    df_ct = recuperer_donnees(exchange, symbole, TIMEFRAME_CT, limite=PERIODE_MM200)
    
    if df_lt is None or df_ct is None or len(df_lt) < PERIODE_MM200 or len(df_ct) < PERIODE_RSI:
        return None

    df_lt['mm200'] = df_lt['close'].rolling(window=PERIODE_MM200).mean()
    prix_actuel = df_ct['close'].iloc[-1]
    mm200_actuelle = df_lt['mm200'].iloc[-1]
    
    df_ct['rsi'] = ta.momentum.RSIIndicator(df_ct['close'], window=PERIODE_RSI).rsi()
    df_ct['ma9'] = df_ct['close'].rolling(window=PERIODE_MA9).mean()
    df_ct['ma50'] = df_ct['close'].rolling(window=PERIODE_MA50).mean()
    
    rsi_actuel = df_ct['rsi'].iloc[-1]
    ma9_actuelle = df_ct['ma9'].iloc[-1]
    ma50_actuelle = df_ct['ma50'].iloc[-1]
    
    ma9_prec = df_ct['ma9'].iloc[-3]
    ma50_prec = df_ct['ma50'].iloc[-3]
    
    if prix_actuel > mm200_actuelle:
        tendance_fond = "Haussière (Prix au-dessus de la MM200)"
        is_haussier_lt = True
    else:
        tendance_fond = "Baissière (Prix sous la MM200)"
        is_haussier_lt = False
        
    signal_achat_ct = (ma9_actuelle > ma50_actuelle) and (ma9_prec <= ma50_prec)
    signal_vente_ct = (ma9_actuelle < ma50_actuelle) and (ma9_prec >= ma50_prec)
    
    action = "Attente"
    montant = 0.0
    stop_loss = 0.0
    objectif = 0.0
    horizon = "-"
    proba = "-"
    note = "Aucun signal clair pour le moment."
    
    if is_haussier_lt and signal_achat_ct and rsi_actuel < 70:
        action = "Achat de continuation"
        montant = CAPITAL_TOTAL * RISQUE_PAR_TRADE
        stop_loss = prix_actuel * 0.98
        objectif = prix_actuel * 1.05
        horizon = "1 à 3 jours"
        proba = "65%"
        note = "Tendance de fond et signal CT alignés."
        
    elif not is_haussier_lt and signal_achat_ct:
        action = "Achat de rebond (risqué)"
        montant = CAPITAL_TOTAL * (RISQUE_PAR_TRADE / 2)
        stop_loss = prix_actuel * 0.99
        objectif = prix_actuel * 1.02
        horizon = "4h à 12h"
        proba = "50%"
        note = "Signal haussier contre la tendance de fond. Risque élevé."
        
    elif not is_haussier_lt and signal_vente_ct:
        action = "Short ou Attente"
        montant = CAPITAL_TOTAL * RISQUE_PAR_TRADE
        stop_loss = prix_actuel * 1.02
        objectif = prix_actuel * 0.96
        horizon = "1 à 2 jours"
        proba = "60%"
        note = "Tendance baissière confirmée par le CT."
        
    etat_rsi = ""
    if rsi_actuel < 30:
        etat_rsi = "sur-vente"
    elif rsi_actuel > 70:
        etat_rsi = "sur-achat"
    else:
        etat_rsi = "neutre"
        
    signe_ma = "au-dessus de" if ma9_actuelle > ma50_actuelle else "en-dessous de"
    situation = f"RSI à {rsi_actuel:.1f} (zone de {etat_rsi}). MA9 {signe_ma} MA50."
    
    return {
        "symbole": symbole,
        "tendance_fond": tendance_fond,
        "situation": situation,
        "action": action,
        "montant": montant,
        "stop_loss": stop_loss,
        "objectif": objectif,
        "horizon": horizon,
        "proba": proba,
        "note": note
    }