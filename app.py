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
# YFINANCE HARDENING
# =================================================
os.environ["YFINANCE_NO_TZ_CACHE"] = "1"

# =================================================
# STREAMLIT CONFIG
# =================================================
st.set_page_config(
    page_title="Capital Market Pulse — PRO",
    layout="wide"
)

st.title("📊 Capital Market Pulse — PRO")
st.caption("Institution-grade • India-first • Intraday ready")

ist = pytz.timezone("Asia/Kolkata")
st.markdown(
    f"🕒 **Last updated:** {datetime.now(ist).strftime('%d-%b-%Y %I:%M %p IST')}"
)

# =================================================
# COMMON FUNCTIONS
# =================================================
@st.cache_data(ttl=900)
def fetch_batch_data(symbol_dict):
    return yf.download(
        tickers=list(symbol_dict.values()),
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

        prev, curr = closes.iloc[-2], closes.iloc[-1]

        # Bond yield normalization
        if symbol in ["^TNX", "^IRX", "^TYX"]:
            prev /= 10
            curr /= 10

        pct = ((curr / prev) - 1) * 100
        return round(curr, 2), round(prev, 2), round(pct, 2)

    except Exception:
        return None


def format_change(val):
    if val > 0:
        return f"▲ {val:.2f}%"
    elif val < 0:
        return f"▼ {val:.2f}%"
    return f"{val:.2f}%"


def bg_change(val):
    if "▲" in val:
        return "background-color:#e6f4ea;color:#137333;font-weight:bold"
    if "▼" in val:
        return "background-color:#fdecea;color:#a50e0e;font-weight:bold"
    return ""


def heat_color(val):
    v = max(min(val, 5), -5)
    if v > 0:
        g = int(255 - (v / 5) * 140)
        return f"background-color: rgb({g},255,{g}); font-weight:bold"
    if v < 0:
        r = int(255 - (abs(v) / 5) * 140)
        return f"background-color: rgb(255,{r},{r}); font-weight:bold"
    return ""

# =================================================
# SYMBOL DEFINITIONS
# =================================================
market_symbols = {
    "NIFTY 50": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "SENSEX": "^BSESN",
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
    "Silver": "SI=F",
    "Crude Oil": "CL=F",

    "US 10Y Bond Yield": "^TNX",
    "US 2Y Bond Yield": "^IRX",
    "US 30Y Bond Yield": "^TYX"
}

nifty_sectors = {
    "NIFTY IT": "^CNXIT",
    "NIFTY BANK": "^NSEBANK",
    "NIFTY FMCG": "^CNXFMCG",
    "NIFTY PHARMA": "^CNXPHARMA",
    "NIFTY METAL": "^CNXMETAL",
    "NIFTY AUTO": "^CNXAUTO",
    "NIFTY REALTY": "^CNXREALTY",
    "NIFTY ENERGY": "^CNXENERGY",
    "NIFTY PSU BANK": "^CNXPSUBANK",
    "NIFTY FIN SERVICE": "^CNXFIN"
}

nifty50_stocks = {
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "INFY": "INFY.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "SBIN": "SBIN.NS",
    "ITC": "ITC.NS",
    "LT": "LT.NS",
    "BHARTIARTL": "BHARTIARTL.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "AXISBANK": "AXISBANK.NS",
    "KOTAKBANK": "KOTAKBANK.NS",
    "MARUTI": "MARUTI.NS",
    "HCLTECH": "HCLTECH.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "TITAN": "TITAN.NS",
    "WIPRO": "WIPRO.NS",
    "NTPC": "NTPC.NS",
    "POWERGRID": "POWERGRID.NS",
    "ADANIENT": "ADANIENT.NS",
    "ADANIPORTS": "ADANIPORTS.NS",
    "TATASTEEL": "TATASTEEL.NS",
    "JSWSTEEL": "JSWSTEEL.NS",
    "COALINDIA": "COALINDIA.NS",
    "BPCL": "BPCL.NS",
    "GRASIM": "GRASIM.NS",
    "DRREDDY": "DRREDDY.NS",
    "DIVISLAB": "DIVISLAB.NS",
    "EICHERMOT": "EICHERMOT.NS",
    "TECHM": "TECHM.NS",
    "BRITANNIA": "BRITANNIA.NS",
    "ONGC": "ONGC.NS",
    "TATAMOTORS": "TATAMOTORS.NS",
    "CIPLA": "CIPLA.NS",
    "HINDALCO": "HINDALCO.NS",
    "LTIM": "LTIM.NS"
}

# =================================================
# FETCH DATA (ONCE)
# =================================================
market_data = fetch_batch_data(market_symbols)
sector_data = fetch_batch_data(nifty_sectors)
heat_data = fetch_batch_data(nifty50_stocks)

# =================================================
# TABS
# =================================================
tabs = st.tabs([
    "🌍 Global",
    "🇮🇳 India",
    "🏭 Sectors",
    "🔥 Heatmap",
    "💰 Bonds & Commodities",
    "📊 Sentiment",
    "📰 News"
])

# =================================================
# 🌍 GLOBAL
# =================================================
with tabs[0]:
    rows = []
    for k in ["S&P 500", "NASDAQ", "Dow Jones", "Nikkei 225", "Hang Seng", "DAX", "FTSE 100"]:
        v = extract_price(market_data, market_symbols[k])
        if v:
            rows.append([k, v[0], format_change(v[2])])

    df = pd.DataFrame(rows, columns=["Index", "Price", "% Change"])
    st.dataframe(df.style.map(bg_change, subset=["% Change"]), use_container_width=True)

# =================================================
# 🇮🇳 INDIA
# =================================================
with tabs[1]:
    rows = []
    for k in ["NIFTY 50", "BANKNIFTY", "SENSEX", "India VIX", "USDINR"]:
        v = extract_price(market_data, market_symbols[k])
        if v:
            rows.append([k, v[0], format_change(v[2])])

    df = pd.DataFrame(rows, columns=["Market", "Value", "% Change"])
    st.dataframe(df.style.map(bg_change, subset=["% Change"]), use_container_width=True)

# =================================================
# 🏭 SECTORS
# =================================================
with tabs[2]:
    rows = []
    for k, sym in nifty_sectors.items():
        v = extract_price(sector_data, sym)
        if v:
            rows.append([k, format_change(v[2])])

    df = pd.DataFrame(rows, columns=["Sector", "% Change"])
    st.dataframe(df.style.map(bg_change, subset=["% Change"]), use_container_width=True)

# =================================================
# 🔥 HEATMAP
# =================================================
with tabs[3]:
    rows = []
    for k, sym in nifty50_stocks.items():
        v = extract_price(heat_data, sym)
        if v:
            rows.append([k, v[2]])

    df = pd.DataFrame(rows, columns=["Stock", "Change %"])
    st.dataframe(
        df.style.applymap(heat_color, subset=["Change %"]),
        use_container_width=True
    )

# =================================================
# 💰 BONDS & COMMODITIES
# =================================================
with tabs[4]:
    rows = []
    for k in ["US 10Y Bond Yield", "US 2Y Bond Yield", "US 30Y Bond Yield", "Gold", "Silver", "Crude Oil"]:
        v = extract_price(market_data, market_symbols[k])
        if v:
            rows.append([k, v[0], format_change(v[2])])

    df = pd.DataFrame(rows, columns=["Asset", "Value", "% Change"])
    st.dataframe(df.style.map(bg_change, subset=["% Change"]), use_container_width=True)

# =================================================
# 📊 SENTIMENT
# =================================================
with tabs[5]:
    score = 0
    if extract_price(market_data, "^INDIAVIX")[2] < 0:
        score += 1
    if extract_price(market_data, "^TNX")[2] < 0:
        score += 1
    if extract_price(market_data, "^GSPC")[2] > 0:
        score += 1

    sentiment = {
        3: "🟢 STRONG RISK ON",
        2: "🟡 MODERATE RISK ON",
        1: "🟠 CAUTION",
        0: "🔴 RISK OFF"
    }

    st.metric("Market Mood", sentiment[score])

# =================================================
# 📰 NEWS
# =================================================
with tabs[6]:
    feeds = {
        "India": "https://news.google.com/rss/search?q=india+stock+market",
        "Global": "https://news.google.com/rss/search?q=global+markets"
    }

    news = []
    for cat, url in feeds.items():
        feed = feedparser.parse(url)
        for e in feed.entries[:6]:
            news.append([cat, e.title, e.link])

    df = pd.DataFrame(news, columns=["Category", "Headline", "Link"])
    st.dataframe(
        df,
        use_container_width=True,
        column_config={"Link": st.column_config.LinkColumn("Link")}
    )

# =================================================
# FOOTER
# =================================================
st.caption("📌 Educational dashboard only. Not investment advice.")
