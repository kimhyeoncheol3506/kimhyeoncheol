"""종목 분석: 기술적 지표 · 밸류에이션 · 티커 해석 · 프롬프트 · Claude 호출 오류 처리."""
from types import SimpleNamespace

import anthropic
import httpx2
import pytest

import stock_analyzer as sa
from tests.conftest import make_ohlcv


# --------------------------------------------------------------------------- #
# 기술적 분석 (출력 그대로 유지돼야 하는 부분)
# --------------------------------------------------------------------------- #
def test_compute_indicators_values():
    h = make_ohlcv(300, seed=1)
    df = sa.compute_indicators(h)
    assert df["SMA_20"].iloc[-1] == pytest.approx(h["Close"].tail(20).mean())
    assert df["SMA_200"].iloc[-1] == pytest.approx(h["Close"].tail(200).mean())
    assert df["RSI"].dropna().between(0, 100).all()
    assert (df["BB_upper"].dropna() >= df["BB_lower"].dropna()).all()
    assert df["MACD_hist"].iloc[-1] == pytest.approx(df["MACD"].iloc[-1] - df["MACD_signal"].iloc[-1])


@pytest.mark.parametrize("up,trend", [(True, "정배열(상승추세)"), (False, "역배열(하락추세)")])
def test_technical_summary_trend(up, trend):
    h = make_ohlcv(400, drift=0.003 if up else -0.003, vol=0.008, seed=2)
    ta = sa.technical_summary(sa.compute_indicators(h))
    assert ta["trend"] == trend
    assert all(s < ta["price"] for s in ta["supports"]) and all(r > ta["price"] for r in ta["resistances"])
    assert ta["supports"] == sorted(ta["supports"], reverse=True)


def test_estimate_fair_value_tolerates_strings():
    info = {"targetMeanPrice": 120.0, "forwardEps": 10.0, "trailingPE": "Infinity", "bookValue": "n/a"}
    fv = sa.estimate_fair_value(info, 100.0)
    assert fv["methods"] == {"애널리스트 평균 목표가": 120.0, "선행EPS×PER 15배": 150.0}
    assert fv["fair_value"] == pytest.approx(135.0) and fv["upside_%"] == pytest.approx(35.0)
    assert sa.estimate_fair_value({}, 100.0)["fair_value"] is None


def test_parse_portfolio():
    assert sa.parse_portfolio("AAPL 30\n005930 40%, NVDA 30 ; bad line") == [("AAPL", 30.0), ("005930", 40.0), ("NVDA", 30.0)]


# --------------------------------------------------------------------------- #
# 티커 해석
# --------------------------------------------------------------------------- #
def test_resolve_ticker_variants(fake):
    fake["005930.KS"] = make_ohlcv(10)
    fake["247540.KQ"] = make_ohlcv(10)
    fake["AAPL"] = make_ohlcv(10)
    assert sa.resolve_ticker("삼성전자") == "005930.KS"
    assert sa.resolve_ticker(" 005930 ") == "005930.KS"
    assert sa.resolve_ticker("247540") == "247540.KQ"           # 코스피에 없으면 코스닥
    assert sa.resolve_ticker("005930.NXT") == "005930.KS"       # 넥스트레이드 시세 없으면 KRX
    assert sa.resolve_ticker("aapl") == "AAPL"
    with pytest.raises(ValueError, match="종목을 입력"):
        sa.resolve_ticker("  ")
    with pytest.raises(ValueError, match="찾지 못했습니다"):
        sa.resolve_ticker("ZZZZ")
    with pytest.raises(ValueError, match="시세를 찾지 못했습니다"):
        sa.resolve_ticker("999999")


def test_resolve_ticker_is_cached(fake, calls):
    fake["AAPL"] = make_ohlcv(10)
    sa.resolve_ticker("AAPL")
    n = calls["history"]
    sa.resolve_ticker("AAPL")
    assert calls["history"] == n


# --------------------------------------------------------------------------- #
# 번들 · 프롬프트
# --------------------------------------------------------------------------- #
def _bundle(fake, fake_info):
    fake["005930.KS"] = make_ohlcv(600, seed=3)
    fake_info["005930.KS"] = {"longName": "Samsung", "currency": "KRW", "trailingPE": "Infinity",
                              "targetMeanPrice": 70000.0, "dividendYield": 1.2}
    return sa.build_bundle("005930")


def test_build_bundle_offline(fake, fake_info, monkeypatch):
    monkeypatch.setattr(sa, "fetch_macro", lambda: {})
    b = _bundle(fake, fake_info)
    assert b.symbol == "005930.KS" and b.currency == "KRW" and b.name == "Samsung"
    assert "SMA_120" in b.hist and b.fair["fair_value"] == pytest.approx(70000.0)


