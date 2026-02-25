import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import feedparser
import time

# ====================== HYBRID API SETUP ======================
# Finnhub (live price) — optional
FINNHUB_AVAILABLE = False
try:
    import finnhub
    client = finnhub.Client(api_key=st.secrets["FINNHUB_API_KEY"])
    FINNHUB_AVAILABLE = True
except:
    pass

# Caching
@st.cache_data(ttl=60)   # 60-second live quote
def get_live_quote(symbol):
    if FINNHUB_AVAILABLE:
        try:
            q = client.quote(symbol)
            return q.get('c', 0), q.get('pc', 0)   # current, previous close
        except:
            pass
    # Fallback to yfinance
    ticker = yf.Ticker(symbol)
    info = ticker.info
    price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
    prev = info.get('previousClose') or price
    return price, prev

@st.cache_data(ttl=300)  # 5 min for history
def get_history(symbol, period):
    return yf.Ticker(symbol).history(period=period)

# ====================== UI ======================
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
        
        figure { background: #1a1a1a !important; border-radius: 12px; padding: 12px; }
    </style>
""", unsafe_allow_html=True)

st.set_page_config(page_title="Mini Aladdin", layout="wide", page_icon="🧿")
st.title("🧿 Stock Analyzer — Mini BlackRock Aladdin")
st.markdown("**Hybrid APIs • Instant Live • Zero Rate Limits** | Finnhub + Yahoo Finance + Google News")

ticker_input = st.text_input("Enter stock ticker", placeholder="AAPL, TSLA, NVDA", value="AAPL").upper().strip()

if ticker_input:
    live_container = st.empty()
    
    try:
        # Live price (Finnhub if available, else yfinance)
        price, prev = get_live_quote(ticker_input)
        change = price - prev
        pct = (change / prev * 100) if prev else 0
        
        with live_container:
            st.metric("LIVE PRICE", f"${price:,.2f}", f"{change:+.2f} ({pct:+.2f}%)")

        ticker = yf.Ticker(ticker_input)
        info = ticker.info

        col1, col2, col3 = st.columns([3, 2, 2])
        with col1: st.subheader(f"{info.get('longName', ticker_input)} ({ticker_input})")
        with col3: st.metric("Market Cap", f"${info.get('marketCap', 0)/1e9:,.1f}B")

        st.markdown(f"**Industry:** {info.get('industry', 'N/A')} | **Website:** [{info.get('website','N/A')}]({info.get('website','N/A')})")

        tab1, tab2, tab3, tab4 = st.tabs(["📊 Pro Chart", "📈 Key Metrics", "💰 Financials", "📰 Latest News"])

        # Chart — always yfinance (best historical data)
        with tab1:
            period = st.selectbox("Time period", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=3)
            hist = get_history(ticker_input, period)
            
            hist['MA50'] = hist['Close'].rolling(50).mean()
            hist['MA200'] = hist['Close'].rolling(200).mean()

            col_a, col_b, col_c = st.columns([1,1,1])
            with col_a: show_ma50 = st.checkbox("50-day MA", value=True)
            with col_b: show_ma200 = st.checkbox("200-day MA", value=True)
            with col_c: show_volume = st.checkbox("Volume subplot", value=True)

            if show_volume:
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]}, facecolor='#1a1a1a')
            else:
                fig, ax1 = plt.subplots(figsize=(12, 6), facecolor='#1a1a1a')
                ax2 = None

            ax1.plot(hist.index, hist['Close'], label='Close', color='#1E88E5', linewidth=2.5)
            if show_ma50: ax1.plot(hist.index, hist['MA50'], label='50-day MA', color='#ffd700', linewidth=2)
            if show_ma200: ax1.plot(hist.index, hist['MA200'], label='200-day MA', color='#00b4ff', linewidth=2)
            
            ax1.set_title(f"{ticker_input} — {period.upper()} History", color='white', fontsize=16)
            ax1.set_ylabel("Price (USD)", color='#e0e0e0')
            ax1.legend(facecolor='#1a1a1a', labelcolor='white')
            ax1.grid(True, alpha=0.3, color='#4a4a4a')
            ax1.tick_params(colors='#e0e0e0')
            for spine in ax1.spines.values(): spine.set_color('#4a4a4a')
            ax1.set_facecolor('#1a1a1a')

            if show_volume and ax2 is not None:
                colors = ['#00ff9d' if o >= c else '#ff2d55' for o, c in zip(hist['Open'], hist['Close'])]
                ax2.bar(hist.index, hist['Volume'], color=colors, alpha=0.7)
                ax2.set_ylabel("Volume", color='#e0e0e0')
                ax2.tick_params(colors='#e0e0e0')
                for spine in ax2.spines.values(): spine.set_color('#4a4a4a')
                ax2.set_facecolor('#1a1a1a')
                ax2.grid(True, alpha=0.3, color='#4a4a4a')

            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)

        # Other tabs (yfinance data)
        with tab2:
            c1, c2 = st.columns(2)
            with c1: st.write("**52-Week High:**", f"${info.get('fiftyTwoWeekHigh', 'N/A'):,.2f}")
            with c1: st.write("**52-Week Low:**", f"${info.get('fiftyTwoWeekLow', 'N/A'):,.2f}")
            with c2: st.write("**Trailing P/E:**", info.get('trailingPE', 'N/A'))
            with c2: st.write("**Dividend Yield:**", f"{info.get('dividendYield', 0)*100:.2f}%")

        with tab3:
            st.write("**Enterprise Value:**", f"${info.get('enterpriseValue', 0)/1e9:,.1f}B")
            st.write("**Trailing EPS:**", info.get('trailingEps', 'N/A'))

        with tab4:
            st.subheader("📰 Latest News")
            feed = feedparser.parse(f"https://news.google.com/rss/search?q={ticker_input}+stock+OR+earnings&hl=en-US&gl=US&ceid=US:en")
            for entry in feed.entries[:8]:
                st.markdown(f"**{entry.title}**")
                st.caption(f"📅 {entry.get('published', 'N/A')} | [Read →]({entry.link})")
                st.divider()

        # Auto-refresh live price every 5 seconds
        time.sleep(5)
        st.rerun()

    except Exception as e:
        st.error(f"❌ Could not load {ticker_input}. Try Refresh or wait 30s.")
        st.caption(str(e))
