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
        prev = round(c.iloc[-2], 2)
        curr = round(c.iloc[-1], 2)
        pct = round(((curr / prev) - 1) * 100, 2)
        return curr, pct
    except:
        return None

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
# SYMBOLS
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
    "ALUM":"ALI=F","URANIUM":"URA"
}

SECTOR_WEIGHTS = {
    "FIN":36.5,"IT":12,"ENERGY":9.5,"AUTO":8,
    "FMCG":6.5,"TELECOM":4.5,"INFRA":4,"PHARMA":3.5
}
SECTOR_SYMBOLS = {
    "FIN":"^NSEBANK","IT":"^CNXIT","ENERGY":"^CNXENERGY",
    "AUTO":"^CNXAUTO","FMCG":"^CNXFMCG","TELECOM":"^CNXMEDIA",
    "INFRA":"^CNXINFRA","PHARMA":"^CNXPHARMA"
}

# =================================================
# FULL STOCK LISTS
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
# FETCH DATA (BATCHED)
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

    # GLOBAL
    st.subheader("🌍 Global")
    rows=[]
    for k,s in GLOBAL.items():
        v=extract_price(market_data,s)
        if v: rows.append([k,v[0],v[1]])
    st.dataframe(pd.DataFrame(rows,columns=["MKT","PRICE","%"])
                 .style.applymap(dir_color,subset=["%"]),
                 hide_index=True,use_container_width=False)

    # INDIA
    st.subheader("🇮🇳 India")
    rows=[]
    for k,s in INDIA.items():
        v=extract_price(market_data,s)
        if v: rows.append([k,v[0],v[1]])
    st.dataframe(pd.DataFrame(rows,columns=["MKT","PRICE","%"])
                 .style.applymap(dir_color,subset=["%"]),
                 hide_index=True,use_container_width=False)

    # HEATMAP
    st.subheader("🔥 Heatmap")
    choice = st.radio("Index",["NIFTY 50","NIFTY NEXT 50"],horizontal=True)
    stocks = NIFTY_50 if choice=="NIFTY 50" else NIFTY_NEXT_50

    adv=dec=neu=0; rows=[]
    for s in stocks:
        v=extract_price(market_data,f"{s}.NS")
        if v:
            rows.append([s,v[1]])
            adv += v[1]>0
            dec += v[1]<0
            neu += v[1]==0

    c1,c2,c3=st.columns(3)
    c1.metric("Advances",adv)
    c2.metric("Declines",dec)
    c3.metric("Neutral",neu)

    st.dataframe(pd.DataFrame(rows,columns=["STOCK","%"])
                 .style.applymap(heat_color,subset=["%"]),
                 hide_index=True,use_container_width=False)

    # SECTORS
    st.subheader("🏭 Sectors")
    rows=[]
    for k,s in SECTOR_SYMBOLS.items():
        v=extract_price(market_data,s)
        if v: rows.append([k,f"{SECTOR_WEIGHTS[k]}%",v[1]])
    rows.append(["OTHERS",f"{round(100-sum(SECTOR_WEIGHTS.values()),1)}%","—"])
    st.dataframe(pd.DataFrame(rows,columns=["SEC","WT","%"]),
                 hide_index=True,use_container_width=False)

    # BONDS & COMMODITIES
    st.subheader("💰 Bonds & Commodities")
    rows=[]
    for k,s in BONDS_COMMODITIES.items():
        v=extract_price(market_data,s)
        if v: rows.append([k,v[0],v[1]])
    st.dataframe(pd.DataFrame(rows,columns=["ASSET","PRICE","%"])
                 .style.applymap(dir_color,subset=["%"]),
                 hide_index=True,use_container_width=False)

    # NEWS
    st.subheader("📰 Market News (48h)")
    feeds={
        "India":"https://news.google.com/rss/search?q=india+stock+market",
        "Global":"https://news.google.com/rss/search?q=global+markets"
    }
    news=[]
    now=datetime.now(ist)
    for cat,url in feeds.items():
        feed=feedparser.parse(url)
        for e in feed.entries:
            try:
                pub=datetime(*e.published_parsed[:6],tzinfo=pytz.utc).astimezone(ist)
            except: continue
            if (now-pub).total_seconds()>48*3600: continue
            impact="HIGH" if any(k in e.title.lower() for k in HIGH_IMPACT_KEYWORDS) else \
                   "LOW" if any(k in e.title.lower() for k in LOW_IMPACT_KEYWORDS) else "NORMAL"
            news.append([cat,impact,e.title,ai_takeaway(e.title),
                         pub.strftime("%d-%b %I:%M"),e.link])
    if news:
        st.dataframe(pd.DataFrame(news,
            columns=["CAT","IMP","HEADLINE","TAKEAWAY","TIME","LINK"]),
            hide_index=True,use_container_width=True,
            column_config={"LINK":st.column_config.LinkColumn("Open")})
    else:
        st.info("No major news")

# =================================================
# TAB 2: OPTIONS OI
# =================================================
with tab2:
    st.subheader("📈 NIFTY Options – FREE")
    exp,calls,puts=get_nifty_oi()
    if exp:
        top_c=calls.sort_values("openInterest",ascending=False).head(5)
        top_p=puts.sort_values("openInterest",ascending=False).head(5)
        c1,c2=st.columns(2)
        c1.dataframe(top_c[["strike","openInterest"]],hide_index=True)
        c2.dataframe(top_p[["strike","openInterest"]],hide_index=True)
        st.metric("Support",int(top_p.iloc[0]["strike"]))
        st.metric("Resistance",int(top_c.iloc[0]["strike"]))
    else:
        st.warning("Option chain unavailable (free data limit)")

st.caption("📌 Educational only. Not investment advice.")
