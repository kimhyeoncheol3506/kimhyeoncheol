#!/usr/bin/env python3
"""아모레퍼시픽 v2 스토리보드."""
import json, os
P = os.path.dirname(os.path.abspath(__file__)); X = []
def sh(kind, s, **k):
    d = {"kind": kind}
    if s is not None: d["s"] = s if isinstance(s, list) else [s]
    d.update(k); X.append(d)
def lab(text, at, color="lime", **k): return dict(text=text, at=at, color=color, **k)
def ch(id, x, emotion="neutral", pose="idle", **k): return dict(id=id, x=x, emotion=emotion, pose=pose, **k)
def chap(t, n): sh("title", None, text=t, sub=n, hold=1.6)
OIL = {"color": "#C98A2E", "cap": "#6B3A1E"}      # 동백 머릿기름 병 (상표 없음)
GOLD = {"color": "#E2B65A", "cap": "#7A4A1E"}     # 인삼 한방 화장품 병 (상표 없음)
GREEN = {"color": "#8CC87A", "cap": "#3E7A4A"}    # 중저가 화장품 병 (상표 없음)
SNAIL = {"color": "#E8EEF4", "cap": "#9AA6B4"}    # 에센스 병 (상표 없음)

# ── 훅
sh("closeup", 0, who="mother", side="right", set="home", time="dusk", emotion="calm", pose="hold",
   bubble={"who": "mother", "text": "동백 머릿기름", "at": "동백"}, labels=[lab("개성", "개성에서", "gold")])
sh("counter", 1, value={"from": 0, "to": 24, "suffix": "조 원+", "at": "24조"}, caption="2015년 7월 시가총액 (보도)", icon="trophy",
   compare={"text": "황제주", "icon": "coins", "at": "황제주가"})
sh("chart", 2, board="white", chart={"type": "bar", "values": [288000, 251500], "labels": ["2017.3.2", "2017.3.3"], "suffix": "원", "title": "아모레퍼시픽 주가 (수정주가)", "show_values": True, "highlight": 1, "at": "하루에"},
   labels=[lab("하루 -12%", "12%", "red")])
sh("map", [3, 4], places=[{"name": "한국", "x": 1420, "y": 520}, {"name": "바다 건너", "x": 560, "y": 430}], vehicle="plane", at="바다",
   labels=[lab("회사 잘못이 아니었다", "잘못해서가", "cream", x=960, y=880, size=90)])
sh("skyline", 5, time="day", labels=[lab("아모레퍼시픽", "아모레퍼시픽입니다", size=160)])
chap("판돈", "1장")
sh("wide", 6, set="home", wall="sand", time="day", tag="1932년 · 개성",
   chars=[ch("mother", 860, "happy", "hold", beats=[{"at": "팔기", "pose": "present"}])],
   props=[{"icon": "vial", "x": 1450, "y": 700, "s": .5, "at": "머릿기름을", **OIL}],
   lower_third={"name": "윤독정", "sub": "창업주의 어머니", "at": "윤독정"})
sh("closeup", 7, who="founder", side="left", set="home", time="day", emotion="smile", pose="hold",
   lower_third={"name": "서성환", "sub": "아모레퍼시픽 창업주", "at": "서성환입니다"})
sh("wide", 8, set="office", era="old", wall="green", time="day", calendar="1945",
   chars=[ch("founder", 900, "confident", "present", beats=[{"at": "세웁니다", "pose": "celebrate", "emotion": "excited"}])],
   props=[{"icon": "factory", "x": 1450, "y": 690, "s": .6, "at": "태평양화학공업사를"}],
   labels=[lab("태평양화학공업사", "태평양화학공업사를", "gold", x=1300, y=250)])
sh("icon", 9, tag="1951년", icons=[{"name": "vial", "label": "식물성 에이비씨 포마드", "at": "포마드를", **OIL}])
sh("map", 10, places=[{"name": "한국", "x": 1400, "y": 500}, {"name": "첫 수출", "x": 520, "y": 450}], vehicle="ship", at="수출",
   labels=[lab("1964년 첫 화장품 수출", "1964년", "gold")])
