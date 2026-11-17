# -*- coding: utf-8 -*-
"""hot_kospi 계산: 코스피 반토막 때마다 '본전까지 몇 년' (지수 기준, 배당·수수료·세금 제외).

자료: Yahoo Finance ^KS11 일별 종가(1996-12-11~). 2026-11-17 종가 4,968.48 은 기사(연합뉴스·뉴스1 11/17)로 확인해 덧붙임.
실행: python3 projects/_series_hot/calc_kospi.py   (캐시: /tmp/t3d_hot_kospi/ks11d.json)

전략 정의
 ① 고점 일시매수 = ③ 버티기: 고점 종가에 한 번에 사서 그대로 보유 → 종가가 다시 고점 종가 이상이 된 첫날.
    (지수 기준으로는 ①과 ③이 같은 값이 나온다. 차이는 '중간에 팔았느냐'뿐.)
 ② 적립식: 고점 날 첫 매수, 이후 매달 같은 날짜(휴장이면 다음 거래일)에 같은 금액. 본전 = 평가액 ≥ 넣은 돈.
    바닥(최저 종가일) 이후 처음 본전이 된 날을 기준으로 함(바닥 전 잠깐 본전이 된 경우는 따로 표시).
"""
import json, os, math, datetime as dt, urllib.request

CACHE = '/tmp/t3d_hot_kospi/ks11d.json'
URL = 'https://query1.finance.yahoo.com/v8/finance/chart/%5EKS11?period1=846000000&period2=1800000000&interval=1d'


def load():
    if not os.path.exists(CACHE):
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
        open(CACHE, 'wb').write(urllib.request.urlopen(req, timeout=60).read())
    d = json.load(open(CACHE))['chart']['result'][0]
    rows = {}
    for t, x in zip(d['timestamp'], d['indicators']['quote'][0]['close']):
        if x:
            rows[dt.datetime.fromtimestamp(t + 32400, dt.UTC).date()] = round(x, 2)
    rows[dt.date(2026, 11, 17)] = 4968.48  # 기사 확인 종가
    return sorted(rows.items())


ROWS = load()


def ym(a, b):
    m = (b.year - a.year) * 12 + (b.month - a.month) + (b.day - a.day) / 30.4
    return m


def fmt(m):
    y, mm = divmod(int(round(m)), 12)
    return (f'{y}년 ' if y else '') + (f'{mm}개월' if mm else '')


def monthly_dates(start):
    """start 와 같은 날짜(없으면 다음 거래일)를 매달 하나씩."""
    days = [d for d, _ in ROWS]
    out, y, m = [], start.year, start.month
    while True:
        try:
            target = dt.date(y, m, start.day)
        except ValueError:
            target = dt.date(y, m, 28)
        nxt = next((d for d in days if d >= target), None)
        if nxt is None:
            break
        out.append(nxt)
        m += 1
        if m > 12:
            y, m = y + 1, 1
    return set(out)


def episode(name, a, b):
    win = [(d, x) for d, x in ROWS if a <= str(d) <= b]
    pk_d, pk = max(win, key=lambda r: r[1])
    after = [(d, x) for d, x in ROWS if d > pk_d]
    tr_d, tr = min([r for r in after if str(r[0]) <= b], key=lambda r: r[1])
    dd = tr / pk - 1
    need = pk / tr - 1
    rec = next(((d, x) for d, x in after if x >= pk), None)
    # ② 적립식
    buys = monthly_dates(pk_d)
    units = inv = 0.0
    early = None
    dca = None
    for d, x in [(pk_d, pk)] + after:
        if d in buys or d == pk_d:
            units += 1 / x
            inv += 1
        if d == pk_d:
            continue
        if units * x >= inv:
            if d < tr_d and early is None:
                early = d
            if d > tr_d:
                dca = (d, inv, units * x)
                break
    worst = None
    print(f'\n[{name}] 고점 {pk_d} {pk:,.2f} → 바닥 {tr_d} {tr:,.2f}  하락 {dd*100:.1f}%  바닥에서 본전까지 필요 +{need*100:.1f}%')
    if rec:
        print(f'  ①③ 일시매수·버티기 본전: {rec[0]} ({rec[1]:,.2f})  고점부터 {fmt(ym(pk_d, rec[0]))}  (바닥부터 {fmt(ym(tr_d, rec[0]))})')
    else:
        print('  ①③ 아직 본전 아님')
    if dca:
        print(f'  ② 적립식 본전(바닥 이후): {dca[0]}  고점부터 {fmt(ym(pk_d, dca[0]))}  넣은 횟수 {int(dca[1])}회'
              + (f'  (바닥 전 잠깐 본전: {early})' if early else ''))
    # 적립식 최악 손실률
    units = inv = 0.0
    lo = 0
    for d, x in [(pk_d, pk)] + after:
        if d in buys or d == pk_d:
            units += 1 / x
            inv += 1
        r = units * x / inv - 1
        lo = min(lo, r)
        if dca and d >= dca[0]:
            break
    print(f'  ② 적립식 최악 평가손실 {lo*100:.1f}%  /  ① 최악 {dd*100:.1f}%')
    return dict(pk_d=pk_d, pk=pk, tr_d=tr_d, tr=tr, rec=rec, dca=dca)


