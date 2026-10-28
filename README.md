# CRD Technical Assessment – Portfolio Rebalancer Tests

Manual and automated tests for a portfolio rebalancing application (Account ABC, $100,000).

## Answer: what gets account ABC to zero target variance?

| Security | Variance | Action |
|---|---|---|
| IBM | -10% | **Buy 66 shares** ($10,000 / $150 = 66.67) |
| MSFT | 0% | Hold |
| ORCL | +10% | **Sell 45 shares** ($10,000 / $220 = 45.45) |
| AAPL | 0% | Hold |
| HD | 0% | Hold |

Formula per security: `shares = ((target% − current%) / 100 × total assets) / unit price`, truncated to a whole share.

Exact zero variance isn't reachable with whole shares; the remaining gap is about $100 (≈0.1%) on IBM and ORCL.

## Assumptions

1. Only whole shares can be traded (no fractional shares).
2. Share counts are **truncated toward zero** (66.67 → 66), so the app never buys or sells more than the target requires. Rounding to nearest (67 / 45) would be a valid alternative, but it would overshoot IBM.
3. Unit prices are fixed for the run; no commissions, fees, taxes or cash balance.
4. Total assets stay at $100,000 (the sell proceeds fund the buy).
5. Target % and current % must each total 100; inputs outside 0–100 are invalid.
6. Since the actual application wasn't provided, `src/rebalancer.py` is a minimal reference implementation built so the tests have something to run against.

## Structure

```
src/rebalancer.py          reference implementation (system under test)
tests/test_rebalancer.py   28 automated pytest cases
docs/manual_test_cases.md  29 manual test cases (TC-01..TC-29) with traceability
```

## Run

```bash
pip install pytest
python -m pytest -v
python -m src.rebalancer     # prints the trade list for account ABC
```

## Known limitations / not covered

- UI, export, and permission tests (TC-24 to TC-29) are manual only.
- No performance or concurrency testing.
- Real market data, partial fills and order execution are out of scope.
