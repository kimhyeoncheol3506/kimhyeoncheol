from decimal import Decimal as D

from finclose import audit
from finclose.db import Database
from finclose.journal import balance_check
from finclose.periods import comparison_targets, prev_quarter_end
from finclose.variance import NEW, REMOVED, SIGN_CHANGE, ZERO_BASE, change_rate, compare
from datetime import date


def test_change_rate_edge_cases():
    assert change_rate(D(10), D(0)) == (ZERO_BASE, None)
    assert change_rate(D(0), D(0))[0] == "NO_CHANGE"
    assert change_rate(D(-5), D(10)) == (SIGN_CHANGE, None)
    assert change_rate(D(5), None) == (NEW, None)
    assert change_rate(None, D(5)) == (REMOVED, None)
    assert change_rate(D(-12), D(-10)) == ("RATE", D("-0.2"))   # 분모 절대값
    assert change_rate(D(110), D(100)) == ("RATE", D("0.1"))


def test_compare_flags_and_causes():
    cur = {"A": {"amount": D(1_000_000_000), "quantity": D(100), "label": "a"},
           "B": {"amount": D(50), "quantity": D(200), "label": "b"},
           "N": {"amount": D(10), "quantity": None, "label": "n"}}
    base = {"A": {"amount": D(800_000_000), "quantity": D(100), "label": "a"},
            "B": {"amount": D(50), "quantity": D(100), "label": "b"},
            "R": {"amount": D(5), "quantity": None, "label": "r"}}
    res = compare(cur, base, {"abs_amount": "100000000", "pct": "0.1"})
    rows = {r["key"]: r for r in res["rows"]}
    assert rows["A"]["anomaly"] and any("가격" in c for c in rows["A"]["cause_candidates"])
    assert "금액 유사·수량 급변" in rows["B"]["flags"]
    assert rows["N"]["rate_status"] == NEW and rows["R"]["rate_status"] == REMOVED
    assert all("확인되지 않은 추정" in r["cause_candidates"][-1] for r in rows.values() if r["cause_candidates"])


def test_periods():
    t = comparison_targets(date(2026, 9, 30))
    assert t == {"PREV_MONTH": date(2026, 8, 31), "PREV_QUARTER": date(2026, 6, 30),
                 "SAME_PERIOD_LAST_YEAR": date(2025, 9, 30), "PRIOR_YEAR_END": date(2025, 12, 31)}
    assert prev_quarter_end(date(2026, 1, 31)) == date(2025, 12, 31)
    assert comparison_targets(date(2026, 2, 28), fy_end_month=3)["PRIOR_YEAR_END"] == date(2025, 3, 31)


def test_balance_check_detects_imbalance():
    lines = [{"voucher_no": "1", "currency": "KRW", "debit": D(100), "credit": D(0)},
             {"voucher_no": "1", "currency": "KRW", "debit": D(0), "credit": D(99)},
             {"voucher_no": "2", "currency": "KRW", "debit": D(5), "credit": D(5)}]
    bad = balance_check(lines)
    assert len(bad) == 1 and bad[0]["difference"] == D(1)


def test_audit_chain_tamper_and_scrub(tmp_path):
    db = Database(tmp_path / "a.db")
    audit.record(db, "u", "admin", "X", "run", "1", {"api_key": "secret!", "n": {"password": "p"}})
    audit.record(db, "u", "admin", "Y", "run", "1", {})
    row = db.one("SELECT details_json FROM audit_log WHERE id=1")
    assert "secret!" not in row["details_json"] and '"p"' not in row["details_json"]
    assert audit.verify_chain(db)["ok"]
    db.execute("UPDATE audit_log SET actor='attacker' WHERE id=1")
    v = audit.verify_chain(db)
    assert not v["ok"] and v["broken_at_id"] == 1
