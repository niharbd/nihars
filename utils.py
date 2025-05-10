
import requests

def get_all_usdt_futures_symbols():
    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    data = requests.get(url).json()
    return [
        s["symbol"] for s in data.get("symbols", [])
        if s.get("contractType") == "PERPETUAL" and s.get("quoteAsset") == "USDT"
    ]

def fetch_binance_data(symbol, interval="15m", limit=100):
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}&limit={limit}"
    data = requests.get(url).json()
    closes = [float(c[4]) for c in data]
    volumes = [float(c[5]) for c in data]
    return closes, volumes

def calculate_indicators(closes):
    if len(closes) < 200:
        return 0, 0, 50
    ema_fast = sum(closes[-10:]) / 10
    ema_slow = sum(closes[-30:]) / 30
    gains = [closes[i] - closes[i - 1] for i in range(1, len(closes)) if closes[i] > closes[i - 1]]
    losses = [-1 * (closes[i] - closes[i - 1]) for i in range(1, len(closes)) if closes[i] < closes[i - 1]]
    avg_gain = sum(gains[-14:]) / 14 if gains else 0
    avg_loss = sum(losses[-14:]) / 14 if losses else 1
    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    rsi = 100 - (100 / (1 + rs))
    return ema_fast, ema_slow, rsi
