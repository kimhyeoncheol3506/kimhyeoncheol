"""33편 경제 지식 2시간 완전정리 — 3부 (금리와 환율). 8부로 나눠 만든 뒤 합친다.
사용: python3 projects/20261106-econ2h-p03/build.py plan | render [ids]
"""
import json
import os
import re
import subprocess
import sys

os.environ.setdefault("HF_LOOK", "sting")  # OPUSCAR 98 No.46 The Sting 룩
os.environ.setdefault("HF_BG", "scenery")  # v1.16.0 정보 패널 뒤 흐린 풍경 + 움직이는 메시 그라데이션
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
PJ = "projects/20261106-econ2h-p03"

sc = []
_chip = ""
_intro = None


def CH(no, title, chip, name=None):
    """챕터 시작: 다음 장면에 챕터 카드(2초)를 붙인다"""
    global _chip, _intro
    _chip = chip
    _intro = (no, title, name or re.sub(r"[\[\]{}|‹›]", "", title))


def N(t, s="", c="gold", icon="", **kw):
    return dict(t=t, s=s, c=c, icon=icon, **kw)


def S(text, kind, **p):
    S2(text, (None, kind, p))


def S2(text, *parts):
    """한 문장을 여러 그림으로 나눠 보여 줄 때: parts = (해당 구절, kind, params) ... 구절 길이 비율로 시간 배분"""
    global _intro
    n = len(sc) + 1
    d = {"id": f"s{n:03d}", "text": text, "parts": []}
    for seg, kind, p in parts:
        p = dict(p)
        p.setdefault("chip", _chip)
        d["parts"].append({"seg": seg or text, "kind": kind, "p": p})
    if _intro:
        d["parts"][0]["p"]["intro"] = [_intro[0], _intro[1]]
        d["chapter"] = _intro[2]
        _intro = None
    sc.append(d)


def Q(text, *lines, **kw):
    S(text, "quote", lines=list(lines), **kw)


EX = "개념도 · 실제 수치 아님"

# ═════════════ 3강 금리와 환율 ═════════════
CH("3강", "금리와 환율, [밀고 당기는] 돈의 힘", "3강 · 금리와 환율 — 밀고 당기는 돈의 힘", name="3강 금리와 환율 — 밀고 당기는 돈의 힘")
S("세 번째 이야기는 금리와 환율입니다. 경제 공부를 시작하면 가장 먼저 만나는 두 단어이자, 가장 많이 포기하게 만드는 두 단어죠.", "compare", headline="경제 공부의 [첫 번째 산]",
  left=dict(title="금리", c="red", rows=["돈을 빌리는 값"]), right=dict(title="환율", c="blue", rows=["나라 돈끼리 바꾸는 값"]))
S("오늘은 딱 한 문장만 기억하시면 됩니다. 금리와 환율은 둘 다 교환 비율이다.", "quote", lines=["금리와 환율은 둘 다", "[교환 비율]이다"], size=130)
S("금리는 지금의 돈과 미래의 돈을 바꾸는 비율이고, 환율은 우리나라 돈과 외국 돈을 바꾸는 비율입니다.", "compare", headline="둘 다 [교환 비율]",
  left=dict(title="금리", c="red", rows=["지금의 돈 ↔ 미래의 돈"]), right=dict(title="환율", c="blue", rows=["원화 ↔ 외국 돈"]))
S("금리부터 볼게요. 지금 100만 원과 1년 뒤 100만 원, 어느 쪽이 더 좋으세요?", "qa", q="지금 100만 원 vs\n1년 뒤 100만 원")
S("당연히 지금이죠. 지금 있으면 당장 쓸 수도 있고, 그사이 물가가 오를 수도 있고, 1년 뒤에 못 받을 위험도 있으니까요.", "check", headline="지금의 돈이 [더 비싼] 이유",
  items=[dict(t="지금 [바로 쓸 수] 있다", c="gold"), dict(t="그사이 [물가]가 오를 수 있다", c="blue"), dict(t="나중에 [못 받을] 위험이 있다", c="red")])
S("그러니 누군가 지금 내 돈을 빌려 간다면, 1년 뒤에 웃돈을 얹어서 돌려받아야 공평하겠죠. 그 웃돈의 비율이 바로 금리입니다.", "flow", headline="금리 = 기다림의 [웃돈]", badge="계산 예시",
  nodes=[dict(t="지금 100만 원", s="빌려줌", c="gold", icon="1"), dict(t="1년 기다림", s="", c="blue", icon="2"), dict(t="1년 뒤 105만 원", s="금리 5%", c="red", icon="3")])
S("지금의 100만 원이 1년 뒤 105만 원과 같은 값이라면, 금리는 5%인 거죠. 금리는 결국 시간의 가격입니다.", "kpi", kicker="한 줄 정의", big="금리 = 시간의 가격", color="red", unit="기다려 준 대가", size=190)
S("여기서 꼭 구분해야 할 게 있습니다. 통장에 찍히는 금리와, 진짜로 내 돈이 불어나는 금리는 다릅니다.", "quote", lines=["통장에 찍히는 금리와", "[진짜] 금리는 다르다"], size=120)
S("통장에 찍히는 금리를 명목금리, 여기서 물가 상승률을 뺀 걸 실질금리라고 합니다.", "flow", headline="[실질금리] = 명목금리 − 물가 상승률", badge="계산 예시",
  nodes=[dict(t="예금 금리 3%", s="명목금리", c="gold", icon="1"), dict(t="− 물가 3%", s="", c="blue", icon="−"), dict(t="실질금리 0%", s="사실상 제자리", c="red", icon="=")])
