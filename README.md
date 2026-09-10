# TradeLab

### Indian Stock Market Analysis & Backtesting Platform

TradeLab is a Python-based financial analytics and backtesting platform designed to analyze Indian stock market data, generate technical trading signals, simulate trading strategies, and evaluate their performance using quantitative metrics.

The project focuses on systematic strategy evaluation rather than real-money trading.

---

## 1. Project Overview

TradeLab provides an end-to-end workflow:

**Market Data**  
↓  
**Data Cleaning & Validation**  
↓  
**Technical Indicators**  
↓  
**Trading Signals**  
↓  
**Strategy Rules**  
↓  
**Backtesting**  
↓  
**Performance Metrics**  
↓  
**Validation**  
↓  
**Interactive Dashboard**

The platform currently focuses on Indian equities and major market indices.

---

## 2. Key Features

- Historical Indian market data analysis
- OHLCV data cleaning and validation
- SMA and EMA indicators
- RSI indicator
- MACD indicator
- Volume-based analysis
- Technical signal generation
- Rule-based trading strategy
- Stop-loss and target management
- Risk-based position sizing
- Backtesting
- Transaction-cost analysis
- Performance evaluation
- SQLite trade/result storage
- Multi-asset validation
- Multi-period validation
- Parameter sensitivity / overfitting analysis
- Out-of-sample validation
- Robustness analysis
- Interactive Streamlit dashboard
- Trade history and equity-curve visualization

---

## 3. Technology Stack

| Technology | Purpose |
|------------|---------|
| Python | Core development |
| Pandas | Data manipulation |
| NumPy | Numerical analysis |
| yfinance | Historical market data |
| Backtesting.py | Strategy backtesting |
| Plotly | Interactive visualization |
| Streamlit | Dashboard |
| SQLite | Result storage |
| Excel | Supporting analysis |
| Git & GitHub | Version control |

---

## 4. Strategy Logic

### Entry Conditions

A long position is considered when:

- Close > EMA 20
- EMA 20 > EMA 50
- RSI > 50
- MACD > Signal
- Volume > 20-day average volume

For market indices, the volume condition is skipped where volume is unavailable or unsuitable.

### Exit Conditions

A position can be exited when:

- Close < EMA 20
- EMA 20 < EMA 50
- RSI < 50
- MACD < Signal

### Risk Management

- Initial capital: ₹100,000
- Risk per trade: 1%
- Stop-loss: 5%
- Reward-to-risk ratio: 1:2
- Position sizing is based on the amount of capital being risked per trade.

---

## 5. Technical Indicators

TradeLab currently implements:

### Moving Averages

- SMA 20
- SMA 50
- EMA 20
- EMA 50

### Momentum

- RSI 14

### Trend / Momentum

- MACD (12, 26, 9)

### Volume

- 20-day average volume
- Volume-based signal confirmation

---

## 6. Backtesting & Performance Metrics

The backtesting module evaluates strategies using metrics such as:

- Total Return
- Buy & Hold Return
- Annualized Return
- CAGR
- Volatility
- Sharpe Ratio
- Sortino Ratio
- Calmar Ratio
- Maximum Drawdown
- Number of Trades
- Win Rate
- Profit Factor
- Expectancy
- Transaction Costs

The project also compares performance with and without transaction costs.

---

## 7. Validation Methodology

TradeLab does not rely only on a single backtest.

The strategy was evaluated through multiple validation layers.

### Multi-Asset Validation

The same baseline strategy was tested across multiple Indian stocks and indices.

### Multi-Period Validation

Testing was performed across different historical periods:

- 2020–2021
- 2022–2023
- 2024–2025

### Parameter Sensitivity

Multiple combinations of strategy parameters were tested to study sensitivity and identify potential overfitting.

### Out-of-Sample Validation

A separate 2026 period was used for out-of-sample testing where data was available.

### Robustness Analysis

Results from different assets, periods, parameter combinations, and out-of-sample testing were consolidated to evaluate strategy stability.

---

## 8. Supported Assets

The project currently includes analysis for assets such as:

### Stocks

- RELIANCE
- GACM Technologies
- ETERNAL
- IRFC
- RVNL
- RailTel
- Torrent Power

### Indices

- NIFTY 50
- BANK NIFTY
- SENSEX

---

## 9. Project Structure

```text
TradeLab/
│
├── Dataset/
│   ├── Raw/
│   └── Processed/
│
├── Document/
│
├── Notebooks/
│
├── result/
│   └── validation/
│
├── Src/
│   ├── data/
│   ├── validation/
│   ├── app.py
│   └── assets.py
│
├── Tests/
│
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 10. Dashboard

The TradeLab Streamlit dashboard provides an interactive interface for:

- Selecting a stock or market index
- Viewing historical price data
- Viewing technical indicators
- Viewing trading signals
- Running backtests
- Viewing performance metrics
- Viewing trade history
- Viewing equity curves
- Performing historical what-if analysis

---

## 11. Installation

Clone the repository:

```bash
git clone https://github.com/utkarsh-workin/TradeLab.git
cd TradeLab
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment on Windows:

```bash
.venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

---

## 12. Running the Dashboard

Run the following command from the project root:

```bash
streamlit run Src/app.py
```

The TradeLab dashboard will open in your browser.

---

## 13. Data & Storage

TradeLab follows a structured data workflow:

1. Data Collection
2. Data Cleaning
3. Data Validation
4. Technical Indicator Calculation
5. Trading Signal Generation
6. Backtesting
7. Result Storage

SQLite is used for storing backtesting and trade-related results.

Raw and processed datasets, generated results, and database files are excluded from Git tracking using `.gitignore`.

---

## 14. Limitations

- Historical backtesting does not guarantee future performance.
- Market data from external providers may have limitations.
- Transaction costs are modeled using a simplified assumption.
- The current strategy is rule-based.
- The project does not provide live trading or automated order execution.
- The current version focuses on Indian stocks and indices.
- Strategy parameters are not guaranteed to be optimal.
- TradeLab is intended for educational and research purposes.

---

## 15. Future Scope

- Portfolio-level backtesting
- Advanced transaction-cost modeling
- Walk-forward analysis
- More extensive out-of-sample testing
- Advanced risk analytics
- Machine-learning-based strategy research
- Real-time market data
- Trading alerts
- Paper trading
- Broker API integration
- Algorithmic trading
- International market support

---

## 16. Disclaimer

TradeLab is an educational and research project.

The results generated by this platform are based on historical data and simulated trading conditions. Historical performance does not guarantee future results.

Nothing in this project should be considered financial, investment, or trading advice.

---

## 17. Author

**Kumar Utkarsh**

B.Tech Computer Science & Engineering

### Interests

- Financial Analytics
- Data Analytics
- Quantitative Trading
- Python
- SQL
- Financial Markets

---

## Project Status

**Version:** V1  
**Market:** Indian Stocks & Indices  
**Focus:** Technical Analysis + Rule-Based Backtesting + Validation

---

## License

This project is intended for educational and research purposes.