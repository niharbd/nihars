
import pandas as pd
import requests
from datetime import datetime
import pytz
import os
import joblib
from utils import fetch_klines
from signal_logger import log_signal

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

def compute_atr(df, period=14):
    high_low = df["High"] - df["Low"]
    high_close = (df["High"] - df["Close"].shift()).abs()
    low_close = (df["Low"] - df["Close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr

def compute_adx(df, period=14):
    df["TR"] = df["High"] - df["Low"]
    df["+DM"] = df["High"].diff()
    df["-DM"] = df["Low"].diff()
    df["+DM"] = df["+DM"].where((df["+DM"] > df["-DM"]) & (df["+DM"] > 0), 0)
    df["-DM"] = df["-DM"].where((df["-DM"] > df["+DM"]) & (df["-DM"] > 0), 0)
    tr14 = df["TR"].rolling(window=period).sum()
    plus_dm14 = df["+DM"].rolling(window=period).sum()
    minus_dm14 = df["-DM"].rolling(window=period).sum()
    plus_di14 = 100 * (plus_dm14 / tr14)
    minus_di14 = 100 * (minus_dm14 / tr14)
    dx = (abs(plus_di14 - minus_di14) / (plus_di14 + minus_di14)) * 100
    return dx.rolling(window=period).mean()

def compute_relative_volume(df, period=20):
    avg_vol = df["Volume"].rolling(window=period).mean()
    return df["Volume"] / avg_vol

def get_fear_greed_index():
    try:
        url = "https://api.alternative.me/fng/"
        response = requests.get(url)
        data = response.json()
        return int(data["data"][0]["value"])
    except:
        return 50

def get_btc_dominance():
    try:
        response = requests.get("https://api.coingecko.com/api/v3/global")
        return response.json()["data"]["market_cap_percentage"]["btc"]
    except:
        return 50.0

def is_recent_news(symbol):
    try:
        response = requests.get("https://www.binance.com/bapi/composite/v1/public/cms/article/list/category?category=Trading&limit=10")
        news = response.json().get("data", {}).get("articles", [])
        for article in news:
            title = article.get("title", "").lower()
            if symbol.lower().replace("usdt", "") in title:
                return True
    except:
        pass
    return False

def load_model(path="model.pkl"):
    try:
        if os.path.exists(path):
            return joblib.load(path)
    except:
        pass
    return None

def get_all_usdt_futures_symbols():
    try:
        data = requests.get("https://fapi.binance.com/fapi/v1/exchangeInfo").json()
        return [s["symbol"] for s in data["symbols"] if s["contractType"] == "PERPETUAL" and s["quoteAsset"] == "USDT"]
    except:
        return []

def scan_market():
    fgi = get_fear_greed_index()
    btc_d = get_btc_dominance()
    if fgi < 20 or fgi > 80:
        print("Market sentiment extreme — skipping signals.")
        return pd.DataFrame(), datetime.now(pytz.timezone("Asia/Dhaka")).strftime("%Y-%m-%d %H:%M:%S")

    ml_model = load_model()
    symbols = get_all_usdt_futures_symbols()
    results = []

    for symbol in symbols:
        df_15m = fetch_klines(symbol, interval="15m", limit=100)
        df_1h = fetch_klines(symbol, interval="1h", limit=100)
        if df_15m is None or df_1h is None or df_15m.empty or df_1h.empty:
            continue

        for df in [df_15m, df_1h]:
            df["EMA20"] = df["Close"].ewm(span=20).mean()
            df["EMA50"] = df["Close"].ewm(span=50).mean()
            df["RSI"] = compute_rsi(df["Close"])
            df["MACD"], df["MACD_Signal"] = compute_macd(df["Close"])
            df["ATR"] = compute_atr(df)
            df["ADX"] = compute_adx(df)
            df["RVOL"] = compute_relative_volume(df)

        l15 = df_15m.iloc[-1]
        l1h = df_1h.iloc[-1]

        breakout = (
            l15["Close"] > l15["EMA20"] > l15["EMA50"] and
            l1h["Close"] > l1h["EMA20"] > l1h["EMA50"] and
            l15["RSI"] > 60 and l1h["RSI"] > 60 and
            l15["MACD"] > l15["MACD_Signal"] and
            l15["ADX"] > 20 and l15["RVOL"] > 1.5
        )

        breakdown = (
            l15["Close"] < l15["EMA20"] < l15["EMA50"] and
            l1h["Close"] < l1h["EMA20"] < l1h["EMA50"] and
            l15["RSI"] < 40 and l1h["RSI"] < 40 and
            l15["MACD"] < l15["MACD_Signal"] and
            l15["ADX"] > 20 and l15["RVOL"] > 1.5
        )

        if (breakout or breakdown) and not is_recent_news(symbol):
            entry = l15["Close"]
            atr = l15["ATR"]
            rr_multiplier = 2.0  # risk/reward

            tp = round(entry + rr_multiplier * atr, 4) if breakout else round(entry - rr_multiplier * atr, 4)
            sl = round(entry - atr, 4) if breakout else round(entry + atr, 4)
            signal_type = "Breakout" if breakout else "Breakdown"
            now_bst = datetime.now(pytz.timezone("Asia/Dhaka")).strftime("%Y-%m-%d %H:%M:%S")

            if ml_model:
                features = [[
                    l15["EMA20"] - l15["EMA50"],
                    l15["RSI"],
                    l15["MACD"] - l15["MACD_Signal"],
                    l15["ADX"],
                    l15["ATR"],
                    l15["ATR"] / entry,
                    l15["RVOL"]
                ]]
                confidence = round(ml_model.predict_proba(features)[0][1] * 100, 2)
            else:
                confidence = 90

            if confidence >= 80:
                row = {
                    "Coin": symbol,
                    "Type": signal_type,
                    "Confidence": confidence,
                    "Entry": round(entry, 4),
                    "TP": tp,
                    "SL": sl,
                    "Why Detected": "ML-confirmed: EMA, RSI, MACD, ADX, Volume, ATR",
                    "Signal Time": now_bst
                }

                log_signal({
                    **row,
                    "ema_diff": l15["EMA20"] - l15["EMA50"],
                    "rsi": l15["RSI"],
                    "macd_hist": l15["MACD"] - l15["MACD_Signal"],
                    "adx": l15["ADX"],
                    "atr": l15["ATR"],
                    "atr_ratio": l15["ATR"] / entry,
                    "rvol": l15["RVOL"]
                })

                results.append(row)

    return pd.DataFrame(results), datetime.now(pytz.timezone("Asia/Dhaka")).strftime("%Y-%m-%d %H:%M:%S")