S("예금 이자가 3%인데 물가가 3% 올랐다면, 숫자는 늘었지만 살 수 있는 물건의 양은 그대로입니다. 실질금리 0%죠.", "story", scene="saving_32")
S("물가가 4% 오르는데 이자가 3%라면 실질금리는 마이너스 1%. 저축하면서도 조금씩 가난해지는 겁니다. 첫 번째 이야기와 똑같죠.", "kpi", kicker="물가 4%, 예금 3%라면", big="실질금리 −1%", color="blue", unit="저축하면서도 조금씩 가난해진다", size=200)
S("이 시간의 가격을 정하는 데 가장 큰 영향을 주는 게 중앙은행, 우리나라는 한국은행입니다. 한국은행이 정하는 금리가 기준금리예요.", "kpi", kicker="한국은행 금융통화위원회가 결정", big="기준금리", color="gold", unit="모든 금리의 출발점", size=240)
S("한국은행은 1년에 여덟 번 회의를 열어 기준금리를 올릴지, 내릴지, 그대로 둘지 결정합니다.", "story", scene="news_tv", relabel={">시총 −660조<": ">기준금리 결정<"})
S("기준금리가 움직이면 은행의 예금 금리, 대출 금리, 채권 금리가 줄줄이 따라 움직입니다. 물결이 퍼지듯이요.", "flow", headline="기준금리의 [물결]",
  nodes=[dict(t="기준금리", s="한국은행", c="gold", icon="1"), dict(t="시장 금리", s="채권·은행 간 금리", c="blue", icon="2"), dict(t="예금·대출 금리", s="내 통장", c="red", icon="3")])
S("그런데 내가 은행에서 받는 대출 금리는 기준금리보다 훨씬 높죠. 은행이 자기 몫을 얹기 때문입니다.", "flow", headline="내 대출 금리의 [구조]",
  nodes=[dict(t="기준 금리", s="시장의 출발점", c="gold", icon="1"), dict(t="+ 가산금리", s="은행 몫·내 신용도", c="blue", icon="+"), dict(t="= 내 대출 금리", s="", c="red", icon="=")])
S("가산금리는 내 신용 점수, 소득, 담보에 따라 달라집니다. 같은 날 같은 은행에서 빌려도 사람마다 금리가 다른 이유죠.", "kpi", kicker="사람마다 다른 이유", big="가산금리", color="blue", unit="신용·소득·담보에 따라 달라진다", size=230)
S("그리고 대출에는 변동금리와 고정금리가 있습니다. 변동금리는 시장 금리를 따라 바뀌고, 고정금리는 정해진 기간 동안 그대로죠. 이건 다섯 번째 이야기에서 더 자세히 할게요.", "compare", headline="[변동금리] vs [고정금리]",
  left=dict(title="변동금리", c="blue", rows=["시장 따라 바뀜", "금리 내릴 땐 유리"]), right=dict(title="고정금리", c="red", rows=["정해진 기간 고정", "금리 오를 땐 유리"]))
S("그럼 한국은행은 왜 금리를 올리고 내릴까요? 경제의 온도를 조절하기 위해서입니다.", "qa", q="왜 금리를\n[올리고 내릴까?]")
S("경기가 너무 뜨거워 물가가 치솟으면 금리를 올려서 식히고, 경기가 너무 차가우면 금리를 내려서 데웁니다.", "compare", headline="금리는 경제의 [온도 조절기]",
  left=dict(title="너무 뜨거울 때", c="red", rows=["물가 급등", "→ 금리 인상"]), right=dict(title="너무 차가울 때", c="blue", rows=["경기 침체", "→ 금리 인하"]))
S("금리가 오르면 대출 이자가 비싸지니까 사람들이 돈을 덜 빌리고 덜 씁니다. 대신 예금 이자가 높아지니까 저축은 늘죠.", "flow", headline="금리가 [오르면]",
  nodes=[dict(t="대출 이자 ↑", s="", c="red", icon="1"), dict(t="빌리기·쓰기 ↓", s="", c="gold", icon="2"), dict(t="물가 진정", s="경기 식음", c="blue", icon="3")])
S("첫 번째 이야기에서 돈은 대출에서 태어난다고 했죠. 금리가 오르면 대출이 줄고, 돈이 늘어나는 속도도 느려집니다. 다 연결돼 있어요.", "story", scene="debt_bill")
S("반대로 금리가 내리면 빌리기 쉬워지고, 돈이 돌고, 자산 가격이 오르기 쉬워집니다. 2020년에 우리가 본 장면이죠.", "flow", headline="금리가 [내리면]",
  nodes=[dict(t="대출 이자 ↓", s="", c="blue", icon="1"), dict(t="빌리기·쓰기 ↑", s="", c="gold", icon="2"), dict(t="자산 가격 ↑", s="경기 데워짐", c="red", icon="3")])
S("그래서 금리를 알면 경기가 보인다는 말이 있습니다. 금리가 오르는 시기와 내리는 시기에는 돈의 흐름이 완전히 달라지거든요.", "quote", lines=["금리를 알면", "[경기]가 보인다"], size=140)
S("여기서 투자자에게 정말 중요한 공식 하나를 알려 드릴게요. 금리와 자산 가격은 시소처럼 반대로 움직이는 경향이 있습니다.", "scale", headline="금리와 자산 가격은 [시소]",
  left=dict(t="금리", s="오르면", c="red"), right=dict(t="자산 가격", s="내려가기 쉽다", c="blue"), tilt=12)
