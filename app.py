import os
import datetime
import yfinance as yf
import pandas as pd
from flask import Flask, render_template, jsonify
import openai

# הגדרות API
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# רשימת המניות לניטור (תוכל להרחיב)
NASDAQ_STOCKS = ["AAPL", "MSFT", "NVDA", "GOOG", "AMZN"]
TASE_STOCKS = ["TEVA.TA", "ICL.TA", "BZRA.TA", "MZTF.TA", "ELAL.TA"]

# פונקציה להבאת נתונים היסטוריים
def get_stock_history(symbol, period="6mo"):
    ticker = yf.Ticker(symbol)
    data = ticker.history(period=period)
    return data

# פונקציה להפקת המלצה עם AI
def generate_ai_recommendation(symbol, history_df):
    try:
        avg_price = history_df["Close"].mean()
        last_price = history_df["Close"].iloc[-1]
        change_percent = ((last_price - avg_price) / avg_price) * 100

        prompt = f"""
        נתח את המניה {symbol} על בסיס נתוני מחירים היסטוריים ({len(history_df)} ימים) 
        ושינויים באחוזים ({change_percent:.2f}% מהמחיר הממוצע). 
        קבע האם קיימת ציפייה לעלייה יציבה של מעל 10% בתקופה הקרובה.
        הסבר את המסקנה בצורה עניינית.
        """
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"שגיאה בניתוח המניה: {e}"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/recommendations")
def recommendations():
    all_recs = []
    for stock in NASDAQ_STOCKS + TASE_STOCKS:
        history = get_stock_history(stock)
        rec = generate_ai_recommendation(stock, history)
        all_recs.append({
            "symbol": stock,
            "recommendation": rec
        })
    return jsonify(all_recs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
