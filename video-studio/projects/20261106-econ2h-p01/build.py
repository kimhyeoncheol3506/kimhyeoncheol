"""33편 경제 지식 2시간 완전정리 — 1부 (통화량). 8부로 나눠 만든 뒤 합친다.
사용: python3 projects/20261106-econ2h-p01/build.py plan | render [ids]
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
PJ = "projects/20261106-econ2h-p01"

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

# ═════════════ 전체 오프닝 ═════════════
_chip = "오프닝"
Q("월급은 그대로인데, 왜 나만 점점 가난해지는 것 같을까요?", "월급은 그대로인데", "왜 나만 [가난해지는] 것 같을까", size=110)
S("열심히 일하고, 아껴 쓰고, 꼬박꼬박 저축했는데도 말이죠.", "story", scene="bed_phone")
S("오늘은 그 이유를 돈이 움직이는 원리부터 하나씩 풀어 보려고 합니다.", "quote", lines=["그 이유를", "[돈이 움직이는 원리]부터"], size=120)
S("준비한 이야기는 여덟 개입니다. 통화량, 리스크, 금리와 환율, 부동산.", "check", headline="오늘의 [여덟 가지 이야기] ①",
  items=[dict(t="[통화량] — 돈은 왜 계속 늘어날까", c="gold", no="1"), dict(t="[리스크] — 이기는 투자의 조건", c="blue", no="2"),
         dict(t="[금리와 환율] — 돈과 돈의 교환 비율", c="red", no="3"), dict(t="[부동산] — 우리나라 집값의 비밀", c="gold", no="4")])
S("그리고 부채, 경제 위기, 잘사는 나라의 조건, 마지막으로 선택입니다.", "check", headline="오늘의 [여덟 가지 이야기] ②",
  items=[dict(t="[부채] — 독일까, 도구일까", c="blue", no="5"), dict(t="[경제 위기] — 진짜 위기의 신호", c="red", no="6"),
         dict(t="[선진국] — 잘사는 나라의 조건", c="gold", no="7"), dict(t="[선택] — 나는 내 선택의 합", c="blue", no="8")])
S("화면을 안 보셔도 괜찮습니다. 운전하시면서, 설거지하시면서, 운동하시면서 그냥 귀로 들으셔도 다 이해되게 말로 풀어 드릴게요.", "story", scene="subway_comments", relabel={">거품!<": ">경제<", ">닷컴 2!<": ">금리<", ">끝났다<": ">환율<", ">탈출!<": ">부동산<"})
S("숫자는 꼭 필요한 것만, 대신 왜 그런지는 끝까지 설명하겠습니다. 그럼 시작해 볼까요.", "quote", lines=["숫자는 꼭 필요한 것만", "[왜 그런지]는 끝까지"], size=120)

# ═════════════ 1강 통화량 ═════════════
CH("1강", "통화량, 우리가 [재테크]를 하는 이유", "1강 · 통화량 — 우리가 재테크를 하는 이유", name="1강 통화량 — 우리가 재테크를 하는 이유")
S("첫 번째 이야기는 통화량입니다. 말은 어렵지만 뜻은 간단해요. 세상에 풀려 있는 돈의 양입니다.", "kpi", kicker="1강 · 오늘의 단어", big="통화량", color="gold", unit="세상에 풀려 있는 돈의 양", size=230)
S("지갑 속 현금, 통장에 든 예금, 언제든 꺼내 쓸 수 있는 돈을 전부 합친 거죠.", "flow", headline="통화량 = [꺼내 쓸 수 있는 돈]의 합",
  nodes=[dict(t="현금", s="지갑 속 돈", c="gold", icon="1"), dict(t="예금", s="통장 속 돈", c="blue", icon="2"), dict(t="통화량", s="전부 더한 것", c="red", icon="=")])
S("한국은행은 이걸 여러 단계로 나눠서 재는데, 뉴스에 가장 자주 나오는 건 엠투, 넓은 의미의 통화량입니다.", "kpi", kicker="뉴스에 자주 나오는 지표", big="M2 (광의통화)", color="blue", unit="현금 + 예금 + 짧은 기간 금융상품", size=170)
S("그런데 이 숫자에는 아주 중요한 특징이 하나 있습니다.", "quote", lines=["이 숫자에는", "[아주 중요한 특징]이 하나"], size=120)
S("거의 줄어들지 않는다는 겁니다. 길게 보면 해마다 7% 안팎씩 꾸준히 늘어 왔습니다.", "chart", headline="통화량은 [거의 줄지 않는다]", badge=EX,
  lines=[dict(name="광의통화(M2)", color="gold", pts=[.12, .17, .22, .29, .37, .46, .57, .7, .84], end="해마다 7% 안팎")])
S("2025년 10월 기준으로 우리나라 광의통화는 약 4천4백70조 원, 역대 최대였습니다.", "kpi", kicker="2025년 10월 광의통화 평잔 (한국은행, 구 기준)", big="약 4,470조 원", color="red", unit="역대 최대", size=190)
S("해마다 7%씩 늘어나면 어떻게 될까요? 여기서 쓰는 계산법이 하나 있습니다. 칠십이의 법칙입니다.", "kpi", kicker="두 배가 되는 데 걸리는 시간", big="72의 법칙", color="gold", unit="72 ÷ 증가율 = 두 배까지 걸리는 해", size=210)
S("72를 7로 나누면 약 10입니다. 그러니까 돈의 양이 대략 10년마다 두 배가 된다는 뜻이에요.", "flow", headline="72 ÷ 7 ≈ [10년마다 두 배]", badge="계산 예시",
  nodes=[dict(t="72", s="", c="gold", icon="1"), dict(t="÷ 7%", s="해마다 늘어나는 속도", c="blue", icon="÷"), dict(t="≈ 10년", s="돈의 양이 두 배", c="red", icon="=")])
S("10년 전보다 세상에 돈이 두 배 많아졌다. 이게 무슨 의미인지 짜장면으로 한번 볼까요.", "story", scene="memory_store", relabel={">가격 ↑↑<": ">짜장면 ↑<"})
S("1970년, 짜장면 한 그릇의 평균 가격은 100원이었습니다.", "kpi", kicker="1970년 짜장면 평균 가격 (한국물가정보)", big="100원", color="blue", size=260)
S("2025년 서울에서는 7천5백 원 정도 합니다. 약 75배가 올랐죠.", "compare", headline="짜장면 한 그릇, [약 75배]",
  left=dict(title="1970년", c="mute", rows=["100원"]), right=dict(title="2025년 서울 (보도)", c="red", rows=["약 7,500원", "약 75배"]))
S("짜장면이 75배 맛있어졌을까요? 아니죠. 짜장면은 그대로인데, 돈의 양이 늘어서 돈 한 장의 힘이 약해진 겁니다.", "scale", headline="짜장면은 그대로, [돈의 힘]이 약해졌다",
  left=dict(t="짜장면", s="그대로", c="gold"), right=dict(t="돈의 양", s="계속 늘어남", c="red"), tilt=-10)
S("여기서 첫 번째 핵심이 나옵니다. 돈이 늘어나는 세상에서, 현금을 그냥 쥐고만 있으면 가만히 있어도 가난해집니다.", "quote", lines=["돈이 늘어나는 세상에서", "현금만 쥐고 있으면", "가만히 있어도 [가난해진다]"], size=100)
S("이걸 이해하려면, 돈이 도대체 어떻게 늘어나는지부터 알아야 합니다.", "qa", q="돈은 도대체\n[어떻게] 늘어날까?")
S("돈을 처음 찍어 내는 곳은 한국은행입니다. 이렇게 찍어 낸 돈을 본원통화라고 부릅니다.", "kpi", kicker="돈의 출발점", big="본원통화", color="gold", unit="한국은행이 처음 공급하는 돈", size=220)
S("그런데 실제로 세상에 도는 돈은 이것보다 훨씬 많습니다. 은행이 돈을 불리는 마법을 부리기 때문이에요.", "story", scene="vault")
S("예를 들어 볼게요. 제가 은행에 100만 원을 맡깁니다.", "kpi", kicker="신용창조 예시", big="예금 100만 원", color="blue", size=200)
S("은행은 이 돈을 금고에 그대로 두지 않습니다. 일부만 남기고 나머지를 다른 사람에게 빌려줍니다.", "flow", headline="은행은 [빌려준다]", badge="계산 예시",
  nodes=[dict(t="예금 100만 원", s="내가 맡긴 돈", c="blue", icon="1"), dict(t="10만 원 남김", s="지급준비금", c="gold", icon="2"), dict(t="90만 원 대출", s="다른 사람에게", c="red", icon="3")])
S("90만 원을 빌린 사람은 그 돈으로 가게에서 물건을 사고, 가게 주인은 그 90만 원을 다시 은행에 넣습니다.", "story", scene="shop_window", relabel={">연말 보고서<": ">오늘 매출<"})
S("그럼 은행은 또 그중 일부를 남기고 81만 원을 빌려줍니다. 이게 계속 반복되는 거죠.", "chart", headline="예금 → 대출 → 예금, [끝없이 반복]", badge="계산 예시",
  lines=[dict(name="쌓이는 예금 합계", color="gold", pts=[.1, .28, .42, .53, .62, .69, .74, .78, .8], end="최대 1천만 원")])
S("이론적으로는 처음 맡긴 100만 원이 최대 천만 원어치 예금으로 불어날 수 있습니다. 이걸 신용창조라고 합니다.", "kpi", kicker="지급준비율 10%일 때 이론상 최대", big="100만 → 1천만 원", color="red", unit="신용창조", size=170)
S("물론 실제로는 사람들이 현금도 들고 있고, 은행도 마음대로 다 빌려주지는 못하니까 이만큼 불어나지는 않습니다.", "check", headline="실제로는 [덜] 불어난다",
  items=[dict(t="사람들이 [현금]을 일부 들고 있음", c="blue"), dict(t="은행이 [대출 규제]를 받음", c="gold"), dict(t="빌리려는 [수요]가 있어야 함", c="red")])
S("핵심은 이겁니다. 지금 세상의 돈 대부분은 누군가의 대출에서 태어났다는 것.", "quote", lines=["세상의 돈 대부분은", "누군가의 [대출]에서 태어났다"], size=110)
S("그래서 대출이 늘면 돈이 늘고, 대출이 줄면 돈이 도는 속도가 느려집니다. 이 연결 고리는 다섯 번째 이야기, 부채에서 다시 만납니다.", "flow", headline="대출과 통화량은 [한 몸]",
  nodes=[dict(t="대출 증가", s="", c="red", icon="↑"), dict(t="예금 증가", s="", c="gold", icon="→"), dict(t="통화량 증가", s="", c="blue", icon="↑")])
S("잠깐 돈의 역사 이야기를 해 볼게요. 옛날에는 돈을 마음대로 늘릴 수가 없었습니다. 돈이 금에 묶여 있었거든요.", "kpi", kicker="금본위제", big="돈 = 금", color="gold", unit="금이 있는 만큼만 돈을 찍을 수 있었다", size=230)
S("은행에 지폐를 가져가면 정해진 양의 금으로 바꿔 줬습니다. 그러니 금이 늘지 않으면 돈도 늘 수 없었죠.", "flow", headline="금본위제의 [약속]",
  nodes=[dict(t="지폐", s="", c="gold", icon="1"), dict(t="은행에 가져가면", s="", c="blue", icon="2"), dict(t="정해진 양의 금", s="으로 바꿔 줌", c="red", icon="3")])
S("2차 세계대전 뒤에는 미국 달러만 금과 바꿔 주고, 다른 나라 돈은 달러에 묶는 방식이 쓰였습니다.", "kpi", kicker="1944년 브레턴우즈 체제", big="달러 = 금", color="gold", unit="다른 나라 돈은 달러에 고정", size=230)
S("그런데 1971년, 미국 닉슨 대통령이 달러를 더 이상 금으로 바꿔 주지 않겠다고 선언합니다.", "timeline", headline="돈이 금에서 [풀려난 날]",
  events=[dict(when="1944", t="브레턴우즈 체제", s="달러만 금과 교환", c="gold"), dict(when="1971.8", t="닉슨 선언", s="금 교환 중단", c="red"), dict(when="이후", t="신용화폐 시대", s="돈 = 믿음", c="blue")])
S("이때부터 돈은 금이 아니라 믿음으로 움직이게 됩니다. 정부와 중앙은행을 믿으니까 이 종이를 돈으로 쓰는 거죠.", "quote", lines=["이때부터 돈은", "금이 아니라 [믿음]으로 움직인다"], size=110)
S("금이라는 족쇄가 풀리자, 돈의 양은 경제 상황에 맞춰 훨씬 자유롭게 늘어날 수 있게 됐습니다. 지금 우리가 사는 세상이 바로 이 세상입니다.", "chart", headline="족쇄가 풀린 뒤 [돈의 양]", badge=EX,
  lines=[dict(name="세계 통화량", color="gold", pts=[.1, .11, .13, .18, .26, .37, .52, .72], end="1971년 이후 가속")], marks=[dict(x=.3, text="1971 금 교환 중단", color="red")])
S("믿음으로 움직이는 돈이라서, 그 믿음이 흔들릴 때가 진짜 위험합니다. 이건 여섯 번째 이야기, 경제 위기에서 자세히 다룰게요.", "story", scene="shield", relabel={">FCF<": ">믿음<"})
S("그럼 물어볼게요. 돈의 양이 늘어나는 건, 우리한테 좋은 일일까요, 나쁜 일일까요?", "qa", q="돈이 늘어나는 건\n[좋은 일]일까, 나쁜 일일까?")
S("나쁜 점부터 보겠습니다. 가장 먼저 떠오르는 건 물가죠.", "kpi", kicker="나쁜 점 ①", big="물가 상승", color="blue", unit="같은 돈으로 살 수 있는 게 줄어든다", size=210)
S("돈이 늘어나는 만큼 물건이 늘지 않으면, 같은 물건을 사는 데 더 많은 돈이 필요해집니다.", "scale", headline="돈이 물건보다 [빨리] 늘면",
  left=dict(t="물건의 양", s="천천히 증가", c="gold"), right=dict(t="돈의 양", s="빠르게 증가", c="red"), tilt=-12)
S("그런데 사실 더 무서운 건 물가보다 자산 가격입니다.", "quote", lines=["더 무서운 건", "물가보다 [자산 가격]"], size=130)
S("소비자물가는 보통 1년에 2에서 3% 정도 오르는데, 집값이나 주가 같은 자산은 길게 보면 돈의 양이 늘어나는 속도를 더 닮아 갑니다.", "chart", headline="물가보다 [자산]이 돈의 양을 닮는다", badge=EX,
  lines=[dict(name="소비자물가", color="blue", pts=[.2, .23, .26, .29, .32, .35, .38], end="연 2~3%"), dict(name="자산 가격", color="red", pts=[.2, .26, .31, .4, .47, .58, .7], end="돈의 양을 닮음")])
S("새로 생긴 돈은 결국 어딘가에 머물러야 하는데, 그 돈이 가장 많이 흘러가는 곳이 집과 주식 같은 자산이거든요.", "flow", headline="새 돈이 [흘러가는 곳]",
  nodes=[dict(t="새로 생긴 돈", s="대출·예금", c="gold", icon="1"), dict(t="머물 곳을 찾음", s="", c="blue", icon="2"), dict(t="집·주식 등 자산", s="가격 상승", c="red", icon="3")])
S("여기서 경제학 이야기 하나 더 할게요. 칸티용 효과라는 게 있습니다.", "kpi", kicker="18세기 경제학자 리샤르 칸티용", big="칸티용 효과", color="gold", unit="새 돈을 먼저 받는 사람이 이득", size=210)
S("새로 풀린 돈은 모두에게 똑같이 나눠지지 않습니다. 은행, 대출을 받는 기업, 자산을 가진 사람에게 먼저 도착하죠.", "flow", headline="새 돈이 [도착하는 순서]",
  nodes=[dict(t="은행·금융", s="가장 먼저", c="red", icon="1"), dict(t="대출받는 기업·자산가", s="그다음", c="gold", icon="2"), dict(t="월급 받는 사람", s="가장 늦게", c="blue", icon="3")])
S("먼저 받은 사람은 아직 가격이 덜 오른 상태에서 돈을 씁니다. 늦게 받는 사람은 이미 가격이 오른 뒤에야 돈을 받고요.", "compare", headline="먼저 받는 사람 vs [늦게 받는 사람]",
  left=dict(title="먼저 받는 쪽", c="red", rows=["가격이 덜 오른 때 산다", "이득"]), right=dict(title="늦게 받는 쪽", c="blue", rows=["가격이 오른 뒤 받는다", "손해"]))
S("월급은 보통 가장 늦게 오르죠. 열심히 일하는데도 뒤처지는 느낌, 기분 탓이 아니었던 겁니다.", "story", scene="party_outside")
S("이 효과를 가장 생생하게 본 게 2020년 코로나 때였습니다.", "kpi", kicker="가장 최근의 생생한 사례", big="2020년", color="red", unit="코로나와 돈 풀기", size=260)
S("경제가 멈추자 세계 각국은 금리를 거의 0까지 내리고, 돈을 엄청나게 풀었습니다.", "flow", headline="2020년, 세계가 [돈을 풀다]",
  nodes=[dict(t="경제 멈춤", s="코로나", c="blue", icon="1"), dict(t="금리 0% 근처", s="", c="gold", icon="2"), dict(t="대규모 돈 풀기", s="", c="red", icon="3")])
S("미국 중앙은행의 자산은 2020년 초 4조 달러 정도에서 2022년에는 9조 달러 가까이로 두 배 넘게 불어났습니다.", "dual", headline="미국 연준 자산, [두 배 넘게]",
  panels=[dict(title="2020년 초", color="blue", pts=[.3, .3], tag="약 4조 달러", note="미국 연준 총자산"), dict(title="2022년", color="red", pts=[.3, .8], tag="약 9조 달러", note="미국 연준 총자산")])
S("우리나라도 통화량 증가율이 한때 10%를 훌쩍 넘었습니다. 그리고 그 돈은 어디로 갔을까요?", "qa", q="그 많은 돈은\n[어디로] 갔을까?")
S("주식과 집으로 갔습니다. 2020년과 2021년, 주가와 집값이 가파르게 올랐던 거 기억하시죠.", "chart", headline="풀린 돈은 [자산]으로", badge=EX,
  lines=[dict(name="주가·집값", color="red", pts=[.3, .25, .4, .55, .7, .78], end="급등"), dict(name="월급", color="blue", pts=[.3, .3, .31, .32, .33, .34], end="제자리")])
S("그때 자산을 가지고 있던 사람과, 현금만 가지고 있던 사람의 격차가 크게 벌어졌습니다. 벼락거지라는 말이 나온 게 이때였죠.", "story", scene="two_giants", relabel={">삼성전자<": ">집<", ">SK하이닉스<": ">주식<"})
S("두 번째 나쁜 점은 상대적인 가난입니다. 내 통장은 그대로인데, 남들 자산이 7%씩 늘어나면 어떻게 될까요?", "kpi", kicker="나쁜 점 ②", big="상대적 가난", color="blue", unit="내가 그대로면, 뒤로 가는 것", size=210)
S("1억 원이 있는 두 사람이 있다고 해 볼게요. 한 사람은 현금으로 들고 있고, 한 사람은 해마다 7%씩 불렸습니다.", "compare", headline="1억 원을 가진 [두 사람]",
  left=dict(title="A: 현금 보관", c="blue", rows=["1억 원 그대로"]), right=dict(title="B: 해마다 7%", c="red", rows=["10년 뒤 약 2억 원", "20년 뒤 약 3억 9천만 원"]))
S("20년 뒤, 둘의 차이는 거의 네 배가 됩니다. 처음엔 똑같이 출발했는데 말이죠.", "dual", headline="20년 뒤, [거의 네 배]", badge="계산 예시 · 복리 7%",
  panels=[dict(title="A: 현금", color="blue", pts=[.3, .3], tag="1억 원", note="숫자는 그대로"), dict(title="B: 해마다 7%", color="red", pts=[.3, .85], tag="약 3.9억 원", note="복리 효과")])
S("그래서 재테크는 부자가 되려는 욕심이 아니라, 제자리를 지키려는 최소한의 방어라고 볼 수 있습니다.", "quote", lines=["재테크는 욕심이 아니라", "제자리를 지키는 [최소한의 방어]"], size=110)
S("그럼 좋은 점은 없을까요? 있습니다. 돈이 늘어난다는 건 기회도 같이 늘어난다는 뜻이거든요.", "kpi", kicker="좋은 점", big="기회의 증가", color="red", unit="돈이 돌면 기업도, 일자리도 커진다", size=210)
S("돈이 돌면 기업이 투자를 하고, 일자리가 생기고, 새로운 사업이 태어납니다. 경제가 성장하려면 돈이 적당히 늘어나야 해요.", "story", scene="fab_korea")
S("실제로 돈이 너무 안 늘어나면 더 큰일이 납니다. 물가가 거꾸로 떨어지는 디플레이션이죠.", "kpi", kicker="돈이 너무 안 늘면", big="디플레이션", color="blue", unit="물가가 계속 떨어지는 상태", size=210)
S("물건값이 계속 떨어지면 사람들은 내일 사려고 오늘 소비를 미룹니다. 기업은 물건이 안 팔리니 월급을 깎고, 사람을 줄이죠.", "flow", headline="디플레이션의 [악순환]",
  nodes=[dict(t="물가 하락", s="", c="blue", icon="1"), dict(t="소비 미룸", s="내일이 더 싸니까", c="gold", icon="2"), dict(t="월급·일자리 감소", s="", c="red", icon="3")])
S("일본이 1990년대부터 오랫동안 겪은 게 바로 이 문제였습니다. 잃어버린 20년, 30년이라는 말이 그래서 나왔죠.", "timeline", headline="일본의 [잃어버린 시간]",
  events=[dict(when="1990년 전후", t="자산 거품 붕괴", s="", c="red"), dict(when="1990년대 후반~", t="물가 하락 시작", s="디플레이션", c="blue"), dict(when="2010년대", t="돈 풀기로 탈출 시도", s="", c="gold")])
S("그래서 중앙은행들은 물가가 1년에 2% 정도 오르는 걸 목표로 삼습니다. 한국은행도 마찬가지예요.", "kpi", kicker="한국은행 물가안정목표", big="연 2%", color="gold", unit="너무 낮지도, 너무 높지도 않게", size=250)
S("돈이 너무 많이 풀리면 어떤 일이 벌어지는지, 역사 속 극단적인 이야기 두 개를 들려드릴게요.", "quote", lines=["돈이 너무 많이 풀리면", "[역사 속 두 장면]"], size=130)
S("첫 번째는 1923년 독일입니다. 1차 세계대전에서 진 독일은 엄청난 배상금을 물어야 했고, 정부는 돈을 마구 찍어 냈습니다.", "kpi", kicker="1923년 독일", big="하이퍼인플레이션", color="red", unit="정부가 돈을 마구 찍어 낸 결과", size=200)
S("물가가 하루에도 몇 번씩 올라서, 노동자들은 월급을 하루에 두 번 받아 받자마자 뛰어가서 물건을 샀다고 합니다. 오후가 되면 같은 돈으로 살 수 있는 게 줄어드니까요.", "story", scene="chase_buy")
S("그해 말 빵 한 덩어리 값이 수천억 마르크에 이르렀고, 아이들은 지폐 다발로 블록 쌓기 놀이를 했습니다. 돈이 종이보다 못한 물건이 된 거죠.", "chart", headline="1923년 독일 [빵값]", badge=EX,
  lines=[dict(name="빵 한 덩어리 가격", color="red", pts=[.02, .02, .03, .05, .1, .3, .9], end="수천억 마르크")])
S("두 번째는 2000년대 짐바브웨입니다. 물가가 폭등해서 결국 100조 짐바브웨 달러짜리 지폐까지 찍었어요. 그 지폐 한 장으로 빵 몇 개도 사기 어려웠습니다.", "kpi", kicker="2000년대 후반 짐바브웨", big="100조 달러 지폐", color="blue", unit="그래도 빵 몇 개 사기 어려웠다", size=200)
S("두 나라의 공통점은 정부가 믿음을 잃었다는 겁니다. 이 종이를 내일도 돈으로 받아 줄까 하는 의심이 퍼지는 순간, 돈은 순식간에 가치를 잃었죠.", "quote", lines=["돈의 가치를 지키는 건", "[믿음]이다"], size=140)
S("우리가 사는 세상은 다행히 이런 극단과는 거리가 멉니다. 하지만 원리는 같아요. 돈이 늘어나는 속도가 빨라질수록, 돈의 힘은 약해집니다.", "story", scene="saving_32")
S("정리하면 이렇습니다. 돈이 늘어나는 건 피할 수 없는 흐름이고, 경제가 돌아가려면 필요하기도 합니다.", "check", headline="1강 정리 ①",
  items=[dict(t="통화량은 [거의 줄지 않는다]", c="gold"), dict(t="돈은 [대출]에서 태어난다", c="blue"), dict(t="새 돈은 [자산]부터 올린다", c="red")])
S("문제는 그 흐름에서 내가 어디에 서 있느냐입니다. 현금만 쥐고 있으면 흐름에 밀려나고, 자산을 가지고 있으면 흐름을 탈 수 있죠.", "story", scene="goose")
S("그럼 생존법은 뭘까요? 첫째, 내 돈이 불어나는 속도를 돈의 양이 늘어나는 속도와 비교하는 습관입니다.", "kpi", kicker="생존법 ①", big="속도 비교", color="gold", unit="내 자산 증가율 vs 통화량 증가율", size=230)
S("예금 금리가 3%인데 돈의 양이 7%씩 늘어난다면, 숫자는 늘어도 실제로는 뒤로 가고 있는 겁니다.", "scale", headline="예금 3% vs [통화량 7%]",
  left=dict(t="예금 이자", s="연 3% (예시)", c="blue"), right=dict(t="통화량 증가", s="연 7% 안팎", c="red"), tilt=-14)
S("둘째, 가진 돈의 일부라도 돈이 흘러가는 곳, 그러니까 자산에 두는 겁니다. 주식이든, 부동산이든, 내 사업이든요.", "check", headline="생존법 ② · 돈이 [흘러가는 곳]에",
  items=[dict(t="[주식] — 기업의 성장을 나눠 갖기", c="red"), dict(t="[부동산] — 실물 자산", c="gold"), dict(t="[내 실력·사업] — 가장 큰 자산", c="blue")])
S("셋째, 그렇다고 아무 자산이나 사면 안 된다는 겁니다. 흐름을 타려다 크게 다치는 사람도 많거든요.", "kpi", kicker="생존법 ③", big="아무거나 X", color="blue", unit="흐름을 타려다 다치지 않기", size=230)
S("돈의 양이 10년마다 두 배가 되는 세상에서도, 망하는 회사가 있고 떨어지는 집값이 있습니다.", "story", scene="hacked")
S("여기서 자주 받는 질문 두 개에 답하고 넘어갈게요.", "quote", lines=["자주 받는 질문", "[두 가지]"], size=140)
S("첫 번째 질문. 그럼 현금은 아예 들고 있으면 안 되나요? 아닙니다. 현금은 꼭 필요합니다.", "qa", q="현금은 아예\n[들고 있으면 안 되나요?]")
S("갑자기 일이 끊기거나 아플 때를 대비한 비상금, 보통 생활비 서너 달에서 여섯 달 치는 현금처럼 바로 꺼낼 수 있게 두는 게 좋습니다.", "kpi", kicker="현금의 역할 ①", big="비상금", color="gold", unit="생활비 3~6개월 치는 바로 꺼낼 수 있게", size=230)
S("그리고 시장이 크게 흔들릴 때 좋은 자산을 싸게 살 수 있는 기회 자금이기도 하죠. 현금은 수익이 아니라 선택권입니다.", "quote", lines=["현금은 수익이 아니라", "[선택권]입니다"], size=130)
S("두 번째 질문. 통화량은 어디서 확인하나요? 한국은행이 매달 통화 및 유동성이라는 자료를 발표합니다.", "kpi", kicker="매달 한국은행 발표", big="통화 및 유동성", color="blue", unit="뉴스에서 '시중 통화량'으로 나오는 숫자", size=180)
S("뉴스에서 시중 통화량이 역대 최대라는 말이 나오면, 이제 이렇게 들으시면 됩니다. 돈의 힘이 또 조금 약해졌구나.", "story", scene="news_tv", relabel={">시총 −660조<": ">통화량 역대 최대<"})
S("여기서 조금 더 깊이 들어가 볼게요. 돈의 양과 물가의 관계를 설명하는 아주 오래된 생각이 있습니다. 화폐 수량설이라고 해요.", "kpi", kicker="더 깊이 ①", big="화폐 수량설", color="gold", unit="돈의 양 × 도는 속도 = 물가 × 생산량", size=220)
S("돈의 양에 돈이 도는 속도를 곱하면, 물가에 생산량을 곱한 것과 같다는 식이죠. 생산량이 그대로인데 돈만 늘면 물가가 오른다는 겁니다.", "flow", headline="MV = PY, [말로] 풀면",
  nodes=[dict(t="돈의 양 × 도는 속도", s="M × V", c="gold", icon="1"), dict(t="=", s="", c="blue", icon="="), dict(t="물가 × 생산량", s="P × Y", c="red", icon="2")])
S("그런데 2010년대에는 이상한 일이 벌어졌습니다. 각국이 돈을 엄청나게 풀었는데도 소비자 물가는 별로 오르지 않았거든요.", "qa", q="돈을 풀었는데\n물가는 [왜 안 올랐을까?]")
S("답은 돈이 도는 속도에 있었습니다. 풀린 돈이 가게로 가지 않고, 은행과 자산 시장에 머물렀어요. 그래서 물가 대신 집값과 주가가 올랐던 거죠.", "dual", headline="풀린 돈이 [머문 곳]", badge=EX,
  panels=[dict(title="소비자 물가", color="blue", pts=[.4, .46], tag="조금 상승", note="가게로 덜 갔다"), dict(title="자산 가격", color="red", pts=[.4, .85], tag="크게 상승", note="자산 시장에 머물렀다")])
S("그러다 2020년 코로나 때는 정부가 사람들에게 직접 돈을 나눠 줬고, 공급까지 막히면서 물가가 폭발했습니다. 미국 물가는 2022년 6월 9%를 넘었고, 우리나라도 2022년 7월 6.3%를 기록했죠.", "compare", headline="2022년, [물가가 폭발]하다",
  left=dict(title="미국", c="red", rows=["2022년 6월", "9%대"]), right=dict(title="한국", c="red", rows=["2022년 7월", "6.3%"]))
S("결국 돈이 늘어날 때 무엇이 오르느냐는, 그 돈이 어디로 흘러가느냐에 달려 있습니다. 은행과 자산으로 가면 자산이, 사람들 지갑으로 가면 물가가 오르기 쉽죠.", "flow", headline="돈이 [어디로] 가느냐",
  nodes=[dict(t="새 돈", s="", c="gold", icon="1"), dict(t="자산 시장으로 → 자산 가격 ↑", s="", c="red", icon="2"), dict(t="지갑으로 → 물가 ↑", s="", c="blue", icon="3")])
S("그래서 뉴스를 볼 때 돈을 푼다는 말이 나오면, 이 돈이 누구 손에 먼저 들어가는지를 같이 보시면 됩니다. 앞에서 본 칸티용 효과와 같은 이야기예요.", "story", scene="news_tv", relabel={">시총 −660조<": ">돈 푼다<"})
S("마지막으로 경제학자들이 쓰는 조금 무서운 표현 하나 소개할게요. 인플레이션은 보이지 않는 세금이다.", "quote", lines=["인플레이션은", "[보이지 않는 세금]"], size=140)
S("정부가 세금을 올리면 다들 알아차리고 반대하죠. 그런데 돈의 가치가 조금씩 떨어지는 건 아무도 고지서를 받지 않습니다. 조용히, 현금을 가진 모든 사람에게서 걷히는 세금이에요.", "compare", headline="[보이는 세금] vs 보이지 않는 세금",
  left=dict(title="세금 인상", c="gold", rows=["고지서가 온다", "모두가 알아챈다"]), right=dict(title="인플레이션", c="blue", rows=["고지서가 없다", "현금에서 조용히 빠져나간다"]))
S("그래서 돈의 양이 정해져 있는 자산에 관심을 갖는 사람들도 있습니다. 대표적인 게 금이고, 최근에는 발행량이 정해진 비트코인을 디지털 금이라고 부르는 사람도 있죠.", "compare", headline="양이 [정해진] 자산",
  left=dict(title="금", c="gold", rows=["캘 수 있는 양에 한계", "수천 년의 신뢰"]), right=dict(title="비트코인", c="blue", rows=["발행량 상한 2,100만 개", "가격 변동이 매우 큼"]))
S("다만 양이 정해져 있다고 가격이 꼭 오르는 건 아닙니다. 사람들이 그 자산을 얼마나 원하느냐에 따라 크게 흔들리죠. 이건 바로 다음 이야기, 리스크와 연결됩니다.", "story", scene="candle_board")
S("결국 질문은 이렇게 바뀝니다. 무엇을, 언제, 얼마나 위험을 감수하면서 살 것인가.", "quote", lines=["무엇을, 언제,", "[얼마나 위험을 감수]하며 살 것인가"], size=110)
S("이게 바로 다음 이야기, 리스크입니다.", "quote", lines=["다음 이야기", "[리스크]"], size=150)


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
