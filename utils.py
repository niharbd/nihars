import requests
import pandas as pd

def fetch_klines(symbol, interval="15m", limit=100):
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        res = requests.get(url)
        data = res.json()
        df = pd.DataFrame(data, columns=[
            "OpenTime", "Open", "High", "Low", "Close", "Volume",
            "CloseTime", "QuoteAssetVolume", "NumTrades", "TakerBuyBaseVol", "TakerBuyQuoteVol", "Ignore"
        ])
        df = df.astype({
            "Open": float, "High": float, "Low": float,
            "Close": float, "Volume": float
        })
        return df
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None
