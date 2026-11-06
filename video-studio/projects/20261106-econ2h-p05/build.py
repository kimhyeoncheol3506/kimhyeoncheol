"""33편 경제 지식 2시간 완전정리 — 5부 (부채). 8부로 나눠 만든 뒤 합친다.
사용: python3 projects/20261106-econ2h-p05/build.py plan | render [ids]
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
PJ = "projects/20261106-econ2h-p05"

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

# ═════════════ 5강 부채 ═════════════
CH("5강", "부채, [쓸 것인가] 말 것인가", "5강 · 부채 — 쓸 것인가 말 것인가", name="5강 부채 — 쓸 것인가 말 것인가")
S("다섯 번째 이야기는 부채, 그러니까 빚입니다. 빚이라는 말을 들으면 어떤 느낌이 드세요?", "kpi", kicker="5강 · 오늘의 단어", big="부채", color="blue", unit="남에게 빌려 쓴 돈", size=250)
S("대부분 무섭다, 피해야 한다고 생각하실 겁니다. 빚 때문에 고생한 이야기를 주변에서 한 번쯤은 들어 보셨을 테니까요.", "story", scene="debt_bill")
S("그런데 이상한 점이 하나 있습니다. 빚이 그렇게 위험하기만 하다면, 은행은 어떻게 돈을 벌까요?", "qa", q="빚이 위험하기만 하다면\n은행은 [어떻게] 돈을 벌까?")
S("은행은 예금으로 돈을 모아서 대출로 빌려주고, 그 이자 차이로 돈을 법니다. 이걸 예대마진이라고 해요.", "flow", headline="은행이 돈을 버는 [구조]", badge="예시",
  nodes=[dict(t="예금 이자 3%", s="맡긴 사람에게 줌", c="blue", icon="1"), dict(t="대출 이자 5%", s="빌린 사람에게 받음", c="red", icon="2"), dict(t="차이 2%", s="예대마진", c="gold", icon="=")])
S("빚이 없으면 은행도 없고, 첫 번째 이야기에서 봤듯이 대출이 없으면 돈도 늘어나지 않습니다. 현대 경제는 사실 빚으로 돌아가는 기계예요.", "quote", lines=["현대 경제는", "[빚으로 돌아가는] 기계"], size=130)
S("기업은 빚을 내서 공장을 짓고, 정부는 빚을 내서 도로를 깔고, 사람들은 빚을 내서 집을 삽니다. 그 돈이 돌고 돌아 누군가의 월급이 되죠.", "flow", headline="빚이 [돌고 도는] 길",
  nodes=[dict(t="기업·정부·가계의 빚", s="", c="blue", icon="1"), dict(t="공장·도로·집", s="", c="gold", icon="2"), dict(t="누군가의 월급", s="", c="red", icon="3")])
S("그러니 빚 자체가 선하거나 악한 게 아닙니다. 어떻게 쓰느냐에 따라 독이 되기도 하고 득이 되기도 하죠.", "scale", headline="빚은 [독]도 되고 [득]도 된다",
  left=dict(t="독", s="갚지 못할 빚", c="blue"), right=dict(t="득", s="불려 주는 빚", c="red"), tilt=0)
S("오늘은 이 빚을 다섯 가지 질문으로 뜯어보겠습니다.", "check", headline="빚에 대한 [다섯 가지 질문]",
  items=[dict(t="좋은 빚과 [나쁜 빚]은 어떻게 다를까", c="gold", no="1"), dict(t="빚의 무게를 [시간]은 어떻게 바꿀까", c="blue", no="2"), dict(t="[얼마까지] 빌려도 될까", c="red", no="3"), dict(t="[어떻게] 빌리고 갚을까", c="gold", no="4"), dict(t="빚이 [경제 전체]를 흔드는 순간", c="blue", no="5")])
S("첫 번째 질문, 좋은 빚과 나쁜 빚은 어떻게 다를까요? 기준은 하나입니다. 그 빚이 미래에 돈을 벌어다 주느냐.", "kpi", kicker="질문 1", big="좋은 빚 vs 나쁜 빚", color="gold", unit="미래에 돈을 벌어다 주는가?", size=170)
S("내 실력을 키우는 교육, 이자보다 더 벌 가능성이 높은 사업, 오래 살 집처럼 시간이 지날수록 가치를 만들어 내는 데 쓴 빚은 좋은 빚에 가깝습니다.", "compare", headline="[좋은 빚]과 [나쁜 빚]",
  left=dict(title="좋은 빚에 가까움", c="red", rows=["실력을 키우는 교육", "수익이 나는 사업·자산"]), right=dict(title="나쁜 빚에 가까움", c="blue", rows=["사라지는 소비", "고금리 카드·현금서비스"]))
S("반대로 여행, 명품, 할부로 산 최신 휴대폰처럼 쓰고 나면 사라지는 데 쓴 빚은, 이자만 남깁니다.", "story", scene="shop_window", relabel={">연말 보고서<": ">할부 12개월<"})
S("특히 조심해야 할 게 카드 리볼빙과 현금서비스입니다. 금리가 연 10%대 중후반까지 올라가는 경우가 많거든요.", "kpi", kicker="가장 비싼 빚", big="리볼빙 · 현금서비스", color="blue", unit="연 10%대 중후반 금리가 흔하다", size=170)
S("리볼빙은 이번 달 카드값의 일부만 내고 나머지를 다음 달로 넘기는 건데, 넘긴 돈에 높은 이자가 붙고 그게 또 넘어가면서 눈덩이처럼 불어납니다.", "chart", headline="리볼빙의 [눈덩이]", badge=EX,
  lines=[dict(name="갚아야 할 돈", color="blue", pts=[.2, .26, .33, .42, .52, .64, .78], end="눈덩이")])
S("빚을 고를 때 가장 쉬운 판단법을 하나 드릴게요. 이 빚의 이자율보다, 이 돈으로 버는 수익률이 확실히 높은가.", "quote", lines=["빌린 돈의 [이자율]보다", "버는 [수익률]이 확실히 높은가"], size=110)
S("대출 금리가 5%인데 그 돈으로 3%짜리 예금을 하면 손해고, 7%를 꾸준히 버는 사업에 쓰면 이득이죠. 단, 그 7%가 확실해야 합니다.", "compare", headline="이자율 5%로 빌렸다면",
  left=dict(title="3% 예금에 넣으면", c="blue", rows=["−2% 손해"]), right=dict(title="7% 사업에 쓰면", c="red", rows=["+2% 이득", "단, 확실해야"]))
S("두 번째 질문, 시간은 빚의 무게를 어떻게 바꿀까요? 여기서 첫 번째 이야기의 통화량 이야기가 다시 등장합니다.", "kpi", kicker="질문 2", big="시간과 빚", color="blue", unit="돈의 가치가 줄어들면, 빚의 무게도 줄어든다", size=220)
S("돈의 가치가 해마다 조금씩 떨어진다고 했죠. 그런데 빚은 숫자가 정해져 있습니다. 1억 원을 빌렸으면 10년 뒤에도 갚을 돈은 1억 원이에요.", "flow", headline="빚은 [숫자가 고정]돼 있다",
  nodes=[dict(t="1억 원 빌림", s="", c="blue", icon="1"), dict(t="10년 동안 물가 상승", s="", c="gold", icon="2"), dict(t="갚을 돈은 그대로 1억", s="", c="red", icon="3")])
S("물가가 해마다 3%씩 오른다면, 10년 뒤의 1억 원은 지금 돈으로 치면 7천4백만 원 정도의 가치밖에 안 됩니다. 빚의 실제 무게가 4분의 1 넘게 가벼워진 거죠.", "dual", headline="물가 3%로 10년이면 [빚이 가벼워진다]", badge="계산 예시",
  panels=[dict(title="빚의 숫자", color="blue", pts=[.6, .6], tag="1억 원", note="그대로"), dict(title="빚의 실제 무게", color="red", pts=[.6, .44], tag="약 7,400만 원", note="지금 돈 가치로")])
S("그래서 인플레이션은 돈을 가진 사람에게는 나쁘고, 빚을 진 사람에게는 상대적으로 유리하다는 말이 있습니다. 물가가 빚을 조용히 녹여 주거든요.", "scale", headline="인플레이션의 [두 얼굴]",
  left=dict(t="현금을 가진 사람", s="불리", c="blue"), right=dict(t="빚을 진 사람", s="상대적으로 유리", c="red"), tilt=10)
S("이게 바로 많은 사람들이 대출을 끼고 집을 사는 경제학적 이유 중 하나입니다. 집값은 돈의 양을 따라 오르고, 빚의 무게는 물가에 녹으니까요.", "story", scene="goose")
S("하지만 여기엔 큰 함정이 있습니다. 물가가 빚을 녹이려면, 그동안 내 월급도 같이 올라야 하고, 그동안 이자를 계속 낼 수 있어야 합니다.", "quote", lines=["빚이 녹으려면", "[월급도 오르고, 이자를 버텨야] 한다"], size=110)
S("월급이 안 오르거나, 일자리를 잃거나, 금리가 갑자기 오르면 시간은 내 편이 아니라 적이 됩니다. 녹기도 전에 무너지는 거죠.", "story", scene="bed_phone")
S("세 번째 질문, 얼마까지 빌려도 될까요? 가장 중요한 기준은 집값이 아니라 소득입니다.", "kpi", kicker="질문 3", big="얼마까지?", color="red", unit="기준은 집값이 아니라 소득", size=250)
S("정부도 이걸 기준으로 규제합니다. 1년에 갚는 모든 대출의 원금과 이자가 연 소득의 몇 퍼센트를 넘지 못하게 하는 거죠. 이게 네 번째 이야기에서 나온 디에스알입니다.", "flow", headline="DSR = 1년 원리금 ÷ [연 소득]",
  nodes=[dict(t="1년 동안 갚는 원금+이자", s="모든 대출 합계", c="blue", icon="1"), dict(t="÷ 연 소득", s="", c="gold", icon="÷"), dict(t="= DSR", s="은행권 규제 기준 40%", c="red", icon="=")])
S("은행권 규제 기준은 대략 40%입니다. 연봉 5천만 원이면 1년에 2천만 원, 한 달에 약 167만 원까지가 원리금 한도라는 뜻이죠.", "kpi", kicker="연봉 5천만 원 · DSR 40%라면 (계산 예시)", big="월 약 167만 원", color="gold", unit="모든 대출 원리금 한도", size=200)
S("그런데 규제 한도는 빌릴 수 있는 최대치일 뿐, 빌려도 괜찮은 금액이 아닙니다. 세금과 보험을 떼고 생활비까지 생각하면 훨씬 빠듯하거든요.", "compare", headline="[빌릴 수 있는 돈] ≠ [빌려도 되는 돈]",
  left=dict(title="규제 한도", c="blue", rows=["최대치", "연 소득의 40%"]), right=dict(title="편하게 갚을 수 있는 돈", c="red", rows=["훨씬 적다", "생활비·저축 고려"]))
S("많은 재무 전문가들은 월 원리금이 세후 월급의 30%를 넘지 않게 하라고 조언합니다. 금리가 오를 때를 대비한 여유까지 남겨 두라는 거죠.", "kpi", kicker="재무 상담의 경험칙", big="세후 월급의 30%", color="red", unit="월 원리금이 이 선을 넘지 않게", size=210)
S("여기에 꼭 하나 더 해 보셔야 할 계산이 있습니다. 금리가 2%포인트 오르면 내 이자가 얼마나 늘어나는지, 미리 계산해 보는 스트레스 테스트예요.", "story", scene="check_account")
S("변동금리로 3억 원을 빌렸는데 금리가 2%포인트 오르면, 이자만 1년에 6백만 원, 한 달에 50만 원이 늘어납니다. 이걸 버틸 수 있는지 미리 알아야 해요.", "flow", headline="[스트레스 테스트] · 금리 +2%p", badge="계산 예시 · 이자만",
  nodes=[dict(t="대출 3억 원", s="변동금리", c="blue", icon="1"), dict(t="금리 +2%p", s="", c="gold", icon="2"), dict(t="이자 월 +50만 원", s="연 +600만 원", c="red", icon="3")])
S("네 번째 질문, 어떻게 빌리고 어떻게 갚을까요? 먼저 금리 종류부터 보겠습니다. 세 번째 이야기에서 잠깐 나온 변동금리와 고정금리죠.", "compare", headline="질문 4 · [변동] vs [고정]",
  left=dict(title="변동금리", c="blue", rows=["처음엔 보통 더 낮음", "금리 오르면 부담 ↑"]), right=dict(title="고정금리", c="red", rows=["처음엔 보통 더 높음", "계획 세우기 쉬움"]))
S("금리가 앞으로 내려갈 것 같으면 변동이, 오를 것 같으면 고정이 유리합니다. 하지만 금리를 정확히 맞히는 건 전문가도 어렵다고 했죠.", "quote", lines=["금리를 맞히기보다", "[내가 버틸 수 있는 쪽]을 고르기"], size=110)
S("그래서 저는 이렇게 고르시라고 권합니다. 이자가 갑자기 늘면 생활이 흔들리는 분은 고정금리, 여유가 있고 일찍 갚을 계획이 있다면 변동금리를 검토하는 식으로요.", "check", headline="금리 종류 [고르는 법]",
  items=[dict(t="이자가 늘면 흔들린다 → [고정] 쪽", c="red"), dict(t="여유 있고 일찍 갚는다 → [변동] 검토", c="blue"), dict(t="섞는 [혼합형]도 있다", c="gold")])
S("갚는 방식도 세 가지가 있습니다. 매달 같은 금액을 내는 원리금균등, 원금을 똑같이 나눠 내는 원금균등, 이자만 내다가 마지막에 한꺼번에 갚는 만기일시.", "check", headline="갚는 방식 [세 가지]",
  items=[dict(t="[원리금균등] — 매달 같은 금액", c="gold", no="1"), dict(t="[원금균등] — 처음 많이, 점점 적게", c="blue", no="2"), dict(t="[만기일시] — 이자만 내다 한꺼번에", c="red", no="3")])
S("총이자는 원금균등이 가장 적고, 만기일시가 가장 많습니다. 원금을 빨리 줄일수록 이자가 붙는 돈이 줄어드니까요.", "chart", headline="총이자는 [원금을 빨리 줄일수록] 적다", badge=EX,
  lines=[dict(name="총이자", color="red", pts=[.3, .42, .75], end="")], marks=[dict(x=.0, text="원금균등", color="blue"), dict(x=.45, text="원리금균등", color="gold"), dict(x=.9, text="만기일시", color="red")])
S("대신 원금균등은 처음 몇 년의 부담이 크죠. 그래서 초반 현금 흐름이 빠듯하면 원리금균등이 현실적인 선택이 됩니다.", "story", scene="calendar_flip", relabel={">12월<": ">매달<", ">31<": ">25<", ">1월<": ">매달<", ">2<": ">25<"})
S("빚이 여러 개라면 무엇부터 갚아야 할까요? 경제적으로는 이자율이 가장 높은 것부터 갚는 게 정답입니다.", "kpi", kicker="빚이 여러 개라면", big="높은 이자부터", color="red", unit="이자율이 가장 높은 빚부터 갚는다", size=230)
S("카드론 15%, 신용대출 7%, 주택담보대출 4%가 있다면, 남는 돈은 카드론부터 갚는 거죠. 15% 빚을 갚는 건 15% 수익을 확실하게 버는 것과 같으니까요.", "check", headline="갚는 [순서] 예시",
  items=[dict(t="① 카드론 [15%] — 가장 먼저", c="red"), dict(t="② 신용대출 [7%]", c="gold"), dict(t="③ 주택담보대출 [4%] — 가장 나중", c="blue")])
S("심리적으로 지친 분이라면 금액이 작은 빚부터 하나씩 없애 나가는 방법도 있습니다. 하나를 완전히 끝냈다는 성취감이 다음 빚을 갚을 힘이 되거든요.", "quote", lines=["작은 빚부터 하나씩 없애는", "[성취감]도 힘이 된다"], size=110)
S("그리고 가장 중요한 건, 빚을 갚는 동안에도 비상금은 꼭 남겨 두는 겁니다. 비상금이 없으면 작은 사고에도 다시 비싼 빚을 지게 되거든요.", "story", scene="shield", relabel={">FCF<": ">비상금<"})
S("마지막 다섯 번째 질문, 빚이 경제 전체를 흔드는 순간은 언제일까요? 여기서 한 경제학자를 소개하고 싶습니다. 하이먼 민스키입니다.", "kpi", kicker="질문 5", big="하이먼 민스키", color="gold", unit="빚과 금융 위기를 연구한 경제학자", size=210)
S("민스키는 경제가 좋을 때 오히려 위기의 씨앗이 자란다고 말했습니다. 좋은 시절이 길어지면 사람들이 점점 대담하게 빚을 지기 때문이죠.", "quote", lines=["안정이", "[불안정]을 낳는다", "하이먼 민스키"], size=120)
S("민스키는 빚을 지는 사람을 세 단계로 나눴습니다. 이자도 원금도 갚을 수 있는 사람, 이자만 갚을 수 있는 사람, 이자조차 새 빚으로 갚는 사람.", "check", headline="민스키의 [세 단계]",
  items=[dict(t="[헤지 금융] — 이자도 원금도 갚는다", c="blue", no="1"), dict(t="[투기 금융] — 이자만 갚는다", c="gold", no="2"), dict(t="[폰지 금융] — 이자도 새 빚으로", c="red", no="3")])
S("좋은 시절이 이어지면 첫 번째 단계에 있던 사람들이 점점 두 번째, 세 번째 단계로 옮겨 갑니다. 자산 가격이 계속 오르니 빚을 더 내도 괜찮아 보이거든요.", "chart", headline="좋은 시절이 길어질수록 [위험한 빚]이 는다", badge=EX,
  lines=[dict(name="헤지", color="blue", pts=[.7, .6, .5, .4, .32], end=""), dict(name="폰지", color="red", pts=[.1, .15, .24, .36, .5], end="")])
S("그러다 자산 가격이 멈추거나 금리가 오르는 순간, 세 번째 단계 사람들이 한꺼번에 무너지고, 그들이 급하게 파는 자산이 가격을 더 떨어뜨립니다. 이 순간을 민스키 모멘트라고 부르죠.", "story", scene="hacked")
S("2008년 미국 금융위기가 바로 이랬습니다. 소득이 불안정한 사람들에게까지 집값이 오를 거라는 믿음으로 대출을 내줬다가, 집값이 꺾이자 한꺼번에 무너졌죠. 이건 다음 이야기에서 자세히 볼게요.", "timeline", headline="2008년, [민스키 모멘트]",
  events=[dict(when="2000년대 중반", t="느슨한 주택 대출", s="", c="gold"), dict(when="2006~07", t="집값 정점·하락", s="", c="blue"), dict(when="2008", t="금융위기", s="", c="red")])
S("그럼 우리나라 빚은 어떨까요? 가계부채는 2천조 원에 가까운 규모로, 경제 규모에 비해 세계적으로 높은 편입니다.", "kpi", kicker="우리나라 가계부채 (한국은행 가계신용)", big="2천조 원에 가까운", color="blue", unit="경제 규모 대비 세계적으로 높은 편", size=170)
S("특히 대부분이 집과 연결돼 있고, 변동금리 비중이 높은 편이라 금리가 오를 때 충격이 빠르게 전해집니다. 우리 경제가 금리에 유독 민감한 이유죠.", "flow", headline="한국 가계부채의 [특징]",
  nodes=[dict(t="집과 연결된 빚", s="주택담보·전세대출", c="gold", icon="1"), dict(t="변동금리 비중 높음", s="", c="blue", icon="2"), dict(t="금리에 민감", s="", c="red", icon="3")])
S("나라의 빚, 국가채무도 뉴스에 자주 나오죠. 나라 빚은 집안 빚과 조금 다릅니다. 나라는 세금을 걷을 수 있고, 갚는 기간이 아주 길거든요.", "compare", headline="나라 빚 vs [우리 집 빚]",
  left=dict(title="나라", c="gold", rows=["세금을 걷을 수 있음", "아주 길게 갚음"]), right=dict(title="가계", c="blue", rows=["월급이 끊기면 끝", "갚을 기간이 정해짐"]))
S("그래도 나라 빚이 너무 빨리 늘면 이자 부담이 커지고, 위기 때 쓸 여력이 줄어듭니다. 숫자 자체보다 늘어나는 속도와 무엇에 쓰느냐를 봐야 하는 건 가계와 같아요.", "quote", lines=["빚은 크기보다", "[속도]와 [쓰임새]를 봐라"], size=120)
S("조금 더 깊이, 생활 속에서 가장 흔한 빚 두 가지를 보겠습니다. 자동차 할부와 학자금 대출이에요.", "kpi", kicker="더 깊이 ⑤", big="생활 속 빚", color="gold", unit="자동차 할부와 학자금 대출", size=240)
S("자동차는 사는 순간부터 가치가 떨어지는 대표적인 자산입니다. 몇 년만 지나도 중고 가격이 크게 내려가죠. 그런데 할부 원금은 그대로 남습니다.", "dual", headline="차 값은 내려가고 [할부는 남는다]", badge=EX,
  panels=[dict(title="차의 가치", color="blue", pts=[.8, .35], tag="빠르게 하락", note="몇 년 사이"), dict(title="남은 할부", color="red", pts=[.8, .5], tag="천천히 감소", note="")])
S("그래서 차는 감당할 수 있는 가격으로, 할부 기간은 짧게 잡는 게 좋습니다. 차 값보다 할부가 더 남는 순간, 빚이 차보다 무거워지거든요.", "quote", lines=["차보다 할부가 더 남는 순간", "[빚이 차보다 무거워진다]"], size=110)
S("학자금 대출은 보통 좋은 빚에 가깝습니다. 내 실력과 미래 소득에 투자하는 빚이니까요. 대신 금리가 낮은 공공 대출을 쓰고, 소득이 생기면 계획적으로 갚는 게 핵심이죠.", "story", scene="report_read", relabel={">펀드 보고서<": ">학자금 상환 계획<"})
S("많이 받는 질문도 하나 있습니다. 빚을 먼저 갚을까요, 투자를 먼저 할까요? 답은 금리 비교에 있습니다.", "qa", q="빚 먼저 갚을까,\n[투자] 먼저 할까?")
S("빚의 금리가 투자로 기대할 수 있는 수익보다 높다면 빚부터, 낮다면 투자를 병행하는 걸 생각해 볼 수 있습니다. 확실한 금리와 불확실한 수익을 비교한다는 걸 잊지 마세요.", "compare", headline="[금리]로 정하는 순서",
  left=dict(title="빚 금리가 높다", c="red", rows=["예: 카드론·신용대출", "빚부터 갚기"]), right=dict(title="빚 금리가 낮다", c="blue", rows=["예: 저금리 장기 대출", "투자 병행 검토"]))
S("빚을 잘 쓰려면 꼭 관리해야 할 숫자가 하나 있습니다. 신용점수예요. 같은 돈을 빌려도 신용점수에 따라 금리가 몇 퍼센트포인트씩 달라지거든요.", "kpi", kicker="빚의 가격을 정하는 숫자", big="신용점수", color="gold", unit="같은 돈도 점수에 따라 금리가 달라진다", size=230)
S("신용점수를 지키는 방법은 생각보다 단순합니다. 연체하지 않기, 카드 한도를 꽉 채워 쓰지 않기, 그리고 리볼빙과 현금서비스를 멀리하기.", "check", headline="신용점수 [지키는 법]",
  items=[dict(t="[연체] 하지 않기 — 소액이라도", c="red", no="1"), dict(t="카드 한도 [꽉 채워] 쓰지 않기", c="gold", no="2"), dict(t="[리볼빙·현금서비스] 멀리하기", c="blue", no="3")])
S("많은 직장인이 쓰는 마이너스 통장도 조심할 점이 있습니다. 쓴 만큼만 이자를 내니 편하지만, 한도가 곧 내 돈처럼 느껴져서 어느새 빚이 굳어 버리기 쉽거든요.", "story", scene="bed_phone")
S("마이너스 통장은 정말 급할 때 쓰는 비상구로만 두시고, 쓰셨다면 갚는 날짜를 정해 두세요. 비상구가 거실이 되면 안 됩니다.", "quote", lines=["마이너스 통장은 [비상구]", "거실이 되면 안 된다"], size=120)
S("이미 빚 때문에 너무 힘든 분이라면 혼자 버티지 마세요. 신용회복위원회 같은 공공 기관에서 이자를 낮추거나 갚는 기간을 늘리는 채무조정 상담을 받을 수 있습니다.", "kpi", kicker="빚이 너무 힘들 때", big="채무조정 상담", color="blue", unit="신용회복위원회 등 공공 기관", size=220)
S("빚은 숨길수록 커집니다. 연체가 시작되기 전에 먼저 은행이나 상담 기관에 연락하는 사람이, 훨씬 좋은 조건으로 다시 일어섭니다.", "quote", lines=["빚은 숨길수록 커진다", "[먼저 연락하는 사람]이 빨리 일어선다"], size=110)
S("기업의 빚도 같은 원리입니다. 경기가 좋을 때 빚을 크게 늘린 회사는 금리가 오르면 이자에 짓눌리고, 빚이 적은 회사는 위기 때 오히려 경쟁자를 사들이죠. 주식을 고를 때 부채비율을 보는 이유입니다.", "compare", headline="기업도 [빚이 운명]을 가른다",
  left=dict(title="빚이 많은 회사", c="blue", rows=["금리 오르면 이자에 짓눌림"]), right=dict(title="빚이 적은 회사", c="red", rows=["위기 때 오히려 기회"]))
S("자주 받는 질문 하나 보고 정리할게요. 빚을 내서 주식에 투자해도 될까요?", "qa", q="빚을 내서\n[주식]에 투자해도 될까?")
S("두 번째 이야기에서 손실의 수학을 봤죠. 빚으로 투자하면 그 수학이 훨씬 가혹해집니다. 주가가 떨어져도 이자는 계속 나가고, 증권사 빚이라면 강제로 팔리는 반대매매까지 당할 수 있으니까요.", "flow", headline="빚투의 [가혹한 수학]",
  nodes=[dict(t="주가 하락", s="", c="blue", icon="1"), dict(t="이자는 계속", s="", c="gold", icon="2"), dict(t="반대매매 위험", s="바닥에서 강제 매도", c="red", icon="3")])
S("특히 가장 바닥에서 강제로 팔리면, 나중에 주가가 회복돼도 그 회복을 누릴 수가 없습니다. 장기투자의 가장 큰 무기인 기다림을 빚이 빼앗아 가는 거죠.", "quote", lines=["빚은 투자의 가장 큰 무기,", "[기다림]을 빼앗는다"], size=110)
S("그래서 투자용 빚은 정말 조심해야 합니다. 쓰더라도 잃어도 생활이 흔들리지 않는 아주 작은 규모로, 기한이 긴 빚으로만 생각해 보셔야 해요.", "story", scene="short_borrow", relabel={">주식<": ">빚<", ">빌려줌<": ">투자?<", ">떨어지면 이득<": ">조심!<"})
S("빚이 한 나라를 어디까지 몰아붙일 수 있는지 보여 준 사례가 있습니다. 2010년 그리스입니다.", "kpi", kicker="2010년", big="그리스 재정 위기", color="blue", unit="나라 빚이 감당할 수 없게 되자", size=220)
S("그리스는 유로화를 쓰게 되면서 독일 같은 나라와 비슷하게 싼 금리로 돈을 빌릴 수 있게 됐습니다. 그리고 그 싼 돈으로 나라 빚을 크게 늘렸죠.", "flow", headline="그리스의 [싼 빚]",
  nodes=[dict(t="유로화 가입", s="", c="gold", icon="1"), dict(t="싼 금리로 차입", s="", c="blue", icon="2"), dict(t="나라 빚 급증", s="", c="red", icon="3")])
S("그런데 2009년, 정부가 발표한 재정 적자 숫자가 실제보다 훨씬 작게 꾸며져 있었다는 게 드러납니다. 그 순간 투자자들의 믿음이 무너졌어요.", "story", scene="hacked")
S("그리스 국채 금리가 치솟았고, 그리스는 스스로 돈을 빌릴 수 없게 되어 결국 구제금융을 받았습니다. 그 대가로 연금과 월급이 깎이고, 실업률이 20%를 훌쩍 넘었죠.", "chart", headline="믿음이 무너지자 [치솟은 금리]", badge=EX,
  lines=[dict(name="그리스 국채 금리", color="red", pts=[.15, .16, .18, .3, .55, .85, .6], end="")])
S("그리스에는 우리나라처럼 환율을 움직여 충격을 흡수할 수단도 없었습니다. 유로화라는 남의 돈을 쓰고 있었으니까요. 그래서 고통이 고스란히 사람들의 월급과 일자리로 갔습니다.", "quote", lines=["환율이라는 [완충 장치]가 없을 때", "고통은 월급과 일자리로 간다"], size=110)
S("그리스의 교훈은 개인에게도 똑같습니다. 싸게 빌릴 수 있다고 많이 빌리면 안 되고, 숫자를 속이면 신뢰가 한순간에 무너진다는 것. 빚은 결국 믿음 위에 서 있습니다.", "check", headline="그리스의 [교훈]",
  items=[dict(t="싸게 빌릴 수 있다고 [많이 빌리지 마라]", c="red"), dict(t="숫자를 속이면 [신뢰]가 무너진다", c="blue"), dict(t="빚은 결국 [믿음] 위에 서 있다", c="gold")])
S("다섯 번째 이야기를 정리하겠습니다. 빚은 현대 경제를 돌리는 엔진이고, 그 자체로 선도 악도 아닙니다.", "check", headline="다섯 번째 이야기 정리 ①",
  items=[dict(t="빚은 [경제의 엔진]", c="gold"), dict(t="미래에 돈을 벌어 주면 [좋은 빚]", c="red"), dict(t="사라지는 소비·고금리는 [나쁜 빚]", c="blue")])
S("물가는 빚을 녹이지만 버틸 수 있을 때만 그렇고, 얼마를 빌릴지는 집값이 아니라 소득이 정하고, 갚을 때는 이자가 높은 것부터. 그리고 좋은 시절일수록 빚을 경계하세요.", "check", headline="다섯 번째 이야기 정리 ②",
  items=[dict(t="물가는 빚을 녹인다, [버틸 수 있다면]", c="gold"), dict(t="기준은 [소득], 월 원리금 30% 이하", c="red"), dict(t="[높은 이자]부터 갚기", c="blue"), dict(t="좋은 시절일수록 [빚을 경계]", c="red")])
S("빚에 대한 질문도 세 가지 더 받아 볼게요.", "quote", lines=["부채에 대해", "[자주 받는 질문 세 가지]"], size=130)
S("첫 번째 질문. 전세대출은 좋은 빚인가요, 나쁜 빚인가요? 월세보다 이자가 싸다면 주거비를 줄여 주는 빚이라 나쁘지 않습니다. 대신 보증금을 지키는 장치가 꼭 함께 있어야 해요.", "qa", q="전세대출은\n[좋은 빚]일까?")
S("두 번째 질문. 대출을 일찍 갚으면 수수료가 있던데, 그래도 갚는 게 나은가요? 중도상환 수수료와 앞으로 아낄 이자를 비교해 보시면 됩니다. 보통 몇 년이 지나면 수수료가 줄거나 없어져요.", "compare", headline="일찍 갚을까? [계산]으로",
  left=dict(title="중도상환 수수료", c="blue", rows=["지금 내야 할 돈"]), right=dict(title="아낄 이자", c="red", rows=["남은 기간 이자", "보통 이쪽이 더 큼"]))
S("세 번째 질문. 빚이 하나도 없는 게 가장 좋은 거 아닌가요? 마음은 가장 편하죠. 하지만 그 대신 집이나 사업처럼 시간이 걸리는 기회를 놓칠 수도 있습니다.", "qa", q="빚이 하나도 없는 게\n[최선]일까?")
S("중요한 건 빚이 있느냐 없느냐가 아니라, 내가 통제할 수 있느냐입니다. 금리가 올라도, 소득이 줄어도 버틸 수 있는 빚이라면 그건 도구가 됩니다.", "quote", lines=["빚이 있느냐가 아니라", "[통제할 수 있느냐]"], size=130)
S("민스키의 경고처럼, 빚이 쌓인 경제에 의심이 번지는 순간 진짜 위기가 옵니다. 다음 이야기는 경제 위기입니다.", "quote", lines=["빚이 쌓인 곳에 의심이 번질 때", "[진짜 위기]가 온다"], size=110)


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
