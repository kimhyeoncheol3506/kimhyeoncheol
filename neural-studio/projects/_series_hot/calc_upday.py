# -*- coding: utf-8 -*-
"""코스피 4700 1편 계산 2: '하루 +5% 넘게 오른 날' 종가에 산 사람 vs 그 전부터 들고 있던 사람 (2000~2024, 지수 기준, 배당·수수료·세금 제외).
2026년 Yahoo 일별 값은 기사 고점(10/14 6,008.81)과 맞지 않는 구간이 있어 계산에서 뺌. 오늘 사례(11/24 5,006.03 → 11/25 4,697.51)는 기사로 확인한 종가만 씀.
"""
import json, datetime as dt, statistics as st
d = json.load(open('/tmp/t3d_hot_kospi/ks11d.json'))['chart']['result'][0]
R = [(dt.datetime.fromtimestamp(t + 32400, dt.UTC).date(), c) for t, c in zip(d['timestamp'], d['indicators']['quote'][0]['close']) if c]
R = [x for x in R if dt.date(1999, 12, 1) <= x[0] <= dt.date(2025, 12, 31)]
def ret(a, b): return (b / a - 1) * 100
ev = []
for i in range(1, len(R)):
    if not (2000 <= R[i][0].year <= 2024): continue
    u = ret(R[i-1][1], R[i][1])
    if u >= 5:
        g = lambda k: R[i+k][1] if i + k < len(R) else None
        ev.append(dict(day=str(R[i][0]), up=round(u, 2), next=round(ret(R[i][1], g(1)), 2),
                       w1=round(ret(R[i][1], g(5)), 1), m1=round(ret(R[i][1], g(21)), 1), y1=round(ret(R[i][1], g(252)), 1),
                       hold_m1=round(ret(R[i-1][1], g(21)), 1), hold_y1=round(ret(R[i-1][1], g(252)), 1)))
for e in ev: print(e)
n = len(ev)
print('급등일 수', n, '| 다음 날 하락', sum(e['next'] < 0 for e in ev), '| 다음 날 평균', round(st.mean(e['next'] for e in ev), 2))
print('추격매수(급등일 종가) 1주 마이너스', sum(e['w1'] < 0 for e in ev), '1개월 마이너스', sum(e['m1'] < 0 for e in ev))
print('1개월 평균: 추격', round(st.mean(e['m1'] for e in ev), 1), ' 그냥 둔 사람', round(st.mean(e['hold_m1'] for e in ev), 1))
print('1년 평균: 추격', round(st.mean(e['y1'] for e in ev), 1), ' 그냥 둔 사람', round(st.mean(e['hold_y1'] for e in ev), 1))
print('오늘 사례: 11/24 종가 추격 → 11/25', round(ret(5006.03, 4697.51), 2), '| 11/23 종가부터 보유 →', round(ret(4708.54, 4697.51), 2))
