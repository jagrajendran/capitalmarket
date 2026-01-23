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

        c = df["Close"].dropna()
        if len(c) < 2:
            return None

        prev = round(c.iloc[-2], 2)
        curr = round(c.iloc[-1], 2)
        pct = round(((curr / prev) - 1) * 100, 2)
        return prev, curr, pct
    except:
        return None

def color_dir(val):
    return (
        "color:#137333;font-weight:bold"
        if val > 0 else
        "color:#a50e0e;font-weight:bold"
    )

def impact_label(weight, change):
    score = abs(weight * change)
    if score > 4:
        return "HIGH"
    elif score > 2:
        return "MED"
    return "LOW"

def impact_color(val):
    return (
        "color:#a50e0e;font-weight:bold" if val=="HIGH"
        else "color:#8a6d3b;font-weight:bold" if val=="MED"
        else "color:#137333;font-weight:bold"
    )

def ai_takeaway(title):
    t = title.lower()
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
def get_nifty_option_chain_free():
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

SECTOR_BASE = {
    "FIN":36.5,"IT":12,"ENERGY":9.5,"AUTO":8,
    "FMCG":6.5,"TELECOM":4.5,"INFRA":4,"PHARMA":3.5
}

SECTOR_SYMBOLS = {
    "FIN":"^NSEBANK","IT":"^CNXIT","ENERGY":"^CNXENERGY",
    "AUTO":"^CNXAUTO","FMCG":"^CNXFMCG","TELECOM":"^CNXMEDIA",
    "INFRA":"^CNXINFRA","PHARMA":"^CNXPHARMA"
}

# =================================================
# FETCH DATA
# =================================================
market_data = fetch_batch_data({**GLOBAL, **INDIA, **BONDS_COMMODITIES, **SECTOR_SYMBOLS})

# =================================================
# TABS
# =================================================
tab1, tab2 = st.tabs(["📊 Dashboard", "📈 Options OI"])

# =================================================
# TAB 1: DASHBOARD
# =================================================
with tab1:

    # ---- GLOBAL ----
    st.subheader("🌍 Global")
    rows=[]
    for k,s in GLOBAL.items():
        v=extract_price(market_data,s)
        if v: rows.append([k,v[0],v[1],v[2]])
    df=pd.DataFrame(rows,columns=["MKT","PREV","CURR","%"])
    st.dataframe(df.style.applymap(color_dir,subset=["%"]),
                 hide_index=True,use_container_width=False)

    # ---- INDIA ----
    st.subheader("🇮🇳 India")
    rows=[]
    for k,s in INDIA.items():
        v=extract_price(market_data,s)
        if v: rows.append([k,v[0],v[1],v[2]])
    df=pd.DataFrame(rows,columns=["MKT","PREV","CURR","%"])
    st.dataframe(df.style.applymap(color_dir,subset=["%"]),
                 hide_index=True,use_container_width=False)

    # ---- SECTORS ----
    st.subheader("🏭 Sectors (NIFTY Context)")
    rows=[]
    for k,s in SECTOR_SYMBOLS.items():
        v=extract_price(market_data,s)
        if v:
            rows.append([k,f"{SECTOR_BASE[k]}%",v[2],impact_label(SECTOR_BASE[k],v[2])])
    rows.append(["OTHERS",f"{round(100-sum(SECTOR_BASE.values()),1)}%","—","LOW"])
    df=pd.DataFrame(rows,columns=["SEC","WT","%","IMPACT"])
    st.dataframe(df.style.applymap(impact_color,subset=["IMPACT"]),
                 hide_index=True,use_container_width=False)

    # ---- BONDS & COMMODITIES ----
    st.subheader("💰 Bonds & Commodities")
    rows=[]
    for k,s in BONDS_COMMODITIES.items():
        v=extract_price(market_data,s)
        if v: rows.append([k,v[1],v[2]])
    df=pd.DataFrame(rows,columns=["ASSET","PRICE","%"])
    st.dataframe(df.style.applymap(color_dir,subset=["%"]),
                 hide_index=True,use_container_width=False)

    # ---- NEWS ----
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
            except:
                continue
            if (now-pub).total_seconds()>48*3600: continue
            t=e.title.lower()
            impact="HIGH" if any(k in t for k in HIGH_IMPACT_KEYWORDS) else \
                   "LOW" if any(k in t for k in LOW_IMPACT_KEYWORDS) else "NORMAL"
            news.append([cat,impact,e.title,ai_takeaway(e.title),
                         pub.strftime("%d-%b %I:%M"),e.link])
    if news:
        df=pd.DataFrame(news,columns=["CAT","IMP","HEADLINE","TAKEAWAY","TIME","LINK"])
        st.dataframe(df.style.applymap(impact_color,subset=["IMP"]),
                     hide_index=True,use_container_width=True,
                     column_config={"LINK":st.column_config.LinkColumn("Open")})
    else:
        st.info("No major news")

# =================================================
# TAB 2: OPTIONS OI (FREE)
# =================================================
with tab2:
    st.subheader("📈 NIFTY Options – FREE")
    exp,calls,puts=get_nifty_option_chain_free()
    if exp:
        st.caption(f"Expiry: {exp}")
        top_c=calls.sort_values("openInterest",ascending=False).head(5)
        top_p=puts.sort_values("openInterest",ascending=False).head(5)
        c1,c2=st.columns(2)
        c1.dataframe(top_c[["strike","openInterest"]],
                     hide_index=True,use_container_width=False)
        c2.dataframe(top_p[["strike","openInterest"]],
                     hide_index=True,use_container_width=False)
        st.metric("Support",int(top_p.iloc[0]["strike"]))
        st.metric("Resistance",int(top_c.iloc[0]["strike"]))
    else:
        st.warning("Option chain unavailable (free data limit)")

st.caption("📌 Educational only. Not investment advice.")
