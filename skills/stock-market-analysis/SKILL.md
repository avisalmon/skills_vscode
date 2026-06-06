---
name: Stock Market Analysis with Python
description: >
  Analyze public market data with Python for education and research: yfinance,
  pandas time series, adjusted prices, returns, moving averages, volatility,
  drawdowns, portfolio weights, simple backtests, risk metrics, and plotting.
  TRIGGER: stock market, yfinance, ticker, returns, backtest, moving average,
  portfolio, volatility, Sharpe, drawdown.
version: 1.0.0
category: Finance / Data
tags: [stocks, yfinance, pandas, finance, backtesting, portfolio, risk]
---

# Stock Market Analysis with Python

## Overview

Use this skill for educational and research-oriented market data analysis with Python. It focuses on data handling, time series analysis, simple strategy experiments, and risk measurement. It does not provide financial advice or recommendations to buy or sell securities.

**Trigger words:** "stock market", "ticker", "yfinance", "returns", "moving average", "backtest", "portfolio", "volatility", "Sharpe", "drawdown", "market data".

---

## 1. Safety and Scope

Always include these assumptions in finance work:

- This is for education, research, and analysis, not personalized financial advice.
- Historical performance does not imply future results.
- Free data sources may have delays, gaps, corrections, or terms-of-use limits.
- Use adjusted prices for total-return-style equity analysis unless there is a reason not to.
- Avoid look-ahead bias: a decision at time `t` can only use data available at or before time `t`.
- Include transaction costs and slippage in any backtest that claims realism.

---

## 2. Setup

```bash
pip install pandas numpy matplotlib yfinance
```

Optional packages:

```bash
pip install plotly scipy statsmodels pandas-market-calendars
```

Use `pandas` for time series alignment, resampling, rolling windows, and joins. Use `yfinance` for accessible public-market data in small research scripts.

---

## 3. Download Price Data

```python
import yfinance as yf
import pandas as pd

symbols = ["SPY", "QQQ", "TLT"]
prices = yf.download(
    symbols,
    start="2018-01-01",
    auto_adjust=True,
    progress=False,
)["Close"]

prices = prices.dropna(how="all")
print(prices.tail())
```

Single ticker with metadata:

```python
ticker = yf.Ticker("AAPL")
history = ticker.history(period="5y", auto_adjust=True)
info = ticker.info

print(history.tail())
print(info.get("shortName"))
```

Data hygiene checks:

```python
print(prices.index.min(), prices.index.max())
print(prices.isna().sum())
print(prices.dtypes)
print(prices.index.is_monotonic_increasing)
```

---

## 4. Returns

Use percent returns for daily performance and log returns for additive analysis.

```python
simple_returns = prices.pct_change().dropna()
import numpy as np

log_returns = np.log(prices / prices.shift(1)).dropna()
```

Cumulative growth of one unit:

```python
growth = (1 + simple_returns).cumprod()
growth.plot(title="Growth of $1")
```

Annualized return and volatility, assuming daily bars:

```python
trading_days = 252
annual_return = (1 + simple_returns.mean()) ** trading_days - 1
annual_vol = simple_returns.std() * (trading_days ** 0.5)

summary = pd.DataFrame({
    "annual_return": annual_return,
    "annual_volatility": annual_vol,
})
print(summary)
```

---

## 5. Moving Averages and Signals

Simple moving-average crossover example:

```python
symbol = "SPY"
price = prices[symbol].dropna()

fast = price.rolling(50).mean()
slow = price.rolling(200).mean()

signal = (fast > slow).astype(int)
position = signal.shift(1).fillna(0)  # trade next bar, avoids look-ahead
returns = price.pct_change().fillna(0)
strategy_returns = position * returns

result = pd.DataFrame({
    "price": price,
    "fast_ma": fast,
    "slow_ma": slow,
    "signal": signal,
    "position": position,
    "strategy_returns": strategy_returns,
})
```

Plot:

```python
ax = result[["price", "fast_ma", "slow_ma"]].plot(figsize=(12, 6), title=f"{symbol} moving averages")
ax.set_ylabel("Price")
```

