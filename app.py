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

st.set_page_config(
    page_title="Capital Market Pulse — PRO",
    layout="wide"
)

st.title("📊 Capital Market Pulse — PRO")
st.caption("Institution-grade • India-first • Intraday ready")

ist = pytz.timezone("Asia/Kolkata")
st.markdown(
    f"🕒 **Last updated:** {datetime.now(ist).strftime('%d-%b-%Y %I:%M %p IST')}"
)

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


def format_change(val):
    return f"{val:.2f}%"


def bg_change(val):
    if val > 0:
        return "background-color:#e6f4ea;color:#137333;font-weight:bold"
    return "background-color:#fdecea;color:#a50e0e;font-weight:bold"


def heat_color(val):
    v = max(min(val, 5), -5)
    if v > 0:
        g = int(255 - (v / 5) * 140)
        return f"background-color: rgb({g},255,{g}); font-weight:bold"
    r = int(255 - (abs(v) / 5) * 140)
    return f"background-color: rgb(255,{r},{r}); font-weight:bold"

# =================================================
# SYMBOLS
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
# NIFTY 50 (FULL)
# =================================================
NIFTY_50 = {
    "ADANIENT":"ADANIENT.NS","ADANIPORTS":"ADANIPORTS.NS","APOLLOHOSP":"APOLLOHOSP.NS",
    "ASIANPAINT":"ASIANPAINT.NS","AXISBANK":"AXISBANK.NS","BAJAJ-AUTO":"BAJAJ-AUTO.NS",
    "BAJFINANCE":"BAJFINANCE.NS","BAJAJFINSV":"BAJAJFINSV.NS","BHARTIARTL":"BHARTIARTL.NS",
    "BPCL":"BPCL.NS","BRITANNIA":"BRITANNIA.NS","CIPLA":"CIPLA.NS","COALINDIA":"COALINDIA.NS",
    "DIVISLAB":"DIVISLAB.NS","DRREDDY":"DRREDDY.NS","EICHERMOT":"EICHERMOT.NS",
    "GRASIM":"GRASIM.NS","HCLTECH":"HCLTECH.NS","HDFCBANK":"HDFCBANK.NS",
    "HDFCLIFE":"HDFCLIFE.NS","HEROMOTOCO":"HEROMOTOCO.NS","HINDALCO":"HINDALCO.NS",
    "HINDUNILVR":"HINDUNILVR.NS","ICICIBANK":"ICICIBANK.NS","INDUSINDBK":"INDUSINDBK.NS",
    "INFY":"INFY.NS","ITC":"ITC.NS","JSWSTEEL":"JSWSTEEL.NS","KOTAKBANK":"KOTAKBANK.NS",
    "LT":"LT.NS","LTIM":"LTIM.NS","MARUTI":"MARUTI.NS","NESTLEIND":"NESTLEIND.NS",
    "NTPC":"NTPC.NS","ONGC":"ONGC.NS","POWERGRID":"POWERGRID.NS","RELIANCE":"RELIANCE.NS",
    "SBILIFE":"SBILIFE.NS","SBIN":"SBIN.NS","SUNPHARMA":"SUNPHARMA.NS",
    "TATACONSUM":"TATACONSUM.NS","TATAMOTORS":"TATAMOTORS.NS","TATASTEEL":"TATASTEEL.NS",
    "TECHM":"TECHM.NS","TITAN":"TITAN.NS","ULTRACEMCO":"ULTRACEMCO.NS",
    "UPL":"UPL.NS","WIPRO":"WIPRO.NS"
}

# =================================================
# NIFTY NEXT 50 (FULL 50)
# =================================================
NIFTY_NEXT_50 = {
    "ABB":"ABB.NS","ADANIGREEN":"ADANIGREEN.NS","ADANIPOWER":"ADANIPOWER.NS",
    "ALKEM":"ALKEM.NS","AMBUJACEM":"AMBUJACEM.NS","APOLLOTYRE":"APOLLOTYRE.NS",
    "ASHOKLEY":"ASHOKLEY.NS","ASTRAL":"ASTRAL.NS","AUROPHARMA":"AUROPHARMA.NS",
    "BANDHANBNK":"BANDHANBNK.NS","BERGEPAINT":"BERGEPAINT.NS","BIOCON":"BIOCON.NS",
    "BOSCHLTD":"BOSCHLTD.NS","CANBK":"CANBK.NS","CHOLAFIN":"CHOLAFIN.NS",
    "COFORGE":"COFORGE.NS","COLPAL":"COLPAL.NS","CONCOR":"CONCOR.NS",
    "DABUR":"DABUR.NS","DALBHARAT":"DALBHARAT.NS","DLF":"DLF.NS","GAIL":"GAIL.NS",
    "GODREJCP":"GODREJCP.NS","HAVELLS":"HAVELLS.NS","ICICIGI":"ICICIGI.NS",
    "ICICIPRULI":"ICICIPRULI.NS","IGL":"IGL.NS","INDIGO":"INDIGO.NS",
    "JINDALSTEL":"JINDALSTEL.NS","LUPIN":"LUPIN.NS","MUTHOOTFIN":"MUTHOOTFIN.NS",
    "NMDC":"NMDC.NS","PAGEIND":"PAGEIND.NS","PEL":"PEL.NS","PETRONET":"PETRONET.NS",
    "PIDILITIND":"PIDILITIND.NS","POLYCAB":"POLYCAB.NS","PVRINOX":"PVRINOX.NS",
    "SHREECEM":"SHREECEM.NS","SIEMENS":"SIEMENS.NS","SRF":"SRF.NS",
    "TORNTPHARM":"TORNTPHARM.NS","TRENT":"TRENT.NS","TVSMOTOR":"TVSMOTOR.NS",
    "UBL":"UBL.NS","VOLTAS":"VOLTAS.NS","ZEEL":"ZEEL.NS"
}

# =================================================
# FETCH DATA
# =================================================
market_data = fetch_batch_data({**GLOBAL, **INDIA, **SECTORS, **BONDS_COMMODITIES})

# =================================================
# 🔥 HEATMAP (COMPACT)
# =================================================
st.markdown("---")
st.subheader("🔥 NIFTY Heatmap")

index_choice = st.radio("Select Index", ["NIFTY 50", "NIFTY NEXT 50"], horizontal=True)
stocks = NIFTY_50 if index_choice == "NIFTY 50" else NIFTY_NEXT_50

heat_data = fetch_batch_data(stocks)

rows = []
for name, sym in stocks.items():
    v = extract_price(heat_data, sym)
    if v:
        rows.append([name, v[0], v[1], v[2]])

df = pd.DataFrame(rows, columns=["Stock", "Prev", "Current", "%Chg"])

st.dataframe(
    df.style.applymap(heat_color, subset=["%Chg"]),
    use_container_width=False,
    column_config={
        "Stock": st.column_config.TextColumn(width="small"),
        "Prev": st.column_config.NumberColumn(format="%.2f", width="small"),
        "Current": st.column_config.NumberColumn(format="%.2f", width="small"),
        "%Chg": st.column_config.NumberColumn(format="%.2f", width="small")
    },
    hide_index=True
)

st.caption("📌 Educational dashboard only. Not investment advice.")
