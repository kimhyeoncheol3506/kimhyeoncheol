"""지지 눌림목 전략 (차트의 맥 x 워뇨띠) v2.

- evaluate(): 특정 시점의 신호 판정 (유동성 · 횡보 · 셋업 · 눌림목 · 트리거 · 금지 · 손익비)
- size_position(): 자금 관리 (손실한도 0.5%, 최소/최대, 유동성 상한)
- backtest(): 진입(종가) → 익절/본전스톱/2차익절/손절 5종 시뮬레이션 + 계좌 단위 배분
- 일봉 기반이므로 장중 순서(익절 vs 손절)는 보수적으로 손절 우선으로 가정한다.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, replace  # noqa: F401  (replace: app에서 stg.replace 로 사용)

import numpy as np
import pandas as pd

from common import cached, index_symbol, is_krw, load_history, log, tick, tz_naive  # noqa: F401 (재노출)

EOK = 1e8  # 1억

MIN_BARS = 130  # 120일선 + 여유


# --------------------------------------------------------------------------- #
# 파라미터
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Params:
    name: str = "v2"
    # 유니버스/유동성 (KRW 종목에만 적용)
    min_avg_value_20: float = 300 * EOK   # 20일 평균 거래대금
    min_value_today: float = 200 * EOK    # 당일 거래대금
    exclude_limit_up: bool = True         # 상한가 종목 제외
    # 시장 필터
    market_filter: bool = False
    # 횡보 필터
    sideways_rest_count: int = 3          # 4개 중 N개 이상이면 쉼
    # 셋업
    require_120: bool = False             # True: 20>60>120, False: 20>60
    # 눌림목 (최근 20일 고점 대비 종가 낙폭)
    pb_min: float = -0.20
    pb_max: float = -0.03
    # 손익비
    rr_min: float = 1.5
    # 손절
    max_loss: float = 0.07
    stop_mode: str = "pullback_low"       # "pullback_low"(눌림 저점 이탈) | "sma20_-3%"(20일선 -3%)
    support_buffer: float = 0.0           # 눌림 저점 아래 여유폭(예: 0.01 = 1%)
    time_stop_days: int = 10
    time_stop_gain: float = 0.03
    # 비용
    cost_round_trip: float = 0.003
    # 자금 관리
    risk_per_trade: float = 0.005         # 계좌의 0.5%
    min_pos_frac: float = 0.10            # 최소 (30억 기준 3억)
    max_pos_frac: float = 0.20            # 최대 (30억 기준 6억)
    liq_cap: float = 0.02                 # 20일 평균 거래대금의 2%
    max_per_sector: int = 2


V2 = Params()
V2_150 = replace(V2, name="v2 (150억)", min_avg_value_20=150 * EOK, min_value_today=100 * EOK)
ORIGINAL = Params(
    name="원안", min_avg_value_20=0, min_value_today=0, market_filter=True, sideways_rest_count=2,
    require_120=True, pb_min=-0.15, pb_max=-0.04,
)
PRESETS = {"v2 (300억)": V2, "v2 (150억)": V2_150, "원안 + 시장필터": ORIGINAL}


# --------------------------------------------------------------------------- #
# 유틸
# --------------------------------------------------------------------------- #
def prepare(hist: pd.DataFrame) -> dict[str, np.ndarray]:
    """OHLCV → 전략용 배열 묶음 (이평선은 기본값 5/20/60/120)."""
    df = hist[["Open", "High", "Low", "Close", "Volume"]].copy()
    c, v = df["Close"], df["Volume"]
    for n in (5, 20, 60, 120):
        df[f"S{n}"] = c.rolling(n).mean()
    df["TV"] = c * v
    df["TV20"] = df["TV"].rolling(20).mean()
    df["V20"] = v.rolling(20).mean()
    df["V60"] = v.rolling(60).mean()
    df["RET"] = c.pct_change()
    # 대량 장대음봉: 거래량 ≥ 직전 20일 평균의 3배, 하루 -4% 이하, 음봉
    df["BIGBEAR"] = (v >= 3 * df["V20"].shift(1)) & (df["RET"] <= -0.04) & (c < df["Open"])
    A = {k: df[k].to_numpy(dtype=float) for k in df.columns}
    A["_index"] = df.index
    return A


def market_ok_series(index_sym: str, period: str = "3y") -> pd.Series:
    """지수가 60일선 아래이고 60일선이 하락 중이면 False(전체 쉼)."""
    h = load_history(index_sym, period)["Close"].dropna()
    s60 = h.rolling(60).mean()
    bad = (h < s60) & (s60 < s60.shift(5))
    return ~bad


def _market_ok_aligned(mkt_ok: pd.Series | None, idx: pd.DatetimeIndex) -> np.ndarray:
    """종목 날짜에 맞춘 시장 필터 (지수 데이터 시작 전·빈 날은 통과)."""
    if mkt_ok is None or mkt_ok.empty:
        return np.ones(len(idx), dtype=bool)
    al = mkt_ok.astype(float).reindex(idx, method="ffill")
    return al.fillna(1.0).to_numpy() > 0.5


def prescreen(A: dict, p: Params, krw: bool = True) -> np.ndarray:
    """evaluate()가 통과하려면 반드시 만족해야 하는 조건만 벡터로 먼저 계산 (백테스트 가속).

    여기서 False면 evaluate()도 반드시 False다. True인 봉만 evaluate()로 정밀 판정한다.
    """
    O, C, V = A["Open"], A["Close"], A["Volume"]
    s20, s60, s120 = A["S20"], A["S60"], A["S120"]
    n = len(C)
    s20_prev5 = np.full(n, np.nan)
    s20_prev5[5:] = s20[:-5]
    v_prev = np.full(n, np.nan)
    v_prev[1:] = V[:-1]
    with np.errstate(invalid="ignore"):
        m = (s20 > s60) & (s20 > s20_prev5) & (C > s60) & (C > O) & (C > s20)
        m &= (V > v_prev) & (V >= 0.8 * A["V20"]) & ~np.isnan(s120)
        if p.require_120:
            m &= s60 > s120
        if krw and p.min_avg_value_20 > 0:
            m &= (A["TV20"] >= p.min_avg_value_20) & (A["TV"] >= p.min_value_today)
        if krw and p.exclude_limit_up:
            m &= ~(A["RET"] >= 0.295)
    m[:MIN_BARS] = False
    return m


# --------------------------------------------------------------------------- #
# 신호 판정
# --------------------------------------------------------------------------- #
class _Stop(Exception):
    """evaluate(fast=True)에서 첫 실패 시 중단용."""


def evaluate(A: dict, i: int, p: Params, krw: bool = True, market_ok: bool = True, fast: bool = False) -> dict:
    """i 번째 봉(종가 기준)에서 지지 눌림목 신호를 판정.

    fast=True 이면 첫 실패에서 바로 멈추고 상세 문구를 만들지 않는다(백테스트용). pass 결과는 동일하다.
    """
    out = {"pass": False, "checks": [], "sideways": [], "entry": None, "stop": None,
           "target": None, "rr": None, "pb_low": None}
    if i < MIN_BARS or np.isnan(A["S120"][i]):
        out["checks"].append(("데이터 길이", False, f"최소 {MIN_BARS}봉 필요"))
        return out

    O, H, L, C, V = (A[k] for k in ("Open", "High", "Low", "Close", "Volume"))
    s5, s20, s60, s120 = A["S5"], A["S20"], A["S60"], A["S120"]

    def add(name, ok, detail):
        ok = bool(ok)
        if fast:
            if not ok:
                raise _Stop
            return
        out["checks"].append((name, ok, detail() if callable(detail) else detail))

    try:
        # ---- 유동성 (KRW)
        if krw and p.min_avg_value_20 > 0:
            add("20일 평균 거래대금", A["TV20"][i] >= p.min_avg_value_20,
                lambda: f"{A['TV20'][i] / EOK:,.0f}억 (기준 {p.min_avg_value_20 / EOK:,.0f}억)")
            add("당일 거래대금", A["TV"][i] >= p.min_value_today,
                lambda: f"{A['TV'][i] / EOK:,.0f}억 (기준 {p.min_value_today / EOK:,.0f}억)")
        if krw and p.exclude_limit_up:
            add("상한가 제외", not (A["RET"][i] >= 0.295), lambda: f"당일 등락 {A['RET'][i] * 100:+.1f}%")

        # ---- 시장 필터
        if p.market_filter:
            add("시장 필터(지수>60일선 또는 60일선 상승)", market_ok, "통과" if market_ok else "지수 하락장 → 전체 쉼")

        # ---- 횡보 필터 4종
        w = slice(i - 19, i + 1)
        f1 = abs(s20[i] / s20[i - 10] - 1) <= 0.01
        d = np.sign(s5[w] - s20[w])
        crosses = int(np.sum(d[1:] * d[:-1] < 0))
        f2 = crosses >= 2
        rng = H[w].max() / L[w].min() - 1
        f3 = rng < 0.08
        f4 = A["V20"][i] < A["V60"][i] * 0.8
        n_side = int(f1) + int(f2) + int(f3) + int(f4)
        if not fast:
            out["sideways"] = [
                ("① 20일선 평평(10일 ±1%)", bool(f1), f"{(s20[i] / s20[i - 10] - 1) * 100:+.2f}%"),
                ("② 이평선 꼬임(5·20일선 교차 ≥2회)", f2, f"{crosses}회"),
                ("③ 박스권(20일 고저폭 <8%)", bool(f3), f"{rng * 100:.1f}%"),
                ("④ 거래량 고갈(20일평균 <60일평균×0.8)", bool(f4), f"{A['V20'][i] / A['V60'][i]:.2f}배"),
            ]
        add(f"횡보장 아님 (해당 {n_side}/4, {p.sideways_rest_count}개 이상이면 쉼)",
            n_side < p.sideways_rest_count, f"{n_side}개 해당")

        # ---- 셋업
        aligned = s20[i] > s60[i] and (s60[i] > s120[i] if p.require_120 else True)
        add("정배열 " + ("20>60>120" if p.require_120 else "20>60"), aligned,
            lambda: f"20일 {s20[i]:,.2f} / 60일 {s60[i]:,.2f} / 120일 {s120[i]:,.2f}")
        add("20일선 상승(5일 전보다 위)", s20[i] > s20[i - 5], lambda: f"{s20[i - 5]:,.2f} → {s20[i]:,.2f}")
        add("종가 > 60일선", C[i] > s60[i], lambda: f"{C[i]:,.2f} vs {s60[i]:,.2f}")

        # ---- 눌림목
        hi_idx = i - 19 + int(np.argmax(H[w]))
        high20 = float(H[hi_idx])
        dd = C[i] / high20 - 1
        add(f"조정폭 {p.pb_min * 100:.0f}% ~ {p.pb_max * 100:.0f}%", p.pb_min <= dd <= p.pb_max,
            lambda: f"20일 고점 {high20:,.2f} 대비 {dd * 100:+.1f}%")

        if 10 <= hi_idx < i:
            adj_v = float(np.mean(V[hi_idx + 1:i + 1]))
            pre_v = float(np.mean(V[hi_idx - 10:hi_idx]))
            pb_low = float(np.min(L[hi_idx + 1:i + 1]))
            out["pb_low"] = pb_low
            add("조정 거래량 감소", adj_v < pre_v, lambda: f"조정기간 평균 {adj_v:,.0f} vs 고점 직전10일 {pre_v:,.0f}")
        else:
            pb_low = float(L[i])
            out["pb_low"] = pb_low
            add("조정 거래량 감소", False, "눌림 구간 없음(오늘이 20일 고점 근처)")

        near20 = abs(L[i] / s20[i] - 1) <= 0.02
        strong = s20[i] / s20[i - 5] - 1 >= 0.03
        near5 = strong and abs(L[i] / s5[i] - 1) <= 0.01
        add("지지 위치(저가가 20일선 ±2%, 강한 추세면 5일선 ±1%)", near20 or near5,
            lambda: f"저가 {L[i]:,.2f} / 20일선 {s20[i]:,.2f} ({(L[i] / s20[i] - 1) * 100:+.1f}%)"
            + (" / 5일선 허용(강한 추세)" if strong else ""))

        # ---- 트리거
        add("양봉", C[i] > O[i], lambda: f"시가 {O[i]:,.2f} → 종가 {C[i]:,.2f}")
        add("종가 > 20일선", C[i] > s20[i], lambda: f"{C[i]:,.2f} vs {s20[i]:,.2f}")
        add("거래량 > 전일 & ≥ 20일평균의 80%",
            V[i] > V[i - 1] and V[i] >= 0.8 * A["V20"][i],
            lambda: f"당일 {V[i]:,.0f} / 전일 {V[i - 1]:,.0f} / 20일평균 {A['V20'][i]:,.0f}")

        # ---- 금지: 최근 20일 내 대량 장대음봉
        big = bool(np.any(A["BIGBEAR"][w]))
        add("고점 대량 장대음봉 없음(20일 내)", not big, "발견 → 패스" if big else "없음")

        # ---- 진입가 / 손절 / 목표 / 손익비
        entry = float(C[i] + tick(C[i], krw))
        floor_stop = entry * (1 - p.max_loss)
        if p.stop_mode == "sma20_-3%":
            raw_stop = float(s20[i] * 0.97)
        else:
            raw_stop = pb_low * (1 - p.support_buffer) - tick(pb_low, krw)
        stop = max(raw_stop, floor_stop)
        target = high20
        rr = (target - entry) / (entry - stop) if entry > stop else float("nan")
        out.update(entry=entry, stop=stop, target=target, rr=rr, high20=high20)
        add(f"손익비 ≥ {p.rr_min}", (not math.isnan(rr)) and rr >= p.rr_min,
            lambda: f"진입 {entry:,.2f} / 목표 {target:,.2f} / 손절 {stop:,.2f} → {rr:.2f}")
    except _Stop:
        return out
    out["pass"] = all(ok for _, ok, _ in out["checks"]) if not fast else True
    return out


# --------------------------------------------------------------------------- #
# 자금 관리
# --------------------------------------------------------------------------- #
def size_position(entry: float, stop: float, account: float, avg_value_20: float, p: Params) -> dict:
    stop_pct = (entry - stop) / entry
    if stop_pct <= 0:
        return {"ok": False, "reason": "손절폭 계산 불가"}
    risk_amt = account * p.risk_per_trade
    amt = risk_amt / stop_pct
    raw = amt
    amt = min(amt, account * p.max_pos_frac)
    capped = []
    if raw > account * p.max_pos_frac:
        capped.append("최대 비중 적용")
    if avg_value_20 and not np.isnan(avg_value_20):
        liq = avg_value_20 * p.liq_cap
        if amt > liq:
            amt = liq
            capped.append("유동성 상한(20일 평균 거래대금의 2%) 적용")
    if amt < account * p.min_pos_frac:
        return {"ok": False, "reason": f"최소 금액({account * p.min_pos_frac:,.0f}) 미달 → 건너뜀",
                "stop_pct": stop_pct, "amount": amt}
    return {"ok": True, "amount": amt, "shares": int(amt // entry), "stop_pct": stop_pct,
            "risk_amt": risk_amt, "notes": capped}


# --------------------------------------------------------------------------- #
# 매매 시뮬레이션
# --------------------------------------------------------------------------- #
def _simulate(A: dict, i: int, ev: dict, p: Params, krw: bool) -> dict:
    n = len(A["Close"])
    O, H, L, C, V = (A[k] for k in ("Open", "High", "Low", "Close", "Volume"))
    entry, target, pb_low = ev["entry"], ev["target"], ev["pb_low"]
    hard = entry * (1 - p.max_loss)
    partial, r1 = False, 0.0
    hi_since = entry
    j = i
    for j in range(i + 1, n):
        days = j - i
        hi_since = max(hi_since, H[j])
        # 1) 본전 스톱 (1차 익절 이후)
        if partial and L[j] <= entry:
            px = O[j] if O[j] < entry else entry
            return _close(A, i, j, ev, 0.5 * r1 + 0.5 * (px / entry - 1), "본전 스톱", p)
        # 2) 최대 손실
        if L[j] <= hard:
            px = min(O[j], hard)
            r = px / entry - 1
            return _close(A, i, j, ev, _blend(r1, r, partial), "최대손실 -7%", p)
        # 3) 1차 익절
        if not partial and H[j] >= target:
            px = max(O[j], target)
            r1, partial = px / entry - 1, True
        # 4) 종가 기준 규칙
        cpx = C[j] - tick(C[j], krw)
        r_c = _blend(r1, cpx / entry - 1, partial)   # 1차 익절 후면 절반씩 합산
        if p.stop_mode == "sma20_-3%":
            broke = C[j] < A["S20"][j] * 0.97
            lbl = "20일선 -3% 이탈"
        else:
            broke = C[j] < pb_low * (1 - p.support_buffer)
            lbl = "지지 붕괴(눌림 저점 이탈)"
        if broke:
            return _close(A, i, j, ev, r_c, lbl, p)
        if C[j] < A["S20"][j] and V[j] >= 1.5 * A["V20"][j]:
            return _close(A, i, j, ev, r_c, "거래량 동반 20일선 이탈", p)
        if A["BIGBEAR"][j]:
            return _close(A, i, j, ev, r_c, "긴급 청산(대량 장대음봉)", p)
        if partial and C[j] < A["S5"][j]:
            return _close(A, i, j, ev, r_c, "2차 익절(5일선 이탈)", p)
        if days >= p.time_stop_days and not partial and hi_since < entry * (1 + p.time_stop_gain):
            return _close(A, i, j, ev, r_c, f"시간 손절({p.time_stop_days}일 +{p.time_stop_gain * 100:.0f}% 미달)", p)
    # 미청산: 마지막 종가로 평가
    last = C[n - 1]
    t = _close(A, i, n - 1, ev, _blend(r1, last / entry - 1, partial), "보유 중", p)
    t["status"] = "보유"
    return t


def _blend(r1: float, r: float, partial: bool) -> float:
    """1차 익절(절반 r1) 이후면 나머지 절반 수익 r과 합산, 아니면 r."""
    return 0.5 * r1 + 0.5 * r if partial else r


def _close(A, i, j, ev, ret, reason, p: Params) -> dict:
    ret_net = ret - p.cost_round_trip
    return {
        "entry_date": A["_index"][i], "exit_date": A["_index"][j], "days": j - i,
        "entry": ev["entry"], "stop": ev["stop"], "target": ev["target"],
        "stop_pct": (ev["entry"] - ev["stop"]) / ev["entry"], "ret": ret_net, "reason": reason,
        "status": "익절" if ret_net > 0 else "손절", "tv": A["TV"][i], "tv20": A["TV20"][i],
        "entry_i": i, "exit_i": j,
    }


def backtest_symbol(symbol: str, hist: pd.DataFrame, p: Params, start=None, end=None,
                    mkt_ok: pd.Series | None = None) -> list[dict]:
    """한 종목의 신호 → 청산을 시간순으로 시뮬레이션 (보유 중에는 새 진입 없음)."""
    A = prepare(hist)
    krw = is_krw(symbol)
    idx = A["_index"]
    n = len(idx)
    cand = prescreen(A, p, krw)
    if start is not None:
        cand &= idx >= pd.Timestamp(start)
    if end is not None:
        cand &= idx <= pd.Timestamp(end)
    cand[n - 1:] = False  # 마지막 봉은 다음 날이 없어 진입 불가
    m_ok = _market_ok_aligned(mkt_ok, idx) if p.market_filter else None

    trades, next_free = [], 0
    for i in np.flatnonzero(cand):
        if i < next_free:
            continue
        ev = evaluate(A, int(i), p, krw, bool(m_ok[i]) if m_ok is not None else True, fast=True)
        if ev["pass"]:
            t = _simulate(A, int(i), ev, p, krw)
            t["symbol"] = symbol
            trades.append(t)
            next_free = t["exit_i"] + 1
    return trades


def backtest(symbols: list[str], p: Params, account: float = 3_000_000_000, start=None, end=None,
             period: str = "3y", sectors: dict | None = None, progress=None) -> dict:
    """여러 종목 백테스트 + 계좌 단위 자금 배분(손실한도·최소/최대·동시보유·업종 2종목)."""
    idx_cache: dict[str, pd.Series] = {}
    raw, errors = [], []
    for k, sym in enumerate(symbols):
        try:
            h = load_history(sym, period)
            mk = None
            if p.market_filter and is_krw(sym):
                ix = index_symbol(sym)
                if ix not in idx_cache:
                    idx_cache[ix] = market_ok_series(ix, period)
                mk = idx_cache[ix]
            raw += backtest_symbol(sym, h, p, start, end, mk)
        except Exception as e:  # noqa: BLE001 - 한 종목 실패가 전체를 멈추지 않게
            log.warning("백테스트 실패 %s: %s", sym, e)
            errors.append(f"{sym}: {e}")
        if progress:
            progress((k + 1) / len(symbols))

    # 계좌 배분: 진입일 순 → 거래대금 큰 순
    raw.sort(key=lambda t: (t["entry_date"], -t["tv"]))
    open_pos, done, skipped = [], [], []
    for t in raw:
        open_pos = [o for o in open_pos if o["exit_date"] >= t["entry_date"]]
        sz = size_position(t["entry"], t["stop"], account, t["tv20"] if is_krw(t["symbol"]) else 0, p)
        if not sz["ok"]:
            skipped.append((t["symbol"], t["entry_date"], sz["reason"]))
            continue
        if sum(o["amount"] for o in open_pos) + sz["amount"] > account:
            skipped.append((t["symbol"], t["entry_date"], "계좌 한도 초과"))
            continue
        sec = (sectors or {}).get(t["symbol"])
        if sec and sum(1 for o in open_pos if (sectors or {}).get(o["symbol"]) == sec) >= p.max_per_sector:
            skipped.append((t["symbol"], t["entry_date"], f"같은 업종({sec}) {p.max_per_sector}종목 초과"))
            continue
        t = {**t, "amount": sz["amount"], "pnl": sz["amount"] * t["ret"]}
        open_pos.append(t)
        done.append(t)

    df = pd.DataFrame(done)
    summary = {"trades": len(done), "skipped": len(skipped), "errors": errors}
    if not df.empty:
        wins = df[df["ret"] > 0]
        loss = df[df["ret"] <= 0]
        summary.update(
            win_rate=len(wins) / len(df), avg_win=wins["ret"].mean() if len(wins) else 0.0,
            avg_loss=loss["ret"].mean() if len(loss) else 0.0, pnl=df["pnl"].sum(),
            pnl_pct=df["pnl"].sum() / account,
            n_win=int((df["status"] == "익절").sum()), n_loss=int((df["status"] == "손절").sum()),
            n_hold=int((df["status"] == "보유").sum()),
            payoff=(wins["ret"].mean() / abs(loss["ret"].mean())) if len(wins) and len(loss) else None,
        )
    return {"trades": df, "summary": summary, "skipped": skipped}


# --------------------------------------------------------------------------- #
# 현재 신호 스캔 / AI 프롬프트용 요약
# --------------------------------------------------------------------------- #
def scan_symbol(symbol: str, p: Params, account: float, hist: pd.DataFrame | None = None) -> dict:
    h = hist if hist is not None else load_history(symbol, "2y")
    A = prepare(h)
    i = len(A["Close"]) - 1
    krw = is_krw(symbol)
    m_ok = True
    if p.market_filter and krw:
        m_ok = bool(_market_ok_aligned(market_ok_series(index_symbol(symbol)), A["_index"])[i])
    ev = evaluate(A, i, p, krw, m_ok)
    ev["date"] = A["_index"][i]
    ev["symbol"] = symbol
    ev["size"] = size_position(ev["entry"], ev["stop"], account, A["TV20"][i] if krw else 0, p) if ev["entry"] else None
    return ev


def strategy_prompt(symbol: str, hist: pd.DataFrame, p: Params = V2, account: float = 3_000_000_000) -> str:
    """AI 분석 프롬프트에 붙이는 '지지 눌림목 전략' 결과 (조건별 근거는 넣지 않음)."""
    try:
        ev = scan_symbol(symbol, p, account, hist)
    except Exception as e:  # noqa: BLE001
        return f"- 판정 불가: {e}"
    if not ev["pass"]:
        return f"- {ev['date']:%Y-%m-%d} 기준: 신호 없음"
    line = f"- {ev['date']:%Y-%m-%d} 기준: 매수 신호 / 진입 {ev['entry']:,.2f} · 목표 {ev['target']:,.2f} · 손절 {ev['stop']:,.2f}"
    sz = ev.get("size")
    if sz:
        line += f" · 매수금액 {sz['amount']:,.0f}" if sz["ok"] else f" · {sz['reason']}"
    return line


RULES_MD = """
**철학 7원칙** — 캔들·거래량 우선 / 거래량 없는 돌파 불신 / 이평선 5·20·60·120 기본값은 지지 확인용 /
돌파 추격 대신 눌림목 진입 / 대형주만, 횡보장은 쉼 / 시나리오 먼저, 지지 깨지면 즉시 손절 / 소액 반복

**매매 시각** — 15:15 신호 점검 → 15:20~15:30 종가 단일가 매수(종가+1호가) →
다음날 08:30 접수 / 09:00 시가 또는 장중 지정가로 1차 익절(절반, 직전 20일 고점) →
나머지는 매수가 본전 스톱, 종가가 5일선 아래면 15:30 2차 익절

**손절** — 매수가 -7%(시가/장중 스톱) · 종가가 눌림 저점 아래 · 거래량 1.5배 동반 20일선 이탈 ·
보유 중 고점 대량 장대음봉 · 10거래일 내 +3% 미달(시간 손절)

**자금 관리** — 1회 손실 한도 계좌 0.5% → 매수금액 = 한도 ÷ 손절폭, 최소 10%·최대 20%(30억 기준 3억/6억),
20일 평균 거래대금의 2% 이하, 동시보유 계좌 이내·같은 업종 2종목, 비용 왕복 0.3% + 불리한 1호가
"""
