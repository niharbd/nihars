
from utils import fetch_binance_data, calculate_indicators, get_all_usdt_futures_symbols
from datetime import datetime
import pytz

def scan_market():
    valid_signals = []
    symbols = get_all_usdt_futures_symbols()
    now_bst = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone("Asia/Dhaka"))
    
    for symbol in symbols:
        closes, volumes = fetch_binance_data(symbol)
        if not closes or not volumes:
            continue
        ema_fast, ema_slow, rsi = calculate_indicators(closes)
        price = closes[-1]
        
        # Tight breakout/breakdown logic
        if ema_fast > ema_slow and rsi > 55 and volumes[-1] > sum(volumes[-10:])/10:
            tp = round(price * 1.05, 2)
            sl = round(price * 0.985, 2)
            valid_signals.append({
                "symbol": symbol,
                "type": "Breakout",
                "confidence": "85%",
                "entry": price,
                "tp": tp,
                "sl": sl,
                "reason": "Volume spike + EMA trend + RSI confirmation",
                "time": now_bst.strftime("%Y-%m-%d %H:%M:%S BST")
            })
        elif ema_fast < ema_slow and rsi < 45 and volumes[-1] > sum(volumes[-10:])/10:
            tp = round(price * 0.95, 2)
            sl = round(price * 1.015, 2)
            valid_signals.append({
                "symbol": symbol,
                "type": "Breakdown",
                "confidence": "85%",
                "entry": price,
                "tp": tp,
                "sl": sl,
                "reason": "Volume spike + EMA trend + RSI confirmation",
                "time": now_bst.strftime("%Y-%m-%d %H:%M:%S BST")
            })
    return valid_signals
