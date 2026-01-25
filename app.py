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
st.markdown(f"🕒 Last updated: {datetime.now(ist).strftime('%d-%b-%Y %I:%M %p IST')}")

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
        df = data[sym]
        close = df["Close"].dropna()
        if len(close) < 2:
            return None

        prev = round(float(close.iloc[-2]), 2)
        curr = round(float(close.iloc[-1]), 2)
        pct  = round(((curr / prev) - 1) * 100, 2)

        return prev, curr, pct
    except:
        return None

@st.cache_data(ttl=1800)
def get_market_caps(stocks):
    caps={}
    for s in stocks:
        try:
            mc = yf.Ticker(f"{s}.NS").fast_info.get("marketCap")
            if mc:
                caps[s]=mc/1e7   # ₹ Cr
        except:
            pass
    return caps

# =================================================
# COLOR FUNCTIONS
# =================================================
def dir_color(v):
    return "color:#137333;font-weight:bold" if float(v)>0 else "color:#a50e0e;font-weight:bold"

def heat_color(v):
    v=float(v)
    if v>1: return "background-color:#1b5e20;color:white"
    if v>0: return "background-color:#c8e6c9"
    if v<-1: return "background-color:#b71c1c;color:white"
    if v<0: return "background-color:#f4c7c3"
    return ""

# =================================================
# SYMBOL GROUPS
# =================================================
GLOBAL={
"S&P500":"^GSPC","NASDAQ":"^IXIC","DOW":"^DJI",
"NIKKEI":"^N225","HANG SENG":"^HSI","DAX":"^GDAXI","FTSE":"^FTSE"
}

INDIA={
"GIFT NIFTY":"^NIFTY_GIFT","NIFTY":"^NSEI","BANKNIFTY":"^NSEBANK",
"SENSEX":"^BSESN","VIX":"^INDIAVIX","USDINR":"USDINR=X"
}

BONDS_COMMODITIES={
"US10Y":"^TNX","GOLD":"GC=F","SILVER":"SI=F",
"CRUDE":"CL=F","COPPER":"HG=F"
}

NIFTY_50=[
"ADANIENT","ADANIPORTS","APOLLOHOSP","ASIANPAINT","AXISBANK",
"BAJAJ-AUTO","BAJFINANCE","BAJAJFINSV","BPCL","BHARTIARTL",
"BRITANNIA","CIPLA","COALINDIA","DIVISLAB","DRREDDY","EICHERMOT",
"GRASIM","HCLTECH","HDFCBANK","HDFCLIFE","HEROMOTOCO","HINDALCO",
"HINDUNILVR","ICICIBANK","ITC","INDUSINDBK","INFY","JSWSTEEL",
"KOTAKBANK","LT","LTIM","M&M","MARUTI","NESTLEIND","NTPC","ONGC",
"POWERGRID","RELIANCE","SBIN","SUNPHARMA","TATACONSUM","TATAMOTORS",
"TATASTEEL","TECHM","TITAN","ULTRACEMCO","UPL","WIPRO"
]

# =================================================
# FETCH DATA
# =================================================
market_data=fetch_batch({
**GLOBAL,**INDIA,**BONDS_COMMODITIES,
**{s:f"{s}.NS" for s in NIFTY_50}
})

# =================================================
# TABS
# =================================================
tab1,tab2=st.tabs(["📊 Dashboard","📈 Options OI"])

# =================================================
# TAB 1
# =================================================
with tab1:

    c1,c2,c3=st.columns(3)

    # ---------- GLOBAL ----------
    with c1:
        st.subheader("🌍 Global Markets")
        rows=[]
        for k,s in GLOBAL.items():
            v=extract_price(market_data,s)
            if v: rows.append([k,v[0],v[1],v[2]])
        df=pd.DataFrame(rows,columns=["Market","Prev Close","Price","%"])
        df["%"]=df["%"].map("{:.2f}".format)
        st.dataframe(df.style.applymap(dir_color,subset=["%"]),
                     hide_index=True,use_container_width=True)

    # ---------- INDIA ----------
    with c2:
        st.subheader("🇮🇳 India Markets")
        rows=[]
        for k,s in INDIA.items():
            v=extract_price(market_data,s)
            if v: rows.append([k,v[0],v[1],v[2]])
        df=pd.DataFrame(rows,columns=["Market","Prev Close","Price","%"])
        df["%"]=df["%"].map("{:.2f}".format)
        st.dataframe(df.style.applymap(dir_color,subset=["%"]),
                     hide_index=True,use_container_width=True)

    # ---------- BONDS ----------
    with c3:
        st.subheader("💰 Bonds & Commodities")
        rows=[]
        for k,s in BONDS_COMMODITIES.items():
            v=extract_price(market_data,s)
            if v: rows.append([k,v[0],v[1],v[2]])
        df=pd.DataFrame(rows,columns=["Asset","Prev Close","Price","%"])
        df["%"]=df["%"].map("{:.2f}".format)
        st.dataframe(df.style.applymap(dir_color,subset=["%"]),
                     hide_index=True,use_container_width=True)

    # =================================================
    # 🔥 HEATMAP
    # =================================================
    st.subheader("🔥 NIFTY 50 Heatmap (Weight-aware)")

    caps=get_market_caps(NIFTY_50)
    total=sum(caps.values())

    rows=[];adv=dec=neu=0
    for s in NIFTY_50:
        v=extract_price(market_data,f"{s}.NS")
        if v and s in caps:
            wt=round((caps[s]/total)*100,2)
            rows.append([s,v[2],round(caps[s],0),wt])
            adv+=v[2]>0
            dec+=v[2]<0
            neu+=v[2]==0

    m1,m2,m3=st.columns(3)
    m1.metric("Advances",adv)
    m2.metric("Declines",dec)
    m3.metric("Neutral",neu)

    hdf=pd.DataFrame(rows,columns=["Stock","%","MCap ₹Cr","Weight %"])
    hdf["%"]=hdf["%"].map("{:.2f}".format)

    st.dataframe(
        hdf.style.applymap(heat_color,subset=["%"]),
        hide_index=True,use_container_width=True
    )

# =================================================
# TAB 2
# =================================================
with tab2:
    st.subheader("📈 NIFTY Options – FREE (Levels Only)")
    st.info("Option chain may be unavailable on free data")

# =================================================
st.caption("📌 Educational only. Not investment advice.")