sh("walk", 11, set="street", time="day", chars=[{"id": "seller", "emotion": "happy", "pose": "hold"}], shop="집집마다",
   labels=[lab("방문판매 · 아모레", "아모레를", "lime")])
sh("table", 12, items=[{"type": "letter", "title": "1966년", "text": "세계 첫 한방 화장품 · 인삼크림", "at": "인삼크림이"}], stamp={"text": "세계 첫 한방", "at": "한방", "color": "green"})
sh("closeup", 13, who="founder", side="right", set="office", time="day", emotion="smug", pose="hold",
   props=[{"icon": "vial", "x": 520, "y": 700, "s": .5, "at": "인삼크림", **GOLD}], labels=[lab("30여 년 뒤의 씨앗", "30여", "gold", x=560, y=300)])
sh("closeup", [14, 15], who="m1", side="left", set="office", time="night", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "?", "at": "실수는", "thought": True}, labels=[lab("가장 비싼 실수?", "실수는", "red", x=1350, y=860, size=110)])
sh("icon", 16, icons=[{"name": "book", "label": "아모레퍼시픽 성적표", "at": "성적표를"}], stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
chap("결정", "2장")
sh("wide", [17, 18], set="office", era="modern", wall="blue", time="day", tag="1997년 3월",
   chars=[ch("son", 900, "confident", "present", beats=[{"at": "서른넷이었습니다", "pose": "hips"}])],
   lower_third={"name": "서경배", "sub": "2대 · 현 회장", "at": "서경배가"}, labels=[lab("서른넷", "서른넷이었습니다", "gold", x=1400, y=300)])
sh("closeup", 19, who="son", side="left", set="office", time="night", emotion="worried", pose="stressed", labels=[lab("외환위기", "외환위기가", "red", x=1350, y=320, size=130)])
sh("icon", 20, icons=[{"name": "building", "label": "금융 · 전자 · 스포츠", "at": "금융부터"}, {"name": "building", "label": "계열사 24곳", "at": "24곳이나"}])
sh("closeup", 21, who="son", side="right", set="office", time="day", emotion="confident", pose="push", labels=[lab("가지치기", "가지를", "lime", x=560, y=320)])
sh("table", 22, hand="son", items=[{"type": "contract", "title": "계열사 정리", "text": "24곳 → 9곳", "at": "가지를", "stamp": {"text": "정리", "at": "팔거나"}}],
   labels=[lab("2010년 9곳", "9곳만", "gold")])
sh("versus", 23, colors=["#E0E0F0", "#F6E0B6"], left={"who": "son", "title": "백화점 같던 회사", "emotion": "tired", "pose": "shrug", "at": "백화점"},
   right={"who": "son", "title": "화장품 가게 하나", "emotion": "excited", "pose": "present", "at": "화장품"})
sh("wide", 24, set="office", era="modern", wall="cream", time="day", chars=[ch("son", 760, "confident", "present", beats=[{"at": "가장", "pose": "hold"}])],
   props=[{"icon": "trophy", "x": 1400, "y": 690, "s": .6, "at": "좋은"}], labels=[lab("가장 좋은 물건", "좋은", "gold", x=1350, y=280)])
sh("icon", [25, 26], icons=[{"name": "vial", "label": "인삼크림 기술", "at": "인삼크림의", **GOLD}, {"name": "vial", "label": "설화수 (1997)", "at": "설화수입니다", **GOLD}])
sh("counter", 27, value={"from": 0, "to": 1000, "suffix": "억 원", "at": "1천억"}, caption="설화수 · 출시 4년 만의 매출 (보도)", icon="chart_up")
sh("counter", 28, value={"from": 0, "to": 10000, "suffix": "억 원", "at": "1조"}, caption="2015년 설화수 한 해 매출 · 국내 뷰티 브랜드 최초 (회사 발표)", icon="trophy",
   compare={"text": "한 해 1조 원", "icon": "moneybag", "at": "넘깁니다"})
sh("icon", 29, icons=[{"name": "vial", "label": "이니스프리 (2000)", "at": "이니스프리가", **GREEN}])
sh("walk", 30, set="street", time="day", chars=[{"id": "son", "emotion": "excited", "pose": "idle"}], shop="설화수 · 이니스프리",
   labels=[lab("두 다리로", "두", "lime")])
sh("map", [31, 32], places=[{"name": "서울", "x": 1450, "y": 470}, {"name": "상하이", "x": 620, "y": 560}], vehicle="plane", at="상하이에",
   labels=[lab("2014년 상하이 사업장", "2014년", "gold")])
sh("crowd", 33, count=22, emotion="happy", set="street", labels=[lab("면세점", "면세점에서", "lime", size=140)])
sh("counter", [34, 35], value={"from": 0, "to": 445000, "suffix": "원", "at": "44만"}, caption="2015년 7월 주가 꼭대기 (종가)", icon="chart_up",
   compare={"text": "시가총액 24조 원+ · 코스피 5위", "icon": "trophy", "at": "24조"})
sh("table", 36, items=[{"type": "receipt", "title": "2016년 실적", "rows": [["매출", "5조 6,454억"], ["영업이익", "8,481억"]], "text": "사상 최대", "at": "매출은"}],
   stamp={"text": "사상 최대", "at": "사상", "color": "green"})
sh("counter", 37, value={"from": 0, "to": 10828, "suffix": "억 원", "at": "1조"}, caption="2016년 그룹 영업이익 · 화장품 회사 첫 1조 (보도)", icon="trophy")
chap("위기", "3장")
sh("closeup", [38, 39], who="m1", side="right", set="office", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "하루 -12%?", "at": "하루", "thought": True})
sh("title", 40, text="화장품이 아니라, 미사일 방어 체계")
sh("chart", [41, 42], board="chalk", chart={"type": "bar", "values": [441000, 421500], "labels": ["7월 7일", "7월 8일"], "suffix": "원", "title": "2016년 사드 배치 발표 전후 주가", "show_values": False, "highlight": 1, "at": "사드"},
   labels=[lab("-4.4%", "4.4%", "red")])
