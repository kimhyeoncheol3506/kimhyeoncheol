"""29편 매년 12월 당신 주식이 오르는 진짜 이유 (윈도우 드레싱) — 현철님 제공 대본 (HyperFrames 모션그래픽 중심)

사용:
  python3 projects/20261101-window-dressing/build.py plan     # project.json(장면·대사) 생성 → 음성 생성에 사용
  python3 projects/20261101-window-dressing/build.py render   # 음성 길이에 맞춰 HyperFrames 장면 렌더 → project.json 갱신
"""
import json
import os
import re
import subprocess
import sys

os.environ.setdefault("HF_LOOK", "sting")  # OPUSCAR 98 No.46 The Sting 룩
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
PJ = "projects/20261101-window-dressing"

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


# ═════════════ 오프닝 ═════════════
_chip = "오프닝"
S("매년 12월 마지막 거래일, 이상한 일이 벌어집니다.", "story", scene="calendar_flip")
S("어떤 주식들은 갑자기 거래량이 폭증하고, 펀드 수익률은 하루 만에 반등합니다.", "chart", headline="12월 마지막 날, 갑자기 [튀어오른다]", badge="개념도 · 실제 수치 아님",
  lines=[dict(name="펀드 수익률", color="red", pts=[.35, .33, .36, .34, .35, .37, .8], end="반등")], marks=[dict(x=.92, text="12월 마지막 거래일", color="gold")])
S("그리고 1월 첫 거래일이 되면, 그 반등이 사라지기도 하죠.", "chart", headline="1월 첫날, 반등이 [사라진다]", badge="개념도 · 실제 수치 아님",
  lines=[dict(name="펀드 수익률", color="gold", pts=[.35, .34, .36, .8, .4, .37, .36], end="원위치")], marks=[dict(x=.45, text="12월 말", color="red"), dict(x=.62, text="1월 첫날", color="blue")])
S("우연일까요?", "qa", q="[우연]일까요?")
S("아닙니다. 경제학과 금융학에서는 이 현상을 ‘윈도우 드레싱(window dressing)’, 즉 ‘보고서 꾸미기’라고 부릅니다.", "kpi", kicker="경제학·금융학의 이름", big="윈도우 드레싱", color="gold", unit="Window Dressing = 보고서 꾸미기", size=180)
S("오늘 영상을 끝까지 보시면, 연말 주가 움직임 뒤에 숨은 기관 투자자의 심리와 경제적 메커니즘, 그리고 개인 투자자가 이 시기에 절대로 저지르면 안 되는 실수까지 알게 됩니다.", "check", headline="오늘 알게 되는 것",
  items=[dict(t="기관 투자자의 [심리]", c="gold"), dict(t="연말 주가의 [경제적 메커니즘]", c="red"), dict(t="개인이 절대 하면 안 되는 [실수]", c="blue")])
Q("특히 마지막에 말씀드릴 ‘연말 수익률의 함정’은, 매년 반복되는 시장의 패턴을 이해하는 데 매우 중요합니다.", "마지막에 말씀드릴", "[연말 수익률의 함정]", "꼭 끝까지 보세요", size=100)

# ═════════════ 1. 윈도우 드레싱이란 ═════════════
CH("01", "[윈도우 드레싱]이란?", "01 · 윈도우 드레싱이란?", name="윈도우 드레싱이란?")
S("윈도우 드레싱은 쉽게 말해 펀드매니저가 연말 보고서를 더 좋아 보이게 만들기 위해 포트폴리오를 조정하는 행위입니다.", "story", scene="shop_window")
Q("상상해 보세요. 당신이 펀드 투자자라고 합시다.", "상상해 보세요", "당신이 [펀드 투자자]라면", size=120)
Q("연말에 받는 보고서에 이런 문장이 있다면 어떤 느낌이 드시겠습니까?", "연말 보고서에", "이런 문장이 있다면?", size=120)
S("“이 펀드는 올해 시장을 이끈 대형 기술주와 실적이 좋은 성장주를 보유하고 있습니다.”", "story", scene="report_read")
Q("좋아 보이죠.", "[좋아] 보이죠", size=170)
S2("그런데 실제로는 그 종목을 일 년 내내 들고 있었던 게 아니라, 12월 말에 성과 좋은 주식을 사고, 부진한 주식을 팔아서 보고서에만 좋은 종목이 남겨진 것일 수도 있습니다.",
   ("그런데 실제로는 그 종목을 일 년 내내 들고 있었던 게 아니라,", "quote", dict(lines=["실제로는 일 년 내내", "들고 있던 게 {아니라}"], size=110)),
   ("12월 말에 성과 좋은 주식을 사고, 부진한 주식을 팔아서 보고서에만 좋은 종목이 남겨진 것일 수도 있습니다.", "ledger", dict(headline="12월 말 [사고] {팔고}", rows=[dict(n="성과 좋은 주식", v="매수", g=True), dict(n="부진한 주식 A", v="−18%", g=False), dict(n="성과 좋은 주식 B", v="매수", g=True), dict(n="부진한 주식 C", v="−25%", g=False)], sell=[1, 3], hold=[0, 2], t_sell=0.35, hold_label="매수")))
