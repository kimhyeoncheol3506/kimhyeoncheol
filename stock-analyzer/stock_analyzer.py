"""데이터 수집 + 기술적 지표 + 밸류에이션 + Claude 분석.

지원: KOSPI(.KS) / KOSDAQ(.KQ) / 넥스트레이드(.NXT 시도, 불가 시 .KS 시세로 대체) /
      NYSE·NASDAQ·다우존스 구성종목 및 지수(^DJI, ^IXIC, ^GSPC, ^KS11 ...)
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import yfinance as yf

from prompts import MACRO_SYSTEM_PROMPT, MASTER_SYSTEM_PROMPT, PORTFOLIO_SYSTEM_PROMPT

DEFAULT_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5-5")

MACRO_TICKERS = {
    "KOSPI": "^KS11",
    "KOSDAQ": "^KQ11",
    "다우존스": "^DJI",
    "나스닥": "^IXIC",
    "S&P500": "^GSPC",
    "VIX": "^VIX",
    "미국10년물금리(%)": "^TNX",
    "원/달러": "KRW=X",
    "달러인덱스": "DX-Y.NYB",
    "WTI유가": "CL=F",
    "금": "GC=F",
}


KR_NAMES = {
    "삼성전자": "005930", "SK하이닉스": "000660", "LG에너지솔루션": "373220", "삼성바이오로직스": "207940",
    "현대차": "005380", "현대자동차": "005380", "기아": "000270", "셀트리온": "068270", "KB금융": "105560",
    "네이버": "035420", "NAVER": "035420", "카카오": "035720", "POSCO홀딩스": "005490", "포스코홀딩스": "005490",
    "삼성SDI": "006400", "LG화학": "051910", "신한지주": "055550", "한화에어로스페이스": "012450",
    "에코프로": "086520", "에코프로비엠": "247540", "알테오젠": "196170", "HLB": "028300",
    "삼성전자우": "005935", "크래프톤": "259960", "두산에너빌리티": "034020", "HD현대중공업": "329180",
}


# --------------------------------------------------------------------------- #
# 티커 해석
# --------------------------------------------------------------------------- #
def resolve_ticker(query: str, market: str = "auto") -> str:
    """사용자 입력을 야후 파이낸스 티커로 변환.

    - 005930 / 005930.KS  -> 005930.KS (없으면 .KQ)
    - 005930.NXT / 넥스트레이드 선택 -> .NXT 시도, 데이터 없으면 .KS
    - AAPL, ^DJI 등은 그대로
    - 삼성전자 같은 이름은 yfinance Search 로 조회
    """
    q = query.strip().upper() if query.isascii() else query.strip()
    if not q:
        raise ValueError("종목을 입력하세요.")

    q = KR_NAMES.get(q.replace(" ", ""), q)

    if re.fullmatch(r"\d{6}", q):  # 한국 종목코드
        suffixes = [".NXT", ".KS", ".KQ"] if market == "nxt" else [".KS", ".KQ"]
        for sfx in suffixes:
            if _has_price(q + sfx):
                return q + sfx
        raise ValueError(f"{q}: 한국 거래소에서 시세를 찾지 못했습니다.")

    if re.fullmatch(r"\d{6}\.(KS|KQ|NXT)", q):
        if q.endswith(".NXT") and not _has_price(q):
            return q.replace(".NXT", ".KS")
        return q

    if q.isascii() and re.fullmatch(r"[\^A-Z0-9.\-=]{1,15}", q):
        if _has_price(q):
            return q

    try:  # 이름 검색 (예: 삼성전자, Apple)
        for item in yf.Search(query, max_results=8).quotes:
            sym = item.get("symbol")
            if sym and item.get("quoteType") in ("EQUITY", "ETF", "INDEX"):
                return sym
    except Exception:
        pass
    raise ValueError(f"'{query}' 종목을 찾지 못했습니다. 티커/종목코드로 입력해 보세요.")


def _has_price(symbol: str) -> bool:
    try:
        return not yf.Ticker(symbol).history(period="5d").empty
    except Exception:
        return False


# --------------------------------------------------------------------------- #
# 기술적 지표 (pandas_ta 없이 직접 계산: 파이썬 버전 호환성)
# --------------------------------------------------------------------------- #
def compute_indicators(hist: pd.DataFrame) -> pd.DataFrame:
    df = hist.copy()
    c, h, l, v = df["Close"], df["High"], df["Low"], df["Volume"]

    for n in (5, 20, 60, 120, 200):
        df[f"SMA_{n}"] = c.rolling(n).mean()
    df["EMA_12"] = c.ewm(span=12, adjust=False).mean()
    df["EMA_26"] = c.ewm(span=26, adjust=False).mean()

    delta = c.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    df["RSI"] = 100 - 100 / (1 + gain / loss.replace(0, np.nan))

    df["MACD"] = df["EMA_12"] - df["EMA_26"]
    df["MACD_signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_hist"] = df["MACD"] - df["MACD_signal"]

    mid, std = c.rolling(20).mean(), c.rolling(20).std()
    df["BB_upper"], df["BB_lower"] = mid + 2 * std, mid - 2 * std

    low14, high14 = l.rolling(14).min(), h.rolling(14).max()
    df["STOCH_K"] = 100 * (c - low14) / (high14 - low14).replace(0, np.nan)
    df["STOCH_D"] = df["STOCH_K"].rolling(3).mean()

    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    df["ATR"] = tr.ewm(alpha=1 / 14, adjust=False).mean()
    df["VOL_SMA_20"] = v.rolling(20).mean()
    return df


def support_resistance(df: pd.DataFrame, window: int = 5, n: int = 3):
    """최근 1년 스윙 고/저점 기반 지지·저항선 (현재가 기준 가까운 순)."""
    price = float(df["Close"].iloc[-1])
    lows = df["Low"][(df["Low"] == df["Low"].rolling(2 * window + 1, center=True).min())]
    highs = df["High"][(df["High"] == df["High"].rolling(2 * window + 1, center=True).max())]
    sup = sorted([float(x) for x in lows if x < price], reverse=True)[:n]
    res = sorted([float(x) for x in highs if x > price])[:n]
    return sup, res


def technical_summary(df: pd.DataFrame) -> dict:
    last = df.iloc[-1]
    price = float(last["Close"])
    sup, res = support_resistance(df)

    def g(k):
        v = last.get(k)
        return None if v is None or pd.isna(v) else float(v)

    smas = {n: g(f"SMA_{n}") for n in (5, 20, 60, 120, 200)}
    if all(smas[n] for n in (20, 60, 120)) and smas[20] > smas[60] > smas[120]:
        trend = "정배열(상승추세)"
    elif all(smas[n] for n in (20, 60, 120)) and smas[20] < smas[60] < smas[120]:
        trend = "역배열(하락추세)"
    else:
        trend = "혼조/횡보"

    prev = df.iloc[-2] if len(df) > 1 else last
    cross = None
    if not pd.isna(last["MACD"]) and not pd.isna(prev["MACD"]):
        if prev["MACD"] <= prev["MACD_signal"] and last["MACD"] > last["MACD_signal"]:
            cross = "골든크로스(MACD)"
        elif prev["MACD"] >= prev["MACD_signal"] and last["MACD"] < last["MACD_signal"]:
            cross = "데드크로스(MACD)"

    return {
        "price": price,
        "sma": smas,
        "trend": trend,
        "rsi": g("RSI"),
        "macd": g("MACD"),
        "macd_signal": g("MACD_signal"),
        "macd_hist": g("MACD_hist"),
        "macd_cross": cross,
        "stoch_k": g("STOCH_K"),
        "stoch_d": g("STOCH_D"),
        "bb_upper": g("BB_upper"),
        "bb_lower": g("BB_lower"),
        "atr": g("ATR"),
        "volume": g("Volume"),
        "volume_vs_20d": (g("Volume") / g("VOL_SMA_20")) if g("VOL_SMA_20") else None,
        "high_52w": float(df["High"].tail(252).max()),
        "low_52w": float(df["Low"].tail(252).min()),
        "supports": sup,
        "resistances": res,
    }


# --------------------------------------------------------------------------- #
# 펀더멘털 / 재무제표 / 실적
# --------------------------------------------------------------------------- #
def _fmt_df(df: pd.DataFrame | None, rows: list[str], max_cols: int = 4) -> str:
    if df is None or df.empty:
        return "데이터 없음"
    df = df.iloc[:, :max_cols]
    keep = [r for r in rows if r in df.index]
    if not keep:
        return "데이터 없음"
    out = df.loc[keep].copy()
    out.columns = [str(c)[:10] for c in out.columns]
    return out.map(lambda x: "N/A" if pd.isna(x) else f"{x:,.0f}").to_string()


def fetch_fundamentals(t: yf.Ticker) -> dict:
    def safe(fn):
        try:
            return fn()
        except Exception:
            return None

    info = safe(lambda: t.info) or {}
    return {
        "info": info,
        "income": safe(lambda: t.income_stmt),
        "balance": safe(lambda: t.balance_sheet),
        "cashflow": safe(lambda: t.cashflow),
        "q_income": safe(lambda: t.quarterly_income_stmt),
        "earnings_dates": safe(lambda: t.earnings_dates),
        "recommendations": safe(lambda: t.recommendations_summary),
    }


def fetch_macro() -> dict:
    out = {}
    for name, sym in MACRO_TICKERS.items():
        try:
            h = yf.Ticker(sym).history(period="3mo")["Close"].dropna()
            if len(h) > 21:
                out[name] = {
                    "last": float(h.iloc[-1]),
                    "chg_1d_%": float((h.iloc[-1] / h.iloc[-2] - 1) * 100),
                    "chg_1m_%": float((h.iloc[-1] / h.iloc[-22] - 1) * 100),
                }
        except Exception:
            continue
    return out


# --------------------------------------------------------------------------- #
# 밸류에이션 (규칙 기반 참고치)
# --------------------------------------------------------------------------- #
def estimate_fair_value(info: dict, price: float) -> dict:
    """애널리스트 목표가 / 목표PER×EPS / PBR×BPS 를 종합한 참고용 적정가."""
    cands = {}
    if info.get("targetMeanPrice"):
        cands["애널리스트 평균 목표가"] = float(info["targetMeanPrice"])
    eps_f, eps_t = info.get("forwardEps"), info.get("trailingEps")
    pe_t = info.get("trailingPE")
    if eps_f and eps_f > 0:
        target_pe = min(max(pe_t or 15, 8), 30) if pe_t else 15
        cands[f"선행EPS×PER {target_pe:.0f}배"] = float(eps_f) * target_pe
    elif eps_t and eps_t > 0:
        cands["후행EPS×PER 15배"] = float(eps_t) * 15
    if info.get("bookValue") and info.get("returnOnEquity"):
        roe = info["returnOnEquity"]
        cands["BPS×적정PBR(ROE 기반)"] = float(info["bookValue"]) * min(max(roe * 10, 0.6), 4)
    if not cands:
        return {"methods": {}, "fair_value": None, "upside_%": None}
    fv = float(np.median(list(cands.values())))
    return {"methods": cands, "fair_value": fv, "upside_%": (fv / price - 1) * 100}


# --------------------------------------------------------------------------- #
# 종합 데이터 패키지
# --------------------------------------------------------------------------- #
@dataclass
class StockBundle:
    symbol: str
    name: str
    currency: str
    hist: pd.DataFrame
    ta: dict
    info: dict
    fair: dict
    fundamentals: dict = field(default_factory=dict)
    macro: dict = field(default_factory=dict)


def build_bundle(query: str, market: str = "auto", period: str = "2y") -> StockBundle:
    symbol = resolve_ticker(query, market)
    t = yf.Ticker(symbol)
    hist = t.history(period=period)
    if hist.empty:
        raise ValueError(f"{symbol}: 시세 데이터가 없습니다.")
    hist.index = hist.index.tz_localize(None) if hist.index.tz is not None else hist.index
    df = compute_indicators(hist)
    ta = technical_summary(df)
    f = fetch_fundamentals(t)
    info = f["info"]
    return StockBundle(
        symbol=symbol,
        name=info.get("longName") or info.get("shortName") or symbol,
        currency=info.get("currency") or ("KRW" if symbol.endswith((".KS", ".KQ", ".NXT")) else "USD"),
        hist=df,
        ta=ta,
        info=info,
        fair=estimate_fair_value(info, ta["price"]),
        fundamentals=f,
        macro=fetch_macro(),
    )


# --------------------------------------------------------------------------- #
# 프롬프트 직렬화
# --------------------------------------------------------------------------- #
def _n(x, d=2):
    return "데이터 없음" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:,.{d}f}"


def _pct(x):
    return "데이터 없음" if x is None else f"{x * 100:.1f}%"


def _strategy_block(b: "StockBundle") -> str:
    import strategy  # 지연 import (순환 방지)

    return strategy.strategy_prompt(b.symbol, b.hist)


def bundle_to_prompt(b: StockBundle, portfolio_text: str = "") -> str:
    i, ta, cur = b.info, b.ta, b.currency
    f = b.fundamentals
    inc_rows = ["Total Revenue", "Gross Profit", "Operating Income", "Net Income", "EBITDA", "Basic EPS"]
    bal_rows = ["Total Assets", "Total Liabilities Net Minority Interest", "Stockholders Equity",
                "Total Debt", "Cash And Cash Equivalents", "Current Assets", "Current Liabilities"]
    cf_rows = ["Operating Cash Flow", "Capital Expenditure", "Free Cash Flow"]

    methods = "\n".join(f"  - {k}: {_n(v)} {cur}" for k, v in b.fair["methods"].items()) or "  데이터 없음"
    ed = f.get("earnings_dates")
    earn_txt = "데이터 없음"
    if ed is not None and not ed.empty:
        earn_txt = ed.head(6).to_string()

    macro_txt = "\n".join(
        f"  - {k}: {_n(v['last'])} (1일 {v['chg_1d_%']:+.2f}%, 1개월 {v['chg_1m_%']:+.2f}%)"
        for k, v in b.macro.items()
    ) or "  데이터 없음"

    return f"""다음 종목을 분석해줘.

