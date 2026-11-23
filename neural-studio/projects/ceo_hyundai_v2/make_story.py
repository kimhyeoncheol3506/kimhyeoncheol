#!/usr/bin/env python3
"""현대자동차 v2 스토리보드 (12편)."""
import json, os
P = os.path.dirname(os.path.abspath(__file__)); X = []
def sh(kind, s, **k):
    d = {"kind": kind}
    if s is not None: d["s"] = s if isinstance(s, list) else [s]
    d.update(k); X.append(d)
def lab(text, at, color="lime", **k): return dict(text=text, at=at, color=color, **k)
def ch(id, x, emotion="neutral", pose="idle", **k): return dict(id=id, x=x, emotion=emotion, pose=pose, **k)
def chap(t, n): sh("title", None, text=t, sub=n, hold=1.6)

# 인트로 · 로봇 하나로 2.5배, 그리고 3분의 1
sh("chart", [0, 1], board="white", chart={"type": "bar", "values": [296500, 750000], "labels": ["2025년 마지막 거래일", "2026.6.1"], "suffix": "원", "title": "현대차 종가 (네이버 증권)", "show_values": True, "highlight": 1, "at": "29만"},
   labels=[lab("다섯 달", "다섯", "gold")])
sh("closeup", 2, who="m1", side="left", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "차를 더 팔았나?", "at": "팔아서가", "thought": True})
sh("wide", 3, set="board", time="night", chars=[ch("atlas", 960, "confident", "wave")],
   labels=[lab("무대 위 로봇 하나", "로봇", "lime", x=960, y=250)])
sh("counter", [4, 5], value={"from": 750000, "to": 253000, "suffix": "원", "at": "25만"}, caption="현대차 종가 2026년 11월 20일 (네이버 증권)", icon="chart_down",
   compare={"text": "꼭대기의 3분의 1", "icon": "warning", "at": "3분의"})
sh("skyline", 6, time="day", labels=[lab("현대자동차", "현대자동차입니다", size=180)])
chap("판돈", "1장")
sh("wide", [7, 8], set="office", era="old", wall="sand", time="day", tag="1967년 · 서울", calendar="1967 12",
   chars=[ch("founder", 900, "confident", "present", beats=[{"at": "세웁니다", "pose": "celebrate", "emotion": "excited"}])],
   lower_third={"name": "정주영", "sub": "창업주", "at": "정주영"})
sh("icon", [9, 10], tag="1968년 · 울산", icons=[{"name": "car", "label": "남의 차를 조립", "at": "조립했습니다"}, {"name": "factory", "label": "포드 코티나 조립 (울산)", "at": "코티나를"}])
sh("table", 11, items=[{"type": "contract", "title": "합작 협상", "text": "포드 ↔ 현대", "at": "+0.2", "stamp": {"text": "결렬 · 1971년", "at": "깨집니다"}}])
sh("wide", 12, set="board", time="day", tag="1973년 3월",
   chars=[ch("founder", 760, "angry", "arms_crossed", beats=[{"at": "만들겠다고", "pose": "point", "emotion": "confident"}])],
   props=[{"icon": "car", "x": 1400, "y": 700, "s": .6, "at": "차를"}],
   stamp={"text": "독자 모델", "at": "정합니다", "color": "red"})
sh("map", [13, 14], places=[{"name": "울산", "x": 1450, "y": 560}, {"name": "이탈리아", "x": 520, "y": 420}], vehicle="plane", at="이탈리아",
   labels=[lab("설계 용역비 120만 달러", "120만", "gold")])
sh("closeup", 15, who="founder", side="left", set="street", time="day", emotion="excited", pose="present",
   labels=[lab("포니", "포니입니다", "lime", x=1350, y=860, size=150)])
sh("wide", 16, set="street", time="day", shop="울산 공장", tag="1975년 12월",
   chars=[ch("worker", 700, "happy", "push")],
   props=[{"icon": "car", "x": 1200, "y": 700, "s": .5, "at": "울산"}, {"icon": "car", "x": 1450, "y": 700, "s": .5, "at": "양산이"}, {"icon": "car", "x": 1700, "y": 700, "s": .5, "at": "시작됩니다"}])