S("금융학 연구들은 윈도우 드레싱을 “기관 투자자가 연말·분기말 보고 시점에 손실 종목을 정리하고, 수익률이 좋은 종목을 매수해 포트폴리오의 인상을 개선하는 전략”으로 설명합니다.", "flow", headline="금융학의 정의",
  nodes=[dict(t="연말·분기말 보고 시점", s="", c="gold", icon="▣"), dict(t="손실 종목 정리 + 수익 종목 매수", s="", c="red", icon="⇄", fs=36), dict(t="포트폴리오 인상 개선", s="", c="red", icon="✓")])
S("즉, 이것은 단순한 주식 매매가 아니라 정보 비대칭을 이용한 인식 관리에 가깝습니다.", "kpi", kicker="단순한 매매가 아니라", big="인식 관리", color="gold", unit="정보 비대칭을 이용한", size=210)

# ═════════════ 2. 왜 주가가 움직이는가 ═════════════
CH("02", "왜 [주가]가 움직이는가?", "02 · 왜 주가가 움직이는가?", name="왜 주가가 움직이는가?")
Q("여기서 핵심 질문이 나옵니다.", "여기서", "[핵심 질문]이 나옵니다", size=130)
S("“펀드매니저가 보고서를 예쁘게 꾸민다고, 왜 주가가 오르고 내리는가?”", "qa", q="보고서를 꾸미는데\n왜 [주가]가 움직일까?")
S("경제학적으로 답은 간단합니다. 수요와 공급의 일시적 왜곡 때문입니다.", "kpi", kicker="경제학적 답", big="수요·공급 왜곡", color="gold", unit="일시적으로", size=160)
S("첫째, 기관이 ‘승자 주식’을 대량으로 사면 수요가 몰립니다. 매물은 한정돼 있으니 가격이 오릅니다.", "scale", headline="① 승자 주식: 수요 ↑ → [가격 ↑]",
  left=dict(t="한정된 매물", s="공급", c="blue"), right=dict(t="기관 대량 매수", s="수요", c="red"), tilt=13)
S("둘째, 기관이 ‘패자 주식’을 대량으로 팔면 공급이 늘어납니다. 매수 세력이 부족하면 가격은 떨어집니다.", "scale", headline="② 패자 주식: 공급 ↑ → [가격 ↓]",
  left=dict(t="부족한 매수 세력", s="수요", c="red"), right=dict(t="기관 대량 매도", s="공급", c="blue"), tilt=13)
S("셋째, 이 움직임은 펀드의 실제 투자역량 변화가 아니라, 보고일이라는 특정 시점에 맞춘 포트폴리오 재배치일 수 있습니다.", "compare", headline="③ 실력이 아니라 [타이밍]",
  left=dict(title="실제 투자역량", c="mute", rows=["변하지 않았을 수도"]), right=dict(title="보고일 맞춤 재배치", c="gold", rows=["특정 시점에만 예쁘게"]))
S("미국 뮤추얼펀드를 분석한 연구에서는 펀드들이 연말과 분기말 마지막 거래일에는 S&P 500을 앞서는 경향을 보였지만, 바로 다음 거래일에는 시장 대비 부진한 성과를 보였다고 밝혔습니다.", "dual", headline="연구: 마지막 날 [앞서고], 다음 날 {뒤처진다}", badge="개념도 · 실제 수치 아님",
  panels=[dict(title="연말·분기말 마지막 날", color="red", pts=[.4, .42, .4, .44, .85], tag="S&P 500 앞섬", note=""), dict(title="바로 다음 거래일", color="blue", pts=[.8, .5, .45, .44, .42], tag="시장 대비 부진", note="")])