S("왜 그럴까요? 예금 이자가 5%나 나오면, 굳이 위험한 주식이나 집에 돈을 넣을 이유가 줄어들잖아요.", "compare", headline="안전한 곳이 [5%]를 준다면",
  left=dict(title="예금", c="gold", rows=["연 5% · 안전"]), right=dict(title="주식·집", c="blue", rows=["위험한데 굳이?", "수요 감소 → 가격 하락"]))
S("반대로 예금 이자가 1%밖에 안 되면, 사람들은 조금이라도 더 벌려고 위험한 자산으로 몰려갑니다.", "story", scene="chase_buy")
S("이 시소가 가장 직접적으로 보이는 곳이 채권입니다. 채권 가격과 금리는 정확히 반대로 움직이거든요.", "kpi", kicker="가장 정확한 시소", big="채권 가격 ↔ 금리", color="blue", unit="금리가 오르면 이미 가진 채권 가격은 내린다", size=170)
S("예를 들어 볼게요. 제가 이자를 3% 주는 채권을 갖고 있는데, 갑자기 시장 금리가 5%로 올랐습니다.", "flow", headline="3% 채권을 가졌는데 [금리가 5%]로", badge="계산 예시",
  nodes=[dict(t="내 채권", s="이자 3%", c="gold", icon="1"), dict(t="새 채권", s="이자 5%", c="red", icon="2"), dict(t="누가 내 걸 사지?", s="", c="blue", icon="?")])
S("누가 3%짜리를 사려고 할까요? 5%짜리가 나왔는데요. 그래서 제 채권은 가격을 깎아서 팔아야 합니다. 금리가 오르면 채권 가격이 떨어지는 이유죠.", "chart", headline="금리 ↑ → [채권 가격 ↓]", badge=EX,
  lines=[dict(name="시장 금리", color="red", pts=[.3, .35, .45, .58, .7], end="상승"), dict(name="기존 채권 가격", color="blue", pts=[.7, .65, .55, .42, .3], end="하락")])
S("반대로 금리가 내려갈 때는 높은 이자를 주는 옛날 채권이 귀해지니까 가격이 오르고요. 그래서 금리가 내릴 것 같을 때 채권 투자가 인기를 끕니다.", "kpi", kicker="채권 투자의 원리", big="금리 ↓ 기대 → 채권 ↑", color="red", unit="이자 + 가격 상승을 함께 노림", size=160)
S("금리에서 하나만 더 보겠습니다. 경기의 신호등이라고 불리는 장단기 금리차입니다.", "kpi", kicker="경기의 신호등", big="장단기 금리차", color="gold", unit="10년 금리 − 2년(또는 3년) 금리", size=210)
S("보통은 오래 빌려줄수록 이자를 더 받습니다. 10년 동안 묶이는 돈이 2년 동안 묶이는 돈보다 위험하니까요.", "chart", headline="보통은 [오래 빌려줄수록] 높은 금리", badge=EX,
  lines=[dict(name="정상 금리 곡선", color="gold", pts=[.25, .4, .5, .57, .62], end="10년")], marks=[dict(x=.0, text="1년", color="blue"), dict(x=.95, text="10년", color="red")])
S("그런데 가끔 이게 뒤집힐 때가 있습니다. 짧게 빌려주는 금리가 길게 빌려주는 금리보다 높아지는 거죠. 이걸 금리 역전이라고 합니다.", "chart", headline="뒤집힌 곡선 · [금리 역전]", badge=EX,
  lines=[dict(name="역전된 금리 곡선", color="blue", pts=[.62, .58, .52, .48, .45], end="10년")])
S("시장이 앞으로 경기가 나빠져 금리가 내려갈 거라고 예상하면 이런 일이 생깁니다. 그래서 미국에서는 금리 역전이 경기 침체의 대표적인 예고 신호로 여겨져 왔어요.", "story", scene="calendar_flip", relabel={">12월<": ">역전<", ">31<": ">!<", ">1월<": ">침체?<", ">2<": ">?<"})
S("물론 신호일 뿐 정답은 아닙니다. 역전된 뒤 침체가 늦게 오거나 오지 않은 때도 있었으니까요. 하지만 뉴스에서 금리 역전이라는 말이 나오면 귀를 기울일 이유는 충분합니다.", "quote", lines=["신호일 뿐 정답은 아니다", "하지만 [귀 기울일] 이유는 충분"], size=110)
S("그런데 우리나라 금리만 봐서는 반쪽짜리입니다. 세계의 금리를 움직이는 진짜 주인공이 있거든요. 미국 중앙은행, 연준입니다.", "kpi", kicker="세계 금리의 기준점", big="미국 연준 (Fed)", color="red", unit="달러를 찍는 곳", size=200)
S("달러는 세계에서 가장 많이 쓰이는 돈, 기축통화입니다. 석유도, 반도체도, 대부분 달러로 사고팔죠. 그래서 연준이 금리를 움직이면 전 세계 돈의 흐름이 같이 흔들립니다.", "story", scene="two_giants", relabel={">삼성전자<": ">달러<", ">SK하이닉스<": ">연준<"})
S("2022년에서 2023년 사이, 연준은 0% 근처였던 금리를 5%대 중반까지 빠르게 올렸습니다. 40여 년 만에 가장 빠른 속도였어요.", "chart", headline="미국 기준금리, [0% → 5%대]", badge=EX,
  lines=[dict(name="미국 기준금리", color="red", pts=[.1, .1, .2, .4, .6, .72, .74], end="5%대")], marks=[dict(x=.2, text="2022년 인상 시작", color="red")])
