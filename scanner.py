import pandas as pd
import requests
from datetime import datetime
import pytz
from utils import fetch_klines

def get_all_usdt_futures_symbols():
    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    try:
        response = requests.get(url)
        data = response.json()
        return [
            s["symbol"] for s in data["symbols"]
            if s["contractType"] == "PERPETUAL" and s["quoteAsset"] == "USDT"
        ]
    except Exception as e:
        print("Error fetching symbols:", e)
        return []

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def compute_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast).mean()
    ema_slow = series.ewm(span=slow).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal).mean()
    return macd_line, signal_line

def scan_market():
    symbols = get_all_usdt_futures_symbols()
    results = []
    for symbol in symbols:
        df = fetch_klines(symbol)
        if df is None or df.empty:
            continue

        df["EMA20"] = df["Close"].ewm(span=20).mean()
        df["EMA50"] = df["Close"].ewm(span=50).mean()
        df["RSI"] = compute_rsi(df["Close"])
        df["VolumeMA"] = df["Volume"].rolling(window=20).mean()
        df["MACD"], df["Signal"] = compute_macd(df["Close"])

        latest = df.iloc[-1]

        macd_confirm = latest["MACD"] > latest["Signal"]

        breakout = (
            latest["Close"] > latest["EMA20"] > latest["EMA50"] and
            latest["RSI"] > 60 and
            latest["Volume"] > latest["VolumeMA"] and
            macd_confirm
        )
        breakdown = (
            latest["Close"] < latest["EMA20"] < latest["EMA50"] and
            latest["RSI"] < 40 and
            latest["Volume"] > latest["VolumeMA"] and
            not macd_confirm
        )

        if breakout or breakdown:
            entry = latest["Close"]
            signal_type = "Breakout" if breakout else "Breakdown"
            tp = round(entry * 1.05, 4) if breakout else round(entry * 0.95, 4)
            sl = round(entry * 0.98, 4) if breakout else round(entry * 1.02, 4)
            now_bst = datetime.now(pytz.timezone("Asia/Dhaka")).strftime("%Y-%m-%d %H:%M:%S")

            results.append({
                "Coin": symbol,
                "Type": signal_type,
                "Confidence": 90,
                "Entry": entry,
                "TP": tp,
                "SL": sl,
                "Why Detected": "EMA trend + RSI + Volume spike + MACD confirm",
                "Signal Time": now_bst
            })

    return pd.DataFrame(results), now_bst
