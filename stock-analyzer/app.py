"""Streamlit UI:  streamlit run app.py"""
import os

import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import pandas as pd

import stock_analyzer as sa
import quant as qt
import robustness as rb
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

tab_stock, tab_strat, tab_quant, tab_port, tab_macro = st.tabs(["🔎 종목 분석", "🎯 지지 눌림목 전략", "🧮 퀀트 17전략", "💼 포트폴리오 분석", "🌐 매크로 분석"])


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
                tg = rb.validate_trades(trades["ret"], trials=int(st.session_state.get("trials", 1)))
                with st.expander(f"🛡 과최적화 검증: {tg['verdict']}", expanded=True):
                    st.number_input("이 전략을 만들기까지 시도한 버전/설정 수 (많을수록 우연 가능성을 크게 반영)", 1, 1000, 1, key="trials")
                    st.dataframe(pd.DataFrame([({"Pass": "✅", "Warn": "🟡", "Fail": "❌"}[s_], n, d) for n, s_, d in tg["checks"]],
                                              columns=["", "검사", "결과"]), use_container_width=True, hide_index=True)
                    if tg["mc"]:
                        mc = tg["mc"]
                        st.caption(f"몬테카를로: 손실로 끝날 확률 {mc['loss_prob'] * 100:.0f}%, 수익률 하위5%/중앙/상위5% "
                                   f"{mc['ret_p5']:.0%}/{mc['ret_p50']:.0%}/{mc['ret_p95']:.0%}, 최악 MDD {mc['mdd_p95_worst']:.0%}")
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


@st.cache_data(ttl=3600, show_spinner=False)
def _hist(sym: str, period: str = "5y"):
    return stg.load_history(sym, period)


def _load_universe(txt: str, period: str = "5y") -> dict:
    out = {}
    for sym in _universe(txt):
        try:
            out[sym] = _hist(sym, period)
        except Exception as e:  # noqa: BLE001
            st.warning(f"{sym}: {e}")
    return out


