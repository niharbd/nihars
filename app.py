
import pytz
import os
from flask import Flask, render_template
from scanner import scan_market

app = Flask(__name__)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

@app.route("/")
def home():
    signals = scan_market()
    return render_template("index.html", signals=signals)