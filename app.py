import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.graph_objects as go

# 1. THE BOARD OF AGENTS (The Logic)
def run_boardroom(ticker):
    # Fetch Market Data
    data = yf.download(ticker, period="1mo", progress=False)
    if data.empty:
        st.error("Could not find that ticker. Try AAPL or NVDA.")
        return

    st.subheader(f"Boardroom Analysis: {ticker}")
    
    # Simple Logic for 3 Agents
    price_change = (data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1
    volatility = data['Close'].pct_change().std()

    # Agent 1: The Bull (Optimist)
    bull_opinion = price_change + 0.05
    # Agent 2: The Bear (Pessimist)
    bear_opinion = price_change - 0.05
    # Agent 3: The Math (Neutral)
    math_opinion = price_change # Display Opinions in Columns col1, col2, col3 = st.columns(3)col1.metric("Agent Alpha (Bull)", f"{bull_opinion:+.2%}", "Optimistic") col2.metric("Agent Beta (Bear)", f"{bear_opinion:+.2%}", "Cynical")   col3.metric("Agent Gamma (Math)", f"{math_opinion:+.2%}", "Neutral")

    # 1. Ensure the math uses float numbers to avoid TypeErrors
    # 2. Add a fallback to 0.0 if data is missing
    bull_opinion = float(price_change + 0.05) if not np.isnan(price_change) else 0.0
    bear_opinion = float(price_change - 0.05) if not np.isnan(price_change) else 0.0
    math_opinion = float(price_change) if not np.isnan(price_change) else 0.0
    
    # The Chairperson's Final Verdict
    consensus = (bull_opinion + bear_opinion + math_opinion) / 3
    st.divider()
    st.header(f"Final Verdict: {'BUY' if consensus > 0 else 'SELL'}")
    st.write(f"The boardroom has reached a consensus of **{consensus:+.2%}** expected movement.")

    # Simple Visual
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = consensus * 100,
        title = {'text': "Consensus Score"},
        gauge = {'axis': {'range': [-10, 10]}, 'bar': {'color': "darkblue"}}
    ))
    st.plotly_chart(fig, use_container_width=True)

# 2. THE DASHBOARD (The UI)
st.title("🏛️ Sentinel Boardroom")
selected_ticker = st.text_input("Enter Ticker (e.g. BTC-USD, TSLA, AAPL)", "NVDA")

if st.button("Start Debate"):
    run_boardroom(selected_ticker)
