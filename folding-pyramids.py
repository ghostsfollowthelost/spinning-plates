import polygon
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Initialize Polygon client (API key is pre-configured in the environment)
client = polygon.RESTClient()

# Prompt user for ticker input
ticker = input("Enter stock ticker (e.g., AAPL): ").upper()

# Fetch ticker details
details = client.get_ticker_details(ticker)
print(f"Company Name: {details.name}")
print(f"Market Cap: ${details.market_cap:,.2f}")
print(f"Industry: {details sic_description}")
print(f"Homepage: {details.homepage_url}")

# Fetch previous close data
prev_close = client.get_previous_close_agg(ticker)[0]
print(f"Last Close Price: ${prev_close.close:.2f}")
print(f"Volume: {prev_close.volume:,}")

# Fetch 1-year historical daily data
to_date = datetime.now().date()
from_date = to_date - timedelta(days=365)
aggs = client.get_aggs(ticker, 1, "day", from_date, to_date)

# Convert to DataFrame
df = pd.DataFrame(aggs)
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('timestamp', inplace=True)

# Basic analysis
returns = df['close'].pct_change().dropna()
mean_return = returns.mean() * 252  # Annualized mean return
volatility = returns.std() * (252 ** 0.5)  # Annualized volatility
sharpe_ratio = mean_return / volatility if volatility != 0 else 0  # Simple Sharpe (risk-free rate = 0)

print(f"\n1-Year Analysis:")
print(f"Annualized Return: {mean_return:.2%}")
print(f"Annualized Volatility: {volatility:.2%}")
print(f"Sharpe Ratio: {sharpe_ratio:.2f}")

# Plot closing prices
plt.figure(figsize=(10, 5))
df['close'].plot()
plt.title(f"{ticker} 1-Year Price History")
plt.xlabel("Date")
plt.ylabel("Close Price ($)")
plt.grid(True)
plt.show()
