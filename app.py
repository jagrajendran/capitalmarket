# =================================================
# IMPORTS
# =================================================
import os
import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
from datetime import datetime
import pytz

# =================================================
# CONFIG
# =================================================
os.environ["YFINANCE_NO_TZ_CACHE"] = "1"

st.set_page_config(
    page_title="Capital Market Pulse — PRO",
    layout="wide"
)

st.title("📊 Capital Market Pulse — PRO")
st.caption("Institution-grade • India-first • Intraday ready")

ist = pytz.timezone("Asia/Kolkata")
st.markdown(f"🕒 **Last updated:** {datetime.now(ist).strftime('%d-%b-%Y %I:%M %p IST')}")

# =================================================
# COMMON FUNCTIONS
# =================================================
@st.cache_data(ttl=900)
def fetch_batch_data(symbols):
    return yf.download(
        tickers=list(symbols.values()),
        period="5d",
        group_by="ticker",
        auto_adjust=True,
        threads=False,
        progress=False
    )


def extract_price(data, symbol):
    try:
        if isinstance(data.columns, pd.MultiIndex):
            if symbol not in data.columns.get_level_values(0):
                return None
            df = data[symbol]
        else:
            df = data

        closes = df["Close"].dropna()
        if len(closes) < 2:
            return None

        prev = round(closes.iloc[-2], 2)
        curr = round(closes.iloc[-1], 2)

        if symbol in ["^TNX", "^IRX", "^TYX"]:
            prev = round(prev / 10, 2)
            curr = round(curr / 10, 2)

        pct = round(((curr / prev) - 1) * 100, 2)
        return prev, curr, pct
    except:
        return None


def format_change(val):
    return f"▲ {val:.2f}%" if val > 0 else f"▼ {abs(val):.2f}%"


def bg_change(val):
    if "▲" in val:
        return "background-color:#e6f4ea;color:#137333;font-weight:bold"
    return "background-color:#fdecea;color:#a50e0e;font-weight:bold"


def heat_color(val):
    v = max(min(val, 5), -5)
    if v > 0:
        g = int(255 - (v / 5) * 140)
        return f"background-color: rgb({g},255,{g}); font-weight:bold"
    r = int(255 - (abs(v) / 5) * 140)
    return f"background-color: rgb(255,{r},{r}); font-weight:bold"

# =================================================
# SYMBOLS
# =================================================
GLOBAL = {
    "S&P 500": "^GSPC", "NASDAQ": "^IXIC", "Dow Jones": "^DJI",
    "Nikkei 225": "^N225", "Hang Seng": "^HSI",
    "DAX": "^GDAXI", "FTSE 100": "^FTSE"
}

INDIA = {
    "NIFTY 50": "^NSEI", "BANKNIFTY": "^NSEBANK",
    "SENSEX": "^BSESN", "India VIX": "^INDIAVIX",
    "USDINR": "USDINR=X"
}

SECTORS = {
    "NIFTY IT": "^CNXIT", "NIFTY BANK": "^NSEBANK",
    "NIFTY FMCG": "^CNXFMCG", "NIFTY PHARMA": "^CNXPHARMA",
    "NIFTY METAL": "^CNXMETAL", "NIFTY AUTO": "^CNXAUTO"
}

BONDS_COMMODITIES = {
    "US 10Y Bond Yield": "^TNX",
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Crude Oil": "CL=F"
}

# =================================================
# STOCK LISTS
# =================================================
NIFTY_50 = {
    "RELIANCE": "RELIANCE.NS", "TCS": "TCS.NS", "INFY": "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS", "ICICIBANK": "ICICIBANK.NS",
    "SBIN": "SBIN.NS", "ITC": "ITC.NS", "LT": "LT.NS",
    "BHARTIARTL": "BHARTIARTL.NS", "BAJFINANCE": "BAJFINANCE.NS",
    "HINDUNILVR": "HINDUNILVR.NS", "AXISBANK": "AXISBANK.NS",
    "KOTAKBANK": "KOTAKBANK.NS", "MARUTI": "MARUTI.NS",
    "SUNPHARMA": "SUNPHARMA.NS", "TITAN": "TITAN.NS",
    "NTPC": "NTPC.NS", "POWERGRID": "POWERGRID.NS",
    "ONGC": "ONGC.NS", "TATAMOTORS": "TATAMOTORS.NS"
}

NIFTY_NEXT_50 = {
    "DLF": "DLF.NS", "INDIGO": "INDIGO.NS", "GODREJCP": "GODREJCP.NS",
    "TRENT": "TRENT.NS", "PIDILITIND": "PIDILITIND.NS",
    "POLYCAB": "POLYCAB.NS", "LUPIN": "LUPIN.NS",
    "MUTHOOTFIN": "MUTHOOTFIN.NS", "NMDC": "NMDC.NS",
    "TVSMOTOR": "TVSMOTOR.NS"
}