sh("counter", [17, 18], value={"from": 0, "to": 10726, "suffix": "대", "at": "1만"}, caption="1976년 포니 판매 (현대차 공식)", icon="car",
   compare={"text": "국내 승용차의 44%", "icon": "trophy", "at": "44%였습니다"})
sh("map", [19, 20], places=[{"name": "울산", "x": 1450, "y": 520}, {"name": "에콰도르", "x": 420, "y": 700}], vehicle="ship", at="에콰도르에",
   labels=[lab("1976년 7월 · 5대", "5대를", "cream"), lab("1978년 40개국 1만 8,317대", "40개국에", "gold")])
sh("closeup", [21, 22, 23], who="m1", side="right", set="home", time="night", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "정말 자동차?", "at": "자동차였을까요", "thought": True},
   labels=[lab("성적표는 끝에", "성적표를", "red", x=600, y=860, size=100)])
chap("결정", "2장")
sh("wide", 24, set="office", era="old", wall="blue", time="day",
   chars=[ch("mk", 900, "confident", "hips")],
   lower_third={"name": "정몽구", "sub": "2대 회장", "at": "정몽구의"})
sh("table", 25, hand="mk", items=[{"type": "newspaper", "title": "1998년 10월 (보도)", "text": "기아 국제입찰 · 현대 낙찰", "at": "+0.2", "ring_at": "낙찰자로"}],
   stamp={"text": "낙찰", "at": "선정됩니다", "color": "red"})
sh("icon", 26, tag="1999년", icons=[{"name": "building", "label": "현대차 경영을 맡다", "at": "+0.2"}, {"name": "handshake", "label": "정몽구 회장", "at": "경영을"}])
sh("wide", [27, 28], set="board", time="day", tag="1999년 · 미국",
   chars=[ch("mk", 700, "confident", "arms_crossed", beats=[{"at": "결정", "pose": "point", "emotion": "confident"}, {"at": "늘린", "pose": "celebrate", "emotion": "excited"}]),
          ch("exec", 1300, "worried", "stressed")],
   stamp={"text": "10년 · 10만 마일", "at": "늘린", "color": "red"})
sh("chart", [29, 30], board="chalk", chart={"type": "bar", "values": [3, 5, 10], "labels": ["포드·GM", "도요타", "현대"], "suffix": "년", "title": "당시 무상보증 기간 (보도)", "show_values": True, "highlight": 2, "at": "포드와"})
sh("closeup", [31, 32], who="exec", side="left", set="office", time="night", emotion="nervous", pose="stressed",
   bubble={"who": "exec", "text": "수리비 폭탄?", "icon": "warning", "at": "수리비가"},
   labels=[lab("품질을 올릴 수밖에", "품질을", "lime", x=1350, y=860)])
sh("icon", 33, icons=[{"name": "trophy", "label": "2004년 초기품질조사 7위 (보도)", "at": "+0.2"}, {"name": "target", "label": "도요타 앞섬", "at": "도요타를"}])
sh("counter", [34, 35], value={"from": 130, "to": 418, "suffix": "만 대", "at": "130만"}, caption="현대차+기아 판매, 10년 사이 (보도)", icon="chart_up",
   compare={"text": "3.2배", "icon": "trophy", "at": "3.2배입니다"})
chap("위기", "3장")
sh("skyline", [36, 37], time="dusk", tag="2014년 9월 18일 · 서울 삼성동", labels=[lab("한국전력 본사 부지", "부지입니다", "gold", size=110)])
sh("table", 38, hand="mk", items=[{"type": "contract", "title": "부지 입찰서", "text": "현대차·기아·현대모비스", "at": "+0.2", "stamp": {"text": "10조 5,500억 원", "at": "10조"}}])
sh("chart", [39, 40], board="white", chart={"type": "bar", "values": [33346, 105500], "labels": ["감정가", "써낸 값"], "suffix": "억 원", "title": "한전 부지 (보도)", "show_values": True, "highlight": 1, "at": "감정가는"},
   labels=[lab("약 3.2배", "3.2배를", "red")])
