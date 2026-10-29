# -*- coding: utf-8 -*-
"""10월 노량진 경락시세 → 주간(1~7, 8~14, 15~21, 22~28일) kg당 평균가
 1) 규격 단위 표준화: 모든 행 kg당 단가 = 평균가 ÷ 중량(kg), 총중량 = 수량 × 중량(kg)  (kg 포장은 중량 1)
 2) 이상치 제거: 품종별 한 달 전체 kg당 단가 분포에서 상·하위 5% 거래건 제외(20건 미만 품종은 제외 안 함)
 3) 거래 물량(kg)으로 가중평균
"""
import json, sys, numpy as np, pandas as pd
SRC = sys.argv[1]; OUT = sys.argv[2]
df = pd.read_excel(SRC, header=3)
df = df[df['평균가(원)'] > 0].copy()
df = df[df['중량(kg)'] > 0]
df['총kg'] = df['수량'] * df['중량(kg)']          # 포장 종류와 상관없이 수량 × 상자(단위)당 kg
df['kg단가'] = df['평균가(원)'] / df['중량(kg)']   # 평균가는 그 포장 단위 가격 → kg당으로 환산
df = df[df['총kg'] > 0]
# 이상치 제거(사용자 제시 방식): 품종(상태 포함)별로 한 달 전체의 kg당 단가 분포에서 5%·95% 밖을 제외, 20건 미만은 그대로
def _cut(g):
    if len(g) < 20: return g
    a, b = g['kg단가'].quantile(0.05), g['kg단가'].quantile(0.95)
    return g[(g['kg단가'] >= a) & (g['kg단가'] <= b)]
df = pd.concat([_cut(g) for _, g in df.groupby('품종')])
df['주'] = ((df['일자'].dt.day - 1) // 7 + 1)
WEEKS = {1: '10/1~10/7', 2: '10/8~10/14', 3: '10/15~10/21', 4: '10/22~10/28'}
HWAL = ['참돔', '왕게', '넙치', '수꽃게', '농어', '전복', '암꽃게', '참숭어', '민어', '감성돔', '줄돔', '감숭어']
SUBST = {'선오징어': '무늬오징어'}  # (선)오징어는 10/1~7에만 거래돼 주간 흐름이 안 나옴 → 4주 모두 거래된 (선)무늬오징어로 대체
SEON = ['은갈치', '오징어', '삼치', '참조기', '깐굴', '고등어']
def stat(g, trim=0.05):
    n = len(g); t = g  # 컷은 위에서 한 달 기준으로 이미 적용
    return dict(price=float((t['kg단가'] * t['총kg']).sum() / t['총kg'].sum()), n=int(n), n_used=int(len(t)), kg=float(t['총kg'].sum()),
                lo=float(t['kg단가'].min()), hi=float(t['kg단가'].max()), days=int(g['일자'].nunique()))
res = {}
for st, names in (('활', HWAL), ('선', SEON)):
    for nm in names:
        src = SUBST.get(f'{st}{nm}', nm)  # 엑셀에 주차 데이터가 없는 품종은 같은 상태의 대체 품종(아래 SUBST)
        s = df[df['품종'] == f'({st}){src}']
        top = s.groupby('산지')['총kg'].sum().sort_values(ascending=False)
        res[f'{st}{nm}'] = dict(source=f'({st}){src}', origins=[o for o in top.index[:2]], origin_share=[round(float(v / top.sum()) * 100) for v in top.iloc[:2]],
                                weeks={w: stat(s[s['주'] == w]) if (s['주'] == w).any() else None for w in WEEKS})
json.dump(dict(weeks=WEEKS, data=res), open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in res.items():
    print(k, v['origins'], v['origin_share'], ' | '.join(f"{w}주 {x['price']:>8,.0f}원 {x['kg']:>7,.0f}kg {x['n_used']}/{x['n']}건" if x else f'{w}주  —' for w, x in v['weeks'].items()))