S("또 다른 연구에서는 미국 펀드들이 12월 마지막 거래일에 평균적으로 S&P 500을 약 0.53% 앞섰고, 소형주 펀드는 약 1.03% 앞섰다고 분석했습니다.", "compare", headline="12월 마지막 거래일 하루, S&P 500 대비",
  left=dict(title="미국 펀드 평균", c="red", rows=["약 +0.53%"]), right=dict(title="소형주 펀드", c="red", rows=["약 +1.03%"]))
Q("숫자는 작아 보이지만, 하루 만에 나오는 초과 수익이라는 점에서 매우 큰 신호입니다.", "숫자는 작아 보여도", "[하루 만의 초과 수익]은", "매우 큰 신호입니다", size=100)

# ═════════════ 3. 연말 효과와 1월 효과 ═════════════
CH("03", "연말 효과와 [1월 효과]", "03 · 연말 효과와 1월 효과", name="연말 효과와 1월 효과")
S("여기에 또 하나의 경제학적 장치가 겹칩니다. 바로 ‘1월 효과(January effect)’입니다.", "kpi", kicker="또 하나의 장치", big="1월 효과", color="gold", unit="January Effect", size=220)
S("연말에 기관이나 개인 투자자가 손실 종목을 정리하면, 그 주식의 가격은 일시적으로 더 떨어질 수 있습니다.", "chart", headline="연말: 손실 종목 정리로 [더 떨어진다]", badge="개념도 · 실제 수치 아님",
  lines=[dict(name="부진 종목", color="blue", pts=[.6, .55, .5, .42, .3, .2], end="12월 말")])
S("그런데 새해가 되면 매도 압력이 사라지고, 다시 매수 세력이 들어오면서 가격이 반등할 수 있습니다.", "chart", headline="새해: 매도 압력이 사라지면 [반등]", badge="개념도 · 실제 수치 아님",
  lines=[dict(name="부진 종목", color="red", pts=[.6, .5, .38, .2, .35, .5], end="1월 반등")], marks=[dict(x=.6, text="새해", color="gold")])
S("이것이 바로 “12월에 팔리고, 1월에 다시 사지는” 구조입니다.", "loop", headline="12월에 팔리고, 1월에 [다시 사진다]",
  nodes=[dict(t="12월 손실 매도", c="blue"), dict(t="일시적 하락", c="blue"), dict(t="1월 매도 압력 소멸", c="gold"), dict(t="재매수·반등", c="red")], center="연말·1월 효과", cfs=54)
S("실제 연구에서는 12월 마지막 10거래일보다 1월 첫 10거래일의 이상 수익률이 평균 3.9% 더 높았다는 결과도 있습니다.", "compare", headline="연구: 1월 첫 10거래일이 [평균 3.9%] 더 높았다",
  left=dict(title="12월 마지막 10거래일", c="blue", rows=["상대적으로 낮음"]), right=dict(title="1월 첫 10거래일", c="red", rows=["이상 수익률 +3.9%p 더"]))
Q("특히 작은 규모의 부진 종목에서는 그 차이가 더 컸습니다.", "특히 [작은 규모의 부진 종목]에서", "차이가 더 컸습니다", size=100)
Q("다만 여기서 조심해야 합니다.", "다만 여기서", "{조심}해야 합니다", size=140)
S("연말 주가 움직임에는 윈도우 드레싱 외에도 양도소득세 절세를 위한 손실 매도, 즉 ‘택스 로스 셀링(tax-loss selling)’이 함께 작동합니다.", "hub", headline="연말 주가를 움직이는 [두 가지 힘]", center="연말 주가",
  chips=[dict(t="윈도우 드레싱", c="gold"), dict(t="택스 로스 셀링", c="blue"), dict(t="양도세 절세용 손실 매도", c="blue")], cfs=60)
S("미국 연구들은 두 요인이 서로 비슷한 시장 현상을 만들기 때문에, 이를 정확히 분리하기 어렵다고 지적합니다.", "compare", headline="둘은 [정확히 분리하기 어렵다]",
  left=dict(title="윈도우 드레싱", c="gold", rows=["보고서 꾸미기"]), right=dict(title="택스 로스 셀링", c="blue", rows=["절세용 손실 매도"]))
Q("그러니 “12월에 오른 주식은 무조건 윈도우 드레싱이다”라고 단정하면 안 됩니다.", "12월에 오른 주식 = 무조건 윈도우 드레싱?", "{단정하면 안 됩니다}", size=96)

