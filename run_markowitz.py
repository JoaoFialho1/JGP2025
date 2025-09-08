from src.expeted_return import expecteds_returns
from src.markowitz import markowitz_monte_carlo
import pandas as pd


# Read datas
info = pd.read_excel("inputs/notes.xlsx", index_col=0)

# Infos
tickers = info.columns.tolist()
notes = info.iloc[0]

# Expected returns
expected = expecteds_returns(info)

# Markowitz
expected = expected.reindex(tickers)
markowitz_monte_carlo(tickers, expected, notes, n_portfolios=1000000, name="semana2")