S("그때 우리나라 금리는 미국보다 낮아졌고, 한때 그 차이가 2%포인트까지 벌어졌습니다. 역대 가장 큰 차이였죠.", "compare", headline="한미 금리 [역전]",
  left=dict(title="미국", c="red", rows=["5%대"]), right=dict(title="한국", c="blue", rows=["3%대", "차이 최대 2%p"]))
S("이렇게 미국 금리가 높아지면 무슨 일이 생길까요? 그 답이 바로 환율입니다.", "quote", lines=["미국 금리가 높아지면", "[환율]이 움직인다"], size=130)
S("자, 이제 환율로 넘어가 볼게요. 환율은 우리나라 돈과 외국 돈을 바꾸는 비율입니다.", "kpi", kicker="두 번째 교환 비율", big="환율", color="blue", unit="원화 ↔ 외국 돈", size=260)
S("원 달러 환율이 1,400원이라는 건, 1달러를 사려면 1,400원을 내야 한다는 뜻이죠.", "flow", headline="원·달러 환율 1,400원이란", badge="예시",
  nodes=[dict(t="1,400원", s="", c="gold", icon="₩"), dict(t="↔", s="바꾼다", c="blue", icon="="), dict(t="1달러", s="", c="red", icon="$")])
S("여기서 많이 헷갈리는 게 있습니다. 환율이 오르면 원화가 강해진 걸까요, 약해진 걸까요?", "qa", q="환율이 오르면\n원화는 [강해진 걸까?]")
S("약해진 겁니다. 1,300원이면 사던 1달러를 이제 1,400원을 내야 사니까, 원화의 힘이 빠진 거죠. 환율 상승은 원화 약세입니다.", "compare", headline="환율 상승 = [원화 약세]",
  left=dict(title="1,300원 → 1,400원", c="red", rows=["환율 상승"]), right=dict(title="같은 1달러에 더 냄", c="blue", rows=["원화 약세"]))
S("그럼 환율은 무엇이 움직일까요? 크게 세 가지 힘이 있습니다. 금리 차이, 무역, 그리고 불안감.", "check", headline="환율을 움직이는 [세 가지 힘]",
  items=[dict(t="[금리 차이] — 돈은 이자 높은 곳으로", c="red", no="1"), dict(t="[무역] — 수출로 번 달러, 수입에 쓰는 달러", c="gold", no="2"), dict(t="[불안감] — 위기 때는 달러로", c="blue", no="3")])
S("첫째, 금리 차이입니다. 돈은 이자를 더 주는 곳으로 흘러갑니다. 미국 금리가 한국보다 많이 높으면, 돈이 달러로 옮겨 가면서 달러 값이 오르기 쉽죠.", "flow", headline="힘 1 · 돈은 [이자가 높은 곳]으로",
  nodes=[dict(t="미국 금리 > 한국 금리", s="", c="red", icon="1"), dict(t="돈이 달러로 이동", s="", c="gold", icon="2"), dict(t="원·달러 환율 ↑", s="원화 약세", c="blue", icon="3")])
S("둘째, 무역입니다. 우리 기업이 수출을 많이 해서 달러를 많이 벌어 오면, 그 달러를 원화로 바꾸면서 원화 값이 오릅니다.", "flow", headline="힘 2 · [수출]로 번 달러",
  nodes=[dict(t="수출 증가", s="달러 유입", c="red", icon="1"), dict(t="달러 → 원화 교환", s="", c="gold", icon="2"), dict(t="환율 ↓", s="원화 강세", c="blue", icon="3")])
S("셋째, 불안감입니다. 세계 경제가 흔들리면 사람들은 가장 믿을 만한 돈, 달러로 몰립니다. 그래서 위기 때마다 원 달러 환율이 치솟곤 하죠.", "story", scene="vault")
S("1997년 외환위기 때는 1달러에 800원대이던 환율이 두 달도 안 돼 2천 원 가까이까지 뛰었습니다. 이 이야기는 여섯 번째 이야기에서 자세히 할게요.", "chart", headline="1997년, 환율이 [두 배 넘게]", badge=EX,
  lines=[dict(name="원·달러 환율", color="red", pts=[.25, .26, .27, .3, .55, .9, .7], end="2천 원 가까이")], marks=[dict(x=.6, text="1997년 말", color="red")])
S("위기 때를 대비해 나라가 쌓아 두는 달러도 있습니다. 외환보유액이죠. 우리나라는 4천억 달러 안팎을 갖고 있습니다.", "kpi", kicker="나라의 비상금", big="외환보유액", color="gold", unit="우리나라 약 4천억 달러 안팎", size=220)
S("1997년에는 이 비상금이 바닥나서 위기를 맞았습니다. 그 뒤로 우리나라는 비상금을 넉넉히 쌓아 두는 나라가 됐어요.", "chart", headline="1997년 이후 [쌓아 온] 비상금", badge=EX,
  lines=[dict(name="외환보유액", color="gold", pts=[.05, .2, .32, .45, .6, .7, .72, .74], end="약 4천억 달러")], marks=[dict(x=.0, text="1997 바닥", color="blue")])