[종목 정보]
- 종목명: {b.name} ({b.symbol}) / 통화: {cur}
- 섹터/산업: {i.get('sector', '데이터 없음')} / {i.get('industry', '데이터 없음')}
- 사업 개요: {(i.get('longBusinessSummary') or '데이터 없음')[:900]}
- 시가총액: {_n(i.get('marketCap'), 0)} {cur}
- 현재가: {_n(ta['price'])} {cur} / 52주 고가 {_n(ta['high_52w'])} / 저가 {_n(ta['low_52w'])}

[밸류에이션 지표]
- PER(후행) {_n(i.get('trailingPE'))} / PER(선행) {_n(i.get('forwardPE'))} / PBR {_n(i.get('priceToBook'))} / PSR {_n(i.get('priceToSalesTrailing12Months'))}
- EV/EBITDA {_n(i.get('enterpriseToEbitda'))} / PEG {_n(i.get('pegRatio'))} / 배당수익률 {_n(i.get('dividendYield'))}
- EPS(후행) {_n(i.get('trailingEps'))} / EPS(선행) {_n(i.get('forwardEps'))} / BPS {_n(i.get('bookValue'))}
- 애널리스트 목표가: 평균 {_n(i.get('targetMeanPrice'))} / 최고 {_n(i.get('targetHighPrice'))} / 최저 {_n(i.get('targetLowPrice'))} (의견 {i.get('recommendationKey', '데이터 없음')}, 참여 {i.get('numberOfAnalystOpinions', '데이터 없음')}명)
- 규칙 기반 참고 적정가 산출:
{methods}
  => 중앙값 {_n(b.fair['fair_value'])} {cur} (현재가 대비 {_n(b.fair['upside_%'], 1)}%)

