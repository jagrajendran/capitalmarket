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

        closes = df["Close"].dropna()
        if len(closes) < 2:
            return None

        prev = round(closes.iloc[-2], 2)
        curr = round(closes.iloc[-1], 2)
        pct = round(((curr / prev) - 1) * 100, 2)
        return prev, curr, pct
    except:
        return None

def dir_color(val):
    return (
        "background-color:#e6f4ea;color:#137333;font-weight:bold"
        if val > 0 else
        "background-color:#fdecea;color:#a50e0e;font-weight:bold"
    )

def impact_label(weight, change):
    score = abs(weight * change)
    if score > 4:
        return "HIGH"
    elif score > 2:
        return "MEDIUM"
    return "LOW"

def impact_color(val):
    if val == "HIGH":
        return "background-color:#fdecea;color:#a50e0e;font-weight:bold"
    if val == "MEDIUM":
        return "background-color:#fff4e5;color:#8a6d3b;font-weight:bold"
    return "background-color:#e6f4ea;color:#137333;font-weight:bold"

def ai_takeaway(headline):
    h = headline.lower()
    if "rbi" in h:
        return "RBI policy cue → rate-sensitive stocks may react"
    if "fed" in h:
        return "Fed signal → global risk sentiment impacted"
    if "inflation" in h:
        return "Inflation data → bond yields & rates in focus"
    if "oil" in h or "crude" in h:
        return "Oil prices → inflation & energy stocks affected"
    if "earnings" in h:
        return "Earnings → stock-specific volatility"
    if "war" in h or "geopolitical" in h:
        return "Geopolitical risk → volatility rises"
    return "Market sentiment cue → watch index reaction"

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
            expiry = t.options[0]
            opt = t.option_chain(expiry)
            if opt.calls.empty or opt.puts.empty:
                continue
            return expiry, opt.calls, opt.puts
        except:
            continue
    return None, None, None

# =================================================
# SYMBOLS
# =================================================
GLOBAL = {
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "Dow Jones": "^DJI",
    "Nikkei 225": "^N225",
    "Hang Seng": "^HSI",
    "DAX": "^GDAXI",
    "FTSE 100": "^FTSE"
}

INDIA = {
    "GIFT NIFTY": "^NIFTY_GIFT",
    "SGX NIFTY": "SGXNIFTY=F",
    "NIFTY 50": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "SENSEX": "^BSESN",
    "India VIX": "^INDIAVIX",
    "USDINR": "USDINR=X"
}

SECTOR_BASE_WEIGHTS = {
    "Financial Services": 36.5,
    "Information Technology": 12.0,
    "Oil, Gas & Consumable Fuels": 9.5,
    "Automobile & Auto Components": 8.0,
    "Fast Moving Consumer Goods": 6.5,
    "Telecommunication": 4.5,
    "Construction / Capital Goods": 4.0,
    "Healthcare / Pharma": 3.5
}

SECTOR_SYMBOLS = {
    "Financial Services": "^NSEBANK",
    "Information Technology": "^CNXIT",
    "Oil, Gas & Consumable Fuels": "^CNXENERGY",
    "Automobile & Auto Components": "^CNXAUTO",
    "Fast Moving Consumer Goods": "^CNXFMCG",
    "Telecommunication": "^CNXMEDIA",
    "Construction / Capital Goods": "^CNXINFRA",
    "Healthcare / Pharma": "^CNXPHARMA"
}

# =================================================
# FETCH DATA
# =================================================
market_data = fetch_batch_data({**GLOBAL, **INDIA, **SECTOR_SYMBOLS})

# =================================================
# TABS
# =================================================
tab1, tab2 = st.tabs(["📊 Market Dashboard", "📈 Options OI (FREE)"])

# =================================================
# TAB 1: MARKET DASHBOARD
# =================================================
with tab1:
    st.subheader("🌍 Global Markets")
    rows=[]
    for k,sym in GLOBAL.items():
        v=extract_price(market_data,sym)
        if v: rows.append([k,v[0],v[1],v[2]])
    df=pd.DataFrame(rows,columns=["Index","Prev","Current","%Chg"])
    st.dataframe(df.style.applymap(dir_color,subset=["%Chg"]),
                 hide_index=True)

    st.markdown("---")
    st.subheader("🇮🇳 India Markets")
    rows=[]
    for k,sym in INDIA.items():
        v=extract_price(market_data,sym)
        if v: rows.append([k,v[0],v[1],v[2]])
    df=pd.DataFrame(rows,columns=["Market","Prev","Current","%Chg"])
    st.dataframe(df.style.applymap(dir_color,subset=["%Chg"]),
                 hide_index=True)

    st.markdown("---")
    st.subheader("🏭 Sector Performance")
    rows=[]
    sector_data=fetch_batch_data(SECTOR_SYMBOLS)
    for s,sym in SECTOR_SYMBOLS.items():
        v=extract_price(sector_data,sym)
        if v:
            wt=SECTOR_BASE_WEIGHTS[s]
            rows.append([s,f"{wt:.1f} %",f"{v[2]:.2f} %",impact_label(wt,v[2])])
    rows.append(["Other Sectors",f"{round(100-sum(SECTOR_BASE_WEIGHTS.values()),1)} %","—","LOW"])
    df=pd.DataFrame(rows,columns=["Sector","Weight","%Chg","Impact"])
    st.dataframe(df.style.applymap(impact_color,subset=["Impact"]),
                 hide_index=True)

    # ================= NEWS =================
    st.markdown("---")
    st.subheader("📰 Market News (Last 48 Hours)")

    feeds = {
        "India": "https://news.google.com/rss/search?q=india+stock+market+nifty",
        "Global": "https://news.google.com/rss/search?q=global+financial+markets"
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
            if (now-pub).total_seconds()>48*3600:
                continue
            t=e.title.lower()
            impact="HIGH" if any(k in t for k in HIGH_IMPACT_KEYWORDS) else \
                   "LOW" if any(k in t for k in LOW_IMPACT_KEYWORDS) else "NORMAL"
            news.append([cat,impact,e.title,ai_takeaway(e.title),
                         pub.strftime("%d-%b-%Y %I:%M %p IST"),e.link])

    if news:
        df=pd.DataFrame(news,columns=["Category","Impact","Headline","AI Takeaway","Published","Link"])
        st.dataframe(df.style.applymap(impact_color,subset=["Impact"]),
                     hide_index=True,
                     column_config={"Link":st.column_config.LinkColumn("Open")})
    else:
        st.info("No major market news in last 48 hours")

# =================================================
# TAB 2: OPTIONS OI
# =================================================
with tab2:
    st.subheader("📈 NIFTY Options – FREE OI Levels")
    expiry,calls,puts=get_nifty_option_chain_free()

    if expiry:
        st.caption(f"Nearest Expiry: {expiry}")
        top_c=calls.sort_values("openInterest",ascending=False).head(5)
        top_p=puts.sort_values("openInterest",ascending=False).head(5)

        c1,c2=st.columns(2)
        c1.dataframe(top_c[["strike","openInterest","lastPrice"]],
                     hide_index=True)
        c2.dataframe(top_p[["strike","openInterest","lastPrice"]],
                     hide_index=True)

        st.metric("🟢 Support",int(top_p.iloc[0]["strike"]))
        st.metric("🔴 Resistance",int(top_c.iloc[0]["strike"]))
    else:
        st.warning("NIFTY option chain unavailable (free data limitation)")

st.caption("📌 Educational dashboard only. Not investment advice.")
