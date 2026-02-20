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
        threads=False,
        progress=False
    )

# --------- UPDATED ----------
def extract_price(data, sym):
    try:
        df=data[sym]
        close=df["Close"].dropna()
        prev=round(float(close.iloc[-2]),2)
        curr=round(float(close.iloc[-1]),2)
        chg =round(curr-prev,2)
        pct =round(((curr/prev)-1)*100,2)
        return prev,curr,chg,pct
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
    return "color:#137333;font-weight:bold" if float(v)>0 else "color:#a50e0e;font-weight:bold"

# --------- NEW ----------
def change_color(v):
    return "color:#137333;font-weight:bold" if float(v)>0 else "color:#a50e0e;font-weight:bold"

def heat_color(v):
    v=float(v)
    if v>1: return "background-color:#1b5e20;color:white"
    if v>0: return "background-color:#c8e6c9"
    if v<-1: return "background-color:#b71c1c;color:white"
    if v<0: return "background-color:#f4c7c3"
    return ""

# =================================================
# NEWS FETCH
# =================================================
@st.cache_data(ttl=900)
def fetch_news():
    url="https://news.google.com/rss/search?q=india+stock+market"
    return feedparser.parse(url).entries[:12]

# =================================================
# SYMBOL GROUPS
# =================================================
GLOBAL={"S&P500":"^GSPC","NASDAQ":"^IXIC","DOW":"^DJI",
"NIKKEI":"^N225","HANG SENG":"^HSI","DAX":"^GDAXI","FTSE":"^FTSE"}

INDIA={"GIFT NIFTY":"^NIFTY_GIFT","NIFTY":"^NSEI","BANKNIFTY":"^NSEBANK",
"SENSEX":"^BSESN","VIX":"^INDIAVIX","USDINR":"USDINR=X"}

SECTORS={
"NIFTY AUTO":"^CNXAUTO",
"NIFTY BANK":"^NSEBANK",
"NIFTY IT":"^CNXIT",
"NIFTY FMCG":"^CNXFMCG",
"NIFTY METAL":"^CNXMETAL",
"NIFTY PHARMA":"^CNXPHARMA",
"NIFTY PSU BANK":"^CNXPSUBANK",
"NIFTY REALTY":"^CNXREALTY",
"NIFTY MEDIA":"^CNXMEDIA",
"NIFTY ENERGY":"^CNXENERGY",
"NIFTY FINANCIAL SERVICES": "^CNXFINANCE",
"NIFTY PRIVATE BANK": "^NIFTYPVTBANK"
}

CAP_INDICES={
"LARGE CAP (NIFTY 50)":"^NSEI",
"MID CAP (NIFTY MIDCAP 100)":"^NSEMDCP50",
"SMALL CAP (NIFTY SMALLCAP 100)":"^NIFTY_SMLCAP_100.NS",
"MICRO CAP (NIFTY MICROCAP 250)":"^NIFTYMICROCAP250"
}

BONDS_COMMODITIES={"US10Y":"^TNX","GOLD":"GC=F","SILVER":"SI=F",
"CRUDE":"CL=F","COPPER":"HG=F"}

NIFTY_50=[
"ADANIENT","ADANIPORTS","APOLLOHOSP","ASIANPAINT","AXISBANK","BAJAJ-AUTO",
"BAJFINANCE","BAJAJFINSV","BPCL","BHARTIARTL","BRITANNIA","CIPLA","COALINDIA",
"DIVISLAB","DRREDDY","EICHERMOT","GRASIM","HCLTECH","HDFCBANK","HDFCLIFE",
"HEROMOTOCO","HINDALCO","HINDUNILVR","ICICIBANK","ITC","INDUSINDBK","INFY",
"JSWSTEEL","KOTAKBANK","LT","LTIM","M&M","MARUTI","NESTLEIND","NTPC","ONGC",
"POWERGRID","RELIANCE","SBIN","SUNPHARMA","TATACONSUM","TATAMOTORS",
"TATASTEEL","TECHM","TITAN","ULTRACEMCO","UPL","WIPRO"
]

