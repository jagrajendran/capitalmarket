# =================================================
# IMPORTS
# =================================================
import os
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

# =================================================
# CONFIG
# =================================================
os.environ["YFINANCE_NO_TZ_CACHE"] = "1"
st.set_page_config(page_title="Capital Market Pulse — FREE", layout="wide")

ist = pytz.timezone("Asia/Kolkata")
st.title("📊 Capital Market Pulse — FREE Intraday")
st.caption("Free data only • Honest signals • Intraday-ready")
st.markdown(f"🕒 **Last updated:** {datetime.now(ist).strftime('%d-%b-%Y %I:%M %p IST')}")

# =================================================
# FUNCTIONS
# =================================================
@st.cache_data(ttl=900)
def fetch_batch(symbols):
    return yf.download(
        tickers=list(symbols.values()),
        period="5d",
        group_by="ticker",
        auto_adjust=True,
        threads=False,
        progress=False
    )

def extract_price(data, sym):
    try:
        df = data[sym] if isinstance(data.columns, pd.MultiIndex) else data
        close = df["Close"].dropna()
        if len(close) < 2:
            return None

        prev = round(float(close.iloc[-2]), 2)
        curr = round(float(close.iloc[-1]), 2)
        pct = round(((curr / prev) - 1) * 100, 2)

        return prev, curr, pct
    except:
        return None

@st.cache_data(ttl=1800)
def get_market_caps(stocks):
    caps = {}
    for s in stocks:
        try:
            mc = yf.Ticker(f"{s}.NS").fast_info.get("marketCap")
            if mc:
                caps[s] = mc / 1e7
        except:
            pass
    return caps

def heat_color(v):
    if v > 1: return "background-color:#1b5e20;color:white"
    if v > 0: return "background-color:#c8e6c9"
    if v < -1: return "background-color:#b71c1c;color:white"
    if v < 0: return "background-color:#f4c7c3"
    return "background-color:#eeeeee"

def dir_color(v):
    return "color:#137333;font-weight:bold" if v > 0 else "color:#a50e0e;font-weight:bold"

# =================================================
# SYMBOL GROUPS
# =================================================
GLOBAL = {
    "S&P500":"^GSPC","NASDAQ":"^IXIC","DOW":"^DJI",
    "NIKKEI":"^N225","HANG SENG":"^HSI","DAX":"^GDAXI","FTSE":"^FTSE"
}

INDIA = {
    "GIFT NIFTY":"^NIFTY_GIFT","NIFTY":"^NSEI","BANKNIFTY":"^NSEBANK",
    "SENSEX":"^BSESN","VIX":"^INDIAVIX","USDINR":"USDINR=X"
}

BONDS_COMMODITIES = {
    "US10Y":"^TNX","GOLD":"GC=F","SILVER":"SI=F",
    "CRUDE":"CL=F","COPPER":"HG=F","URANIUM ETF":"URA"
}

# =================================================
# FETCH DATA
# =================================================
market_data = fetch_batch({**GLOBAL, **INDIA, **BONDS_COMMODITIES})

# =================================================
# TABS
# =================================================
tab1, tab2 = st.tabs(["📊 Dashboard", "📈 Options OI"])

# =================================================
# TAB 1
# =================================================
with tab1:

    col1, col2, col3 = st.columns(3)

    # 🌍 GLOBAL
    with col1:
        st.subheader("🌍 Global Markets")
        rows=[]
        for k,s in GLOBAL.items():
            v=extract_price(market_data,s)
            if v: rows.append([k,v[0],v[1],v[2]])
        st.dataframe(pd.DataFrame(rows,
            columns=["Market","Prev Close","Price","% Change"])
            .style.applymap(dir_color,subset=["% Change"]),
            hide_index=True,use_container_width=True)

    # 🇮🇳 INDIA
    with col2:
        st.subheader("🇮🇳 India Markets")
        rows=[]
        for k,s in INDIA.items():
            v=extract_price(market_data,s)
            if v: rows.append([k,v[0],v[1],v[2]])
        st.dataframe(pd.DataFrame(rows,
            columns=["Market","Prev Close","Price","% Change"])
            .style.applymap(dir_color,subset=["% Change"]),
            hide_index=True,use_container_width=True)

    # 💰 BONDS
    with col3:
        st.subheader("💰 Bonds & Commodities")
        rows=[]
        for k,s in BONDS_COMMODITIES.items():
            v=extract_price(market_data,s)
            if v: rows.append([k,v[0],v[1],v[2]])
        st.dataframe(pd.DataFrame(rows,
            columns=["Asset","Prev Close","Price","% Change"])
            .style.applymap(dir_color,subset=["% Change"]),
            hide_index=True,use_container_width=True)

# =================================================
# TAB 2
# =================================================
with tab2:
    st.subheader("📈 NIFTY Options – FREE (Levels Only)")
    st.info("Option chain may be unavailable due to free data limits.")

# =================================================
st.caption("📌 Educational only. Not investment advice.")
