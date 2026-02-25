from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

YAHOO_BASE = "https://query1.finance.yahoo.com/v8/finance/chart/"

# Realistic browser headers
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

def get_yahoo_crumb():
    """
    Yahoo Finance requires a crumb token alongside requests.
    We fetch the finance homepage first to get a session cookie and crumb.
    """
    session = requests.Session()
    session.get("https://fc.yahoo.com", headers=HEADERS, timeout=10)
    resp = session.get("https://query1.finance.yahoo.com/v1/test/getcrumb", headers=HEADERS, timeout=10)
    crumb = resp.text.strip()
    return session, crumb

# Cache the session and crumb so we don't re-fetch on every request
_session = None
_crumb   = None

def get_session_and_crumb():
    global _session, _crumb
    if not _session or not _crumb or len(_crumb) < 2:
        _session, _crumb = get_yahoo_crumb()
    return _session, _crumb

@app.route("/price")
def price():
    ticker   = request.args.get("ticker")
    period1  = request.args.get("period1")
    period2  = request.args.get("period2")
    interval = request.args.get("interval", "1d")

    if not ticker or not period1 or not period2:
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        session, crumb = get_session_and_crumb()
        url = f"{YAHOO_BASE}{ticker}?period1={period1}&period2={period2}&interval={interval}&crumb={crumb}"
        resp = session.get(url, headers=HEADERS, timeout=15)

        # If crumb has expired, refresh and retry once
        if resp.status_code in (401, 403):
            global _session, _crumb
            _session, _crumb = get_yahoo_crumb()
            url = f"{YAHOO_BASE}{ticker}?period1={period1}&period2={period2}&interval={interval}&crumb={_crumb}"
            resp = _session.get(url, headers=HEADERS, timeout=15)

        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.RequestException as e:
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