NIFTY_NEXT_50=[
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
market_data=fetch_batch({
**GLOBAL,**INDIA,**SECTORS,**CAP_INDICES,**BONDS_COMMODITIES,
**{s:f"{s}.NS" for s in NIFTY_50+NIFTY_NEXT_50}
})

news=fetch_news()

# =================================================
# MARKET MOOD
# =================================================
pos=neg=0
reasons=[]

for idx in ["^NSEI","^NSEBANK","^BSESN"]:
    v=extract_price(market_data,idx)
    if v:
        if v[3]>0:
            pos+=1
            reasons.append(f"{idx} up {v[3]:.2f}%")
        else:
            neg+=1
            reasons.append(f"{idx} down {v[3]:.2f}%")

vix=extract_price(market_data,"^INDIAVIX")
if vix:
    if vix[3]<0:
        pos+=1
        reasons.append("India VIX falling (risk-on)")
    else:
        neg+=1
        reasons.append("India VIX rising (risk-off)")

if pos>neg:
    mood="BULLISH 🟢"
elif neg>pos:
    mood="BEARISH 🔴"
else:
    mood="NEUTRAL ⚪"

# =================================================
# TABS
# =================================================
tab1,tab2=st.tabs(["📊 Dashboard","📈 Options OI"])

# =================================================
# TAB 1
# =================================================
with tab1:

    st.subheader("😊 Market Mood")

    if "BULLISH" in mood:
        st.success(f"Overall Mood: {mood}")
    elif "BEARISH" in mood:
        st.error(f"Overall Mood: {mood}")
    else:
        st.warning(f"Overall Mood: {mood}")

    st.markdown("**Reasons:**")
    for r in reasons:
        st.write(f"• {r}")

    # =========================
    # ROW 1 : Global | India | Bonds
    # =========================
    r1c1,r1c2,r1c3=st.columns(3)

    def market_table(title,data_dict):
        rows=[]
        for k,s in data_dict.items():
            v=extract_price(market_data,s)
            if v:
                rows.append([k,f"{v[0]:.2f}",f"{v[1]:.2f}",f"{v[2]:.2f}",f"{v[3]:.2f}"])

        df=pd.DataFrame(rows,columns=["Market","Prev","Price","Change","%"])
        st.subheader(title)
        st.dataframe(
            df.style
              .applymap(change_color,subset=["Change"])
              .applymap(dir_color,subset=["%"]),
            hide_index=True,
            use_container_width=True
        )

    with r1c1:
        market_table("🌍 Global Markets",GLOBAL)
    with r1c2:
        market_table("🇮🇳 India Markets",INDIA)
    with r1c3:
        market_table("💰 Bonds & Commodities",BONDS_COMMODITIES)

    # =========================
    # ROW 2 : Sector | Market Cap
    # =========================
    r2c1,r2c2=st.columns(2)

    with r2c1:
        st.subheader("🏭 Sector Performance")
        rows=[]
        for k,s in SECTORS.items():
            v=extract_price(market_data,s)
            if v:
                rows.append([k,f"{v[0]:.2f}",f"{v[1]:.2f}",f"{v[2]:.2f}",f"{v[3]:.2f}"])

        sdf=pd.DataFrame(rows,columns=["Sector","Prev","Price","Change","%"])
        st.dataframe(
            sdf.style
              .applymap(change_color,subset=["Change"])
              .applymap(dir_color,subset=["%"]),
            hide_index=True,
            use_container_width=True
        )

    with r2c2:
        st.subheader("📦 Market Cap Performance")
        rows=[]
        for k,s in CAP_INDICES.items():
            v=extract_price(market_data,s)
            if v:
                rows.append([k,f"{v[0]:.2f}",f"{v[1]:.2f}",f"{v[2]:.2f}",f"{v[3]:.2f}"])

        cdf=pd.DataFrame(rows,columns=["Category","Prev","Price","Change","%"])
        st.dataframe(
            cdf.style
              .applymap(change_color,subset=["Change"])
              .applymap(dir_color,subset=["%"]),
            hide_index=True,
            use_container_width=True
        )

    # =========================
    # HEATMAP (unchanged)
    # =========================
    st.subheader("🔥 Heatmap")

    idx_sel=st.radio("Select Index",["NIFTY 50","NIFTY NEXT 50"],horizontal=True)
    stocks=NIFTY_50 if idx_sel=="NIFTY 50" else NIFTY_NEXT_50

    caps=get_market_caps(stocks)
    total=sum(caps.values())

    rows=[];adv=dec=neu=0
    for s in stocks:
        v=extract_price(market_data,f"{s}.NS")
        if v and s in caps:
            wt=round((caps[s]/total)*100,2)
            rows.append([s,f"{v[3]:.2f}",round(caps[s],0),f"{wt:.2f}"])
            adv+=v[3]>0
            dec+=v[3]<0
            neu+=v[3]==0

    a,b,c=st.columns(3)
    a.metric("Advances",adv)
    b.metric("Declines",dec)
    c.metric("Neutral",neu)

    hdf=pd.DataFrame(rows,columns=["Stock","%","MCap ₹Cr","Weight %"])
    st.dataframe(hdf.style.applymap(heat_color,subset=["%"]),
                 hide_index=True,use_container_width=True)

    # =========================
    # MARKET NEWS (unchanged)
    # =========================
    st.subheader("📰 Market News")

    news_rows=[]
    for n in news:
        title=n.title
        link=n.link

        pub=pd.to_datetime(n.published)
        pub=pub.tz_localize("UTC").tz_convert("Asia/Kolkata")
        time=pub.strftime("%d-%b %I:%M %p")

        txt=title.lower()
        if any(x in txt for x in ["india","nifty","sensex","rbi","rupee","banknifty"]):
            category="India"
        else:
            category="Global"

        if any(x in txt for x in ["crash","plunge","selloff","rate hike","inflation","war","recession"]):
            impact="High"
        elif any(x in txt for x in ["earnings","results","growth","profit","policy","gdp"]):
            impact="Medium"
        else:
            impact="Low"

        news_rows.append([category,title,impact,time,link])

    news_df=pd.DataFrame(news_rows,
        columns=["Category","Headline","Impact","Time (IST)","Link"]
    )

    def make_clickable(url,text):
        return f'<a href="{url}" target="_blank">{text}</a>'

    news_df["Headline"]=news_df.apply(
        lambda x: make_clickable(x["Link"],x["Headline"]),axis=1
    )

    news_df=news_df.drop(columns=["Link"])

    st.markdown(news_df.to_html(escape=False,index=False),
                unsafe_allow_html=True)

# =================================================
# TAB 2
# =================================================
with tab2:
    st.subheader("📈 NIFTY Options – FREE (Levels Only)")
    st.info("Option chain may be unavailable on free data")

# =================================================
st.caption("📌 Educational only. Not investment advice.")
