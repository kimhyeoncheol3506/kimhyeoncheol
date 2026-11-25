# -*- coding: utf-8 -*-
"""코스피 4700 1편 계산: '급등 다음 날 급락' (지수 기준, 배당·수수료·세금 제외).
자료: Yahoo Finance ^KS11 일별 종가(1996-12-11~2026-11-25). 캐시 /tmp/t3d_hot_kospi/ks11d.json
정의: U일 = 전날 대비 +UP% 이상 오른 날. 그다음 거래일 D = -DN% 이상 내린 날이면 '휩쏘'.
 - 추격매수: U일 종가에 산 사람 → D일 종가 평가(하루 손실), 투매(D일 종가에 팔면) 확정손실.
 - 그냥 둔 사람: U일 전날 종가부터 들고 있던 사람 → D일 종가(두 날 합산), 1년 뒤.
 - D일 종가에 판 사람 vs 버틴 사람: D일 종가 → 1년(252거래일) 뒤.
"""
import json, datetime as dt, statistics as st, sys
d = json.load(open('/tmp/t3d_hot_kospi/ks11d.json'))['chart']['result'][0]
R = [(dt.datetime.fromtimestamp(t + 32400, dt.UTC).date(), c) for t, c in zip(d['timestamp'], d['indicators']['quote'][0]['close']) if c]
UP, DN = float(sys.argv[1]) if len(sys.argv) > 1 else 5, float(sys.argv[2]) if len(sys.argv) > 2 else 4
def ret(a, b): return (b / a - 1) * 100
ev = []
for i in range(1, len(R) - 1):
    u = ret(R[i-1][1], R[i][1]); dd = ret(R[i][1], R[i+1][1])
    if u >= UP and dd <= -DN:
        y = R[i+1+252][1] if i + 1 + 252 < len(R) else None
        ev.append(dict(up_day=str(R[i][0]), up=round(u, 2), dn=round(dd, 2), two_day=round(ret(R[i-1][1], R[i+1][1]), 2),
                       buyU_1y=round(ret(R[i][1], y), 1) if y else None, D_1y=round(ret(R[i+1][1], y), 1) if y else None,
                       hold_1y=round(ret(R[i-1][1], y), 1) if y else None))
for e in ev: print(e)
f = [e for e in ev if e['D_1y'] is not None]
print('n', len(ev), 'with1y', len(f))
if f:
    print('D일에 판 사람 1년 뒤 0% / 버틴 사람 평균', round(st.mean(e['D_1y'] for e in f), 1), '중앙', round(st.median(e['D_1y'] for e in f), 1), '플러스', sum(e['D_1y'] > 0 for e in f))
    print('급등일 추격매수 1년 평균', round(st.mean(e['buyU_1y'] for e in f), 1), '그냥 둔 사람(급등 전날부터) 1년 평균', round(st.mean(e['hold_1y'] for e in f), 1))
    print('급등일 산 사람 이틀째 평균', round(st.mean(e['dn'] for e in ev), 2))
