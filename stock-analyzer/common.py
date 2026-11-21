"""공통 유틸: 시장 판별 · 호가단위 · 숫자 정리 · 지표 · 데이터 캐시.

여러 모듈에 흩어져 있던 중복(시간대 정리, RSI, 벤치마크 지수 선택, 숫자 포맷)을 한곳에 모았다.
데이터 조회는 프로세스 안에서 TTL 캐시를 공유해, 같은 종목을 여러 기능이 반복 조회하지 않게 한다.
"""
from __future__ import annotations

import logging
import math
import re
import threading
import time
from typing import Any, Callable

import numpy as np
import pandas as pd
import yfinance as yf

log = logging.getLogger("stock_analyzer")
# 코스닥 종목을 .KS 로 먼저 찾아볼 때 yfinance가 찍는 404 같은 잡음을 숨긴다(실패는 위 log로 남김).
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

KRW_SUFFIXES = (".KS", ".KQ", ".NXT")
CACHE_TTL = 15 * 60  # 초

ICONS = {"Pass": "✅", "Warn": "🟡", "Fail": "❌"}


# --------------------------------------------------------------------------- #
# 시장 / 호가
# --------------------------------------------------------------------------- #
def is_krw(symbol: str) -> bool:
    return symbol.upper().endswith(KRW_SUFFIXES)


def index_symbol(symbol: str) -> str:
    """종목이 속한 시장의 대표 지수 (코스닥 → ^KQ11, 국내 → ^KS11, 그 외 → ^GSPC)."""
    s = symbol.upper()
    if s.endswith(".KQ"):
        return "^KQ11"
    return "^KS11" if is_krw(s) else "^GSPC"


_KRX_TICKS = ((2000, 1), (5000, 5), (20000, 10), (50000, 50), (200000, 100), (500000, 500))


def tick(price: float, krw: bool = True) -> float:
    """1호가 단위 (KRX 호가단위 표, 해외는 0.01)."""
    if not krw:
        return 0.01
    for lim, t in _KRX_TICKS:
        if price < lim:
            return t
    return 1000


# --------------------------------------------------------------------------- #
# 숫자 정리 / 포맷
# --------------------------------------------------------------------------- #
def to_float(x: Any) -> float | None:
    """숫자로 쓸 수 없는 값(None, NaN, inf, 'Infinity' 같은 문자열)은 None."""
    if x is None or isinstance(x, bool):
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def fmt_num(x: Any, d: int = 2) -> str:
    v = to_float(x)
    return "데이터 없음" if v is None else f"{v:,.{d}f}"


def fmt_pct(x: Any) -> str:
    """비율(0.12) → '12.0%'."""
    v = to_float(x)
    return "데이터 없음" if v is None else f"{v * 100:.1f}%"


def safe_div(a: float, b: float, default: float = float("nan")) -> float:
    try:
        return a / b if b not in (0, None) and math.isfinite(b) else default
    except TypeError:
        return default


def parse_symbols(text: str) -> list[str]:
    """콤마·줄바꿈·세미콜론·공백 구분 목록 → 중복 없는 순서 유지 리스트."""
    seen, out = set(), []
    for tok in re.split(r"[\s,;]+", text or ""):
        tok = tok.strip()
        if tok and tok not in seen:
            seen.add(tok)
            out.append(tok)
    return out


# --------------------------------------------------------------------------- #
# 지표 / 포지션 유틸
# --------------------------------------------------------------------------- #
def rsi(c: pd.Series, n: int = 14) -> pd.Series:
    """Wilder RSI (EWM alpha=1/n). 손실이 전혀 없으면 100, 변동이 전혀 없으면 50."""
    d = c.diff()
    g = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    l = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    out = 100 - 100 / (1 + g / l.replace(0, np.nan))
    out = out.mask((l == 0) & (g > 0), 100.0).mask((l == 0) & (g == 0), 50.0)
    return out.where(d.notna().cumsum() > 0)  # 첫 봉(변화량 없음)은 NaN 유지


def hold_positions(enter: np.ndarray, exit_: np.ndarray, index) -> pd.Series:
    """진입 신호에 들어가 청산 신호에 나오는 1/0 포지션 (같은 날 둘 다면: 미보유→진입, 보유→청산)."""
    enter = np.asarray(enter, dtype=bool)
    exit_ = np.asarray(exit_, dtype=bool)
    pos = np.zeros(len(enter))
    on = False
    for i in range(len(enter)):
        if not on:
            on = bool(enter[i])
        elif exit_[i]:
            on = False
        pos[i] = on
    return pd.Series(pos, index=index)


def tz_naive(df: pd.DataFrame | pd.Series):
    """야후 데이터의 시간대 인덱스를 제거 (국내·해외 날짜 비교 가능하게)."""
    idx = df.index
    if isinstance(idx, pd.DatetimeIndex) and idx.tz is not None:
        df = df.copy()
        df.index = idx.tz_localize(None)
    return df


# --------------------------------------------------------------------------- #
# 데이터 캐시 (프로세스 공유, TTL)
# --------------------------------------------------------------------------- #
_cache: dict[tuple, tuple[float, Any]] = {}
_lock = threading.Lock()


def clear_cache() -> None:
    with _lock:
        _cache.clear()


def cached(key: tuple, fn: Callable[[], Any], ttl: float = CACHE_TTL) -> Any:
    now = time.monotonic()
    with _lock:
        hit = _cache.get(key)
        if hit and now - hit[0] < ttl:
            return hit[1]
    val = fn()  # 네트워크 호출은 락 밖에서
    with _lock:
        _cache[key] = (now, val)
    return val


def load_history(symbol: str, period: str = "3y") -> pd.DataFrame:
    """일봉 OHLCV (시간대 제거). 캐시된 원본을 보호하려고 복사본을 돌려준다."""
    def fetch():
        h = yf.Ticker(symbol).history(period=period)
        if h is None or h.empty:
            raise ValueError(f"{symbol}: 시세 없음")
        return tz_naive(h)

    return cached(("hist", symbol, period), fetch).copy()


def has_price(symbol: str) -> bool:
    try:
        load_history(symbol, "5d")
        return True
    except Exception:  # noqa: BLE001 - 조회 실패는 '시세 없음'으로 취급
        return False


def get_info(symbol: str) -> dict:
    """yfinance info (실패·요청 제한이면 빈 dict). 실패는 캐시하지 않는다."""
    try:
        return dict(cached(("info", symbol), lambda: yf.Ticker(symbol).info or {}))
    except Exception as e:  # noqa: BLE001
        log.warning("info 조회 실패 %s: %s", symbol, e)
        return {}


def get_earnings_dates(symbol: str) -> pd.DataFrame | None:
    try:
        return cached(("earn", symbol), lambda: yf.Ticker(symbol).earnings_dates)
    except Exception as e:  # noqa: BLE001
        log.info("실적 발표일 조회 실패 %s: %s", symbol, e)
        return None