S("환율이 적정한지 재미있게 보는 방법도 하나 알려 드릴게요. 햄버거 가격으로 보는 빅맥 지수입니다.", "kpi", kicker="이코노미스트가 만든 지표", big="빅맥 지수", color="red", unit="같은 햄버거, 나라마다 얼마?", size=230)
S("같은 햄버거라면 어느 나라에서든 비슷한 값이어야 한다는 생각에서 출발합니다. 이걸 구매력 평가라고 해요.", "story", scene="memory_store", relabel={">가격 ↑↑<": ">햄버거 값<"})
S("미국에서 5달러인 햄버거가 한국에서 5천 원이라면, 햄버거로 본 적정 환율은 1달러에 천 원입니다. 실제 환율이 1,400원이라면 원화가 햄버거 기준으로는 싸게 평가된 거죠.", "flow", headline="햄버거로 본 [적정 환율]", badge="계산 예시",
  nodes=[dict(t="미국 5달러", s="", c="red", icon="$"), dict(t="한국 5천 원", s="", c="gold", icon="₩"), dict(t="적정 환율 1천 원", s="실제 1,400원이면 원화 저평가", c="blue", icon="=")])
S("물론 햄버거 하나로 환율을 맞힐 수는 없습니다. 하지만 환율이 길게 보면 물가 수준을 따라가려 한다는 감을 잡는 데는 꽤 쓸모가 있어요.", "quote", lines=["환율은 길게 보면", "[물가 수준]을 따라가려 한다"], size=110)
S("환율이 오르고 내리는 건 누구에게 좋고, 누구에게 나쁠까요? 정답은 입장에 따라 다르다는 겁니다.", "qa", q="환율이 오르면\n[누가 웃고 누가 울까?]")
S("환율이 오르면 수출 기업은 웃습니다. 같은 1달러어치를 팔아도 원화로 바꾸면 더 많은 돈이 들어오니까요.", "compare", headline="환율 상승의 [희비]",
  left=dict(title="웃는 쪽", c="red", rows=["수출 기업", "해외 자산을 가진 사람"]), right=dict(title="우는 쪽", c="blue", rows=["수입 기업·소비자", "해외여행·유학"]))
S("반대로 수입하는 기업과 소비자는 웁니다. 수입하는 기름, 밀가루, 원자재 값이 원화로 비싸지니까요. 그래서 환율이 오르면 물가도 따라 오르기 쉽습니다.", "flow", headline="환율 ↑ → [수입 물가 ↑]",
  nodes=[dict(t="환율 상승", s="", c="red", icon="1"), dict(t="수입품 원화 가격 ↑", s="기름·곡물·원자재", c="gold", icon="2"), dict(t="물가 상승", s="", c="blue", icon="3")])
S("해외 주식에 투자하는 분이라면 환율이 수익률에 직접 들어옵니다. 미국 주식이 10% 올라도 환율이 10% 떨어지면 원화로는 제자리일 수 있죠.", "dual", headline="해외 주식 = 주가 × [환율]", badge="계산 예시",
  panels=[dict(title="달러 기준", color="red", pts=[.4, .65], tag="+10%", note="미국 주가"), dict(title="원화 기준", color="gold", pts=[.4, .4], tag="약 0%", note="환율이 10% 하락했다면")])
S("반대로 주가가 그대로여도 환율이 오르면 원화로는 돈을 번 셈이 되고요. 이걸 환차익, 반대는 환차손이라고 합니다.", "compare", headline="[환차익]과 [환차손]",
  left=dict(title="환차익", c="red", rows=["환율 상승", "원화로 더 많이"]), right=dict(title="환차손", c="blue", rows=["환율 하락", "원화로 더 적게"]))
S("그럼 환율은 예측할 수 있을까요? 솔직히 말씀드리면, 아주 어렵습니다. 전문가들의 환율 전망도 자주 빗나가요.", "quote", lines=["환율 예측은", "[전문가도] 자주 틀린다"], size=130)
S("금리, 무역, 정치, 전쟁, 사람들의 심리까지 수많은 변수가 동시에 움직이니까요. 그래서 환율은 맞히는 게 아니라 대비하는 겁니다.", "quote", lines=["환율은 맞히는 게 아니라", "[대비하는] 것"], size=130)
S("대비하는 방법은 두 번째 이야기의 분산과 똑같습니다. 원화 자산과 달러 자산을 섞어 두는 거죠.", "kpi", kicker="환율 대비법", big="통화 분산", color="gold", unit="원화 자산 + 달러 자산", size=230)
S("위기가 오면 원화 자산은 떨어지는데 환율이 올라서 달러 자산이 그 손실을 받쳐 주는 경우가 많았습니다. 자연스러운 보험이 되는 셈이죠.", "dual", headline="위기 때 [달러 자산]이 받쳐 준 경향", badge=EX,
  panels=[dict(title="원화 자산", color="blue", pts=[.65, .35], tag="하락", note="위기 때"), dict(title="달러 자산 (원화 환산)", color="red", pts=[.45, .6], tag="상승", note="환율 상승 효과")])
S("달러를 한 번에 왕창 사기보다는, 두 번째 이야기에서 말씀드린 것처럼 시간을 나눠 조금씩 모으는 게 마음 편합니다.", "story", scene="calendar_flip", relabel={">12월<": ">매달<", ">31<": ">$<", ">1월<": ">매달<", ">2<": ">$<"})
S("환율은 우리 주식 시장에도 큰 영향을 줍니다. 외국인 투자자 입장에서 생각해 보면 쉬워요.", "qa", q="외국인 투자자는\n[환율]을 왜 볼까?")
S("외국인은 달러를 원화로 바꿔서 한국 주식을 삽니다. 그런데 주식이 그대로여도 환율이 오르면, 다시 달러로 바꿀 때 손해를 보죠.", "flow", headline="외국인의 [환율 계산]",
  nodes=[dict(t="달러 → 원화", s="한국 주식 매수", c="gold", icon="1"), dict(t="환율 상승", s="원화 약세", c="blue", icon="2"), dict(t="원화 → 달러", s="환차손", c="red", icon="3")])
