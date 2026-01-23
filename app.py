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

st.set_page_config(page_title="Capital Market Pulse — PRO", layout="wide")

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

@st.cache_data(ttl=86400)
def get_market_caps(symbols):
    caps = {}
    for name, sym in symbols.items():
        try:
            cap = yf.Ticker(sym).info.get("marketCap")
            caps[name] = round(cap / 1e7, 0) if cap else None  # ₹ Cr approx
        except:
            caps[name] = None
    return caps

def extract_price(data, symbol):
    try:
        df = data[symbol] if isinstance(data.columns, pd.MultiIndex) else data
        closes = df["Close"].dropna()
        if len(closes) < 2:
            return None
        prev = round(closes.iloc[-2], 2)
        curr = round(closes.iloc[-1], 2)
        pct = round(((curr / prev) - 1) * 100, 2)
        return prev, curr, pct
    except:
        return None

def heat_color(val):
    v = max(min(val, 5), -5)
    if v > 0:
        g = int(255 - (v / 5) * 140)
        return f"background-color: rgb({g},255,{g}); font-weight:bold"
    r = int(255 - (abs(v) / 5) * 140)
    return f"background-color: rgb(255,{r},{r}); font-weight:bold"

def dir_color(val):
    return (
        "background-color:#e6f4ea;color:#137333;font-weight:bold"
        if val > 0 else
        "background-color:#fdecea;color:#a50e0e;font-weight:bold"
    )

# =================================================
# SYMBOL DEFINITIONS
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
# NIFTY STOCK LISTS (FULL)
# =================================================
NIFTY_50 = {k: f"{k}.NS" for k in [
    "ADANIENT","ADANIPORTS","APOLLOHOSP","ASIANPAINT","AXISBANK","BAJAJ-AUTO",
    "BAJFINANCE","BAJAJFINSV","BHARTIARTL","BPCL","BRITANNIA","CIPLA","COALINDIA",
    "DIVISLAB","DRREDDY","EICHERMOT","GRASIM","HCLTECH","HDFCBANK","HDFCLIFE",
    "HEROMOTOCO","HINDALCO","HINDUNILVR","ICICIBANK","INDUSINDBK","INFY","ITC",
    "JSWSTEEL","KOTAKBANK","LT","LTIM","MARUTI","NESTLEIND","NTPC","ONGC",
    "POWERGRID","RELIANCE","SBILIFE","SBIN","SUNPHARMA","TATACONSUM","TATAMOTORS",
    "TATASTEEL","TECHM","TITAN","ULTRACEMCO","UPL","WIPRO"
]}

NIFTY_NEXT_50 = {k: f"{k}.NS" for k in [
    "ABB","ADANIGREEN","ADANIPOWER","ALKEM","AMBUJACEM","APOLLOTYRE","ASHOKLEY",
    "ASTRAL","AUROPHARMA","BANDHANBNK","BERGEPAINT","BIOCON","BOSCHLTD","CANBK",
    "CHOLAFIN","COFORGE","COLPAL","CONCOR","DABUR","DALBHARAT","DLF","GAIL",
    "GODREJCP","HAVELLS","ICICIGI","ICICIPRULI","IGL","INDIGO","JINDALSTEL",
    "LUPIN","MUTHOOTFIN","NMDC","PAGEIND","PEL","PETRONET","PIDILITIND","POLYCAB",
    "PVRINOX","SHREECEM","SIEMENS","SRF","TORNTPHARM","TRENT","TVSMOTOR","UBL",
    "VOLTAS","ZEEL"
]}