with tab_quant:
    st.markdown("**퀀트 트레이딩 17전략** — 모멘텀 · 평균회귀 · 통계적 차익거래 · 페어 · 추세 · 시장조성 · 이벤트 · 팩터 · 캐리 · 변동성차익 · 옵션 · 횡단면 · 단기반전 · 돌파 · 국면전환 · ML · 집행")
    st.caption("일봉 기반 계산. 🟢/🔴/⚪는 방향성 전략의 신호, '참고'는 비용·리스크 정보(시장조성·캐리·옵션·집행)입니다. 백테스트는 롱/현금, 왕복 0.3% 비용 반영.")
    qa, qb, qc, qd, qv = st.tabs(["📋 종목 17전략 판정", "🌐 유니버스(횡단면·통계차익·페어)", "🛠 도구(캐리·집행)", "ℹ️ 17전략 설명", "🛡 과최적화 검증"])

    with qa:
        qc1, qc2, qc3 = st.columns([3, 2, 1])
        qsym = qc1.text_input("종목", "AAPL", key="qsym")
        qpeers = qc2.text_area("비교 유니버스(선택: 페어·횡단면용)", "", height=70, key="qpeers",
                               help="비워두면 페어/횡단면 항목은 '유니버스 필요'로 표시됩니다. 5종목 이상 권장.")
        qml = qc3.checkbox("ML 포함", True)
        qorder = st.number_input("집행 계산용 주문금액(원 또는 달러)", 0.0, 1e12, 0.0, help="0이면 기본값(원화 3억 / 달러 30만)")
        if st.button("17전략 분석", type="primary"):
            try:
                with st.spinner("전략 계산 중 (ML 학습 포함, 수십 초)..."):
                    sym = sa.resolve_ticker(qsym)
                    peers = _load_universe(qpeers) if qpeers.strip() else None
                    st.session_state["quant"] = (sym, qt.analyze(sym, hist=_hist(sym), peers=peers,
                                                                 order_value=qorder or None, with_ml=qml))
            except Exception as e:  # noqa: BLE001
                st.error(f"오류: {e}")
        if "quant" in st.session_state:
            sym, r = st.session_state["quant"]
            m = st.columns(3)
            m[0].metric("방향성 종합", r["label"], f"평균 신호 {r['score']:+.2f}")
            m[1].metric("판정 전략 수", f"{r['n_dir']}개")
            m[2].metric("종목", sym)
            st.dataframe(pd.DataFrame([{"#": x.no, "전략": x.name, "구분": x.kind, "신호": x.label, "근거": x.detail} for x in r["signals"]]),
                         use_container_width=True, hide_index=True, height=640)
            st.subheader("백테스트 (롱/현금, 비용 반영)")
            st.dataframe(r["perf"].style.format({"CAGR": "{:.1%}", "연변동성": "{:.1%}", "샤프": "{:.2f}", "MDD": "{:.1%}", "누적": "{:.1%}", "시장노출": "{:.0%}"}),
                         use_container_width=True)
            st.line_chart(r["equity"])
            st.caption("과거 성과는 미래를 보장하지 않으며, 한 종목 한 구간의 결과라 과적합 가능성이 큽니다. ML은 학습에 쓰지 않은 구간(OOS) 검증을 통과해야 신호로 반영됩니다.")

    with qb:
        utxt = st.text_area("유니버스", DEFAULT_UNIVERSE, height=80, key="quni")
        fund = st.checkbox("가치·퀄리티 팩터 포함(재무 조회, 느림)", False)
        if st.button("유니버스 분석"):
            with st.spinner("데이터 수집 중..."):
                H = _load_universe(utxt)
            if len(H) < 4:
                st.warning("4종목 이상 필요합니다.")
            else:
                st.subheader("12·8. 횡단면 알파 / 팩터 점수 (상위 20% 롱, 하위 20% 숏·회피)")
                st.dataframe(qt.cross_section(H, fund).style.format(precision=3), use_container_width=True)
                st.subheader("3. 통계적 차익거래 (바스켓 대비 잔차 z, 롱·숏을 짝지어 시장중립)")
                st.dataframe(qt.stat_arb_universe(H).style.format(precision=2), use_container_width=True)
                st.subheader("4. 페어 트레이딩 후보 (상관≥0.7, 헤지비율>0, 반감기 2~60일)")
                pairs = qt.find_pairs(H, 10)
                st.dataframe(pairs.style.format(precision=2), use_container_width=True)
                if len(pairs):
                    a, b = pairs.iloc[0]["A"], pairs.iloc[0]["B"]
                    pb = qt.pair_backtest(H[a]["Close"], H[b]["Close"])
                    if pb:
                        st.write(f"**{a} / {b} 스프레드 백테스트** (z±2 진입, 0 청산): 거래 {pb['trades']}회, "
                                 f"CAGR {pb['perf']['CAGR'] * 100:.1f}%, 샤프 {pb['perf']['샤프']:.2f}, MDD {pb['perf']['MDD'] * 100:.1f}%")
                        st.line_chart(pb["equity"])

    with qc:
        st.subheader("9. 캐리 트레이드 계산기")
        x1, x2, x3 = st.columns(3)
        fxs = x1.text_input("환율 심볼(야후)", "JPY=X", help="JPY=X 엔/달러, KRW=X 원/달러, AUDJPY=X 호주달러/엔")
        ir = x2.number_input("투자통화 금리(%)", -5.0, 50.0, 4.0)
        fr = x3.number_input("조달통화 금리(%)", -5.0, 50.0, 0.5)
        if st.button("캐리 평가"):
            try:
                st.json({k: (round(v, 3) if isinstance(v, float) else v) for k, v in qt.carry_calc(fxs, ir, fr).items()})
            except Exception as e:  # noqa: BLE001
                st.error(f"오류: {e}")
        st.subheader("17. 집행 알고리즘 (주문 분할 계획)")
        e1, e2 = st.columns(2)
        esym = e1.text_input("종목", "005930", key="esym")
        eval_ = e2.number_input("주문금액", 0.0, 1e13, 300_000_000.0, key="eval")
        part = st.slider("거래량 참여율 상한(%)", 1, 20, 5) / 100
        if st.button("분할 계획 산출"):
            try:
                es = sa.resolve_ticker(esym)
                eh = _hist(es, "1y")
                p = qt.execution_plan(eval_, eh["Close"].iloc[-1], eh["Volume"].tail(20).mean(), eh["Close"].pct_change().tail(60).std(), part)
                st.json({k: (round(v, 4) if isinstance(v, float) else v) for k, v in p.items()})
            except Exception as e:  # noqa: BLE001
                st.error(f"오류: {e}")
        st.info("6. 시장조성 · 10. 변동성차익 · 11. 옵션은 종목 판정 탭에서 추정 스프레드/IV/프리미엄을 확인합니다. 실제 호가 제출·옵션 주문은 증권사 API 연동이 필요해 이 툴은 주문을 내지 않습니다.")

    with qd:
        st.markdown("""
| # | 전략 | 이 툴의 구현 |
|---|---|---|
| 1 | 모멘텀 | 12-1개월·6개월 수익률 부호, 백테스트 |
| 2 | 평균회귀 | 20일 z-score ±2, RSI, 백테스트(z<-1.5 진입, 0 청산) |
| 3 | 통계적 차익거래 | 시장/바스켓 β 제거 잔차 z, 유니버스 롱·숏 짝 구성 |
| 4 | 페어 트레이딩 | 상관·헤지비율·공적분 p·반감기·스프레드 z, 백테스트 |
| 5 | 추세 추종 | 50/200일선 + 종가, 백테스트 |
| 6 | 시장조성 | Corwin-Schultz 스프레드 추정 vs 호가단위 (참고, 주문 없음) |
| 7 | 이벤트 드리븐 | 실적발표일 D-day, 과거 반응 평균, 발표 후 드리프트 |
| 8 | 팩터 투자 | 가치·퀄리티·저변동·모멘텀 6개 테스트 / 유니버스 z-점수 |
| 9 | 캐리 트레이드 | 배당-단기금리, 통화쌍 캐리/환변동 계산기 |
| 10 | 변동성 차익거래 | 옵션 ATM IV vs EWMA 예측변동성 (미국 종목) |
| 11 | 옵션 전략 | 커버드콜 수취율·보호풋 비용 (미국 종목) |
| 12 | 횡단면 알파 | 모멘텀·반전·저변동·추세(+가치·퀄리티) 종합점수 순위 |
| 13 | 단기 반전 | 3일 수익률 z ≤ -2 & 거래량 1.5배, 백테스트 |
| 14 | 돌파 매매 | 55일 고점 돌파 + 거래량 1.5배, 20일 저점 이탈 청산, 백테스트 |
| 15 | 국면 전환 | 지수 200일선·변동성·VIX → 4국면, 변동성 타깃 노출 |
| 16 | 머신러닝 알파 | HistGradientBoosting, 5일 후 방향, 70/30 시계열 분할+엠바고, OOS 통과 시만 반영 |
| 17 | 집행 알고리즘 | 평균 거래량 대비 비중 → TWAP 분할·충격비용(제곱근 법칙) |
""")


    with qv:
        st.markdown("**백테스트가 좋다 ≠ 진짜 엣지.** 워크포워드·Sharpe 디플레이션(DSR)·PBO(CSCV)·CPCV·고원·몬테카를로·국면별 성과로 "
                    "'우연이거나 과최적화'인지 검증합니다. 종목이 여러 개면 설정별 수익률을 합쳐서 검증해 거래 표본을 늘립니다.")
        vc1, vc2 = st.columns([2, 3])
        vno = vc1.selectbox("검증할 전략", list(rb.STRATS), format_func=lambda n: f"{n}. {qt.STRATEGY_NAMES[n]}")
        vtxt = vc2.text_area("검증 유니버스 (5년 일봉 사용, 종목이 많을수록 신뢰↑)", DEFAULT_UNIVERSE, height=80, key="vuni")
        if st.button("검증 실행", type="primary", key="vrun"):
            try:
                with st.spinner("데이터 수집 및 검증 중..."):
                    H = _load_universe(vtxt, "5y")
                    st.session_state["gate"] = rb.validate(H, vno)
            except Exception as e:  # noqa: BLE001
                st.error(f"오류: {e}")
        if "gate" in st.session_state:
            g = st.session_state["gate"]
            st.subheader(f"{g['strategy']} — {g['verdict']}")
            st.caption(f"{g['n_symbols']}종목 · 시도한 설정 {g['trials']}개 · 파라미터 그리드 {g['grid']} · 기본값 {g['default']}")
            icon = {"Pass": "✅", "Warn": "🟡", "Fail": "❌"}
            st.dataframe(pd.DataFrame([(icon[s_], n, d) for n, s_, d in g["checks"]], columns=["", "검사", "결과"]),
                         use_container_width=True, hide_index=True)
            p = g["oos_perf"]
            m = st.columns(4)
            m[0].metric("OOS CAGR", f"{p['CAGR']:.1%}", f"B&H {p['B&H CAGR']:.1%}")
            m[1].metric("OOS Sharpe(연)", f"{p['Sharpe(연)']:.2f}", f"B&H {p['B&H Sharpe(연)']:.2f}")
            m[2].metric("OOS MDD", f"{p['MDD']:.1%}")
            m[3].metric("OOS 거래", f"{len(g['trades'])}회")
            st.line_chart(pd.DataFrame({"전략(OOS)": g["oos_equity"], "Buy&Hold(동일가중)": g["bh_equity"]}))
            st.write("**워크포워드 창별 선택 파라미터와 성과**")
            st.dataframe(g["windows"].astype({"선택 설정": str}).style.format({"IS Sharpe(연)": "{:.2f}", "OOS Sharpe(연)": "{:.2f}", "OOS 수익률": "{:.1%}"}),
                         use_container_width=True, hide_index=True)
            mc = g["mc"]
            st.write("**몬테카를로 (OOS 일수익 블록 부트스트랩 1,000회)**")
            st.write(f"손실로 끝날 확률 {mc['loss_prob'] * 100:.0f}% · 수익률 하위5%/중앙/상위5% {mc['ret_p5']:.0%} / {mc['ret_p50']:.0%} / {mc['ret_p95']:.0%} · "
                     f"MDD 중앙 {mc['mdd_p50']:.0%}, 최악 5% {mc['mdd_p95_worst']:.0%}")
            if g["decay"]:
                d = g["decay"]
                st.write(f"**엣지 감소**: 앞 1/3 거래당 {d['early'] * 100:+.2f}% → 뒤 1/3 {d['late'] * 100:+.2f}% (t={d['t']:.2f}, 음수면 엣지가 줄어드는 중)")
            st.write("**시장 국면별 OOS 성과** (추세/횡보, 변동성, 20일 방향)")
            st.dataframe(g["regimes"].style.format({"누적수익률": "{:.1%}", "연환산 Sharpe": "{:.2f}"}), use_container_width=True, hide_index=True)
            st.caption("방법: PSR/DSR(Bailey·López de Prado), PBO via CSCV, CPCV(퍼지+엠바고), 워크포워드(학습 2년/검증 6개월). "
                       "영감: ralphtradesz/trading-hub 의 검증 게이트(합격 기준 아이디어만 참고). 합격은 '엣지가 있다'가 아니라 '우연으로 설명되지 않는다'는 뜻입니다.")

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
