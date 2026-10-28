"""
Portfolio rebalancer - application under test.

For each security:
    variance %        = current % - target %
    dollar adjustment = -(variance % / 100) * total assets
    shares            = dollar adjustment / unit price, truncated toward zero
    positive shares = BUY, negative shares = SELL, 0 = HOLD

Assumptions are listed in README.md.
"""
from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN


@dataclass
class Holding:
    symbol: str
    target_pct: float
    current_pct: float
    unit_price: float


@dataclass
class Trade:
    symbol: str
    variance_pct: float
    shares: int          # signed: + buy, - sell
    action: str          # BUY / SELL / HOLD


class ValidationError(ValueError):
    pass


def _validate(total_assets, holdings):
    if total_assets is None or total_assets <= 0:
        raise ValidationError("Total assets must be greater than zero")
    if not holdings:
        raise ValidationError("Account must hold at least one security")

    symbols = [h.symbol for h in holdings]
    if len(symbols) != len(set(symbols)):
        raise ValidationError("Duplicate security in account")

    for h in holdings:
        if not h.symbol or not str(h.symbol).strip():
            raise ValidationError("Security symbol is required")
        if h.unit_price is None or h.unit_price <= 0:
            raise ValidationError(f"{h.symbol}: unit price must be greater than zero")
        for name, val in (("target", h.target_pct), ("current", h.current_pct)):
            if val is None or val < 0 or val > 100:
                raise ValidationError(f"{h.symbol}: {name} % must be between 0 and 100")

    if round(sum(h.target_pct for h in holdings), 6) != 100:
        raise ValidationError("Target % must total 100")
    if round(sum(h.current_pct for h in holdings), 6) != 100:
        raise ValidationError("Current % must total 100")


def rebalance(total_assets, holdings):
    """Return a list of Trade objects, one per holding, in input order."""
    _validate(total_assets, holdings)

    trades = []
    for h in holdings:
        variance = Decimal(str(h.current_pct)) - Decimal(str(h.target_pct))
        dollars = -(variance / Decimal(100)) * Decimal(str(total_assets))
        raw_shares = dollars / Decimal(str(h.unit_price))
        # Whole shares only, truncate toward zero so we never over-buy or over-sell
        shares = int(raw_shares.copy_abs().quantize(Decimal(1), rounding=ROUND_DOWN))
        if raw_shares < 0:
            shares = -shares

        action = "BUY" if shares > 0 else "SELL" if shares < 0 else "HOLD"
        trades.append(Trade(h.symbol, float(variance), shares, action))
    return trades


if __name__ == "__main__":
    account = [
        Holding("IBM", 20, 10, 150),
        Holding("MSFT", 20, 20, 90),
        Holding("ORCL", 20, 30, 220),
        Holding("AAPL", 20, 20, 450),
        Holding("HD", 20, 20, 70),
    ]
    print(f"{'Security':<8} {'Variance':>8} {'Action':>6} {'Shares':>6}")
    for t in rebalance(100_000, account):
        print(f"{t.symbol:<8} {t.variance_pct:>8.1f} {t.action:>6} {abs(t.shares):>6}")
