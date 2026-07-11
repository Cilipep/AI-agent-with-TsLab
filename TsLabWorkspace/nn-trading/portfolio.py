"""Portfolio allocation based on walk-forward results."""
import json
import numpy as np
from pathlib import Path


def load_results():
    # Load from instruments walkforward (10 instruments)
    path1 = Path("results/instruments_walkforward.json")
    # Load from mtf results (BTC, ETH, SOL)
    path2 = Path("results/walk_forward_mtf_results.json")

    results = []
    if path1.exists():
        with open(path1) as f:
            results.extend(json.load(f).get("instruments", []))
    if path2.exists():
        with open(path2) as f:
            for inst in json.load(f).get("instruments", []):
                if inst["instrument"] not in [r["instrument"] for r in results]:
                    results.append(inst)
    return results


def allocate_portfolio(instruments, max_alloc=0.25, min_alloc=0.05):
    """Allocate capital proportional to Sharpe ratio."""
    profitable = [i for i in instruments if i.get("sharpe", 0) > 0]
    if not profitable:
        # Equal weight if no profitable instruments
        n = len(instruments)
        return {i["instrument"]: round(100/n, 1) for i in instruments}

    sharpes = {i["instrument"]: max(i.get("sharpe", 0), 0.01) for i in profitable}
    total_sharpe = sum(sharpes.values())

    alloc = {}
    for name, sh in sharpes.items():
        raw = sh / total_sharpe
        alloc[name] = min(max(raw * 100, min_alloc * 100), max_alloc * 100)

    # Normalize to 100%
    total = sum(alloc.values())
    alloc = {k: round(v / total * 100, 1) for k, v in alloc.items()}

    return alloc


def main():
    instruments = load_results()
    if not instruments:
        print("No results found. Run walk_forward first.")
        return

    alloc = allocate_portfolio(instruments)

    print("=" * 60)
    print("PORTFOLIO ALLOCATION")
    print("=" * 60)

    total_return = 0
    for name, pct in sorted(alloc.items(), key=lambda x: -x[1]):
        inst = next((i for i in instruments if i["instrument"] == name), None)
        ret = inst["total_return"] if inst else 0
        sh = inst["sharpe"] if inst else 0
        contrib = ret * pct / 100
        total_return += contrib
        print(f"  {name:8s} | {pct:5.1f}% | Return: {ret:+.2f}% | Sharpe: {sh:+.2f} | Contrib: {contrib:+.2f}%")

    print(f"\n  Portfolio Expected Return: {total_return:+.2f}%")
    print(f"  Instruments: {len(alloc)}")

    with open("results/portfolio_allocation.json", "w") as f:
        json.dump({"allocation": alloc, "expected_return": round(total_return, 2)}, f, indent=2)

    print(f"\nSaved to results/portfolio_allocation.json")


if __name__ == "__main__":
    main()
