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
        progress=False
    )

def extract_price(data, sym):
    try:
        df = data[sym]
        close = df["Close"].dropna()
        prev = round(float(close.iloc[-2]),2)
        curr = round(float(close.iloc[-1]),2)
        pct  = round(((curr/prev)-1)*100,2)
        return prev,curr,pct
    except:
        return None

@st.cache_data(ttl=1800)
def get_market_caps(stocks):
    caps={}
    for s in stocks:
        try:
            mc=yf.Ticker(f"{s}.NS").fast_info.get("marketCap")
            if mc:
                caps[s]=mc/1e7
        except:
            pass
    return caps

def dir_color(v):
    return "color:green;font-weight:bold" if float(v)>0 else "color:red;font-weight:bold"

def heat_color(v):
    v=float(v)
    if v>1: return "background-color:#1b5e20;color:white"
    if v>0: return "background-color:#c8e6c9"
    if v<-1: return "background-color:#b71c1c;color:white"
    if v<0: return "background-color:#f4c7c3"
    return ""

@st.cache_data(ttl=900)
def fetch_news():
    return feedparser.parse(
        "https://news.google.com/rss/search?q=india+stock+market"
    ).entries[:12]

# =================================================
# SYMBOL GROUPS
# =================================================
GLOBAL={"S&P500":"^GSPC","NASDAQ":"^IXIC","DOW":"^DJI",
"NIKKEI":"^N225","HANGSENG":"^HSI","DAX":"^GDAXI","FTSE":"^FTSE"}

INDIA={"GIFT":"^NIFTY_GIFT","NIFTY":"^NSEI","BANKNIFTY":"^NSEBANK",
"SENSEX":"^BSESN","VIX":"^INDIAVIX","USDINR":"USDINR=X"}

BONDS={"US10Y":"^TNX","GOLD":"GC=F","SILVER":"SI=F","CRUDE":"CL=F"}

SECTORS={"AUTO":"^CNXAUTO","IT":"^CNXIT","FMCG":"^CNXFMCG",
"METAL":"^CNXMETAL","PHARMA":"^CNXPHARMA","REALTY":"^CNXREALTY"}

CAPS={"LARGE":"^NSEI","MID":"^NIFTY_MIDCAP_50","SMALL":"^NIFTY_SMLCAP_50"}

NIFTY50=["RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","LT",
"ITC","SBIN","BHARTIARTL","AXISBANK"]

NEXT50=["ADANIGREEN","NAUKRI","PEL","PIDILITIND","DMART","DLF"]

# =================================================
# FETCH DATA
# =================================================
market_data=fetch_batch({
**GLOBAL,**INDIA,**BONDS,**SECTORS,**CAPS,
**{s:f"{s}.NS" for s in NIFTY50+NEXT50}
})

news=fetch_news()

# =================================================
# MARKET MOOD
# =================================================
pos=neg=0
reasons=[]
for i in ["^NSEI","^NSEBANK","^BSESN"]:
    v=extract_price(market_data,i)
    if v:
        if v[2]>0:
            pos+=1; reasons.append(f"{i} up {v[2]:.2f}%")
        else:
            neg+=1; reasons.append(f"{i} down {v[2]:.2f}%")

mood="BULLISH 🟢" if pos>neg else "BEARISH 🔴" if neg>pos else "NEUTRAL ⚪"

# =================================================
# TABS
# =================================================
tab1,tab2=st.tabs(["📊 Dashboard","📈 Options OI"])

# =================================================
# TAB1
# =================================================
with tab1:

    st.subheader("😊 Market Mood")
    st.success(mood)
    for r in reasons:
        st.write("•",r)

    # ===== ROW1 =====
    c1,c2,c3=st.columns(3)
    def table(title,d):
        rows=[]
        for k,s in d.items():
            v=extract_price(market_data,s)
            if v:
                rows.append([k,v[0],v[1],v[2]])
        df=pd.DataFrame(rows,columns=["Name","Prev","Price","%"])
        st.subheader(title)
        st.dataframe(df.style.applymap(dir_color,subset=["%"]),
                     hide_index=True,use_container_width=True)

    with c1: table("🌍 Global Markets",GLOBAL)
    with c2: table("🇮🇳 India Markets",INDIA)
    with c3: table("💰 Bonds & Commodities",BONDS)

    # ===== ROW2 =====
    c4,c5=st.columns(2)
    with c4: table("🏭 Sector Performance",SECTORS)
    with c5: table("📦 Market Cap Performance",CAPS)

    # ===== HEATMAP =====
    st.subheader("🔥 Heatmap")
    idx=st.radio("Index",["NIFTY 50","NIFTY NEXT 50"],horizontal=True)
    stocks=NIFTY50 if idx=="NIFTY 50" else NEXT50

    caps=get_market_caps(stocks)
    rows=[]
    for s in stocks:
        v=extract_price(market_data,f"{s}.NS")
        if v and s in caps:
            rows.append([s,v[2],caps[s]])

    hdf=pd.DataFrame(rows,columns=["Stock","%","Mcap Cr"])
    st.dataframe(hdf.style.applymap(heat_color,subset=["%"]),
                 hide_index=True,use_container_width=True)

    # ===== NEWS =====
    st.subheader("📰 Market News")
    news_rows=[]
    for n in news:
        title=n.title
        link=n.link
        time=pd.to_datetime(n.published).strftime("%d-%b %H:%M")
        news_rows.append([f"[{title}]({link})",time])

    ndf=pd.DataFrame(news_rows,columns=["Headline","Time"])
    st.markdown(ndf.to_markdown(index=False))

# =================================================
# TAB2
# =================================================
with tab2:
    st.info("Options OI coming soon...")

st.caption("📌 Educational only. Not investment advice.")
