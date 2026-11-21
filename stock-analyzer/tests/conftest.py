"""테스트 공통: 네트워크 차단 + 합성 시세 + 가짜 yfinance Ticker.

모든 테스트는 인터넷 없이 돈다. 야후 대신 FAKE 레지스트리의 합성 데이터를 돌려준다.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import yfinance as yf  # noqa: E402

import common  # noqa: E402

PERIOD_BARS = {"5d": 5, "3mo": 63, "6mo": 126, "1y": 252, "2y": 504, "3y": 756, "5y": 1260}


def make_ohlcv(n: int = 800, drift: float = 0.0005, vol: float = 0.015, seed: int = 0,
               start: str = "2022-01-03", price: float = 50_000.0, volume: float = 2e6) -> pd.DataFrame:
    """기하 랜덤워크 일봉 (영업일)."""
    rng = np.random.default_rng(seed)
    r = rng.normal(drift, vol, n)
    close = price * np.exp(np.cumsum(r))
    open_ = close * np.exp(rng.normal(0, vol / 3, n))
    high = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, vol / 2, n)))
    low = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, vol / 2, n)))
    v = volume * np.exp(rng.normal(0, 0.3, n))
    idx = pd.bdate_range(start, periods=n)
    return pd.DataFrame({"Open": open_, "High": high, "Low": low, "Close": close, "Volume": v}, index=idx)


def from_close(close, volume=None, start: str = "2022-01-03") -> pd.DataFrame:
    """종가 배열로 단순 OHLCV 만들기 (시가=전일 종가, 고가/저가=±0.5%)."""
    close = np.asarray(close, dtype=float)
    open_ = np.concatenate(([close[0]], close[:-1]))
    hi = np.maximum(open_, close) * 1.005
    lo = np.minimum(open_, close) * 0.995
    vol = np.full(len(close), 1e6) if volume is None else np.asarray(volume, dtype=float)
    return pd.DataFrame({"Open": open_, "High": hi, "Low": lo, "Close": close, "Volume": vol},
                        index=pd.bdate_range(start, periods=len(close)))


FAKE: dict[str, pd.DataFrame] = {}
FAKE_INFO: dict[str, dict] = {}
FAKE_EARN: dict[str, pd.DataFrame] = {}
CALLS = {"history": 0, "info": 0}


class FakeTicker:
    def __init__(self, sym):
        self.ticker = sym

    def history(self, period="1y", **_):
        CALLS["history"] += 1
        h = FAKE.get(self.ticker)
        if h is None:
            return pd.DataFrame()
        return h.tail(PERIOD_BARS.get(period, len(h))).copy()

    @property
    def info(self):
        CALLS["info"] += 1
        return dict(FAKE_INFO.get(self.ticker, {}))

    @property
    def earnings_dates(self):
        return FAKE_EARN.get(self.ticker)

    options = ()

    def option_chain(self, *_):
        raise RuntimeError("no options in tests")

    income_stmt = balance_sheet = cashflow = quarterly_income_stmt = pd.DataFrame()
    recommendations_summary = None


class _NoSearch:
    def __init__(self, *a, **k):
        raise RuntimeError("network blocked in tests")


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    """네트워크 차단 + 깨끗한 캐시·레지스트리."""
    monkeypatch.setattr(yf, "Ticker", FakeTicker)
    monkeypatch.setattr(yf, "Search", _NoSearch)
    FAKE.clear()
    FAKE_INFO.clear()
    FAKE_EARN.clear()
    CALLS.update(history=0, info=0)
    common.clear_cache()
    yield
    common.clear_cache()


@pytest.fixture
def fake():
    """테스트에서 FAKE[...] 로 종목 데이터를 등록."""
    return FAKE


@pytest.fixture
def fake_info():
    return FAKE_INFO


@pytest.fixture
def fake_earn():
    return FAKE_EARN


@pytest.fixture
def calls():
    return CALLS
