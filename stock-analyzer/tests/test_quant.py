"""퀀트 17전략: 개별 신호·집계 형식·버그 회귀(이벤트 정렬, 페어 미래정보)·유니버스 도구."""
import itertools

import numpy as np
import pandas as pd
import pytest

import quant as qt
from tests.conftest import from_close, make_ohlcv


def _trend(n=600, up=True, seed=0):
    return make_ohlcv(n, drift=0.002 if up else -0.002, vol=0.01, seed=seed)


# --------------------------------------------------------------------------- #
# 출력 형식: 17개 중 매수·중립·매도 개수
# --------------------------------------------------------------------------- #
def _sig(no, s):
    return qt.Sig(no, "x", "방향", s, "")


def test_count_and_summary_format():
    sigs = [_sig(i, s) for i, s in enumerate([1, 1, 0, -1, None] + [None] * 12, start=1)]
    assert qt.count_signals(sigs) == {"매수": 2, "중립": 1, "매도": 1, "참고": 13}
    txt = qt.summary_text({"signals": sigs, "label": "중립"})
    assert txt == "17개 중 매수 2 · 중립 1 · 매도 1 (참고·해당없음 13) → 중립"


def test_analyze_offline_returns_17_ordered(fake, fake_info):
    h = make_ohlcv(1000, seed=1)
    fake["^KS11"] = make_ohlcv(800, seed=2, price=2500)
    fake_info["T.KS"] = {"trailingPE": "Infinity", "priceToBook": 1.1, "returnOnEquity": 0.2, "profitMargins": 0.15}
    r = qt.analyze("T.KS", hist=h, with_ml=True)
    assert [s.no for s in r["signals"]] == list(range(1, 18))
    c = qt.count_signals(r["signals"])
    assert sum(c.values()) == 17
    assert r["label"] in ("매수 우위", "중립", "매도·회피 우위")
    assert r["perf"].empty  # 화면에 안 쓰는 백테스트표는 기본으로 계산하지 않음
    assert not qt.analyze("T.KS", hist=h, with_ml=False, with_backtest=True)["perf"].empty


def test_quant_prompt_is_one_line(fake):
    fake["T.KS"] = make_ohlcv(1300, seed=4)
    out = qt.quant_prompt("T.KS", fake["T.KS"])
    assert out.startswith("- 17개 중 매수 ") and "\n" not in out


def test_analyze_short_history_still_gives_17(fake):
    r = qt.analyze("NEW.KS", hist=make_ohlcv(12), with_ml=True)   # 신규 상장 등 짧은 이력
    assert len(r["signals"]) == 17 and qt.count_signals(r["signals"])["참고"] >= 14
    with pytest.raises(ValueError):
        qt.analyze("NEW.KS", hist=make_ohlcv(12).iloc[:0])


def test_quant_prompt_error_is_reported():
    out = qt.quant_prompt("NONE.KS", make_ohlcv(10))
    assert out.startswith("- 판정 불가:")


def test_verdict_thresholds_and_kinds():
    mk = lambda sig, kind="방향": qt.Sig(1, "x", kind, sig, "")  # noqa: E731
    assert qt.verdict([mk(1), mk(1), mk(0)]) == (pytest.approx(2 / 3), "매수 우위", 3)
    assert qt.verdict([mk(-1), mk(0), mk(0)]) == (pytest.approx(-1 / 3), "매도·회피 우위", 3)
    assert qt.verdict([mk(1), mk(0), mk(0), mk(0)])[1] == "중립"            # 0.25 < 0.3
    # 참고·변동성 항목과 해당없음(None)은 종합 의견에서 빠진다
    assert qt.verdict([mk(1), mk(-1, "참고"), mk(-1, "변동성"), mk(None)]) == (1.0, "매수 우위", 1)
    assert qt.verdict([mk(1, "시장")])[2] == 1
    assert qt.verdict([]) == (0.0, "중립", 0)


# --------------------------------------------------------------------------- #
# 개별 신호
# --------------------------------------------------------------------------- #
def test_momentum_and_trend_direction():
    up, dn = _trend(up=True)["Close"], _trend(up=False)["Close"]
    assert qt.s_momentum(up).signal == 1 and qt.s_momentum(dn).signal == -1
    assert qt.s_trend(up).signal == 1 and qt.s_trend(dn).signal == -1
    assert qt.s_momentum(up.iloc[:100]).signal is None


def test_meanrev_extremes_and_flat():
    c = pd.Series(np.r_[np.full(40, 100.0) + np.sin(np.arange(40)), 80.0])
    assert qt.s_meanrev(c).signal == 1
    c2 = pd.Series(np.r_[np.full(40, 100.0) + np.sin(np.arange(40)), 120.0])
    assert qt.s_meanrev(c2).signal == -1
    assert qt.s_meanrev(pd.Series(np.full(30, 100.0))).signal is None  # 변동 없음 → 0으로 나누지 않음