# =================================================
# FETCH DATA
# =================================================
market_data = fetch_batch_data({**GLOBAL, **INDIA, **SECTORS, **BONDS_COMMODITIES})

# =================================================
# 🌍 GLOBAL
# =================================================
st.markdown("---")
st.subheader("🌍 Global Markets")

rows = []
i = 1
for k, sym in GLOBAL.items():
    v = extract_price(market_data, sym)
    if v:
        rows.append([i, k, v[0], v[1], format_change(v[2])])
        i += 1

df = pd.DataFrame(rows, columns=["S.No", "Index", "Prev Close", "Current", "% Change"])
st.dataframe(df.style.map(bg_change, subset=["% Change"]), use_container_width=True, hide_index=True)

# =================================================
# 🇮🇳 INDIA
# =================================================
st.markdown("---")
st.subheader("🇮🇳 India Markets")

rows = []
i = 1
for k, sym in INDIA.items():
    v = extract_price(market_data, sym)
    if v:
        rows.append([i, k, v[0], v[1], format_change(v[2])])
        i += 1

df = pd.DataFrame(rows, columns=["S.No", "Market", "Prev Close", "Current", "% Change"])
st.dataframe(df.style.map(bg_change, subset=["% Change"]), use_container_width=True, hide_index=True)

# =================================================
# 🏭 SECTORS
# =================================================
st.markdown("---")
st.subheader("🏭 Sector Performance")

rows = []
for k, sym in SECTORS.items():
    v = extract_price(market_data, sym)
    if v:
        rows.append([k, format_change(v[2])])

df = pd.DataFrame(rows, columns=["Sector", "% Change"])
st.dataframe(df.style.map(bg_change, subset=["% Change"]), use_container_width=True, hide_index=True)

# =================================================
# 🔥 HEATMAP
# =================================================
st.markdown("---")
st.subheader("🔥 Heatmap")

choice = st.radio("Select Index", ["NIFTY 50", "NIFTY NEXT 50"], horizontal=True)
stocks = NIFTY_50 if choice == "NIFTY 50" else NIFTY_NEXT_50
heat_data = fetch_batch_data(stocks)

rows = []
for k, sym in stocks.items():
    v = extract_price(heat_data, sym)
    if v:
        rows.append([k, v[0], v[1], v[2]])

df = pd.DataFrame(rows, columns=["Stock", "Prev Close", "Current", "% Change"])
st.dataframe(df.style.applymap(heat_color, subset=["% Change"]), use_container_width=True, hide_index=True)

# =================================================
# 💰 BONDS & COMMODITIES
# =================================================
st.markdown("---")
st.subheader("💰 Bonds & Commodities")

rows = []
i = 1
for k, sym in BONDS_COMMODITIES.items():
    v = extract_price(market_data, sym)
    if v:
        rows.append([i, k, v[0], v[1], format_change(v[2])])
        i += 1

df = pd.DataFrame(rows, columns=["S.No", "Asset", "Prev Close", "Current", "% Change"])
st.dataframe(df.style.map(bg_change, subset=["% Change"]), use_container_width=True, hide_index=True)

# =================================================
# 📊 SENTIMENT
# =================================================
st.markdown("---")
st.subheader("📊 Market Sentiment")

reasons = []
score = 0

vix = extract_price(market_data, "^INDIAVIX")
spx = extract_price(market_data, "^GSPC")
bond = extract_price(market_data, "^TNX")

if vix and vix[2] < 0:
    score += 1
    reasons.append("India VIX falling → volatility easing")
else:
    reasons.append("India VIX rising → fear increasing")

if bond and bond[2] < 0:
    score += 1
    reasons.append("US 10Y yield falling → equity supportive")
else:
    reasons.append("US 10Y yield rising → equity pressure")

if spx and spx[2] > 0:
    score += 1
    reasons.append("S&P 500 positive → global risk-on")
else:
    reasons.append("S&P 500 weak → global caution")

mood = {
    3: "🟢 STRONG RISK ON",
    2: "🟡 MODERATE RISK ON",
    1: "🟠 CAUTION",
    0: "🔴 RISK OFF"
}

st.metric("Overall Market Mood", mood[score])
for r in reasons:
    st.write("•", r)

# =================================================
# 📰 NEWS
# =================================================
st.markdown("---")
st.subheader("📰 Market News")

feed = feedparser.parse("https://news.google.com/rss/search?q=india+stock+market+nifty")
rows = []
for e in feed.entries[:8]:
    rows.append([e.title, e.link])

df = pd.DataFrame(rows, columns=["Headline", "Link"])
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={"Link": st.column_config.LinkColumn("Open")}
)

st.caption("📌 Educational dashboard only. Not investment advice.")
