# DevilTongues - Synthetic Bond Arbitrage Platform

## Overview

DevilTongues is a real-time options arbitrage detection platform that identifies mispricing opportunities in synthetic bonds through put-call parity analysis. The application connects to LSEG (London Stock Exchange Group) data to monitor options chains and calculate implied risk-free rates, flagging profitable conversion and reverse conversion arbitrage opportunities.

## What Does This Tool Do?

The platform performs sophisticated financial analysis to detect arbitrage opportunities by:

1. **Fetching Real-Time Market Data**: Retrieves live spot prices and options chains from LSEG Refinitiv Data API
2. **Calculating Implied Risk-Free Rates**: Uses put-call parity to compute implied rates from options pricing
3. **Identifying Arbitrage Signals**: Compares implied rates against benchmark risk-free rates to detect mispricing
4. **Visualizing Opportunities**: Displays arbitrage signals with detailed execution strategies and cost calculations
5. **3D Surface Analysis**: Renders implied rate surfaces across strike prices and time to expiration

## Key Features

### Market Data Integration
- **Real-time spot price fetching** for major equity underlyings (AAPL, MSFT, TSLA, NVDA, etc.)
- **Options chain retrieval** with customizable strike and expiry filters
- **Mid-price calculation** from bid-ask spreads with last trade fallback
- **Exchange timestamp tracking** for data freshness validation

### Arbitrage Detection Engine
- **Put-Call Parity Analysis**: Validates the relationship C - P = S - K*e^(-rT)
- **Implied Rate Calculation**: Derives risk-free rates from options pricing
- **Threshold-Based Signaling**: Flags opportunities exceeding user-defined arbitrage thresholds
- **Dual Strategy Detection**: Identifies both conversion (buy synthetic + short stock) and reverse conversion (sell synthetic + buy stock) opportunities

### Strategy Analysis Tools
- **Detailed Position Breakdown**: Shows exact call, put, and stock positions required
- **Profit/Loss Calculations**: Estimates expected returns with best/worst case scenarios
- **Risk Assessment**: Outlines execution risks, margin requirements, and potential complications
- **Execution Cost Modeling**: Incorporates commissions, slippage, and transaction costs

### Advanced Visualization
- **Interactive 3D Surface Plots**: Visualize implied rate term structures
- **Time Series Analysis**: Track implied volatility and rate changes over time
- **Moneyness Comparison**: Analyze arbitrage opportunities across different strike levels

## Data Sources

### LSEG Refinitiv Data API
The platform connects to LSEG's enterprise-grade financial data infrastructure:

- **Equity Quotes**: Real-time spot prices for underlying securities
- **Options Discovery**: Comprehensive options chain data from OPRA (Options Price Reporting Authority)
- **Pricing Fields**: Bid, Ask, Last, Settle prices for options contracts
- **Greeks & Analytics**: Delta, gamma, vega, theta from LSEG's analytics engines

### Data Fields Retrieved
```python
# Spot Price Fields
"TR.PriceClose"  # Closing price for underlying

# Options Chain Filters
- SearchAllCategoryv2: 'Options'
- ExpiryDate: User-defined range
- StrikePrice: User-defined range  
- ExchangeName: 'OPRA'
- UnderlyingQuoteRIC: Target underlying

# Options Pricing Fields
- CF_BID: Call/Put bid price
- CF_ASK: Call/Put ask price
- CF_LAST: Last traded price
```

## Strategy Explanation

### Put-Call Parity Foundation

The platform exploits deviations from put-call parity, a fundamental no-arbitrage relationship:

**C - P = S - K * e^(-rT)**

Where:
- C = Call option price
- P = Put option price (same strike & expiry)
- S = Spot price of underlying
- K = Strike price
- r = Risk-free interest rate
- T = Time to expiration (years)

### Arbitrage Detection Logic

#### Reverse Conversion (Sell Synthetic + Buy Stock)
When implied rate > benchmark rate:

**Positions:**
1. SELL Call option at strike K
2. BUY Put option at strike K  
3. BUY underlying stock

**Profit Source:** The synthetic short stock (short call + long put) is overpriced relative to actual stock. Collect premium from selling the expensive synthetic.

**Example:**
- Implied rate: 5.5% (detected from options prices)
- Benchmark rate: 5.0% (actual risk-free rate)
- Arbitrage: 0.5% spread * position size

#### Conversion (Buy Synthetic + Short Stock)
When implied rate < benchmark rate:

**Positions:**
1. BUY Call option at strike K
2. SELL Put option at strike K
3. SHORT underlying stock

**Profit Source:** The synthetic long stock (long call + short put) is underpriced. Buy cheap synthetic, earn interest on short proceeds.

### Risk Considerations

The platform flags important execution risks:

1. **Execution Risk**: Simultaneous 3-leg orders may not fill at desired prices
2. **Pin Risk**: At expiration, if stock = strike, assignment uncertainty arises
3. **Early Assignment**: American-style short options may be assigned early
4. **Dividend Risk**: Ex-dividend dates affect put-call parity
5. **Transaction Costs**: Commissions and slippage may erode thin arbitrage margins
6. **Margin Requirements**: Short stock positions require substantial margin/collateral

## How to Run Locally

### Prerequisites

1. **Python Environment**: Python 3.12 required (3.13 not supported by some dependencies)
2. **LSEG Access**: Valid Refinitiv Data API credentials
3. **Desktop Application**: LSEG Workspace or Eikon must be running for authentication

### Installation Steps

#### 1. Clone the Repository
```bash
git clone https://github.com/deviltongues/Tongues.git
cd Tongues
```

#### 2. Create Virtual Environment
```bash
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -e .
```

