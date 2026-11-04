"""31편 주식용어 백과사전 — 중고등학생도 이해하는 주식 용어 40개 (HyperFrames 모션그래픽 + A4 스틱맨)

사용:
  python3 projects/20261104-stock-terms/build.py plan     # project.json 생성
  python3 projects/20261104-stock-terms/build.py render   # 음성 길이에 맞춰 장면 렌더
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
PJ = "projects/20261104-stock-terms"

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


EX = "예시 · 실제 수치 아님"


def W(no, word, mean, color="gold", size=190):
    """용어 카드: 번호 + 용어 + 한 줄 뜻"""
    return dict(kicker=f"용어 {no:02d} / 40", big=word, color=color, unit=mean, size=size)


# ═════════════ 오프닝 ═════════════
_chip = "오프닝"
S("외국인 순매도에 코스피 2% 하락, 반도체는 PER 부담에 줄줄이 음봉.", "quote", lines=["외국인 [순매도]에 코스피 2% 하락", "반도체는 [PER 부담]에 줄줄이 {음봉}"], size=96)
S("이 뉴스, 무슨 말인지 다 들리시나요?", "story", scene="confused_news")
Q("주식이 어려운 건 머리가 나빠서가 아닙니다. 단어를 몰라서입니다.", "주식이 어려운 건 머리가 아니라", "[단어]를 몰라서입니다", size=110)
S("오늘은 뉴스와 주식 앱에 매일 나오는 용어 40개를, 중학생도 알아듣게 정리해 드리겠습니다.", "kpi", kicker="주식용어 백과사전", big="40개", color="gold", unit="뉴스·주식 앱에 매일 나오는 말", size=240)
S("영상이 끝나면, 처음 그 뉴스 문장이 한 번에 읽히실 겁니다.", "check", headline="오늘의 [5단계]",
  items=[dict(t="[기본] — 주식이 뭔데?", c="gold", no="1"), dict(t="[사고팔기] — 주문 버튼의 말", c="red", no="2"), dict(t="[차트] — 빨간 막대, 파란 막대", c="blue", no="3"),
         dict(t="[성적표] — PER, PBR, 배당", c="gold", no="4"), dict(t="[시장] — 외국인, 공매도, 서킷", c="red", no="5")])

# ═════════════ 1. 기본 ═════════════
CH("01", "주식의 [기본]", "01 · 기본 — 주식이 뭔데?", name="주식의 기본 — 주식, 상장, 코스피, 시가총액")
S("첫 번째, 주식. 주식은 회사를 아주 잘게 나눈 조각입니다.", "kpi", **W(1, "주식", "회사를 잘게 나눈 조각"))
S("피자 한 판을 여덟 조각으로 자르면, 한 조각을 가진 사람도 그 피자의 주인 중 한 명이죠.", "story", scene="pizza_share")
S("두 번째, 주주. 그 조각을 가진 사람입니다. 삼성전자 주식을 한 주만 사도 삼성전자의 주주가 됩니다.", "kpi", **W(2, "주주", "한 주만 사도 회사의 주인 중 한 명"))
S("세 번째, 상장. 아무 회사 주식이나 앱에서 살 수 있는 건 아닙니다.", "kpi", **W(3, "상장", "거래소에 이름을 올려 누구나 사고팔게 하는 것", "blue"))
S("한국거래소의 심사를 통과해 시장에 이름을 올려야, 누구나 사고팔 수 있습니다. 이걸 상장이라고 합니다.", "flow", headline="상장까지의 길",
  nodes=[dict(t="회사", s="돈이 필요", c="gold", icon="1"), dict(t="거래소 심사", s="한국거래소", c="blue", icon="2"), dict(t="상장", s="누구나 사고팜", c="red", icon="3")])
S2("네 번째와 다섯 번째, 코스피와 코스닥. 둘 다 주식 시장의 이름입니다. 코스피에는 삼성전자처럼 큰 회사가, 코스닥에는 기술 중심의 작고 젊은 회사가 많습니다.",
   ("네 번째와 다섯 번째, 코스피와 코스닥. 둘 다 주식 시장의 이름입니다.", "kpi", dict(kicker="용어 04·05 / 40", big="코스피 · 코스닥", color="gold", unit="한국 주식 시장의 두 이름", size=170)),
   ("코스피에는 삼성전자처럼 큰 회사가, 코스닥에는 기술 중심의 작고 젊은 회사가 많습니다.", "compare", dict(headline="[코스피] vs [코스닥]",
        left=dict(title="코스피", c="red", rows=["큰 회사가 많음", "예: 삼성전자"]), right=dict(title="코스닥", c="blue", rows=["기술 중심", "작고 젊은 회사"]))))
S("여섯 번째, 지수. 뉴스에서 '코스피 2% 하락'이라고 할 때, 그 숫자는 시장 전체의 평균 점수 같은 겁니다.", "kpi", **W(6, "지수", "시장 전체의 평균 점수"))
S("반 전체 평균이 떨어졌다고 모든 학생 점수가 떨어진 건 아니듯, 지수가 내려도 오르는 주식은 있습니다.", "chart", headline="지수 = 반 [평균] 점수", badge=EX,
  lines=[dict(name="코스피 지수", color="blue", pts=[.6, .58, .55, .5, .46], end="평균 하락"), dict(name="어떤 종목", color="red", pts=[.3, .36, .45, .52, .62], end="그래도 상승")])
S("일곱 번째, 시가총액. 주가에 주식 수를 곱한 값, 그러니까 회사 전체의 몸값입니다.", "flow", headline="용어 07 · [시가총액] = 회사 몸값",
  nodes=[dict(t="주가", s="한 주 가격", c="gold", icon="₩"), dict(t="× 주식 수", s="발행된 전부", c="blue", icon="×"), dict(t="= 시가총액", s="회사 전체 몸값", c="red", icon="=")])
S("주가가 비싸다고 큰 회사가 아닙니다. 한 주 100만 원짜리보다 한 주 5만 원짜리 회사의 시가총액이 더 클 수도 있습니다.", "compare", headline="주가가 비싸다 ≠ [큰 회사]",
  left=dict(title="A사: 한 주 100만 원", c="mute", rows=["× 100만 주", "= 1조 원"]), right=dict(title="B사: 한 주 5만 원", c="red", rows=["× 1억 주", "= 5조 원"]))
S("여덟 번째, 우량주. 실적이 좋고 오래 버틴 큰 회사의 주식입니다. 영어로는 블루칩이라고 부릅니다.", "kpi", **W(8, "우량주", "실적 좋고 튼튼한 큰 회사 · 블루칩", "red"))

# ═════════════ 2. 사고팔기 ═════════════
CH("02", "주문 버튼의 [말]", "02 · 사고팔기 — 주문 버튼의 말", name="사고팔기 — 매수, 호가, 예수금, 상한가")
S("아홉 번째와 열 번째, 매수와 매도. 매수는 사는 것, 매도는 파는 것입니다.", "compare", headline="용어 09·10 · [매수]와 {매도}",
  left=dict(title="매수", c="red", rows=["사는 것", "앱의 빨간 버튼"]), right=dict(title="매도", c="blue", rows=["파는 것", "앱의 파란 버튼"]))
S("열한 번째, 호가. 사고 싶은 사람과 팔고 싶은 사람이 각자 부르는 가격입니다.", "kpi", **W(11, "호가", "사고팔겠다고 부르는 가격", "blue"))
S("시장에서 흥정하듯, 산다는 값과 판다는 값이 딱 맞을 때 거래가 이루어집니다.", "story", scene="haggle")
S2("열두 번째, 시장가와 지정가. 지정가는 내가 정한 가격에만 사는 주문이고, 시장가는 지금 바로 아무 가격에나 사는 주문입니다.",
   ("열두 번째, 시장가와 지정가.", "kpi", dict(kicker="용어 12 / 40", big="시장가 · 지정가", color="gold", unit="주문하는 두 가지 방법", size=170)),
   ("지정가는 내가 정한 가격에만 사는 주문이고, 시장가는 지금 바로 아무 가격에나 사는 주문입니다.", "compare", dict(headline="[지정가] vs [시장가]",
        left=dict(title="지정가", c="blue", rows=["내가 정한 가격에만", "안 맞으면 안 사짐"]), right=dict(title="시장가", c="red", rows=["지금 바로", "가격은 시장 마음"]))))
S("급할 때 누른 시장가 주문이 생각보다 비싸게 체결되는 일, 초보 때 정말 많이 겪습니다.", "story", scene="chase_buy")
S("열세 번째, 예수금. 증권 계좌에 들어 있는, 아직 주식을 사지 않은 현금입니다.", "kpi", **W(13, "예수금", "계좌 안의 아직 안 쓴 현금"))
S("열네 번째, 결제일. 한국 주식은 오늘 사면 영업일 기준 이틀 뒤에 실제로 돈이 오갑니다. 그래서 디 플러스 투라고 부릅니다.", "timeline", headline="용어 14 · 결제는 [D+2]",
  events=[dict(when="오늘 (D)", t="매수·매도 체결", s="", c="gold"), dict(when="D+1", t="아직 정산 중", s="", c="blue"), dict(when="D+2", t="실제로 돈이 오감", s="영업일 기준", c="red")])
S("오늘 팔았는데 출금이 안 된다고 놀라지 마세요. 이틀만 기다리면 됩니다.", "story", scene="calendar_flip", relabel={">12월<": ">11월<", ">31<": ">3<", ">1월<": ">11월<", ">2<": ">5<"})
S("열다섯 번째, 시가와 종가. 한국 주식 정규장은 아침 9시에 열어 오후 3시 30분에 닫습니다.", "timeline", headline="용어 15 · [시가]와 [종가]",
  events=[dict(when="오전 9:00", t="시가", s="그날 첫 가격", c="gold"), dict(when="장중", t="고가 · 저가", s="가장 높은·낮은 가격", c="blue"), dict(when="오후 3:30", t="종가", s="그날 마지막 가격", c="red")])
S("그날 처음 거래된 가격이 시가, 마지막 가격이 종가입니다. 뉴스에 나오는 하루 등락률은 보통 종가 기준입니다.", "kpi", kicker="용어 15 / 40", big="종가 기준", color="red", unit="뉴스 속 하루 등락률은 보통 마지막 가격으로", size=200)
S("열여섯 번째, 거래량. 그날 사고판 주식의 수입니다. 가격이 크게 움직일 때 거래량도 같이 터지면, 그만큼 관심이 몰렸다는 뜻입니다.", "chart", headline="용어 16 · [거래량] = 관심의 크기", badge=EX,
  lines=[dict(name="거래량", color="gold", pts=[.15, .18, .16, .2, .78, .5], end="관심 폭발")])
S("열일곱 번째, 상한가와 하한가. 한국 주식은 하루에 전날 종가보다 최대 30%까지만 오르거나 내릴 수 있습니다.", "compare", headline="용어 17 · 하루 [±30%] 제한",
  left=dict(title="상한가", c="red", rows=["하루 최대 +30%", "더는 못 오름"]), right=dict(title="하한가", c="blue", rows=["하루 최대 −30%", "더는 못 내림"]))
S("1만 원짜리 주식이면, 하루에 1만 3천 원보다 비싸지거나 7천 원보다 싸질 수 없다는 뜻입니다.", "scale", headline="1만 원 주식의 하루 한계",
  left=dict(t="하한가 7천 원", s="−30%", c="blue"), right=dict(t="상한가 1만 3천 원", s="+30%", c="red"), tilt=0)
S("열여덟 번째와 열아홉 번째, 손절과 익절. 손해를 보고 파는 게 손절, 이익을 보고 파는 게 익절입니다.", "compare", headline="용어 18·19 · [손절]과 [익절]",
  left=dict(title="손절", c="blue", rows=["손해 보고 팔기", "더 큰 손해를 막음"]), right=dict(title="익절", c="red", rows=["이익 보고 팔기", "번 돈을 확정"]))
S("스무 번째, 물타기. 산 주식이 떨어졌을 때 더 사서 평균 가격을 낮추는 겁니다.", "flow", headline="용어 20 · [물타기]", badge="계산 예시",
  nodes=[dict(t="1만 원에 1주", s="처음 매수", c="gold", icon="1"), dict(t="8천 원에 1주 더", s="떨어져서 추가", c="blue", icon="+"), dict(t="평균 9천 원", s="평균 가격이 낮아짐", c="red", icon="=")])
S("하지만 회사가 정말 나빠져서 떨어지는 거라면, 물타기는 손실만 키웁니다.", "story", scene="bed_phone")

# ═════════════ 3. 차트 ═════════════
CH("03", "빨간 막대, [파란 막대]", "03 · 차트 — 빨간 막대, 파란 막대", name="차트 — 양봉, 이동평균선, 골든크로스")
S("스물한 번째와 스물두 번째, 양봉과 음봉. 차트의 막대 하나가 하루를 뜻합니다.", "story", scene="candle_board")
S("시작보다 끝이 높으면 빨간 양봉, 시작보다 끝이 낮으면 파란 음봉입니다. 미국은 반대로 초록이 오름, 빨강이 내림이에요.", "compare", headline="용어 21·22 · [양봉]과 {음봉}",
  left=dict(title="양봉 (빨강)", c="red", rows=["시가보다 종가가 높음", "그날 올랐다"]), right=dict(title="음봉 (파랑)", c="blue", rows=["시가보다 종가가 낮음", "그날 내렸다"]))
S("막대 위아래로 삐죽 나온 가는 선은 꼬리라고 부릅니다. 그날 잠깐 찍었던 가장 높은 가격과 가장 낮은 가격이죠.", "kpi", kicker="양봉·음봉의 꼬리", big="꼬리", color="gold", unit="그날의 고가와 저가", size=230)
S("스물세 번째, 이동평균선. 최근 며칠 동안의 종가 평균을 이어 그린 선입니다.", "chart", headline="용어 23 · [이동평균선]", badge=EX,
  lines=[dict(name="주가", color="red", pts=[.3, .5, .38, .6, .45, .68, .55, .72], end=""), dict(name="20일 평균선", color="gold", pts=[.32, .38, .42, .48, .5, .56, .58, .63], end="평균선")])
S("5일선은 일주일, 20일선은 한 달, 120일선은 반년의 흐름이라고 생각하면 쉽습니다.", "check", headline="평균선 [읽는 법]",
  items=[dict(t="[5일선] — 약 일주일 흐름", c="red", no="5"), dict(t="[20일선] — 약 한 달 흐름", c="gold", no="20"), dict(t="[120일선] — 약 반년 흐름", c="blue", no="120")])
S("스물네 번째, 골든크로스와 데드크로스. 짧은 평균선이 긴 평균선을 뚫고 올라가면 골든크로스, 뚫고 내려가면 데드크로스입니다.", "dual", headline="용어 24 · [골든크로스] vs {데드크로스}",
  panels=[dict(title="골든크로스", color="red", pts=[.25, .7], tag="상승 신호?", note="짧은 선이 위로"), dict(title="데드크로스", color="blue", pts=[.7, .25], tag="하락 신호?", note="짧은 선이 아래로")])
S("신호일 뿐, 정답은 아닙니다. 차트는 과거를 보여 줄 뿐 미래를 약속하지 않으니까요.", "quote", lines=["신호일 뿐, [정답]은 아닙니다", "차트는 {과거}만 보여 줍니다"], size=110)
S("스물다섯 번째와 스물여섯 번째, 지지선과 저항선. 주가가 자꾸 멈춰 서는 바닥이 지지선, 자꾸 막히는 천장이 저항선입니다.", "chart", headline="용어 25·26 · [지지선]과 [저항선]", badge=EX,
  lines=[dict(name="주가", color="gold", pts=[.3, .65, .32, .66, .3, .64, .33], end="")], marks=[dict(x=.15, text="천장 = 저항선", color="red"), dict(x=.65, text="바닥 = 지지선", color="blue")])
S("스물일곱 번째, 조정. 오르던 주가가 잠깐 쉬어 가듯 떨어지는 걸 말합니다. 보통 고점에서 10% 안팎 빠지면 조정이라고 부릅니다.", "kpi", **W(27, "조정", "오르다 잠깐 쉬어 가는 하락 · 보통 10% 안팎", "blue"))
S("스물여덟 번째, 불장과 곰장. 황소가 뿔을 위로 치받듯 오르는 시장이 불장, 곰이 앞발로 내리치듯 떨어지는 시장이 곰장입니다.", "compare", headline="용어 28 · [불장]과 {곰장}",
  left=dict(title="불장 (강세장)", c="red", rows=["황소 = Bull", "뿔을 위로 치받듯 상승"]), right=dict(title="곰장 (약세장)", c="blue", rows=["곰 = Bear", "앞발로 내리치듯 하락"]))
S("보통 고점에서 20% 넘게 떨어지면 약세장, 곰장에 들어갔다고 말합니다.", "kpi", kicker="약세장의 기준 (관행)", big="−20%", color="blue", unit="고점 대비 20% 넘게 하락", size=240)

# ═════════════ 4. 성적표 ═════════════
CH("04", "회사의 [성적표]", "04 · 성적표 — PER, PBR, 배당", name="회사의 성적표 — 영업이익, PER, PBR, ROE, 배당")
S("스물아홉 번째, 매출, 영업이익, 순이익. 회사의 성적표 맨 위에 나오는 세 숫자입니다.", "kpi", **W(29, "매출 · 영업이익 · 순이익", "회사 성적표의 세 줄", size=120))
S("떡볶이 가게로 생각해 볼까요. 하루 떡볶이를 100만 원어치 팔았다면, 그게 매출입니다.", "story", scene="shop_window", relabel={">연말 보고서<": ">오늘 매출 100만<"})
S("재료비, 월세, 알바비를 빼고 남은 돈이 영업이익, 거기서 이자와 세금까지 빼고 진짜 손에 남는 돈이 순이익입니다.", "flow", headline="떡볶이 가게 [성적표]", badge="계산 예시",
  nodes=[dict(t="매출 100만 원", s="판 돈 전부", c="gold", icon="1"), dict(t="영업이익 20만 원", s="재료비·월세·알바비 뺌", c="blue", icon="2"), dict(t="순이익 15만 원", s="이자·세금까지 뺌", c="red", icon="3")])
S("서른 번째, EPS, 주당순이익. 순이익을 주식 수로 나눈 값, 주식 한 주당 1년에 벌어 오는 돈입니다.", "kpi", **W(30, "EPS", "주당순이익 · 주식 한 주당 1년에 버는 돈", "gold", 230))
S("서른한 번째, 뉴스에 정말 자주 나오는 PER. 주가를 주당순이익으로 나눈 값입니다.", "flow", headline="용어 31 · [PER] = 주가 ÷ EPS", badge="계산 예시",
  nodes=[dict(t="주가 1만 원", s="", c="gold", icon="₩"), dict(t="÷ EPS 1천 원", s="한 주당 1년에 버는 돈", c="blue", icon="÷"), dict(t="PER 10배", s="", c="red", icon="=")])
S("PER 10배는, 회사가 지금처럼 벌면 내 주식값만큼 버는 데 10년이 걸린다는 뜻입니다.", "story", scene="hourglass")
S("그래서 PER이 높으면 이익에 비해 비싸다, 낮으면 싸다고 봅니다. 뉴스의 'PER 부담'은 너무 비싸졌다는 말이에요.", "scale", headline="[PER 부담] = 이익에 비해 비쌈",
  left=dict(t="PER 낮음", s="이익에 비해 쌈", c="blue"), right=dict(t="PER 높음", s="이익에 비해 비쌈", c="red"), tilt=10)
S("물론 앞으로 크게 성장할 회사는 PER이 높아도 비싸지 않을 수 있습니다. 같은 업종끼리 비교하는 게 기본입니다.", "check", headline="PER 볼 때 [주의할 점]",
  items=[dict(t="[같은 업종]끼리 비교하기", c="gold"), dict(t="[성장]이 빠르면 높아도 정상일 수 있음", c="blue"), dict(t="이익이 [적자]면 PER은 의미 없음", c="red")])
S("서른두 번째, PBR. 주가를 회사가 가진 순수한 재산, 즉 순자산으로 나눈 값입니다.", "kpi", **W(32, "PBR", "주가 ÷ 주당순자산", "blue", 230))
S("PBR이 1보다 낮으면, 장부상으로는 회사를 당장 정리해서 재산을 나눠 가져도 지금 주가보다 많이 받는다는 뜻입니다. 그만큼 싸게 거래된다는 거죠.", "compare", headline="[PBR 1]이 기준선",
  left=dict(title="PBR 1 미만", c="blue", rows=["재산보다 싸게 거래", "저평가?"]), right=dict(title="PBR 1 초과", c="red", rows=["재산보다 비싸게 거래", "미래 기대 반영"]))
S("서른세 번째, ROE, 자기자본이익률. 주주가 맡긴 돈으로 1년에 몇 퍼센트를 벌었는지 보여 줍니다.", "flow", headline="용어 33 · [ROE] = 순이익 ÷ 자기자본", badge="계산 예시",
  nodes=[dict(t="자기자본 100억", s="주주의 돈", c="gold", icon="₩"), dict(t="순이익 15억", s="1년 동안", c="blue", icon="÷"), dict(t="ROE 15%", s="돈을 잘 굴림", c="red", icon="=")])
S("은행 이자보다 훨씬 높은 ROE를 꾸준히 내는 회사가, 흔히 말하는 돈 잘 버는 회사입니다.", "story", scene="report_read", relabel={">펀드 보고서<": ">실적 보고서<"})
S("서른네 번째, 배당. 회사가 번 돈의 일부를 주주에게 현금으로 나눠 주는 겁니다.", "story", scene="dividend_rain")
S("주가가 1만 원인데 1년에 배당을 500원 준다면, 배당수익률은 5%입니다.", "kpi", kicker="배당수익률 = 배당금 ÷ 주가 (계산 예시)", big="5%", color="red", unit="1만 원 주식에 배당 500원", size=250)

# ═════════════ 5. 시장 ═════════════
CH("05", "시장의 [주인공들]", "05 · 시장 — 외국인, 공매도, 서킷", name="시장의 주인공 — 외국인, 순매도, 공매도, 서킷브레이커")
S("서른다섯 번째, 개인, 외국인, 기관. 주식 시장의 세 주인공입니다.", "hub", center="주식 시장", chips=[dict(t="개인 · 우리", c="gold"), dict(t="외국인 · 해외 투자자", c="blue"), dict(t="기관 · 연금·보험·펀드", c="red")])
S("개인은 우리 같은 사람, 외국인은 해외 투자자, 기관은 국민연금이나 보험사, 펀드처럼 큰돈을 굴리는 곳입니다.", "check", headline="세 주인공 [구분하기]",
  items=[dict(t="[개인] — 우리 같은 개미 투자자", c="gold"), dict(t="[외국인] — 해외의 투자자·펀드", c="blue"), dict(t="[기관] — 연금·보험사·자산운용사", c="red")])
S("서른여섯 번째, 순매수와 순매도. 판 것보다 산 게 많으면 순매수, 산 것보다 판 게 많으면 순매도입니다.", "compare", headline="용어 36 · [순매수]와 {순매도}",
  left=dict(title="순매수", c="red", rows=["산 돈 > 판 돈", "더 많이 샀다"]), right=dict(title="순매도", c="blue", rows=["판 돈 > 산 돈", "더 많이 팔았다"]))
S("외국인은 굴리는 돈이 커서, 외국인이 대규모로 순매도하면 지수가 크게 흔들리곤 합니다.", "story", scene="two_giants")
S("서른일곱 번째, 테마주. 회사 실적보다 '요즘 뜨는 이야기' 하나로 우르르 함께 움직이는 주식들입니다.", "kpi", **W(37, "테마주", "실적보다 '뜨는 이야기'로 같이 움직이는 주식", "red"))
S("이야기가 식으면 올랐던 만큼 빠르게 떨어지는 경우가 많아서, 가장 조심해야 하는 종류입니다.", "story", scene="subway_comments")
S("서른여덟 번째, 공매도. 주식을 빌려서 먼저 팔고, 나중에 싸게 사서 갚는 방법입니다.", "story", scene="short_borrow")
S("1만 원일 때 빌려서 팔고, 7천 원으로 떨어졌을 때 사서 갚으면 3천 원이 남습니다. 떨어질수록 돈을 버는 구조죠.", "flow", headline="용어 38 · [공매도]의 구조", badge="계산 예시",
  nodes=[dict(t="빌려서 1만 원에 팜", s="먼저 판다", c="blue", icon="1"), dict(t="7천 원에 다시 삼", s="떨어진 뒤", c="gold", icon="2"), dict(t="갚고 3천 원 남음", s="하락에 베팅", c="red", icon="3")])
S("서른아홉 번째, 신용거래와 반대매매. 증권사에서 돈을 빌려 주식을 사는 게 신용거래입니다.", "kpi", **W(39, "신용거래 · 반대매매", "빚내서 산 주식이 떨어지면 강제로 팔림", "blue", 130))
S("주가가 많이 떨어져 담보가 모자라면, 증권사가 내 주식을 강제로 팔아 버립니다. 이게 반대매매입니다.", "story", scene="debt_bill", relabel={">청구서<": ">증권사<", ">이자<": ">반대매매<"})
S2("마지막 마흔 번째, 사이드카와 서킷브레이커. 시장이 너무 급하게 움직일 때 거는 브레이크입니다. 사이드카는 코스피 선물이 5% 넘게 급변해 1분 넘게 이어지면, 컴퓨터 자동 주문을 5분 동안 멈춥니다.",
   ("마지막 마흔 번째, 사이드카와 서킷브레이커. 시장이 너무 급하게 움직일 때 거는 브레이크입니다.", "kpi", dict(kicker="용어 40 / 40", big="사이드카 · 서킷브레이커", color="red", unit="시장이 급할 때 거는 브레이크", size=130)),
   ("사이드카는 코스피 선물이 5% 넘게 급변해 1분 넘게 이어지면, 컴퓨터 자동 주문을 5분 동안 멈춥니다.", "signal", dict(headline="1단계 브레이크 · [사이드카]",
        lamps=[dict(c="gold", t="선물 5% 급변", s="1분 넘게 지속"), dict(c="red", t="프로그램 매매 5분 정지", s="코스피 기준")])))
S("서킷브레이커는 더 센 브레이크입니다. 코스피가 전날보다 8% 넘게 떨어진 상태가 1분 넘게 이어지면, 모든 거래를 20분 동안 멈춥니다.", "timeline", headline="[서킷브레이커] 3단계",
  events=[dict(when="−8%", t="1단계: 20분 정지", s="1분 넘게 지속 시", c="gold"), dict(when="−15%", t="2단계: 20분 정지", s="", c="red"), dict(when="−20%", t="3단계: 그날 장 종료", s="", c="blue")])
S("사람들이 겁에 질려 다 같이 팔 때, 잠깐 숨 돌릴 시간을 주는 장치입니다.", "story", scene="shield", relabel={">FCF<": ">서킷<"})

# ═════════════ 엔딩 ═════════════
CH("06", "이제 [다시] 읽어 볼까요?", "06 · 엔딩 — 다시 읽는 그 뉴스", name="엔딩 — 처음 그 뉴스, 다시 읽기")
S("자, 처음 그 뉴스를 다시 읽어 보겠습니다.", "quote", lines=["외국인 [순매도]에 코스피 2% 하락", "반도체는 [PER 부담]에 줄줄이 {음봉}"], size=96)
S2("해외 투자자들이 산 것보다 판 게 많아서, 시장 평균 점수가 2% 내려갔고, 반도체 회사들은 버는 돈에 비해 주가가 비싸다는 걱정 때문에, 시작보다 낮게 끝났다.",
   ("해외 투자자들이 산 것보다 판 게 많아서, 시장 평균 점수가 2% 내려갔고,", "check", dict(headline="뉴스 [번역]하기 ①",
        items=[dict(t="외국인 순매도 → [해외 투자자가 더 많이 팔았다]", c="blue"), dict(t="코스피 2% 하락 → [시장 평균 점수가 2% 내렸다]", c="blue")])),
   ("반도체 회사들은 버는 돈에 비해 주가가 비싸다는 걱정 때문에, 시작보다 낮게 끝났다.", "check", dict(headline="뉴스 [번역]하기 ②",
        items=[dict(t="PER 부담 → [이익에 비해 주가가 비싸다]", c="gold"), dict(t="음봉 → [시작보다 낮게 끝났다]", c="blue")])))
S("어떠세요? 이제 한 번에 들리시죠.", "story", scene="lightbulb")
S("용어를 안다고 돈을 버는 건 아니지만, 용어를 모르면 남의 말만 믿고 투자하게 됩니다.", "quote", lines=["용어를 안다고 돈을 버는 건 아니지만", "모르면 [남의 말]만 믿게 됩니다"], size=100)
S("오늘 40개면 뉴스와 주식 앱의 말 대부분은 읽힙니다. 헷갈릴 때마다 이 영상을 사전처럼 다시 꺼내 보세요.", "kpi", kicker="저장해 두고 사전처럼", big="40개 끝", color="gold", unit="뉴스·주식 앱의 말, 이제 대부분 읽힙니다", size=240)
S("도움이 되셨다면 구독과 좋아요 부탁드립니다. 감사합니다.", "story", scene="wave")


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
