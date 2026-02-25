import subprocess
import sys

# Function to install packages if not present
def install_package(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Install required packages
install_package("streamlit")
install_package("yfinance")
install_package("pandas")
install_package("matplotlib")
install_package("feedparser")  # For Google News RSS

import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import feedparser

st.title("Stock Analyzer - Mini Aladdin")

ticker_input = st.text_input("Enter stock ticker (e.g., AAPL):", "").upper()

if ticker_input:
    try:
        # Fetch data from Yahoo Finance
        ticker = yf.Ticker(ticker_input)
        info = ticker.info
        
        st.subheader("Company Details (from Yahoo Finance)")
        st.write(f"**Company Name:** {info.get('longName', 'N/A')}")
        st.write(f"**Market Cap:** ${info.get('marketCap', 0):,.2f}")
        st.write(f"**Industry:** {info.get('industry', 'N/A')}")
        st.write(f"**Homepage:** {info.get('website', 'N/A')}")

        # Fetch previous close data
        history = ticker.history(period="2d")
        if len(history) >= 2:
            prev_close = history.iloc[-2]
            st.subheader("Last Close (from Yahoo Finance)")
            st.write(f"**Price:** ${prev_close['Close']:.2f}")
            st.write(f"**Volume:** {int(prev_close['Volume']):,}")
        else:
            st.warning("Insufficient data for previous close.")

        # Fetch 1-year historical daily data
        one_year_history = ticker.history(period="1y")
        df = one_year_history[['Close']].copy()
        df.index = pd.to_datetime(df.index).tz_localize(None)  # Remove timezone

        # Basic analysis
        returns = df['Close'].pct_change().dropna()
        mean_return = returns.mean() * 252  # Annualized mean return
        volatility = returns.std() * (252 ** 0.5)  # Annualized volatility
        sharpe_ratio = mean_return / volatility if volatility != 0 else 0  # Simple Sharpe (risk-free rate = 0)

        st.subheader("1-Year Analysis (from Yahoo Finance)")
        st.write(f"**Annualized Return:** {mean_return:.2%}")
        st.write(f"**Annualized Volatility:** {volatility:.2%}")
        st.write(f"**Sharpe Ratio:** {sharpe_ratio:.2f}")

        # Plot closing prices
        st.subheader("1-Year Price History (from Yahoo Finance)")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df.index, df['Close'])
        ax.set_title(f"{ticker_input} 1-Year Price History")
        ax.set_xlabel("Date")
        ax.set_ylabel("Close Price ($)")
        ax.grid(True)
        st.pyplot(fig)

        # Fetch news from Google News
        st.subheader("Recent News (from Google News)")
        news_url = f"https://news.google.com/rss/search?q={ticker_input}+stock&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(news_url)
        if feed.entries:
            for entry in feed.entries[:5]:  # Top 5 news
                st.write(f"- **{entry.title}** ([Link]({entry.link}))")
                st.write(f"  Published: {entry.published}")
        else:
            st.write("No recent news found.")

    except Exception as e:
        st.error(f"Error fetching data for {ticker_input}: {str(e)}")