sh("table", 43, items=[{"type": "newspaper", "title": "2017년 3월", "text": "한국행 여행 상품 판매 중단", "at": "중국", "ring_at": "막았다는"}])
sh("closeup", [44, 45], who="son", side="left", set="office", time="night", emotion="shocked", pose="stressed", tag="2017년 3월 3일",
   stamp={"text": "-12.85%", "at": "12.85%", "color": "red", "x": 1350, "y": 500})
sh("chart", 46, board="white", chart={"type": "bar", "values": [806, 417], "labels": ["2016", "2017"], "suffix": "만 명", "title": "중국인 방한객 (보도)", "show_values": True, "highlight": 1, "at": "806만"},
   labels=[lab("-48%", "48%", "red")])
sh("crowd", [47, 48], count=10, emotion="sad", set="street", labels=[lab("국내 매출 -16%", "16%", "red", size=120)])
sh("chart", [49, 50], board="chalk", who="son", chart={"type": "bar", "values": [8481, 5964], "labels": ["2016", "2017"], "suffix": "억", "title": "영업이익 (회사 발표)", "show_values": True, "highlight": 1, "at": "8,481억"},
   stamp={"text": "-2,517억", "at": "2,517억", "color": "red"})
sh("closeup", 51, who="son", side="left", set="office", time="night", emotion="nervous", pose="stressed", labels=[lab("이니스프리도", "이니스프리도", "orange", x=1350, y=300)])
sh("chart", 52, board="white", chart={"type": "bar", "values": [7679, 3486], "labels": ["2016", "2020"], "suffix": "억", "title": "이니스프리 국내 매출 (보도)", "show_values": True, "highlight": 1, "at": "7,679억"})
sh("chart", 53, board="chalk", chart={"type": "bar", "values": [1965, 70], "labels": ["2016", "2020"], "suffix": "억", "title": "이니스프리 영업이익 (보도)", "show_values": True, "highlight": 1, "at": "1,965억"},
   labels=[lab("내려앉다", "내려앉습니다", "red")])
sh("icon", 54, icons=[{"name": "shopping", "text": "607곳", "label": "2019년 중국 매장", "at": "607곳에서"}, {"name": "shopping", "text": "397곳", "label": "2021년 상반기", "at": "397곳으로"}])
sh("table", [55, 56], items=[{"type": "receipt", "title": "시가총액", "rows": [["2015년 7월", "24조 원+"], ["2019년 8월", "7조 6,288억"]], "text": "약 3분의 1", "at": "시가총액은"}],
   stamp={"text": "3분의 1", "at": "3분의", "color": "red"})
