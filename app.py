
import pytz
from flask import Flask, render_template
from scanner import scan_market

app = Flask(__name__)

@app.route("/")
def home():
    signals = scan_market()
    return render_template("index.html", signals=signals)
