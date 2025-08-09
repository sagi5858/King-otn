from flask import Flask, render_template
import yfinance as yf
from datetime import datetime, timedelta

app = Flask(__name__)

# רשימת מניות למעקב (תוכל להרחיב)
NASDAQ_TICKERS = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN"]
TASE_TICKERS = ["TEVA.TA", "BCTR.TA", "ISL.TA"]

def get_stock_data(tickers):
    results = []
    for ticker in tickers:
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period="6mo")
            change = ((hist["Close"][-1] - hist["Close"][0]) / hist["Close"][0]) * 100
            results.append({"symbol": ticker, "change": round(change, 2)})
        except Exception as e:
            results.append({"symbol": ticker, "error": str(e)})
    return results

@app.route("/")
def home():
    nasdaq_data = get_stock_data(NASDAQ_TICKERS)
    tase_data = get_stock_data(TASE_TICKERS)
    return render_template("index.html", nasdaq=nasdaq_data, tase=tase_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
