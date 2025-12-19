import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(layout="wide")
st.title("📊 Capital Market Dashboard")

# IST timestamp
ist = pytz.timezone("Asia/Kolkata")
st.caption(f"Last updated: {datetime.now(ist).strftime('%d-%b-%Y %I:%M %p IST')}")

symbols = {
    "NIFTY 50": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "India VIX": "^INDIAVIX",
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "Dow Jones": "^DJI",
    "Nikkei 225": "^N225",
    "Hang Seng": "^HSI",
    "DAX": "^GDAXI",
    "FTSE 100": "^FTSE",
    "USDINR": "USDINR=X",
    "Gold": "GC=F",
    "Crude": "CL=F"
}

rows = []
for name, symbol in symbols.items():
    hist = yf.Ticker(symbol).history(period="2d")
    if len(hist) >= 2:
        prev = hist["Close"].iloc[-2]
        curr = hist["Close"].iloc[-1]
        chg = ((curr / prev) - 1) * 100
        rows.append([name, round(curr,2), round(prev,2), round(chg,2)])

df = pd.DataFrame(rows, columns=["Market", "CMP", "Prev Close", "% Change"])

def bg_color(val):
    if val > 0:
        return "background-color: #e6f4ea; font-weight: bold"
    elif val < 0:
        return "background-color: #fdecea; font-weight: bold"
    else:
        return "background-color: #f2f2f2"

st.dataframe(
    df.style.map(bg_color, subset=["% Change"]),
    use_container_width=True
)