---

## 6. Simple Backtest Metrics

```python
def performance_stats(returns, periods_per_year=252):
    returns = returns.dropna()
    equity = (1 + returns).cumprod()
    total_return = equity.iloc[-1] - 1
    annual_return = equity.iloc[-1] ** (periods_per_year / len(returns)) - 1
    annual_vol = returns.std() * (periods_per_year ** 0.5)
    sharpe = annual_return / annual_vol if annual_vol != 0 else float("nan")
    running_max = equity.cummax()
    drawdown = equity / running_max - 1
    max_drawdown = drawdown.min()

    return pd.Series({
        "total_return": total_return,
        "annual_return": annual_return,
        "annual_volatility": annual_vol,
        "sharpe_no_rf": sharpe,
        "max_drawdown": max_drawdown,
    })

print(performance_stats(strategy_returns))
```

Compare buy-and-hold:

```python
comparison = pd.DataFrame({
    "buy_hold": returns,
    "strategy": strategy_returns,
})

print(comparison.apply(performance_stats))
(1 + comparison).cumprod().plot(title="Strategy vs Buy and Hold")
```

---

## 7. Drawdown Analysis

```python
def drawdown_series(returns):
    equity = (1 + returns.fillna(0)).cumprod()
    peak = equity.cummax()
    return equity / peak - 1

dd = drawdown_series(strategy_returns)
dd.plot(title="Drawdown", figsize=(12, 3))
```

Worst drawdown date:

```python
worst_date = dd.idxmin()
print("Worst drawdown:", dd.loc[worst_date], "on", worst_date.date())
```

---

## 8. Portfolio Weights

Static weighted portfolio:

```python
weights = pd.Series({
    "SPY": 0.60,
    "QQQ": 0.25,
    "TLT": 0.15,
})

returns = prices.pct_change().dropna()
weights = weights.reindex(returns.columns).fillna(0)
portfolio_returns = returns.dot(weights)

print(performance_stats(portfolio_returns))
```

Normalize user-provided weights:

```python
weights = weights / weights.sum()
```

Rebalanced monthly portfolio approximation:

```python
monthly_returns = (1 + returns).resample("ME").prod() - 1
monthly_portfolio = monthly_returns.dot(weights)
```

---

## 9. Avoid Common Backtest Bugs

Look-ahead bias:

```python
# Bad: position uses today's close and earns today's return
strategy_returns = signal * returns

# Better: today's signal becomes tomorrow's position
strategy_returns = signal.shift(1).fillna(0) * returns
```

Survivorship bias:

- Testing only current successful companies ignores delisted and failed companies.
- Be careful when testing long histories of index constituents.

Dividend and split handling:

- Use adjusted prices for most equity-return analysis.
- If you need raw execution prices, keep raw OHLC separate from adjusted return series.

Costs:

```python
turnover = position.diff().abs().fillna(position.abs())
cost_per_trade = 0.0005  # 5 basis points example
strategy_returns_after_costs = strategy_returns - turnover * cost_per_trade
```

---

## 10. Useful Prompts for Copilot

```text
Write a Python script using yfinance and pandas to compare SPY, QQQ, and TLT annualized return, volatility, and max drawdown since 2018.
```

```text
Build an educational moving-average crossover backtest that shifts signals by one day to avoid look-ahead bias and includes simple transaction costs.
```

```text
Help me debug why my portfolio returns have NaN values after joining several ticker price series.
```

```text
Create a clean matplotlib chart with price, moving averages, buy/sell markers, and a drawdown subplot.
```

---

## Best Practices

- Use adjusted close or auto-adjusted OHLC for return calculations.
- Check missing data before computing returns.
- Keep price data, signals, positions, and returns as separate columns.
- Shift signals before multiplying by returns.
- Include transaction costs for strategy comparisons.
- Report max drawdown alongside return and volatility.
- Use business-day aware resampling carefully and document assumptions.
- Never present a backtest as a prediction.
- State clearly that the analysis is educational and not financial advice.
