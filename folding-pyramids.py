import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import feedparser

# ── Grok-style dark UI + smooth animations ──
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Josefin+Sans:wght@400;700&display=swap');
        
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.03); } 100% { transform: scale(1); } }
        
        .stApp { background: linear-gradient(to bottom right, #000000, #1a1a1a); color: #ffffff; animation: fadeIn 0.5s cubic-bezier(0.25,0.1,0.25,1); }
        h1, h2, h3, h4 { font-family: 'Josefin Sans', sans-serif; color: #ffffff; animation: fadeIn 0.4s cubic-bezier(0.25,0.1,0.25,1); }
        body, p, div, .stMarkdown { font-family: 'Josefin Sans', sans-serif; color: #e0e0e0; animation: fadeIn 0.5s cubic-bezier(0.25,0.1,0.25,1); }
        
        .stTextInput > div > div > input { background: #2a2a2a; color: #fff; border-radius: 8px; transition: all 0.2s; }
        .stTextInput > div > div > input:focus { border-color: #1E88E5; box-shadow: 0 0 12px rgba(30,136,229,0.6); }
        
        .stButton > button { background: #1E88E5; transition: all 0.2s; }
        .stButton > button:hover { background: #1565C0; transform: scale(1.05); }
        
        .stMetric { background: #2a2a2a; border-radius: 8px; animation: pulse 1.2s infinite; }
        .stMetric:hover { transform: scale(1.05); }
        
        .stTabs [data-baseweb="tab"] { transition: all 0.2s; }
        .stTabs [data-baseweb="tab"]:hover { transform: translateY(-2px); }
        
        .plotly-chart-container { background: #1a1a1a; border-radius: 12px; padding: 8px; }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Mini Aladdin", layout="wide", page_icon="🧿")
st.title("🧿 Stock Analyzer — Mini BlackRock Aladdin")
st.markdown("**Real-time • Interactive • Professional** | Yahoo Finance + Google News")

ticker_input = st.text_input("Enter stock ticker", placeholder="AAPL, TSLA, NVDA", value="AAPL").upper().strip()

if ticker_input:
    with st.spinner(f"Loading live intelligence for {ticker_input}..."):
        try:
            ticker = yf.Ticker(ticker_input)
            info = ticker.info

            # Header
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.subheader(f"{info.get('longName', ticker_input)} ({ticker_input})")
            with col2:
                price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
                st.metric("Current Price", f"${price:,.2f}" if price else "N/A")
            with col3:
                st.metric("Market Cap", f"${info.get('marketCap', 0)/1e9:,.1f}B")

            st.markdown(f"**Industry:** {info.get('industry', 'N/A')} | **Website:** [{info.get('website','N/A')}]({info.get('website','N/A')})")

            tab1, tab2, tab3, tab4 = st.tabs(["📊 Interactive Chart", "📈 Key Metrics", "💰 Financials", "📰 Latest News"])

            # ── TAB 1: PRO INTERACTIVE CHART (Candlestick + Volume + MA toggles) ──
            with tab1:
                period = st.selectbox("Time period", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=3)
                hist = ticker.history(period=period)
                
                # Calculate moving averages
                hist['MA50'] = hist['Close'].rolling(window=50).mean()
                hist['MA200'] = hist['Close'].rolling(window=200).mean()

                # Controls
                col_a, col_b, col_c = st.columns([1,1,1])
                with col_a:
                    show_ma50 = st.checkbox("50-day MA", value=True)
                with col_b:
                    show_ma200 = st.checkbox("200-day MA", value=True)
                with col_c:
                    show_volume = st.checkbox("Volume bars", value=True)

                fig = go.Figure()

                # Candlestick
                fig.add_trace(go.Candlestick(
                    x=hist.index,
                    open=hist['Open'],
                    high=hist['High'],
                    low=hist['Low'],
                    close=hist['Close'],
                    name="Price",
                    increasing_line_color='#00ff9d',
                    decreasing_line_color='#ff2d55'
                ))

                # Moving Averages
                if show_ma50:
                    fig.add_trace(go.Scatter(x=hist.index, y=hist['MA50'], name="50-day MA", line=dict(color='#ffd700', width=2)))
                if show_ma200:
                    fig.add_trace(go.Scatter(x=hist.index, y=hist['MA200'], name="200-day MA", line=dict(color='#00b4ff', width=2)))

                # Volume
                if show_volume:
                    colors = ['#00ff9d' if o >= c else '#ff2d55' for o, c in zip(hist['Open'], hist['Close'])]
                    fig.add_trace(go.Bar(
                        x=hist.index,
                        y=hist['Volume'],
                        name="Volume",
                        marker_color=colors,
                        opacity=0.6,
                        yaxis="y2"
                    ))

                # Layout
                fig.update_layout(
                    template="plotly_dark",
                    plot_bgcolor="#1a1a1a",
                    paper_bgcolor="#1a1a1a",
                    font=dict(color="#e0e0e0"),
                    title=f"{ticker_input} — Interactive {period.upper()} Chart",
                    xaxis=dict(rangeslider=dict(visible=True), type="date"),
                    yaxis=dict(title="Price (USD)"),
                    yaxis2=dict(title="Volume", overlaying="y", side="right", showgrid=False),
                    height=650,
                    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
                    margin=dict(l=40, r=40, t=60, b=40)
                )

                st.plotly_chart(fig, use_container_width=True)

            # Rest of tabs (same as before)
            with tab2:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Performance**")
                    st.write(f"52-Week High: **${info.get('fiftyTwoWeekHigh', 'N/A'):,.2f}**")
                    st.write(f"52-Week Low: **${info.get('fiftyTwoWeekLow', 'N/A'):,.2f}**")
                    st.write(f"Beta: **{info.get('beta', 'N/A')}**")
                with c2:
                    st.markdown("**Valuation**")
                    st.write(f"Trailing P/E: **{info.get('trailingPE', 'N/A')}**")
                    st.write(f"Forward P/E: **{info.get('forwardPE', 'N/A')}**")
                    st.write(f"Dividend Yield: **{info.get('dividendYield', 0)*100:,.2f}%**")

            with tab3:
                st.markdown("**Key Financial Statistics**")
                stats = {k: v for k, v in {
                    "Enterprise Value": f"${info.get('enterpriseValue', 0)/1e9:,.1f}B",
                    "Trailing EPS": info.get('trailingEps', 'N/A'),
                    "Forward EPS": info.get('forwardEps', 'N/A'),
                    "Profit Margin": f"{info.get('profitMargins', 0)*100:,.1f}%",
                    "Return on Equity": f"{info.get('returnOnEquity', 0)*100:,.1f}%",
                }.items()}
                for k, v in stats.items():
                    st.write(f"**{k}**: {v}")

            with tab4:
                st.subheader("📰 Recent News")
                news_url = f"https://news.google.com/rss/search?q={ticker_input}+stock+OR+earnings&hl=en-US&gl=US&ceid=US:en"
                feed = feedparser.parse(news_url)
                if feed.entries:
                    for entry in feed.entries[:10]:
                        st.markdown(f"**{entry.title}**")
                        st.caption(f"📅 {entry.get('published', 'N/A')} | [Read →]({entry.link})")
                        st.divider()
                else:
                    st.info("No recent news found.")

        except Exception as e:
            st.error(f"❌ Could not load **{ticker_input}** — double-check the ticker.")
            st.caption(str(e))