[수익성/안정성]
- 매출성장률 {_pct(i.get('revenueGrowth'))} / 이익성장률(분기) {_pct(i.get('earningsQuarterlyGrowth'))}
- 매출총이익률 {_pct(i.get('grossMargins'))} / 영업이익률 {_pct(i.get('operatingMargins'))} / 순이익률 {_pct(i.get('profitMargins'))}
- ROE {_pct(i.get('returnOnEquity'))} / ROA {_pct(i.get('returnOnAssets'))}
- 부채비율(D/E) {_n(i.get('debtToEquity'))} / 유동비율 {_n(i.get('currentRatio'))} / 잉여현금흐름 {_n(i.get('freeCashflow'), 0)}

[최근 실적 발표 (분기)]
{_fmt_df(f.get('q_income'), inc_rows)}
[실적 발표일 / EPS 추정 vs 실제]
{earn_txt}

[연간 재무제표]
손익계산서:
{_fmt_df(f.get('income'), inc_rows)}
재무상태표:
{_fmt_df(f.get('balance'), bal_rows)}
현금흐름표:
{_fmt_df(f.get('cashflow'), cf_rows)}

[기술적 지표]
- 이동평균: 5일 {_n(ta['sma'][5])} / 20일 {_n(ta['sma'][20])} / 60일 {_n(ta['sma'][60])} / 120일 {_n(ta['sma'][120])} / 200일 {_n(ta['sma'][200])}
- 추세 배열: {ta['trend']}
- RSI(14): {_n(ta['rsi'], 1)} / 스토캐스틱 K {_n(ta['stoch_k'], 1)} D {_n(ta['stoch_d'], 1)}
- MACD {_n(ta['macd'])} / 시그널 {_n(ta['macd_signal'])} / 히스토그램 {_n(ta['macd_hist'])} / 최근 신호: {ta['macd_cross'] or '없음'}
- 볼린저밴드(20,2): 상단 {_n(ta['bb_upper'])} / 하단 {_n(ta['bb_lower'])} / ATR(14) {_n(ta['atr'])}
- 거래량: 최근 {_n(ta['volume'], 0)} (20일 평균 대비 {_n(ta['volume_vs_20d'], 2)}배)
- 지지선(가까운 순): {', '.join(_n(x) for x in ta['supports']) or '데이터 없음'}
- 저항선(가까운 순): {', '.join(_n(x) for x in ta['resistances']) or '데이터 없음'}

