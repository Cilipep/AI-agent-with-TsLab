"""Portfolio allocation with correlation-based diversification."""
import json
import numpy as np
import pandas as pd
from pathlib import Path


def load_results():
    """Load results from walk-forward files."""
    results = []
    for fname in ["results/instruments_walkforward.json", "results/walk_forward_mtf_results.json"]:
        path = Path(fname)
        if path.exists():
            with open(path) as f:
                for inst in json.load(f).get("instruments", []):
                    if inst["instrument"] not in [r["instrument"] for r in results]:
                        results.append(inst)
    return results


def load_equity_curves():
    """Load equity curves for correlation calculation."""
    curves = {}
    for fname in ["results/equity_curves_3yr.json", "results/equity_curves_fixed.json"]:
        path = Path(fname)
        if path.exists():
            with open(path) as f:
                data = json.load(f)
                for k, v in data.items():
                    if k != "portfolio" and len(v) > 10:
                        curves[k] = np.array(v)
    return curves


def compute_correlation_matrix(curves):
    """Compute correlation matrix from equity curves."""
    names = sorted(curves.keys())
    n = len(names)
    if n < 2:
        return None, names

    # Align to shortest length
    min_len = min(len(curves[k]) for k in names)
    returns = []
    for name in names:
        eq = curves[name][:min_len]
        ret = np.diff(eq) / eq[:-1]
        returns.append(ret)

    returns = np.array(returns)  # (n_assets, n_periods)
    corr = np.corrcoef(returns)
    return corr, names


def diversify_portfolio(alloc, corr_matrix, corr_names, risk_aversion=0.5):
    """
    Adjust allocation based on correlation.
    Reduce weight of highly correlated assets, boost uncorrelated ones.
    """
    alloc_names = list(alloc.keys())
    n = len(alloc_names)
    if corr_matrix is None or n < 2:
        return alloc

    # Build correlation penalty for each asset
    penalties = {}
    for i, name_i in enumerate(alloc_names):
        if name_i not in corr_names:
            penalties[name_i] = 0
            continue
        idx_i = corr_names.index(name_i)
        avg_corr = 0
        count = 0
        for j, name_j in enumerate(alloc_names):
            if name_i == name_j or name_j not in corr_names:
                continue
            idx_j = corr_names.index(name_j)
            avg_corr += abs(corr_matrix[idx_i, idx_j])
            count += 1
        if count > 0:
            avg_corr /= count
        # Higher avg correlation → higher penalty
        penalties[name_i] = avg_corr * risk_aversion

    # Adjust weights: reduce by penalty, boost uncorrelated
    adjusted = {}
    total = 0
    for name, pct in alloc.items():
        penalty = penalties.get(name, 0)
        adj = pct * (1 - penalty)
        adjusted[name] = max(adj, 1.0)  # minimum 1%
        total += adjusted[name]

    # Normalize to 100%
    adjusted = {k: round(v / total * 100, 1) for k, v in adjusted.items()}
    return adjusted


def main():
    instruments = load_results()
    if not instruments:
        print("No results found.")
        return

    curves = load_equity_curves()
    corr_matrix, corr_names = compute_correlation_matrix(curves)

    # Base allocation (Sharpe-weighted)
    profitable = [i for i in instruments if i.get("sharpe", 0) > 0]
    if not profitable:
        alloc = {i["instrument"]: round(100 / len(instruments), 1) for i in instruments}
    else:
        sharpes = {i["instrument"]: max(i.get("sharpe", 0), 0.01) for i in profitable}
        total_sharpe = sum(sharpes.values())
        alloc = {}
        for name, sh in sharpes.items():
            raw = sh / total_sharpe
            alloc[name] = min(max(raw * 100, 5), 25)
        total = sum(alloc.values())
        alloc = {k: round(v / total * 100, 1) for k, v in alloc.items()}

    # Apply diversification
    diversified = diversify_portfolio(alloc, corr_matrix, corr_names)

    print("=" * 60)
    print("PORTFOLIO ALLOCATION (with diversification)")
    print("=" * 60)

    total_return = 0
    for name, pct in sorted(diversified.items(), key=lambda x: -x[1]):
        inst = next((i for i in instruments if i["instrument"] == name), None)
        ret = inst["total_return"] if inst else 0
        sh = inst["sharpe"] if inst else 0
        contrib = ret * pct / 100
        total_return += contrib
        print(f"  {name:8s} | {pct:5.1f}% | Return: {ret:+.2f}% | Sharpe: {sh:+.2f} | Contrib: {contrib:+.2f}%")

    print(f"\n  Portfolio Expected Return: {total_return:+.2f}%")
    print(f"  Instruments: {len( diversified)}")

    if corr_matrix is not None:
        print(f"\n  Correlation Matrix:")
        print(f"  {'':8s}", end="")
        for name in corr_names[:6]:
            print(f" {name:>6s}", end="")
        print()
        for i, name_i in enumerate(corr_names[:6]):
            print(f"  {name_i:8s}", end="")
            for j, name_j in enumerate(corr_names[:6]):
                print(f" {corr_matrix[i,j]:6.2f}", end="")
            print()

    with open("results/portfolio_allocation.json", "w") as f:
        json.dump({
            "allocation": diversified,
            "expected_return": round(total_return, 2),
            "correlation_available": corr_matrix is not None,
        }, f, indent=2)

    print(f"\nSaved to results/portfolio_allocation.json")


if __name__ == "__main__":
    main()
