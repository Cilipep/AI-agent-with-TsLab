# Moving M15 Strategy — Final Summary
## Tested Instruments & Best Configurations

### Strategy Rules
- Main: SMMA(X) Close vs SMMA(X) Close shifted +X bars
- Sub: Williams %R(Y), SMMA(8) of WR, SMMA(21) of WR
- Entry: MA crossover + WR crossover WR8 + WR above/below WR21

---

### Performance Ranking

| Rank | Symbol | SL% | TP% | SMMA | WR | Trades | WinRate | Return% | MaxDD% |
|------|--------|-----|-----|------|-----|--------|---------|---------|--------|
| 1 | SOL | 3.0 | 8.0 | 7 | 10 | 18 | 50.0 | +49.84 | 9.4 |
| 2 | LINK | 3.0 | 8.0 | 5 | 10 | 37 | 35.1 | +30.05 | 18.5 |
| 3 | INJ | 3.0 | 6.0 | 7 | 10 | 21 | 38.1 | +10.43 | 11.7 |
| 4 | ETH | 3.0 | 8.0 | 7 | 10 | 20 | 35.0 | +8.38 | 20.3 |
| 5 | DOGE | 3.0 | 6.0 | 7 | 10 | 12 | 41.7 | +5.57 | 10.1 |
| 6 | FET | 3.0 | 6.0 | 7 | 10 | 27 | 33.3 | +2.58 | 13.3 |
| 7 | WIF | 3.0 | 6.0 | 7 | 10 | 25 | 36.0 | -0.84 | 10.1 |
| 8 | AVAX | 3.0 | 6.0 | 7 | 10 | 20 | 35.0 | -2.76 | 20.2 |
| 9 | BTC | 3.0 | 8.0 | 7 | 10 | 19 | 5.3 | -21.81 | 24.7 |
| 10 | BONK | 3.0 | 6.0 | 7 | 10 | 25 | 28.0 | -16.94 | 20.5 |

---

### Key Findings

1. SOL is the clear winner — 50% win rate with 1:2.7 R:R yields nearly 50% return
2. LINK requires more trades (37) to achieve 30% return, lower win rate at 35%
3. SMMA period 7 consistently outperforms period 5 across most instruments
4. TP=8% works better than TP=6% for higher-volatility assets (SOL, LINK, ETH)
5. BTC and meme tokens (BONK) should be avoided — strategy fails in those conditions

### Recommended Portfolio Allocation
- Primary: SOL (highest Sharpe, lowest MDD)
- Secondary: LINK, INJ
- Tertiary: ETH, DOGE, FET
- Avoid: BTC, BONK, WIF, AVAX

---

### Files Generated
- tmp/moving_m15_opt_sol.csv — SOL optimization results
- tmp/moving_m15_opt_link.csv — LINK optimization results
- tmp/moving_m15_opt_doge.csv — DOGE optimization results
- tmp/moving_m15_sol_trades.csv — SOL detailed trade log
- tmp/moving_m15_sol_equity.csv — SOL equity curve
- tmp/moving_m15_doge_trades.csv — DOGE detailed trade log
- tmp/moving_m15_multi.csv — multi-instrument comparison
