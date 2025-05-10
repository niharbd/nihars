from flask import Flask, render_template
from scanner import scan_market
import os

app = Flask(__name__, template_folder="templates")

@app.route("/")
def home():
    signals = scan_market()
    return render_template("index.html", signals=signals)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)