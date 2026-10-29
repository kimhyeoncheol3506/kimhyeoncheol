# -*- coding: utf-8 -*-
"""weekly.json → 대본데이터.json (문장마다 [음성용 글, 자막용 글, 장면 신호]) + 조사표.md
숫자는 모두 weekly.json에서 나온 값만 쓴다. 음성용은 한글 숫자, 자막용은 아라비아 숫자.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, "/home/user/kimhyeoncheol/.claude/skills/ranking-video/voice")
from pronounce import sino as _sino, native as _native
sino = lambda n: _sino(int(round(n)))

W = json.load(open(f"{ROOT}/00_data/weekly.json", encoding="utf-8"))
DATA, WEEKS = W["data"], W["weeks"]
HWAL = [("활참돔", "참돔", ""), ("활왕게", "왕게", "킹크랩"), ("활넙치", "넙치", "광어"), ("활수꽃게", "수꽃게", ""), ("활농어", "농어", ""),
        ("활전복", "전복", ""), ("활암꽃게", "암꽃게", ""), ("활참숭어", "참숭어", ""), ("활민어", "민어", ""), ("활감성돔", "감성돔", ""),
        ("활줄돔", "줄돔", "돌돔"), ("활감숭어", "감숭어", "")]
SEON = [("선은갈치", "은갈치", ""), ("선오징어", "무늬오징어", ""), ("선삼치", "삼치", ""), ("선참조기", "참조기", ""), ("선깐굴", "깐굴", ""), ("선고등어", "고등어", "")]
ORD = ["첫째", "둘째", "셋째", "넷째"]


def batchim(w): c = w[-1]; return (ord(c) - 0xAC00) % 28 != 0 if "가" <= c <= "힣" else False
def josa(w, a, b): return a if batchim(w) else b          # 받침 있으면 a, 없으면 b


def won(v):  # (음성, 자막)
    r = int(round(v, -2))
    if r >= 20000:
        r = int(round(v, -3)); return "약 " + sino(r) + " 원", f"약 {r:,}원"
    return sino(r) + " 원", f"{r:,}원"


def ton(kg):
    if kg >= 10000: t = round(kg / 1000); return sino(t) + " 톤", f"{t}톤"
    r = int(round(kg, -2)) if kg >= 1000 else int(round(kg, -1)) or int(round(kg)); return sino(r) + " 킬로그램", f"{r:,}킬로그램"


def pct(x): n = int(round(abs(x))); return sino(n) + " 퍼센트", f"{n}%"


def build(key, name, alias, idx):
    d = DATA[key]; wk = [d["weeks"][str(i)] for i in range(1, 5)]
    P = [w["price"] for w in wk]; K = [w["kg"] for w in wk]
    total = (P[3] / P[0] - 1) * 100
    hi, lo = max(range(4), key=lambda i: P[i]), min(range(4), key=lambda i: P[i])
    state = key[0]
    pw = [won(p) for p in P]
    sents = []

    def add(tts, sub, sig): sents.append([tts, sub, sig])
    # ① 소개 + 첫째 주
    al = f", {alias}{josa(alias, "이라고도", "라고도")} 하죠" if alias else ""
    alsub = f" {alias}{josa(alias, "이라고도", "라고도")} 하죠" if alias else ""
    a = idx % 3
    if a == 0:
        add(f"{name}입니다{al}. 첫째 주 킬로그램당 평균 경락가는 {pw[0][0]}으로 출발했습니다.", f"{name}입니다{alsub} 첫째 주 킬로그램당 평균 경락가는 {pw[0][1]}으로 출발했습니다", dict(point=0))
    elif a == 1:
        who = f"{name}, {alias}{josa(alias, "이라고도", "라고도")} 하죠" if alias else f"다음은 {name}"
        who = ("다음은 " + who) if alias else who
        add(f"{who}. 첫째 주에는 킬로그램당 {pw[0][0]}이었습니다.", f"{who.replace(',', '')} 첫째 주에는 킬로그램당 {pw[0][1]}이었습니다", dict(point=0))
    else:
        add(f"{name}의 한 달을 볼까요? 시월 첫째 주는 킬로그램당 {pw[0][0]}으로 시작합니다.", f"{name}의 한 달을 볼까요? 시월 첫째 주는 킬로그램당 {pw[0][1]}으로 시작합니다", dict(point=0))
    # ②③ 둘째·셋째 주
    for k in (1, 2):
        ch = (P[k] / P[k - 1] - 1) * 100; pc = pct(ch); v = (idx + k) % 3
        if abs(ch) < 2:
            t = f"{ORD[k]} 주는 {pw[k][0]}으로 지난주와 거의 같았습니다."; s = f"{ORD[k]} 주는 {pw[k][1]}으로 지난주와 거의 같았습니다"
        elif ch > 0:
            big = ch >= 15
            t = [f"{ORD[k]} 주에는 {pc[0]} 올라 {pw[k][0]}이 됐습니다.", f"{ORD[k]} 주는 {pw[k][0]}, 지난주보다 {pc[0]} 오른 값입니다.", f"{ORD[k]} 주에 {pc[0]} {'뛰어올라' if big else '올라'} {pw[k][0]}입니다."][v]
            s = [f"{ORD[k]} 주에는 {pc[1]} 올라 {pw[k][1]}이 됐습니다", f"{ORD[k]} 주는 {pw[k][1]} 지난주보다 {pc[1]} 오른 값입니다", f"{ORD[k]} 주에 {pc[1]} {'뛰어올라' if big else '올라'} {pw[k][1]}입니다"][v]
        else:
            big = ch <= -15
            t = [f"{ORD[k]} 주에는 {pc[0]} 내려 {pw[k][0]}이 됐습니다.", f"{ORD[k]} 주는 {pw[k][0]}, 지난주보다 {pc[0]} 내린 값입니다.", f"{ORD[k]} 주에 {pc[0]} {'뚝 떨어져' if big else '내려'} {pw[k][0]}입니다."][v]
            s = [f"{ORD[k]} 주에는 {pc[1]} 내려 {pw[k][1]}이 됐습니다", f"{ORD[k]} 주는 {pw[k][1]} 지난주보다 {pc[1]} 내린 값입니다", f"{ORD[k]} 주에 {pc[1]} {'뚝 떨어져' if big else '내려'} {pw[k][1]}입니다"][v]
        add(t, s, dict(point=k))
    # ④ 넷째 주 + 한 달 변화
    ch = (P[3] / P[2] - 1) * 100; tp = pct(total)
    if abs(total) < 3:
        tail_t, tail_s = "한 달 전과 거의 같은 값입니다.", "한 달 전과 거의 같은 값입니다"
    elif total > 0:
        tail_t, tail_s = f"한 달 전보다 {tp[0]} 오른 값입니다.", f"한 달 전보다 {tp[1]} 오른 값입니다"
    else:
        tail_t, tail_s = f"한 달 전보다 {tp[0]} 내린 값입니다.", f"한 달 전보다 {tp[1]} 내린 값입니다"
    add(f"마지막 넷째 주는 {pw[3][0]}. {tail_t}", f"마지막 넷째 주는 {pw[3][1]} {tail_s}", dict(point=3, final=True))
    # ⑤ 가장 비쌌던 주 · 가장 쌌던 주
    h, l = ORD[hi], ORD[lo]
    if idx % 2 == 0:
        add(f"가장 비쌌던 주는 {h} 주 {pw[hi][0]}, 가장 쌌던 주는 {l} 주 {pw[lo][0]}이었습니다.", f"가장 비쌌던 주는 {h} 주 {pw[hi][1]} 가장 쌌던 주는 {l} 주 {pw[lo][1]}이었습니다", dict(hilo=True))
    else:
        add(f"한 달 중 가장 비싼 주는 {h} 주, 가장 싼 주는 {l} 주였습니다. 값 차이는 킬로그램당 {won(P[hi]-P[lo])[0].replace('약 ', '약 ')}입니다.",
            f"한 달 중 가장 비싼 주는 {h} 주 가장 싼 주는 {l} 주였습니다 값 차이는 킬로그램당 {won(P[hi]-P[lo])[1]}입니다", dict(hilo=True))
    thin = [i for i in range(4) if K[i] < 300]
    if thin:
        ws = "·".join(ORD[i] for i in thin)
        add(f"다만 {ws} 주는 거래 물량이 적어서 참고만 해 주세요.", f"다만 {ws} 주는 거래 물량이 적어서 참고만 해 주세요", dict(thin=thin))
    # ⑥ 물량 (첫째 주 대비 넷째 주 ±30% 이상이거나 산지가 뚜렷할 때)
    vch = (K[3] / K[0] - 1) * 100; kt = [ton(k) for k in K]
    org = d["origins"][0]; share = d["origin_share"][0]
    if abs(vch) >= 30 and (K[0] >= 150 or K[3] >= 150):
        up = vch > 0
        add(f"같은 기간 주간 거래 물량은 {kt[0][0]}에서 {kt[3][0]}으로 {'늘었' if up else '줄었'}습니다.", f"같은 기간 주간 거래 물량은 {kt[0][1]}에서 {kt[3][1]}으로 {'늘었' if up else '줄었'}습니다", dict(volume=True))
    elif share >= 60:
        add(f"{org}산이 한 달 물량의 {sino(share)} 퍼센트를 차지했습니다.", f"{org}산이 한 달 물량의 {share}%를 차지했습니다", dict(volume=True))
    return dict(key=key, name=name, alias=alias, state=state, sentences=sents, P=P, K=K, total=total, hi=hi, lo=lo, origins=d["origins"])


SECS, INFO = [], {}
# -------- 인트로 --------
allc = {k: (v["weeks"]["4"]["price"] / v["weeks"]["1"]["price"] - 1) * 100 for k, v in DATA.items()}
nm = {k: n for grp in (HWAL, SEON) for k, n, _ in grp}
dn = min(allc, key=allc.get); up = max(allc, key=allc.get)
dn2 = sorted(allc, key=allc.get)[1]; up2 = sorted(allc, key=allc.get, reverse=True)[1]
n_down = sum(1 for v in allc.values() if v <= -3); n_up = sum(1 for v in allc.values() if v >= 3)
I = lambda k: pct(allc[k])
intro = [
    [f"한 달 만에 {nm[dn]}{josa(nm[dn], '이', '가')} {I(dn)[0]} 내렸습니다!", f"한 달 만에 {nm[dn]}{josa(nm[dn], '이', '가')} {I(dn)[1]} 내렸습니다!", dict(hook="down", key=dn)],
    [f"반대로 {nm[up]}{josa(nm[up], '은', '는')} {I(up)[0]} 올랐죠.", f"반대로 {nm[up]}{josa(nm[up], '은', '는')} {I(up)[1]} 올랐죠", dict(hook="up", key=up)],
    ["시월 한 달 노량진 시세를 주 단위 그래프로 움직여서 보여드립니다.", "시월 한 달 노량진 시세를 주 단위 그래프로 움직여서 보여드립니다", dict(title=True)],
    ["활어 열두 종, 선어 여섯 종, 첫째 주부터 넷째 주까지 품종마다 흐름을 따라가 보세요.", "활어 12종 선어 6종 첫째 주부터 넷째 주까지 품종마다 흐름을 따라가 보세요", dict(counts=True)],
    ["끝까지 보시면 가장 많이 내린 품종과 오른 품종, 그리고 품종마다 싼 주와 비싼 주를 한눈에 알 수 있습니다.", "끝까지 보시면 가장 많이 내린 품종과 오른 품종 그리고 품종마다 싼 주와 비싼 주를 한눈에 알 수 있습니다", dict(checklist=True)],
    ["자료는 노량진수산 경락시세입니다. 도매 경매가라서 가게 판매가와는 다릅니다.", "자료는 노량진수산 경락시세입니다 도매 경매가라서 가게 판매가와는 다릅니다", dict(method=1)],
    ["킬로그램당 가중평균으로 계산했고, 상하위 오 퍼센트 거래는 뺐습니다. 변동률은 첫째 주와 넷째 주를 비교했습니다.", "킬로그램당 가중평균으로 계산했고 상하위 5% 거래는 뺐습니다 변동률은 첫째 주와 넷째 주를 비교했습니다", dict(method=2)],
    ["먼저 활어부터 갑니다.", "먼저 활어부터 갑니다", dict(go=True)],
]
SECS.append(dict(id="intro", kind="intro", name="인트로", sentences=intro))
SECS.append(dict(id="ch_hwal", kind="chapter", name="활어 편", state="활", sentences=[["수조 속에서 살아 움직이는 활어 열두 종입니다.", "수조 속에서 살아 움직이는 활어 12종입니다", dict(chapter="활")]]))
for i, (k, n, a) in enumerate(HWAL): s = build(k, n, a, i); s.update(id=k, kind="species", short=n, name=n + (f"({a})" if a else "")); SECS.append(s)
SECS.append(dict(id="ch_seon", kind="chapter", name="선어 편", state="선", sentences=[["이번에는 살아 있지는 않지만 싱싱하게 거래되는 선어 여섯 종입니다.", "이번에는 살아 있지는 않지만 싱싱하게 거래되는 선어 6종입니다", dict(chapter="선")]]))
for i, (k, n, a) in enumerate(SEON): s = build(k, n, a, i + 12); s.update(id=k, kind="species", short=n, name=n + (f"({a})" if a else "")); SECS.append(s)
# -------- 아웃트로 --------
d1, d2 = sorted(allc, key=allc.get)[:2]; u1, u2 = sorted(allc, key=allc.get, reverse=True)[:2]
fmt = lambda k: f"{nm[k]} {pct(allc[k])[0]}"; fmts = lambda k: f"{nm[k]} {pct(allc[k])[1]}"
outro = [
    ["시월 한 달 품종 열여덟 종의 흐름을 한 번에 정리해 보겠습니다.", "시월 한 달 품종 18종의 흐름을 한 번에 정리해 보겠습니다", dict(recap=True)],
    [f"가장 많이 내린 품종은 {fmt(d1)}, {fmt(d2)}였고, 가장 많이 오른 품종은 {fmt(u1)}, {fmt(u2)}였습니다.", f"가장 많이 내린 품종은 {fmts(d1)} {fmts(d2)}였고 가장 많이 오른 품종은 {fmts(u1)} {fmts(u2)}였습니다", dict(recap_top=True)],
    [f"제 눈에는 열여덟 종 가운데 값이 내린 품종이 {_native(n_down) or sino(n_down)} 종, 오른 품종이 {_native(n_up) or sino(n_up)} 종으로 보였습니다.", f"제 눈에는 18종 가운데 값이 내린 품종이 {n_down}종 오른 품종이 {n_up}종으로 보였습니다", dict(opinion=True)],
    ["다시 말씀드리지만 오늘 보신 값은 도매 경락가라서 가게 판매가와는 다를 수 있습니다.", "다시 말씀드리지만 오늘 보신 값은 도매 경락가라서 가게 판매가와는 다를 수 있습니다", dict(disclaimer=True)],
    ["구독하고 다음 시세도 확인해 주세요.", "구독하고 다음 시세도 확인해 주세요", dict(end=True)],
]
SECS.append(dict(id="outro", kind="outro", name="요약", sentences=outro))

out = dict(title="10월 노량진 활어·선어 주간 시세 흐름", weeks=WEEKS,
           sections=[dict(id=s["id"], kind=s["kind"], name=s["name"], sentences=s["sentences"], **({k: s[k] for k in ("key", "short", "state", "alias", "P", "K", "total", "hi", "lo", "origins") if k in s})) for s in SECS],
           allc=allc)
json.dump(out, open(f"{HERE}/대본데이터.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
chars = sum(len(x[0].replace(" ", "")) for s in SECS for x in s["sentences"])
print("문장", sum(len(s["sentences"]) for s in SECS), "글자", chars, "예상", round(chars / 6.5 / 60 * 1.0, 1), "분(1.12배 기준 약", round(chars / 7.2 / 60, 1), "분)")
bad = [x[0] for s in SECS for x in s["sentences"] if x[0].startswith("그")]
print("'그' 시작:", bad)
with open(f"{HERE}/조사표.md", "w", encoding="utf-8") as f:
    f.write("# 조사표 — 10월 노량진 주간 시세 (출처: 수협노량진수산 어종별 경락시세 엑셀 20261001-20261028)\n\n")
    f.write("방법: kg당 단가 = 평균가 ÷ 중량(kg), 총중량 = 수량 × 중량(kg). 품종별 한 달 전체 분포에서 상·하위 5% 제외(20건 미만 품종은 제외 안 함) 후 주차별 총거래금액 ÷ 총중량.\n")
    f.write("주차: 1주 10/1~7, 2주 10/8~14, 3주 10/15~21, 4주 10/22~28. (선)오징어는 1주에만 거래 → (선)무늬오징어로 대체.\n\n| 품종 | 1주 | 2주 | 3주 | 4주 | 4주/1주 | 1주 물량 | 4주 물량 | 주요 산지 |\n|---|---|---|---|---|---|---|---|---|\n")
    for s in SECS:
        if s["kind"] != "species": continue
        P, K = s["P"], s["K"]
        f.write(f"| {s['state']} {s['name']} | " + " | ".join(f"{p:,.0f}" for p in P) + f" | {s['total']:+.1f}% | {K[0]:,.0f}kg | {K[3]:,.0f}kg | {'/'.join(s['origins'])} |\n")
