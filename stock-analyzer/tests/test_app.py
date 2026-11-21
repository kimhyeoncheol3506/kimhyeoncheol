"""Streamlit 앱 스모크 테스트 (오프라인 합성 데이터). 화면 출력 형식이 유지되는지 확인."""
import os

import pytest
from streamlit.testing.v1 import AppTest

from tests.conftest import ROOT, make_ohlcv

KS = ["005930", "000660", "035420", "005380", "000270", "068270", "035720", "105560", "051910", "006400"]
KQ = ["247540", "196170", "086520", "028300"]


@pytest.fixture
def app(fake, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    for k, code in enumerate(KS):
        fake[f"{code}.KS"] = make_ohlcv(1300, drift=0.0006, vol=0.02, seed=k)
    for k, code in enumerate(KQ):
        fake[f"{code}.KQ"] = make_ohlcv(1300, drift=0.0006, vol=0.02, seed=20 + k)
    for k, (sym, price) in enumerate((("AAPL", 200.0), ("^GSPC", 5000.0), ("^VIX", 18.0), ("^KS11", 2500.0),
                                       ("^KQ11", 800.0))):
        fake[sym] = make_ohlcv(1300, seed=40 + k, price=price)
    at = AppTest.from_file(os.path.join(ROOT, "app.py"), default_timeout=240)
    at.run()
    assert not at.exception
    return at


def _click(at, label):
    [b for b in at.button if b.label == label][0].click()
    at.run()
    assert not at.exception, [e.value for e in at.exception]


def test_tabs_render(app):
    labels = [t.label for t in app.tabs]
    for name in ("🔎 종목 분석", "🎯 지지 눌림목 전략", "🧮 퀀트 17전략", "💼 포트폴리오 분석", "🌐 매크로 분석"):
        assert name in labels


def test_stock_analysis_keeps_technical_section(app):
    _click(app, "분석하기")
    assert [m.label for m in app.metric][:5] == ["현재가", "참고 적정가", "RSI(14)", "추세", "PER"]
    md = " ".join(m.value for m in app.markdown)
    assert "규칙 기반 요약" in md          # 키 없으면 규칙 기반 요약
    code = app.code[0].value
    assert "[기술적 지표]" in code and "- 17개 중 매수 " in code


def test_pullback_scan_simple_table(app):
    _click(app, "신호 스캔")
    df, _ = app.session_state["scan"]
    assert list(df.columns) == ["종목", "기준일", "신호", "진입가", "손절가", "목표가", "매수금액"]
    assert len(df) == len(KS) + len(KQ)
    assert set(df["신호"]) <= {"✅ 매수", "—"}
    no_sig = df[df["신호"] == "—"]
    assert no_sig[["진입가", "손절가", "목표가", "매수금액"]].isna().all().all()  # 신호 없으면 빈칸
    assert not [s for s in app.selectbox if s.label == "조건 상세"]            # 조건별 근거 화면 없음


def test_quant_counts_only(app):
    _click(app, "17전략 분석")
    counts = {m.label: m.value for m in app.metric if m.label in ("🟢 매수", "⚪ 중립", "🔴 매도", "참고·해당없음")}
    assert list(counts) == ["🟢 매수", "⚪ 중립", "🔴 매도", "참고·해당없음"]
    assert sum(int(v.rstrip("개")) for v in counts.values()) == 17
    assert any(s.value.startswith("AAPL — ") for s in app.subheader)


def test_pullback_backtest_runs(app):
    _click(app, "백테스트 실행")
    labels = [m.label for m in app.metric]
    warnings = [w.value for w in app.warning]
    # 매매가 있으면 요약 지표 5개, 없으면 안내 문구
    assert labels[:5] == ["매매", "승률", "평균 익절 / 손절", "손익비(평균)", "계좌 손익"] or \
        "조건에 맞는 매매가 없습니다." in warnings
