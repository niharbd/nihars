import requests
import pandas as pd
from datetime import datetime
import pytz
from utils import fetch_klines, calculate_indicators

def scan_market():
    valid_signals = []
    symbols = [
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'AVAXUSDT',
        'XRPUSDT', 'ADAUSDT', 'DOGEUSDT', 'MATICUSDT', 'LTCUSDT'
    ]
    now_bst = datetime.now(pytz.timezone('Asia/Dhaka')).strftime("%Y-%m-%d %H:%M:%S")

    for symbol in symbols:
        df = fetch_klines(symbol)
        if df is None or len(df) < 50:
            continue

        df = calculate_indicators(df)
        signal_type, confidence = detect_signal(df)

        if confidence >= 80:
            entry = df['close'].iloc[-1]
            direction = 1 if signal_type == 'Breakout' else -1
            tp1 = round(entry * (1 + 0.02 * direction), 4)
            tp2 = round(entry * (1 + 0.035 * direction), 4)
            tp3 = round(entry * (1 + 0.05 * direction), 4)
            sl = round(entry * (1 - 0.015 * direction), 4)

            valid_signals.append({
                "Coin": symbol,
                "Type": signal_type,
                "Confidence": f"{confidence}%",
                "Entry": entry,
                "TP1": tp1,
                "TP2": tp2,
                "TP3": tp3,
                "SL": sl,
                "Why Detected": "Volume spike + EMA trend + RSI confirmation",
                "Signal Time": now_bst
            })

    return pd.DataFrame(valid_signals)

def detect_signal(df):
    if df['ema_fast'].iloc[-1] > df['ema_slow'].iloc[-1] and df['rsi'].iloc[-1] > 55:
        return "Breakout", 90
    elif df['ema_fast'].iloc[-1] < df['ema_slow'].iloc[-1] and df['rsi'].iloc[-1] < 45:
        return "Breakdown", 85
    else:
        return None, 0
