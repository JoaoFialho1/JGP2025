import pandas as pd
from src.windows_backtests import RSIBacktest
from src.RSI_calculate import rsi_adjusted

# Ler planilha
info = pd.read_excel("inputs/notes.xlsx", index_col=0)

tickers = info.columns.tolist()
notes = pd.Series(info.iloc[0, :], index=tickers)

rsi_class = RSIBacktest(tickers)
models = rsi_class.window_test()

# Chamar função RSI ajustada
rsi_values = rsi_adjusted(models)
print(rsi_values)