"""33편 경제 지식 2시간 완전정리 — 8부 (선택). 8부로 나눠 만든 뒤 합친다.
사용: python3 projects/20261106-econ2h-p08/build.py plan | render [ids]
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
PJ = "projects/20261106-econ2h-p08"

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

# ═════════════ 8강 선택 ═════════════
CH("8강", "선택, 나는 [내 선택의 합]이다", "8강 · 선택 — 나는 내 선택의 합", name="8강 선택 — 나는 내 선택의 합이다")
S("마지막 여덟 번째 이야기는 선택입니다. 지금까지 돈, 위험, 금리, 집, 빚, 위기, 나라를 이야기했는데, 이 모든 걸 꿰뚫는 한 단어가 있어요.", "hub", center="선택", chips=[dict(t="통화량", c="gold"), dict(t="리스크", c="blue"), dict(t="금리·환율", c="red"), dict(t="부동산", c="gold"), dict(t="부채", c="blue"), dict(t="위기", c="red")])
S("경제학을 한 문장으로 말하면, 한정된 것으로 무엇을 할지 고르는 학문입니다. 돈도, 시간도, 체력도 다 한정돼 있으니까요.", "quote", lines=["경제학은", "[한정된 것]으로 무엇을 할지 고르는 학문"], size=110)
S("그래서 경제의 본질은 선택입니다. 무언가를 고른다는 건, 다른 무언가를 포기한다는 뜻이죠.", "kpi", kicker="8강 · 오늘의 단어", big="선택 = 포기", color="gold", unit="무언가를 고르면, 다른 무언가를 놓는다", size=230)
S("이렇게 포기한 것 중 가장 아까운 것의 가치를 기회비용이라고 합니다. 경제학에서 가장 중요한 개념 하나만 고르라면 저는 이걸 꼽겠어요.", "kpi", kicker="경제학에서 가장 중요한 개념", big="기회비용", color="red", unit="포기한 것 중 가장 아까운 것의 가치", size=240)
S("예를 들어 볼게요. 대학원에 2년 다니는 비용은 등록금만이 아닙니다. 그 2년 동안 일했으면 벌었을 월급이 진짜 큰 비용이죠.", "flow", headline="대학원 2년의 [진짜 비용]", badge="예시",
  nodes=[dict(t="등록금", s="눈에 보이는 비용", c="gold", icon="1"), dict(t="+ 못 번 월급 2년", s="눈에 안 보이는 비용", c="blue", icon="+"), dict(t="= 진짜 비용", s="기회비용 포함", c="red", icon="=")])
S("돈을 예금에 묶어 두는 것도, 집을 사는 것도, 아무것도 안 하는 것도 다 기회비용이 있습니다. 아무것도 안 하는 것도 선택이니까요.", "quote", lines=["아무것도 안 하는 것도", "[선택]이다"], size=140)
S("첫 번째 이야기를 떠올려 보세요. 돈이 해마다 7%씩 늘어나는 세상에서 현금만 쥐고 있는 것도, 사실은 큰 기회비용을 치르는 선택이었죠.", "story", scene="saving_32")
S("그럼 좋은 선택은 어떻게 할까요? 오늘은 네 가지 원칙을 말씀드리겠습니다.", "check", headline="좋은 선택의 [네 가지 원칙]",
  items=[dict(t="[게임의 본질]을 알아라", c="gold", no="1"), dict(t="[손실 회피]를 경계하라", c="blue", no="2"), dict(t="[51 대 49]에서는 되돌릴 수 있는지를 봐라", c="red", no="3"), dict(t="[작은 선택]이 복리로 쌓인다", c="gold", no="4")])
S("첫 번째 원칙, 게임의 본질을 아는 겁니다. 모든 게임에는 이기는 핵심이 하나 있어요. 축구는 골을 넣는 거고, 마라톤은 끝까지 달리는 거죠.", "kpi", kicker="원칙 1", big="게임의 본질", color="gold", unit="이 게임에서 이기는 핵심은 무엇인가", size=230)
S("그럼 투자라는 게임의 본질은 뭘까요? 저는 기다리는 것이라고 생각합니다.", "quote", lines=["투자라는 게임의 본질은", "[기다리는 것]"], size=140)
S("지금까지 본 것처럼, 길게 보면 돈의 양은 늘어나고, 기업은 성장하고, 좋은 자산의 가격은 그걸 따라 오릅니다. 이 흐름을 누리려면 시간이 필요하죠.", "chart", headline="흐름을 누리는 데 필요한 건 [시간]", badge=EX,
  lines=[dict(name="좋은 자산의 가격", color="red", pts=[.2, .28, .24, .36, .31, .45, .4, .55, .5, .66, .78], end="")])
S("그런데 많은 사람이 투자에서 실패하는 이유는 종목을 못 골라서가 아니라, 기다리지 못해서입니다. 오르면 빨리 팔고, 떨어지면 무서워서 팔죠.", "story", scene="cheer_sell")
S("워런 버핏이 이런 말을 했습니다. 주식 시장은 인내심 없는 사람의 돈을 인내심 있는 사람에게 옮기는 장치다.", "quote", lines=["주식 시장은 인내심 없는 사람의 돈을", "[인내심 있는 사람]에게 옮긴다", "워런 버핏"], size=100)
S("반대로 단타 매매라는 게임의 본질은 빠른 판단과 엄격한 규칙입니다. 자기가 어떤 게임을 하는지 모르고, 장기투자를 하면서 단타처럼 매일 계좌를 들여다보면 지치기만 하죠.", "compare", headline="[어떤 게임]을 하고 있나",
  left=dict(title="장기투자", c="red", rows=["본질: 기다림", "계좌는 가끔 본다"]), right=dict(title="단타 매매", c="blue", rows=["본질: 속도와 규칙", "하루 종일 본다"]))
S("이 원칙은 일에도 통합니다. 내 직업이라는 게임의 본질이 무엇인지 알면, 어디에 시간을 써야 할지가 선명해지거든요.", "story", scene="lightbulb", relabel={">외국인 순매도<": ">내 게임의 본질은?<", ">PER · 시가총액<": ">어디에 시간을 쓸까<"})
S("두 번째 원칙, 손실 회피를 경계하는 겁니다. 사람은 같은 크기라도 이익보다 손실을 훨씬 크게 느낍니다.", "kpi", kicker="원칙 2", big="손실 회피", color="blue", unit="같은 크기라도 손실이 더 아프다", size=240)
S("심리학자 대니얼 카너먼과 아모스 트버스키의 연구에 따르면, 100만 원을 잃는 아픔은 100만 원을 얻는 기쁨보다 대략 두 배 크게 느껴집니다.", "dual", headline="잃는 아픔은 [약 두 배]", badge="카너먼·트버스키 전망 이론",
  panels=[dict(title="100만 원 얻는 기쁨", color="red", pts=[.4, .6], tag="+1", note=""), dict(title="100만 원 잃는 아픔", color="blue", pts=[.6, .2], tag="약 −2", note="")])
S("이 본능이 투자에서 어떤 실수를 만들까요? 오른 주식은 빨리 팔아서 기쁨을 확정하고, 떨어진 주식은 손실을 확정하기 싫어서 계속 들고 있게 됩니다.", "compare", headline="손실 회피가 만드는 [실수]",
  left=dict(title="오른 주식", c="red", rows=["빨리 팔아 버림", "더 오를 기회를 놓침"]), right=dict(title="떨어진 주식", c="blue", rows=["계속 들고 있음", "손실이 커짐"]))
S("결과적으로 계좌에는 떨어진 종목만 남습니다. 이걸 처분 효과라고 하죠. 이상하게 내 계좌엔 물린 것만 남는 것 같다면, 기분 탓이 아닙니다.", "story", scene="check_account")
S("이걸 이기는 방법은 간단한 질문 하나입니다. 지금 이 주식을 갖고 있지 않다면, 오늘 이 가격에 새로 사겠는가?", "qa", q="지금 갖고 있지 않다면\n[오늘 새로 사겠는가?]")
S("새로 사지 않겠다면, 들고 있을 이유도 사실 없습니다. 내가 얼마에 샀는지는 시장이 전혀 신경 쓰지 않거든요. 이미 쓴 돈에 매달리는 걸 매몰비용의 함정이라고 합니다.", "kpi", kicker="이미 쓴 돈에 매달리지 마라", big="매몰비용의 함정", color="blue", unit="내가 산 가격은 시장이 신경 쓰지 않는다", size=210)
S("손실 회피는 인생의 선택에도 나타납니다. 지금 가진 걸 잃을까 봐 새로운 기회를 피하는 거죠. 잃을 것만 크게 보이고, 얻을 것은 작게 보이니까요.", "scale", headline="잃을 것은 크게, [얻을 것은 작게]",
  left=dict(t="잃을 것", s="두 배로 크게 느낌", c="blue"), right=dict(t="얻을 것", s="작게 느낌", c="red"), tilt=-12)
S("세 번째 원칙, 51 대 49의 갈림길에서 선택하는 법입니다. 인생의 중요한 선택은 대부분 정답이 뻔하지 않아요. 거의 반반이죠.", "kpi", kicker="원칙 3", big="51 대 49", color="red", unit="정답이 뻔하지 않은 갈림길", size=250)
S("이럴 때 많은 사람이 더 많은 정보를 모으면서 결정을 미룹니다. 그런데 51 대 49라는 건, 아무리 고민해도 크게 달라지지 않는다는 뜻이기도 해요.", "quote", lines=["51 대 49는", "[아무리 고민해도] 크게 달라지지 않는다"], size=110)
S("그래서 저는 이 질문을 먼저 해 보시라고 권합니다. 이 선택은 나중에 되돌릴 수 있는가?", "qa", q="이 선택은\n[되돌릴 수 있는가?]")
S("되돌릴 수 있는 선택이라면 빨리 해 보세요. 해 보고 아니면 돌아오면 됩니다. 이직 면접을 보는 것, 소액으로 투자를 시작해 보는 것처럼요.", "compare", headline="[되돌릴 수 있는] 선택 vs [되돌릴 수 없는] 선택",
  left=dict(title="되돌릴 수 있다", c="red", rows=["빨리 해 본다", "소액 투자·면접 보기"]), right=dict(title="되돌릴 수 없다", c="blue", rows=["천천히, 신중하게", "전 재산·큰 빚·건강"]))
S("반대로 되돌릴 수 없는 선택, 전 재산을 거는 투자나 감당하기 힘든 빚, 건강을 해치는 선택이라면 천천히, 아주 신중하게 하셔야 합니다. 두 번째 이야기의 큰 손실 한 번을 피하라는 말과 같죠.", "story", scene="veto_stamp", doc="전 재산 투자", stamp="신중히")
S("그리고 51 대 49에서 하나 더. 결과가 나빴다고 선택이 나빴던 건 아닙니다. 좋은 선택을 해도 운이 나쁠 수 있고, 나쁜 선택을 해도 운이 좋을 수 있어요.", "dual", headline="좋은 선택 ≠ [좋은 결과]", badge="개념",
  panels=[dict(title="좋은 선택", color="red", pts=[.5, .65], tag="대체로 좋은 결과", note="그래도 가끔은 나쁜 결과"), dict(title="나쁜 선택", color="blue", pts=[.5, .35], tag="대체로 나쁜 결과", note="그래도 가끔은 좋은 결과")])
S("그러니 결과가 아니라 과정을 평가하세요. 그때 내가 가진 정보로 합리적인 선택이었는가. 이걸 반복하면 길게 봤을 때 결과는 따라옵니다.", "quote", lines=["결과가 아니라", "[과정]을 평가하라"], size=140)
S("네 번째 원칙, 작은 선택이 복리로 쌓인다는 겁니다. 첫 번째 이야기에서 돈은 복리로 불어난다고 했죠. 선택도 똑같습니다.", "kpi", kicker="원칙 4", big="선택의 복리", color="gold", unit="작은 선택이 쌓여 큰 차이를 만든다", size=230)
S("매일 1%씩 나아지면 1년 뒤에는 약 37배가 되고, 매일 1%씩 나빠지면 1년 뒤에는 거의 0에 가까워진다는 계산이 있습니다. 물론 비유적인 계산이지만, 방향의 힘을 잘 보여 주죠.", "dual", headline="매일 1%의 [복리]", badge="계산 예시 · 비유",
  panels=[dict(title="매일 1% 나아지면", color="red", pts=[.2, .9], tag="1년 뒤 약 37배", note="1.01의 365제곱"), dict(title="매일 1% 나빠지면", color="blue", pts=[.6, .05], tag="1년 뒤 약 0.03", note="0.99의 365제곱")])
S("매달 10만 원을 투자하는 선택, 하루 30분 공부하는 선택, 충동구매를 한 번 참는 선택. 하나하나는 작아 보여도 10년, 20년이 지나면 완전히 다른 사람을 만듭니다.", "check", headline="복리로 쌓이는 [작은 선택들]",
  items=[dict(t="매달 [10만 원]이라도 투자하기", c="gold"), dict(t="하루 [30분] 공부하기", c="blue"), dict(t="[충동구매] 한 번 참기", c="red")])
S("그래서 이런 말이 있습니다. 당신은 당신이 한 선택의 총합이다. 지금의 나는 지난 선택들이 쌓인 결과이고, 10년 뒤의 나는 오늘부터의 선택이 쌓인 결과입니다.", "quote", lines=["당신은", "[당신이 한 선택의 총합]이다"], size=130)
S("조금 더 깊이, 돈과 행복의 관계를 보겠습니다. 돈이 많으면 더 행복할까요?", "qa", q="돈이 많으면\n[더 행복할까?]")
S("한때는 소득이 일정 수준을 넘으면 행복이 더 늘지 않는다는 연구가 유명했습니다. 그런데 이후 연구들은 대부분의 사람에게 소득이 늘수록 행복도 조금씩 계속 늘어난다는 걸 보여 줬어요.", "chart", headline="소득과 [행복]", badge="연구 경향 · 개념도",
  lines=[dict(name="행복감", color="red", pts=[.2, .38, .5, .58, .64, .69, .73], end="완만하게 증가")])
S("흥미로운 건 그 다음입니다. 같은 돈이라도 어떻게 쓰느냐에 따라 행복이 달라진다는 연구들이 있어요. 물건보다 경험, 그리고 시간을 사는 데 쓴 돈이 더 오래 행복을 준다는 거죠.", "compare", headline="같은 돈, [다른 행복]",
  left=dict(title="물건에 쓴 돈", c="blue", rows=["금방 익숙해짐"]), right=dict(title="경험·시간에 쓴 돈", c="red", rows=["더 오래 남는 행복"]))
S("결국 돈을 모으는 이유는 숫자 자체가 아니라, 내 시간을 내가 원하는 대로 쓸 수 있는 자유를 사기 위해서입니다. 재테크의 진짜 목표는 선택의 자유예요.", "quote", lines=["재테크의 진짜 목표는", "[선택의 자유]"], size=130)
S("시간도 돈처럼 한정된 자원입니다. 오히려 돈보다 더 귀하죠. 돈은 다시 벌 수 있지만 시간은 되돌릴 수 없으니까요. 시간의 기회비용까지 생각하는 것, 그게 가장 성숙한 선택입니다.", "story", scene="hourglass", relabel={">몇 년 뒤<": ">되돌릴 수 없음<"})
S("마지막으로 우리 선택을 흐리는 함정 두 가지를 더 알려 드릴게요. 확증 편향과 군중 심리입니다.", "compare", headline="선택을 흐리는 [두 가지 함정]",
  left=dict(title="확증 편향", c="blue", rows=["보고 싶은 것만 본다"]), right=dict(title="군중 심리", c="red", rows=["남들이 하니까 따라 한다"]))
S("확증 편향은 내가 이미 믿는 것을 뒷받침하는 정보만 눈에 들어오는 현상입니다. 주식을 산 뒤에는 좋은 뉴스만 보이고, 나쁜 뉴스는 별것 아닌 것처럼 느껴지죠.", "story", scene="confused_news", relabel={">외국인 순매도 · PER 부담<": ">좋은 뉴스만 보인다<"})
S("이걸 이기려면 일부러 반대 의견을 찾아 읽어 보세요. 내가 틀렸다면 그 이유가 뭘까를 스스로 묻는 습관이 큰 손실을 막아 줍니다.", "quote", lines=["내가 틀렸다면", "[그 이유는 무엇일까]"], size=130)
S("군중 심리는 요즘 말로 포모, 나만 뒤처질까 봐 두려운 마음입니다. 주변 사람이 다 돈을 벌었다는 이야기를 들으면 급하게 따라 사게 되죠. 그리고 그때가 대개 가장 비쌀 때입니다.", "story", scene="chase_buy")
S("기다리는 힘에 대한 유명한 실험도 있습니다. 마시멜로를 지금 하나 먹을지, 조금 기다렸다가 두 개를 먹을지 아이들에게 고르게 한 실험이죠.", "kpi", kicker="기다림에 대한 유명한 실험", big="마시멜로 실험", color="gold", unit="지금 하나, 기다리면 둘", size=230)
S("처음 연구에서는 기다린 아이들이 나중에 더 좋은 결과를 얻었다고 알려졌지만, 뒤의 연구들은 가정 환경 같은 다른 요인의 영향도 크다는 걸 보여 줬습니다. 의지만의 문제는 아니라는 거죠.", "compare", headline="마시멜로 실험, [다시 보기]",
  left=dict(title="처음 연구", c="gold", rows=["기다린 아이들이 더 좋은 결과"]), right=dict(title="뒤의 연구들", c="blue", rows=["환경의 영향도 크다", "의지만의 문제가 아니다"]))
S("그래서 저는 의지보다 환경을 바꾸라고 권합니다. 월급날 자동으로 투자 계좌로 돈이 빠져나가게 해 두면, 매번 참을 필요가 없죠. 좋은 선택을 자동으로 만드는 겁니다.", "flow", headline="의지보다 [자동화]",
  nodes=[dict(t="월급날", s="", c="gold", icon="1"), dict(t="자동 이체", s="투자·저축 계좌", c="blue", icon="2"), dict(t="참을 필요 없음", s="좋은 선택이 자동으로", c="red", icon="3")])
S("오늘 들은 내용을 바로 실천하고 싶은 분들을 위해, 오늘 할 수 있는 다섯 가지를 정리해 드릴게요.", "check", headline="오늘 바로 할 수 있는 [다섯 가지]",
  items=[dict(t="[비상금] 생활비 3~6개월 치 따로 두기", c="gold", no="1"), dict(t="내 빚의 [금리와 만기] 적어 보기", c="red", no="2"), dict(t="예금은 금융회사당 [1억 원] 안으로", c="blue", no="3"), dict(t="월급날 [자동 투자] 걸어 두기", c="gold", no="4"), dict(t="[투자 일지] 첫 줄 쓰기", c="red", no="5")])
S("선택의 복리를 이야기로 한번 풀어 볼게요. 비슷한 출발선에 선 두 친구, 민수와 지영의 이야기입니다. 물론 이해를 돕기 위해 만든 가상의 이야기예요.", "kpi", kicker="가상의 이야기", big="민수와 지영", color="gold", unit="같은 출발선, 다른 선택", size=240)
S("둘 다 스물여덟 살에 같은 회사에 입사했고, 월급도 같았습니다. 다른 건 딱 하나, 월급날의 습관이었죠.", "compare", headline="같은 출발선, [다른 습관]",
  left=dict(title="민수", c="blue", rows=["남는 돈을 저축", "가끔 남지 않음"]), right=dict(title="지영", c="red", rows=["월급날 먼저 30만 원 투자", "자동 이체"]))
S("지영은 월급날 자동으로 30만 원씩 투자 계좌로 보냈습니다. 시장이 떨어질 때도, 오를 때도 그냥 두었죠. 민수는 쓰고 남으면 저축했는데, 남는 달이 생각보다 적었습니다.", "story", scene="calendar_flip", relabel={">12월<": ">월급날<", ">31<": ">30만<", ">1월<": ">월급날<", ">2<": ">30만<"})
S("연 6% 수익을 가정하면, 지영이 30년 동안 매달 30만 원씩 모은 돈은 3억 원 정도가 됩니다. 넣은 돈은 1억 8백만 원인데 말이죠.", "dual", headline="매달 30만 원 · [30년]", badge="계산 예시 · 연 6% 가정 · 세금·비용 제외",
  panels=[dict(title="넣은 돈", color="blue", pts=[.2, .42], tag="1억 800만 원", note="30만 원 × 360개월"), dict(title="30년 뒤", color="red", pts=[.2, .88], tag="약 3억 원", note="복리 효과")])
S("민수가 게으르거나 무능했던 게 아닙니다. 차이를 만든 건 의지가 아니라 습관을 자동으로 만들어 둔 하나의 선택이었어요.", "quote", lines=["차이를 만든 건 의지가 아니라", "[자동으로 만든 습관] 하나"], size=110)
S("그리고 민수에게도 기회는 남아 있습니다. 오늘부터 시작하면 되니까요. 가장 좋은 시작 시점은 10년 전이었고, 두 번째로 좋은 시점은 바로 오늘입니다.", "quote", lines=["가장 좋은 때는 10년 전", "[두 번째로 좋은 때는 오늘]"], size=120)
S("여덟 번째 이야기를 정리하겠습니다. 선택은 포기이고, 모든 선택에는 기회비용이 있습니다.", "check", headline="여덟 번째 이야기 정리",
  items=[dict(t="게임의 본질을 알아라 — 투자는 [기다림]", c="gold", no="1"), dict(t="손실 회피를 경계하라 — [오늘 새로 사겠나?]", c="blue", no="2"), dict(t="51 대 49 — [되돌릴 수 있으면 빨리]", c="red", no="3"), dict(t="작은 선택이 [복리]로 쌓인다", c="gold", no="4")])

# ═════════════ 전체 마무리 ═════════════
CH("마무리", "여덟 가지 이야기 [한 번에] 정리", "마무리 — 여덟 가지 이야기 한 번에", name="마무리 — 여덟 가지 이야기 한 번에 정리")
S("긴 시간 함께해 주셔서 감사합니다. 마지막으로 오늘 여덟 가지 이야기를 한 줄씩 다시 짚어 볼게요. 이 부분만 다시 들으셔도 오늘 내용이 정리되도록요.", "story", scene="wave")
S("하나, 통화량. 돈은 해마다 늘어나고, 그래서 현금만 쥐고 있으면 가만히 있어도 가난해집니다.", "kpi", kicker="하나", big="통화량", color="gold", unit="현금만 쥐고 있으면 가만히 있어도 가난해진다", size=240)
S("둘, 리스크. 리스크는 지는 게 아니라 줄이는 것. 나눠 담고, 시간을 나누고, 오래 기다리세요.", "kpi", kicker="둘", big="리스크", color="blue", unit="나눠 담고, 시간을 나누고, 오래 기다린다", size=240)
S("셋, 금리와 환율. 금리는 시간의 가격, 환율은 나라 돈끼리의 가격. 환율은 맞히지 말고 대비하세요.", "kpi", kicker="셋", big="금리와 환율", color="red", unit="금리는 시간의 가격, 환율은 대비하는 것", size=210)
S("넷, 부동산. 시장의 온도는 금리와 공급과 소득이 정하고, 내 집의 운명은 입지가 정합니다.", "kpi", kicker="넷", big="부동산", color="gold", unit="온도는 다섯 가지 힘, 운명은 입지", size=240)
S("다섯, 부채. 빚은 독도 득도 될 수 있습니다. 기준은 집값이 아니라 소득, 그리고 좋은 시절일수록 빚을 경계하세요.", "kpi", kicker="다섯", big="부채", color="blue", unit="기준은 소득, 좋은 시절일수록 경계", size=240)
S("여섯, 경제 위기. 진짜 위기는 의심에서 시작됩니다. 1억 원씩 나눠 맡기고, 비상금을 지키고, 위기를 기회로 볼 여유를 가지세요.", "kpi", kicker="여섯", big="경제 위기", color="red", unit="의심에서 시작, 대비는 분산·비상금·여유", size=210)
S("일곱, 선진국. 잘사는 나라의 조건은 제도와 신뢰, 그리고 이 원리는 사람에게도 똑같이 통합니다.", "kpi", kicker="일곱", big="선진국", color="gold", unit="제도와 신뢰, 사람에게도 같다", size=240)
S("여덟, 선택. 나는 내 선택의 총합입니다. 게임의 본질을 알고, 손실 회피를 경계하고, 작은 선택을 쌓아 가세요.", "kpi", kicker="여덟", big="선택", color="blue", unit="나는 내 선택의 총합", size=240)
S("경제 공부는 돈을 많이 벌기 위한 기술이기 전에, 세상이 어떻게 돌아가는지 알고 내 선택을 스스로 할 수 있게 해 주는 힘입니다.", "quote", lines=["경제 공부는", "[내 선택을 스스로 할 수 있게] 해 주는 힘"], size=110)
S("뉴스에서 금리, 환율, 통화량이라는 말이 나올 때마다 오늘 이야기가 하나씩 떠오르신다면, 오늘 시간은 충분히 값진 투자였을 겁니다.", "story", scene="lightbulb", relabel={">외국인 순매도<": ">금리 · 환율<", ">PER · 시가총액<": ">통화량 · 부채<"})
S("이 영상은 틀어 놓고 몇 번이고 다시 들으셔도 좋습니다. 들을 때마다 다른 부분이 귀에 들어오실 거예요.", "quote", lines=["몇 번이고 다시 들으셔도", "[들을 때마다 다른 부분]이 들립니다"], size=110)
S("오늘 영상이 도움이 되셨다면 구독과 좋아요 부탁드립니다. 끝까지 함께해 주셔서 감사합니다.", "story", scene="wave")


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
