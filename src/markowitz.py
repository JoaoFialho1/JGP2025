from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt


def markowitz_monte_carlo(tickers, expected_returns, notes, days_analysis=123, end=None,
                          risk_free=0.05, n_portfolios=100000, name=None):


    # Modify dates
    if end is None:
        end = datetime.today()
    else:
        end = datetime.strptime(end, "%Y-%m-%d")
    start = end - timedelta(days=days_analysis)

    # Datas & Returns
    data = yf.download(tickers, start=start, end=end, auto_adjust=False)['Adj Close']
    returns = data.pct_change().fillna(0)

    # Add Risk-free column daily returns
    if risk_free:
        risk_free_daily = (1 + risk_free) ** (1/252) - 1
        risk_free_week = risk_free_daily ** 7
        dates = pd.date_range(start=start, end=end)
        risk_free_column = pd.Series(risk_free_daily, index=dates, name="Risk free")

        # Concat
        returns = pd.concat([returns, risk_free_column], axis=1).fillna(0)
        expected_returns.loc['Risk free'] = risk_free_daily

        #notes
        notes = notes.copy()
        notes.loc['Risk free'] = 1

        notes = notes.reindex(returns.columns)
        expected_returns = expected_returns.reindex(returns.columns)

    else:
        expected_returns = expected_returns.reindex(returns.columns)

    # Parameters
    cov_matrix = returns.cov() * 252 # Annual
    num_assets = len(expected_returns)

    # Covert to array
    expected_returns = expected_returns.values
    notes = notes.values


    #==============GENERATE-RANDOM-PORTFOLIOS================#

    # Portfolios
    portfolios_dict = {"Sharpe": [], "Return": [], "Volatility": []}
    portfolios_dict.update({asset: [] for asset in returns.columns})

    for portfolio in range(n_portfolios):
        # Random weights
        raw_weights = np.random.randint(1, 10001, size=num_assets) / 10000

        # Signal
        signed_weights  = raw_weights * np.sign(notes)

        # Normalize
        weights = signed_weights / np.sum(np.abs(signed_weights))

        # Results
        portfolio_returns = weights.T @ expected_returns
        portfolio_volatility = np.sqrt(weights.T @ cov_matrix.values @ weights)

        # Sharpe
        if portfolio_volatility==0:
            sharpe = np.nan
        else:
            sharpe = (portfolio_returns - risk_free_week) / portfolio_volatility


    # ===================EXPORT-DATAS========================#

        # Export datas
        for i, ticker in enumerate(returns.columns):
            portfolios_dict[ticker].append(weights[i])
        portfolios_dict["Sharpe"].append(sharpe)
        portfolios_dict["Return"].append(portfolio_returns)
        portfolios_dict["Volatility"].append(portfolio_volatility)

    portfolios_dict = pd.DataFrame(portfolios_dict)


    # ===============SAVE-PORTFOLIOS==================#

    time = end.strftime("%Y-%m-%d")
    # Save inputs
    portfolios_dict.to_excel(f'outputs/{name}_portfolios_{time}.xlsx')


    #===============PLOT-EFFICIENT-FRONTIER==================#

    # Portfolio with best Sharpe
    idx_max_sharpe = portfolios_dict['Sharpe'].idxmax()
    best_portfolio = portfolios_dict.loc[idx_max_sharpe]

    # Plot Returns x Volatility rainbow by Sharpe
    fig, ax = plt.subplots(figsize=(12, 8))
    scatter = ax.scatter(
        portfolios_dict['Volatility'],
        portfolios_dict['Return'],
        c=portfolios_dict['Sharpe'],
        cmap='viridis',  # colorshape: 'plasma', 'coolwarm'
        alpha=0.6)

    # Best Sharpe
    ax.scatter(
        best_portfolio['Volatility'],
        best_portfolio['Return'],
        color='red',
        marker='*',
        s=300,  # Star size
        label='Best Sharpe')

    # Parameters of graph
    ax.set_xlabel('Volatility')
    ax.set_ylabel('Expected return')
    ax.set_title(f'Efficient frontier (Monte Carlo)\n{name}')
    ax.grid(True)

    # Sharpe colorbar
    cbar = fig.colorbar(scatter, ax=ax)
    cbar.set_label('Sharpe Ratio')

    # Save Plot
    fig.savefig(f'outputs/{name}_efficient_frontier_{time}.png', dpi=300)
    plt.show()