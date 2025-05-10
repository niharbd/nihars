# scanner.py (updated)

import requests
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator
from datetime import datetime
import pytz


def fetch_klines(symbol, interval='15m', limit=100):
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        response = requests.get(url)
        data = response.json()
        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades",
            "taker_buy_base_volume", "taker_buy_quote_volume", "ignore"])
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        return df
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None


def detect_signal(df, symbol):
    try:
        rsi = RSIIndicator(close=df['close'], window=14).rsi().iloc[-1]
        ema_fast = EMAIndicator(close=df['close'], window=9).ema_indicator().iloc[-1]
        ema_slow = EMAIndicator(close=df['close'], window=21).ema_indicator().iloc[-1]
        volume_now = df['volume'].iloc[-1]
        volume_avg = df['volume'].rolling(window=20).mean().iloc[-1]
        price = df['close'].iloc[-1]

        if price > ema_fast > ema_slow and volume_now > volume_avg * 1.5 and rsi > 60:
            return {
                "Coin": symbol,
                "Type": "Breakout",
                "Confidence": 90,
                "Entry": price,
                "TP": round(price * 1.05, 2),
                "SL": round(price * 0.98, 2),
                "Why": "Volume spike + EMA trend + RSI confirmation",
                "Time": datetime.now(pytz.timezone('Asia/Dhaka')).strftime("%Y-%m-%d %H:%M:%S")
            }

        if price < ema_fast < ema_slow and volume_now > volume_avg * 1.5 and rsi < 40:
            return {
                "Coin": symbol,
                "Type": "Breakdown",
                "Confidence": 90,
                "Entry": price,
                "TP": round(price * 0.95, 2),
                "SL": round(price * 1.02, 2),
                "Why": "Volume spike + EMA trend + RSI confirmation",
                "Time": datetime.now(pytz.timezone('Asia/Dhaka')).strftime("%Y-%m-%d %H:%M:%S")
            }
    except:
        pass
    return None


def scan_market():
    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    info = requests.get(url).json()
    symbols = [s['symbol'] for s in info['symbols'] if s['contractType'] == 'PERPETUAL' and s['quoteAsset'] == 'USDT']

    valid_signals = []
    for symbol in symbols:
        df = fetch_klines(symbol)
        if df is not None and len(df) >= 21:
            signal = detect_signal(df, symbol)
            if signal:
                valid_signals.append(signal)

    return valid_signals