This installs:
- `shiny>=0.6.0` - Web application framework
- `refinitiv.data>=1.5.0` - LSEG data connectivity
- `pandas>=2.0.0` - Data manipulation
- `numpy>=1.24.0` - Numerical computing
- `plotly>=5.18.0` - Interactive visualizations
- `scipy>=1.11.0` - Scientific computing (for surface interpolation)

#### 4. Configure LSEG Authentication

The application uses LSEG Workspace desktop authentication. Ensure:
- LSEG Workspace or Eikon desktop application is running
- You are logged in with valid credentials
- API access is enabled in your account

#### 5. Launch Application
```bash
shiny run app.py
```

The application will start on `http://127.0.0.1:8000` by default.

### First-Time Usage

1. **Fetch Spot Price**: 
   - Select underlying (e.g., MSFT.O)
   - Click "FETCH SPOT" to retrieve current price

2. **Configure Options Chain**:
   - Set Min/Max Strike (e.g., 300-500)
   - Set Min/Max Expiry dates
   - Click "SCAN OPTIONS"

3. **Analyze Arbitrage**:
   - Set Risk-Free Rate (e.g., 5.0%)
   - Set Arbitrage Threshold (e.g., 0.5%)
   - Click "ANALYZE ARBITRAGE"

4. **Review Results**:
   - View detected opportunities in "Arbitrage Signals" tab
   - Click on rows to see detailed strategy breakdowns
   - Use "Execution Calculator" to model real-world costs

## Screenshots

### Main Dashboard - Market Data
![Market Data Interface](screenshots/market_data.png)
*The main control panel showing spot price fetching and options chain configuration. Users can filter by strike range, expiry dates, and maximum contracts.*

### Arbitrage Signals Table  
![Arbitrage Detection](screenshots/arbitrage_signals.png)
*Detected arbitrage opportunities displaying strike prices, expiry dates, implied rates, and recommended strategies. Green highlights indicate profitable conversion opportunities.*

### Strategy Detail View
![Strategy Breakdown](screenshots/strategy_details.png)
*Detailed breakdown of a selected arbitrage opportunity showing required positions, expected profit, risks, and actionable recommendations.*

### Execution Cost Calculator
![Cost Calculator](screenshots/execution_calculator.png)
*Interactive calculator modeling real-world execution costs including commissions, slippage, and margin requirements. Shows expected returns with best/worst case scenarios.*

### 3D Implied Rate Surface
![3D Surface Plot](screenshots/surface_plot.png)
*Interactive 3D visualization of implied risk-free rates across strike prices and time to expiration. Allows identification of term structure arbitrage opportunities.*

## Technical Architecture

### Data Flow
1. **User Input** → Strike/Expiry filters → Options chain query
2. **LSEG API** → Raw options prices → DataFrame processing
3. **Arbitrage Engine** → Put-Call parity analysis → Signal generation
4. **Visualization** → Plotly/Dash rendering → Interactive UI

### Key Components

**`app.py`** - Main Shiny application with 4 core functions:
- `_fetch_spot()`: Retrieves underlying spot prices
- `_fetch_chain()`: Queries and processes options chains
- `_analyze_arbitrage()`: Computes implied rates and detects opportunities
- `surface_plot()`: Renders 3D implied rate visualization

**`build_surface_df()`** - Transforms raw options data:
- Calculates mid-prices from bid-ask
- Computes time to expiration (T)
- Structures data for arbitrage analysis

**`analyze_arbitrage()`** - Core detection logic:
- Merges call and put data by strike/expiry
- Calculates implied risk-free rates
- Flags opportunities exceeding threshold

**`get_strategy_details()`** - Strategy explanation engine:
- Generates position breakdowns
- Calculates expected P&L
- Assesses execution risks

## Project Structure

```
Tongues/
├── app.py                          # Main Shiny application
├── custom.css                      # UI styling
├── pyproject.toml                  # Project metadata & dependencies
├── requirements.txt                # Pip dependencies
├── README.md                       # Project overview
├── index.html                      # GitHub Pages entry (iframe wrapper)
├── src/
│   └── deviltongues/
│       ├── __init__.py
│       ├── fetch_options.py        # Options data retrieval utilities
│       └── utilities.py            # Helper functions
└── old code/                       # Legacy FastAPI implementation
```

## Development Roadmap

### Planned Features
- [ ] Multi-leg order execution simulation
- [ ] Historical arbitrage backtest module
- [ ] Real-time alert notifications
- [ ] Portfolio position tracking
- [ ] Integration with execution platforms (IB, TDA)
- [ ] Machine learning arbitrage prediction

### Known Limitations
- Requires active LSEG Workspace session
- Limited to OPRA exchange options data
- No automated order execution (analysis only)
- 3D surface requires manual refresh in some cases

## Contributing

Contributions welcome! Key areas for improvement:
- Enhanced execution cost models
- Additional arbitrage strategies (box spreads, butterflies)
- Backtesting framework
- Performance optimization for large options chains

## License

MIT License - see LICENSE file for details

## Authors

**Jake Vestal** - Duke University - jmv13@duke.edu

## Acknowledgments

- LSEG Refinitiv for market data infrastructure
- Shiny for Python team for the web framework
- Duke University Quantitative Finance program

---

## Quick Start Commands

```bash
# Clone and setup
git clone https://github.com/deviltongues/Tongues.git
cd Tongues
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e .

# Launch application
shiny run app.py

# Access at http://127.0.0.1:8000
```

## Contact & Support

- **GitHub Issues**: [https://github.com/deviltongues/Tongues/issues](https://github.com/deviltongues/Tongues/issues)
- **Email**: jmv13@duke.edu
- **Website**: [https://www.deviltongues.website](https://www.deviltongues.website)

---

*Last Updated: December 2025*