sh("counter", [41, 42], value={"from": 0, "to": 9.17, "prefix": "-", "suffix": "%", "at": "9.17%"}, caption="2014년 9월 18일 현대차 하루 주가 (보도)", icon="chart_down",
   compare={"text": "종가 19만 8천 원", "icon": "coins", "at": "19만"})
sh("crowd", 43, count=20, emotion="worried", set="street", labels=[lab("승자의 저주?", "저주를", "red", size=120)])
sh("chart", [44, 45], board="chalk", chart={"type": "line", "values": [198000, 160000, 140000, 120000, 65900], "trend": "down", "show_values": False, "title": "현대차 종가 2014.9 → 2020.3 (네이버)", "at": "2020년"},
   labels=[lab("6만 5,900원", "6만", "red"), lab("땅 산 날의 3분의 1", "3분의", "cream")])
chap("베팅", "4장")
sh("wide", [46, 47], set="office", era="modern", wall="teal", time="day", tag="2020년 10월 14일",
   chars=[ch("es", 760, "confident", "present"), ch("mk", 1250, "smile", "wave")],
   lower_third={"name": "정의선", "sub": "현대차그룹 회장", "at": "정의선"})
sh("counter", 48, value={"from": 0, "to": 178000, "suffix": "원", "at": "17만"}, caption="정의선 회장 취임일 현대차 종가 (네이버)", icon="coins")
sh("table", [49, 50], hand="es", items=[{"type": "contract", "title": "인수 계약", "text": "보스턴다이나믹스", "at": "+0.2", "stamp": {"text": "계약", "at": "보스턴다이나믹스입니다"}}])
sh("versus", [51, 52], colors=["#D9E4F2", "#E6E6E6"], left={"who": "es", "title": "현대차그룹 80%", "emotion": "happy", "pose": "point", "at": "+0.2"},
   right={"who": "atlas", "title": "로봇 회사", "emotion": "smile", "pose": "wave", "at": "80%를"},
   labels=[lab("2021년 6월 인수 완료", "2021년", "gold", x=960, y=900)])
sh("counter", 53, value={"from": 0, "to": 12468, "suffix": "억 원", "at": "+0.3"}, caption="2021년 보스턴다이나믹스 기업가치 (보도)", icon="moneybag",
   compare={"text": "약 11억 달러", "icon": "coins", "at": "11억"})
sh("closeup", [54, 55], who="m1", side="left", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "차 회사가 왜 로봇을?", "at": "로봇", "thought": True})
sh("wide", [56, 57], set="street", time="day", shop="자동차 공장",
   chars=[ch("worker", 650, "happy", "present"), ch("atlas", 1150, "confident", "push", beats=[{"at": "나눠", "pose": "hold", "emotion": "happy"}])],
   props=[{"icon": "factory", "x": 1600, "y": 690, "s": .6, "at": "공장에"}], labels=[lab("답은 공장", "공장에", "lime", x=1400, y=260)])
sh("title", [58, 59], text="그런데, 미국 관세")
sh("counter", 60, value={"from": 0, "to": 1862545, "suffix": "억 원", "at": "+0.3"}, caption="2025년 매출 (DART)", icon="trophy",
   compare={"text": "역대 최대 (보도)", "icon": "chart_up", "at": "역대"})
sh("chart", [61, 62], board="white", chart={"type": "bar", "values": [142396, 114679], "labels": ["2024년", "2025년"], "suffix": "억 원", "title": "영업이익 (DART)", "show_values": True, "highlight": 1, "at": "영업이익은"},
   labels=[lab("-19.5%", "19.5%", "red"), lab("관세 손실 4조 원 넘게 (보도)", "관세로만", "cream")])
sh("wide", [63, 64], set="board", time="night", tag="2026년 1월 · 라스베이거스",
   chars=[ch("es", 600, "confident", "present_left"), ch("atlas", 1200, "excited", "celebrate")],
   lower_third={"name": "아틀라스", "sub": "사람 모양 로봇", "at": "아틀라스의"})
