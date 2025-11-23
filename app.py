import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime, timedelta

from indicators import calculate_sma, calculate_ema, calculate_rsi

# --------------------- PAGE CONFIG ---------------------
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    layout="wide",
    page_icon="📈"
)

st.markdown("""
    <h1 style='text-align: center; color: #2E86C1;'>
        📈 Stock Analysis Dashboard
    </h1>
    <p style='text-align: center; font-size: 18px;'>
       Analyze stock trends with SMA, EMA, RSI, and interactive charts.
    </p>
""", unsafe_allow_html=True)

# --------------------- SIDEBAR INPUTS ---------------------
st.sidebar.header("🔧 Settings")

ticker = st.sidebar.text_input("Stock Ticker (e.g. AAPL, MSFT, TSLA)", value="AAPL")

# Date range
default_start = datetime.today() - timedelta(days=365)
default_end = datetime.today()

start_date = st.sidebar.date_input("Start Date", value=default_start)
end_date = st.sidebar.date_input("End Date", value=default_end)

# Indicator settings
st.sidebar.subheader("📊 Indicator Settings")
sma_window = st.sidebar.number_input("SMA Window", min_value=5, max_value=200, value=20)
ema_window = st.sidebar.number_input("EMA Window", min_value=5, max_value=200, value=20)
rsi_window = st.sidebar.number_input("RSI Window", min_value=5, max_value=50, value=14)

show_sma = st.sidebar.checkbox("Show SMA", value=True)
show_ema = st.sidebar.checkbox("Show EMA", value=True)
show_rsi = st.sidebar.checkbox("Show RSI", value=True)

# Button
load_data = st.sidebar.button("Load & Analyze")

# --------------------- MAIN LOGIC ---------------------
if load_data:
    if not ticker:
        st.error("Please enter a stock ticker.")
    else:
        with st.spinner("Fetching data from yfinance..."):
            data = yf.download(
                ticker,
                start=start_date,
                end=end_date
            )

        if data.empty:
            st.error("No data found. Check the ticker symbol or date range.")
        else:
            data.dropna(inplace=True)

            # Calculate indicators
            data["SMA"] = calculate_sma(data, sma_window)
            data["EMA"] = calculate_ema(data, ema_window)
            data["RSI"] = calculate_rsi(data, rsi_window)

            # --------------------- TABS ---------------------
            tab1, tab2, tab3 = st.tabs(["📈 Price Chart", "📊 RSI & Indicators", "📄 Data & Export"])

            # ---------- TAB 1: Candlestick + Moving Averages ----------
            with tab1:
                st.subheader(f"Price Chart for {ticker.upper()}")

                fig = go.Figure()

                # Candlestick
                fig.add_trace(go.Candlestick(
                    x=data.index,
                    open=data["Open"],
                    high=data["High"],
                    low=data["Low"],
                    close=data["Close"],
                    name="Candlestick"
                ))

                # SMA
                if show_sma:
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=data["SMA"],
                        mode="lines",
                        name=f"SMA {sma_window}"
                    ))

                # EMA
                if show_ema:
                    fig.add_trace(go.Scatter(
                        x=data.index,
                        y=data["EMA"],
                        mode="lines",
                        name=f"EMA {ema_window}"
                    ))

                fig.update_layout(
                    xaxis_title="Date",
                    yaxis_title="Price",
                    xaxis_rangeslider_visible=False,
                    template="plotly_white",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )

                st.plotly_chart(fig, use_container_width=True)

            # ---------- TAB 2: RSI + Close Price ----------
            with tab2:
                st.subheader(f"RSI & Close Price for {ticker.upper()}")

                # RSI chart
                fig_rsi = go.Figure()
                if show_rsi:
                    fig_rsi.add_trace(go.Scatter(
                        x=data.index,
                        y=data["RSI"],
                        mode="lines",
                        name=f"RSI {rsi_window}"
                    ))

                    # Add overbought/oversold lines
                    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
                    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")

                fig_rsi.update_layout(
                    title="RSI",
                    xaxis_title="Date",
                    yaxis_title="RSI",
                    template="plotly_white"
                )

                st.plotly_chart(fig_rsi, use_container_width=True)

                # Close price line chart
                fig_close = go.Figure()
                fig_close.add_trace(go.Scatter(
                    x=data.index,
                    y=data["Close"],
                    mode="lines",
                    name="Close Price"
                ))
                fig_close.update_layout(
                    title="Close Price",
                    xaxis_title="Date",
                    yaxis_title="Price",
                    template="plotly_white"
                )

                st.plotly_chart(fig_close, use_container_width=True)

            # ---------- TAB 3: Data, Summary, CSV Export ----------
            with tab3:
                st.subheader("📄 Data Table")

                st.dataframe(data[["Open", "High", "Low", "Close", "Volume", "SMA", "EMA", "RSI"]])

                st.subheader("📊 Performance Summary")

                # Basic summary stats
                returns = data["Close"].pct_change().dropna()
                total_return = float((data["Close"].iloc[-1] / data["Close"].iloc[0] - 1) * 100)
                avg_daily_return = float(returns.mean() * 100)
                volatility = float(returns.std() * 100)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Return (%)", f"{total_return:.2f}")
                col2.metric("Avg Daily Return (%)", f"{avg_daily_return:.2f}")
                col3.metric("Volatility (%)", f"{volatility:.2f}")

                # CSV export
                st.subheader("💾 Export Data")
                csv_data = data.to_csv().encode("utf-8")
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"{ticker}_data.csv",
                    mime="text/csv"
                )

else:
    st.info("👈 Enter a stock ticker and click **Load & Analyze** to begin.")
