"""퀀트 트레이딩 17전략 엔진.

종목 단위 판정(analyze) + 유니버스 단위 도구(cross_section / stat_arb_universe / find_pairs) +
계산 도구(carry_calc / execution_plan).

일봉 데이터로 실제 계산 가능한 전략은 신호·백테스트까지, 호가창/체결 연동이 필요한 전략(6 시장조성,
17 집행)은 분석·계획 도구로만 제공한다(자동 주문 없음).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd
import yfinance as yf

from strategy import is_krw, load_history, tick

COST_ONE_WAY = 0.0015  # 왕복 0.3%

STRATEGY_NAMES = {
    1: "모멘텀", 2: "평균회귀", 3: "통계적 차익거래", 4: "페어 트레이딩", 5: "추세 추종",
    6: "시장조성", 7: "이벤트 드리븐", 8: "팩터 투자", 9: "캐리 트레이드", 10: "변동성 차익거래",
    11: "옵션 전략", 12: "횡단면 알파", 13: "단기 반전", 14: "돌파 매매", 15: "국면 전환",
    16: "머신러닝 알파", 17: "집행 알고리즘",
}


@dataclass
class Sig:
    no: int
    name: str
    kind: str                 # 방향 / 시장 / 변동성 / 참고 / N/A
    signal: int | None        # +1 매수 우호, -1 매도·회피, 0 중립, None 해당없음
    detail: str

    @property
    def label(self) -> str:
        return {1: "🟢 매수", -1: "🔴 매도/회피", 0: "⚪ 중립"}.get(self.signal, "— 참고")


# --------------------------------------------------------------------------- #
# 공통 유틸
# --------------------------------------------------------------------------- #
def bench_symbol(sym: str) -> str:
    if sym.upper().endswith(".KQ"):
        return "^KQ11"
    return "^KS11" if is_krw(sym) else "^GSPC"


def _rsi(c: pd.Series, n: int = 14) -> pd.Series:
    d = c.diff()
    g = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    l = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + g / l.replace(0, np.nan))


def _hold(enter: np.ndarray, exit_: np.ndarray, index) -> pd.Series:
    pos, on = np.zeros(len(enter)), False
    for i in range(len(enter)):
        if not on and enter[i]:
            on = True
        elif on and exit_[i]:
            on = False
        pos[i] = 1.0 if on else 0.0
    return pd.Series(pos, index=index)


def run_bt(close: pd.Series, pos: pd.Series) -> pd.Series:
    ret = close.pct_change().fillna(0)
    p = pos.reindex(close.index).fillna(0.0).astype(float)
    turn = p.diff().abs().fillna(p.abs())
    return p.shift(1).fillna(0) * ret - turn * COST_ONE_WAY


def perf(sr: pd.Series, pos: pd.Series | None = None) -> dict:
    eq = (1 + sr).cumprod()
    yrs = max(len(sr) / 252, 1e-9)
    sd = sr.std()
    return {
        "CAGR": eq.iloc[-1] ** (1 / yrs) - 1,
        "연변동성": sd * math.sqrt(252),
        "샤프": (sr.mean() / sd * math.sqrt(252)) if sd > 0 else np.nan,
        "MDD": (eq / eq.cummax() - 1).min(),
        "누적": eq.iloc[-1] - 1,
        "매매횟수": int((pos.diff() > 0).sum()) if pos is not None else None,
        "시장노출": float(pos.mean()) if pos is not None else 1.0,
    }


# --------------------------------------------------------------------------- #
# 시계열 포지션 규칙 (신호 + 백테스트 공용)
# --------------------------------------------------------------------------- #
def pos_momentum(c: pd.Series, **_) -> pd.Series:           # 1
    return ((c.shift(21) / c.shift(252) - 1 > 0) & (c / c.shift(126) - 1 > 0)).astype(float)


def pos_meanrev(c: pd.Series, **_) -> pd.Series:            # 2
    z = (c - c.rolling(20).mean()) / c.rolling(20).std()
    return _hold((z < -1.5).to_numpy(), (z >= 0).to_numpy(), c.index)


def pos_trend(c: pd.Series, **_) -> pd.Series:              # 5
    s50, s200 = c.rolling(50).mean(), c.rolling(200).mean()
    return ((c > s200) & (s50 > s200)).astype(float)


def pos_reversal(c: pd.Series, v: pd.Series, **_) -> pd.Series:   # 13
    r3 = c.pct_change(3)
    z = (r3 - r3.rolling(120).mean()) / r3.rolling(120).std()
    spike = v >= 1.5 * v.rolling(20).mean().shift(1)
    entry = ((z <= -2) & spike).astype(float)
    return entry.rolling(3, min_periods=1).max()


def pos_breakout(c: pd.Series, v: pd.Series, h: pd.Series, l: pd.Series, **_) -> pd.Series:  # 14
    hi55 = h.rolling(55).max().shift(1)
    lo20 = l.rolling(20).min().shift(1)
    vol_ok = v >= 1.5 * v.rolling(20).mean().shift(1)
    return _hold(((c > hi55) & vol_ok).to_numpy(), (c < lo20).to_numpy(), c.index)


BACKTESTABLE = {1: pos_momentum, 2: pos_meanrev, 5: pos_trend, 13: pos_reversal, 14: pos_breakout}


# --------------------------------------------------------------------------- #
# 종목 단위 신호 17종
# --------------------------------------------------------------------------- #
def s_momentum(c):
    if len(c) < 253:
        return Sig(1, "모멘텀", "방향", None, "데이터 부족(253봉 필요)")
    r121, r6 = c.iloc[-22] / c.iloc[-253] - 1, c.iloc[-1] / c.iloc[-127] - 1
    sig = 1 if (r121 > 0 and r6 > 0) else -1 if (r121 < 0 and r6 < 0) else 0
    return Sig(1, "모멘텀", "방향", sig, f"12-1개월 {r121 * 100:+.1f}% / 6개월 {r6 * 100:+.1f}% (둘 다 +면 매수, 둘 다 -면 회피)")


def s_meanrev(c):
    m, sd = c.rolling(20).mean().iloc[-1], c.rolling(20).std().iloc[-1]
    z = (c.iloc[-1] - m) / sd
    sig = 1 if z < -2 else -1 if z > 2 else 0
    return Sig(2, "평균회귀", "방향", sig, f"20일 평균 대비 z={z:.2f} (±2 밖이면 반대 포지션), RSI14 {_rsi(c).iloc[-1]:.0f}")


def s_statarb(c, bc):
    if bc is None:
        return Sig(3, "통계적 차익거래", "방향", None, "벤치마크 데이터 없음 (유니버스 탭에서 바스켓 기준 계산)")
    df = pd.concat([c.pct_change(), bc.pct_change()], axis=1, join="inner").dropna().tail(250)
    if len(df) < 130:
        return Sig(3, "통계적 차익거래", "방향", None, "데이터 부족")
    y, x = df.iloc[:, 0], df.iloc[:, 1]
    beta = np.cov(y.tail(120), x.tail(120))[0, 1] / x.tail(120).var()
    resid = y - beta * x
    s5 = resid.rolling(5).sum()
    z = (s5.iloc[-1] - s5.tail(120).mean()) / s5.tail(120).std()
    sig = 1 if z < -2 else -1 if z > 2 else 0
    return Sig(3, "통계적 차익거래", "방향", sig,
               f"시장(β={beta:.2f}) 제거 후 5일 잔차 z={z:.2f} (<-2면 복귀 기대 매수, >2면 매도). 시장중립은 매수/매도 짝으로 구성")


def pair_stats(a: pd.Series, b: pd.Series) -> dict | None:
    df = pd.concat([a, b], axis=1, join="inner").dropna().tail(252)
    if len(df) < 120:
        return None
    la, lb = np.log(df.iloc[:, 0]), np.log(df.iloc[:, 1])
    corr = df.pct_change().dropna().corr().iloc[0, 1]
    beta = np.polyfit(lb, la, 1)[0]
    spread = la - beta * lb
    z = (spread.iloc[-1] - spread.mean()) / spread.std()
    ds, lag = spread.diff().dropna(), spread.shift(1).dropna()
    k = np.polyfit(lag.loc[ds.index] - spread.mean(), ds, 1)[0]
    hl = -math.log(2) / k if k < 0 else float("inf")
    p = None
    try:
        from statsmodels.tsa.stattools import coint
        p = float(coint(la, lb)[1])
    except Exception:
        pass
    return {"corr": corr, "beta": beta, "z": z, "half_life": hl, "coint_p": p, "spread": spread}


def s_pairs(sym, c, peers):
    if not peers:
        return Sig(4, "페어 트레이딩", "방향", None, "비교 종목(유니버스) 필요 — 유니버스 입력 시 자동으로 최적 짝을 탐색")
    best = None
    for k, h in peers.items():
        if k == sym:
            continue
        st = pair_stats(c, h["Close"])
        if st and (best is None or st["corr"] > best[1]["corr"]):
            best = (k, st)
    if not best:
        return Sig(4, "페어 트레이딩", "방향", None, "짝 후보 없음")
    k, st = best
    ok = st["corr"] >= 0.7 and st["beta"] > 0 and 2 <= st["half_life"] <= 60
    sig = 0
    if ok:
        sig = -1 if st["z"] > 2 else 1 if st["z"] < -2 else 0
    pv = f", 공적분 p={st['coint_p']:.3f}" if st["coint_p"] is not None else ""
    return Sig(4, "페어 트레이딩", "방향", sig,
               f"최적 짝 {k}: 상관 {st['corr']:.2f}, 스프레드 z={st['z']:.2f}, 반감기 {st['half_life']:.0f}일{pv}"
               + ("" if ok else " (상관≥0.7·헤지비율>0·반감기 2~60일 미충족 → 거래 부적합)")
               + (f" → z>2면 {sym} 매도·{k} 매수, z<-2면 반대" if ok else ""))


def s_trend(c):
    if len(c) < 200:
        return Sig(5, "추세 추종", "방향", None, "데이터 부족(200봉 필요)")
    s50, s200 = c.rolling(50).mean().iloc[-1], c.rolling(200).mean().iloc[-1]
    p = c.iloc[-1]
    sig = 1 if (p > s200 and s50 > s200) else -1 if (p < s200 and s50 < s200) else 0
    return Sig(5, "추세 추종", "방향", sig, f"종가 {p:,.2f} / 50일 {s50:,.2f} / 200일 {s200:,.2f}")


def s_marketmaking(sym, h):
    hh, ll = h["High"], h["Low"]
    beta = (np.log(hh / ll) ** 2).rolling(2).sum()
    gamma = np.log(hh.rolling(2).max() / ll.rolling(2).min()) ** 2
    alpha = (np.sqrt(2 * beta) - np.sqrt(beta)) / (3 - 2 * np.sqrt(2)) - np.sqrt(gamma / (3 - 2 * np.sqrt(2)))
    spread = (2 * (np.exp(alpha) - 1) / (1 + np.exp(alpha))).clip(lower=0).tail(60).mean()
    px = h["Close"].iloc[-1]
    tk = tick(px, is_krw(sym)) / px
    return Sig(6, "시장조성", "참고", None,
               f"추정 유효스프레드(Corwin-Schultz) {spread * 100:.2f}% vs 1호가 {tk * 100:.3f}% "
               f"→ {'스프레드 여지 있음' if spread > 3 * tk else '호가단위에 근접(경쟁 치열)'}. "
               "호가창·초단타 인프라 필요 → 개인 자동화 대상 아님(참고용)")


def s_event(sym, c, tkr):
    try:
        ed = tkr.earnings_dates
    except Exception:
        ed = None
    if ed is None or len(ed) == 0:
        return Sig(7, "이벤트 드리븐", "방향", None, "실적 발표일 데이터 없음")
    today = pd.Timestamp.today().normalize()
    dts = pd.DatetimeIndex([d.tz_localize(None) if d.tzinfo else d for d in ed.index]).normalize()
    fut = [d for d in dts if d >= today]
    past = [d for d in dts if d < today]
    react = []
    for d in past[:12]:
        pos = c.index.searchsorted(d)
        if 1 <= pos < len(c) - 1:
            react.append(c.iloc[pos + 1] / c.iloc[pos - 1] - 1)  # 발표 전일 → 발표 다음날
    avg_abs = np.mean(np.abs(react)) if react else None
    txt = f"과거 실적 반응 평균 ±{avg_abs * 100:.1f}%" if avg_abs is not None else "과거 반응 데이터 없음"
    sig, note = 0, ""
    if fut:
        dd = (min(fut) - today).days
        note = f"다음 발표 {min(fut):%Y-%m-%d} (D-{dd})"
        if dd <= 7:
            note += " → 발표 임박: 이벤트 리스크, 신규 진입 보수적"
    if react and past:
        last_d = past[0]
        days_since = (today - last_d).days
        if days_since <= 30:
            sig = 1 if react[0] > 0.03 else -1 if react[0] < -0.03 else 0
            note += f" / 직전 발표 반응 {react[0] * 100:+.1f}% ({days_since}일 전, 실적발표 후 드리프트 {'+' if sig > 0 else '-' if sig < 0 else '없음'})"
    return Sig(7, "이벤트 드리븐", "방향", sig, f"{note or '예정 이벤트 없음'} / {txt}")


def s_factor(c, info):
    per, pbr = (info or {}).get("trailingPE"), (info or {}).get("priceToBook")
    roe, pm = (info or {}).get("returnOnEquity"), (info or {}).get("profitMargins")
    if all(x is None for x in (per, pbr, roe, pm)):
        return Sig(8, "팩터 투자", "방향", None, "재무 데이터 조회 실패(야후 제한) — 잠시 후 재시도")
    vol = c.pct_change().tail(250).std() * math.sqrt(252)
    mom = c.iloc[-22] / c.iloc[-253] - 1 if len(c) >= 253 else None
    tests = [
        ("가치(PER<15)", per is not None and 0 < per < 15), ("가치(PBR<1.5)", pbr is not None and 0 < pbr < 1.5),
        ("퀄리티(ROE>10%)", roe is not None and roe > 0.10), ("퀄리티(순이익률>10%)", pm is not None and pm > 0.10),
        ("저변동(연 35%↓)", vol < 0.35), ("모멘텀(12-1>0)", mom is not None and mom > 0),
    ]
    n = sum(ok for _, ok in tests)
    sig = 1 if n >= 4 else -1 if n <= 1 else 0
    return Sig(8, "팩터 투자", "방향", sig, f"{n}/6 충족 — " + ", ".join(f"{k}{'✓' if ok else '✗'}" for k, ok in tests))


def s_carry(sym, info):
    if is_krw(sym):
        return Sig(9, "캐리 트레이드", "참고", None, "통화쌍 전략 — '도구' 탭 캐리 계산기로 원/달러·엔/달러 등 금리차 대비 환변동 평가")
    dy = (info or {}).get("dividendYield")
    if dy is None:
        return Sig(9, "캐리 트레이드", "참고", None, "주식은 배당수익률 vs 조달금리가 캐리. 배당 데이터 없음 — '도구' 탭 참고")
    try:
        rf = yf.Ticker("^IRX").history(period="5d")["Close"].iloc[-1]
    except Exception:
        rf = None
    d = dy  # yfinance 1.x 는 이미 % 단위
    return Sig(9, "캐리 트레이드", "참고", None,
               f"배당수익률 {d:.2f}%" + (f" vs 미 단기금리 {rf:.2f}% → 캐리 {d - rf:+.2f}%p" if rf is not None else ""))


def _atm_iv(tkr, price):
    exps = tkr.options
    if not exps:
        return None
    today = pd.Timestamp.today().normalize()
    exp = next((e for e in exps if (pd.Timestamp(e) - today).days >= 25), exps[-1])
    ch = tkr.option_chain(exp)
    calls, puts = ch.calls, ch.puts
    ci = (calls["strike"] - price).abs().idxmin()
    pi = (puts["strike"] - price).abs().idxmin()
    iv = float(np.nanmean([calls.loc[ci, "impliedVolatility"], puts.loc[pi, "impliedVolatility"]]))
    return {"exp": exp, "days": (pd.Timestamp(exp) - today).days, "iv": iv, "calls": calls, "puts": puts, "ci": ci}


def s_volarb(sym, c, tkr):
    r = c.pct_change().dropna()
    lam, var = 0.94, r.iloc[:20].var()
    for x in r.iloc[20:]:
        var = lam * var + (1 - lam) * x * x
    ewma = math.sqrt(var * 252)
    rv20 = r.tail(20).std() * math.sqrt(252)
    base = f"실현변동성 20일 {rv20 * 100:.0f}% / EWMA 예측 {ewma * 100:.0f}%"
    if is_krw(sym):
        return Sig(10, "변동성 차익거래", "참고", None, base + " — 국내 개별종목 옵션 데이터 없음(미국 종목에서 IV 비교 가능)")
    try:
        o = _atm_iv(tkr, c.iloc[-1])
    except Exception:
        o = None
    if not o:
        return Sig(10, "변동성 차익거래", "참고", None, base + " — 옵션 체인 없음")
    if o["iv"] < 0.05:
        return Sig(10, "변동성 차익거래", "참고", None, base + " — 내재변동성 값이 비정상(장 마감·호가 없음), 장중에 다시 확인")
    ratio = o["iv"] / ewma
    view = "내재변동성 고평가 → 변동성 매도(프리미엄 수취) 우위" if ratio > 1.2 else \
           "내재변동성 저평가 → 변동성 매수(보험·스트래들) 우위" if ratio < 0.8 else "내재≈예측 → 우위 없음"
    return Sig(10, "변동성 차익거래", "변동성", 0, f"{base} / ATM IV {o['iv'] * 100:.0f}% ({o['days']}일) → IV/예측 {ratio:.2f}: {view}")


def s_options(sym, c, tkr):
    if is_krw(sym):
        return Sig(11, "옵션 전략", "참고", None, "국내 개별종목 옵션 데이터 없음 (미국 종목에서 커버드콜/보호풋 비용 계산)")
    try:
        o = _atm_iv(tkr, c.iloc[-1])
    except Exception:
        o = None
    if not o:
        return Sig(11, "옵션 전략", "참고", None, "옵션 체인 없음")
    px = c.iloc[-1]
    calls, puts = o["calls"], o["puts"]

    def mid(row):
        b, a = row.get("bid", 0), row.get("ask", 0)
        return (b + a) / 2 if b and a else row.get("lastPrice", np.nan)

    atm_call = mid(calls.loc[o["ci"]])
    pr = puts.loc[(puts["strike"] - px * 0.95).abs().idxmin()]
    put_cost = mid(pr)
    otm = calls.loc[(calls["strike"] - px * 1.05).abs().idxmin()]
    cc = mid(otm)
    return Sig(11, "옵션 전략", "참고", None,
               f"만기 {o['exp']}({o['days']}일): 5% OTM 커버드콜 수취 {cc / px * 100:.2f}% / "
               f"5% OTM 보호풋 비용 {put_cost / px * 100:.2f}% / ATM 콜 {atm_call / px * 100:.2f}% (연환산 약 {cc / px * 365 / o['days'] * 100:.0f}%)")


def s_xsec(sym, peers):
    if not peers or len(peers) < 5:
        return Sig(12, "횡단면 알파", "방향", None, "유니버스 5종목 이상 필요 — 유니버스 탭에서 점수 순위 산출")
    tbl = cross_section(peers)
    if sym not in tbl.index:
        return Sig(12, "횡단면 알파", "방향", None, "유니버스에 해당 종목 없음")
    rk = int(tbl.index.get_loc(sym)) + 1
    n = len(tbl)
    pct = 1 - (rk - 1) / (n - 1)
    sig = 1 if pct >= 0.8 else -1 if pct <= 0.2 else 0
    return Sig(12, "횡단면 알파", "방향", sig, f"유니버스 {n}종목 중 종합점수 {rk}위 (상위 20%면 롱, 하위 20%면 숏·회피)")


def s_reversal(c, v):
    r3 = c.pct_change(3)
    z = (r3.iloc[-1] - r3.tail(120).mean()) / r3.tail(120).std()
    vr = v.iloc[-1] / v.rolling(20).mean().iloc[-2]
    spike = vr >= 1.5
    sig = 1 if (z <= -2 and spike) else -1 if (z >= 2 and spike) else 0
    return Sig(13, "단기 반전", "방향", sig, f"3일 수익률 {r3.iloc[-1] * 100:+.1f}% (z={z:.2f}), 거래량 {vr:.1f}배 → 급락+거래량 폭증이면 반등 기대, 급등+폭증이면 되돌림")


def s_breakout(c, v, h, l):
    if len(c) < 60:
        return Sig(14, "돌파 매매", "방향", None, "데이터 부족")
    hi55, lo20 = h.iloc[-56:-1].max(), l.iloc[-21:-1].min()
    vr = v.iloc[-1] / v.rolling(20).mean().iloc[-2]
    p = c.iloc[-1]
    sig = 1 if (p > hi55 and vr >= 1.5) else -1 if p < lo20 else 0
    return Sig(14, "돌파 매매", "방향", sig,
               f"종가 {p:,.2f} / 55일 고점 {hi55:,.2f} / 20일 저점 {lo20:,.2f} / 거래량 {vr:.1f}배 (거래량 1.5배 이상 동반 돌파만 인정)")


def s_regime(sym, bench, vix):
    if bench is None or len(bench) < 220:
        return Sig(15, "국면 전환", "시장", None, "지수 데이터 부족")
    c = bench["Close"]
    s200 = c.rolling(200).mean().iloc[-1]
    vol20 = c.pct_change().tail(20).std() * math.sqrt(252)
    vols = c.pct_change().rolling(20).std() * math.sqrt(252)
    hi_vol = vol20 > vols.tail(252).median()
    up = c.iloc[-1] > s200
    expo = float(np.clip(0.15 / vol20, 0, 1)) if vol20 > 0 else 1.0
    label = ("상승·저변동 (공격)" if up and not hi_vol else "상승·고변동 (중립)" if up else
             "하락·고변동 (방어)" if hi_vol else "하락·저변동 (관망)")
    sig = 1 if (up and not hi_vol) else -1 if (not up and hi_vol) else 0
    vtxt = f", VIX {vix['Close'].iloc[-1]:.1f}" if vix is not None and len(vix) else ""
    return Sig(15, "국면 전환", "시장", sig,
               f"{bench_symbol(sym)} {label}: 200일선 {'위' if up else '아래'}, 20일 변동성 {vol20 * 100:.0f}%{vtxt} "
               f"→ 변동성 타깃(15%) 권장 노출 {expo * 100:.0f}%")


def ml_features(h: pd.DataFrame) -> pd.DataFrame:
    c, v = h["Close"], h["Volume"]
    f = pd.DataFrame(index=h.index)
    for n in (1, 5, 20, 60):
        f[f"r{n}"] = c.pct_change(n)
    f["vol20"] = c.pct_change().rolling(20).std()
    f["rsi"] = _rsi(c)
    f["d20"] = c / c.rolling(20).mean() - 1
    f["d60"] = c / c.rolling(60).mean() - 1
    f["vr"] = v / v.rolling(20).mean()
    f["hl"] = (h["High"] - h["Low"]) / c
    return f


def s_ml(h: pd.DataFrame):
    try:
        from sklearn.ensemble import HistGradientBoostingClassifier
        from scipy.stats import spearmanr
    except Exception:
        return Sig(16, "머신러닝 알파", "방향", None, "scikit-learn 미설치")
    if len(h) < 400:
        return Sig(16, "머신러닝 알파", "방향", None, f"학습 데이터 부족({len(h)}봉, 400봉 이상 필요 — 5년 데이터 권장)")
    H = 5
    f = ml_features(h)
    fwd = h["Close"].shift(-H) / h["Close"] - 1
    d = pd.concat([f, fwd.rename("fwd")], axis=1).replace([np.inf, -np.inf], np.nan)
    train_all = d.dropna()
    cut = int(len(train_all) * 0.7)
    tr, te = train_all.iloc[:cut - H], train_all.iloc[cut:]   # 엠바고 H일 (정보 누수 방지)
    X, cols = tr.drop(columns="fwd"), list(f.columns)
    mk = lambda: HistGradientBoostingClassifier(max_iter=80, max_depth=3, learning_rate=0.05, random_state=0)
    m = mk().fit(X, tr["fwd"] > 0)
    p_te = m.predict_proba(te[cols])[:, 1]
    acc = float(np.mean((p_te > 0.5) == (te["fwd"] > 0)))
    base = float(max((te["fwd"] > 0).mean(), 1 - (te["fwd"] > 0).mean()))
    ic = float(spearmanr(p_te, te["fwd"])[0])
    m2 = mk().fit(train_all[cols], train_all["fwd"] > 0)
    p_now = float(m2.predict_proba(f.iloc[[-1]][cols])[0, 1])
    valid = acc > base + 0.01 and ic > 0.03
    sig = (1 if p_now > 0.58 else -1 if p_now < 0.42 else 0) if valid else 0
    return Sig(16, "머신러닝 알파", "방향", sig,
               f"{H}일 후 상승확률 {p_now * 100:.0f}% | 검증(학습에 쓰지 않은 최근 30%): 적중률 {acc * 100:.1f}% (기준선 {base * 100:.1f}%), IC {ic:+.3f} → "
               + ("OOS 유의미, 신호 반영" if valid else "OOS 우위 확인 안 됨 → 신호 무시(과적합 가능성)"))


def execution_plan(order_value: float, price: float, adv_shares: float, daily_vol: float,
                   participation: float = 0.05, session_minutes: int = 390) -> dict:
    """주문 분할 계획 (TWAP). 시장충격은 제곱근 법칙으로 추정."""
    shares = order_value / price
    pct_adv = shares / adv_shares if adv_shares else float("nan")
    days = max(1, math.ceil(pct_adv / participation)) if pct_adv == pct_adv else 1
    impact_bps = 1.0 * daily_vol * math.sqrt(max(pct_adv, 0) / days) * 1e4 if pct_adv == pct_adv else float("nan")
    slices_per_day = 10 if pct_adv <= participation else 20
    return {"shares": shares, "pct_adv": pct_adv, "days": days, "slices_per_day": slices_per_day,
            "slice_shares": shares / (days * slices_per_day), "slice_interval_min": session_minutes / slices_per_day,
            "impact_bps": impact_bps,
            "advice": ("거래량 대비 미미 — 종가 단일가/지정가 일괄 가능" if pct_adv < 0.01 else
                       "TWAP/VWAP 분할 권장" if pct_adv <= participation else f"{days}일에 걸쳐 분할(일 거래량의 {participation * 100:.0f}% 이내)")}


def s_exec(sym, h, order_value):
    c, v = h["Close"], h["Volume"]
    plan = execution_plan(order_value, c.iloc[-1], v.tail(20).mean(), c.pct_change().tail(60).std())
    cur = "원" if is_krw(sym) else "USD"
    return Sig(17, "집행 알고리즘", "참고", None,
               f"주문 {order_value:,.0f}{cur} = 20일 평균 거래량의 {plan['pct_adv'] * 100:.2f}% → {plan['advice']} "
               f"(예상 충격비용 약 {plan['impact_bps']:.1f}bp, {plan['days']}일 × {plan['slices_per_day']}회 분할, 회당 약 {plan['slice_shares']:,.0f}주)")


# --------------------------------------------------------------------------- #
# 종목 종합 분석
# --------------------------------------------------------------------------- #
def analyze(symbol: str, hist: pd.DataFrame | None = None, peers: dict | None = None,
            order_value: float | None = None, bench: pd.DataFrame | None = None,
            with_ml: bool = True) -> dict:
    h = hist if hist is not None else load_history(symbol, "5y")
    c, v, hi, lo = h["Close"], h["Volume"], h["High"], h["Low"]
    tkr = yf.Ticker(symbol)
    try:
        info = tkr.info
    except Exception:
        info = {}
    if bench is None:
        try:
            bench = load_history(bench_symbol(symbol), "3y")
        except Exception:
            bench = None
    vix = None
    if not is_krw(symbol):
        try:
            vix = load_history("^VIX", "3mo")
        except Exception:
            pass
    order_value = order_value or (300_000_000 if is_krw(symbol) else 300_000)

    sigs = [
        s_momentum(c), s_meanrev(c), s_statarb(c, bench["Close"] if bench is not None else None),
        s_pairs(symbol, c, peers), s_trend(c), s_marketmaking(symbol, h), s_event(symbol, c, tkr),
        s_factor(c, info), s_carry(symbol, info), s_volarb(symbol, c, tkr), s_options(symbol, c, tkr),
        s_xsec(symbol, peers), s_reversal(c, v), s_breakout(c, v, hi, lo), s_regime(symbol, bench, vix),
        s_ml(h) if with_ml else Sig(16, "머신러닝 알파", "방향", None, "비활성화"),
        s_exec(symbol, h, order_value),
    ]
    dirs = [s.signal for s in sigs if s.kind in ("방향", "시장") and s.signal is not None]
    score = float(np.mean(dirs)) if dirs else 0.0
    label = "매수 우위" if score >= 0.3 else "매도·회피 우위" if score <= -0.3 else "중립"

    rows, eq = [], {"Buy&Hold": (1 + c.pct_change().fillna(0)).cumprod()}
    pb = perf(c.pct_change().fillna(0))
    rows.append({"전략": "Buy&Hold", **pb})
    for no, fn in BACKTESTABLE.items():
        try:
            pos = fn(c=c, v=v, h=hi, l=lo)
            sr = run_bt(c, pos)
            rows.append({"전략": f"{no}. {STRATEGY_NAMES[no]}", **perf(sr, pos)})
            eq[f"{no}. {STRATEGY_NAMES[no]}"] = (1 + sr).cumprod()
        except Exception:
            continue
    return {"signals": sigs, "score": score, "label": label, "n_dir": len(dirs),
            "perf": pd.DataFrame(rows).set_index("전략"), "equity": pd.DataFrame(eq), "info": info}


def count_signals(sigs: list[Sig]) -> dict:
    """17개 전략을 매수/중립/매도/참고(해당없음) 개수로 집계."""
    return {"매수": sum(s.signal == 1 for s in sigs), "중립": sum(s.signal == 0 for s in sigs),
            "매도": sum(s.signal == -1 for s in sigs), "참고": sum(s.signal is None for s in sigs)}


def summary_text(r: dict) -> str:
    c = count_signals(r["signals"])
    return f"17개 중 매수 {c['매수']} · 중립 {c['중립']} · 매도 {c['매도']} (참고·해당없음 {c['참고']}) → {r['label']}"


def quant_prompt(symbol: str, hist: pd.DataFrame) -> str:
    """AI 분석 프롬프트용 '퀀트 17전략' 집계 한 줄."""
    try:
        if len(hist) < 1000:  # ML/모멘텀 판정에는 5년치가 필요
            hist = load_history(symbol, "5y")
        r = analyze(symbol, hist=hist, with_ml=True)
    except Exception as e:  # noqa: BLE001
        return f"- 판정 불가: {e}"
    return "- " + summary_text(r)


# --------------------------------------------------------------------------- #
# 유니버스 단위 도구
# --------------------------------------------------------------------------- #
def _z(s: pd.Series) -> pd.Series:
    s = s.clip(s.quantile(0.05), s.quantile(0.95))
    return (s - s.mean()) / s.std() if s.std() > 0 else s * 0


def cross_section(hists: dict, with_fundamentals: bool = False) -> pd.DataFrame:
    """12. 횡단면 알파 + 8. 팩터: 모든 종목에 점수를 매겨 순위화."""
    rows = {}
    for sym, h in hists.items():
        c = h["Close"].dropna()
        if len(c) < 130:
            continue
        r = {
            "모멘텀(12-1)": c.iloc[-22] / c.iloc[-253] - 1 if len(c) >= 253 else c.iloc[-22] / c.iloc[0] - 1,
            "단기반전(-5일)": -(c.iloc[-1] / c.iloc[-6] - 1),
            "저변동": -c.pct_change().tail(60).std() * math.sqrt(252),
            "추세(200일 괴리)": c.iloc[-1] / c.rolling(200).mean().iloc[-1] - 1 if len(c) >= 200 else np.nan,
        }
        if with_fundamentals:
            try:
                i = yf.Ticker(sym).info
                r["가치(1/PER)"] = 1 / i["trailingPE"] if i.get("trailingPE") and i["trailingPE"] > 0 else np.nan
                r["가치(1/PBR)"] = 1 / i["priceToBook"] if i.get("priceToBook") and i["priceToBook"] > 0 else np.nan
                r["퀄리티(ROE)"] = i.get("returnOnEquity", np.nan)
            except Exception:
                pass
        rows[sym] = r
    df = pd.DataFrame(rows).T
    z = df.apply(_z)
    df["종합점수"] = z.mean(axis=1, skipna=True)
    df = df.sort_values("종합점수", ascending=False)
    k = max(1, math.ceil(len(df) * 0.2))
    df["포지션"] = ["롱(상위20%)" if i < k else "숏·회피(하위20%)" if i >= len(df) - k else "중립" for i in range(len(df))]
    return df


def stat_arb_universe(hists: dict) -> pd.DataFrame:
    """3. 통계적 차익거래: 동일가중 바스켓 대비 잔차 z-score. 롱/숏을 짝지어 시장중립 구성."""
    rets = pd.DataFrame({k: h["Close"].pct_change() for k, h in hists.items()}).dropna(how="all").tail(250)
    rets = rets.dropna(axis=1, thresh=200).fillna(0)
    out = {}
    for s in rets.columns:
        basket = rets.drop(columns=s).mean(axis=1)
        b = np.cov(rets[s].tail(120), basket.tail(120))[0, 1] / basket.tail(120).var()
        resid = rets[s] - b * basket
        s5 = resid.rolling(5).sum()
        z = (s5.iloc[-1] - s5.tail(120).mean()) / s5.tail(120).std()
        out[s] = {"β(바스켓)": b, "5일 잔차(%)": s5.iloc[-1] * 100, "z": z,
                  "신호": "롱(저평가 복귀)" if z < -2 else "숏(고평가 복귀)" if z > 2 else "—"}
    return pd.DataFrame(out).T.sort_values("z")


def find_pairs(hists: dict, top: int = 8) -> pd.DataFrame:
    """4. 페어 트레이딩 후보 탐색."""
    syms, rows = list(hists), []
    for i in range(len(syms)):
        for j in range(i + 1, len(syms)):
            st = pair_stats(hists[syms[i]]["Close"], hists[syms[j]]["Close"])
            if st:
                rows.append({"A": syms[i], "B": syms[j], "상관": st["corr"], "헤지비율β": st["beta"], "스프레드 z": st["z"],
                             "반감기(일)": st["half_life"], "공적분 p": st["coint_p"],
                             "신호": (f"A 매도·B 매수" if st["z"] > 2 else "A 매수·B 매도" if st["z"] < -2 else "—")
                             if st["corr"] >= 0.7 and st["beta"] > 0 and 2 <= st["half_life"] <= 60 else "부적합"})
    df = pd.DataFrame(rows)
    return df.sort_values("상관", ascending=False).head(top) if len(df) else df


def pair_backtest(a: pd.Series, b: pd.Series, entry: float = 2.0, exit_: float = 0.0) -> dict | None:
    st = pair_stats(a, b)
    if not st:
        return None
    sp = st["spread"]
    z = (sp - sp.rolling(60).mean()) / sp.rolling(60).std()
    pos = np.zeros(len(z))
    cur = 0
    for i, zv in enumerate(z.to_numpy()):
        if np.isnan(zv):
            continue
        if cur == 0 and zv > entry:
            cur = -1
        elif cur == 0 and zv < -entry:
            cur = 1
        elif cur == 1 and zv >= -exit_ or cur == -1 and zv <= exit_:
            cur = 0
        pos[i] = cur
    pos = pd.Series(pos, index=sp.index)
    pnl = pos.shift(1).fillna(0) * sp.diff().fillna(0)
    turn = pos.diff().abs().fillna(0)
    gross = 1 + abs(st["beta"])
    sr = pnl / gross - turn * COST_ONE_WAY * 2
    return {"perf": perf(sr), "equity": (1 + sr).cumprod(), "trades": int((turn > 0).sum() // 2), "beta": st["beta"]}


# --------------------------------------------------------------------------- #
# 9. 캐리 트레이드 계산기
# --------------------------------------------------------------------------- #
def carry_calc(fx_symbol: str, invest_rate_pct: float, funding_rate_pct: float, period: str = "3y") -> dict:
    """fx_symbol: 야후 환율 심볼 (예 'KRW=X' 원/달러, 'JPY=X' 엔/달러, 'AUDJPY=X').
    투자통화 금리가 높고 조달통화 금리가 낮은 쌍에서 금리차(캐리)와 환변동 리스크를 비교."""
    fx = load_history(fx_symbol, period)["Close"].dropna()
    r = np.log(fx).diff().dropna()
    vol = r.std() * math.sqrt(252)
    carry = invest_rate_pct - funding_rate_pct
    # 환율 하락(조달통화 대비 투자통화 약세)을 가정한 손익분기 연간 환변동
    return {"carry_%": carry, "fx_vol_%": vol * 100, "carry/vol": carry / (vol * 100) if vol > 0 else float("nan"),
            "worst_1y_chg_%": float((fx / fx.shift(252) - 1).min() * 100) if len(fx) > 260 else None,
            "last": float(fx.iloc[-1]),
            "verdict": ("캐리 대비 환변동 낮음 — 유리" if carry / (vol * 100) > 0.5 else
                        "캐리가 환변동에 잠식될 위험 큼" if carry / (vol * 100) < 0.25 else "보통")}