chap("반격", "4장")
sh("walk", 57, set="street", time="dusk", chars=[{"id": "son", "emotion": "thinking", "pose": "idle"}], labels=[lab("새 바구니", "바구니를", "lime")])
sh("wide", 58, set="office", era="modern", wall="teal", time="day", tag="2021년",
   chars=[ch("son", 760, "confident", "present", beats=[{"at": "지분", "pose": "point"}])],
   props=[{"icon": "handshake", "x": 1400, "y": 690, "s": .6, "at": "지분"}], labels=[lab("지분 38.4% · 1,800억 원", "38.4%", "gold", x=1350, y=260)])
sh("icon", 59, icons=[{"name": "vial", "label": "달팽이 점액 에센스", "at": "달팽이", **SNAIL}])
sh("wide", 60, set="home", wall="blue", time="day", chars=[ch("buyer", 760, "excited", "hold", beats=[{"at": "1위에", "pose": "celebrate"}])],
   props=[{"icon": "laptop", "x": 1400, "y": 700, "s": .6, "at": "아마존의", "text": "1위"}], labels=[lab("미국 아마존 페이셜 세럼 1위", "1위에", "lime", x=1300, y=280, size=80)])
sh("table", [61, 62], hand="son", items=[{"type": "contract", "title": "코스알엑스 나머지 지분 인수", "text": "7,551억 원", "at": "계약서에", "stamp": {"text": "쾅", "at": "도장을"}}],
   labels=[lab("2023년 10월", "2023년", "gold")])
sh("counter", 63, value={"from": 0, "to": 9351, "suffix": "억 원", "at": "9,351억"}, caption="코스알엑스 인수 합계 · 회사 사상 최대 (공시·보도)", icon="handshake",
   compare={"text": "1,800억 + 7,551억", "icon": "coins", "at": "합치면"})
sh("map", 64, places=[{"name": "한국", "x": 1450, "y": 470}, {"name": "미국", "x": 440, "y": 430}], vehicle="car", at="미국으로",
   labels=[lab("달리는 차를 통째로", "통째로", "lime")])
sh("closeup", 65, who="son", side="left", set="office", time="night", emotion="tired", pose="stressed", labels=[lab("바닥", "바닥은", "red", x=1350, y=320, size=140)])
sh("chart", 66, board="chalk", chart={"type": "bar", "values": [8481, 1082], "labels": ["2016", "2023"], "suffix": "억", "title": "영업이익 (DART·회사 발표)", "show_values": True, "highlight": 1, "at": "1,082억"},
   labels=[lab("약 8분의 1", "8분의", "red")])
sh("counter", [67, 68], value={"from": 0, "to": 3358, "suffix": "억 원", "at": "3,358억"}, caption="2025년 영업이익 (DART)", icon="chart_up",
   compare={"text": "2024년 2,205억 원", "icon": "coins", "at": "2,205억"})
sh("closeup", 69, who="m1", side="right", set="office", time="day", emotion="happy", pose="present", labels=[lab("매출 4조 2,528억 원", "4조", "gold", x=560, y=320, size=90)])
sh("map", 70, places=[{"name": "한국", "x": 1450, "y": 470}, {"name": "해외", "x": 520, "y": 430}], vehicle="ship", at="해외",
   labels=[lab("해외 매출 1조 9,091억", "1조", "lime")])
sh("versus", 71, colors=["#D8F0D8", "#E0E0F0"], left={"who": "buyer", "title": "해외 이익 2,099억", "emotion": "excited", "pose": "celebrate", "at": "해외"},
   right={"who": "m1", "title": "국내 이익 1,449억", "emotion": "calm", "pose": "pockets", "at": "국내"})
sh("wide", 72, set="office", era="modern", wall="green", time="day",
   chars=[ch("son", 700, "happy", "present", beats=[{"at": "흑자로", "pose": "celebrate", "emotion": "excited"}]), ch("m1", 1200, "smile", "idle")],
   labels=[lab("중화권 흑자 전환", "흑자로", "lime", x=960, y=230)])
