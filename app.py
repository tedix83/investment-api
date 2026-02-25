from flask import Flask, jsonify, request
import yfinance as yf
from datetime import datetime, timezone

app = Flask(__name__)

@app.route("/price")
def price():
    ticker   = request.args.get("ticker")
    period1  = request.args.get("period1")
    period2  = request.args.get("period2")
    interval = request.args.get("interval", "1d")

    if not ticker or not period1 or not period2:
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        start = datetime.fromtimestamp(int(period1), tz=timezone.utc).strftime("%Y-%m-%d")
        end   = datetime.fromtimestamp(int(period2), tz=timezone.utc).strftime("%Y-%m-%d")

        t    = yf.Ticker(ticker)
        hist = t.history(start=start, end=end, interval=interval, auto_adjust=True)

        if hist.empty:
            return jsonify({"error": f"No data returned for {ticker}"}), 404

        timestamps = [int(d.timestamp()) for d in hist.index]
        closes     = [round(float(c), 6) for c in hist["Close"]]

        # Return in the same shape the frontend already expects
        data = {
            "chart": {
                "result": [{
                    "timestamp": timestamps,
                    "indicators": {
                        "quote": [{"close": closes}]
                    }
                }]
            }
        }

    except Exception as e:
        return jsonify({"error": str(e)}), 502

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
