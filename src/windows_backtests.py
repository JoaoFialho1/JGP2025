import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta



class MeanBacktest:
    def __init__(self, tickers, end=None, max_window_days=721):

        # Modify dates
        if end is None:
            end = datetime.today()
        else:
            end = datetime.strptime(end, "%Y-%m-%d")
        start = end - timedelta(days=max_window_days*1.5)

        # Download datas
        data = yf.download(tickers, start=start, end=end, auto_adjust=False)['Adj Close']

        # Returns
        returns = data.pct_change().fillna(0)

        # Atributes
        self.__prices = data
        self.__returns = returns
        self.__max_window_days = max_window_days

    def window_test(self, steps_window_size=7, days_to_predict=7, days_to_backtest=365):

        result = pd.DataFrame()

        for columns in self.__returns.columns:

            hits_per_window = []
            index = []

            for window_size in range(steps_window_size, self.__max_window_days+1, steps_window_size):

                # List with window size
                hits_number = []

                for window in range(-1, -days_to_backtest-1, -1):
                    # Window with datas (scroll through negative numbers, part of the last date. ex: window=(-1) => [-8 : -1])
                    window_x = self.__returns[columns].iloc[window - window_size : window]

                    # Calculate precision range
                    dp = window_x.std()
                    mean = window_x.mean()
                    real_return = (1 +self.__returns[columns].iloc[window: window + days_to_predict]).prod() -1

                    # Calculate forecast accuracy
                    if mean-dp <= real_return <= mean+dp:
                        prevision = 1
                    else:
                        prevision = 0
                    hits_number.append(prevision)
                # Create hits series of 1 ticker
                hits = sum(hits_number)
                hits_per_window.append(hits)
                index.append(window_size)


            # Add hits series to final DF
            hits_per_window = pd.Series(hits_per_window, index = index)
            result[columns] = hits_per_window


        return result



class RSIBacktest:
    def __init__(self, tickers, interval=1, period="2mo"):

        # Download prices
        prices = yf.download(tickers, period=period, interval=f"{interval}h", auto_adjust=False)['Adj Close']
        prices = prices.ffill()

        # Atributes
        self.__prices = prices

    def __calc_rsi(self, ticker, window_size, interval):
        delta = ticker.diff(periods=interval)
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)

        avg_gain = gain.tail(window_size).mean()
        avg_loss = loss.tail(window_size).mean()

        rs = avg_gain / (avg_loss if avg_loss != 0 else 1e-14)
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def window_test(self):

        summary_df = pd.DataFrame(columns=self.__prices.columns, index=['window_size', 'hour_interval'])

        with pd.ExcelWriter('outputs/RSIBacktest.xlsx', engine='openpyxl') as writer:


            for column in self.__prices.columns:

                # Data frame per ticker (column)
                ticker = self.__prices[column]

                # Create empty column. Before concat each different window size
                window_column = pd.DataFrame(index=range(1, 25))

                # Diferente window sizes
                for window_size in range(1, 21):

                    # List with hits per each hour
                    hits_per_each_hour = []

                    # Diferente hours distances
                    for hour in range(1, 25):

                        # RSI trend
                        rsi = self.__calc_rsi(ticker, window_size, interval=hour)
                        if rsi <= 30:
                            rsi_trend = 1
                        elif rsi >= 70:
                            rsi_trend = -1
                        else:
                            rsi_trend = 0

                        # List to hits to hours distances
                        accuracy_per_each_hour = []

                        #Backtest model
                        for backtest in range(0, 61):
                            # Window to prevision
                            backtest_window = self.__prices[column].iloc[backtest : backtest+window_size]
                            diff = backtest_window.iloc[-1] - backtest_window.iloc[0]

                            # If prevision is right
                            real_trend = 1 if diff > 0 else -1
                            hit = 1 if real_trend==rsi_trend else 0

                            # Add hit to a list
                            accuracy_per_each_hour.append(hit)

                        # Result for this hour distance
                        accuracy_per_hour = sum(accuracy_per_each_hour)
                        hits_per_each_hour.append(accuracy_per_hour)

                    # For a same window hits_per_each_hour
                    window_hits_per_each_hour = pd.Series(hits_per_each_hour, name=window_size)
                    # Concat like a column each list, hours in rows
                    window_column[window_size] = window_hits_per_each_hour

                # Create a sheet to each asset, in the same workplace excel
                window_column.to_excel(writer, sheet_name=column, index=True)

                # Best model for this asset
                max_hits_pos = window_column.stack().idxmax()
                hour_index, best_window = max_hits_pos
                summary_df.loc['window_size', column] = best_window
                summary_df.loc['hour_interval', column] = hour_index

            # salvar aba de resumo
            summary_df.to_excel(writer, sheet_name='Resume', index=True)

        return summary_df