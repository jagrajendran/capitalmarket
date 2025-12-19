import yfinance as yf
import pandas as pd
from IPython.display import display
from datetime import datetime
import pytz

# -----------------------------
# IST TIMESTAMP
# -----------------------------
ist = pytz.timezone("Asia/Kolkata")
timestamp_ist = datetime.now(ist).strftime("%d-%b-%Y %I:%M %p IST")

# -----------------------------
# SYMBOLS
# -----------------------------
symbols = {
    # US
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "Dow Jones": "^DJI",

    # Asia
    "Nikkei 225": "^N225",
    "Hong Kong - Hang Seng": "^HSI",

    # India
    "NIFTY 50": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "India VIX": "^INDIAVIX",
    "GIFT NIFTY (Proxy)": "^NSEI",

    # Europe
    "DAX": "^GDAXI",
    "FTSE 100": "^FTSE",

    # Macro
    "USDINR": "USDINR=X",
    "Gold (XAU/USD)": "GC=F",
    "Crude Oil (WTI)": "CL=F"
}

rows = []

for name, ticker_symbol in symbols.items():
    ticker = yf.Ticker(ticker_symbol)
    hist = ticker.history(period="2d")

    if len(hist) >= 2:
        prev_close = hist["Close"].iloc[-2]
        cmp = hist["Close"].iloc[-1]
        pct_change = ((cmp / prev_close) - 1) * 100

        rows.append([
            name,
            round(cmp, 2),
            round(prev_close, 2),
            round(pct_change, 2)
        ])

df = pd.DataFrame(
    rows,
    columns=["Market / Index", "CMP", "Previous Close", "% Change"]
)

# -----------------------------
# BACKGROUND COLOR FORMATTING
# -----------------------------
def bg_color(val):
    if val > 0:
        return "background-color: #e6f4ea; font-weight: bold"   # light green
    elif val < 0:
        return "background-color: #fdecea; font-weight: bold"   # light red
    else:
        return "background-color: #f2f2f2"

styled_df = (
    df.style
      .map(bg_color, subset=["% Change"])
      .set_caption(f"📊 Global Market Dashboard | Last Updated: {timestamp_ist}")
)

display(styled_df)
