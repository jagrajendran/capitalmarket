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
st.set_page_config(page_title="Capital Market Pulse — Intraday PRO", layout="wide")

st.title("📊 Capital Market Pulse — Intraday PRO")
st.caption("Macro → Index → Sector → Stock → News → Sentiment")

ist = pytz.timezone("Asia/Kolkata")
st.markdown(f"🕒 **Last updated:** {datetime.now(ist).strftime('%d-%b-%Y %I:%M %p IST')}")

# =================================================
# CONSTANTS
# =================================================
HIGH_IMPACT_KEYWORDS = [
    "rbi","fed","interest rate","rate hike","rate cut","inflation","cpi","wpi",
    "gdp","recession","crash","selloff","war","geopolitical","bond yield"
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
    if "rbi" in h or "repo" in h:
        return "RBI policy cue → rate-sensitive stocks may react"
    if "fed" in h:
        return "Fed signal → global risk sentiment & FII flows impacted"
    if "inflation" in h:
        return "Inflation data → bond yields & rate expectations in focus"
    if "oil" in h or "crude" in h:
        return "Oil prices → inflation & energy stocks affected"
    if "earnings" in h or "results" in h:
        return "Earnings news → stock-specific volatility likely"
    if "war" in h or "geopolitical" in h:
        return "Geopolitical risk → volatility rises"
    return "Market sentiment cue → watch index & sector reaction"

# =================================================
# SYMBOL DEFINITIONS
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

# ✅ GIFT + SGX fallback
INDIA = {
    "GIFT NIFTY": "^NIFTY_GIFT",
    "SGX NIFTY": "SGXNIFTY=F",
    "NIFTY 50": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "SENSEX": "^BSESN",
    "India VIX": "^INDIAVIX",
    "USDINR": "USDINR=X"
}

BONDS_COMMODITIES = {
    "US 10Y Bond Yield": "^TNX",
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Crude Oil": "CL=F",
    "Natural Gas": "NG=F",
    "Copper": "HG=F",
    "Aluminium": "ALI=F",
    "Uranium (ETF)": "URA",
    "Wheat": "ZW=F",
    "Corn": "ZC=F"
}

# =================================================
# SECTOR SETUP (FIXED & REALISTIC)
# =================================================
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

# ✅ FIX: Financial Services via BankNifty proxy
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
market_data = fetch_batch_data(
    {**GLOBAL, **INDIA, **BONDS_COMMODITIES, **SECTOR_SYMBOLS}
)

# =================================================
# 🌍 GLOBAL MARKETS
# =================================================
st.markdown("---")
st.subheader("🌍 Global Markets")

rows=[]
for k,sym in GLOBAL.items():
    v=extract_price(market_data,sym)
    if v: rows.append([k,v[0],v[1],v[2]])

df=pd.DataFrame(rows,columns=["Index","Prev","Current","%Chg"])
st.dataframe(df.style.applymap(dir_color,subset=["%Chg"]),
             use_container_width=False, hide_index=True)

# =================================================
# 🇮🇳 INDIA MARKETS
# =================================================
st.markdown("---")
st.subheader("🇮🇳 India Markets")

rows=[]
for k,sym in INDIA.items():
    v=extract_price(market_data,sym)
    if v: rows.append([k,v[0],v[1],v[2]])

df=pd.DataFrame(rows,columns=["Market","Prev","Current","%Chg"])
st.dataframe(df.style.applymap(dir_color,subset=["%Chg"]),
             use_container_width=False, hide_index=True)

# =================================================
# 🏭 SECTOR PERFORMANCE (WITH OTHER SECTORS)
# =================================================
st.markdown("---")
st.subheader("🏭 Sector Performance (NIFTY 50 Context)")

rows=[]
sector_data = fetch_batch_data(SECTOR_SYMBOLS)

for sector,sym in SECTOR_SYMBOLS.items():
    v=extract_price(sector_data,sym)
    if not v: continue
    wt=SECTOR_BASE_WEIGHTS[sector]
    impact=impact_label(wt,v[2])
    rows.append([sector,f"{wt:.1f} %",f"{v[2]:.2f} %",impact])

sector_df=pd.DataFrame(
    rows,
    columns=["Sector","Approx Weight in NIFTY","Sector % Change","Impact"]
)

# ➕ Add Other sectors as residual
other_weight = round(100 - sum(SECTOR_BASE_WEIGHTS.values()), 1)
sector_df.loc[len(sector_df)] = [
    "Other Sectors (Metals, Utilities, Durables)",
    f"{other_weight} %",
    "—",
    "LOW"
]

st.dataframe(
    sector_df.style.applymap(impact_color,subset=["Impact"]),
    use_container_width=False,
    hide_index=True
)

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
st.dataframe(df.style.applymap(dir_color,subset=["%Chg"]),
             use_container_width=False, hide_index=True)

# =================================================
# 📰 MARKET NEWS (LAST 48 HOURS + AI SUMMARY)
# =================================================
st.markdown("---")
st.subheader("📰 Market News (Last 48 Hours)")

NEWS_FEEDS={
    "India":"https://news.google.com/rss/search?q=india+stock+market+nifty",
    "Global":"https://news.google.com/rss/search?q=global+financial+markets"
}

news=[]
now_ist=datetime.now(ist)

for cat,url in NEWS_FEEDS.items():
    feed=feedparser.parse(url)
    for e in feed.entries:
        try:
            pub_utc=datetime(*e.published_parsed[:6],tzinfo=pytz.utc)
            pub_ist=pub_utc.astimezone(ist)
        except:
            continue

        if (now_ist-pub_ist).total_seconds()>48*3600:
            continue

        t=e.title.lower()
        if any(k in t for k in HIGH_IMPACT_KEYWORDS):
            impact="HIGH"
        elif any(k in t for k in LOW_IMPACT_KEYWORDS):
            impact="LOW"
        else:
            impact="NORMAL"

        news.append([
            cat,
            impact,
            e.title,
            ai_takeaway(e.title),
            pub_ist.strftime("%d-%b-%Y %I:%M %p IST"),
            e.link
        ])

news_df=pd.DataFrame(
    news,
    columns=["Category","Impact","Headline","AI Takeaway","Published","Link"]
).sort_values("Published",ascending=False)

st.dataframe(
    news_df.style.applymap(impact_color,subset=["Impact"]),
    use_container_width=True,
    hide_index=True,
    column_config={"Link":st.column_config.LinkColumn("Open")}
)

st.caption("📌 Educational dashboard only. Not investment advice.")