def test_breakout_requires_volume():
    close = list(np.linspace(100, 110, 80)) + [100] * 10 + [130]
    vol = [1e6] * 90 + [5e6]
    h = from_close(close, vol)
    assert qt.s_breakout(h["Close"], h["Volume"], h["High"], h["Low"]).signal == 1
    h2 = from_close(close, [1e6] * 91)
    assert qt.s_breakout(h2["Close"], h2["Volume"], h2["High"], h2["Low"]).signal == 0


def test_reversal_on_crash_with_volume_and_zero_volume_safe():
    base = make_ohlcv(300, vol=0.01, seed=5)
    c = base["Close"].copy()
    c.iloc[-3:] = c.iloc[-4] * np.array([0.93, 0.87, 0.82])
    v = base["Volume"].copy()
    v.iloc[-1] = v.iloc[-25:-1].mean() * 4
    assert qt.s_reversal(c, v).signal == 1
    assert qt.s_reversal(c, v * 0).signal == 0  # 거래량 0(지수 등)이어도 예외 없음


def test_factor_handles_string_values():
    c = _trend()["Close"]
    s = qt.s_factor(c, {"trailingPE": "Infinity", "priceToBook": "abc", "returnOnEquity": None, "profitMargins": None})
    assert s.signal is None  # 숫자가 하나도 없으면 판정하지 않음 (이전: 비교 연산에서 TypeError)
    s2 = qt.s_factor(c, {"trailingPE": "Infinity", "priceToBook": 1.0, "returnOnEquity": 0.2, "profitMargins": 0.2})
    assert s2.signal == 1


def test_ml_insufficient_and_single_class():
    assert qt.s_ml(make_ohlcv(200)).signal is None
    up_only = from_close(100 * 1.01 ** np.arange(600))  # 5일 뒤 항상 상승 → 학습 라벨이 한 종류
    assert qt.s_ml(up_only).signal is None


def test_ml_false_signal_rate_on_random_walks():
    """예측 불가능한 무작위 데이터에서 ML이 신호를 내는 비율(거짓 신호)이 10% 이하인지."""
    sigs = [qt.s_ml(make_ohlcv(1200, drift=0.0, seed=k)) for k in range(30)]
    false_signals = sum(s.signal not in (0, None) for s in sigs)
    assert false_signals <= 3
    ignored = [s for s in sigs if s.signal == 0 and "OOS 우위 확인 안 됨" in s.detail]
    assert len(ignored) >= 20  # 대부분은 '검증 우위 없음 → 신호 무시'로 처리


# --------------------------------------------------------------------------- #
# 이벤트: 날짜별 반응 매칭 (회귀 테스트)
# --------------------------------------------------------------------------- #
def test_event_reaction_uses_most_recent_date_only(monkeypatch):
    c = make_ohlcv(300, start="2025-08-01", seed=6)["Close"]
    last_bar = c.index[-1]
    today = last_bar + pd.Timedelta(days=12)
    monkeypatch.setattr(pd.Timestamp, "today", classmethod(lambda cls, *a, **k: today))
    old_d = c.index[200]
    c.iloc[201:] *= 1.10  # 오래전 발표는 +10% 반응
    recent = last_bar + pd.Timedelta(days=5)  # 가장 최근 발표는 데이터 끝 뒤 → 반응 측정 불가
    ed = pd.DataFrame(index=pd.DatetimeIndex([recent, old_d]).tz_localize("UTC"))
    s = qt.s_event("X", c, ed)
    # 이전 코드: 최근 발표(5일 전)의 반응 자리에 오래전 +10%가 들어가 '매수'로 판정
    assert s.signal == 0
    assert "과거 실적 반응 평균" in s.detail


def test_event_recent_positive_drift(monkeypatch):
    c = make_ohlcv(300, start="2025-08-01", seed=6)["Close"]
    d = c.index[-5]
    c.iloc[-4:] *= 1.08
    monkeypatch.setattr(pd.Timestamp, "today", classmethod(lambda cls, *a, **k: c.index[-1] + pd.Timedelta(days=1)))
    s = qt.s_event("X", c, pd.DataFrame(index=pd.DatetimeIndex([d])))
    assert s.signal == 1
    assert qt.s_event("X", c, None).signal is None


# --------------------------------------------------------------------------- #
# 페어: 미래 정보 없는 백테스트 (회귀 테스트)
# --------------------------------------------------------------------------- #
def _coint_pair(n=900, seed=7, beta=1.5):
    rng = np.random.default_rng(seed)
    lb = np.cumsum(rng.normal(0, 0.01, n)) + 4.0
    spread = np.zeros(n)
    for t in range(1, n):
        spread[t] = 0.85 * spread[t - 1] + rng.normal(0, 0.01)
    la = beta * lb + spread
    idx = pd.bdate_range("2022-01-03", periods=n)
    return pd.Series(np.exp(la), idx), pd.Series(np.exp(lb), idx)


