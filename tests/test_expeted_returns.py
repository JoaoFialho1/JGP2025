from src.expeted_return import expecteds_returns
import pandas as pd

info = pd.read_excel("inputs/notes.xlsx", index_col=0)

expexted = expecteds_returns(info)
print(expexted)