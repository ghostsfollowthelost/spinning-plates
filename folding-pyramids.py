import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import feedparser

st.set_page_config(page_title="Mini Aladdin", layout="wide")
st.title("🧿 Stock Analyzer - Mini BlackRock Aladdin")
st.markdown("**Yahoo Finance + Google News** | Real-time intelligence")

ticker_input = st.text_input("Enter stock ticker", placeholder="AAPL, TSLA, NVDA", value="AAPL").upper().strip()

if ticker_input:
    with st.spinner(f"Fetching data for {ticker_input}..."):
        try:
            ticker = yf.Ticker(ticker_input)
            info = ticker.info

            # Header
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.subheader(f"{info.get('longName', ticker_input)} ({ticker_input})")
                price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
                st.metric("Current Price", f"${price:,.2f}" if price else "N/A")
            with col2:
                st.metric("Market Cap", f"${info.get('marketCap', 0)/1e9:,.1f}B")
            with col3:
                st.metric("Industry", info.get('industry', 'N/A'))

            # Tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Price Chart", "📈 Key Metrics", "💰 Financials", "📰 Latest News"])

            # Tab 1: Interactive Chart
            with tab1:
                period = st.selectbox("Time period", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=3)
                hist = ticker.history(period=period)
                
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.plot(hist.index, hist['Close'], linewidth=2.5, color='#1E88E5')
                ax.set_title(f"{ticker_input} — {period.upper()} Price History")
                ax.set_ylabel("Price (USD)")
                ax.grid(True, alpha=0.3)
                st.pyplot(fig)

            # Tab 2: Key Metrics
            with tab2:
                c1, c2 = st.columns(2)
                with c1:
                    st.write("**Performance**")
                    st.write(f"52-Week High: **${info.get('fiftyTwoWeekHigh', 'N/A'):,.2f}**")
                    st.write(f"52-Week Low: **${info.get('fiftyTwoWeekLow', 'N/A'):,.2f}**")
                    st.write(f"Beta: **{info.get('beta', 'N/A')}**")
                    st.write(f"52-Week Change: **{info.get('52WeekChange', 0)*100:,.1f}%**")
                with c2:
                    st.write("**Valuation**")
                    st.write(f"Trailing P/E: **{info.get('trailingPE', 'N/A')}**")
                    st.write(f"Forward P/E: **{info.get('forwardPE', 'N/A')}**")
                    st.write(f"Dividend Yield: **{info.get('dividendYield', 0)*100:,.2f}%**")
                    st.write(f"PEG Ratio: **{info.get('pegRatio', 'N/A')}**")

            # Tab 3: Financials
            with tab3:
                st.write("**Key Financial Statistics**")
                stats = {
                    "Enterprise Value": f"${info.get('enterpriseValue', 0)/1e9:,.1f}B",
                    "Trailing EPS": info.get('trailingEps', 'N/A'),
                    "Forward EPS": info.get('forwardEps', 'N/A'),
                    "Profit Margin": f"{info.get('profitMargins', 0)*100:,.1f}%",
                    "Return on Equity": f"{info.get('returnOnEquity', 0)*100:,.1f}%",
                    "Debt/Equity": f"{info.get('debtToEquity', 'N/A')}",
                }
                for k, v in stats.items():
                    st.write(f"**{k}**: {v}")

            # Tab 4: Google News
            with tab4:
                st.subheader("📰 Recent News")
                news_url = f"https://news.google.com/rss/search?q={ticker_input}+stock+OR+earnings&hl=en-US&gl=US&ceid=US:en"
                feed = feedparser.parse(news_url)
                
                if feed.entries:
                    for entry in feed.entries[:10]:
                        st.markdown(f"**{entry.title}**")
                        st.caption(f"📅 {entry.get('published', 'N/A')}   |   [Read full article]({entry.link})")
                        st.divider()
                else:
                    st.info("No recent news found.")

        except Exception as e:
            st.error(f"❌ Could not load **{ticker_input}**. Make sure the ticker is correct.")
            st.caption(f"Error: {str(e)}")
