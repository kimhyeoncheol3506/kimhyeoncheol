import math

import numpy as np
import pandas as pd
import pytest

import common
from tests.conftest import make_ohlcv


@pytest.mark.parametrize("price,expected", [
    (1999, 1), (2000, 5), (4999, 5), (5000, 10), (19999, 10), (20000, 50), (49999, 50),
    (50000, 100), (199999, 100), (200000, 500), (499999, 500), (500000, 1000), (2_000_000, 1000),
])
def test_tick_krx_table(price, expected):
    assert common.tick(price, True) == expected


def test_tick_overseas():
    assert common.tick(123.45, False) == 0.01


@pytest.mark.parametrize("sym,krw,idx", [
    ("005930.KS", True, "^KS11"), ("247540.KQ", True, "^KQ11"), ("005930.nxt", True, "^KS11"),
    ("AAPL", False, "^GSPC"), ("^DJI", False, "^GSPC"),
])
def test_market_helpers(sym, krw, idx):
    assert common.is_krw(sym) is krw
    assert common.index_symbol(sym) == idx


@pytest.mark.parametrize("raw,expected", [
    (None, None), ("Infinity", None), ("abc", None), (float("nan"), None), (float("inf"), None),
    (True, None), ("3.5", 3.5), (7, 7.0), (np.float64(1.25), 1.25),
])
def test_to_float(raw, expected):
    assert common.to_float(raw) == expected


def test_formatters_never_raise():
    assert common.fmt_num("Infinity") == "데이터 없음"
    assert common.fmt_num(1234.5) == "1,234.50"
    assert common.fmt_num(1234.5, 0) == "1,234"
    assert common.fmt_pct(0.123) == "12.3%"
    assert common.fmt_pct(None) == "데이터 없음"


def test_safe_div():
    assert common.safe_div(1, 2) == 0.5
    assert math.isnan(common.safe_div(1, 0))
    assert common.safe_div(1, 0, 0.0) == 0.0
    assert common.safe_div(1, float("nan"), -1) == -1


def test_parse_symbols_dedup_and_separators():
    assert common.parse_symbols("005930, 000660\nAAPL;MSFT  005930") == ["005930", "000660", "AAPL", "MSFT"]
    assert common.parse_symbols("") == []
    assert common.parse_symbols(None) == []


def test_rsi_bounds_and_extremes():
    up = pd.Series(np.arange(1, 60, dtype=float))
    assert common.rsi(up).iloc[-1] == pytest.approx(100.0)
    r = common.rsi(make_ohlcv(300, seed=3)["Close"]).dropna()
    assert ((r >= 0) & (r <= 100)).all()


def test_hold_positions_semantics():
    enter = [0, 1, 0, 0, 1, 0, 1]
    exit_ = [0, 0, 0, 1, 1, 1, 1]
    pos = common.hold_positions(np.array(enter), np.array(exit_), range(7))
    # 1일차 진입 → 3일차 청산 → 4일차(둘 다) 진입 → 5일차 청산 → 6일차(둘 다) 진입
    assert pos.tolist() == [0, 1, 1, 0, 1, 0, 1]


def test_tz_naive():
    idx = pd.date_range("2024-01-01", periods=3, tz="Asia/Seoul")
    df = pd.DataFrame({"x": [1, 2, 3]}, index=idx)
    out = common.tz_naive(df)
    assert out.index.tz is None and df.index.tz is not None  # 원본은 그대로


def test_cached_ttl_and_failures_not_cached(monkeypatch):
    n = {"calls": 0}

    def ok():
        n["calls"] += 1
        return n["calls"]

    assert common.cached(("k",), ok) == 1
    assert common.cached(("k",), ok) == 1          # 캐시 적중
    assert common.cached(("k",), ok, ttl=0) == 2   # 만료

    def boom():
        raise ValueError("x")

    with pytest.raises(ValueError):
        common.cached(("bad",), boom)
    assert common.cached(("bad",), ok) == 3        # 실패는 저장되지 않음


def test_load_history_copy_and_cache(fake, calls):
    fake["AAA"] = make_ohlcv(50)
    h1 = common.load_history("AAA", "1y")
    h1.iloc[0, 0] = -1  # 반환값을 고쳐도
    h2 = common.load_history("AAA", "1y")
    assert h2.iloc[0, 0] != -1  # 캐시 원본은 보호
    assert calls["history"] == 1  # 두 번째는 캐시


def test_load_history_missing_raises():
    with pytest.raises(ValueError, match="시세 없음"):
        common.load_history("NOPE", "1y")
    assert common.has_price("NOPE") is False


def test_get_info_failure_returns_empty(monkeypatch):
    class Boom:
        def __init__(self, *_):
            pass

        @property
        def info(self):
            raise RuntimeError("429")

    import yfinance as yf
    monkeypatch.setattr(yf, "Ticker", Boom)
    assert common.get_info("X") == {}