# ═════════════ 4. 기관의 게임, 개인의 기회? ═════════════
CH("04", "기관의 게임, [개인의 기회]?", "04 · 기관의 게임, 개인의 기회?", name="기관의 게임, 개인의 기회?")
S("그렇다면 개인 투자자는 이걸 이용해 돈을 벌 수 있을까요?", "qa", q="개인은 이걸 이용해\n[돈을 벌 수] 있을까?")
S("이론적으로는 가능해 보입니다. 12월 말에 오르는 ‘승자 주식’을 미리 사두고, 1월 초에 기관이 팔았던 부진 종목의 반등을 노리고, 분기말과 연말의 반복되는 수요를 이용하는 겁니다.", "check", headline="이론적으로는 [가능해 보이는] 전략",
  items=[dict(t="12월 말 [승자 주식]을 미리 사두기", c="red"), dict(t="1월 초 [부진 종목 반등] 노리기", c="gold"), dict(t="분기말·연말 [반복 수요] 이용하기", c="blue")])
Q("하지만 현실은 훨씬 어렵습니다.", "하지만 현실은", "{훨씬 어렵습니다}", ant="걱정", size=120)
S("첫째, 기관은 이미 시장에 영향을 줄 만큼 큰 자금을 움직입니다. 개인 투자자는 그 움직임을 뒤늦게 관찰하는 경우가 많습니다.", "story", scene="chase_buy")
S("둘째, 윈도우 드레싱은 매년 같은 방식으로 나타나지 않습니다. 시장 상황, 금리, 환율, 실적 발표, 지정학 리스크가 모두 겹치기 때문입니다.", "hub", headline="② 매년 [같지 않다]", center="연말 주가",
  chips=[dict(t="시장 상황", c="gold"), dict(t="금리", c="red"), dict(t="환율", c="blue"), dict(t="실적 발표", c="gold"), dict(t="지정학 리스크", c="blue")], cfs=56)
S("셋째, 일부 연구는 오히려 연말 가격 상승이 기관의 대규모 매수보다 기관의 매도를 줄이는 방식에서 나타났다고 분석합니다.", "compare", headline="③ 연구: 사서가 아니라 [덜 팔아서]?",
  left=dict(title="통념", c="mute", rows=["기관이 대량 매수"]), right=dict(title="일부 연구", c="gold", rows=["기관이 매도를 줄임"]))
Q("즉, “기관이 무조건 좋은 주식을 대량 매수한다”는 통념과 다를 수 있습니다.", "\"기관이 무조건 대량 매수한다\"는", "[통념과 다를 수] 있습니다", size=100)
S("결국 윈도우 드레싱은 확률을 높이는 배경 요인일 수는 있어도, 단기 매매의 확실한 신호는 아닙니다.", "signal", headline="윈도우 드레싱은",
  lamps=[dict(c="gold", t="배경 요인", s="확률을 높일 수는 있다"), dict(c="blue", t="확실한 신호", s="단기 매매 신호는 아니다")])

# ═════════════ 5. 진짜 의미 ═════════════
CH("05", "경제학적으로 본 [진짜 의미]", "05 · 경제학적으로 본 진짜 의미", name="경제학적으로 본 진짜 의미")
Q("윈도우 드레싱의 진짜 무서움은 주가 등락 자체가 아닙니다.", "진짜 무서움은", "주가 등락이 {아닙니다}", size=120)
S("그것은 시장 정보의 왜곡입니다.", "kpi", kicker="진짜 무서움", big="정보의 왜곡", color="red", size=220)
S("투자자는 연말 보고서를 보고 “이 펀드는 좋은 종목을 잘 골랐구나”라고 판단할 수 있습니다.", "story", scene="report_read")
S("하지만 그 보고서가 실제 투자 과정이 아니라, 특정 시점에 맞춘 ‘전시용 포트폴리오’라면 어떨까요?", "story", scene="shop_window")
S("이때 발생하는 문제는 세 가지입니다. 투자자는 펀드의 실제 리스크를 과소평가할 수 있고, 좋아 보이는 종목에 자금이 몰려 가격이 일시적으로 과열될 수 있으며, 반대로 팔린 부진 종목은 과도하게 저평가될 수 있습니다.", "check", headline="이때 생기는 [세 가지 문제]",
  items=[dict(t="펀드의 실제 리스크를 [과소평가]", c="gold"), dict(t="좋아 보이는 종목은 일시적 [과열]", c="red"), dict(t="팔린 부진 종목은 과도한 [저평가]", c="blue")])
