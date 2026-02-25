from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

YAHOO_BASE = "https://query1.finance.yahoo.com/v8/finance/chart/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

@app.route("/price")
def price():
    ticker   = request.args.get("ticker")
    period1  = request.args.get("period1")
    period2  = request.args.get("period2")
    interval = request.args.get("interval", "1d")

    if not ticker or not period1 or not period2:
        return jsonify({"error": "Missing required parameters"}), 400

    url = f"{YAHOO_BASE}{ticker}?period1={period1}&period2={period2}&interval={interval}"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 502

    # Pass the response straight through to the browser
    response = jsonify(data)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.route("/")
def index():
    return "Investment API is running."

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
