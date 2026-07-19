"""Generate TSLab script configs for all optimized instruments."""
import json
from pathlib import Path

# Optimized params from walk-forward validation
INSTRUMENTS = {
    "ETH": {
        "symbol": "ETHUSDT",
        "exchange": "BINANCE",
        "params": {
            "hidden_size": 32, "num_layers": 2, "dropout": 0.4899, "nhead": 8,
            "window": 20, "max_features": 40, "batch_size": 128,
            "learning_rate": 0.000181, "stop_loss_pct": 0.0332, "take_profit_pct": 0.0852,
        },
        "metrics": {"return": 15.79, "sharpe": 0.84, "max_dd": -14.37, "win_rate": 34.0},
    },
    "SOL": {
        "symbol": "SOLUSDT",
        "exchange": "BINANCE",
        "params": {
            "hidden_size": 16, "num_layers": 2, "dropout": 0.3037, "nhead": 4,
            "window": 30, "max_features": 40, "batch_size": 128,
            "learning_rate": 0.000209, "stop_loss_pct": 0.0415, "take_profit_pct": 0.1030,
        },
        "metrics": {"return": 8.30, "sharpe": 0.62, "max_dd": -8.17, "win_rate": 36.4},
    },
    "XLM": {
        "symbol": "XLMUSDT",
        "exchange": "BINANCE",
        "params": {
            "hidden_size": 16, "num_layers": 1, "dropout": 0.3443, "nhead": 4,
            "window": 40, "max_features": 40, "batch_size": 32,
            "learning_rate": 0.000232, "stop_loss_pct": 0.0236, "take_profit_pct": 0.0810,
        },
        "metrics": {"return": 35.74, "sharpe": 0.65, "max_dd": -19.70, "win_rate": 41.5},
    },
    "NEAR": {
        "symbol": "NEARUSDT",
        "exchange": "BINANCE",
        "params": {
            "hidden_size": 32, "num_layers": 2, "dropout": 0.3246, "nhead": 4,
            "window": 30, "max_features": 50, "batch_size": 32,
            "learning_rate": 0.000253, "stop_loss_pct": 0.0256, "take_profit_pct": 0.1111,
        },
        "metrics": {"return": 82.72, "sharpe": 0.96, "max_dd": -13.15, "win_rate": 36.0},
    },
    "AAVE": {
        "symbol": "AAVEUSDT",
        "exchange": "BINANCE",
        "params": {
            "hidden_size": 16, "num_layers": 2, "dropout": 0.4361, "nhead": 4,
            "window": 40, "max_features": 30, "batch_size": 64,
            "learning_rate": 0.000335, "stop_loss_pct": 0.0209, "take_profit_pct": 0.1196,
        },
        "metrics": {"return": 155.45, "sharpe": 1.34, "max_dd": -12.91, "win_rate": 43.4},
    },
}

# Generate TSLab script configs
output_dir = Path("tslab_scripts")
output_dir.mkdir(exist_ok=True)

for name, data in INSTRUMENTS.items():
    config = {
        "scriptName": f"NN_{name}",
        "description": f"NN Trading {name} - HybridEnsemble (Optuna optimized)",
        "symbol": data["symbol"],
        "exchange": data["exchange"],
        "interval": "1d",
        "model": {
            "type": "attention",
            "hidden_size": data["params"]["hidden_size"],
            "num_layers": data["params"]["num_layers"],
            "nhead": data["params"]["nhead"],
            "dropout": data["params"]["dropout"],
        },
        "data": {
            "window": data["params"]["window"],
            "max_features": data["params"]["max_features"],
            "batch_size": data["params"]["batch_size"],
            "learning_rate": data["params"]["learning_rate"],
        },
        "risk": {
            "stop_loss_pct": data["params"]["stop_loss_pct"],
            "take_profit_pct": data["params"]["take_profit_pct"],
            "trailing_stop_pct": 0.015,
        },
        "ensemble": {
            "n_models": 3,
            "use_xgboost": True,
            "use_catboost": True,
            "use_lightgbm": True,
            "use_random_forest": True,
        },
        "validation": {
            "method": "walk_forward",
            "n_folds": 5,
            "embargo": 7,
        },
        "metrics": data["metrics"],
    }

    filepath = output_dir / f"NN_{name}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print(f"Generated: {filepath}")

# Generate portfolio config
portfolio = {
    "name": "NN_Trading_Portfolio",
    "instruments": {},
    "total_expected_return": 0,
}

for name, data in INSTRUMENTS.items():
    weight = data["metrics"]["sharpe"] / sum(d["metrics"]["sharpe"] for d in INSTRUMENTS.values())
    portfolio["instruments"][name] = {
        "symbol": data["symbol"],
        "weight": round(weight, 4),
        "expected_return": data["metrics"]["return"],
        "sharpe": data["metrics"]["sharpe"],
    }
    portfolio["total_expected_return"] += data["metrics"]["return"] * weight

portfolio["total_expected_return"] = round(portfolio["total_expected_return"], 2)

with open(output_dir / "portfolio_config.json", "w", encoding="utf-8") as f:
    json.dump(portfolio, f, indent=2, ensure_ascii=False)
print(f"\nGenerated: {output_dir / 'portfolio_config.json'}")

# Summary
print("\n" + "=" * 60)
print("PORTFOLIO ALLOCATION (by Sharpe ratio)")
print("=" * 60)
for name, info in sorted(portfolio["instruments"].items(), key=lambda x: -x[1]["weight"]):
    print(f"  {name:6s}: {info['weight']*100:5.1f}% | Return: {info['expected_return']:+.2f}% | Sharpe: {info['sharpe']:.2f}")
print(f"\n  Expected portfolio return: {portfolio['total_expected_return']:+.2f}%")
