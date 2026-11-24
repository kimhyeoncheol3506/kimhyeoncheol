# -*- coding: utf-8 -*-
"""크리스마스·연말 회 장보기(지금 사두면 얼마 아끼나 → 언제 사러 갈까) 대본 → 대본데이터.json
숫자: 00_data/prices.json(노량진 경락시세 일별 수집본, kg당 수량 가중 중앙값)과 조사_연말1편.md(1인 200g·수율)만. 최근 4주 변동폭 30% 이상 품목 제외.
표기: {p:59200}=금액(음성·자막 천 원 단위 반올림) {e:14800}=금액 그대로 {pc:40}=퍼센트 {k:2}=킬로그램 {kd:2.7}=소수 킬로그램 {g:200}=그램 {n:10}=수 {y:2025}=연도
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, "/home/user/kimhyeoncheol/.claude/skills/ranking-video/voice")
from pronounce import sino as _s
sino = lambda n: _s(int(n)); DIG = "영일이삼사오육칠팔구"
P = json.load(open(f"{ROOT}/00_data/prices.json", encoding="utf-8"))


def dec(v):
    a, _, b = v.partition("."); return sino(int(a)) + (" 점 " + " ".join(DIG[int(c)] for c in b) if b else "")


def won(n):
    r = int(n / 1000 + 0.5); m, k = divmod(r, 10)
    if k == 0: return sino(m * 10000) + " 원", f"{m}만 원"
    return ((sino(m * 10000) + " ") if m else "") + sino(k * 1000) + " 원", ((f"{m}만 ") if m else "") + f"{k}천 원"


def tok(kind, v):
    if kind == "p": return won(int(v))
    if kind == "e": n = int(v); return sino(n).replace("만 천", "만 일천") + " 원", f"{n:,}원"  # '이만 천이백'은 '이천이백'으로 들림 → '이만 일천이백'
    if kind == "pc": return sino(int(v)) + " 퍼센트", f"{v}%"
    if kind == "k": return sino(int(v)) + " 킬로그램", f"{v}kg"
    if kind == "kd": return dec(v) + " 킬로그램", f"{v}kg"
    if kind == "g": return sino(int(v)) + " 그램", f"{v}g"
    if kind == "n": return sino(int(v)), v
    if kind == "kq": return sino(int(v)) + " 킬로그램", f"{int(v):,}kg"
    if kind == "y": return sino(int(v)) + "년", f"{v}년"
    raise ValueError(kind)


SUBFIX = []  # 아래에서 채움


def S(text, **sig):
    tts = re.sub(r"\{(\w+):([^}]+)\}", lambda m: tok(m.group(1), m.group(2))[0], text)
    sub = re.sub(r"\{(\w+):([^}]+)\}", lambda m: tok(m.group(1), m.group(2))[1], text)
    for a, b in sorted(SUBFIX, key=lambda x: -len(x[0])): sub = sub.replace(a, b)
    return [tts, sig, sub]




WK = P["weeks"]; TWO = P["two"]; VAR = P["var4"]
FISH = [("광어", "넙치(활)", 0.40), ("참돔", "참돔(활)", 0.30), ("농어", "농어(활)", 0.40)]
wk = lambda lab: next(w for w in WK if w["week"] == lab)
F1, XM = wk("작년 12/1~12/6"), wk("작년 12/22~12/27")
LAST = WK[3]["week"].split("~")[1]  # 올해 마지막 날짜 m/d
pr = lambda w, k: w["items"][k]["med"]
kgf = lambda n, y: n * 0.2 / y
r1000 = lambda v: (lambda r: (f"{r // 10}만" if r >= 10 else "") + (f" {r % 10}천" if r % 10 else ""))(int(v / 1000 + 0.5)).strip()
T = {n: TWO["items"][k]["med"] for n, k, _ in FISH}; A = {n: pr(F1, k) for n, k, _ in FISH}; X = {n: pr(XM, k) for n, k, _ in FISH}; Y = {n: y for n, _, y in FISH}
pct = lambda a, b: round((b - a) / a * 100)
BUD = lambda n, ppl, price: kgf(ppl, Y[n]) * price
DIFF10 = {n: BUD(n, 10, X[n]) - BUD(n, 10, A[n]) for n in T}
BIG = max(DIFF10, key=DIFF10.get); SMALL = min(DIFF10, key=DIFF10.get)
EXCL = [k.split("(")[0] for k, v in VAR.items() if v >= 30]
SUBFIX += [("십이월 첫 주", "12월 첫 주"), ("크리스마스 주", "크리스마스 주"), ("열 명", "10명"), ("여섯 명", "6명"), ("네 명", "4명"), ("두 가지", "2가지"), ("세 가지", "3가지"), ("다섯 가지", "5가지"), ("네 주", "4주"), ("두 주", "2주"),
           ("일 인당", "1인당"), ("이백 그램", "200g"), ("사십 퍼센트", "40%"), ("삼십 퍼센트", "30%"), ("십이월", "12월"), ("십일월", "11월"), ("이천이십오년", "2025년"), ("오 킬로그램", "5kg"), ("이 킬로그램", "2kg"), ("일 점", "1."),
           ("이틀", "이틀"), ("하루", "하루"), ("일요일", "일요일")]
D_LAST = TWO["week"].split("~")[1]; dd = int(D_LAST.split("/")[1])
PER2 = f"십일월 십육일부터 {sino(dd)}일까지"; SUBFIX += [(PER2, f"11월 16일부터 {dd}일까지")]
B10 = {n: (BUD(n, 10, A[n]), BUD(n, 10, X[n])) for n in T}
TAB = []
for n, k, y in FISH:
    TAB.append([n, f"수율 {int(y * 100)}% · 작년 kg당 {A[n]:,} → {X[n]:,}원", [(f"{r1000(BUD(n, p, A[n]))} → {r1000(BUD(n, p, X[n]))}", f"+{r1000(BUD(n, p, X[n]) - BUD(n, p, A[n]))}원") for p in (4, 6, 10)]])
NOW = [[n, f"수율 {int(Y[n] * 100)}% · 최근 2주 kg당 {T[n]:,}원", [(f"{kgf(p, Y[n]):.1f}kg", f"{r1000(BUD(n, p, T[n]))}원") for p in (4, 6, 10)]] for n, _, _ in FISH]
up_dn = lambda a, b: "올랐어요" if b > a else "내렸어요"
SECS = [
 dict(id="hook", kind="hook", name="오프닝", vis=dict(q="크리스마스 주에 사면<br>얼마 더 낼까?", label=f"작년 · 10명 · {BIG} {kgf(10, Y[BIG]):g}kg · 도매 경락가", won=int(DIFF10[BIG]), sub=f"12월 첫 주 {int(B10[BIG][0]):,}원 → 크리스마스 주 {int(B10[BIG][1]):,}원",
     note="작년 데이터 · 올해 보장 아님 · 가게 판매가와 다름", two=[("언제 사러 갈지", "활어는 미리 사 두는 게 아님"), ("생선 조합", "주마다 다른 값 차이")], agenda=["작년 12월 주별 흐름", "인원별 예산 차이", "올해 지금 값", "언제 사러 갈까"]),
     sentences=[
  S("크리스마스 주에 회를 사면, 십이월 첫 주보다 얼마나 더 낼까요?", q=1),
  S(f"작년 노량진 경락가로 계산하면, 열 명이 {BIG}로만 먹을 때 약 {{p:{int(DIFF10[BIG])}}}을 더 냈습니다.", count=1),
  S(f"십이월 첫 주엔 약 {{p:{int(B10[BIG][0])}}}, 크리스마스 주엔 약 {{p:{int(B10[BIG][1])}}}이었어요.", count=2),
  S("다만 활어는 미리 사 두는 게 아닙니다. 아끼는 방법은 언제 사러 갈지, 그리고 어떤 생선을 고를지예요.", two=1),
  S("오늘은 작년 십이월 주별 흐름으로, 첫 주와 크리스마스 주 차이를 인원별 예산으로 바꿔 보고, 올해 지금 값까지 확인합니다.", agenda=1),
  S("지난 연말 모임 편의 후속이라, 그 편의 계산법을 그대로 씁니다.", agenda=2)]),
 dict(id="title", kind="title", name="데이터 설명", vis=dict(cards=[
   dict(sig=["title", 1], kick="NORYANGJIN · CHRISTMAS DATA", big="크리스마스·연말 회 장보기", bigsize=96, lines=["12월 첫 주 vs 크리스마스 주 · 인원별 예산"], top=260),
   dict(sig=["src", 1], kick="SOURCE", photo="시장", lines=["노량진수산(주) 어종별 경락시세(일별 수집본)", "<span style='color:#8C919B;font-size:36px'>새벽 경매 낙찰가 · 도매 가격 · kg 경매 수량 가중 중앙값</span>"], top=260),
   dict(sig=["period", 1], kick="PERIOD", lines=[f"올해 최근 2주 · {TWO['week']} ({len(TWO['days'])}일)", "<span style='color:#8C919B'>작년 · 2025.11.24 ~ 12.31 주별 (월~토 전체)</span>",
         f"<span style='color:#E4775F;font-size:38px'>최근 4주 변동폭 30% 이상 제외 · {', '.join(EXCL) or '없음'}</span>"], top=250),
   dict(sig=["warn", 0], kick="꼭 알아 두세요", lines=["① 경락가 = 도매 낙찰가 ≠ 가게 판매가", "② 작년 12월 = 과거 데이터 ≠ 올해 보장", "③ 활어는 미리 사 두는 게 아님 → 언제 사러 갈지"], size=48, top=230)]), sentences=[
  S("크리스마스와 연말 회 장보기, 데이터로 봅니다.", title=1),
  S("가격은 노량진수산주식회사의 어종별 경락시세 일별 수집본, 새벽 경매 낙찰가예요.", src=1),
  S("킬로그램 단위 경매의 수량 가중 중앙값으로 계산했습니다.", src=2),
  S(f"올해는 최근 두 주, {PER2}의 값을 썼어요.", period=1),
  S("작년은 십일월 마지막 주부터 십이월 말까지, 월요일부터 토요일까지 모든 날짜를 주별로 묶었습니다.", period=2),
  S("지난 편에서는 작년 값을 주마다 월요일과 화요일 이틀만 뽑았는데, 이번엔 모든 날짜를 넣어서 값이 조금 달라요.", period=2),
  S("최근 네 주 동안 값이 평균의 삼십 퍼센트 넘게 오르내린 생선은 이번에도 뺐습니다." + (f" 방어가 그래서 빠졌어요." if "방어" in EXCL else ""), period=3),
  S("먼저 세 가지를 꼭 알아 두세요.", warn=0),
  S("첫째, 경락가는 도매 낙찰가라서, 가게에서 사는 값과 다릅니다.", warn=1),
  S("둘째, 작년 숫자는 과거 데이터라서, 올해도 똑같이 흘러간다는 보장은 없어요.", warn=2),
  S("셋째, 활어는 오래 둘 수 없어요. 그래서 오늘 얘기는 미리 사 두기가 아니라, 언제 사러 갈지입니다.", warn=3)]),
 dict(id="recent", kind="faq", name="올해 최근 2주", vis=dict(cards=[
   dict(sig=["r", 0], kick=f"올해 최근 2주 · {TWO['week']} · kg당 경락가", lines=[f"광어 {T['광어']:,}원", f"참돔 {T['참돔']:,}원", f"농어 {T['농어']:,}원"], size=62, top=220),
   dict(sig=["r", 1], kick="최근 4주 변동폭 · (최고 − 최저) ÷ 평균", lines=[f"광어 {VAR['넙치(활)']:g}% · 참돔 {VAR['참돔(활)']:g}% · 농어 {VAR['농어(활)']:g}%", f"<span style='color:#E4775F;font-size:40px'>방어 {VAR['방어(활)']:g}% → 제외</span>"], size=54, top=240),
   dict(sig=["r", 2], kick="작년 12월 첫 주보다", lines=[f"광어 {pct(A['광어'], T['광어']):+d}%", f"참돔 {pct(A['참돔'], T['참돔']):+d}%", f"농어 {pct(A['농어'], T['농어']):+d}%"], size=64, top=220)]), sentences=[
  S("올해 지금 값부터 볼게요.", r=0),
  S(f"최근 두 주 킬로그램당 경락가는 광어 {{e:{T['광어']}}}, 참돔 {{e:{T['참돔']}}}, 농어 {{e:{T['농어']}}}입니다.", r=0),
  S(f"최근 네 주 변동폭은 광어 {{pc:{round(VAR['넙치(활)'])}}}, 참돔 {{pc:{round(VAR['참돔(활)'])}}}, 농어 {{pc:{round(VAR['농어(활)'])}}}로, 모두 삼십 퍼센트 안쪽이었어요.", r=1),
  S(f"방어는 {{pc:{round(VAR['방어(활)'])}}}나 오르내려서, 계산에서 뺐습니다.", r=1),
  S("작년 십이월 첫 주와 비교하면 어떨까요?", r=2),
  S(f"광어는 작년 {{e:{A['광어']}}}에서 올해 {{e:{T['광어']}}}으로, 약 {{pc:{abs(pct(A['광어'], T['광어']))}}} {up_dn(A['광어'], T['광어'])}.", r=2),
  S(f"참돔은 {{e:{A['참돔']}}}에서 {{e:{T['참돔']}}}, 농어는 {{e:{A['농어']}}}에서 {{e:{T['농어']}}}이에요.", r=2)]),
]
XS = ["작년 11/24~11/29", "작년 12/1~12/6", "작년 12/8~12/13", "작년 12/15~12/20", "작년 12/22~12/27", "작년 12/29~12/31"]
dl = lambda k: [pr(wk(x), k) for x in XS]
lo_w = lambda k: XS[dl(k).index(min(dl(k)))].replace("작년 ", "")
SECS += [dict(id="flow", kind="flow", name="작년 12월 주별 흐름", vis=dict(title="작년(2025) kg당 경락가 주별 · 월~토 전체 · 과거 데이터", x=["11/24", "12/1", "12/8", "12/15", "12/22", "12/29"], ymin=15000, ymax=25000, step=2500,
    lines=[dict(name="광어", c="#F1D9A0", p=dl("넙치(활)")), dict(name="참돔", c="#E4775F", p=dl("참돔(활)")), dict(name="농어", c="#5FB7A6", p=dl("농어(활)"))],
    rc=[["line", 0, "광어 · 작년", [f"첫 주 {A['광어']:,} → 크리스마스 주 {X['광어']:,}원", f"{pct(A['광어'], X['광어']):+d}% · 가장 작은 변화"]], ["line", 1, "참돔 · 작년", [f"첫 주 {A['참돔']:,} → 크리스마스 주 {X['참돔']:,}원", f"{pct(A['참돔'], X['참돔']):+d}%"]],
        ["line", 2, "농어 · 작년", [f"첫 주 {A['농어']:,} → 크리스마스 주 {X['농어']:,}원", f"{pct(A['농어'], X['농어']):+d}% · 가장 큰 변화"]], ["season", 1, "작년 흐름", ["세 생선 모두", "크리스마스 주가 12월 첫 주보다 비쌌다"]]]), sentences=[
  S("작년 십이월은 어떻게 흘러갔을까요?", chart=1),
  S("작년 십일월 마지막 주부터 십이월 말까지, 주별 경락가를 그려 봤습니다.", chart=2),
  S(f"광어는 십이월 첫 주 {{e:{A['광어']}}}, 크리스마스 주 {{e:{X['광어']}}}. 약 {{pc:{pct(A['광어'], X['광어'])}}}로 거의 그대로였어요.", line=0),
  S(f"참돔은 {{e:{A['참돔']}}}에서 {{e:{X['참돔']}}}, 약 {{pc:{pct(A['참돔'], X['참돔'])}}} 올랐습니다.", line=1),
  S(f"농어는 {{e:{A['농어']}}}에서 {{e:{X['농어']}}}, 약 {{pc:{pct(A['농어'], X['농어'])}}}로 가장 많이 올랐어요.", line=2),
  S("작년엔 세 생선 모두, 크리스마스 주가 십이월 첫 주보다 비쌌습니다.", season=1),
  S("다만 한 해 데이터일 뿐이라, 올해도 그렇다고 단정할 수는 없어요.", end=1)]),
 dict(id="table", kind="table", name="인원별 예산 차이", vis=dict(kick="작년 가격 · 12월 첫 주 → 크리스마스 주 · 인원별 도매가 예산 (1인 회 200g ÷ 수율)", head=["4명", "6명", "10명"], rows=TAB,
     foot="작년(2025) 경락가 · 과거 데이터 · 금액은 천 원 단위 반올림 · 가게 판매가 아님"), sentences=[
  S("이 차이를 인원별 예산으로 바꿔 볼게요. 계산법은 지난 편과 같습니다. 일 인당 회 이백 그램을 수율로 나눠요."),
  S(f"광어는 열 명 기준 약 {{p:{int(B10['광어'][0])}}}에서 {{p:{int(B10['광어'][1])}}}. 차이는 약 {{p:{int(DIFF10['광어'])}}}이에요.", row=0),
  S(f"참돔은 수율이 낮아 킬로그램이 더 필요해서, 열 명이면 약 {{p:{int(DIFF10['참돔'])}}} 차이가 났습니다.", row=1),
  S(f"농어는 열 명 기준 약 {{p:{int(B10['농어'][0])}}}에서 {{p:{int(B10['농어'][1])}}}. 약 {{p:{int(DIFF10['농어'])}}}을 더 냈어요.", row=2),
  S(f"네 명이면 농어로 약 {{p:{int(BUD('농어', 4, X['농어']) - BUD('농어', 4, A['농어']))}}}, 광어로는 약 {{p:{int(BUD('광어', 4, X['광어']) - BUD('광어', 4, A['광어']))}}} 차이예요.", foot=1),
  S("인원이 많을수록, 그리고 값이 많이 오르는 생선일수록 차이가 커집니다.", foot=2)]),
 dict(id="now", kind="table", name="올해 지금 값 예산", vis=dict(kick=f"올해 최근 2주({TWO['week']}) 경락가 · 인원별 필요 kg · 도매가 예산", head=["4명", "6명", "10명"], rows=NOW, foot="필요 kg = 인원 × 200g ÷ 수율 · 금액은 천 원 단위 반올림 · 가게 판매가 아님"), sentences=[
  S("올해 지금 값으로는 얼마일까요?"),
  S(f"광어는 네 명 이 킬로그램에 약 {{p:{int(BUD('광어', 4, T['광어']))}}}, 열 명 오 킬로그램에 약 {{p:{int(BUD('광어', 10, T['광어']))}}}입니다.", row=0),
  S(f"참돔은 열 명이면 약 {{p:{int(BUD('참돔', 10, T['참돔']))}}}이에요.", row=1),
  S(f"농어는 열 명 오 킬로그램에 약 {{p:{int(BUD('농어', 10, T['농어']))}}}으로, 세 생선 중 가장 낮습니다.", row=2),
  S(f"올해 광어는 작년 이맘때보다 비싸서, 열 명 광어 예산이 작년 크리스마스 주보다도 약 {{p:{int(BUD('광어', 10, T['광어']) - B10['광어'][1])}}} 높아요.", foot=1)]),
 dict(id="when", kind="calc", name="언제 사러 갈까", vis=dict(cards=[
   dict(sig=["w", 1], kick="먼저 · 활어는 미리 사 두는 게 아님", photo="수조", lines=["모임 당일 사서 바로 회로", "<span style='color:#8C919B;font-size:36px'>아끼는 건 '언제 사러 갈지'와 '어떤 생선'</span>"], top=180),
   dict(sig=["w", 2], kick="날짜를 고를 수 있다면", big="12월 초·중순", bigsize=120, lines=["작년엔 세 생선 모두 크리스마스 주보다 쌌다", "<span style='color:#8C919B;font-size:34px'>과거 데이터 · 올해 보장 아님</span>"], top=220),
   dict(sig=["w", 3], kick="크리스마스 주라면", lines=[f"광어 중심 · 작년 변화 {pct(A['광어'], X['광어']):+d}%", f"농어 비중은 줄이기 · 작년 {pct(A['농어'], X['농어']):+d}%", "<span style='color:#8C919B;font-size:34px'>올해 지금은 농어가 가장 쌈 → 그 주 값 확인</span>"], size=52, top=230),
   dict(sig=["w", 4], kick="가기 전에", lines=["매주 토요일 노량진 주간 시세", "그 주 경락가 확인 후 생선 조합 정하기"], size=54, top=260)]), sentences=[
  S("언제 사러 가는 게 좋을까요?", w=0),
  S("먼저, 활어는 오래 두고 먹는 게 아닙니다. 모임 날 사서 바로 회로 뜨는 게 기본이에요.", w=1),
  S("지금 미리 사 두는 게 아니라, 모임 날짜와 장 보는 날을 어떻게 잡을지가 핵심입니다.", w=1),
  S("모임 날짜를 고를 수 있다면, 십이월 초나 중순이 유리했어요. 작년엔 세 생선 모두 크리스마스 주보다 쌌습니다.", w=2),
  S("물론 과거 데이터라 올해도 그렇다는 보장은 없어요.", w=2),
  S(f"크리스마스 주에 모인다면, 작년에 변화가 가장 작았던 광어를 중심에 두는 방법이 있습니다.", w=3),
  S(f"작년 크리스마스 주에 가장 많이 오른 건 농어였어요. 다만 올해 지금은 농어가 가장 싸니, 그 주 값을 보고 정하세요.", w=3),
  S("가기 전에는 매주 토요일 올라오는 노량진 주간 시세에서, 그 주 경락가를 확인하면 됩니다.", w=4)]),
 dict(id="check", kind="checklist", name="장보기 체크리스트", vis=dict(title="크리스마스·연말 회 장보기 5단계", rows=[("날짜", "가능하면 12월 초·중순"), ("인원", "인원 × 200g ÷ 수율"), ("생선", "그 주 값 보고 광어·참돔·농어 조합"),
                                                                                           ("시세", "토요일 주간 시세로 그 주 경락가"), ("당일", "모임 날 사서 바로 회로")]), sentences=[
  S("한 장으로 정리합니다. 크리스마스와 연말 회 장보기 다섯 단계예요.", cal=1),
  S("첫째, 날짜. 고를 수 있다면 십이월 초나 중순으로요.", row=0),
  S("둘째, 인원. 인원에 이백 그램을 곱하고 수율로 나눠 킬로그램을 정하세요.", row=1),
  S("셋째, 생선. 그 주 값을 보고 광어, 참돔, 농어를 섞으세요.", row=2),
  S("넷째, 시세. 토요일 주간 시세로 그 주 경락가를 확인하세요.", row=3),
  S("다섯째, 당일. 활어는 모임 날 사서 바로 회로 뜨세요.", row=4),
  S("이 화면은 캡처해 두셨다가, 장 보러 가기 전에 꺼내 보세요.", hold=1)]),
 dict(id="outro", kind="outro", name="마무리", vis=dict(disc=["경락가 = 도매 낙찰가 ≠ 가게 판매가", "작년 12월 = 과거 데이터 ≠ 올해 보장", "활어는 미리 사 두는 게 아님"],
                                                        take="아끼는 건 미리 사기가 아니라<br><span style='color:#F1D9A0'>날짜와 생선 조합</span>"), sentences=[
  S("다시 한 번 말씀드립니다.", disc=0),
  S("오늘 금액은 모두 노량진 도매 경락가로 계산한 값이고, 가게 판매가와 초장집 비용은 따로입니다.", disc=1),
  S("작년 십이월 숫자는 과거 데이터일 뿐, 올해도 똑같이 흘러간다는 보장은 없어요.", disc=2),
  S("제 생각에는, 크리스마스 회값을 아끼는 건 미리 사 두기가 아니라, 날짜와 생선 조합입니다.", opinion=1),
  S("인원별 필요한 킬로그램과 생선별 가성비는, 지난 연말 모임 회 장보기 편에 자세히 있어요.", cta=1),
  S("매주 토요일 노량진 주간 시세 재생목록도 같이 보시면, 모임 주의 값을 바로 확인할 수 있습니다.", cta=2),
  S("여러분은 크리스마스 모임 날짜, 정하셨나요? 댓글로 알려 주세요.", end=1)]),
]
DY = P["daily"]; dpr = lambda i, k: DY[i]["items"][k]["med"]; dq = lambda i, k: DY[i]["items"][k]["qty"]
Q25 = dq(3, "넙치(활)"); QMAX = max(d["items"]["넙치(활)"]["qty"] for d in DY)
COMBO = lambda w, parts: sum(kg * w[n] for n, kg in parts)
C10 = [("광어", 2.5), ("농어", 2.5)]; C6 = [("농어", 2), ("광어", 1)]
SUBFIX += [("이 점 오 킬로그램", "2.5kg"), ("육 점 칠 킬로그램", "6.7kg"), ("일 킬로그램", "1kg"), ("이십오일", "25일"), ("이십이일", "22일"), ("이십칠일", "27일"), ("크리스마스 당일", "크리스마스 당일"), ("삼십에서 사십 퍼센트", "30~40%"), ("사십에서 오십 퍼센트", "40~50%"), ("오백 그램", "500g"), ("영 점 사", "0.4")]
CALC = [dict(id="calc", kind="calc", name="계산법 다시 보기", vis=dict(cards=[
   dict(sig=["c", 1], kick="STEP 1 · 한 사람 회 양", photo="회", big="200g", lines=["여러 후기에서 1인당 200g"], top=200),
   dict(sig=["c", 2], kick="STEP 2 · 수율 (낮은 쪽 값)", lines=["광어 40% · 참돔 30% · 농어 40%", "<span style='color:#8C919B;font-size:34px'>자료 범위 광어 40~50% · 참돔 30~40% · 농어 40% 전후</span>"], size=54, top=240),
   dict(sig=["c", 3], kick="STEP 3 · 계산", big="인원 × 200g ÷ 수율", bigsize=96, lines=["광어 10명 = 활어 5kg · 참돔 10명 = 6.7kg"], top=260)]), sentences=[
  S("계산법을 짧게 다시 볼게요.", c=0),
  S("한 사람이 먹는 회 양은, 여러 후기에서 많이 잡는 이백 그램으로 했습니다.", c=1),
  S("수율은 활어 무게 중 회로 뜨는 살의 비율이에요. 모자라지 않게 자료 범위의 낮은 쪽 값을 썼습니다.", c=2),
  S("광어 사십 퍼센트, 참돔 삼십 퍼센트, 농어 사십 퍼센트예요.", c=2),
  S("인원에 이백 그램을 곱하고 수율로 나누면, 사야 할 활어 킬로그램이 나옵니다.", c=3),
  S("광어 열 명이면 오 킬로그램, 참돔은 수율이 낮아 열 명에 육 점 칠 킬로그램이에요.", c=3)])]
XDAY = [dict(id="xday", kind="faq", name="크리스마스 주 하루하루", vis=dict(cards=[
   dict(sig=["d", 1], kick="작년 크리스마스 주 · 광어(활) 하루 경락가", lines=[" · ".join(f"{d['date'][8:]}일({d['dow']}) {d['items']['넙치(활)']['med']:,}" for d in DY[:3]), " · ".join(f"{d['date'][8:]}일({d['dow']}) {d['items']['넙치(활)']['med']:,}" for d in DY[3:])], size=44, top=240),
   dict(sig=["d", 2], kick="12월 25일 크리스마스 당일", big=f"{Q25:,}kg", bigsize=120, lines=[f"그 주 광어 경매 물량이 가장 많았던 날 · kg당 {dpr(3, '넙치(활)'):,}원", "<span style='color:#8C919B;font-size:34px'>당일에도 새벽 경매가 열렸다 (작년)</span>"], top=220),
   dict(sig=["d", 3], kick="하루 차이보다", lines=["주 단위 흐름 · 생선 선택이 더 큼", "<span style='color:#8C919B;font-size:36px'>하루 값은 날마다 오르내림 · 한 해 데이터</span>"], size=52, top=260)]), sentences=[
  S("크리스마스 주 안에서는 어땠을까요? 작년 광어 하루하루 값을 봤어요.", d=0),
  S(f"이십이일 월요일은 {{e:{dpr(0, '넙치(활)')}}}, 이십오일 크리스마스 당일은 {{e:{dpr(3, '넙치(활)')}}}, 이십칠일 토요일은 {{e:{dpr(5, '넙치(활)')}}}이었습니다.", d=1),
  S(f"작년 크리스마스 당일에도 새벽 경매가 열렸고, 광어 물량은 {{kq:{Q25}}}으로 그 주에 가장 많았어요.", d=2),
  S("물량이 많은 날 값이 조금 낮았던 셈이지만, 하루 값은 날마다 오르내립니다.", d=2),
  S("크리스마스 주 안에서는 어느 요일이냐보다, 주 단위 흐름과 어떤 생선을 고르느냐가 예산을 더 크게 가릅니다.", d=3)])]
PICK = [dict(id="combo", kind="calc", name="조합 예산", vis=dict(cards=[
   dict(sig=["m", 1], kick="10명 · 광어 2.5kg + 농어 2.5kg", lines=[f"작년 첫 주 약 {r1000(COMBO(A, C10))}원 → 크리스마스 주 약 {r1000(COMBO(X, C10))}원", f"올해 지금 약 {r1000(COMBO(T, C10))}원"], size=50, top=240),
   dict(sig=["m", 2], kick="6명 · 농어 2kg + 광어 1kg", lines=[f"작년 첫 주 약 {r1000(COMBO(A, C6))}원 → 크리스마스 주 약 {r1000(COMBO(X, C6))}원", f"올해 지금 약 {r1000(COMBO(T, C6))}원"], size=50, top=240),
   dict(sig=["m", 3], kick="생선 비율만 바꿔도", lines=["값이 덜 오르는 생선 비중을 늘리면", "같은 날짜에도 예산이 달라짐"], size=54, top=260)]), sentences=[
  S("실제로는 한 생선만 사지 않죠. 지난 편의 조합 예로 계산해 볼게요.", m=0),
  S(f"열 명이 광어 이 점 오 킬로그램과 농어 이 점 오 킬로그램을 산다면, 작년엔 첫 주 약 {{p:{int(COMBO(A, C10))}}}, 크리스마스 주 약 {{p:{int(COMBO(X, C10))}}}이었어요.", m=1),
  S(f"올해 지금 값으로는 약 {{p:{int(COMBO(T, C10))}}}입니다.", m=1),
  S(f"여섯 명이 농어 이 킬로그램과 광어 일 킬로그램이면, 작년 첫 주 약 {{p:{int(COMBO(A, C6))}}}, 크리스마스 주 약 {{p:{int(COMBO(X, C6))}}}.", m=2),
  S(f"올해 지금 값으로는 약 {{p:{int(COMBO(T, C6))}}}이에요.", m=2),
  S("날짜를 못 바꾼다면, 그 주에 덜 오른 생선의 비중을 늘리는 것만으로도 예산이 달라집니다.", m=3)])]
FAQ = [dict(id="faq", kind="faq", name="자주 묻는 질문", vis=dict(cards=[
   dict(sig=["q", 1], kick="Q1 · 며칠 전에 미리 사 두면?", lines=["활어는 사 온 날 회로 먹는 게 기본", "<span style='color:#8C919B;font-size:36px'>'미리'는 날짜 계획 · 사 두기 아님</span>"], size=50, top=250),
   dict(sig=["q", 2], kick="Q2 · 지난 편과 작년 값이 다른 이유", lines=["지난 편: 주마다 월·화 이틀 표본", "이번: 월~토 모든 날짜", "<span style='color:#8C919B;font-size:34px'>같은 자료 · 묶은 날짜가 다름</span>"], size=50, top=230),
   dict(sig=["q", 3], kick="Q3 · 일요일엔?", lines=["일별 수집본에 일요일 경매 값 없음", "<span style='color:#8C919B;font-size:36px'>주간 비교는 월~토로 계산</span>"], size=50, top=250)]), sentences=[
  S("자주 받을 만한 질문 세 가지만 짚을게요.", q=0),
  S("첫 번째, 며칠 전에 미리 사서 두면 안 될까요?", q=1),
  S("활어는 사 온 날 회로 먹는 게 기본이에요. 오늘 말한 미리는, 사 두기가 아니라 날짜 계획입니다.", q=1),
  S("두 번째, 지난 편의 작년 값과 왜 다른가요?", q=2),
  S("지난 편은 주마다 월요일과 화요일 이틀만 뽑았고, 이번엔 월요일부터 토요일까지 모든 날짜를 넣었어요.", q=2),
  S("같은 자료지만 묶은 날짜가 달라서, 값도 조금 다르게 나왔습니다.", q=2),
  S("세 번째, 일요일에는요? 일별 수집본에는 일요일 경매 값이 없어서, 주간 비교는 월요일부터 토요일로 계산했어요.", q=3)])]

SECS = SECS[:2] + CALC + SECS[2:4] + XDAY + SECS[4:6] + PICK + SECS[6:7] + FAQ + SECS[7:]
D = dict(title="노량진수산시장 크리스마스·연말 회 장보기, 지금 사두면 얼마 아끼나", hdr="노량진수산시장 · 크리스마스·연말 회 장보기 · 도매 경락가 기준",
         src_label=f"자료 · 노량진수산(주) 어종별 경락시세(일별 수집본) · 올해 {TWO['week']} · 작년 2025.11.24~12.31", end_label="노량진 시세 · 장보기 데이터", hf_id="xmas_hoe", sections=SECS)
if __name__ != "short":
    json.dump(D, open(f"{HERE}/대본데이터.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ch = sum(len(x[0].replace(" ", "")) for s_ in SECS for x in s_["sentences"]); n = sum(len(s_["sentences"]) for s_ in SECS)
    print("글자", ch, "문장", n, "예상", round((ch / 6.8 + n * 0.45) / 60 * 753.9 / 720, 1), "분")
    print("'그' 시작:", [x[0][:20] for s_ in SECS for x in s_["sentences"] if x[0].startswith("그")])