# Static weight maps (realistic, rest default 0.5)
NIFTY50_WEIGHTS = {
    "RELIANCE":10.5,"HDFCBANK":8.9,"ICICIBANK":7.2,"INFY":6.4,"TCS":4.6,
    "LT":4.0,"HINDUNILVR":3.1,"ITC":3.0,"AXISBANK":2.9,"SBIN":2.8
}
NEXT50_WEIGHTS = {
    "PIDILITIND":3.2,"DLF":2.8,"TRENT":2.6,"INDIGO":2.5,"GODREJCP":2.4
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
for k,sym in GLOBAL.items():
    v = extract_price(market_data, sym)
    if v: rows.append([k,v[0],v[1],v[2]])
df = pd.DataFrame(rows,columns=["Index","Prev","Current","%Chg"])
st.dataframe(df.style.applymap(dir_color,subset=["%Chg"]),use_container_width=False,hide_index=True)

# =================================================
# 🇮🇳 INDIA
# =================================================
st.markdown("---")
st.subheader("🇮🇳 India Markets")
rows=[]
for k,sym in INDIA.items():
    v=extract_price(market_data,sym)
    if v: rows.append([k,v[0],v[1],v[2]])
df=pd.DataFrame(rows,columns=["Market","Prev","Current","%Chg"])
st.dataframe(df.style.applymap(dir_color,subset=["%Chg"]),use_container_width=False,hide_index=True)

# =================================================
# 🏭 SECTORS
# =================================================
st.markdown("---")
st.subheader("🏭 Sectors")
rows=[]
for k,sym in SECTORS.items():
    v=extract_price(market_data,sym)
    if v: rows.append([k,v[2]])
df=pd.DataFrame(rows,columns=["Sector","%Chg"])
st.dataframe(df.style.applymap(dir_color,subset=["%Chg"]),use_container_width=False,hide_index=True)

# =================================================
# 🔥 HEATMAP
# =================================================
st.markdown("---")
st.subheader("🔥 Heatmap")

choice=st.radio("Index",["NIFTY 50","NIFTY NEXT 50"],horizontal=True)
stocks=NIFTY_50 if choice=="NIFTY 50" else NIFTY_NEXT_50
weights=NIFTY50_WEIGHTS if choice=="NIFTY 50" else NEXT50_WEIGHTS

heat_data=fetch_batch_data(stocks)
caps=get_market_caps(stocks)

adv=dec=neu=0
rows=[]
for name,sym in stocks.items():
    v=extract_price(heat_data,sym)
    if not v: continue
    if v[2]>0: adv+=1
    elif v[2]<0: dec+=1
    else: neu+=1
    rows.append([name,v[0],v[1],v[2],caps.get(name),weights.get(name,0.5)])

c1,c2,c3=st.columns(3)
c1.metric("Advances 🟢",adv)
c2.metric("Declines 🔴",dec)
c3.metric("Neutral ⚪",neu)

df=pd.DataFrame(rows,columns=["Stock","Prev","Current","%Chg","MCap ₹Cr","Weight %"])
st.dataframe(df.style.applymap(heat_color,subset=["%Chg"]),use_container_width=False,hide_index=True)

# =================================================
# 💰 BONDS & COMMODITIES
# =================================================
st.markdown("---")
st.subheader("💰 Bonds & Commodities")
rows=[]
for k,sym in BONDS_COMMODITIES.items():
    v=extract_price(market_data,sym)
    if v: rows.append([k,v[0],v[1],v[2]])
df=pd.DataFrame(rows,columns=["Asset","Prev","Current","%Chg"])
st.dataframe(df.style.applymap(dir_color,subset=["%Chg"]),use_container_width=False,hide_index=True)

# =================================================
# 📊 SENTIMENT
# =================================================
st.markdown("---")
st.subheader("📊 Market Sentiment")

score=0; reasons=[]
vix=extract_price(market_data,"^INDIAVIX")
bond=extract_price(market_data,"^TNX")
spx=extract_price(market_data,"^GSPC")

if vix and vix[2]<0: score+=1; reasons.append("India VIX falling → volatility easing")
else: reasons.append("India VIX rising → risk increasing")

if bond and bond[2]<0: score+=1; reasons.append("US 10Y yield falling → equity supportive")
else: reasons.append("US 10Y yield rising → equity pressure")

if spx and spx[2]>0: score+=1; reasons.append("S&P 500 positive → global risk-on")
else: reasons.append("S&P 500 weak → global caution")

mood={3:"🟢 STRONG RISK ON",2:"🟡 MODERATE RISK ON",1:"🟠 CAUTION",0:"🔴 RISK OFF"}
st.metric("Overall Market Mood",mood[score])
for r in reasons: st.write("•",r)

# =================================================
# 📰 NEWS
# =================================================
st.markdown("---")
st.subheader("📰 Market News")
feed=feedparser.parse("https://news.google.com/rss/search?q=india+stock+market")
news=[[e.title,e.link] for e in feed.entries[:8]]
df=pd.DataFrame(news,columns=["Headline","Link"])
st.dataframe(df,use_container_width=True,hide_index=True,
             column_config={"Link":st.column_config.LinkColumn("Open")})

st.caption("📌 Educational dashboard only. Not investment advice.")
