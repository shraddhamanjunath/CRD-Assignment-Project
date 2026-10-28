"""Automated tests for the rebalancer (pytest). Test IDs map to docs/manual_test_cases.md."""
import pytest

from src.rebalancer import Holding, ValidationError, rebalance


def given_account():
    """Exact data from the assignment."""
    return [
        Holding("IBM", 20, 10, 150),
        Holding("MSFT", 20, 20, 90),
        Holding("ORCL", 20, 30, 220),
        Holding("AAPL", 20, 20, 450),
        Holding("HD", 20, 20, 70),
    ]


def by_symbol(trades):
    return {t.symbol: t for t in trades}


# ---------- TC-01..TC-05: the scenario in the assignment ----------

@pytest.mark.parametrize(
    "symbol, expected_shares, expected_action",
    [
        ("IBM", 66, "BUY"),     # $10,000 / $150 = 66.67 -> 66
        ("MSFT", 0, "HOLD"),
        ("ORCL", -45, "SELL"),  # $10,000 / $220 = 45.45 -> 45
        ("AAPL", 0, "HOLD"),
        ("HD", 0, "HOLD"),
    ],
)
def test_given_scenario_shares_per_security(symbol, expected_shares, expected_action):
    trade = by_symbol(rebalance(100_000, given_account()))[symbol]
    assert trade.shares == expected_shares
    assert trade.action == expected_action


def test_given_scenario_variance_values():  # TC-06
    trades = by_symbol(rebalance(100_000, given_account()))
    assert trades["IBM"].variance_pct == -10
    assert trades["ORCL"].variance_pct == 10
    assert trades["MSFT"].variance_pct == 0


def test_output_has_one_row_per_security_in_input_order():  # TC-07
    trades = rebalance(100_000, given_account())
    assert [t.symbol for t in trades] == ["IBM", "MSFT", "ORCL", "AAPL", "HD"]


def test_trade_value_never_exceeds_required_dollars():  # TC-08
    for t, h in zip(rebalance(100_000, given_account()), given_account()):
        required = abs(h.current_pct - h.target_pct) / 100 * 100_000
        assert abs(t.shares) * h.unit_price <= required


# ---------- Calculation / boundary cases ----------

def test_already_balanced_account_has_no_trades():  # TC-09
    acct = [Holding("A", 50, 50, 10), Holding("B", 50, 50, 20)]
    assert all(t.shares == 0 and t.action == "HOLD" for t in rebalance(100_000, acct))


def test_exact_whole_share_result():  # TC-10
    acct = [Holding("A", 60, 50, 100), Holding("B", 40, 50, 100)]
    trades = by_symbol(rebalance(100_000, acct))
    assert trades["A"].shares == 100
    assert trades["B"].shares == -100


def test_price_higher_than_dollar_adjustment_gives_zero_shares():  # TC-11
    acct = [Holding("A", 51, 50, 2000), Holding("B", 49, 50, 2000)]
    trades = by_symbol(rebalance(100_000, acct))  # $1,000 needed, share costs $2,000
    assert trades["A"].shares == 0
    assert trades["B"].shares == 0


def test_fractional_percentages():  # TC-12
    acct = [Holding("A", 33.33, 30, 10), Holding("B", 66.67, 70, 10)]
    trades = by_symbol(rebalance(100_000, acct))
    assert trades["A"].shares == 333   # $3,330 / $10
    assert trades["B"].shares == -333


def test_full_liquidation_of_a_position():  # TC-13
    acct = [Holding("A", 0, 20, 100), Holding("B", 100, 80, 100)]
    trades = by_symbol(rebalance(100_000, acct))
    assert trades["A"].shares == -200
    assert trades["B"].shares == 200


def test_results_scale_with_total_assets():  # TC-14
    small = by_symbol(rebalance(100_000, given_account()))
    big = by_symbol(rebalance(1_000_000, given_account()))
    assert big["IBM"].shares == 666
    assert big["ORCL"].shares == -454
    assert abs(big["IBM"].shares) >= abs(small["IBM"].shares) * 10


def test_single_security_account():  # TC-15
    trades = rebalance(100_000, [Holding("A", 100, 100, 50)])
    assert trades[0].shares == 0


# ---------- Negative / validation cases ----------

@pytest.mark.parametrize("total", [0, -1, None])
def test_invalid_total_assets_rejected(total):  # TC-16
    with pytest.raises(ValidationError):
        rebalance(total, given_account())


@pytest.mark.parametrize("price", [0, -10, None])
def test_invalid_unit_price_rejected(price):  # TC-17
    acct = given_account()
    acct[0].unit_price = price
    with pytest.raises(ValidationError):
        rebalance(100_000, acct)


def test_target_not_totalling_100_rejected():  # TC-18
    acct = given_account()
    acct[0].target_pct = 25
    with pytest.raises(ValidationError, match="Target"):
        rebalance(100_000, acct)


def test_current_not_totalling_100_rejected():  # TC-19
    acct = given_account()
    acct[0].current_pct = 15
    with pytest.raises(ValidationError, match="Current"):
        rebalance(100_000, acct)


@pytest.mark.parametrize("bad", [-5, 101])
def test_percentage_out_of_range_rejected(bad):  # TC-20
    acct = [Holding("A", bad, 50, 10), Holding("B", 100 - bad, 50, 10)]
    with pytest.raises(ValidationError):
        rebalance(100_000, acct)


def test_empty_account_rejected():  # TC-21
    with pytest.raises(ValidationError):
        rebalance(100_000, [])


def test_duplicate_security_rejected():  # TC-22
    acct = [Holding("A", 50, 50, 10), Holding("A", 50, 50, 10)]
    with pytest.raises(ValidationError, match="Duplicate"):
        rebalance(100_000, acct)


def test_blank_symbol_rejected():  # TC-23
    acct = [Holding(" ", 50, 50, 10), Holding("B", 50, 50, 10)]
    with pytest.raises(ValidationError):
        rebalance(100_000, acct)