def test_bundle_to_prompt_built_once(fake, fake_info, monkeypatch):
    monkeypatch.setattr(sa, "fetch_macro", lambda: {"KOSPI": {"last": 2500.0, "chg_1d_%": 1.0, "chg_1m_%": -2.0}})
    n = {"q": 0, "s": 0}

    def qb(b):
        n["q"] += 1
        return "- 17개 중 매수 1 · 중립 8 · 매도 1 (참고·해당없음 7) → 중립"

    def sb(b):
        n["s"] += 1
        return "- 2026-11-20 기준: 신호 없음"

    monkeypatch.setattr(sa, "_quant_block", qb)
    monkeypatch.setattr(sa, "_strategy_block", sb)
    b = _bundle(fake, fake_info)
    p1 = sa.bundle_to_prompt(b)
    p2 = sa.bundle_to_prompt(b)          # 앱의 '원본 데이터 보기'에서 다시 호출
    assert p1 is p2 and n == {"q": 1, "s": 1}  # 이전: 매번 17전략·ML을 다시 계산
    for sec in ("[종목 정보]", "[밸류에이션 지표]", "[기술적 지표]", "[매크로 환경]",
                "[지지 눌림목 전략 판정 (차트의 맥 x 워뇨띠 v2)]", "[퀀트 17전략 판정]", "[보유 포트폴리오]"):
        assert sec in p1
    assert "PER(후행) 데이터 없음" in p1   # 'Infinity' 문자열도 안전하게
    assert "- 17개 중 매수 1 · 중립 8 · 매도 1 (참고·해당없음 7) → 중립" in p1
    sa.bundle_to_prompt(b, "AAPL 50")
    assert n["q"] == 2  # 포트폴리오 입력이 다르면 새로 생성


def test_rule_based_summary(fake, fake_info, monkeypatch):
    monkeypatch.setattr(sa, "fetch_macro", lambda: {})
    out = sa.rule_based_summary(_bundle(fake, fake_info))
    assert out.startswith("**[규칙 기반 요약") and "- 의견: **" in out and "투자 권유가 아니며" in out


def test_fetch_macro_skips_failures(fake):
    fake["^KS11"] = make_ohlcv(80, price=2500)
    m = sa.fetch_macro()
    assert list(m) == ["KOSPI"] and set(m["KOSPI"]) == {"last", "chg_1d_%", "chg_1m_%"}


# --------------------------------------------------------------------------- #
# Claude 호출 (가짜 클라이언트)
# --------------------------------------------------------------------------- #
def _resp(text="분석 결과", stop="end_turn"):
    blocks = [SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text=text)]
    return SimpleNamespace(content=blocks, stop_reason=stop)


def _err(cls, status):
    req = httpx2.Request("POST", "https://api.anthropic.com/v1/messages")
    return cls("err", response=httpx2.Response(status, request=req), body=None)


class FakeClient:
    def __init__(self, beta=None, plain=None):
        self.calls = []
        self.beta = SimpleNamespace(messages=SimpleNamespace(create=self._mk("beta", beta)))
        self.messages = SimpleNamespace(create=self._mk("plain", plain))

    def _mk(self, kind, outcome):
        def create(**kw):
            self.calls.append((kind, kw))
            if isinstance(outcome, Exception):
                raise outcome
            return outcome
        return create


@pytest.fixture
def client(monkeypatch):
    holder = {}

    def use(**kw):
        holder["c"] = FakeClient(**kw)
        monkeypatch.setattr(sa, "_client", lambda: holder["c"])
        return holder["c"]
    return use


def test_ask_success_uses_fallbacks_and_text_only(client):
    c = client(beta=_resp("결과"))
    assert sa._ask("sys", "user") == "결과"
    kind, kw = c.calls[0]
    assert kind == "beta" and kw["fallbacks"] == "default" and kw["betas"] == [sa.FALLBACK_BETA]
    assert kw["max_tokens"] == sa.AI_MAX_TOKENS and kw["model"] == sa.DEFAULT_MODEL


def test_ask_retries_without_fallbacks_on_bad_request(client):
    c = client(beta=_err(anthropic.BadRequestError, 400), plain=_resp("일반"))
    assert sa._ask("s", "u") == "일반"
    assert [k for k, _ in c.calls] == ["beta", "plain"] and "fallbacks" not in c.calls[1][1]


@pytest.mark.parametrize("exc,status,msg", [
    (anthropic.AuthenticationError, 401, "API 키"),
    (anthropic.NotFoundError, 404, "찾을 수 없습니다"),
    (anthropic.RateLimitError, 429, "요청 한도"),
    (anthropic.InternalServerError, 500, r"Claude API 오류\(500\)"),
])
def test_ask_maps_errors(client, exc, status, msg):
    client(beta=_err(exc, status))
    with pytest.raises(sa.AIError, match=msg):
        sa._ask("s", "u")


def test_ask_connection_error(client):
    client(beta=anthropic.APIConnectionError(request=httpx2.Request("POST", "https://x")))
    with pytest.raises(sa.AIError, match="연결하지 못했습니다"):
        sa._ask("s", "u")


def test_ask_refusal_empty_and_truncated(client):
    client(beta=_resp("", "refusal"))
    with pytest.raises(sa.AIError, match="거절"):
        sa._ask("s", "u")
    client(beta=_resp("   "))
    with pytest.raises(sa.AIError, match="비어"):
        sa._ask("s", "u")
    client(beta=_resp("앞부분", "max_tokens"))
    assert "잘렸습니다" in sa._ask("s", "u")


def test_missing_key(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(sa.AIError, match="ANTHROPIC_API_KEY"):
        sa._client()


def test_portfolio_requires_holdings():
    with pytest.raises(ValueError):
        sa.analyze_portfolio_with_ai([])
