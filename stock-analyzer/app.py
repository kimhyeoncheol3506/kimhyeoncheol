"""Streamlit UI:  streamlit run app.py"""
import os

import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import stock_analyzer as sa

st.set_page_config(page_title="AI 주식 분석기", page_icon="📈", layout="wide")
st.title("📈 AI 주식 분석기")
st.caption("KOSPI · KOSDAQ · 넥스트레이드 · 다우존스 · 나스닥 등 — 종목을 넣으면 적정주가와 근거를 제시합니다.")

has_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
with st.sidebar:
    st.header("설정")
    market = st.radio("한국 종목 시세", ["auto", "nxt"], format_func=lambda x: {"auto": "KRX (KOSPI/KOSDAQ)", "nxt": "넥스트레이드 우선"}[x])
    period = st.selectbox("차트 기간", ["6mo", "1y", "2y", "5y"], index=2)
    model = st.text_input("Claude 모델", sa.DEFAULT_MODEL)
    st.success("ANTHROPIC_API_KEY 감지됨") if has_key else st.warning("API 키 없음 → 규칙 기반 요약만 제공")
    st.markdown("**입력 예시**  \n`AAPL` `NVDA` `^DJI` `^IXIC` `005930`(삼성전자) `035720` `삼성전자`")

tab_stock, tab_port, tab_macro = st.tabs(["🔎 종목 분석", "💼 포트폴리오 분석", "🌐 매크로 분석"])


def draw_chart(b: sa.StockBundle):
    df = b.hist
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, row_heights=[0.6, 0.2, 0.2], vertical_spacing=0.03,
                        subplot_titles=(f"{b.name} ({b.symbol})", "RSI(14)", "MACD"))
    fig.add_trace(go.Candlestick(x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="가격"), 1, 1)
    for n, color in ((20, "#f59e0b"), (60, "#10b981"), (120, "#3b82f6"), (200, "#a855f7")):
        fig.add_trace(go.Scatter(x=df.index, y=df[f"SMA_{n}"], name=f"{n}일선", line=dict(width=1.3, color=color)), 1, 1)
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_upper"], name="BB상단", line=dict(width=0.8, dash="dot", color="#9ca3af")), 1, 1)
    fig.add_trace(go.Scatter(x=df.index, y=df["BB_lower"], name="BB하단", line=dict(width=0.8, dash="dot", color="#9ca3af")), 1, 1)
    for p in b.ta["supports"][:2]:
        fig.add_hline(y=p, line=dict(color="#16a34a", dash="dash", width=1), row=1, col=1)
    for p in b.ta["resistances"][:2]:
        fig.add_hline(y=p, line=dict(color="#dc2626", dash="dash", width=1), row=1, col=1)
    if b.fair["fair_value"]:
        fig.add_hline(y=b.fair["fair_value"], line=dict(color="#2563eb", width=2), row=1, col=1,
                      annotation_text=f"참고 적정가 {b.fair['fair_value']:,.2f}")
    fig.add_trace(go.Scatter(x=df.index, y=df["RSI"], name="RSI", line=dict(color="#8b5cf6")), 2, 1)
    fig.add_hline(y=70, line=dict(dash="dot", color="#dc2626"), row=2, col=1)
    fig.add_hline(y=30, line=dict(dash="dot", color="#16a34a"), row=2, col=1)
    fig.add_trace(go.Bar(x=df.index, y=df["MACD_hist"], name="히스토그램", marker_color="#9ca3af"), 3, 1)
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD", line=dict(color="#2563eb")), 3, 1)
    fig.add_trace(go.Scatter(x=df.index, y=df["MACD_signal"], name="시그널", line=dict(color="#f97316")), 3, 1)
    fig.update_layout(height=820, xaxis_rangeslider_visible=False, legend=dict(orientation="h", y=1.04), margin=dict(t=60, b=10))
    st.plotly_chart(fig, use_container_width=True)


with tab_stock:
    c1, c2 = st.columns([4, 1])
    query = c1.text_input("종목 (티커 / 종목코드 / 종목명)", value="AAPL", key="q")
    run = c2.button("분석하기", type="primary", use_container_width=True)
    if run:
        try:
            with st.spinner("데이터 수집 및 지표 계산 중..."):
                bundle = sa.build_bundle(query, market, period)
            ta, cur = bundle.ta, bundle.currency
            m = st.columns(5)
            m[0].metric("현재가", f"{ta['price']:,.2f} {cur}")
            fv = bundle.fair["fair_value"]
            m[1].metric("참고 적정가", f"{fv:,.2f}" if fv else "N/A", f"{bundle.fair['upside_%']:+.1f}%" if fv else None)
            m[2].metric("RSI(14)", f"{ta['rsi']:.1f}" if ta["rsi"] else "N/A")
            m[3].metric("추세", ta["trend"])
            m[4].metric("PER", f"{bundle.info.get('trailingPE'):.1f}" if bundle.info.get("trailingPE") else "N/A")
            draw_chart(bundle)

            st.subheader("🤖 AI 종합 분석")
            if has_key:
                with st.spinner("Claude 분석 중..."):
                    st.markdown(sa.analyze_stock_with_ai(bundle, model=model))
            else:
                st.markdown(sa.rule_based_summary(bundle))
            with st.expander("AI에 전달된 원본 데이터 보기"):
                st.code(sa.bundle_to_prompt(bundle))
        except Exception as e:
            st.error(f"오류: {e}")

with tab_port:
    st.write("한 줄에 `티커 비중(%)` 형식으로 입력하세요.")
    txt = st.text_area("보유 종목", "AAPL 30\n005930 40\nNVDA 30", height=140)
    if st.button("포트폴리오 분석"):
        if not has_key:
            st.warning("포트폴리오 분석은 ANTHROPIC_API_KEY 가 필요합니다.")
        else:
            try:
                with st.spinner("분석 중..."):
                    st.markdown(sa.analyze_portfolio_with_ai(sa.parse_portfolio(txt), model))
            except Exception as e:
                st.error(f"오류: {e}")

with tab_macro:
    if st.button("매크로 분석"):
        with st.spinner("지표 수집 중..."):
            macro = sa.fetch_macro()
        st.dataframe({k: v for k, v in macro.items()}, use_container_width=True)
        if has_key:
            with st.spinner("Claude 분석 중..."):
                st.markdown(sa.analyze_macro_with_ai(macro, model))
        else:
            st.warning("AI 해석은 ANTHROPIC_API_KEY 가 필요합니다.")
