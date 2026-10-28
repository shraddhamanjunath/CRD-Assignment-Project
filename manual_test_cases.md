# Manual Test Cases – Portfolio Rebalancer

**Precondition (all cases):** Rebalancer application is available; user is logged in with access to account ABC.
**Base data (unless stated):** Total assets $100,000; IBM 20/10 @150, MSFT 20/20 @90, ORCL 20/30 @220, AAPL 20/20 @450, HD 20/20 @70 (target%/current% @ unit price).

## Expected result for the assignment scenario

| Security | Variance | $ to adjust | Calculation | Output |
|---|---|---|---|---|
| IBM | -10 | +$10,000 | 10,000 / 150 = 66.67 | **BUY 66** |
| MSFT | 0 | $0 | – | **HOLD 0** |
| ORCL | +10 | -$10,000 | 10,000 / 220 = 45.45 | **SELL 45** |
| AAPL | 0 | $0 | – | **HOLD 0** |
| HD | 0 | $0 | – | **HOLD 0** |

Residual: IBM ends at $9,900 bought (≈$100 short), ORCL $9,900 sold (≈$100 left over) because only whole shares can trade.

## Functional – given scenario

| ID | Title | Steps | Expected result | Priority | Auto |
|---|---|---|---|---|---|
| TC-01 | Buy shares for underweight security | Load base data, run rebalance | IBM: BUY 66 | High | ✅ |
| TC-02 | No trade when variance is zero (MSFT) | Same | MSFT: HOLD 0 | High | ✅ |
| TC-03 | Sell shares for overweight security | Same | ORCL: SELL 45 | High | ✅ |
| TC-04 | No trade for AAPL | Same | AAPL: HOLD 0 | High | ✅ |
| TC-05 | No trade for HD | Same | HD: HOLD 0 | High | ✅ |
| TC-06 | Variance column correct | Same | IBM -10, ORCL +10, others 0 | High | ✅ |
| TC-07 | One output row per security, same order | Same | 5 rows: IBM, MSFT, ORCL, AAPL, HD | Medium | ✅ |
| TC-08 | No over-trading | Same | Shares × price ≤ required $ for every security | High | ✅ |

## Calculation & boundary

| ID | Title | Input change | Expected result | Priority | Auto |
|---|---|---|---|---|---|
| TC-09 | Already balanced account | All current = target | All HOLD 0 | High | ✅ |
| TC-10 | Exact whole-share result | A 60/50 @100, B 40/50 @100 | A BUY 100, B SELL 100 | Medium | ✅ |
| TC-11 | Price larger than adjustment | A 51/50 @2000, B 49/50 @2000 | Both 0 (can't trade a partial share) | Medium | ✅ |
| TC-12 | Decimal percentages | A 33.33/30 @10, B 66.67/70 @10 | A BUY 333, B SELL 333 | Medium | ✅ |
| TC-13 | Full liquidation | A 0/20 @100, B 100/80 @100 | A SELL 200, B BUY 200 | Medium | ✅ |
| TC-14 | Different total assets | Total $1,000,000 | IBM BUY 666, ORCL SELL 454 | Medium | ✅ |
| TC-15 | Single security | A 100/100 @50 | HOLD 0 | Low | ✅ |

## Negative / validation

| ID | Title | Input | Expected result | Priority | Auto |
|---|---|---|---|---|---|
| TC-16 | Invalid total assets | 0, negative, blank | Error, no trades produced | High | ✅ |
| TC-17 | Invalid unit price | 0, negative, blank | Error naming the security | High | ✅ |
| TC-18 | Target % ≠ 100 | IBM target 25 | Error "Target % must total 100" | High | ✅ |
| TC-19 | Current % ≠ 100 | IBM current 15 | Error "Current % must total 100" | High | ✅ |
| TC-20 | % out of range | -5 or 101 | Error | Medium | ✅ |
| TC-21 | Empty account | No securities | Error | Medium | ✅ |
| TC-22 | Duplicate security | IBM twice | Error "Duplicate security" | Medium | ✅ |
| TC-23 | Blank symbol | Symbol " " | Error | Low | ✅ |

## Manual-only (not automated – UI / non-functional)

| ID | Title | Steps | Expected result | Priority |
|---|---|---|---|---|
| TC-24 | Output display | Run rebalance in UI | Shares shown as whole numbers with clear BUY/SELL/HOLD labels | Medium |
| TC-25 | Non-numeric input | Type "abc" in price field | Field-level validation message, run blocked | Medium |
| TC-26 | Re-run is idempotent | Run twice with same data | Identical output both times | Medium |
| TC-27 | Price change refresh | Change IBM price to 100, re-run | IBM BUY 100 | Medium |
| TC-28 | Audit / export | Export trade list | Exported values match screen | Low |
| TC-29 | Permissions | Read-only user opens account | Can view, cannot execute trades | Medium |
