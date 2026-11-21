"""지지 눌림목 전략: 판정·가속 경로 동치성·청산 규칙·자금관리·출력 형식."""
import numpy as np
import pandas as pd
import pytest

import strategy as stg
from tests.conftest import from_close, make_ohlcv

RELAXED = stg.replace(stg.V2, min_avg_value_20=0, min_value_today=0, sideways_rest_count=4, rr_min=0.8)
SEEDS = range(6)


def _series(seed):
    return make_ohlcv(1500, drift=0.0008, vol=0.02, seed=seed)


# --------------------------------------------------------------------------- #
# 판정
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("p", [stg.V2, RELAXED, stg.ORIGINAL], ids=["v2", "relaxed", "original"])
def test_fast_and_prescreen_match_full_evaluation(p):
    """빠른 판정·벡터 사전선별이 정밀 판정과 결과가 같은지 (리팩터 안전장치)."""
    n_pass = 0
    for seed in SEEDS:
        A = stg.prepare(_series(seed))
        pre = stg.prescreen(A, p, True)
        for i in range(stg.MIN_BARS, len(A["Close"])):
            full = stg.evaluate(A, i, p, True, True)
            fast = stg.evaluate(A, i, p, True, True, fast=True)
            assert full["pass"] == fast["pass"], (seed, i)
            if full["pass"]:
                n_pass += 1
                assert pre[i], f"사전선별이 통과 신호를 놓침 seed={seed} i={i}"
                assert (fast["entry"], fast["stop"], fast["target"]) == (full["entry"], full["stop"], full["target"])
    if p is RELAXED:
        assert n_pass > 20  # 의미 있는 표본으로 검증했는지


def test_evaluate_short_history():
    A = stg.prepare(make_ohlcv(50))
    ev = stg.evaluate(A, 49, stg.V2)
    assert ev["pass"] is False and ev["checks"][0][0] == "데이터 길이"


def test_evaluate_checks_structure():
    A = stg.prepare(_series(1))
    ev = stg.evaluate(A, 900, stg.V2)
    assert len(ev["sideways"]) == 4
    assert all(len(c) == 3 and isinstance(c[1], bool) for c in ev["checks"])
    assert ev["pass"] == all(c[1] for c in ev["checks"])


def test_market_filter_blocks_signal():
    p = stg.replace(RELAXED, market_filter=True)
    A = stg.prepare(_series(1))
    passing = [i for i in range(stg.MIN_BARS, 1500) if stg.evaluate(A, i, p, True, True)["pass"]]
    assert passing
    assert not stg.evaluate(A, passing[0], p, True, market_ok=False)["pass"]


def test_market_ok_aligned_defaults_true_before_index_start():
    idx = pd.bdate_range("2024-01-01", periods=5)
    mk = pd.Series([False, True], index=pd.to_datetime(["2024-01-03", "2024-01-05"]))
    assert stg._market_ok_aligned(mk, idx).tolist() == [True, True, False, False, True]
    assert stg._market_ok_aligned(None, idx).all()


# --------------------------------------------------------------------------- #
# 백테스트: 가속 경로 == 기존(전 봉 정밀 판정) 경로
# --------------------------------------------------------------------------- #
def _reference_backtest_symbol(symbol, hist, p, start=None, end=None, mkt_ok=None):
    """리팩터 전 알고리즘 그대로 (모든 봉을 정밀 판정)."""
    A = stg.prepare(hist)
    krw = stg.is_krw(symbol)
    idx = A["_index"]
    trades, i, n = [], stg.MIN_BARS, len(idx)
    while i < n - 1:
        d = idx[i]
        if (start and d < pd.Timestamp(start)) or (end and d > pd.Timestamp(end)):
            i += 1
            continue
        m_ok = True
        if p.market_filter and mkt_ok is not None:
            m_ok = bool(mkt_ok.reindex([d], method="ffill").iloc[0]) if d >= mkt_ok.index[0] else True
        ev = stg.evaluate(A, i, p, krw, m_ok)
        if ev["pass"]:
            t = stg._simulate(A, i, ev, p, krw)
            t["symbol"] = symbol
            trades.append(t)
            i = t["exit_i"] + 1
        else:
            i += 1
    return trades


@pytest.mark.parametrize("seed", SEEDS)
def test_backtest_symbol_matches_reference(seed):
    h = _series(seed)
    mk = pd.Series(np.random.default_rng(seed).random(len(h)) > 0.3, index=h.index)
    for p in (RELAXED, stg.replace(RELAXED, market_filter=True)):
        got = stg.backtest_symbol("TEST.KS", h, p, "2022-06-01", "2027-01-01", mk)
        ref = _reference_backtest_symbol("TEST.KS", h, p, "2022-06-01", "2027-01-01", mk)
        assert pd.DataFrame(got).equals(pd.DataFrame(ref))