[매크로 환경]
{macro_txt}

[지지 눌림목 전략 판정 (차트의 맥 x 워뇨띠 v2)]
{_strategy_block(b)}

[보유 포트폴리오]
{portfolio_text or '제공되지 않음'}
"""


# --------------------------------------------------------------------------- #
# Claude 호출
# --------------------------------------------------------------------------- #
def _client():
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("환경변수 ANTHROPIC_API_KEY 가 설정되어 있지 않습니다.")
    from anthropic import Anthropic

    return Anthropic(api_key=key)


def _ask(system: str, user: str, model: str = DEFAULT_MODEL, max_tokens: int = 4000) -> str:
    resp = _client().messages.create(
        model=model, max_tokens=max_tokens, system=system,
        messages=[{"role": "user", "content": user}],
    )
    return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")


def analyze_stock_with_ai(b: StockBundle, portfolio_text: str = "", model: str = DEFAULT_MODEL) -> str:
    return _ask(MASTER_SYSTEM_PROMPT, bundle_to_prompt(b, portfolio_text), model)


def analyze_macro_with_ai(macro: dict | None = None, model: str = DEFAULT_MODEL) -> str:
    macro = macro or fetch_macro()
    txt = "\n".join(f"- {k}: {_n(v['last'])} (1일 {v['chg_1d_%']:+.2f}%, 1개월 {v['chg_1m_%']:+.2f}%)"
                    for k, v in macro.items())
    return _ask(MACRO_SYSTEM_PROMPT, f"[매크로 데이터]\n{txt}", model, 2500)


def parse_portfolio(text: str) -> list[tuple[str, float]]:
    """'AAPL 30, 005930 40' / 줄바꿈 / 콤마 구분 -> [(티커, 비중)]"""
    rows = []
    for line in re.split(r"[\n,;]+", text):
        m = re.match(r"\s*(\S+)\s+([\d.]+)\s*%?\s*$", line)
        if m:
            rows.append((m.group(1), float(m.group(2))))
    return rows


def analyze_portfolio_with_ai(holdings: list[tuple[str, float]], model: str = DEFAULT_MODEL) -> str:
    lines = []
    closes = {}
    for q, w in holdings:
        try:
            sym = resolve_ticker(q)
            h = yf.Ticker(sym).history(period="1y")["Close"].dropna()
            closes[sym] = h
            info = yf.Ticker(sym).info
            lines.append(
                f"- {sym} ({info.get('shortName', '')}) 비중 {w}% / 섹터 {info.get('sector', '데이터 없음')} / "
                f"1년수익률 {(h.iloc[-1] / h.iloc[0] - 1) * 100:+.1f}% / "
                f"연변동성 {h.pct_change().std() * np.sqrt(252) * 100:.1f}% / "
                f"PER {_n(info.get('trailingPE'))} / 통화 {info.get('currency', '')}"
            )
        except Exception as e:
            lines.append(f"- {q} 비중 {w}% : 데이터 조회 실패 ({e})")
    corr_txt = "데이터 없음"
    if len(closes) >= 2:
        corr_txt = pd.DataFrame(closes).pct_change().corr().round(2).to_string()
    return _ask(PORTFOLIO_SYSTEM_PROMPT, "[보유 종목]\n" + "\n".join(lines) + f"\n\n[상관계수]\n{corr_txt}", model, 3000)


# --------------------------------------------------------------------------- #
# API 키 없을 때의 규칙 기반 요약 (오프라인 폴백)
# --------------------------------------------------------------------------- #
def rule_based_summary(b: StockBundle) -> str:
    ta, cur = b.ta, b.currency
    score, why = 0, []
    if "정배열" in ta["trend"]:
        score += 2; why.append("이동평균 정배열(상승추세)")
    elif "역배열" in ta["trend"]:
        score -= 2; why.append("이동평균 역배열(하락추세)")
    if ta["rsi"] is not None:
        if ta["rsi"] < 30: score += 1; why.append(f"RSI {ta['rsi']:.0f} 과매도")
        elif ta["rsi"] > 70: score -= 1; why.append(f"RSI {ta['rsi']:.0f} 과매수")
    if ta["macd_hist"] is not None:
        score += 1 if ta["macd_hist"] > 0 else -1
        why.append("MACD 히스토그램 " + ("양(+)" if ta["macd_hist"] > 0 else "음(-)"))
    up = b.fair["upside_%"]
    if up is not None:
        score += 2 if up > 15 else (-2 if up < -15 else 0)
        why.append(f"참고 적정가 대비 {up:+.1f}%")
    view = "매수" if score >= 3 else "매도" if score <= -3 else "중립(관망)"
    fv = b.fair["fair_value"]
    fv_txt = f"{fv:,.2f} {cur}" if fv else "데이터 없음"
    return (
        f"**[규칙 기반 요약 – AI 키 없음]** {b.name}({b.symbol})\n\n"
        f"- 의견: **{view}** (점수 {score})\n"
        f"- 현재가: {ta['price']:,.2f} {cur} / 참고 적정가: {fv_txt}\n"
        f"- 근거: " + " · ".join(why) + "\n"
        f"- 지지선: {', '.join(f'{x:,.2f}' for x in ta['supports']) or '없음'} / "
        f"저항선: {', '.join(f'{x:,.2f}' for x in ta['resistances']) or '없음'}\n\n"
        "_투자 권유가 아니며 참고용입니다._"
    )



if __name__ == "__main__":
    import sys

    q = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    bundle = build_bundle(q)
    try:
        print(analyze_stock_with_ai(bundle))
    except RuntimeError as e:
        print(e, "\n")
        print(rule_based_summary(bundle))
