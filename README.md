# DevilTongues - Synthetic Bond Arbitrage Platform

<div align="center">

![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![LSEG](https://img.shields.io/badge/LSEG-Refinitiv-orange.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Real-Time Synthetic Bond Arbitrage Detection Platform**

[Documentation](https://www.deviltongues.website) • [Report Bug](https://github.com/deviltongues/Tongues/issues) • [Request Feature](https://github.com/deviltongues/Tongues/issues)

</div>

---

## Overview

DevilTongues is a sophisticated financial analytics platform that identifies arbitrage opportunities in synthetic bonds through real-time put-call parity analysis. By connecting to LSEG Refinitiv's enterprise-grade market data infrastructure, the platform calculates implied risk-free rates from options pricing and flags profitable conversion and reverse conversion strategies.

### What are Synthetic Bonds?

Synthetic bonds are created by combining options positions to replicate the payoff of holding (or shorting) the underlying stock. When these synthetic positions are mispriced relative to the actual stock, arbitrage opportunities emerge that our platform automatically detects and analyzes.

## Key Features

### 📊 Real-Time Market Data
- Live spot prices and comprehensive options chains from LSEG Refinitiv
- Sub-second latency for major equity underlyings (AAPL, MSFT, TSLA, NVDA, etc.)
- Bid-ask-last price tracking with exchange timestamps

### 🔍 Arbitrage Detection Engine
- **Put-Call Parity Analysis**: Validates the relationship C - P = S - K×e^(-rT)
- **Implied Rate Calculation**: Derives risk-free rates from options pricing
- **Threshold-Based Signaling**: Flags opportunities exceeding user-defined thresholds
- **Dual Strategy Detection**: Identifies both conversion and reverse conversion opportunities

### 💡 Strategy Analysis Tools
- Detailed position breakdowns showing exact call, put, and stock positions required
- Profit/loss calculations with best/worst case scenarios
- Comprehensive risk assessment covering execution, assignment, and margin risks
- Execution cost modeling incorporating commissions, slippage, and transaction costs

### 📈 Advanced Visualization
- **Interactive 3D Surface Plots**: Visualize implied rate term structures
- **Time Series Analysis**: Track implied volatility and rate changes over time
- **Moneyness Comparison**: Analyze arbitrage opportunities across different strike levels

### 💰 Execution Calculator
- Model real-world execution costs with customizable parameters
- ROI and annualized return calculations
- Scenario analysis (best case, expected, worst case)
- Margin requirement estimation

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web Framework | Shiny for Python ≥0.6.0 | Reactive web application with real-time updates |
| Data Provider | LSEG Refinitiv Data API ≥1.5.0 | Market data connectivity and options chains |
| Data Processing | Pandas ≥2.0.0, NumPy ≥1.24.0 | Data manipulation and numerical computations |
| Visualization | Plotly ≥5.18.0 | Interactive 3D surface plots and charts |
| Scientific Computing | SciPy ≥1.11.0 | Surface interpolation and numerical methods |

## Quick Start

### Prerequisites

- **Python 3.12** (Python 3.13 not yet supported by all dependencies)
- **LSEG Refinitiv Data API credentials**
- **LSEG Workspace or Eikon** desktop application running and logged in

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/deviltongues/Tongues.git
cd Tongues

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment

# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -e .

# 5. Launch application
shiny run app.py
```

The application will start on `http://127.0.0.1:8000` by default.

### First-Time Usage

1. **Market Data Tab**: Select an underlying (e.g., MSFT.O) and click "FETCH SPOT PRICE"
2. **Configure Options Chain**: Set strike range (e.g., 400-500), expiry dates, and click "SCAN OPTIONS CHAIN"
3. **Analysis Tab**: Set risk-free rate (e.g., 5.0%), arbitrage threshold (e.g., 0.5%), and click "ANALYZE ARBITRAGE"
4. **Review Results**: Click on detected opportunities to see detailed strategy breakdowns
5. **Execution Calculator Tab**: Model real-world execution costs with your position parameters

## Strategy Explanation

### Put-Call Parity Foundation

The platform exploits deviations from put-call parity, a fundamental no-arbitrage relationship:

```
C - P = S - K × e^(-rT)
```

Where:
- **C** = Call option price
- **P** = Put option price (same strike & expiry)
- **S** = Spot price of underlying
- **K** = Strike price
- **r** = Risk-free interest rate
- **T** = Time to expiration (years)

### Arbitrage Strategies

#### Reverse Conversion (Implied Rate > Benchmark)
**When**: The synthetic short stock is overpriced relative to actual stock

**Positions**:
1. SELL Call option at strike K
2. BUY Put option at strike K
3. BUY underlying stock

**Profit Source**: Collect premium from selling the expensive synthetic (short call + long put)

#### Conversion (Implied Rate < Benchmark)
**When**: The synthetic long stock is underpriced relative to actual stock

**Positions**:
1. BUY Call option at strike K
2. SELL Put option at strike K
3. SHORT underlying stock

**Profit Source**: Buy cheap synthetic (long call + short put), earn interest on short proceeds

### ⚠️ Risk Considerations

The platform flags important execution risks:

- **Execution Risk**: Simultaneous 3-leg orders may not fill at desired prices
- **Pin Risk**: At expiration, if stock ≈ strike, assignment uncertainty arises
- **Early Assignment**: American-style short options may be assigned early
- **Dividend Risk**: Ex-dividend dates affect put-call parity
- **Transaction Costs**: Commissions and slippage may erode thin arbitrage margins
- **Margin Requirements**: Short stock positions require substantial margin/collateral

## Data Sources

### LSEG Refinitiv Data API

The platform connects to LSEG's enterprise-grade financial data infrastructure:

- **Equity Quotes**: Real-time spot prices via `TR.PriceClose` field
- **Options Discovery**: Comprehensive options chain data from OPRA (Options Price Reporting Authority)
- **Pricing Fields**: `CF_BID`, `CF_ASK`, `CF_LAST` for accurate mid-price calculation
- **Contract Details**: Strike prices, expiry dates, call/put designation, RICs

### Data Fields Retrieved

```python
# Spot Price
spot_df = rd.get_data("MSFT.O", ['TR.PriceClose'])

# Options Chain
options_chain = rd.discovery.search(
    view=rd.discovery.Views.EQUITY_QUOTES,
    filter="SearchAllCategoryv2 eq 'Options' and "
           "ExpiryDate gt 2025-12-06 and "
           "StrikePrice ge 400 and StrikePrice le 480 and "
           "ExchangeName xeq 'OPRA'"
)

# Options Pricing
price_data = rd.get_data(
    universe=chain['RIC'].tolist(),
    fields=['CF_BID', 'CF_ASK', 'CF_LAST']
)
```

## Project Structure

```
Tongues/
├── app.py                    # Main Shiny application
├── modern.css                # Modern UI styling
├── custom.css                # Legacy UI styling
├── pyproject.toml            # Project metadata & dependencies
├── requirements.txt          # Pip dependencies
├── README.md                 # This file
├── index.html                # GitHub Pages website
├── CNAME                     # Custom domain configuration
├── src/
│   └── deviltongues/
│       ├── __init__.py
│       ├── fetch_options.py  # Data retrieval utilities
│       └── utilities.py      # Helper functions
└── old code/                 # Legacy implementations
```

## Development Roadmap

### Planned Features
- [ ] Multi-leg order execution simulation with realistic fill modeling
- [ ] Historical arbitrage backtesting engine with P&L attribution
- [ ] Real-time push notifications for high-value opportunities
- [ ] Portfolio position tracking and risk management dashboard
- [ ] Integration with execution platforms (Interactive Brokers, TD Ameritrade)
- [ ] Machine learning models for arbitrage opportunity prediction
- [ ] Additional arbitrage strategies (box spreads, butterflies, iron condors)

### Known Limitations
- Requires active LSEG Workspace/Eikon session for authentication
- Limited to OPRA exchange options data (US equities and indices)
- No automated order execution - analysis and visualization only
- 3D surface visualization may require manual refresh in certain scenarios
- Historical data limited by LSEG API query constraints

## Contributing

Contributions are welcome! Key areas for improvement:

- Enhanced execution cost models incorporating market microstructure
- Additional arbitrage strategies (calendar spreads, diagonal spreads)
- Comprehensive backtesting framework with transaction cost modeling
- Performance optimization for analyzing large options chains (10,000+ contracts)
- Mobile-responsive UI enhancements
- Additional data provider integrations (Bloomberg, FactSet)

Please submit pull requests or open issues on GitHub.

## Authors

**Sunny Zhang** - Duke University  
Fintech Program

**Victoria Li** - Duke University  
Fintech Program

## License

MIT License - see LICENSE file for details

## Acknowledgments

- LSEG Refinitiv for providing market data infrastructure
- Shiny for Python team for the reactive web framework
- Duke University Quantitative Finance program

## Support & Contact

- **GitHub Repository**: [github.com/deviltongues/Tongues](https://github.com/deviltongues/Tongues)
- **Issues**: [Report bugs or request features](https://github.com/deviltongues/Tongues/issues)
- **Website**: [www.deviltongues.website](https://www.deviltongues.website)

---

<div align="center">

**Created by Sunny Zhang & Victoria Li at Duke University**

*Last Updated: December 2025*

</div>