# --------------------------------------------------------------------------- #
# 청산 규칙 (_simulate)
# --------------------------------------------------------------------------- #
def _sim(after, entry=100.0, target=110.0, pb_low=95.0, p=stg.V2, pre=None):
    """진입 봉(i) 뒤에 after 종가들이 이어지는 상황을 시뮬레이션."""
    pre = pre if pre is not None else list(np.linspace(80, 100, 200))
    h = from_close(pre + list(after))
    A = stg.prepare(h)
    i = len(pre) - 1
    ev = {"entry": entry, "stop": max(pb_low, entry * (1 - p.max_loss)), "target": target, "pb_low": pb_low}
    return stg._simulate(A, i, ev, p, krw=False)


def test_exit_max_loss():
    t = _sim([99, 92, 90])
    assert t["reason"] == "최대손실 -7%"
    assert t["ret"] == pytest.approx(-0.07 - stg.V2.cost_round_trip, abs=1e-6)


def test_exit_support_break_on_close():
    t = _sim([99, 94.5, 94], pb_low=95.0)
    assert t["reason"].startswith("지지 붕괴")


def test_partial_take_profit_then_breakeven():
    t = _sim([104, 111, 112, 99.5], target=110.0)
    assert t["reason"] == "본전 스톱"
    # 절반은 목표가(시가가 목표가 아래면 목표가) 체결, 절반은 매수가
    assert t["ret"] == pytest.approx(0.5 * 0.10 + 0.5 * 0.0 - stg.V2.cost_round_trip, abs=1e-6)


def test_time_stop():
    t = _sim([100.5] * 12)
    assert t["reason"].startswith("시간 손절") and t["days"] == 10


def test_open_position_marked_hold():
    t = _sim([101, 102])
    assert t["status"] == "보유" and t["reason"] == "보유 중"


# --------------------------------------------------------------------------- #
# 자금 관리
# --------------------------------------------------------------------------- #
ACC = 3_000_000_000


def test_size_position_risk_based():
    sz = stg.size_position(100.0, 95.0, ACC, 0, stg.V2)   # 손절폭 5% → 1,500만 ÷ 5% = 3억
    assert sz["ok"] and sz["amount"] == pytest.approx(300_000_000) and sz["shares"] == 3_000_000


def test_size_position_caps_and_floor():
    assert stg.size_position(100.0, 98.0, ACC, 0, stg.V2)["amount"] == pytest.approx(600_000_000)  # 최대 20%
    assert not stg.size_position(100.0, 90.0, ACC, 0, stg.V2)["ok"]                                # 1.5억 < 최소 3억
    liq = stg.size_position(100.0, 97.0, ACC, 20_000_000_000, stg.V2)                              # 2% = 4억 상한
    assert liq["amount"] == pytest.approx(400_000_000) and liq["notes"]
    assert not stg.size_position(100.0, 100.0, ACC, 0, stg.V2)["ok"]                               # 손절폭 0


def test_portfolio_allocation_respects_account_and_sector(monkeypatch):
    hs = {f"S{k}.KS": _series(k) for k in range(6)}
    monkeypatch.setattr(stg, "load_history", lambda s, period="3y": hs[s])
    sectors = {s: "같은업종" for s in hs}
    res = stg.backtest(list(hs), RELAXED, ACC, sectors=sectors)
    df = res["trades"]
    assert len(df) > 0 and res["summary"]["trades"] == len(df)
    for _, t in df.iterrows():
        live = df[(df["entry_date"] <= t["entry_date"]) & (df["exit_date"] >= t["entry_date"])]
        assert live["amount"].sum() <= ACC + 1e-6
        assert len(live) <= RELAXED.max_per_sector
    assert any("업종" in r for _, _, r in res["skipped"])


def test_backtest_collects_errors(monkeypatch):
    def boom(s, period="3y"):
        raise ValueError("시세 없음")

    monkeypatch.setattr(stg, "load_history", boom)
    res = stg.backtest(["X.KS"], stg.V2, ACC)
    assert res["trades"].empty and res["summary"]["errors"] == ["X.KS: 시세 없음"]


# --------------------------------------------------------------------------- #
# 출력 형식 (간단 표 · 프롬프트 한 줄)
# --------------------------------------------------------------------------- #
def test_strategy_prompt_no_signal_is_one_line(fake):
    h = make_ohlcv(400, seed=2)
    out = stg.strategy_prompt("X.KS", h)
    assert out == f"- {h.index[-1]:%Y-%m-%d} 기준: 신호 없음"


def test_strategy_prompt_signal_line(monkeypatch):
    ev = {"pass": True, "date": pd.Timestamp("2026-11-20"), "entry": 101.0, "target": 120.0, "stop": 95.0,
          "size": {"ok": True, "amount": 300_000_000.0}}
    monkeypatch.setattr(stg, "scan_symbol", lambda *a, **k: ev)
    out = stg.strategy_prompt("X.KS", pd.DataFrame())
    assert out == "- 2026-11-20 기준: 매수 신호 / 진입 101.00 · 목표 120.00 · 손절 95.00 · 매수금액 300,000,000"
    assert "\n" not in out  # 조건별 근거 없이 한 줄


def test_strategy_prompt_handles_errors(monkeypatch):
    monkeypatch.setattr(stg, "scan_symbol", lambda *a, **k: (_ for _ in ()).throw(ValueError("x")))
    assert stg.strategy_prompt("X.KS", pd.DataFrame()) == "- 판정 불가: x"