S("그래서 환율이 빠르게 오를 때는 외국인이 한국 주식을 파는 경우가 많고, 그게 다시 환율을 올리는 악순환이 생기기도 합니다.", "chart", headline="환율 ↑ ⇄ [외국인 매도]", badge=EX,
  lines=[dict(name="원·달러 환율", color="red", pts=[.3, .35, .45, .58, .66], end=""), dict(name="외국인 보유 주식", color="blue", pts=[.7, .66, .58, .48, .42], end="")])
S("마지막으로 금리와 환율이 어떻게 엮여 있는지 정리해 볼게요. 우리나라 금리가 미국보다 많이 낮으면 어떻게 될까요?", "qa", q="한국 금리가 미국보다\n[많이 낮으면?]")
S("돈이 더 높은 이자를 찾아 빠져나가면서 환율이 오를 수 있습니다. 그러면 수입 물가가 올라 물가를 자극하죠.", "flow", headline="금리와 환율의 [연결 고리]",
  nodes=[dict(t="한국 금리 < 미국 금리", s="", c="blue", icon="1"), dict(t="돈 유출 → 환율 ↑", s="", c="gold", icon="2"), dict(t="수입 물가 ↑", s="", c="red", icon="3")])
S("그래서 한국은행은 경기만 보고 금리를 마음대로 내릴 수가 없습니다. 미국 금리와 환율을 같이 봐야 하죠. 작은 나라 중앙은행의 숙명 같은 겁니다.", "scale", headline="한국은행의 [줄타기]",
  left=dict(t="경기 살리기", s="금리 인하 원함", c="blue"), right=dict(t="환율·물가", s="금리 인하 부담", c="red"), tilt=0)
S("이제 뉴스를 이렇게 읽으시면 됩니다. 미국이 금리를 올린다, 그럼 달러가 강해지고 환율이 오르겠구나. 우리 수입 물가도 오르겠구나.", "story", scene="lightbulb", relabel={">외국인 순매도<": ">미국 금리 ↑<", ">PER · 시가총액<": ">환율 ↑ 물가 ↑<"})
S("조금 더 깊이 가 볼게요. 금리가 주식 가격에 영향을 주는 진짜 이유는 할인율이라는 개념에 있습니다.", "kpi", kicker="더 깊이 ③", big="할인율", color="gold", unit="미래의 돈을 오늘 가치로 바꾸는 비율", size=240)
S("1년 뒤에 110만 원을 받을 수 있는 권리가 있다고 해 볼게요. 금리가 10%라면 이 권리의 오늘 가치는 100만 원입니다. 지금 100만 원을 예금하면 1년 뒤 110만 원이 되니까요.", "flow", headline="미래의 돈을 [오늘 가치]로", badge="계산 예시",
  nodes=[dict(t="1년 뒤 110만 원", s="", c="gold", icon="1"), dict(t="÷ 1.1", s="금리 10%", c="blue", icon="÷"), dict(t="오늘 가치 100만 원", s="", c="red", icon="=")])
S("주식은 결국 그 회사가 앞으로 벌어들일 돈에 대한 권리입니다. 금리가 오르면 그 미래의 돈을 더 크게 깎아서 오늘 가치를 계산하니까, 주가가 내려가는 거죠.", "scale", headline="금리 ↑ = 미래 이익을 [더 크게 깎는다]",
  left=dict(t="금리", s="오르면", c="red"), right=dict(t="미래 이익의 오늘 가치", s="줄어든다", c="blue"), tilt=12)
S("특히 지금은 돈을 못 벌고 먼 미래에 크게 벌 거라는 성장 기업일수록, 금리에 훨씬 민감하게 움직입니다. 먼 미래의 돈일수록 더 많이 깎이니까요.", "dual", headline="먼 미래의 이익일수록 [금리에 민감]", badge=EX,
  panels=[dict(title="지금 버는 회사", color="gold", pts=[.6, .52], tag="덜 흔들림", note="금리 인상 때"), dict(title="먼 미래에 벌 회사", color="blue", pts=[.6, .25], tag="크게 흔들림", note="금리 인상 때")])
S("환율도 하나만 더 볼게요. 2024년 엔화는 1달러에 160엔을 넘으며 30여 년 만에 가장 약해졌습니다. 일본 금리가 0 근처에 머무는 동안 미국 금리가 크게 올랐기 때문이죠.", "compare", headline="2024년 엔화, [30여 년 만의 약세]",
  left=dict(title="일본 금리", c="blue", rows=["0% 근처"]), right=dict(title="미국 금리", c="red", rows=["5%대", "돈이 달러로"]))
S("금리 차이가 환율을 움직인다는 세 번째 이야기의 공식이 그대로 나타난 사례입니다. 그래서 엔화가 싸다고 무작정 사기보다, 금리 차이가 언제 좁혀질지를 함께 봐야 하죠.", "story", scene="haggle")
S("금리 이야기를 실전으로 가져와 볼게요. 금리가 움직이는 시기에 따라 유리한 자산이 달라집니다.", "check", headline="금리 시기별 [유리한 자산] (경향)",
  items=[dict(t="금리가 [오르는] 시기 — 예금·짧은 채권", c="blue", no="1"), dict(t="금리가 [높게 머무는] 시기 — 채권 이자 확보", c="gold", no="2"), dict(t="금리가 [내리는] 시기 — 긴 채권·주식·부동산", c="red", no="3")])
