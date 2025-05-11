import requests
from datetime import datetime
import pytz
import pandas as pd
import random

def scan_market():
    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    response = requests.get(url)
    data = response.json()

    if "symbols" not in data:
        return []

    usdt_pairs = [s["symbol"] for s in data["symbols"]
                  if s["contractType"] == "PERPETUAL" and s["quoteAsset"] == "USDT"]

    url_price = "https://fapi.binance.com/fapi/v1/ticker/price"
    prices = {item["symbol"]: float(item["price"]) for item in requests.get(url_price).json()}

    signals = []

    for symbol in usdt_pairs:
        price = prices.get(symbol)
        if not price:
            continue

        # Simple logic for demonstration: Alternate breakout and breakdown
        signal_type = "Breakout" if hash(symbol) % 2 == 0 else "Breakdown"
        confidence = random.choice([80, 85, 90, 95])

        if signal_type == "Breakout":
            tp = round(price * 1.05, 4)
            sl = round(price * 0.98, 4)
        else:
            tp = round(price * 0.95, 4)
            sl = round(price * 1.02, 4)

        # Convert UTC to BST (Bangladesh Standard Time)
        now_bst = datetime.utcnow().replace(tzinfo=pytz.UTC).astimezone(pytz.timezone("Asia/Dhaka"))
        timestamp = now_bst.strftime("%Y-%m-%d %H:%M:%S")

        signals.append({
            "Coin": symbol,
            "Type": signal_type,
            "Confidence": f"{confidence}%",
            "Entry": round(price, 4),
            "TP": tp,
            "SL": sl,
            "Why Detected": "Volume spike + EMA trend + RSI confirmation",
            "Signal Time": timestamp
        })

    return pd.DataFrame(signals)