sh("icon", [65, 66], icons=[{"name": "calendar", "text": "2028", "top": "투입", "label": "미국 조지아 공장", "at": "+0.2"}, {"name": "factory", "label": "로봇 연 3만 대 체계", "at": "3만"}])
sh("counter", 67, value={"from": 0, "to": 13.8, "prefix": "+", "suffix": "%", "at": "+0.3"}, caption="2026년 1월 7일 하루 주가 (네이버)", icon="chart_up")
sh("crowd", 68, count=26, emotion="excited", set="street", labels=[lab("시총 80조 첫 돌파 (보도)", "80조", "gold", size=110)])
sh("closeup", 69, who="es", side="right", set="office", time="day", emotion="excited", pose="celebrate",
   labels=[lab("종가 75만 원", "75만", "lime", x=600, y=860, size=130)])
sh("counter", [70, 71], value={"from": 0, "to": 153, "prefix": "약 ", "suffix": "조 원", "at": "+0.3"}, caption="6월 1일 보통주 시가총액 (계산)", icon="building",
   compare={"text": "연초보다 2.5배", "icon": "chart_up", "at": "2.5배입니다"})
sh("title", 72, text="꼭대기는 거기까지")
sh("chart", [73, 74], board="chalk", chart={"type": "line", "values": [750000, 640000, 581000, 511000], "trend": "down", "show_values": False, "title": "현대차 종가 6.1 → 6.23 (네이버)", "at": "6월"},
   labels=[lab("6월 23일 하루 -12.05%", "12.05%", "red"), lab("종가 51만 1천 원", "51만", "cream")])
sh("closeup", [75, 76], who="shopper", side="left", set="home", time="night", emotion="shocked", pose="stressed",
   labels=[lab("7월 20일 39만 9천 원", "39만", "cream", x=1350, y=300), lab("40만 원 깨짐 (보도)", "40만", "red", x=1350, y=860)])
sh("versus", [77, 78], colors=["#F6C7B6", "#D8F0D8"], left={"who": "foreign", "title": "외국인 순매도", "emotion": "calm", "pose": "arms_crossed", "at": "+0.2"},
   right={"who": "shopper", "title": "개인 순매수", "emotion": "nervous", "pose": "hold", "at": "개인이었습니다"},
   labels=[lab("10조 8,830억 원 (보도)", "10조", "red", x=960, y=900)])
sh("counter", 79, value={"from": 0, "to": 110500, "suffix": "억 원", "at": "+0.3"}, caption="개인 순매수 2026년 1월~7월 20일 (보도)", icon="coins")
sh("wide", 80, set="street", time="dusk", shop="울산 공장",
   chars=[ch("worker", 700, "worried", "arms_crossed"), ch("exec", 1200, "worried", "think", beats=[{"at": "타결됐습니다", "pose": "present", "emotion": "calm"}])],
   stamp={"text": "9월 2일 타결", "at": "타결됐습니다", "color": "green"})
sh("chart", [81, 82], board="white", chart={"type": "bar", "values": [4158300, 4000000], "labels": ["처음 목표", "낮춘 목표"], "suffix": "대", "title": "2026년 판매 목표 (현대차)", "show_values": True, "highlight": 1, "at": "목표를"},
   labels=[lab("3분기 판매 -11.3%", "11.3%", "red")])
sh("icon", 83, icons=[{"name": "money", "label": "원·달러 1,500원대", "at": "+0.2"}, {"name": "chart_down", "label": "1,300원대로", "at": "1,300원대로"}],
   labels=[lab("부담 (분석)", "부담이", "cream")])
sh("counter", [84, 85], value={"from": 0, "to": 66, "prefix": "-", "suffix": "%", "at": "+0.3"}, caption="6월 1일 꼭대기 → 11월 20일 종가 25만 3,000원 (계산)", icon="chart_down")
chap("성적표", "5장")
sh("closeup", [86, 87], who="m1", side="right", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "지금은 누가?", "at": "누가", "thought": True})
sh("icon", 88, icons=[{"name": "building", "text": "현대모비스", "label": "최대주주 22.50%", "at": "+0.2"}])
sh("wide", 89, set="office", era="modern", wall="blue", time="day",
   chars=[ch("es", 600, "confident", "present"), ch("munoz", 960, "smile", "idle"), ch("choi", 1320, "calm", "idle")],
   labels=[lab("대표이사 세 명", "세", "cream", x=960, y=230)])
