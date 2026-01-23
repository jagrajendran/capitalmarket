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
st.set_page_config(page_title="Capital Market Pulse — FREE", layout="wide")

ist = pytz.timezone("Asia/Kolkata")
st.title("📊 Capital Market Pulse — FREE Intraday")
st.caption("Free data only • Honest signals • Intraday-ready")
st.markdown(f"🕒 **Last updated:** {datetime.now(ist).strftime('%d-%b-%Y %I:%M %p IST')}")

# =================================================
# CONSTANTS
# =================================================
HIGH_IMPACT_KEYWORDS = [
    "rbi","fed","interest rate","rate hike","rate cut","inflation",
    "cpi","gdp","recession","crash","selloff","war","geopolitical"
]
LOW_IMPACT_KEYWORDS = [
    "opinion","outlook","technical","expert view","strategy","may","could"
]

# =================================================
# COMMON FUNCTIONS
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
        prev = c.iloc[-2]
        curr = c.iloc[-1]
        pct = round(((curr / prev) - 1) * 100, 2)
        return round(curr,2), pct
    except:
        return None

@st.cache_data(ttl=1800)
def get_market_caps(stocks):
    caps = {}
    for s in stocks:
        try:
            info = yf.Ticker(f"{s}.NS").fast_info
            mc = info.get("marketCap")
            if mc:
                caps[s] = mc / 1e7   # ₹ Crore approx
        except:
            continue
    return caps

def heat_color(v):
    if v > 1: return "background-color:#1b5e20;color:white"
    if v > 0: return "background-color:#c8e6c9"
    if v < -1: return "background-color:#b71c1c;color:white"
    if v < 0: return "background-color:#f4c7c3"
    return "background-color:#eeeeee"

def dir_color(v):
    return "color:#137333;font-weight:bold" if v > 0 else "color:#a50e0e;font-weight:bold"

def ai_takeaway(t):
    t = t.lower()
    if "rbi" in t: return "RBI cue → rate-sensitive stocks"
    if "fed" in t: return "Fed signal → global risk"
    if "inflation" in t: return "Inflation → yields focus"
    if "oil" in t: return "Oil → inflation pressure"
    if "earnings" in t: return "Results → stock volatility"
    if "war" in t: return "Geo risk → volatility"
    return "Market sentiment cue"

# =================================================
# FREE OPTIONS OI
# =================================================
@st.cache_data(ttl=300)
def get_nifty_oi():
    for sym in ["^NSEI", "NIFTY.NS"]:
        try:
            t = yf.Ticker(sym)
            if not t.options:
                continue
            exp = t.options[0]
            oc = t.option_chain(exp)
            if oc.calls.empty or oc.puts.empty:
                continue
            return exp, oc.calls, oc.puts
        except:
            continue
    return None, None, None

# =================================================
# SYMBOL GROUPS
# =================================================
GLOBAL = {
    "S&P500":"^GSPC","NASDAQ":"^IXIC","DOW":"^DJI",
    "NIKKEI":"^N225","HANG":"^HSI","DAX":"^GDAXI","FTSE":"^FTSE"
}

INDIA = {
    "GIFT":"^NIFTY_GIFT","SGX":"SGXNIFTY=F",
    "NIFTY":"^NSEI","BANKNIFTY":"^NSEBANK",
    "SENSEX":"^BSESN","VIX":"^INDIAVIX","USDINR":"USDINR=X"
}

BONDS_COMMODITIES = {
    "US10Y":"^TNX","GOLD":"GC=F","SILVER":"SI=F",
    "CRUDE":"CL=F","NG":"NG=F","COPPER":"HG=F",
    "URANIUM":"URA"
}

SECTOR_SYMBOLS = {
    "FIN":"^NSEBANK","IT":"^CNXIT","ENERGY":"^CNXENERGY",
    "AUTO":"^CNXAUTO","FMCG":"^CNXFMCG","PHARMA":"^CNXPHARMA"
}

# =================================================
# FULL STOCK LISTS (50 + 50)
# =================================================
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
"ABB","ADANIGREEN","ADANITRANS","ALKEM","AMBUJACEM","AUROPHARMA","BANDHANBNK",
"BERGEPAINT","BIOCON","BOSCHLTD","CANBK","CHOLAFIN","COLPAL","CONCOR","DABUR",
"DLF","GAIL","GODREJCP","HAVELLS","HDFCAMC","ICICIGI","ICICIPRULI","IGL","INDIGO",
"JINDALSTEL","LUPIN","MARICO","MCDOWELL-N","MOTHERSON","MUTHOOTFIN","NAUKRI",
"NMDC","PAGEIND","PEL","PETRONET","PIDILITIND","PNB","SHREECEM","SIEMENS","SRF",
"TORNTPHARM","TRENT","TVSMOTOR","UBL","VEDL","VOLTAS","ZEEL","ZYDUSLIFE"
]

# =================================================
# FETCH DATA
# =================================================
market_data = fetch_batch({
    **GLOBAL, **INDIA, **BONDS_COMMODITIES, **SECTOR_SYMBOLS,
    **{s: f"{s}.NS" for s in NIFTY_50 + NIFTY_NEXT_50}
})

# =================================================
# TABS
# =================================================
tab1, tab2 = st.tabs(["📊 Dashboard", "📈 Options OI"])

# =================================================
# TAB 1: DASHBOARD
# =================================================
with tab1:

    # -------- HEATMAP --------
    st.subheader("🔥 Heatmap (Market Cap & Weight)")
    choice = st.radio("Index",["NIFTY 50","NIFTY NEXT 50"],horizontal=True)
    stocks = NIFTY_50 if choice=="NIFTY 50" else NIFTY_NEXT_50

    caps = get_market_caps(stocks)
    total_cap = sum(caps.values())

    rows=[]
    adv=dec=neu=0
    for s in stocks:
        v = extract_price(market_data,f"{s}.NS")
        if v and s in caps:
            weight = round((caps[s]/total_cap)*100,2)
            rows.append([s,v[1],round(caps[s],0),weight])
            adv += v[1]>0
            dec += v[1]<0
            neu += v[1]==0

    c1,c2,c3 = st.columns(3)
    c1.metric("Advances",adv)
    c2.metric("Declines",dec)
    c3.metric("Neutral",neu)

    df = pd.DataFrame(rows,columns=["Stock","% Change","Mkt Cap (₹ Cr)","Weight %"])
    st.dataframe(df.style.applymap(heat_color,subset=["% Change"]),
                 hide_index=True,use_container_width=False)

# =================================================
# TAB 2: OPTIONS OI
# =================================================
with tab2:
    st.subheader("📈 NIFTY Options – FREE")
    exp,calls,puts = get_nifty_oi()
    if exp:
        top_c = calls.sort_values("openInterest",ascending=False).head(5)
        top_p = puts.sort_values("openInterest",ascending=False).head(5)
        c1,c2 = st.columns(2)
        c1.dataframe(top_c[["strike","openInterest"]],hide_index=True)
        c2.dataframe(top_p[["strike","openInterest"]],hide_index=True)
        st.metric("Support",int(top_p.iloc[0]["strike"]))
        st.metric("Resistance",int(top_c.iloc[0]["strike"]))
    else:
        st.warning("Option chain unavailable (free data limit)")

st.caption("📌 Educational only. Not investment advice.")
