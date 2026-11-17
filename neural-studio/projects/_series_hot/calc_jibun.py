"""hot_jibun 채널 계산 — 같은 집을 20년 동안 ① 지분적립형 ② 일반분양+주담대 ③ 전세 로 살 때 (2026-11-18).
사용: python3 projects/_series_hot/calc_jibun.py

확인된 제도 (국토교통부 11/4 정책브리핑, 공공주택 특별법 시행령 제2조의2·제46조의2, 비즈워치 11/7):
  - 입주 때까지 분양가 25% 취득, 입주 후 4년마다 15%씩 5회 취득(20년). 회차별 취득 의무, 최대 1년 유예.
  - 미취득 지분 임대료 = 주변 전세 시세의 90% × 미취득 지분율(보증금 예치, 일부 월세 전환 가능).
    월세 전환 시 LH 전월세전환율 3.5%(비즈워치, 변동 가능). 정부 예시: 전세 4억 가정 → 보증금 2.7억 또는 월 79만 원.
  - 추가 지분 가격 = (분양가 + 이자) × 취득 지분율. 이자율 = 최초 취득일과 추가 취득일의
    은행 1년 만기 정기예금 평균이자율을 산술평균한 이자율. → 집값(시세)과 무관, 분양가 기준.
채널 가정 (화면에 '가정'으로 표기):
  - 분양가 5억 1,000만 원(정부 예시: 수도권 평균 공공분양가, 전용 55㎡). 창릉 S-2 실제 분양가는 공고 전.
  - 처음 시세 = 분양가, 주변 전세 4억 원(정부 예시와 같음). 전세는 집값과 같은 비율로 변함.
  - 정기예금 금리 연 3.5%(9월 예금은행 저축성수신금리 3.45% 보도 참고). 기간이자는 단리로 계산.
  - 일반분양+주담대: LTV 70%(대출 3억 5,700만 원), 30년 원리금균등, 금리 연 4.88%(9월 신규 주담대 평균, 한국은행·보도).
    실제 한도는 지역·DSR·소득에 따라 다름.
  - 금리 오를 때 = 지금부터 예금·대출·전환율 모두 +0.5%p 로 20년 유지.
  - 묶인 돈 기회비용 = 집 지분·보증금에 넣은 돈이 못 받은 예금이자(같은 예금 금리, 단리, 해마다).
  - 지분적립형 임대료는 '전액 월세' 방식(정부 예시 79만 원과 같은 방식). 임대료는 2년마다 그때 전세 90% 기준으로 재산정.
  - 세금·취득세·보유세·관리비·중개수수료·물가는 뺐다(세 경우 모두).
"""

P = 510_000_000          # 분양가 (정부 예시)
JEONSE0 = 400_000_000    # 주변 전세 (정부 예시 가정)
YEARS = 20


def won(x):
    """억/만 원 표기 (만 원 미만 반올림)"""
    man = round(x / 10_000)
    eok, rest = divmod(abs(man), 10_000)
    s = ("-" if man < 0 else "")
    if eok and rest:
        return f"{s}{eok}억 {rest:,}만"
    if eok:
        return f"{s}{eok}억"
    return f"{s}{rest:,}만"


def jibun(g, dep, conv, dep_up=0.0):
    """g: 집값(전세) 연 상승률, dep: 지금 정기예금 금리, conv: 전월세전환율, dep_up: 앞으로 예금금리 변화"""
    dep_later = dep + dep_up
    paid_equity = 0.25 * P
    out_init = paid_equity
    buys, rent_total, opp = [], 0.0, 0.0
    share_owned = 0.25
    for y in range(YEARS):
        # 이번 해 월세: 2년마다 재산정(그때 전세 × 90% × 미취득 지분)
        reset = y - y % 2
        jeonse = JEONSE0 * (1 + g) ** reset
        deposit_equiv = jeonse * 0.9 * (1 - share_owned)
        rent_total += deposit_equiv * conv
        opp += paid_equity * (dep if y == 0 else dep_later)
        # 4년마다 15% 취득 (연말)
        if (y + 1) % 4 == 0:
            t = y + 1
            r_avg = (dep + dep_later) / 2
            price = (P + P * r_avg * t) * 0.15
            buys.append((t, price))
            paid_equity += price
            share_owned += 0.15
    value_end = P * (1 + g) ** YEARS
    total_out = out_init + sum(b for _, b in buys) + rent_total
    return dict(init=out_init, buys=buys, rent=rent_total, total=total_out, asset=value_end,
                net=total_out - value_end, net_opp=total_out + opp - value_end, opp=opp,
                rent0=JEONSE0 * 0.9 * 0.75 * conv / 12)


