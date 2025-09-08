import pandas as pd

def read_weights(data, sheet_name="Planilha1"):
    df = pd.read_excel(data, sheet_name=sheet_name)

    # Tickers & Weights
    tickers = df.iloc[:, 0].tolist()
    weights = df.iloc[:, 1].astype(float).tolist()

    return tickers, weights

def read_notes(info):
    tickers = info.columns.tolist()
    notes = pd.Series(info.iloc[0,:], index=tickers)

    return tickers, notes