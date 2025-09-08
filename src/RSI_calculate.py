import pandas as pd
import yfinance as yf
import numpy as np


def rsi_adjusted(data, end="2025-09-05"):

    # Extract tickers
    tickers = data.columns.tolist()
    # Download prices
    prices = yf.download(tickers, end=end, period="2mo", interval=f"1h", auto_adjust=False)['Adj Close']
    prices = prices.ffill()

    # RSI for each asset
    rsi_to_assets = []
    for asset in tickers:

        # Parameters to model
        window_size = data.loc["window_size", asset]
        hour_interval = data.loc["hour_interval", asset]

        # Calculate gain & loss
        delta = prices[asset].tail(window_size*24).diff(periods=hour_interval)
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)

        # avgs
        avg_gain = gain.mean()
        avg_loss = loss.mean()

        # calculate rsi
        rs = avg_gain / (avg_loss if avg_loss != 0 else 1e-14)
        rsi = 100 - (100 / (1 + rs))

        rsi_to_assets.append(rsi)

    rsi_to_assets = pd.Series(rsi_to_assets, index=tickers)

    return rsi_to_assets