sh("counter", 73, value={"from": 0, "to": 3593, "suffix": "억 원", "at": "3,593억"}, caption="2026년 1~9월 영업이익 (잠정 공시)", icon="chart_up",
   compare={"text": "2025년 1년 치 3,358억 원 넘음", "icon": "trophy", "at": "넘었습니다"})
chap("성적표", "5장")
sh("wide", [74, 75], set="board", time="day", chars=[ch("son", 600, "neutral", "present")],
   labels=[lab("숫자로만", "숫자로만", "red", x=1250, y=300, size=140), lab("시작: 동백 머릿기름", "동백", "cream", x=1250, y=520)])
sh("counter", 76, value={"from": 0, "to": 42528, "suffix": "억 원", "at": "매출은"}, caption="2025년 매출 (DART)", icon="trophy",
   compare={"text": "영업이익 3,358억 원", "icon": "coins", "at": "영업이익은"})
sh("list", 77, number=1, text="가장 잘한 결정: 설화수", who="son", emotion="excited", badge="gold")
sh("table", 78, items=[{"type": "receipt", "title": "잘한 결정", "rows": [["1966", "인삼크림"], ["1997", "설화수"], ["2015", "한 해 1조 원"]], "text": "브랜드 하나", "at": "잘한"}],
   stamp={"text": "최고의 결정", "at": "1조", "color": "green"})
sh("list", 79, number=2, text="가장 비싼 실수: 한 바구니", who="son", emotion="embarrassed", badge="red")
sh("table", [80, 81], items=[{"type": "receipt", "title": "비싼 실수", "rows": [["한 바구니", "중국 관광객"], ["2017 영업이익", "-2,517억"]], "text": "-30%", "at": "비싼"}],
   stamp={"text": "가장 비싼 실수", "at": "2,517억", "color": "red"})
sh("skyline", 82, time="dusk", labels=[lab("꼭대기 44만 5천 원", "44만", "gold", size=120)])
sh("chart", 83, board="chalk", chart={"type": "bar", "values": [445000, 138500], "labels": ["2015.7.2", "2026.11.20"], "suffix": "원", "title": "아모레퍼시픽 주가", "show_values": True, "highlight": 1, "at": "2026년"},
   labels=[lab("약 -69%", "69%", "red")])
sh("counter", 84, value={"from": 0, "to": 81012, "suffix": "억 원", "at": "8조"}, caption="2026년 11월 20일 시가총액 (네이버 증권)", icon="building")
chap("반전", "6장")
sh("closeup", [85, 86], who="m1", side="right", set="office", time="day", emotion="thinking", pose="think", bubble={"who": "m1", "text": "지금은 누가?", "at": "누가", "thought": True})
sh("wide", 87, set="office", era="old", wall="sand", time="dusk", chars=[ch("founder", 960, "calm", "tiphat")], labels=[lab("2003년 별세", "2003년", "cream", x=1450, y=300)])
sh("wide", [88, 89], set="office", era="modern", wall="blue", time="day",
   chars=[ch("son", 700, "calm", "present"), ch("ceo", 1220, "confident", "present", beats=[{"at": "김승환", "pose": "wave"}])],
   lower_third={"name": "김승환", "sub": "아모레퍼시픽 대표이사 (2023년 3월~)", "at": "김승환"}, labels=[lab("대표이사 2명", "두", "gold", x=960, y=230)])
sh("closeup", 90, who="ceo", side="left", set="office", time="day", emotion="confident", pose="explain", labels=[lab("1969년생 · 인사조직실장 출신", "1969년생", "cream", x=1350, y=320, size=80)])
sh("icon", 91, icons=[{"name": "building", "label": "아모레퍼시픽홀딩스 시총 2조 1,026억", "at": "아모레퍼시픽홀딩스는"}])
sh("closeup", 92, who="mother", side="left", set="home", time="dusk", emotion="calm", pose="hold", labels=[lab("처음의 이야기", "처음의", "cream", x=1350, y=320)])
sh("map", 93, places=[{"name": "한국", "x": 1450, "y": 470}, {"name": "세계", "x": 520, "y": 430}], vehicle="plane", at="바다",
   labels=[lab("다시 바다 건너", "다시", "lime")])