if __name__ == '__main__':
    peak, now = 9114.55, 4968.48
    drop = now / peak - 1
    print(f'지금 고점 대비 {drop*100:.2f}%  본전까지 필요 +{(peak/now-1)*100:.2f}%  검증 1/(1-0.455)-1 = {(1/(1-0.455)-1)*100:.2f}%')
    print(f'1,000만 원 → {1000*now/peak:.1f}만 원 (손실 {1000-1000*now/peak:.1f}만 원)')
    print(f'11월 누적: 10월 말 5,730.74 → {now} = {(now/5730.74-1)*100:.2f}%')
    print(f'7월: 6월 말 8,476.48 → 7월 말 6,595.45 = {(6595.45/8476.48-1)*100:.2f}%')
    eps = [
        ('1997~98 외환위기', '1997-01-01', '1998-12-31'),
        ('2000~01 IT버블', '1999-12-01', '2001-12-31'),
        ('2007~08 금융위기', '2007-06-01', '2009-03-31'),
        ('2020 코로나', '2020-01-01', '2020-04-30'),
        ('2021~22 고점 3300', '2021-06-01', '2022-12-31'),
        ('2026 지금', '2026-06-01', '2026-11-30'),
    ]
    res = {n: episode(n, a, b) for n, a, b in eps}
    # 지금 적립식(6/22부터 매달 22일 무렵) 평가
    buys = monthly_dates(dt.date(2026, 6, 22))
    units = inv = 0.0
    for d, x in ROWS:
        if d >= dt.date(2026, 6, 22) and d in buys:
            units += 1 / x; inv += 1
    print(f'\n2026 적립식(6/22부터 {int(inv)}회): 11/17 평가 {units*now/inv*100-100:.1f}%  평균단가 {inv/units:,.0f}')
    # 가정: 과거 '고점→본전' 기간을 6/22 고점에 그대로 적용
    print('\n[가정] 과거 고점→본전(①) 기간을 2026-06-22 고점에 그대로 적용하면:')
    base = dt.date(2026, 6, 22)
    for n in list(res)[:5]:
        r = res[n]
        if r['rec']:
            m = ym(r['pk_d'], r['rec'][0])
            t = base + dt.timedelta(days=m * 30.44)
            print(f'  {n}: {fmt(m)} → {t.year}년 {t.month}월 무렵')
    # 가정2: 바닥→본전 연평균 상승률을 지금(4,968.48)에서 +83.4% 에 적용
    print('\n[가정2] 과거 바닥→본전 연평균 상승 속도를 지금부터 적용하면:')
    for n in list(res)[:5]:
        r = res[n]
        if r['rec']:
            yrs = ym(r['tr_d'], r['rec'][0]) / 12
            cagr = (r['pk'] / r['tr']) ** (1 / yrs) - 1
            need_y = math.log(peak / now) / math.log(1 + cagr)
            print(f'  {n}: 연 {cagr*100:.0f}% 속도 → 약 {need_y:.1f}년')
