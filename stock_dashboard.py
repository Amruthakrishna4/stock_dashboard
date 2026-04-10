
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Live Stock Dashboard",
    page_icon="📈",
    layout="wide"
)

# ---------------- SIDEBAR ----------------
st.sidebar.title("⚙ Dashboard Settings")

default_stocks = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "AMZN"]

symbols = st.sidebar.text_input(
    "Enter Stock Symbols (comma separated)",
    ", ".join(default_stocks)
)
period = st.sidebar.selectbox(
    "Select Time Period",
    ["1d", "5d", "1mo", "3mo", "6mo", "1y"],
    index=2
)

refresh_interval = st.sidebar.slider(
    "Refresh Interval (Seconds)",
    30,
    300,
    60
)

background_theme = st.sidebar.selectbox(
    "Dashboard Theme",
    ["Dark Blue", "Black", "Purple", "Green"]
)

chart_theme = st.sidebar.selectbox(
    "Chart Theme",
    ["plotly", "plotly_dark", "ggplot2", "presentation", "xgridoff"],
    index=1
)

# ---------------- BACKGROUND COLORS ----------------
if background_theme == "Black":
    page_bg = "linear-gradient(to right, #000000, #1f1f1f)"
elif background_theme == "Purple":
    page_bg = "linear-gradient(to right, #312e81, #6d28d9)"
elif background_theme == "Green":
    page_bg = "linear-gradient(to right, #064e3b, #065f46)"
else:
    page_bg = "linear-gradient(to right, #0f172a, #1e293b)"

