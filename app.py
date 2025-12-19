import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz

st.set_page_config(layout="wide")
st.title("📊 NIFTY Pre-Market Radar")

# IST timestamp
ist = pytz.timezone("Asia/Kolkata")
st.caption(f"Last updated: {datetime.now(ist).strftime('%d-%b-%Y %I:%M %p IST')}")

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
    "Crude": "CL=F"
}

rows = []
for name, symbol in symbols.items():
    hist = yf.Ticker(symbol).history(period="2d")
    if len(hist) >= 2:
        prev = hist["Close"].iloc[-2]
        curr = hist["Close"].iloc[-1]
        chg = ((curr / prev) - 1) * 100
        rows.append([name, round(curr,2), round(prev,2), round(chg,2)])

df = pd.DataFrame(rows, columns=["Market", "CMP", "Prev Close", "% Change"])

def bg_color(val):
    if val > 0:
        return "background-color: #e6f4ea; font-weight: bold"
    elif val < 0:
        return "background-color: #fdecea; font-weight: bold"
    else:
        return "background-color: #f2f2f2"

st.dataframe(
    df.style.map(bg_color, subset=["% Change"]),
    use_container_width=True
)


# ==============================
# 📰 MARKET MOVING NEWS SECTION
# ==============================
import feedparser

st.markdown("---")
st.subheader("📰 Market Moving News")

ist = pytz.timezone("Asia/Kolkata")

news_feeds = {
    "Stock Market": "https://news.google.com/rss/search?q=stock+market",
    "India Market": "https://news.google.com/rss/search?q=india+stock+market+nifty",
    "Global Markets": "https://news.google.com/rss/search?q=global+markets+stocks",
    "Central Banks": "https://news.google.com/rss/search?q=RBI+Federal+Reserve+interest+rates",
    "Commodities": "https://news.google.com/rss/search?q=crude+oil+gold+markets"
}

rows = []

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

        rows.append([
            category,
            entry.title,
            published_dt,
            entry.link
        ])

df_news = pd.DataFrame(
    rows,
    columns=["Category", "Headline", "Published_dt", "Link"]
)

if not df_news.empty:
    df_news = df_news.sort_values("Published_dt", ascending=False)
    df_news.insert(0, "S.No", range(1, len(df_news) + 1))
    df_news["Published (IST)"] = df_news["Published_dt"].dt.strftime("%d-%b-%Y %I:%M %p IST")
    df_news["Link"] = df_news["Link"].apply(lambda x: f"[Open]({x})")

    st.dataframe(
        df_news[["S.No", "Category", "Headline", "Published (IST)", "Link"]],
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No market news available currently.")
