import streamlit as st
import yfinance as yf
import pandas as pd
import feedparser
from datetime import datetime
import pytz
import time
import random

# -------------------------------------------------
# STREAMLIT CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Capital Market Pulse",
    layout="wide"
)

st.title("📊 Capital Market Pulse")
st.caption("Global markets • India bias • Intraday readiness")

# IST timezone
ist = pytz.timezone("Asia/Kolkata")
st.markdown(
    f"🕒 **Last updated:** {datetime.now(ist).strftime('%d-%b-%Y %I:%M %p IST')}"
)

# -------------------------------------------------
# MARKET DATA (RATE-LIMIT SAFE)
# -------------------------------------------------
@st.cache_data(ttl=600)  # cache for 10 minutes
def fetch_market_data(symbol):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="2d")

    if len(hist) < 2:
        return None

    prev = hist["Close"].iloc[-2]
    curr = hist["Close"].iloc[-1]
    pct = ((curr / prev) - 1) * 100

    return round(curr, 2), round(prev, 2), round(pct, 2)


symbols = {
    "NIFTY 50": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
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

market_rows = []

for name, symbol in symbols.items():
    try:
        data = fetch_market_data(symbol)
        if data:
            market_rows.append([name, data[0], data[1], data[2]])
        time.sleep(random.uniform(0.3, 0.8))
    except Exception:
        continue

st.subheader("🌍 Global & India Market Snapshot")

if market_rows:
    market_df = pd.DataFrame(
        market_rows,
        columns=["Market", "CMP", "Previous Close", "% Change"]
    )

    def bg(val):
        if val > 0:
            return "background-color: #e6f4ea; font-weight: bold"
        elif val < 0:
            return "background-color: #fdecea; font-weight: bold"
        return ""

    st.dataframe(
        market_df.style.map(bg, subset=["% Change"]),
        use_container_width=True,
        hide_index=True
    )
else:
    st.warning("⚠️ Market data temporarily unavailable (Yahoo rate limit).")

# -------------------------------------------------
# MARKET MOVING NEWS (HIGH IMPACT + BREAKING)
# -------------------------------------------------
st.markdown("---")
st.subheader("📰 Market Moving News")

# HIGH IMPACT keywords
HIGH_IMPACT_KEYWORDS = [
    "rbi", "fed", "interest rate", "rate hike", "rate cut",
    "inflation", "cpi", "recession", "crash", "selloff",
    "war", "geopolitical", "banking", "default", "liquidity"
]

news_feeds = {
    "Stock Market": "https://news.google.com/rss/search?q=stock+market",
    "India Market": "https://news.google.com/rss/search?q=india+stock+market+nifty",
    "Global Markets": "https://news.google.com/rss/search?q=global+markets+stocks",
    "Central Banks": "https://news.google.com/rss/search?q=RBI+Federal+Reserve+interest+rates",
    "Commodities": "https://news.google.com/rss/search?q=crude+oil+gold+markets"
}

news_rows = []

for category, url in news_feeds.items():
    feed = feedparser.parse(url)

    for entry in feed.entries[:8]:
        try:
            published_dt = datetime(
                *entry.published_parsed[:6],
                tzinfo=pytz.utc
            ).astimezone(ist)
        except:
            continue

        headline_lower = entry.title.lower()
        impact = "HIGH" if any(k in headline_lower for k in HIGH_IMPACT_KEYWORDS) else "NORMAL"

        news_rows.append({
            "Category": category,
            "Headline": entry.title,
            "Impact": impact,
            "Published_dt": published_dt,
            "Link": entry.link
        })

news_df = pd.DataFrame(news_rows)

if not news_df.empty:
    # Sort by latest
    news_df = news_df.sort_values("Published_dt", ascending=False)

    # -----------------------------
    # 🚨 BREAKING NEWS (PINNED)
    # -----------------------------
    breaking_df = news_df[news_df["Impact"] == "HIGH"].head(3)

    if not breaking_df.empty:
        st.markdown("### 🚨 Breaking / High Impact News")
        for _, row in breaking_df.iterrows():
            st.error(
                f"**{row['Headline']}**\n\n"
                f"🕒 {row['Published_dt'].strftime('%d-%b-%Y %I:%M %p IST')}\n\n"
                f"[Read more]({row['Link']})"
            )

    st.markdown("---")

    # -----------------------------
    # FULL NEWS TABLE
    # -----------------------------
    news_df.insert(0, "S.No", range(1, len(news_df) + 1))
    news_df["Published (IST)"] = news_df["Published_dt"].dt.strftime(
        "%d-%b-%Y %I:%M %p IST"
    )

    st.dataframe(
        news_df[["S.No", "Category", "Impact", "Headline", "Published (IST)", "Link"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Link": st.column_config.LinkColumn("Link", display_text="Open"),
            "Impact": st.column_config.TextColumn("Impact")
        }
    )
else:
    st.info("No market news available currently.")

# -------------------------------------------------
# FOOTER
# -------------------------------------------------
st.markdown("---")
st.caption(
    "📌 Educational dashboard only. Market data and news may be delayed. "
    "Not investment advice."
)