def test_pair_stats_on_cointegrated_pair():
    a, b = _coint_pair()
    st = qt.pair_stats(a, b)
    assert st["beta"] == pytest.approx(1.5, abs=0.25)
    assert 1 < st["half_life"] < 20
    assert st["coint_p"] is None or st["coint_p"] < 0.05


def test_pair_backtest_profits_on_mean_reverting_spread():
    a, b = _coint_pair()
    res = qt.pair_backtest(a, b)
    assert res["trades"] > 5 and res["perf"]["누적"] > 0


def test_pair_backtest_starts_at_first_tradable_day():
    a, b = _coint_pair()
    res = qt.pair_backtest(a, b, beta_window=120, z_window=60)
    assert res["equity"].index[0] == a.index[120 + 60 - 2]  # 첫 유효 z (리뷰 지적: 2일 늦게 시작)


def test_pair_backtest_has_no_lookahead():
    """미래 데이터를 덧붙여도 과거 구간의 손익 곡선이 바뀌지 않아야 한다."""
    a, b = _coint_pair()
    full = qt.pair_backtest(a, b)["equity"]
    part = qt.pair_backtest(a.iloc[:600], b.iloc[:600])["equity"]
    common_idx = part.index
    np.testing.assert_allclose(full.loc[common_idx].to_numpy(), part.to_numpy(), rtol=1e-10)


def test_find_pairs_matches_bruteforce():
    rng = np.random.default_rng(1)
    base = make_ohlcv(400, seed=0)["Close"]
    hists = {}
    for k in range(7):
        noise = np.exp(np.cumsum(rng.normal(0, 0.004 * (k + 1), len(base))))
        hists[f"S{k}"] = pd.DataFrame({"Close": base * noise})
    got = qt.find_pairs(hists, top=4)
    rows = []
    for x, y in itertools.combinations(hists, 2):
        st = qt.pair_stats(hists[x]["Close"], hists[y]["Close"])
        if st:
            rows.append((x, y, st["corr"]))
    want = sorted(rows, key=lambda r: -r[2])[:4]
    assert list(zip(got["A"], got["B"])) == [(x, y) for x, y, _ in want]
    assert list(got.index) == [0, 1, 2, 3]


# --------------------------------------------------------------------------- #
# 유니버스·도구
# --------------------------------------------------------------------------- #
def test_cross_section_ranks_strongest_first():
    hists = {f"S{k}": _trend(500, up=True, seed=k) for k in range(3)}
    hists |= {f"D{k}": _trend(500, up=False, seed=k) for k in range(3)}
    tbl = qt.cross_section(hists)
    assert tbl.index[0].startswith("S") and tbl.index[-1].startswith("D")
    assert (tbl["포지션"] == "롱(상위20%)").sum() == 2 and (tbl["포지션"] == "숏·회피(하위20%)").sum() == 2


def test_xsec_includes_target_symbol(fake):
    h = _trend(1000, up=True, seed=9)
    fake["^GSPC"] = make_ohlcv(800, seed=3, price=5000)
    peers = {f"P{k}": _trend(1000, up=False, seed=k) for k in range(5)}
    r = qt.analyze("TGT", hist=h, peers=peers, with_ml=False)
    s12 = r["signals"][11]
    assert s12.signal == 1 and "6종목 중 종합점수 1위" in s12.detail  # 이전: 대상이 유니버스에 없으면 항상 '해당없음'


def test_stat_arb_universe_columns():
    hists = {f"S{k}": make_ohlcv(400, seed=k) for k in range(5)}
    tbl = qt.stat_arb_universe(hists)
    assert list(tbl.columns) == ["β(바스켓)", "5일 잔차(%)", "z", "신호"] and len(tbl) == 5


def test_execution_plan():
    p = qt.execution_plan(3e8, 100_000, 1e6, 0.02)           # 3,000주 = ADV 0.3%
    assert p["shares"] == pytest.approx(3000) and p["days"] == 1
    assert p["advice"].startswith("거래량 대비 미미")
    big = qt.execution_plan(1e10, 100_000, 1e6, 0.02)          # ADV 10% → 5% 참여면 2일
    assert big["days"] == 2 and big["slices_per_day"] == 20
    with pytest.raises(ValueError):
        qt.execution_plan(1e8, 0, 1e6, 0.02)
    assert np.isnan(qt.execution_plan(1e8, 100, 0, 0.02)["pct_adv"])


def test_carry_calc(fake):
    fake["JPY=X"] = make_ohlcv(800, vol=0.005, price=150)
    r = qt.carry_calc("JPY=X", 4.0, 0.5)
    assert r["carry_%"] == pytest.approx(3.5) and r["fx_vol_%"] > 0 and r["verdict"]