sh("chart", [94, 95], board="white", chart={"type": "bar", "values": [20, 42], "labels": ["미주", "유럽·중동·아프리카"], "suffix": "%", "title": "2025년 매출 증가율 (회사 발표)", "show_values": True, "highlight": 1, "at": "미주"},
   labels=[lab("한 나라가 아니다", "한", "lime")])
sh("versus", 96, colors=["#D8F0D8", "#F6C7B6"], left={"who": "son", "title": "이익은 돌아왔다", "emotion": "happy", "pose": "present", "at": "이익이"},
   right={"who": "m1", "title": "주가는 꼭대기의 1/3 아래", "emotion": "worried", "pose": "think", "at": "주가는"})
sh("closeup", [97, 98], who="m1", side="right", set="office", time="night", emotion="thinking", pose="think", bubble={"who": "m1", "text": "바구니가 여러 개?", "at": "바구니가", "thought": True})
sh("wide", 99, set="home", wall="sand", time="dusk", chars=[ch("mother", 700, "calm", "hold"), ch("son", 1200, "embarrassed", "shrug")],
   props=[{"icon": "vial", "x": 950, "y": 720, "s": .45, "at": "동백기름", **OIL}], labels=[lab("24조 원짜리 회사가 되고 나서야", "24조", "gold", x=960, y=230, size=80)])
sh("title", 100, text="달걀은 한 바구니에 담지 말 것")
sh("wide", [101, 104], set="office", era="modern", wall="sand", time="day",
   chars=[ch("son", 600, "happy", "wave"), ch("m1", 960, "happy", "wave"), ch("ceo", 1320, "smile", "celebrate")],
   labels=[lab("구독 · 좋아요", "구독과", "lime", x=960, y=230, size=130), lab("출처는 설명란", "출처는", "cream", x=960, y=420)],
   polaroid={"at": "출처는", "who": "son", "caption": "동백기름에서 24조, 그리고 바구니 여러 개"})

# 빈 화면 방지(2026-11-20 검수): 그래픽 장면의 첫 요소는 장면 시작 직후에 나오게 하고, 나머지만 대사 낱말에 맞춘다
for d in X:
    k = d.get("kind")
    if k == "icon" and d.get("icons"): d["icons"][0]["at"] = "+0.2"
    if k == "table" and d.get("items"): d["items"][0]["at"] = "+0.2"
    if k == "chart" and d.get("chart"): d["chart"]["at"] = "+0.3"
    if k == "counter" and d.get("value"): d["value"]["at"] = "+0.3"

story = {"title": "아모레퍼시픽_v2", "mood": "upbeat", "cast": {
    "mother": {"skin": "light", "outfit": "dress", "color": "#8C5A7A", "hair": "bun", "hair_col": "#3A3A3A"},
    "founder": {"skin": "tan", "outfit": "suit", "color": "#3E5A3A", "shirt": "#F2F2F2", "tie": "#B8862E", "hair": "short", "hair_col": "#2A2420"},
    "son": {"skin": "light", "outfit": "suit", "color": "#24335A", "shirt": "#F2F2F2", "tie": "#C9A24A", "hair": "slick", "hair_col": "#1E1A18", "glasses": True},
    "ceo": {"skin": "fair", "outfit": "suit", "color": "#5A5A64", "shirt": "#F2F2F2", "tie": "#2E8C8C", "hair": "short", "hair_col": "#3A3A3A"},
    "m1": {"skin": "fair", "outfit": "sweater", "color": "#5E8C6A", "hair": "curly", "hair_col": "#3A2C22"},
    "seller": {"skin": "tan", "outfit": "dress", "color": "#D2603A", "hair": "long", "hair_col": "#2A2420"},
    "buyer": {"skin": "brown", "outfit": "hoodie", "color": "#E0A030", "hair": "short", "hair_col": "#1E1A18", "hat": "cap", "hat_col": "#2E5A8C"}},
  "shots": X}
json.dump(story, open(os.path.join(P, "story.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(X), "shots")
