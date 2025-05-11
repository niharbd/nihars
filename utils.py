import requests
import pandas as pd

def fetch_klines(symbol, interval="15m", limit=100):
    """
    Fetch historical candlestick data (klines) from Binance Futures API.

    Args:
        symbol (str): e.g. 'BTCUSDT'
        interval (str): e.g. '15m', '1h'
        limit (int): number of candles

    Returns:
        DataFrame: open, high, low, close, volume
    """
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        df = pd.DataFrame(data, columns=[
            "OpenTime", "Open", "High", "Low", "Close", "Volume",
            "CloseTime", "QuoteAssetVolume", "NumTrades",
            "TakerBuyBaseVol", "TakerBuyQuoteVol", "Ignore"
        ])
        df = df.astype({
            "Open": float,
            "High": float,
            "Low": float,
            "Close": float,
            "Volume": float
        })
        return df
    except Exception as e:
        print(f"Error fetching {symbol} - {interval}: {e}")
        return None
