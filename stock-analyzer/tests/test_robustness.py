"""과최적화 검증: 통계 함수 성질 · numpy 가속 경로 동치성 · 검증 게이트."""
import numpy as np
import pandas as pd
import pytest

import quant as qt
import robustness as rb
from tests.conftest import make_ohlcv


def test_psr_monotone_in_sharpe():
    a = rb.psr(0.05, 0.0, 500, 0.0, 3.0)
    b = rb.psr(0.10, 0.0, 500, 0.0, 3.0)
    assert 0.5 < a < b < 1
    assert np.isnan(rb.psr(0.1, 0.0, 2, 0.0, 3.0))


def test_expected_max_sharpe_grows_with_trials():
    assert rb.expected_max_sr(1, 0.01) == 0.0
    assert 0 < rb.expected_max_sr(10, 0.01) < rb.expected_max_sr(100, 0.01)


def test_deflated_sharpe_in_unit_interval():
    r = pd.Series(np.random.default_rng(0).normal(0.001, 0.01, 1000))
    d = rb.deflated_sharpe(r, 30, np.random.default_rng(1).normal(0, 0.05, 30))
    assert 0 <= d <= 1
    assert rb.deflated_sharpe(r, 1, np.array([0.1])) >= d  # 시도가 적을수록 덜 깎임


def test_numpy_backtest_matches_quant_run_bt():
    h = make_ohlcv(500, seed=2)
    pos = qt.pos_trend(h["Close"])
    ref = qt.run_bt(h["Close"], pos).to_numpy()
    got = rb._run_bt_np(h["Close"].pct_change().fillna(0).to_numpy(), pos.fillna(0).to_numpy())
    np.testing.assert_allclose(got, ref, atol=1e-15)


def test_numpy_sharpe_matches_pandas():
    X = np.random.default_rng(3).normal(0, 0.01, (300, 6))
    X[:, 2] = 0.0  # 변동 없는 열
    np.testing.assert_allclose(rb._sh_np(X), rb._sh(pd.DataFrame(X)).to_numpy(), atol=1e-12)


def test_memoized_strategies_match_plain():
    h = make_ohlcv(700, seed=4)
    c, v, hi, lo = h["Close"], h["Volume"], h["High"], h["Low"]
    for fn, grid in rb.STRATS.values():
        memo = {}
        for p in rb._configs(grid):
            pd.testing.assert_series_equal(fn(c, v, hi, lo, p, memo), fn(c, v, hi, lo, p), check_names=False)


def test_pbo_detects_noise_vs_real_edge():
    rng = np.random.default_rng(5)
    noise = pd.DataFrame(rng.normal(0, 0.01, (1000, 20)))
    p_noise = rb.pbo_cscv(noise)
    edge = noise.copy()
    edge[0] += 0.004  # 진짜 엣지가 있는 설정 하나
    p_edge = rb.pbo_cscv(edge)
    assert p_edge["pbo"] < p_noise["pbo"] and p_edge["loss"] == 0.0
    assert p_noise["splits"] == 70


def test_cpcv_paths():
    X = pd.DataFrame(np.random.default_rng(6).normal(0.001, 0.01, (800, 5)))
    out = rb.cpcv(X)
    assert out["paths"] == 28 and 0 <= out["pos_share"] <= 1


def test_validate_universe(fake):
    hists = {f"S{k}": make_ohlcv(1100, drift=0.0004, seed=k) for k in range(4)}
    for no in rb.STRATS:
        g = rb.validate(hists, no)
        assert g["status"] in ("Pass", "Warn", "Fail")
        assert g["n_symbols"] == 4 and g["trials"] == len(rb._configs(rb.STRATS[no][1]))
        assert {"표본(OOS 거래 수)", "Sharpe 디플레이션(DSR)", "과최적화 확률(PBO/CSCV)"} <= {c[0] for c in g["checks"]}


def test_validate_rejects_short_or_unknown():
    with pytest.raises(ValueError, match="데이터 부족"):
        rb.validate(make_ohlcv(300), 1)
    with pytest.raises(ValueError, match="검증 가능 전략"):
        rb.validate(make_ohlcv(1100), 6)


def test_validate_trades_small_sample_fails():
    g = rb.validate_trades([0.05, -0.03, 0.04], trials=3)
    assert g["status"] == "Fail" and g["mc"] is None
    assert rb.validate_trades([], trials=1)["stats"]["n"] == 0


def test_monte_carlo_deterministic():
    r = pd.Series(np.random.default_rng(7).normal(0.0005, 0.01, 300))
    assert rb.monte_carlo(r) == rb.monte_carlo(r)
