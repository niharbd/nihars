from datetime import datetime

def scan_market():
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    return [
        {
            "symbol": "BTCUSDT",
            "type": "Breakout",
            "confidence": "90%",
            "entry": 64250,
            "tp": 67500,
            "sl": 63000,
            "reason": "Volume spike + EMA trend + RSI confirmation",
            "time": now
        }
    ]