"""33편 경제 지식 2시간 완전정리 — 2부 (리스크). 8부로 나눠 만든 뒤 합친다.
사용: python3 projects/20261106-econ2h-p02/build.py plan | render [ids]
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
PJ = "projects/20261106-econ2h-p02"

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

# ═════════════ 2강 리스크 ═════════════
CH("2강", "리스크, 투자에서 [이기는] 법", "2강 · 리스크 — 투자에서 이기는 법", name="2강 리스크 — 투자에서 이기는 법")
S("두 번째 이야기는 리스크입니다. 앞에서 돈이 늘어나는 세상에서는 자산을 가져야 한다고 했죠.", "kpi", kicker="2강 · 오늘의 단어", big="리스크", color="blue", unit="결과가 내 예상과 달라질 가능성", size=240)
S("그런데 막상 투자를 시작하려고 하면, 다들 같은 질문을 합니다.", "story", scene="confused_news", relabel={">외국인 순매도 · PER 부담<": ">뭘 사야 하지?<"})
S("주식은 어떤 종목을 사야 하나요? 부동산은 지금 사도 되나요?", "qa", q="주식은 [무엇을]?\n부동산은 [언제]?")
S("재미있는 건, 이 두 질문을 거꾸로 해야 한다는 겁니다.", "quote", lines=["이 두 질문은", "[거꾸로] 해야 합니다"], size=130)
S("주식은 무엇을 사느냐보다 언제 사고파느냐가 더 중요하고, 부동산은 언제보다 무엇을 사느냐가 더 중요하거든요.", "compare", headline="질문을 [거꾸로]",
  left=dict(title="주식", c="red", rows=["무엇보다 '언제'", "시장 전체가 같이 움직임"]), right=dict(title="부동산", c="blue", rows=["언제보다 '무엇'", "입지가 수십 년을 좌우"]))
S("왜 그럴까요? 주식은 시장이 크게 흔들릴 때 좋은 종목, 나쁜 종목 할 것 없이 같이 떨어집니다.", "chart", headline="폭락장에서는 [다 같이] 떨어진다", badge=EX,
  lines=[dict(name="좋은 종목", color="red", pts=[.6, .62, .64, .4, .45, .55, .68], end=""), dict(name="나쁜 종목", color="blue", pts=[.5, .52, .53, .28, .3, .33, .35], end="")], marks=[dict(x=.45, text="시장 전체 폭락", color="blue")])
S("2008년 금융위기나 2020년 코로나 폭락 때를 떠올려 보세요. 아무리 좋은 회사도 몇 주 사이에 30%, 40%씩 빠졌습니다.", "story", scene="bed_phone")
S("그래서 주식은 종목을 고르는 실력만큼, 시장 전체가 비쌀 때 덜 사고 쌀 때 더 사는 감각이 중요합니다.", "scale", headline="주식: [시장의 온도]를 읽어라",
  left=dict(t="시장이 쌀 때", s="더 산다", c="red"), right=dict(t="시장이 비쌀 때", s="덜 산다", c="blue"), tilt=8)
S("반대로 부동산은 하나하나가 완전히 다른 물건입니다. 같은 동네라도 역에서 몇 분 거리냐, 학교가 어디냐에 따라 가격이 완전히 달라지죠.", "story", scene="empty_lot", relabel={">입주 2032~<": ">역세권?<"})
S("그리고 부동산은 한번 사면 오래 갖고 있는 경우가 많습니다. 사고팔 때 세금과 비용도 크고요.", "kpi", kicker="부동산의 특징", big="오래 보유", color="blue", unit="거래 비용·세금이 커서 자주 못 사고판다", size=220)
S("오래 갖고 있을 물건이라면, 사는 시점의 작은 차이보다 무엇을 샀느냐가 수십 년의 결과를 바꿉니다.", "quote", lines=["오래 갖고 있을 물건이라면", "[무엇을] 샀느냐가 결과를 바꾼다"], size=110)
S("자, 이제 리스크 이야기로 들어가 볼게요. 투자에서 흔히 하는 말이 있습니다. 하이 리스크, 하이 리턴.", "kpi", kicker="투자의 오래된 속설", big="하이 리스크 하이 리턴", color="red", unit="위험이 클수록 수익도 크다?", size=150)
S("위험을 많이 질수록 돈을 많이 번다. 반은 맞고 반은 틀린 말입니다.", "quote", lines=["위험을 많이 질수록 많이 번다", "[반은 맞고, 반은 틀리다]"], size=110)
S("맞는 부분은, 시장 전체로 보면 위험한 자산일수록 평균 수익률이 높다는 겁니다. 예금보다 채권, 채권보다 주식의 평균 수익률이 높죠.", "chart", headline="위험할수록 [평균] 수익이 높다", badge=EX,
  lines=[dict(name="평균 수익률", color="gold", pts=[.15, .3, .5, .75], end="주식")], marks=[dict(x=.0, text="예금", color="blue"), dict(x=.33, text="채권", color="gold"), dict(x=.66, text="주식", color="red")])
S("위험을 감수하는 사람에게 시장이 주는 보상, 이걸 위험 프리미엄이라고 부릅니다.", "kpi", kicker="위험을 지는 대가", big="위험 프리미엄", color="gold", unit="불확실함을 견딘 사람이 받는 추가 수익", size=200)
S("틀린 부분은, 나 한 사람에게 위험이 크다는 건 결국 크게 잃을 수도 있다는 뜻이라는 겁니다. 평균은 높아도, 내가 그 평균을 누린다는 보장은 없어요.", "story", scene="hacked")
S("그래서 저는 이렇게 말하고 싶습니다. 리스크는 지는 게 아니라 줄이는 겁니다. 같은 수익이라면, 위험은 작을수록 좋습니다.", "quote", lines=["리스크는 지는 게 아니라", "[줄이는] 것"], size=130)
S("왜 이렇게까지 위험을 줄이라고 할까요? 손실의 수학이 우리 편이 아니기 때문입니다.", "qa", q="왜 위험을\n[줄여야] 할까?")
S("100만 원이 50% 떨어지면 50만 원이 됩니다. 그럼 다시 100만 원이 되려면 몇 퍼센트가 올라야 할까요?", "flow", headline="손실의 [수학]", badge="계산 예시",
  nodes=[dict(t="100만 원", s="", c="gold", icon="1"), dict(t="−50% → 50만 원", s="", c="blue", icon="2"), dict(t="원금까지 몇 %?", s="", c="red", icon="?")])
S("50%가 아니라 100%입니다. 두 배가 돼야 겨우 본전이죠.", "kpi", kicker="−50% 손실을 메우려면", big="+100%", color="red", unit="두 배가 돼야 겨우 본전", size=260)
S("10% 손실은 11%만 오르면 회복되지만, 30%는 43%, 50%는 100%, 80%는 무려 400%가 올라야 합니다.", "check", headline="손실별 [본전까지] 필요한 상승",
  items=[dict(t="−10% → [+11%]", c="gold"), dict(t="−30% → [+43%]", c="gold"), dict(t="−50% → [+100%]", c="red"), dict(t="−80% → [+400%]", c="red")])
S("손실이 클수록 회복은 기하급수적으로 어려워집니다. 그래서 큰 손실 한 번을 피하는 게, 큰 수익 한 번보다 중요할 때가 많습니다.", "chart", headline="손실이 클수록 회복은 [가파르게] 어렵다", badge="계산값",
  lines=[dict(name="본전까지 필요한 상승률", color="red", pts=[.05, .1, .17, .27, .42, .9], end="")])
S("워런 버핏의 유명한 말이 있죠. 첫 번째 원칙, 돈을 잃지 마라. 두 번째 원칙, 첫 번째 원칙을 잊지 마라.", "quote", lines=["원칙 1. 돈을 잃지 마라", "원칙 2. [원칙 1을 잊지 마라]", "워런 버핏"], size=100)
S("그럼 위험은 어떻게 줄일까요? 크게 세 가지 방법이 있습니다. 나눠 담기, 시간 나누기, 그리고 오래 기다리기.", "check", headline="위험을 줄이는 [세 가지 방법]",
  items=[dict(t="[나눠 담기] — 분산투자", c="gold", no="1"), dict(t="[시간 나누기] — 적립식 투자", c="blue", no="2"), dict(t="[오래 기다리기] — 장기투자", c="red", no="3")])
S("첫 번째, 나눠 담기입니다. 계란을 한 바구니에 담지 말라는 말, 많이 들어 보셨죠.", "kpi", kicker="방법 1", big="분산투자", color="gold", unit="계란을 한 바구니에 담지 마라", size=230)
S("그런데 분산의 핵심은 개수가 아니라 방향입니다. 같은 방향으로 움직이는 걸 열 개 사면, 사실상 한 개를 산 것과 비슷하거든요.", "compare", headline="분산의 핵심은 [개수]가 아니라 [방향]",
  left=dict(title="가짜 분산", c="blue", rows=["반도체 종목만 10개", "같이 오르고 같이 내림"]), right=dict(title="진짜 분산", c="red", rows=["주식 + 채권 + 현금", "서로 다르게 움직임"]))
S("경제학에서는 이걸 상관관계라고 부릅니다. 함께 움직이는 정도죠. 서로 덜 닮은 자산을 섞을수록 전체의 흔들림이 줄어듭니다.", "dual", headline="덜 닮은 자산을 섞으면 [흔들림이 준다]", badge=EX,
  panels=[dict(title="한 자산만", color="blue", pts=[.5, .4], tag="크게 출렁", note="같이 움직이는 자산 모음"), dict(title="덜 닮은 자산 섞기", color="red", pts=[.5, .55], tag="완만", note="서로 흔들림을 상쇄")])
S("이 생각을 수학으로 정리한 사람이 해리 마코위츠입니다. 1952년에 발표한 이론으로 나중에 노벨 경제학상을 받았죠.", "timeline", headline="분산투자를 [이론]으로 만든 사람",
  events=[dict(when="1952", t="마코위츠 포트폴리오 이론", s="", c="gold"), dict(when="1990", t="노벨 경제학상", s="", c="red"), dict(when="지금", t="자산배분의 기본", s="", c="blue")])
S("마코위츠는 분산을 투자에서 유일한 공짜 점심이라고 표현했다고 알려져 있습니다. 수익은 크게 줄이지 않으면서 위험만 줄일 수 있으니까요.", "quote", lines=["분산은 투자에서", "유일한 [공짜 점심]"], size=120)
S("두 번째, 시간 나누기입니다. 한 번에 다 사지 않고, 매달 같은 금액씩 나눠서 사는 거죠.", "kpi", kicker="방법 2", big="적립식 투자", color="blue", unit="매달 같은 금액씩 나눠 사기", size=230)
S("예를 들어 매달 10만 원씩 산다고 해 볼게요. 가격이 만 원일 땐 10주를 사고, 5천 원으로 떨어지면 20주를 사게 됩니다.", "flow", headline="매달 10만 원씩 사면", badge="계산 예시",
  nodes=[dict(t="1만 원일 때", s="10주", c="gold", icon="1"), dict(t="5천 원일 때", s="20주", c="blue", icon="2"), dict(t="평균 단가 약 6,667원", s="30주에 20만 원", c="red", icon="=")])
S("가격이 쌀 때 자동으로 더 많이 사게 되니까, 평균 매수 가격이 내려갑니다. 무엇보다 언제 사야 하나 고민하지 않아도 되죠.", "story", scene="calendar_flip", relabel={">12월<": ">매달<", ">31<": ">10<", ">1월<": ">매달<", ">2<": ">10<"})
S("타이밍을 맞추려는 사람은 대부분 틀립니다. 전문가도 마찬가지예요. 시간을 나누는 건 내가 틀릴 수 있다는 걸 인정하는 겸손한 방법입니다.", "quote", lines=["시간을 나누는 건", "내가 [틀릴 수 있다]는 걸", "인정하는 방법"], size=100)
S("분산이 좋은 건 알겠는데, 주식 수십 개를 어떻게 다 사냐고요? 그래서 나온 게 인덱스 펀드와 이티에프입니다.", "kpi", kicker="분산을 한 번에", big="인덱스 펀드 · ETF", color="gold", unit="시장 전체를 통째로 담은 바구니", size=180)
S("코스피 200 같은 지수를 그대로 따라가는 상품을 하나 사면, 그 안에 든 수백 개 기업에 한 번에 나눠 투자하는 효과가 납니다.", "flow", headline="상품 하나로 [수백 개 기업]", 
  nodes=[dict(t="지수 추종 상품 1개", s="", c="gold", icon="1"), dict(t="안에 든 기업 수백 개", s="", c="blue", icon="2"), dict(t="자동 분산", s="수수료도 낮은 편", c="red", icon="3")])
S("미국의 전설적인 투자자 존 보글이 이 방식을 대중에게 퍼뜨렸습니다. 건초 더미에서 바늘을 찾지 말고, 건초 더미를 통째로 사라는 말로 유명하죠.", "quote", lines=["바늘을 찾지 말고", "[건초 더미를 통째로] 사라", "존 보글"], size=110)
S("물론 시장 전체가 떨어질 때는 같이 떨어집니다. 그래서 주식만이 아니라 다른 종류의 자산도 섞는 거죠. 대표적인 게 채권입니다.", "kpi", kicker="주식의 짝꿍", big="채권", color="blue", unit="정해진 이자를 받고 만기에 원금을 돌려받는 증서", size=230)
S("채권은 나라나 회사에 돈을 빌려주고 받는 차용증입니다. 정해진 이자가 나오고, 만기가 되면 원금을 돌려받죠.", "story", scene="pizza_share", relabel={">회사<": ">채권<", ">1주<": ">이자<"})
S("경기가 나빠져 주가가 떨어질 때, 금리가 내려가면서 채권 가격은 오르는 경우가 많았습니다. 그래서 주식의 충격을 덜어 주는 쿠션 역할을 해 왔죠.", "dual", headline="주식이 아플 때 [채권이 받쳐 주던] 경향", badge=EX,
  panels=[dict(title="주식", color="blue", pts=[.7, .35], tag="하락", note="경기 둔화 때"), dict(title="채권", color="red", pts=[.4, .6], tag="상승", note="금리 하락 때")])
S("단, 늘 그런 건 아닙니다. 2022년처럼 물가가 치솟아 금리가 빠르게 오를 때는 주식과 채권이 같이 떨어지기도 했어요.", "kpi", kicker="예외도 있다", big="2022년", color="blue", unit="금리 급등에 주식·채권 동반 하락", size=250)
S("분산은 위험을 없애는 마법이 아니라, 줄이는 도구라는 걸 기억해 두시면 됩니다.", "quote", lines=["분산은 위험을 없애는 마법이 아니라", "[줄이는 도구]"], size=110)
S("세 번째, 오래 기다리기입니다. 주식 시장은 하루하루는 롤러코스터지만, 길게 보면 오르는 방향으로 움직여 왔습니다.", "chart", headline="하루는 롤러코스터, [길게 보면] 오르막", badge=EX,
  lines=[dict(name="주가 지수", color="red", pts=[.2, .3, .22, .38, .3, .45, .35, .55, .5, .68, .6, .78], end="장기 상승")])
S("기업은 해마다 돈을 벌고, 그 이익이 쌓이고, 돈의 양도 늘어나니까요. 첫 번째 이야기에서 본 그 흐름입니다.", "flow", headline="길게 보면 오르는 [이유]",
  nodes=[dict(t="기업 이익 증가", s="", c="red", icon="1"), dict(t="이익이 쌓임", s="", c="gold", icon="2"), dict(t="통화량 증가", s="1강", c="blue", icon="3")])
S("보유 기간이 길어질수록 손실을 볼 확률은 줄어든다는 게 여러 연구에서 나타난 경향입니다. 하루는 동전 던지기에 가깝지만, 10년, 20년은 다르죠.", "dual", headline="오래 들고 있을수록 [손실 확률]은 준다", badge=EX,
  panels=[dict(title="하루 보유", color="blue", pts=[.5, .5], tag="반반", note="동전 던지기에 가까움"), dict(title="20년 보유", color="red", pts=[.5, .2], tag="손실 확률 낮음", note="과거 미국 시장 경향")])
S("단, 조건이 있습니다. 오래 기다릴 수 있는 돈이어야 해요. 6개월 뒤 전세금으로 써야 할 돈이라면 장기투자가 아니라 도박이 됩니다.", "kpi", kicker="장기투자의 조건", big="기다릴 수 있는 돈", color="blue", unit="곧 써야 할 돈은 투자하지 않는다", size=190)
S("그리고 개별 기업은 망할 수 있습니다. 시장 전체는 오르막이어도, 한 회사는 사라질 수 있죠. 그래서 장기투자와 분산은 짝꿍입니다.", "story", scene="two_giants", relabel={">삼성전자<": ">A사<", ">SK하이닉스<": ">B사<"})
S("이제 포트폴리오 이야기를 해 볼게요. 포트폴리오는 내 돈을 어디에, 얼마씩 나눠 두었는지 보여 주는 지도입니다.", "kpi", kicker="내 돈의 지도", big="포트폴리오", color="gold", unit="어디에, 얼마씩 나눠 두었나", size=230)
S("가장 기본적인 지도는 세 칸입니다. 안전한 칸, 불리는 칸, 그리고 바로 쓸 칸.", "check", headline="가장 기본적인 [세 칸]",
  items=[dict(t="[바로 쓸 칸] — 비상금·생활비", c="gold", no="1"), dict(t="[안전한 칸] — 예금·채권", c="blue", no="2"), dict(t="[불리는 칸] — 주식·실물 자산", c="red", no="3")])
S("비율은 사람마다 다릅니다. 나이, 소득이 얼마나 안정적인지, 그리고 얼마나 떨어져도 잠을 잘 수 있는지에 따라 달라지죠.", "story", scene="bed_phone")
S("여기서 아주 현실적인 기준 하나를 드릴게요. 내 투자금이 반토막 났을 때 버틸 수 있는지, 미리 상상해 보는 겁니다.", "quote", lines=["반토막 났을 때", "[버틸 수 있는가]"], size=130)
S("천만 원을 투자했는데 오백만 원이 됐다. 그때 팔지 않고 기다릴 수 있다면 감당할 수 있는 위험이고, 잠이 안 올 것 같다면 너무 큰 위험입니다.", "compare", headline="1천만 원이 5백만 원이 된다면",
  left=dict(title="기다릴 수 있다", c="red", rows=["감당할 수 있는 위험"]), right=dict(title="잠이 안 온다", c="blue", rows=["너무 큰 위험", "비중을 줄이자"]))
S("나이에 따라 대략적인 출발점을 잡는 방법도 있습니다. 100에서 내 나이를 뺀 만큼을 주식 같은 위험 자산에 두라는 오래된 경험칙이죠.", "kpi", kicker="오래된 경험칙", big="100 − 나이", color="gold", unit="= 위험 자산 비중의 출발점", size=230)
S("서른 살이면 70%, 쉰 살이면 50%, 일흔 살이면 30% 정도가 되죠. 젊을수록 기다릴 시간이 많으니 위험을 조금 더 질 수 있다는 논리입니다.", "check", headline="100 − 나이 [예시]",
  items=[dict(t="30세 → 위험 자산 약 [70%]", c="red"), dict(t="50세 → 위험 자산 약 [50%]", c="gold"), dict(t="70세 → 위험 자산 약 [30%]", c="blue")])
S("어디까지나 출발점일 뿐입니다. 수명이 길어지면서 110이나 120에서 빼자는 사람도 있고, 소득이 불안정하면 더 낮춰야 하죠.", "story", scene="check_account")
S("위험이 너무 크면 사람은 가장 나쁜 순간에 팝니다. 바닥에서 공포에 팔고, 꼭대기에서 욕심에 사는 거죠. 이게 개인 투자자가 지는 가장 흔한 이유입니다.", "chart", headline="공포에 팔고, [욕심에] 산다", badge=EX,
  lines=[dict(name="주가", color="gold", pts=[.5, .7, .82, .6, .3, .25, .45, .65], end="")], marks=[dict(x=.28, text="욕심에 매수", color="red"), dict(x=.7, text="공포에 매도", color="blue")])
S("그래서 리스크 관리는 계산 문제이기도 하지만, 사실은 내 마음을 관리하는 문제이기도 합니다.", "quote", lines=["리스크 관리는", "[내 마음]을 관리하는 일"], size=130)
S("하나 더, 리밸런싱이라는 습관이 있습니다. 1년에 한두 번, 처음 정한 비율로 다시 맞춰 주는 거예요.", "kpi", kicker="1년에 한두 번", big="리밸런싱", color="gold", unit="처음 정한 비율로 되돌리기", size=230)
S("주식이 많이 올라 비중이 커졌으면 조금 팔아서 채권을 사고, 주식이 많이 떨어졌으면 채권을 팔아 주식을 사는 겁니다.", "flow", headline="리밸런싱은 [자동으로] 싸게 사고 비싸게 판다",
  nodes=[dict(t="주식 급등", s="비중 커짐", c="red", icon="1"), dict(t="조금 팔고", s="채권 매수", c="gold", icon="2"), dict(t="원래 비율", s="회복", c="blue", icon="="),])
S("감정이 아니라 규칙으로 비싸게 팔고 싸게 사게 되니까, 마음이 흔들릴 때 특히 힘을 발휘합니다.", "story", scene="shield", relabel={">FCF<": ">규칙<"})
S("요즘 많이들 하시는 레버리지 상품 이야기도 꼭 하고 싶습니다. 지수가 1% 오르면 2%, 3% 오르게 설계된 상품들이죠.", "kpi", kicker="꼭 알아야 할 함정", big="레버리지 ETF", color="red", unit="하루 수익률의 2배·3배를 따라가는 상품", size=200)
S("하루 기준으로 두 배라는 게 함정입니다. 지수가 하루 10% 오르고 다음 날 10% 내리는 걸 예로 들어 볼게요.", "qa", q="오르고 내리기를 반복하면\n[어떻게 될까?]")
S("지수는 100에서 110, 다시 99가 됩니다. 1% 빠졌죠. 두 배 상품은 100에서 120, 다시 96이 됩니다. 4%가 빠졌어요.", "compare", headline="+10% → −10%를 겪으면", 
  left=dict(title="지수", c="gold", rows=["100 → 110 → 99", "−1%"]), right=dict(title="2배 상품", c="blue", rows=["100 → 120 → 96", "−4%"]))
S("오르내림이 반복되는 장에서는 지수는 제자리인데 레버리지 상품만 계속 녹아내립니다. 이걸 변동성 끌림이라고 불러요.", "chart", headline="제자리 장에서 [녹아내리는] 레버리지", badge=EX,
  lines=[dict(name="지수", color="gold", pts=[.5, .56, .48, .55, .47, .54, .5], end="제자리"), dict(name="2배 상품", color="blue", pts=[.5, .6, .44, .55, .4, .5, .38], end="녹아내림")])
S("레버리지 상품은 방향과 타이밍을 정확히 맞혀야 하는 단기 도구입니다. 오래 묻어 두는 상품이 아니라는 것, 꼭 기억하세요.", "quote", lines=["레버리지는 [단기 도구]", "오래 묻어 두는 상품이 아니다"], size=110)
S("마지막으로 자주 받는 질문 하나. 그럼 한 종목에 몰빵해서 크게 번 사람들은 뭔가요?", "qa", q="몰빵해서 크게 번 사람은\n[뭔가요?]")
S("그 사람들은 눈에 잘 띕니다. 하지만 같은 방법으로 크게 잃은 사람들은 조용히 사라지죠. 우리는 살아남은 사람의 이야기만 듣게 됩니다.", "compare", headline="우리는 [살아남은 사람]만 본다",
  left=dict(title="눈에 띄는 쪽", c="red", rows=["몰빵으로 대박", "이야기가 퍼진다"]), right=dict(title="보이지 않는 쪽", c="blue", rows=["몰빵으로 쪽박", "조용히 사라진다"]))
S("이걸 생존 편향이라고 합니다. 성공담만 보고 따라 하면, 실제 확률보다 훨씬 쉬워 보이게 되죠.", "kpi", kicker="성공담의 함정", big="생존 편향", color="blue", unit="살아남은 이야기만 보인다", size=220)
S("마지막으로 제가 가장 권하고 싶은 습관이 있습니다. 투자 일지를 쓰는 거예요. 거창할 필요 없습니다.", "kpi", kicker="가장 권하는 습관", big="투자 일지", color="gold", unit="샀을 때와 팔 때, 이유를 한 줄씩", size=230)
S("살 때 왜 샀는지, 언제 팔 건지, 얼마까지 떨어지면 다시 생각할 건지를 딱 세 줄만 적어 두는 겁니다.", "check", headline="살 때 적는 [세 줄]",
  items=[dict(t="[왜] 샀나", c="gold", no="1"), dict(t="[언제] 팔 건가", c="blue", no="2"), dict(t="[얼마까지] 떨어지면 다시 생각할까", c="red", no="3")])
S("시장이 흔들릴 때 이 세 줄을 다시 읽어 보면, 공포에 휩쓸리지 않고 처음 내 생각으로 돌아올 수 있습니다. 미래의 나에게 보내는 편지 같은 거죠.", "story", scene="report_read", relabel={">펀드 보고서<": ">투자 일지<"})
S("조금 더 깊이 가 볼게요. 개인 투자자를 가장 많이 다치게 하는 건 시장이 아니라 나 자신이라는 연구들이 있습니다.", "kpi", kicker="더 깊이 ②", big="가장 큰 적은 나", color="blue", unit="과잉 확신과 잦은 매매", size=230)
S("미국의 한 유명한 연구는 증권 계좌 수만 개를 분석했는데, 가장 자주 사고판 사람들의 수익률이 시장 평균보다 크게 낮았습니다. 많이 움직일수록 덜 벌었던 거죠.", "chart", headline="자주 사고팔수록 [덜 벌었다]", badge="바버·오딘 연구 경향",
  lines=[dict(name="연 수익률", color="blue", pts=[.65, .6, .55, .48, .38], end="")], marks=[dict(x=.0, text="거의 안 사고팜", color="red"), dict(x=.88, text="가장 자주", color="blue")])
S("이유는 두 가지입니다. 자기가 남보다 잘 안다고 믿는 과잉 확신, 그리고 사고팔 때마다 나가는 수수료와 세금이죠.", "check", headline="잦은 매매가 지는 [두 가지 이유]",
  items=[dict(t="[과잉 확신] — 나는 남보다 잘 안다는 착각", c="blue", no="1"), dict(t="[거래 비용] — 수수료와 세금", c="red", no="2")])
S("수수료는 작아 보여도 복리로 쌓이면 무섭습니다. 1년에 7%를 버는 투자에서 수수료로 1%가 나간다면, 30년 뒤 내 돈은 수수료가 없을 때보다 4분의 1 정도가 줄어듭니다.", "dual", headline="수수료 1%의 [30년 복리]", badge="계산 예시 · 연 7% vs 6%",
  panels=[dict(title="수수료 없음 (연 7%)", color="red", pts=[.2, .85], tag="100", note="30년 뒤"), dict(title="수수료 1% (연 6%)", color="blue", pts=[.2, .65], tag="약 75", note="약 4분의 1 감소")])
S("그래서 같은 상품이라면 수수료가 낮은 걸 고르는 것만으로도 확실한 수익을 얻는 셈입니다. 시장 수익은 내가 정할 수 없지만, 비용은 내가 정할 수 있거든요.", "quote", lines=["수익은 내가 정할 수 없지만", "[비용]은 내가 정할 수 있다"], size=120)
S("변동성이라는 말도 자주 나오죠. 가격이 평균에서 얼마나 크게 출렁이는지를 나타내는 숫자입니다. 같은 수익률이라도 변동성이 작은 쪽이 마음 편하게 오래 들고 있을 수 있어요.", "chart", headline="같은 수익, [다른 출렁임]", badge=EX,
  lines=[dict(name="변동성 큼", color="blue", pts=[.4, .7, .3, .75, .35, .8, .6], end=""), dict(name="변동성 작음", color="red", pts=[.4, .45, .48, .52, .55, .58, .6], end="")])
S("한 가지 더, 위험에도 종류가 있습니다. 시장 전체의 위험과, 한 회사만의 위험이죠.", "compare", headline="위험의 [두 종류]",
  left=dict(title="시장 위험", c="blue", rows=["경기·금리·전쟁", "분산해도 남는다"]), right=dict(title="개별 위험", c="red", rows=["한 회사의 실수·사고", "분산하면 거의 사라진다"]))
S("한 회사의 공장에 불이 나거나 사장이 잘못된 결정을 하는 위험은, 여러 회사에 나눠 담으면 거의 사라집니다. 하지만 경기 침체나 금리 급등처럼 시장 전체를 흔드는 위험은 분산해도 남아요.", "chart", headline="종목 수를 늘리면 [줄어드는] 위험", badge=EX,
  lines=[dict(name="전체 위험", color="blue", pts=[.85, .6, .48, .42, .39, .37, .36], end="시장 위험만 남음")])
S("그래서 분산은 개별 위험을 없애는 도구이고, 시장 위험은 시간과 자산 배분으로 다뤄야 합니다. 도구마다 맡은 위험이 다른 거죠.", "quote", lines=["개별 위험은 [분산]으로", "시장 위험은 [시간과 배분]으로"], size=110)
S("시장 타이밍에 대해서도 재미있는 분석이 있습니다. 미국 주식 시장에 20년 동안 그대로 투자했을 때와, 그중 가장 많이 오른 날 열흘만 놓쳤을 때를 비교한 거예요.", "qa", q="가장 좋은 날 [열흘]만\n놓치면 어떻게 될까?")
S("자산운용사들의 분석을 보면, 가장 좋은 날 열흘만 놓쳐도 전체 수익이 절반 가까이로 줄어드는 경우가 많았습니다. 그리고 그 좋은 날들은 대부분 폭락 직후에 몰려 있었죠.", "dual", headline="좋은 날 [열흘]의 무게", badge="자산운용사 분석 경향 · 기간마다 다름",
  panels=[dict(title="계속 투자", color="red", pts=[.2, .85], tag="기준", note="20년 보유"), dict(title="좋은 날 10일 놓침", color="blue", pts=[.2, .45], tag="절반 가까이", note="수익 감소")])
S("무서워서 팔고 나간 사이에 가장 좋은 날이 와 버리는 겁니다. 시장에서 버티는 시간이, 시장을 맞히는 실력보다 중요하다는 말이 그래서 나왔어요.", "quote", lines=["시장을 [맞히는 것]보다", "시장에 [머무는 것]"], size=130)
S("그리고 의외로 많은 분이 놓치는 리스크 관리가 있습니다. 보험이에요. 큰 병이나 사고는 한 번에 자산을 무너뜨릴 수 있으니까요.", "kpi", kicker="놓치기 쉬운 리스크 관리", big="보험", color="gold", unit="한 번에 무너질 위험을 남에게 넘기는 장치", size=240)
S("보험의 원칙은 단순합니다. 자주 일어나는 작은 손실은 내 돈으로 감당하고, 드물지만 감당할 수 없는 큰 손실만 보험으로 막는 거죠. 보장이 겹치는 보험에 돈을 너무 많이 쓰고 있지 않은지도 한번 점검해 보세요.", "check", headline="보험의 [원칙]",
  items=[dict(t="작고 잦은 손실은 [내 돈으로]", c="gold"), dict(t="드물고 큰 손실만 [보험으로]", c="red"), dict(t="[겹치는 보장]은 정리하기", c="blue")])
S("리스크 이야기를 마치기 전에, 역사상 가장 똑똑한 사람 중 한 명이 투자에서 크게 실패한 이야기를 들려드릴게요. 아이작 뉴턴입니다.", "kpi", kicker="1720년 영국", big="뉴턴의 투자 실패", color="blue", unit="만유인력의 천재도 피하지 못한 것", size=210)
S("1720년 영국에서는 남해회사라는 회사의 주식이 폭등하고 있었습니다. 뉴턴은 일찍 이 주식을 사서 꽤 큰 이익을 내고 팔았어요. 여기까지는 성공이었죠.", "chart", headline="남해회사 주가, [1720년]", badge=EX,
  lines=[dict(name="남해회사 주가", color="red", pts=[.15, .2, .35, .6, .9, .5, .2], end="")], marks=[dict(x=.3, text="뉴턴 첫 매도", color="gold"), dict(x=.62, text="뉴턴 재매수", color="red")])
S("그런데 팔고 나서도 주가가 계속 오르고, 주변 사람들이 돈을 버는 걸 보자 참지 못하고 훨씬 높은 가격에 다시 큰돈을 넣었습니다. 그리고 얼마 뒤 거품이 터졌죠.", "story", scene="chase_buy")
S("뉴턴은 이때 재산의 상당 부분을 잃었다고 전해집니다. 그리고 이런 말을 남겼다고 하죠. 천체의 움직임은 계산할 수 있지만, 인간의 광기는 계산할 수 없다.", "quote", lines=["천체의 움직임은 계산할 수 있지만", "[인간의 광기]는 계산할 수 없다", "아이작 뉴턴 (전해지는 말)"], size=100)
S("뉴턴의 실패는 지능의 문제가 아니었습니다. 남들이 돈 버는 걸 보며 참지 못한 마음, 그리고 감당할 수 없을 만큼 크게 건 비중이 문제였죠. 오늘 이야기한 리스크의 함정이 다 들어 있습니다.", "check", headline="뉴턴이 빠진 [함정]",
  items=[dict(t="남들이 버는 걸 보고 [참지 못함]", c="red"), dict(t="[너무 높은 가격]에 재매수", c="gold"), dict(t="감당 못 할 만큼 [큰 비중]", c="blue")])
S("세상에서 가장 똑똑한 사람도 마음의 리스크는 피하지 못했습니다. 그러니 우리에게 필요한 건 더 높은 지능이 아니라, 미리 정해 둔 규칙이에요.", "quote", lines=["필요한 건 더 높은 지능이 아니라", "[미리 정해 둔 규칙]"], size=110)
S("두 번째 이야기를 정리하겠습니다. 주식은 언제를, 부동산은 무엇을 먼저 고민하세요.", "check", headline="2강 정리 ①",
  items=[dict(t="주식은 [언제], 부동산은 [무엇을]", c="gold"), dict(t="리스크는 지는 게 아니라 [줄이는] 것", c="red"), dict(t="큰 손실 한 번을 [피하는 게] 먼저", c="blue")])
S("그리고 위험은 나눠 담고, 시간을 나누고, 오래 기다리는 걸로 줄입니다. 감당할 수 있는 만큼만, 규칙대로.", "check", headline="2강 정리 ②",
  items=[dict(t="[나눠 담기] — 방향이 다른 자산", c="gold"), dict(t="[시간 나누기] — 매달 같은 금액", c="blue"), dict(t="[오래 기다리기] — 기다릴 수 있는 돈으로", c="red")])
S("여기서 잠깐, 시청자분들이 자주 물어보시는 질문 세 가지에 답하고 갈게요.", "quote", lines=["리스크에 대해", "[자주 받는 질문 세 가지]"], size=130)
S("첫 번째 질문. 적립식으로 사면 언제 시작해도 괜찮은가요? 시작 시점의 영향은 줄어들지만, 0이 되지는 않습니다.", "qa", q="적립식이면\n[언제] 시작해도 괜찮나?")
S("다만 꾸준히 오래 모을수록 시작 시점의 운이 결과에 미치는 영향은 점점 작아집니다. 그래서 언제 시작할까보다 얼마나 오래 이어 갈까가 더 중요한 질문이에요.", "quote", lines=["언제 시작할까보다", "[얼마나 오래 이어 갈까]"], size=120)
S("두 번째 질문. 분산하면 수익도 줄어드는 거 아닌가요? 맞습니다. 가장 많이 오른 하나만 샀을 때보다는 덜 법니다.", "qa", q="분산하면\n[수익도 줄어들지] 않나?")
S("하지만 어떤 게 가장 많이 오를지 미리 아는 사람은 없습니다. 분산은 최고의 결과를 포기하는 대신, 최악의 결과를 피하는 선택이에요. 오래 살아남는 사람이 결국 이깁니다.", "compare", headline="분산의 [거래]",
  left=dict(title="포기하는 것", c="blue", rows=["최고의 결과"]), right=dict(title="얻는 것", c="red", rows=["최악을 피함", "오래 살아남음"]))
S("세 번째 질문. 손절은 몇 퍼센트에서 해야 하나요? 정답 숫자는 없습니다. 다만 숫자보다 이유가 중요해요.", "qa", q="손절은\n[몇 퍼센트]에서?")
S("처음에 산 이유가 사라졌다면 1%만 떨어져도 파는 게 맞고, 이유가 그대로라면 30% 떨어져도 기다릴 수 있습니다. 그래서 투자 일지에 산 이유를 적어 두라고 한 거예요.", "check", headline="팔지 말지 [판단하는 법]",
  items=[dict(t="산 [이유]가 사라졌다 → 판다", c="blue"), dict(t="이유가 [그대로]다 → 기다릴 수 있다", c="red"), dict(t="잠이 안 온다 → [비중]을 줄인다", c="gold")])
S("그런데 내가 어떤 자산을 고르든, 그 가격을 밀고 당기는 보이지 않는 손이 있습니다. 바로 금리와 환율이죠.", "quote", lines=["모든 자산의 가격을 밀고 당기는", "[금리와 환율]"], size=110)


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