# ---------------- CUSTOM CSS ----------------
st.markdown(
    f"""
    <style>
    .stApp {{
        background: {page_bg};
        color: white;
    }}

    section[data-testid="stSidebar"] {{
        background-color: #111827;
        padding-top: 20px;
    }}

    section[data-testid="stSidebar"] * {{
        color: white !important;
    }}

    .stTextInput input {{
        background-color: #f8fafc !important;
        color: #111827 !important;
        border-radius: 10px !important;
        border: 1px solid #cbd5e1 !important;
    }}

    .stTextInput input::placeholder {{
        color: #64748b !important;
    }}

    .stSelectbox div[data-baseweb="select"] > div {{
        background-color: #f8fafc !important;
        color: #111827 !important;
        border-radius: 10px !important;
        border: 1px solid #cbd5e1 !important;
    }}

    .stSelectbox span {{
        color: #111827 !important;
    }}

    div[data-baseweb="popover"] ul {{
        background-color: #f8fafc !important;
        color: #111827 !important;
    }}

    div[data-baseweb="popover"] li {{
        background-color: #f8fafc !important;
        color: #111827 !important;
    }}

    div[data-baseweb="popover"] li:hover {{
        background-color: #dbeafe !important;
        color: #111827 !important;
    }}

    .stSlider span {{
        color: white !important;
    }}

    div[data-testid="metric-container"] {{
        background-color: rgba(30,41,59,0.9);
        border: 1px solid #334155;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.4);
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
    }}

    .stTabs [data-baseweb="tab"] {{
        background-color: #1e293b;
        color: white !important;
        border-radius: 10px;
        padding: 10px 20px;
    }}

    h1, h2, h3, h4, h5, h6, p, label {{
        color: white !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- TITLE ----------------
st.title("📈 Live Stock Market Dashboard")
st.markdown("Track live stock performance, trends, RSI, moving averages, and comparisons.")

# ---------------- STOCK LIST ----------------
tickers = [ticker.strip().upper() for ticker in symbols.split(",") if ticker.strip()]

# ---------------- FUNCTIONS ----------------
@st.cache_data(ttl=60)
def fetch_stock_data(ticker, period):
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    info = stock.info
    return df, info


def calculate_metrics(df):
    current_price = df["Close"].iloc[-1]
    previous_close = df["Close"].iloc[-2] if len(df) > 1 else current_price
    change = current_price - previous_close
    percent_change = (change / previous_close) * 100

    return {
        "current": current_price,
        "change": change,
        "percent": percent_change,
        "high": df["High"].max(),
        "low": df["Low"].min(),
        "volume": df["Volume"].iloc[-1],
        "volatility": df["Close"].std()
    }


def calculate_rsi(series, window=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


# ---------------- TABS ----------------
tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "Charts",
    "Comparison",
    "Alerts"
])

# ---------------- LAST UPDATED ----------------
st.caption(f"Last Updated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")

stock_changes = []
comparison_data = []

# ---------------- OVERVIEW TAB ----------------
with tab1:
    cols = st.columns(len(tickers))

    for i, ticker in enumerate(tickers):
        with cols[i]:
            try:
                df, info = fetch_stock_data(ticker, period)

                if df.empty:
                    st.error(f"No data found for {ticker}")
                    continue

                metrics = calculate_metrics(df)

                stock_changes.append({
                    "Ticker": ticker,
                    "Change %": metrics["percent"]
                })

                comparison_data.append({
                    "Ticker": ticker,
                    "Price": metrics["current"]
                })

                st.subheader(ticker)
                st.caption(info.get("longName", "Company Name Not Found"))

                market_cap = info.get("marketCap", None)
                pe_ratio = info.get("trailingPE", "N/A")

                if market_cap:
                    st.write(f"Market Cap: ${market_cap:,}")

                st.write(f"P/E Ratio: {pe_ratio}")

                st.metric(
                    "Current Price",
                    f"${metrics['current']:.2f}",
                    f"{metrics['change']:+.2f} ({metrics['percent']:+.2f}%)"
                )

                col1, col2 = st.columns(2)
                col1.metric("High", f"${metrics['high']:.2f}")
                col2.metric("Low", f"${metrics['low']:.2f}")

                st.metric("Volume", f"{metrics['volume']:,}")
                st.metric("Volatility", f"{metrics['volatility']:.2f}")

            except Exception as e:
                st.error(f"Error loading {ticker}: {e}")

# ---------------- CHARTS TAB ----------------
with tab2:
    for ticker in tickers:
        try:
            df, _ = fetch_stock_data(ticker, period)

            if df.empty:
                continue

            df["MA7"] = df["Close"].rolling(7).mean()
            df["MA30"] = df["Close"].rolling(30).mean()
            df["RSI"] = calculate_rsi(df["Close"])

            st.subheader(f"{ticker} Stock Analysis")

            candlestick = go.Figure()

            candlestick.add_trace(go.Candlestick(
                x=df.index,
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="Candlestick"
            ))

            candlestick.add_trace(go.Scatter(
                x=df.index,
                y=df["MA7"],
                mode="lines",
                name="7 Day MA"
            ))

            candlestick.add_trace(go.Scatter(
                x=df.index,
                y=df["MA30"],
                mode="lines",
                name="30 Day MA"
            ))

            candlestick.update_layout(
                title=f"{ticker} Price Chart",
                template=chart_theme,
                height=500,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white")
            )

            st.plotly_chart(candlestick, use_container_width=True)

            volume_chart = px.bar(
                df,
                x=df.index,
                y="Volume",
                title=f"{ticker} Trading Volume",
                template=chart_theme
            )

            volume_chart.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white")
            )

            st.plotly_chart(volume_chart, use_container_width=True)

            rsi_chart = px.line(
                df,
                x=df.index,
                y="RSI",
                title=f"{ticker} RSI Indicator",
                template=chart_theme
            )

            rsi_chart.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white")
            )

            st.plotly_chart(rsi_chart, use_container_width=True)

        except Exception as e:
            st.error(f"Chart error for {ticker}: {e}")

# ---------------- COMPARISON TAB ----------------
with tab3:
    if stock_changes:
        comparison_df = pd.DataFrame(stock_changes)

        change_chart = px.bar(
            comparison_df,
            x="Ticker",
            y="Change %",
            color="Change %",
            title="Stock Percentage Change Comparison",
            template=chart_theme
        )

        change_chart.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )

        st.plotly_chart(change_chart, use_container_width=True)

    if comparison_data:
        price_df = pd.DataFrame(comparison_data)

        price_chart = px.pie(
            price_df,
            names="Ticker",
            values="Price",
            title="Current Price Distribution"
        )

        st.plotly_chart(price_chart, use_container_width=True)

# ---------------- ALERTS TAB ----------------
with tab4:
    for ticker in tickers:
        try:
            df, _ = fetch_stock_data(ticker, period)

            if df.empty:
                continue

            metrics = calculate_metrics(df)
            latest_rsi = calculate_rsi(df["Close"]).iloc[-1]

            if metrics["percent"] > 5:
                st.success(f"{ticker} is up by {metrics['percent']:.2f}%")
            elif metrics["percent"] < -5:
                st.error(f"{ticker} is down by {metrics['percent']:.2f}%")
            else:
                st.info(f"{ticker} has stable movement")

            if latest_rsi > 70:
                st.warning(f"{ticker} may be overbought (RSI: {latest_rsi:.2f})")
            elif latest_rsi < 30:
                st.warning(f"{ticker} may be oversold (RSI: {latest_rsi:.2f})")

        except Exception as e:
            st.error(f"Alert error for {ticker}: {e}")

# ---------------- AUTO REFRESH ----------------
time.sleep(refresh_interval)
st.rerun()
