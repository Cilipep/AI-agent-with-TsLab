"""
Report generation for TSLab analytics.
Generates HTML/JSON reports with advanced metrics and visualizations.
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

from .advanced_metrics import calculate_all_metrics, max_drawdown, sharpe_ratio
from .correlation import correlation_matrix, hierarchical_clustering, diversification_ratio
from .regime import threshold_regime_detection, regime_statistics, regime_transitions


class AnalyticsReport:
    """Generate comprehensive analytics reports."""
    
    def __init__(self, output_dir: str = "./reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_strategy_report(self, 
                                 returns: np.ndarray,
                                 trades: Optional[pd.DataFrame] = None,
                                 strategy_name: str = "Strategy",
                                 period: str = "Daily") -> Dict[str, Any]:
        """
        Generate comprehensive strategy report.
        
        Args:
            returns: Array of periodic returns
            trades: Optional DataFrame with trade details
            strategy_name: Name of the strategy
            period: Return period (Daily, Hourly, etc.)
        
        Returns:
            Report dictionary
        """
        metrics = calculate_all_metrics(returns, trades)
        
        report = {
            'strategy_name': strategy_name,
            'period': period,
            'generated_at': datetime.now().isoformat(),
            'metrics': metrics,
            'summary': self._generate_summary(metrics),
            'risk_metrics': self._extract_risk_metrics(metrics),
            'performance_metrics': self._extract_performance_metrics(metrics),
        }
        
        return report
    
    def generate_portfolio_report(self, 
                                  returns_df: pd.DataFrame,
                                  weights: Optional[np.ndarray] = None,
                                  portfolio_name: str = "Portfolio") -> Dict[str, Any]:
        """
        Generate portfolio-level report with correlation analysis.
        
        Args:
            returns_df: DataFrame with instrument returns
            weights: Portfolio weights
            portfolio_name: Name of the portfolio
        
        Returns:
            Portfolio report dictionary
        """
        # Portfolio returns
        if weights is None:
            weights = np.ones(returns_df.shape[1]) / returns_df.shape[1]
        
        portfolio_returns = (returns_df * weights).sum(axis=1).values
        
        # Individual instrument metrics
        instrument_metrics = {}
        for col in returns_df.columns:
            instrument_metrics[col] = calculate_all_metrics(returns_df[col].values)
        
        # Correlation analysis
        corr_matrix = correlation_matrix(returns_df)
        
        # Diversification ratio
        div_ratio = diversification_ratio(returns_df, weights)
        
        report = {
            'portfolio_name': portfolio_name,
            'generated_at': datetime.now().isoformat(),
            'n_instruments': returns_df.shape[1],
            'instruments': returns_df.columns.tolist(),
            'weights': weights.tolist(),
            'portfolio_metrics': calculate_all_metrics(portfolio_returns),
            'instrument_metrics': instrument_metrics,
            'correlation_matrix': corr_matrix.to_dict(),
            'diversification_ratio': div_ratio,
            'summary': self._generate_portfolio_summary(
                calculate_all_metrics(portfolio_returns),
                instrument_metrics,
                div_ratio
            ),
        }
        
        return report
    
    def generate_regime_report(self, 
                               prices: pd.Series,
                               strategy_name: str = "Strategy") -> Dict[str, Any]:
        """
        Generate regime analysis report.
        
        Args:
            prices: Price series
            strategy_name: Name of the strategy
        
        Returns:
            Regime report dictionary
        """
        regime_result = threshold_regime_detection(prices)
        
        if regime_result.empty:
            return {'error': 'Insufficient data for regime detection'}
        
        stats = regime_statistics(regime_result)
        transitions = regime_transitions(regime_result)
        
        report = {
            'strategy_name': strategy_name,
            'generated_at': datetime.now().isoformat(),
            'n_regimes': len(stats),
            'regime_statistics': stats.to_dict('records'),
            'transition_probabilities': transitions.to_dict(),
            'regime_distribution': regime_result['regime'].value_counts().to_dict(),
        }
        
        return report
    
    def _generate_summary(self, metrics: Dict) -> str:
        """Generate human-readable summary from metrics."""
        summary_parts = []
        
        # Performance
        if metrics['total_return'] > 0:
            summary_parts.append(f"Positive total return of {metrics['total_return']:.2%}")
        else:
            summary_parts.append(f"Negative total return of {metrics['total_return']:.2%}")
        
        # Risk-adjusted
        if metrics['sharpe_ratio'] > 1:
            summary_parts.append("Strong risk-adjusted performance (Sharpe > 1)")
        elif metrics['sharpe_ratio'] > 0:
            summary_parts.append("Moderate risk-adjusted performance")
        else:
            summary_parts.append("Poor risk-adjusted performance")
        
        # Drawdown
        if metrics['max_drawdown'] < 0.1:
            summary_parts.append("Low maximum drawdown (< 10%)")
        elif metrics['max_drawdown'] < 0.2:
            summary_parts.append("Moderate maximum drawdown (10-20%)")
        else:
            summary_parts.append(f"High maximum drawdown ({metrics['max_drawdown']:.2%})")
        
        return ". ".join(summary_parts) + "."
    
    def _generate_portfolio_summary(self, 
                                    portfolio_metrics: Dict,
                                    instrument_metrics: Dict,
                                    div_ratio: float) -> str:
        """Generate portfolio summary."""
        summary_parts = []
        
        # Portfolio performance
        summary_parts.append(
            f"Portfolio returned {portfolio_metrics['total_return']:.2%} "
            f"with Sharpe ratio {portfolio_metrics['sharpe_ratio']:.2f}"
        )
        
        # Diversification
        if div_ratio > 1.2:
            summary_parts.append(
                f"Good diversification (ratio: {div_ratio:.2f})"
            )
        else:
            summary_parts.append(
                f"Limited diversification benefit (ratio: {div_ratio:.2f})"
            )
        
        # Best/worst instrument
        best_inst = max(instrument_metrics.items(), key=lambda x: x[1]['total_return'])
        worst_inst = min(instrument_metrics.items(), key=lambda x: x[1]['total_return'])
        
        summary_parts.append(
            f"Best performer: {best_inst[0]} ({best_inst[1]['total_return']:.2%}), "
            f"Worst: {worst_inst[0]} ({worst_inst[1]['total_return']:.2%})"
        )
        
        return ". ".join(summary_parts) + "."
    
    def _extract_risk_metrics(self, metrics: Dict) -> Dict:
        """Extract risk-related metrics."""
        return {
            'max_drawdown': metrics['max_drawdown'],
            'max_drawdown_duration': metrics['max_drawdown_duration'],
            'std_return': metrics['std_return'],
            'sortino_ratio': metrics['sortino_ratio'],
            'calmar_ratio': metrics['calmar_ratio'],
        }
    
    def _extract_performance_metrics(self, metrics: Dict) -> Dict:
        """Extract performance-related metrics."""
        return {
            'total_return': metrics['total_return'],
            'avg_return': metrics['avg_return'],
            'sharpe_ratio': metrics['sharpe_ratio'],
            'omega_ratio': metrics['omega_ratio'],
            'win_rate': metrics['win_rate'],
            'profit_factor': metrics['profit_factor'],
        }
    
    def save_json(self, report: Dict, filename: str) -> str:
        """Save report as JSON."""
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        return str(filepath)
    
    def save_html(self, report: Dict, filename: str) -> str:
        """Save report as HTML."""
        filepath = self.output_dir / filename
        
        html_content = self._generate_html(report)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(filepath)
    
    def _generate_html(self, report: Dict) -> str:
        """Generate HTML content from report dictionary."""
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{report.get('strategy_name', 'Strategy')} Analytics Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .metric-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .metric-card {{ background: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 4px solid #007bff; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #333; }}
        .metric-label {{ color: #666; font-size: 14px; }}
        .positive {{ color: #28a745; }}
        .negative {{ color: #dc3545; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f8f9fa; font-weight: bold; }}
        tr:hover {{ background: #f5f5f5; }}
        .summary {{ background: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .timestamp {{ color: #999; font-size: 12px; text-align: right; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{report.get('strategy_name', 'Strategy')} Analytics Report</h1>
        <p class="timestamp">Generated: {report.get('generated_at', 'N/A')}</p>
        
        <div class="summary">
            <strong>Summary:</strong> {report.get('summary', 'N/A')}
        </div>
"""
        
        # Add metrics sections
        if 'metrics' in report:
            metrics = report['metrics']
            html += self._html_metrics_section("Key Metrics", metrics)
        
        if 'risk_metrics' in report:
            html += self._html_metrics_section("Risk Metrics", report['risk_metrics'])
        
        if 'performance_metrics' in report:
            html += self._html_metrics_section("Performance Metrics", report['performance_metrics'])
        
        # Portfolio-specific sections
        if 'instrument_metrics' in report:
            html += self._html_instrument_table(report['instrument_metrics'])
        
        if 'correlation_matrix' in report:
            html += self._html_correlation_table(report['correlation_matrix'])
        
        if 'diversification_ratio' in report:
            html += f"""
        <h2>Diversification</h2>
        <div class="metric-card">
            <div class="metric-value">{report['diversification_ratio']:.2f}</div>
            <div class="metric-label">Diversification Ratio</div>
        </div>
"""
        
        html += """
    </div>
</body>
</html>
"""
        return html
    
    def _html_metrics_section(self, title: str, metrics: Dict) -> str:
        """Generate HTML for a metrics section."""
        html = f"<h2>{title}</h2><div class='metric-grid'>"
        
        for key, value in metrics.items():
            if isinstance(value, float):
                if 'ratio' in key or 'return' in key or 'rate' in key or 'drawdown' in key:
                    display_value = f"{value:.2%}" if abs(value) < 10 else f"{value:.2f}"
                else:
                    display_value = f"{value:.2f}"
                
                css_class = "positive" if value > 0 else "negative" if value < 0 else ""
                html += f"""
        <div class="metric-card">
            <div class="metric-value {css_class}">{display_value}</div>
            <div class="metric-label">{key.replace('_', ' ').title()}</div>
        </div>"""
        
        html += "</div>"
        return html
    
    def _html_instrument_table(self, instrument_metrics: Dict) -> str:
        """Generate HTML table for instrument metrics."""
        html = """
        <h2>Instrument Metrics</h2>
        <table>
            <tr>
                <th>Instrument</th>
                <th>Total Return</th>
                <th>Sharpe Ratio</th>
                <th>Max Drawdown</th>
                <th>Win Rate</th>
            </tr>
"""
        
        for inst, metrics in instrument_metrics.items():
            html += f"""
            <tr>
                <td><strong>{inst}</strong></td>
                <td class="{'positive' if metrics['total_return'] > 0 else 'negative'}">{metrics['total_return']:.2%}</td>
                <td>{metrics['sharpe_ratio']:.2f}</td>
                <td>{metrics['max_drawdown']:.2%}</td>
                <td>{metrics['win_rate']:.2%}</td>
            </tr>
"""
        
        html += "</table>"
        return html
    
    def _html_correlation_table(self, corr_matrix: Dict) -> str:
        """Generate HTML table for correlation matrix."""
        if not corr_matrix:
            return ""
        
        instruments = list(corr_matrix.keys())
        
        html = """
        <h2>Correlation Matrix</h2>
        <table>
            <tr>
                <th></th>
"""
        
        for inst in instruments:
            html += f"                <th>{inst}</th>\n"
        
        html += "            </tr>\n"
        
        for inst1 in instruments:
            html += f"            <tr><td><strong>{inst1}</strong></td>"
            for inst2 in instruments:
                corr_value = corr_matrix[inst1].get(inst2, 0)
                html += f"<td>{corr_value:.2f}</td>"
            html += "</tr>\n"
        
        html += "</table>"
        return html


