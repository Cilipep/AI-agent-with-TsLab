# TSLab AI Agent - Enhanced Features

## Overview

This project extends TSLab with advanced analytics, optimization, and risk management capabilities.

## New Modules

### 1. Analytics Module (`analytics/`)

Advanced financial metrics and analysis tools.

**Features:**
- **Advanced Metrics**: Sortino, Calmar, Omega ratios, max drawdown duration
- **Correlation Analysis**: Rolling correlation, hierarchical clustering, diversification ratio
- **Regime Detection**: Threshold-based and Gaussian Mixture regime detection
- **Report Generation**: HTML/JSON reports with comprehensive metrics

**Usage:**
```python
from analytics import AnalyticsReport, calculate_all_metrics, correlation_matrix

# Calculate metrics
metrics = calculate_all_metrics(returns)

# Generate report
report = AnalyticsReport(output_dir="./reports")
report.generate_strategy_report(returns, strategy_name="MyStrategy")
report.save_html(report_data, "report.html")
```

**Files:**
- `analytics/advanced_metrics.py` - Core metrics calculations
- `analytics/correlation.py` - Correlation analysis
- `analytics/regime.py` - Regime detection
- `analytics/generate_report.py` - Report generation

---

### 2. Optimization Module (`optimization/`)

Walk-forward optimization and robustness testing.

**Features:**
- **Walk-Forward Analysis**: Partition data into in-sample/out-of-sample windows
- **Robustness Testing**: Monte Carlo simulation, K-fold cross-validation
- **Multi-Parameter Search**: Grid search, random search via TSLab API

**Usage:**
```powershell
# Walk-forward optimization
.\optimization\walk_forward.ps1 -ScriptName "RSICCIBot" -InSamplePct 70 -NumWindows 5

# Robustness testing
.\optimization\robustness.ps1 -ScriptName "RSICCIBot" -MonteCarloRuns 1000 -KFolds 5
```

```python
from optimization import TSLabOptimizer, grid_search

# Python-based optimization
optimizer = TSLabOptimizer()
results = grid_search(optimizer, "RSICCIBot", param_grids)
```

**Files:**
- `optimization/walk_forward.ps1` - Walk-forward analysis
- `optimization/robustness.ps1` - Monte Carlo & K-fold CV
- `optimization/multi_param.py` - Python optimization utilities

---

### 3. Risk Management Module (`risk/`)

Position sizing and drawdown protection.

**Features:**
- **Position Sizing**: Kelly Criterion, ATR-based, fixed fractional, volatility-adjusted
- **Circuit Breaker**: Drawdown monitoring with auto-stop capability
- **Risk Configuration**: JSON-based risk parameters

**Usage:**
```python
from risk import kelly_criterion, atr_position_size, optimal_position_size

# Kelly sizing
kelly = kelly_criterion(win_rate=0.55, avg_win=1.5, avg_loss=1.0)

# ATR sizing
atr_size = atr_position_size(capital=10000, risk_per_trade_pct=0.01, atr=2.5)

# Optimal sizing
size = optimal_position_size(capital=10000, method='kelly', win_rate=0.6)
```

```powershell
# Circuit breaker monitoring
.\risk\circuit_breaker.ps1 -ScriptName "RSICCIBot" -MaxDrawdownPct 20 -AutoStop
```

**Files:**
- `risk/position_sizing.py` - Position sizing algorithms
- `risk/circuit_breaker.ps1` - Drawdown monitoring
- `risk/config.json` - Risk configuration

---

## Installation

```bash
# Install Python dependencies
pip install pandas numpy scipy scikit-learn matplotlib requests

# Run tests
cd tests
pytest test_analytics.py -v
pytest test_risk.py -v
```

## Configuration

Edit `risk/config.json` to customize:
- Position sizing parameters
- Stop loss / take profit settings
- Drawdown limits
- Alert methods

## Integration with TSLab

All modules integrate with TSLab API at `http://localhost:5000/api`:

1. **Start TSLab**: `.\start-local-tslab.ps1`
2. **Run optimization**: Use PowerShell scripts or Python API
3. **Monitor risk**: Run circuit breaker in background
4. **Generate reports**: Use Analytics module post-backtest

## File Structure

```
ai-agent/
├── analytics/           # Analytics module
│   ├── advanced_metrics.py
│   ├── correlation.py
│   ├── regime.py
│   ├── generate_report.py
│   └── __init__.py
├── optimization/        # Optimization module
│   ├── walk_forward.ps1
│   ├── robustness.ps1
│   ├── multi_param.py
│   └── __init__.py
├── risk/               # Risk management module
│   ├── position_sizing.py
│   ├── circuit_breaker.ps1
│   ├── config.json
│   └── __init__.py
├── tests/              # Test suite
│   ├── test_analytics.py
│   └── test_risk.py
└── reports/            # Generated reports (auto-created)
```

## Examples

See `analytics/generate_report.py` for complete example usage.
