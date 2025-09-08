import pandas  as pd
import yfinance as yf
from datetime import datetime, timedelta
from src.windows_backtests import RSIBacktest
from src.RSI_calculate import rsi_adjusted


def expecteds_returns(info, end=None, fair_days_window=120):

    # Read tickers and notes
    tickers = info.columns.tolist()
    notes = pd.Series(info.iloc[0,:], index=tickers)

    # Modify dates
    if end is None:
        end = datetime.today()
    else:
        end = datetime.strptime(end, "%Y-%m-%d")
    start = end - timedelta(days=fair_days_window)

    # Download datas
    data = yf.download(tickers, start=start, end=end, auto_adjust=False)['Adj Close']
    tickers = data.columns.tolist()

    # Backtest model to RSI
    rsi_class = RSIBacktest(tickers)
    models = rsi_class.window_test()

    # Calculate RSI
    rsi_values = rsi_adjusted(models)

    # Returns dictionary
    series_returns = pd.Series()

    for ticker in tickers:

        # Parameters
        mean = data[ticker].mean()
        std = data[ticker].std()
        last_price = data[ticker].iloc[-1]

        # short or long
        if notes.loc[ticker] > 0:
            # Stats
            price_max = 2*std + mean
            stat_return = (price_max/last_price) - 1
            rsi_ticker = rsi_values.loc[ticker]

            # Coeficient
            coef = 2-(rsi_ticker/50)

            # Formula
            m_tese = coef * stat_return

        else:
            # Stats
            price_min = mean - (2*std)
            stat_return = (price_min / last_price) - 1
            rsi_ticker = rsi_values.loc[ticker]

            # Coeficient
            coef = rsi_ticker / 50

            # Formula
            m_tese = coef * stat_return

        # Add to series
        expeted_return = abs(notes.loc[ticker]) * m_tese
        series_returns[ticker] = expeted_return

    return series_returns