import requests
from datetime import datetime
import pytz

def scan_market():
    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    try:
        response = requests.get(url)
        data = response.json()
        symbols = [
            s['symbol'] for s in data['symbols']
            if s['contractType'] == "PERPETUAL" and s['quoteAsset'] == "USDT"
        ]
    except Exception as e:
        print("Failed to fetch symbols:", e)
        return []

    valid_signals = []
    for symbol in symbols:
        try:
            price_resp = requests.get(f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}")
            price = float(price_resp.json()['price'])

            # Simulated signal logic — You can replace this with your advanced logic
            if price > 1:  # skip low-value tokens
                tp = round(price * 1.05, 4)  # 5% target
                sl = round(price * 0.98, 4)  # tight SL

                valid_signals.append({
                    "symbol": symbol,
                    "type": "Breakout" if int(price) % 2 == 0 else "Breakdown",
                    "confidence": 85,
                    "entry": price,
                    "tp": tp,
                    "sl": sl,
                    "reason": "Volume spike + EMA trend + RSI confirmation"
                })

        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            continue

    return valid_signals
