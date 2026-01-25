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
        c = df["Close"].dropna()
        if len(c) < 2:
            return None
        prev, curr = c.iloc[-2], c.iloc[-1]
        pct = round(((curr / prev) - 1) * 100, 2)
        return round(curr, 2), pct
    except:
        return None

@st.cache_data(ttl=1800)
def get_market_caps(stocks):
    caps = {}
    for s in stocks:
        try:
            mc = yf.Ticker(f"{s}.NS").fast_info.get("marketCap")
            if mc:
                caps[s] = mc / 1e7  # ₹ Cr
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

NIFTY_50 = [
"ADANIENT","ADANIPORTS","APOLLOHOSP","ASIANPAINT","AXISBANK","BAJAJ-AUTO",
"BAJFINANCE","BAJAJFINSV","BPCL","BHARTIARTL","BRITANNIA","CIPLA","COALINDIA",
"DIVISLAB","DRREDDY","EICHERMOT","GRASIM","HCLTECH","HDFCBANK","HDFCLIFE",
"HEROMOTOCO","HINDALCO","HINDUNILVR","ICICIBANK","ITC","INDUSINDBK","INFY",
"JSWSTEEL","KOTAKBANK","LT","LTIM","M&M","MARUTI","NESTLEIND","NTPC","ONGC",
"POWERGRID","RELIANCE","SBIN","SUNPHARMA","TATACONSUM","TATAMOTORS",
"TATASTEEL","TECHM","TITAN","ULTRACEMCO","UPL","WIPRO"
]

NIFTY_NEXT_50 = [
"ABB","ADANIGREEN","ALKEM","AMBUJACEM","AUROPHARMA","BERGEPAINT","BIOCON",
"BOSCHLTD","CANBK","COLPAL","CONCOR","DABUR","DLF","GAIL","GODREJCP",
"HAVELLS","HDFCAMC","ICICIGI","IGL","INDIGO","LUPIN","MARICO","MOTHERSON",
"MUTHOOTFIN","NAUKRI","NMDC","PAGEIND","PEL","PETRONET","PIDILITIND","PNB",
"SHREECEM","SIEMENS","SRF","TORNTPHARM","TRENT","TVSMOTOR","UBL","VEDL",
"VOLTAS","ZEEL","ZYDUSLIFE"
]

# =================================================
# FETCH DATA
# =================================================
market_data = fetch_batch({
    **GLOBAL, **INDIA, **BONDS_COMMODITIES,
    **{s: f"{s}.NS" for s in NIFTY_50 + NIFTY_NEXT_50}
})

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
        g=[]
        for k,s in GLOBAL.items():
            v=extract_price(market_data,s)
            if v: g.append([k,v[0],v[1]])
        st.dataframe(pd.DataFrame(g,columns=["Market","Price","%"])
                     .style.applymap(dir_color,subset=["%"]),
                     hide_index=True,use_container_width=True)

    # 🇮🇳 INDIA
    with col2:
        st.subheader("🇮🇳 India Markets")
        i=[]
        for k,s in INDIA.items():
            v=extract_price(market_data,s)
            if v: i.append([k,v[0],v[1]])
        st.dataframe(pd.DataFrame(i,columns=["Market","Price","%"])
                     .style.applymap(dir_color,subset=["%"]),
                     hide_index=True,use_container_width=True)

    # 💰 BONDS
    with col3:
        st.subheader("💰 Bonds & Commodities")
        b=[]
        for k,s in BONDS_COMMODITIES.items():
            v=extract_price(market_data,s)
            if v: b.append([k,v[0],v[1]])
        st.dataframe(pd.DataFrame(b,columns=["Asset","Price","%"])
                     .style.applymap(dir_color,subset=["%"]),
                     hide_index=True,use_container_width=True)

    # 🔥 HEATMAP
    st.subheader("🔥 Heatmap (Weight-aware)")
    idx = st.radio("Index",["NIFTY 50","NIFTY NEXT 50"],horizontal=True)

    stocks = NIFTY_50 if idx=="NIFTY 50" else NIFTY_NEXT_50
    caps = get_market_caps(stocks)
    total_cap = sum(caps.values())

    rows=[]; adv=dec=neu=0
    for s in stocks:
        v=extract_price(market_data,f"{s}.NS")
        if v and s in caps:
            wt = round((caps[s]/total_cap)*100,2)
            rows.append([s,v[1],round(caps[s],0),wt])
            adv+=v[1]>0
            dec+=v[1]<0
            neu+=v[1]==0

    c1,c2,c3=st.columns(3)
    c1.metric("Advances",adv)
    c2.metric("Declines",dec)
    c3.metric("Neutral",neu)

    st.dataframe(pd.DataFrame(rows,columns=["Stock","%","MCap ₹Cr","Wt %"])
                 .style.applymap(heat_color,subset=["%"]),
                 hide_index=True,use_container_width=True)

# =================================================
# TAB 2
# =================================================
with tab2:
    st.subheader("📈 NIFTY Options – FREE (Levels Only)")
    st.info("Option chain may be unavailable due to free data limits.")

# =================================================
st.caption("📌 Educational only. Not investment advice.")