def mortgage(g, rate, dep, ltv=0.7, n_years=30):
    loan = P * ltv
    down = P - loan
    i = rate / 12
    n = n_years * 12
    pay = loan * i / (1 - (1 + i) ** -n)
    bal, interest, opp, principal_paid = loan, 0.0, 0.0, 0.0
    for m in range(YEARS * 12):
        it = bal * i
        interest += it
        bal -= pay - it
        principal_paid += pay - it
        if m % 12 == 11:
            opp += (down + principal_paid) * dep
    value_end = P * (1 + g) ** YEARS
    total_out = down + pay * YEARS * 12
    asset = value_end - bal
    return dict(down=down, pay=pay, interest=interest, bal=bal, total=total_out, asset=asset,
                net=total_out - asset, net_opp=total_out + opp - asset, opp=opp)


def jeonse(g, dep):
    opp, total_extra = 0.0, 0.0
    dep_amt = JEONSE0
    for y in range(YEARS):
        if y and y % 2 == 0:
            new = JEONSE0 * (1 + g) ** y
            total_extra += new - dep_amt
            dep_amt = new
        opp += dep_amt * dep
    total_out = JEONSE0 + total_extra
    return dict(total=total_out, asset=dep_amt, net=total_out - dep_amt, opp=opp, net_opp=opp)


def show():
    for label, dep, mrate, conv, up in (("금리 지금", 0.035, 0.0488, 0.035, 0.0),
                                        ("금리 +0.5%p", 0.035, 0.0538, 0.040, 0.005)):
        for g in (0.0, 0.02):
            j = jibun(g, dep, conv, up)
            mo = mortgage(g, mrate, dep + up)
            je = jeonse(g, dep + up)
            print(f"\n=== {label} · 집값 연 {g*100:.0f}% ===")
            print(f" ① 지분적립형: 처음 {won(j['init'])} · 첫 월세 {round(j['rent0']/1e4)}만 · 추가지분 "
                  + ", ".join(f"{t}년 {won(b)}" for t, b in j['buys']))
            print(f"    지분대금 합 {won(j['init'] + sum(b for _, b in j['buys']))} · 월세 합 {won(j['rent'])} · "
                  f"총유출 {won(j['total'])} · 20년 뒤 집 {won(j['asset'])} · 순비용 {won(j['net'])} · 기회비용 포함 {won(j['net_opp'])}")
            print(f" ② 일반+주담대: 계약금 {won(mo['down'])} · 월 {round(mo['pay']/1e4)}만 · 이자 합 {won(mo['interest'])} · "
                  f"남은 빚 {won(mo['bal'])} · 총유출 {won(mo['total'])} · 남는 자산 {won(mo['asset'])} · 순비용 {won(mo['net'])} · 기회비용 포함 {won(mo['net_opp'])}")
            print(f" ③ 전세: 보증금 {won(JEONSE0)} → {won(je['asset'])} · 기회비용(=순비용) {won(je['net_opp'])}")


def extras():
    print("\n=== 덧붙임 ===")
    for dep in (0.035, 0.04):
        paid = 0.25 * P + sum(0.15 * (P + P * ((0.035 + dep) / 2) * t) for t in (4, 8, 12, 16, 20))
        be = (paid / P) ** (1 / YEARS) - 1
        print(f" 예금 {dep*100:.1f}%: 지분대금 합 {won(paid)} → 집값이 연 {be*100:.2f}% 넘게 올라야 20년 뒤 집값 > 낸 지분값")
    for g in (-0.01,):
        j = jibun(g, 0.035, 0.035)
        print(f" 집값 연 {g*100:.0f}%: 20년 뒤 집 {won(j['asset'])} · 지분대금 합 {won(j['init'] + sum(b for _, b in j['buys']))} · "
              f"차이 {won(j['init'] + sum(b for _, b in j['buys']) - j['asset'])}")
    j = jibun(0.0, 0.035, 0.035)
    first = j['buys'][0][1]
    print(f" 4년 뒤 첫 추가지분 {won(first)} → 48개월로 나누면 월 {round(first/48/1e4)}만 + 첫 월세 {round(j['rent0']/1e4)}만"
          f" = 월 {round((first/48 + j['rent0'])/1e4)}만 (예금이자 없이 모은다고 가정)")
    print(f" 25% 금액: 5.1억 → {won(0.25*P)} · 창릉 S-4 59㎡ 6억 2,468만 → {won(0.25*624_680_000)}")
    for g in (0.0, 0.02, 0.04):
        row = []
        for t in (4, 8, 12, 16, 20):
            row.append(f"{t}년 시세 {won(0.15*P*(1+g)**t)}/값 {won(0.15*(P+P*0.035*t))}")
        print(f" 집값 연 {g*100:.0f}% · 15%의 시세 vs 내는 값: " + " · ".join(row))
    for t in (4, 20):
        print(f" {t}년 뒤 회차: 집값이 연 {((1+0.035*t)**(1/t)-1)*100:.2f}% 넘게 올라야 시세보다 싸게 사는 셈")
    print(f" 15% 원금만: {won(0.15*P)} · 20년 이자 붙은 마지막 회차 {won(j['buys'][-1][1])}")


if __name__ == "__main__":
    show()
    extras()
