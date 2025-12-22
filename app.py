import os
import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
from datetime import datetime
import pytz

# -------------------------------------------------
# YFINANCE HARDENING (VERY IMPORTANT)
# -------------------------------------------------
os.environ["YFINANCE_NO_TZ_CACHE"] = "1"

# -------------------------------------------------
# STREAMLIT CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Capital Market Pulse", layout="wide")

st.title("📊 Capital Market Pulse")
st.caption("Global markets • India bias • Intraday readiness")

# IST Time
ist = pytz.timezone("Asia/Kolkata")
st.markdown(f"🕒 **Last updated:** {datetime.now(ist).strftime('%d-%b-%Y %I:%M %p IST')}")

# -------------------------------------------------
# COMMON FUNCTIONS
# -------------------------------------------------
@st.cache_data(ttl=900)
def fetch_batch_data(symbol_dict):
    data = yf.download(
        tickers=list(symbol_dict.values()),
        period="2d",
        group_by="ticker",
        threads=False,
        auto_adjust=True,
        progress=False
    )
    return data


def extract_price(data, symbol):
    try:
        df = data[symbol]
        if len(df) < 2:
            return None
        prev = df["Close"].iloc[-2]
        curr = df["Close"].iloc[-1]
        pct = ((curr / prev) - 1) * 100
        return round(curr, 2), round(prev, 2), round(pct, 2)
    except:
        return None


def format_change(val):
    if val > 0:
        return f"▲ {val:.2f}%"
    elif val < 0:
        return f"▼ {val:.2f}%"
    return f"{val:.2f}%"


def bg_change(val):
    if "▲" in val:
        return "background-color:#e6f4ea;color:#137333;font-weight:bold"
    elif "▼" in val:
        return "background-color:#fdecea;color:#a50e0e;font-weight:bold"
    return ""

# -------------------------------------------------
# SYMBOL DEFINITIONS
# -------------------------------------------------
market_symbols = {
    "NIFTY 50": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "SENSEX": "^BSESN",
    "India VIX": "^INDIAVIX",
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "Dow Jones": "^DJI",
    "Nikkei 225": "^N225",
    "Hang Seng": "^HSI",
    "DAX": "^GDAXI",
    "FTSE 100": "^FTSE",
    "USDINR": "USDINR=X",
    "Gold": "GC=F",
    "Crude Oil": "CL=F"
}

nifty_sectors = {
    "NIFTY IT": "^CNXIT",
    "NIFTY BANK": "^NSEBANK",
    "NIFTY FMCG": "^CNXFMCG",
    "NIFTY PHARMA": "^CNXPHARMA",
    "NIFTY METAL": "^CNXMETAL",
    "NIFTY AUTO": "^CNXAUTO",
    "NIFTY REALTY": "^CNXREALTY",
    "NIFTY ENERGY": "^CNXENERGY",
    "NIFTY PSU BANK": "^CNXPSUBANK",
    "NIFTY FIN SERVICE": "^CNXFIN"
}

sensex_sectors = {
    "BSE IT": "^BSEIT",
    "BSE BANKEX": "^BSEBANKEX",
    "BSE FMCG": "^BSEFMCG",
    "BSE PHARMA": "^BSEPHARMA",
    "BSE METAL": "^BSEMETAL",
    "BSE AUTO": "^BSEAUTO",
    "BSE REALTY": "^BSEREALTY",
    "BSE POWER": "^BSEPOWER",
    "BSE CAPITAL GOODS": "^BSECAP"
}

# -------------------------------------------------
# GLOBAL & INDIA MARKET SNAPSHOT
# -------------------------------------------------
st.subheader("🌍 Global & India Market Snapshot")

market_data = fetch_batch_data(market_symbols)
market_rows = []

for name, symbol in market_symbols.items():
    values = extract_price(market_data, symbol)
    if values:
        market_rows.append([name, values[0], values[1], values[2]])

if market_rows:
    market_df = pd.DataFrame(
        market_rows, columns=["Market", "CMP", "Previous Close", "% Change"]
    )
    market_df["% Change"] = market_df["% Change"].apply(format_change)

    st.dataframe(
        market_df.style.map(bg_change, subset=["% Change"]),
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("Market data unavailable")

# -------------------------------------------------
# NIFTY SECTOR PERFORMANCE
# -------------------------------------------------
st.markdown("---")
st.subheader("🏭 NIFTY Sector Performance")

nifty_data = fetch_batch_data(nifty_sectors)
nifty_rows = []

for name, symbol in nifty_sectors.items():
    values = extract_price(nifty_data, symbol)
    if values:
        nifty_rows.append([name, values[0], values[1], values[2]])

if nifty_rows:
    nifty_df = pd.DataFrame(
        nifty_rows, columns=["Sector", "CMP", "Previous Close", "% Change"]
    )
    nifty_df["% Change"] = nifty_df["% Change"].apply(format_change)

    st.dataframe(
        nifty_df.style.map(bg_change, subset=["% Change"]),
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("NIFTY sector data unavailable")

# -------------------------------------------------
# SENSEX SECTOR PERFORMANCE
# -------------------------------------------------
st.markdown("---")
st.subheader("🏭 SENSEX Sector Performance")

sensex_data = fetch_batch_data(sensex_sectors)
sensex_rows = []

for name, symbol in sensex_sectors.items():
    values = extract_price(sensex_data, symbol)
    if values:
        sensex_rows.append([name, values[0], values[1], values[2]])

if sensex_rows:
    sensex_df = pd.DataFrame(
        sensex_rows, columns=["Sector", "CMP", "Previous Close", "% Change"]
    )
    sensex_df["% Change"] = sensex_df["% Change"].apply(format_change)

    st.dataframe(
        sensex_df.style.map(bg_change, subset=["% Change"]),
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("SENSEX sector data unavailable")

# -------------------------------------------------
# MARKET MOVING NEWS
# -------------------------------------------------
st.markdown("---")
st.subheader("📰 Market Moving News")

HIGH_IMPACT_KEYWORDS = [
    "rbi", "fed", "interest rate", "inflation", "cpi",
    "recession", "crash", "selloff", "war", "geopolitical"
]

news_feeds = {
    "India Market": "https://news.google.com/rss/search?q=india+stock+market+nifty",
    "Global Markets": "https://news.google.com/rss/search?q=global+stock+markets"
}

news_rows = []

for category, url in news_feeds.items():
    feed = feedparser.parse(url)
    for entry in feed.entries[:8]:
        try:
            published_dt = datetime(
                *entry.published_parsed[:6], tzinfo=pytz.utc
            ).astimezone(ist)
        except:
            continue

        impact = (
            "HIGH"
            if any(k in entry.title.lower() for k in HIGH_IMPACT_KEYWORDS)
            else "NORMAL"
        )

        news_rows.append({
            "Category": category,
            "Impact": impact,
            "Headline": entry.title,
            "Published": published_dt.strftime("%d-%b-%Y %I:%M %p IST"),
            "Link": entry.link
        })

news_df = pd.DataFrame(news_rows)

if not news_df.empty:
    st.dataframe(
        news_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Link": st.column_config.LinkColumn("Link", display_text="Open"),
            "Impact": st.column_config.TextColumn("Impact", width="small")
        }
    )
else:
    st.info("No news available")

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("---")
st.caption("📌 Educational dashboard only. Not investment advice.")
