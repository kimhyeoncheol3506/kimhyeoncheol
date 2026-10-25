"""Streamlit UI:  streamlit run app.py"""
import os

import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import pandas as pd

import stock_analyzer as sa
import strategy as stg

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

tab_stock, tab_strat, tab_port, tab_macro = st.tabs(["🔎 종목 분석", "🎯 지지 눌림목 전략", "💼 포트폴리오 분석", "🌐 매크로 분석"])


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


DEFAULT_UNIVERSE = "005930, 000660, 035420, 005380, 000270, 068270, 035720, 105560, 051910, 006400, 247540, 196170, 086520, 028300"


def _universe(txt: str) -> list[str]:
    out = []
    for q in [x.strip() for x in txt.replace("\n", ",").split(",") if x.strip()]:
        try:
            out.append(sa.resolve_ticker(q))
        except Exception as e:  # noqa: BLE001
            st.warning(f"{q}: {e}")
    return out


with tab_strat:
    st.markdown("**지지 눌림목 전략 (차트의 맥 x 워뇨띠) v2** — 캔들·거래량 중심, 돌파 추격 대신 지지 구간 눌림목 진입")
    with st.expander("전략 규칙 요약 (7원칙 · 매매 시각 · 손절 · 자금관리)"):
        st.markdown(stg.RULES_MD)
        st.caption("전체 표는 STRATEGY.md 참고")
    c1, c2, c3, c4 = st.columns(4)
    preset = c1.selectbox("전략 버전", list(stg.PRESETS), index=0)
    account_eok = c2.number_input("계좌 (억 원)", 1.0, 1000.0, 30.0, step=1.0)
    stop_mode = c3.selectbox("손절 방식", ["pullback_low", "sma20_-3%"],
                             format_func=lambda x: {"pullback_low": "눌림 저점 이탈 + -7% (v2)", "sma20_-3%": "종가 20일선 -3% (수정 후보)"}[x])
    buffer = c4.slider("눌림 저점 여유폭(%)", 0.0, 3.0, 0.0, 0.5) / 100
    params = stg.replace(stg.PRESETS[preset], stop_mode=stop_mode, support_buffer=buffer)
    account = account_eok * stg.EOK
    with st.expander("세부 파라미터 수정"):
        d1, d2, d3 = st.columns(3)
        params = stg.replace(
            params,
            sideways_rest_count=int(d1.number_input("횡보 쉬는 기준(4개 중)", 1, 4, params.sideways_rest_count)),
            pb_min=-d2.number_input("조정폭 최대(%)", 1.0, 40.0, -params.pb_min * 100) / 100,
            pb_max=-d2.number_input("조정폭 최소(%)", 0.0, 30.0, -params.pb_max * 100) / 100,
            rr_min=d3.number_input("최소 손익비", 0.5, 5.0, params.rr_min, 0.1),
            max_loss=d3.number_input("최대 손실(%)", 1.0, 20.0, params.max_loss * 100) / 100,
            market_filter=d1.checkbox("시장 필터(지수<60일선·60일선 하락 시 쉼)", params.market_filter),
        )
    uni_txt = st.text_area("종목 유니버스 (콤마/줄바꿈) — 코스피 시총 1~500·코스닥 1~300 목록은 직접 붙여넣으세요", DEFAULT_UNIVERSE, height=80)
    st.caption("거래대금 필터는 원화 종목에만 적용됩니다. 데이터는 일봉(야후)이라 15:15 실시간 체결·종가 단일가 물량은 반영되지 않습니다.")

    t_scan, t_bt = st.tabs(["📡 오늘 신호 스캔", "🧪 백테스트"])
    with t_scan:
        if st.button("신호 스캔", type="primary"):
            rows, details = [], {}
            syms = _universe(uni_txt)
            bar = st.progress(0.0)
            for k, sym in enumerate(syms):
                try:
                    ev = stg.scan_symbol(sym, params, account)
                    sz = ev.get("size") or {}
                    fails = [n for n, ok, _ in ev["checks"] if not ok]
                    rows.append({
                        "종목": sym, "기준일": f"{ev['date']:%Y-%m-%d}", "신호": "✅ 매수" if ev["pass"] else "—",
                        "진입가": ev["entry"], "손절가": ev["stop"], "목표가": ev["target"], "손익비": ev["rr"],
                        "매수금액": sz.get("amount") if sz.get("ok") else None,
                        "미충족": ", ".join(fails[:3]) + (" …" if len(fails) > 3 else ""),
                    })
                    details[sym] = ev
                except Exception as e:  # noqa: BLE001
                    rows.append({"종목": sym, "신호": f"오류: {e}"})
                bar.progress((k + 1) / max(len(syms), 1))
            st.session_state["scan"] = (pd.DataFrame(rows), details)
        if "scan" in st.session_state:
            df_scan, details = st.session_state["scan"]
            st.dataframe(df_scan, use_container_width=True, hide_index=True)
            pick = st.selectbox("조건 상세", list(details))
            if pick:
                ev = details[pick]
                st.write("**횡보 필터** (해당 개수가 기준 이상이면 쉼)")
                st.table(pd.DataFrame([(n, "해당" if ok else "비해당", d) for n, ok, d in ev["sideways"]], columns=["항목", "판정", "값"]))
                st.write("**진입 체크리스트**")
                st.table(pd.DataFrame([("✅" if ok else "❌", n, d) for n, ok, d in ev["checks"]], columns=["", "조건", "값"]))
                sz = ev.get("size")
                if sz:
                    st.info((f"매수금액 {sz['amount']:,.0f} (약 {sz['shares']:,}주) · 손절폭 {sz['stop_pct'] * 100:.1f}% · "
                             f"1회 손실한도 {sz['risk_amt']:,.0f} " + " / ".join(sz["notes"])) if sz["ok"] else sz["reason"])

    with t_bt:
        b1, b2 = st.columns(2)
        start = b1.date_input("시작일", pd.Timestamp("2026-01-02"))
        end = b2.date_input("종료일", pd.Timestamp.today())
        if st.button("백테스트 실행"):
            syms = _universe(uni_txt)
            bar = st.progress(0.0)
            res = stg.backtest(syms, params, account, start, end, "5y", progress=bar.progress)
            s, trades = res["summary"], res["trades"]
            if trades.empty:
                st.warning("조건에 맞는 매매가 없습니다.")
            else:
                m = st.columns(5)
                m[0].metric("매매", f"{s['trades']}회", f"익절 {s['n_win']} / 손절 {s['n_loss']} / 보유 {s['n_hold']}")
                m[1].metric("승률", f"{s['win_rate'] * 100:.0f}%")
                m[2].metric("평균 익절 / 손절", f"{s['avg_win'] * 100:+.1f}% / {s['avg_loss'] * 100:+.1f}%")
                m[3].metric("손익비(평균)", f"{s['payoff']:.2f}" if s["payoff"] else "N/A")
                m[4].metric("계좌 손익", f"{s['pnl']:,.0f}", f"{s['pnl_pct'] * 100:+.2f}%")
                eq = trades.sort_values("exit_date").assign(cum=lambda d: d["pnl"].cumsum())
                st.line_chart(eq.set_index("exit_date")["cum"])
                st.write("**청산 사유별**")
                st.dataframe(trades.groupby("reason").agg(건수=("ret", "size"), 평균수익률=("ret", "mean"), 손익=("pnl", "sum")), use_container_width=True)
                st.dataframe(trades[["symbol", "entry_date", "exit_date", "days", "entry", "ret", "reason", "status", "amount", "pnl"]],
                             use_container_width=True, hide_index=True)
            if res["skipped"]:
                with st.expander(f"건너뛴 신호 {len(res['skipped'])}건"):
                    st.dataframe(pd.DataFrame(res["skipped"], columns=["종목", "일자", "사유"]), hide_index=True)
            for e in s["errors"]:
                st.warning(e)

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