S("물론 경향일 뿐 공식은 아닙니다. 하지만 지금이 어느 시기인지 알고 있으면 적어도 거꾸로 움직이는 실수는 줄일 수 있죠.", "story", scene="calendar_flip", relabel={">12월<": ">인상기<", ">31<": ">↑<", ">1월<": ">인하기<", ">2<": ">↓<"})
S("채권에 투자할 때는 누구에게 빌려주느냐도 중요합니다. 나라가 발행하면 국채, 회사가 발행하면 회사채죠. 회사채는 그 회사가 돈을 갚을 수 있는지에 따라 신용등급이 매겨집니다.", "compare", headline="[국채] vs [회사채]",
  left=dict(title="국채", c="blue", rows=["나라가 빌림", "가장 안전한 편, 이자 낮음"]), right=dict(title="회사채", c="red", rows=["회사가 빌림", "신용등급 따라 이자 다름"]))
S("등급이 낮을수록 이자를 더 주지만, 그만큼 돈을 못 받을 위험도 큽니다. 두 번째 이야기의 위험 프리미엄이 여기서도 똑같이 적용되죠. 너무 높은 이자는 늘 의심해 보셔야 합니다.", "chart", headline="신용이 낮을수록 [이자는 높다]", badge=EX,
  lines=[dict(name="채권 이자", color="red", pts=[.2, .26, .33, .45, .65], end="")], marks=[dict(x=.0, text="국채", color="blue"), dict(x=.9, text="낮은 등급", color="red")])
S("환율 이야기도 생활로 가져와 볼게요. 해외여행이나 유학처럼 달러가 필요한 일이 미리 정해져 있다면, 한 번에 다 바꾸지 말고 몇 달에 걸쳐 나눠 바꾸는 것만으로도 환율 위험을 꽤 줄일 수 있습니다.", "flow", headline="생활 속 [환율 대비]",
  nodes=[dict(t="달러 쓸 일 확정", s="여행·유학", c="gold", icon="1"), dict(t="몇 달에 나눠 환전", s="", c="blue", icon="2"), dict(t="평균 환율로 위험 분산", s="", c="red", icon="3")])
S("자주 받는 질문 두 가지. 첫째, 금리가 오르면 무조건 집값이 떨어지나요? 꼭 그렇지는 않습니다.", "qa", q="금리가 오르면\n[무조건] 집값이 떨어지나?")
S("금리는 집값을 누르는 힘이지만, 공급이 부족하거나 소득이 크게 늘거나 돈이 너무 많이 풀려 있으면 그 힘을 이기기도 합니다. 금리는 여러 힘 가운데 하나예요.", "scale", headline="금리는 [여러 힘 중 하나]",
  left=dict(t="금리 인상", s="집값을 누름", c="blue"), right=dict(t="공급 부족·소득·유동성", s="집값을 올림", c="red"), tilt=-6)
S("둘째, 환율이 1,500원을 넘으면 위기인가요? 숫자 자체보다 속도와 이유가 중요합니다.", "qa", q="환율 1,500원이면\n[위기]인가?")
S("천천히 오르는 건 경제가 적응할 시간이 있지만, 몇 주 만에 확 뛰면 기업과 금융 시장이 감당하기 어렵습니다. 그리고 왜 오르는지, 우리 문제인지 미국 문제인지도 봐야 하죠.", "check", headline="환율을 볼 때 [세 가지]",
  items=[dict(t="[수준] — 몇 원인가", c="gold"), dict(t="[속도] — 얼마나 빨리 움직이나", c="red"), dict(t="[이유] — 우리 문제인가, 달러 문제인가", c="blue")])
S("금리가 얼마나 강력한 도구인지 보여 주는 역사 속 장면이 있습니다. 1970년대 말 미국입니다.", "kpi", kicker="1970년대 말 미국", big="물가와의 전쟁", color="red", unit="두 자릿수 물가 상승률", size=230)
S("그 시절 미국은 석유 파동이 겹치면서 물가가 해마다 10% 넘게 올랐습니다. 사람들은 물가가 계속 오를 거라고 믿었고, 그 믿음이 다시 물가를 밀어 올렸죠.", "chart", headline="1970년대 미국의 [물가]", badge=EX,
  lines=[dict(name="물가 상승률", color="red", pts=[.2, .3, .45, .4, .55, .7, .8], end="10%대")])
S("1979년 연준 의장이 된 폴 볼커는 충격적인 결정을 내립니다. 기준금리를 20% 가까이까지 끌어올린 거예요.", "kpi", kicker="1979년 연준 의장 폴 볼커", big="금리 20% 가까이", color="red", unit="물가를 잡기 위한 충격 요법", size=210)
S("대출 이자가 치솟자 집과 차가 팔리지 않았고, 공장이 멈추고, 실업자가 크게 늘었습니다. 농민들은 트랙터를 몰고 와서 연준 건물을 에워싸며 항의했다고 하죠.", "story", scene="party_outside")
S("그래도 볼커는 물러서지 않았습니다. 그리고 몇 년 뒤, 물가는 정말로 잡혔고 미국 경제는 그 뒤로 오랫동안 안정적인 성장을 누렸습니다.", "chart", headline="볼커 이후 [잡힌 물가]", badge=EX,
  lines=[dict(name="기준금리", color="red", pts=[.4, .7, .9, .75, .55, .45, .4], end=""), dict(name="물가 상승률", color="blue", pts=[.7, .78, .6, .4, .3, .25, .22], end="안정")])
