"""
Multi-parameter optimization for TSLab strategies.
Grid search, random search, and Bayesian optimization.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Callable, Optional
from itertools import product
import json
from datetime import datetime
import requests


class TSLabOptimizer:
    """Optimize TSLab script parameters via API."""
    
    def __init__(self, base_url: str = "http://localhost:5000/api"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_parameters(self, script_name: str) -> List[Dict]:
        """Get optimization candidates for a script."""
        response = self.session.get(f"{self.base_url}/scripts/{script_name}/parameters")
        data = response.json()
        
        if data.get('success'):
            return data['data']['optimizationCandidates']
        return []
    
    def set_optimization_ranges(self, script_name: str, ranges: List[Dict]) -> bool:
        """Set optimization ranges via ops."""
        ops_body = {"ops": ranges}
        response = self.session.post(
            f"{self.base_url}/scripts/{script_name}/ops",
            json=ops_body
        )
        return response.json().get('success', False)
    
    def start_optimization(self, script_name: str, param_ids: List[str], 
                          iterations: int = 100, metric: str = "NetProfit") -> Optional[str]:
        """Start optimization and return job ID."""
        body = {
            "iterations": iterations,
            "metric": metric,
            "selectedParameterIds": param_ids
        }
        
        response = self.session.post(
            f"{self.base_url}/scripts/{script_name}/optimization/start",
            json=body
        )
        
        data = response.json()
        if data.get('success'):
            return data['data']['jobId']
        return None
    
    def get_optimization_status(self, job_id: str) -> Dict:
        """Get optimization status."""
        response = self.session.get(f"{self.base_url}/optimizations/{job_id}")
        return response.json()
    
    def get_best_result(self, job_id: str, metric: str = "NetProfit", rank: int = 1) -> Optional[Dict]:
        """Get best optimization result."""
        response = self.session.get(
            f"{self.base_url}/optimizations/{job_id}/best",
            params={"metric": metric, "rank": rank}
        )
        data = response.json()
        
        if data.get('success'):
            return data['data']
        return None
    
    def apply_best(self, job_id: str, metric: str = "NetProfit", rank: int = 1) -> bool:
        """Apply best optimization result."""
        response = self.session.post(
            f"{self.base_url}/optimizations/{job_id}/apply",
            params={"metric": metric, "rank": rank}
        )
        return response.json().get('success', False)


def grid_search(optimizer: TSLabOptimizer, script_name: str,
                param_grids: Dict[str, List], metric: str = "NetProfit",
                max_iterations: int = 100) -> List[Dict]:
    """
    Perform grid search optimization.
    
    Args:
        optimizer: TSLabOptimizer instance
        script_name: Name of the script to optimize
        param_grids: Dictionary of parameter_name -> list of values
        metric: Metric to optimize
        max_iterations: Max iterations per run
    
    Returns:
        List of results with parameters and metrics
    """
    # Generate all combinations
    param_names = list(param_grids.keys())
    param_values = list(param_grids.values())
    combinations = list(product(*param_values))
    
    print(f"Grid search: {len(combinations)} combinations")
    
    results = []
    
    for i, combo in enumerate(combinations):
        print(f"\nCombination {i+1}/{len(combinations)}")
        
        # Create parameter values
        param_values_dict = dict(zip(param_names, combo))
        
        # Set optimization ranges
        ranges = []
        for name, value in param_values_dict.items():
            ranges.append({
                "op": "SetOptimizationRange",
                "blockId": name.split("_")[0],  # Assuming format: blockId_paramName
                "paramInvariantName": "_".join(name.split("_")[1:]),
                "optimDataType": "OptimData",
                "value": value,
                "min": value,
                "max": value,
                "step": 1
            })
        
        optimizer.set_optimization_ranges(script_name, ranges)
        
        # Start optimization
        job_id = optimizer.start_optimization(script_name, list(param_values_dict.keys()), 
                                              iterations=10, metric=metric)
        
        if job_id:
            # Wait for completion
            import time
            for _ in range(60):  # Max 5 minutes
                status = optimizer.get_optimization_status(job_id)
                if status.get('data', {}).get('status') == 'Completed':
                    break
                time.sleep(5)
            
            # Get best result
            best = optimizer.get_best_result(job_id, metric)
            
            if best:
                result = {
                    'params': param_values_dict,
                    'metric_value': best.get(metric, 0),
                    'net_profit': best.get('netProfit', 0),
                    'max_drawdown': best.get('maxDrawdownPct', 0),
                    'profit_factor': best.get('profitFactor', 0),
                    'all_trades': best.get('allTrades', 0),
                }
                results.append(result)
                print(f"  Result: {metric} = {result['metric_value']}")
    
    return results


def random_search(optimizer: TSLabOptimizer, script_name: str,
                  param_ranges: Dict[str, Tuple[float, float]], 
                  n_iter: int = 100, metric: str = "NetProfit") -> List[Dict]:
    """
    Perform random search optimization.
    
    Args:
        optimizer: TSLabOptimizer instance
        script_name: Name of the script to optimize
        param_ranges: Dictionary of parameter_name -> (min, max) tuples
        n_iter: Number of random combinations to try
        metric: Metric to optimize
    
    Returns:
        List of results
    """
    print(f"Random search: {n_iter} iterations")
    
    results = []
    
    for i in range(n_iter):
        print(f"\nIteration {i+1}/{n_iter}")
        
        # Generate random parameters
        param_values = {}
        for name, (min_val, max_val) in param_ranges.items():
            param_values[name] = np.random.uniform(min_val, max_val)
        
        # Set optimization ranges
        ranges = []
        for name, value in param_values.items():
            ranges.append({
                "op": "SetOptimizationRange",
                "blockId": name.split("_")[0],
                "paramInvariantName": "_".join(name.split("_")[1:]),
                "optimDataType": "OptimData",
                "value": value,
                "min": min_val,
                "max": max_val,
                "step": (max_val - min_val) / 10
            })
        
        optimizer.set_optimization_ranges(script_name, ranges)
        
        # Start optimization
        job_id = optimizer.start_optimization(script_name, list(param_values.keys()),
                                              iterations=10, metric=metric)
        
        if job_id:
            import time
            for _ in range(60):
                status = optimizer.get_optimization_status(job_id)
                if status.get('data', {}).get('status') == 'Completed':
                    break
                time.sleep(5)
            
            best = optimizer.get_best_result(job_id, metric)
            
            if best:
                result = {
                    'params': param_values,
                    'metric_value': best.get(metric, 0),
                    'net_profit': best.get('netProfit', 0),
                    'max_drawdown': best.get('maxDrawdownPct', 0),
                    'profit_factor': best.get('profitFactor', 0),
                }
                results.append(result)
                print(f"  Result: {metric} = {result['metric_value']}")
    
    return results


def analyze_results(results: List[Dict], metric: str = "net_profit") -> Dict:
    """
    Analyze optimization results.
    
    Args:
        results: List of result dictionaries
        metric: Metric to analyze
    
    Returns:
        Analysis dictionary
    """
    if not results:
        return {"error": "No results to analyze"}
    
    values = [r.get(metric, 0) for r in results]
    
    analysis = {
        'count': len(results),
        'mean': np.mean(values),
        'std': np.std(values),
        'min': np.min(values),
        'max': np.max(values),
        'median': np.median(values),
        'positive_count': sum(1 for v in values if v > 0),
        'positive_pct': sum(1 for v in values if v > 0) / len(values) * 100,
    }
    
    # Find best result
    best_idx = np.argmax(values)
    analysis['best_result'] = results[best_idx]
    analysis['best_value'] = values[best_idx]
    
    # Parameter importance (simplified)
    if results and 'params' in results[0]:
        param_importance = {}
        for param_name in results[0]['params'].keys():
            param_values = [r['params'].get(param_name, 0) for r in results]
            correlation = np.corrcoef(param_values, values)[0, 1]
            param_importance[param_name] = correlation
        
        analysis['param_importance'] = param_importance
    
    return analysis


def save_results(results: List[Dict], filename: str):
    """Save results to JSON file."""
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)


def main():
    """Example usage."""
    # Initialize optimizer
    optimizer = TSLabOptimizer()
    
    # Example: Grid search on RSI parameters
    script_name = "RSICCIBot"
    
    param_grids = {
        "RSI_Period": [10, 14, 20],
        "RSI_Overbought": [65, 70, 75],
        "RSI_Oversold": [25, 30, 35],
        "CCI_Period": [14, 20, 28],
    }
    
    print("Starting grid search...")
    results = grid_search(optimizer, script_name, param_grids)
    
    # Analyze results
    analysis = analyze_results(results)
    
    print("\n=== Optimization Results ===")
    print(f"Total runs: {analysis['count']}")
    print(f"Mean profit: ${analysis['mean']:.2f}")
    print(f"Best profit: ${analysis['best_value']:.2f}")
    print(f"Positive runs: {analysis['positive_count']}/{analysis['count']} ({analysis['positive_pct']:.1f}%)")
    
    if 'param_importance' in analysis:
        print("\nParameter Importance:")
        for param, importance in analysis['param_importance'].items():
            print(f"  {param}: {importance:.3f}")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_results(results, f"optimization_results_{timestamp}.json")
    print(f"\nResults saved to optimization_results_{timestamp}.json")


if __name__ == "__main__":
    main()