def main():
    """Example usage of the report generator."""
    np.random.seed(42)
    
    # Generate sample data
    n_days = 252
    instruments = ['BTC', 'ETH', 'SOL', 'DOGE', 'ADA']
    
    returns_data = {}
    for inst in instruments:
        returns_data[inst] = np.random.normal(0.001, 0.03, n_days)
    
    returns_df = pd.DataFrame(returns_data)
    
    # Create report generator
    report_gen = AnalyticsReport(output_dir="./reports")
    
    # Strategy report
    portfolio_returns = returns_df.mean(axis=1).values
    strategy_report = report_gen.generate_strategy_report(
        portfolio_returns,
        strategy_name="Multi-Coin Portfolio"
    )
    
    # Save strategy report
    report_gen.save_json(strategy_report, "strategy_report.json")
    report_gen.save_html(strategy_report, "strategy_report.html")
    
    print("Strategy report generated!")
    
    # Portfolio report
    portfolio_report = report_gen.generate_portfolio_report(returns_df)
    report_gen.save_json(portfolio_report, "portfolio_report.json")
    report_gen.save_html(portfolio_report, "portfolio_report.html")
    
    print("Portfolio report generated!")
    
    # Regime report
    prices = 100 * np.cumprod(1 + portfolio_returns)
    prices_series = pd.Series(prices, index=pd.date_range('2024-01-01', periods=n_days))
    
    regime_report = report_gen.generate_regime_report(prices_series, "Multi-Coin Strategy")
    report_gen.save_json(regime_report, "regime_report.json")
    report_gen.save_html(regime_report, "regime_report.html")
    
    print("Regime report generated!")


if __name__ == "__main__":
    main()