S("이 이야기의 교훈은 두 가지입니다. 금리는 경제를 식힐 만큼 강력하다는 것, 그리고 물가는 한번 기대가 굳어지면 잡기가 정말 어렵다는 것.", "check", headline="볼커의 [교훈]",
  items=[dict(t="금리는 경제를 [식힐 만큼] 강력하다", c="red"), dict(t="물가 [기대]가 굳으면 잡기 어렵다", c="blue")])
S("그래서 요즘 중앙은행들이 물가가 조금만 오를 기미가 보여도 민감하게 반응하는 겁니다. 1970년대를 되풀이하지 않으려고요.", "story", scene="news_tv", relabel={">시총 −660조<": ">물가와의 전쟁<"})
S("세 번째 이야기를 정리하겠습니다. 금리는 시간의 가격, 환율은 나라 돈끼리의 가격입니다.", "check", headline="세 번째 이야기 정리 ①",
  items=[dict(t="금리 = [시간의 가격]", c="red"), dict(t="환율 = [나라 돈끼리의 가격]", c="blue"), dict(t="금리 ↑ → 자산 가격 [↓] 경향", c="gold")])
S("환율이 오르면 원화가 약해진 것이고, 수출엔 좋고 수입과 물가엔 부담입니다. 그리고 환율은 맞히지 말고, 나눠서 대비하세요.", "check", headline="세 번째 이야기 정리 ②",
  items=[dict(t="환율 ↑ = [원화 약세]", c="blue"), dict(t="수출엔 [좋고], 물가엔 [부담]", c="gold"), dict(t="환율은 맞히지 말고 [대비]", c="red")])
S("그럼 이 금리가 우리나라에서 가장 큰 힘을 발휘하는 곳은 어디일까요? 바로 집입니다. 다음 이야기는 부동산이에요.", "quote", lines=["금리가 가장 큰 힘을 쓰는 곳", "[우리나라의 집]"], size=120)


def project(clip_paths=None):
    scenes = []
    for s in sc:
        d = {"id": s["id"], "text": s["text"], "visual": {"type": "clip", "path": (clip_paths or {}).get(s["id"], f"{PJ}/clips/_pending.mp4")}}
        if s.get("chapter"):
            d["chapter"] = s["chapter"]
        scenes.append(d)
    meta = json.load(open(os.path.join(HERE, "meta.json"), encoding="utf-8"))
    return dict(meta, scenes=scenes)


def render_all(only=None):
    import hf_econ as H
    sys.path.insert(0, ROOT)
    from studio import tts
    pj = json.load(open(os.path.join(HERE, "project.json"), encoding="utf-8"))
    audio_dir = os.path.join(HERE, "audio")
    clips_dir = os.path.join(HERE, "clips")
    os.makedirs(clips_dir, exist_ok=True)
    paths = {}
    by_id = {s["id"]: s for s in pj["scenes"]}
    for i, s in enumerate(sc):
        if only and s["id"] not in only:
            continue
        scene = by_id[s["id"]]
        audio, real = tts.scene_audio(scene, pj, audio_dir, False)
        nxt = sc[i + 1] if i + 1 < len(sc) else None
        sp = float(pj.get("scene_pause", 0.30))
        pause = max(0.45, sp + 0.2) if nxt and nxt.get("chapter") else sp
        T = round((tts.duration(audio) + pause) * 30) / 30
        parts = s["parts"]
        tot = sum(len(re.sub(r"\s", "", p["seg"])) for p in parts)
        outs = []
        for k, part in enumerate(parts):
            frac = len(re.sub(r"\s", "", part["seg"])) / tot
            Dp = round(T * frac * 30) / 30
            if k == len(parts) - 1:
                Dp = round((T - sum(round(T * len(re.sub(r"\s", "", q["seg"])) / tot * 30) / 30 for q in parts[:-1])) * 30) / 30
            if part["p"].get("intro"):
                Dp = max(Dp, 3.0)
            outs.append(H.render(os.environ.get("HF_ROOT", "/home/user/hf/crisis"), f"{s['id']}p{k}", part["kind"], part["p"], Dp, os.path.join(clips_dir, "parts")))
        if len(outs) == 1:
            final = os.path.join(clips_dir, f"{s['id']}.mp4")
            if not os.path.exists(final) or os.path.realpath(final) != os.path.realpath(outs[0]):
                subprocess.run(["cp", outs[0], final], check=True)
        else:
            final = os.path.join(clips_dir, f"{s['id']}.mp4")
            lst = final + ".txt"
            open(lst, "w").write("".join(f"file '{o}'\n" for o in outs))
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", final], check=True)
        paths[s["id"]] = f"{PJ}/clips/{s['id']}.mp4"
        print(f"{s['id']} {T:.1f}s {[p['kind'] for p in parts]}", flush=True)
    return paths


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "plan"
    if cmd == "plan":
        json.dump(project(), open(os.path.join(HERE, "project.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("scenes:", len(sc), "chars:", sum(len(re.sub(r"\s", "", s["text"])) for s in sc))
    elif cmd == "render":
        only = set(sys.argv[2].split(",")) if len(sys.argv) > 2 else None
        paths = render_all(only)
        allp = {s["id"]: f"{PJ}/clips/{s['id']}.mp4" for s in sc}
        json.dump(project(allp), open(os.path.join(HERE, "project.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