sh("closeup", [90, 91], who="munoz", side="right", set="office", time="day", emotion="confident", pose="present",
   lower_third={"name": "호세 무뇨스", "sub": "대표이사 사장 (2025년 1월~)", "at": "무뇨스"},
   labels=[lab("첫 외국인 최고경영자 (보도)", "외국인", "lime", x=600, y=860, size=80)])
sh("map", 92, places=[{"name": "닛산 북미·중국", "x": 520, "y": 420}, {"name": "현대차 북미권역", "x": 1400, "y": 560}], vehicle="plane", at="2019년부터")
sh("icon", 93, icons=[{"name": "book", "text": "성적표", "label": "현대자동차 성적표", "at": "+0.2"}], stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("table", [94, 95], items=[{"type": "receipt", "title": "창업주 · 2대 회장", "rows": [["포니 첫해", "1만 726대"], ["점유율", "44%"]], "text": "판매 10년 3.2배 (보도)", "at": "+0.2"}])
sh("wide", [96, 97], set="office", era="old", wall="brick", time="night",
   chars=[ch("mk", 900, "worried", "hold")],
   props=[{"icon": "house", "x": 1450, "y": 690, "s": .6, "at": "한전"}],
   stamp={"text": "가장 비싼 결정", "at": "9.17%", "color": "red"}, labels=[lab("10조 5,500억 원", "10조", "gold", x=1450, y=300)])
sh("chart", [98, 99], board="chalk", chart={"type": "bar", "values": [178000, 253000], "labels": ["2020.10.14", "2026.11.20"], "suffix": "원", "title": "정의선 회장 취임 뒤 주가 (종가)", "show_values": True, "highlight": 1, "at": "17만"},
   labels=[lab("+42%", "42%", "lime")])
sh("table", [100, 101], items=[{"type": "receipt", "title": "잘한 결정 · 보스턴다이나믹스", "rows": [["2021년 평가", "1조 2,468억"], ["2026년 지분 1.08%", "631억 (보도)"]], "text": "현대글로비스 매수", "at": "+0.2"}],
   stamp={"text": "최고의 결정", "at": "631억", "color": "green"})
sh("counter", [102, 103], value={"from": 12468, "to": 58426, "prefix": "약 ", "suffix": "억 원", "at": "+0.3"}, caption="631억 원 ÷ 1.08%로 단순 환산 (계산)", icon="chart_up",
   compare={"text": "2021년의 약 4.7배", "icon": "trophy", "at": "4.7배입니다"})
sh("chart", [104, 105], board="white", chart={"type": "bar", "values": [153568, 51477], "labels": ["2026.6.1", "2026.11.20"], "suffix": "억 원", "title": "현대차 보통주 시가총액 (계산)", "show_values": True, "highlight": 1, "at": "시가총액은"},
   labels=[lab("약 51조 4,770억 원", "51조", "gold"), lab("꼭대기의 3분의 1", "3분의", "red")])
chap("반전", "6장")
sh("closeup", 106, who="m1", side="left", set="home", time="dusk", emotion="calm", pose="explain")
sh("counter", [107, 108], value={"from": 0, "to": 26772, "suffix": "억 원", "at": "+0.3"}, caption="2026년 3분기 영업이익 (DART)", icon="coins",
   compare={"text": "1년 전보다 +5.5%", "icon": "chart_up", "at": "5.5%"})
sh("icon", 109, icons=[{"name": "car", "label": "하이브리드 16만 7,414대", "at": "+0.2"}, {"name": "chart_up", "label": "+3.8%", "at": "3.8%"}])
sh("versus", 110, colors=["#D8F0D8", "#F6C7B6"], left={"who": "worker", "title": "영업이익 +5.5%", "emotion": "happy", "pose": "celebrate", "at": "+0.2"},
   right={"who": "shopper", "title": "주가 꼭대기의 1/3", "emotion": "shocked", "pose": "facepalm", "at": "주가는"})
sh("chart", [111, 112], board="white", chart={"type": "bar", "values": [9.17, 153], "labels": ["땅 산 날", "로봇 뒤 다섯 달"], "suffix": "%", "title": "주가를 흔든 두 장면 (보도·계산)", "show_values": False, "highlight": 1, "at": "땅을"},
   labels=[lab("하루 -9.17%", "9.17%", "red"), lab("다섯 달 2.5배", "2.5배가", "lime")])
sh("wide", 113, set="street", time="dusk", shop="조지아 공장", chars=[ch("atlas", 900, "calm", "idle")],
   props=[{"icon": "calendar", "x": 1450, "y": 640, "s": .6, "at": "2028년입니다"}], labels=[lab("투입은 2028년", "2028년입니다", "gold", x=1450, y=280)])
sh("walk", [114, 115], set="street", time="dusk", chars=[ch("es", 0, "confident", "hold")],
   labels=[lab("숙제는 다시 자동차", "숙제는", "lime", x=960, y=260)])
sh("wide", [116, 119], set="office", era="modern", wall="sand", time="day",
   chars=[ch("founder", 600, "happy", "wave"), ch("m1", 960, "happy", "wave"), ch("atlas", 1320, "smile", "celebrate")],
   labels=[lab("구독 · 좋아요", "구독과", "lime", x=960, y=230, size=130), lab("출처는 설명란", "출처는", "cream", x=960, y=420)],
   polaroid={"at": "출처는", "who": "atlas", "caption": "로봇이 올린 주가, 숙제는 다시 자동차"})

# 빈 화면 방지(2026-11-20 검수): 그래픽 장면의 첫 요소는 장면 시작 직후에 나오게 하고, 나머지만 대사 낱말에 맞춘다
for d in X:
    k = d.get("kind")
    if k == "icon" and d.get("icons"): d["icons"][0]["at"] = "+0.2"
    if k == "table" and d.get("items"): d["items"][0]["at"] = "+0.2"
    if k == "chart" and d.get("chart"): d["chart"]["at"] = "+0.3"
    if k == "counter" and d.get("value"): d["value"]["at"] = "+0.3"

story = {"title": "현대자동차_v2", "mood": "upbeat", "cast": {
    "founder": {"skin": "tan", "outfit": "suit", "color": "#3A3A44", "shirt": "#F2F2F2", "tie": "#7A1E2E", "hair": "slick", "hair_col": "#2A2420"},
    "mk": {"skin": "light", "outfit": "suit", "color": "#2E3A5C", "shirt": "#F2F2F2", "tie": "#B8862E", "hair": "short", "hair_col": "#6A6A6A"},
    "es": {"skin": "light", "outfit": "suit", "color": "#1F3A5F", "shirt": "#F2F2F2", "tie": "none", "hair": "short", "hair_col": "#2A2A2A"},
    "munoz": {"skin": "olive", "outfit": "suit", "color": "#4A4A55", "shirt": "#F2F2F2", "tie": "#2E5A8C", "hair": "short", "hair_col": "#8A8A8A", "glasses": True},
    "choi": {"skin": "tan", "outfit": "suit", "color": "#3E4E3A", "shirt": "#F2F2F2", "tie": "#5A5A5A", "hair": "short", "hair_col": "#3A3A3A"},
    "exec": {"skin": "fair", "outfit": "suit", "color": "#6A6A78", "tie": "#2E2E36", "hair": "bald"},
    "worker": {"skin": "tan", "outfit": "tshirt", "color": "#2E5A8C", "hair": "short", "hair_col": "#1E1A18", "hat": "cap", "hat_col": "#2E5A8C"},
    "atlas": {"skin": "#C8CCD2", "outfit": "hoodie", "color": "#9AA3AD", "hair": "none"},
    "m1": {"skin": "fair", "outfit": "sweater", "color": "#5E8C6A", "hair": "curly", "hair_col": "#3A2C22"},
    "shopper": {"skin": "fair", "outfit": "tshirt", "color": "#D0703A", "hair": "long", "hair_col": "#2A2420"},
    "foreign": {"skin": "light", "outfit": "suit", "color": "#2A2A2A", "tie": "#8C1E1E", "hair": "short", "hair_col": "#C8A060"}},
  "shots": X}
for d in X:
    if d.get("kind") == "walk":
        for c in d.get("chars", []): c.pop("x", None)
json.dump(story, open(os.path.join(P, "story.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(X), "shots")