S("경제학에서 말하는 시장의 효율성은 가격이 이용 가능한 정보를 정확히 반영할 때 가장 강합니다.", "flow", headline="시장 효율성의 조건",
  nodes=[dict(t="이용 가능한 정보", s="", c="gold", icon="▣"), dict(t="가격에 정확히 반영", s="", c="red", icon="→"), dict(t="효율적인 시장", s="", c="red", icon="✓")])
S("그런데 윈도우 드레싱은 보고 시점의 정보를 인위적으로 예쁘게 만들어, 가격과 실제 가치 사이의 괴리를 키울 수 있습니다.", "dual", headline="가격과 실제 가치의 [괴리]", badge="개념도 · 실제 수치 아님",
  panels=[dict(title="보고 시점 가격", color="red", pts=[.4, .45, .5, .62, .85], tag="예쁘게", note=""), dict(title="실제 가치", color="gold", pts=[.42, .44, .45, .46, .47], tag="그대로", note="")])
S("그래서 금융 당국과 학계는 이런 행위가 투자자 기만으로 이어질 수 있다는 점을 경계합니다.", "kpi", kicker="금융 당국·학계의 경계", big="투자자 기만", color="red", size=200)

# ═════════════ 6. 마무리 ═════════════
CH("06", "당신의 [수익률을 지키는 법]", "06 · 당신의 수익률을 지키는 법", name="마무리 — 당신의 수익률을 지키는 법")
S("그래서 연말 투자자에게 드리는 세 가지 경고입니다.", "kpi", kicker="연말 투자자에게", big="3가지 경고", color="gold", size=200)
S("첫째, 12월 마지막 며칠의 급등만 보고 추격 매수하지 마세요. 그 상승은 다음 해 1월에 되돌아올 수 있습니다.", "check", headline="연말 투자자 3가지 경고",
  items=[dict(t="12월 말 급등 [추격 매수 금지]", c="red", no="1")])
S("둘째, 펀드를 고를 때는 12월 수익률만 보지 마세요. 3년, 5년 누적 수익률과 최대 낙폭, 운용보수, 포트폴리오 변동성을 함께 보세요.", "check", headline="연말 투자자 3가지 경고",
  items=[dict(t="12월 말 급등 추격 매수 금지", c="mute", no="1"), dict(t="[3·5년 누적 수익률·최대 낙폭·보수·변동성]", c="gold", no="2")])
S("셋째, ‘기관이 사는 종목’이라는 소문에 흔들리지 마세요. 기관의 연말 매매는 당신을 위한 것이 아니라, 기관의 성과 보고서를 위한 것일 수 있습니다.", "check", headline="연말 투자자 3가지 경고",
  items=[dict(t="12월 말 급등 추격 매수 금지", c="mute", no="1"), dict(t="3·5년 누적 수익률·최대 낙폭·보수·변동성", c="mute", no="2"), dict(t="'기관이 사는 종목' [소문에 흔들리지 않기]", c="blue", no="3")])
S("시장은 때때로 당신에게 기회를 주는 것처럼 보이지만, 그 이면에는 누군가의 성적표를 위한 계산이 숨어 있습니다.", "story", scene="shop_window")
Q("연말에 주가가 오른다고 환호하기 전에, 한 번만 물어보세요.", "환호하기 전에", "[한 번만] 물어보세요", size=130)
S("“이 오름은 실제 가치인가, 아니면 누군가의 연말 보고서를 위한 장식인가?”", "signal", headline="한 번만 물어보세요",
  lamps=[dict(c="red", t="실제 가치?", s="기업 가치가 오른 것인가"), dict(c="gold", t="연말 장식?", s="누군가의 보고서를 위한 것인가")])
S("그 질문 하나가, 당신의 계좌를 지킬 수 있습니다.", "story", scene="check_account")
Q("당신이 12월에 번 돈은 수익이 아닐 수 있습니다. 1월에 더 크게 잃을 수도 있으니까요.", "12월에 번 돈은", "{수익이 아닐 수} 있습니다", size=120)
Q("이 영상을 저장해 두세요. 그리고 연말에 ‘갑자기 오르는 주식’을 보면, 댓글에 이렇게 써보세요.", "영상을 [저장]해 두고", "연말에 갑자기 오르는 주식을 보면", "댓글에 써보세요", size=96)
Q("‘이건 상승일까, 윈도우 드레싱일까?’", "\"이건 [상승]일까,", "{윈도우 드레싱}일까?\"", size=120)
S("그 질문을 하는 사람만이 시장에서 오래 살아남습니다.", "story", scene="wave")


# ═════════════ 출력 ═════════════
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
        pause = 0.45 if nxt and nxt.get("chapter") else 0.30
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
