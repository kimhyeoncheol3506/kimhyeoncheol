#!/usr/bin/env python3
"""하이브 v2 스토리보드."""
import json, os
P = os.path.dirname(os.path.abspath(__file__)); X = []
def sh(kind, s, **k):
    d = {"kind": kind}
    if s is not None: d["s"] = s if isinstance(s, list) else [s]
    d.update(k); X.append(d)
def lab(text, at, color="lime", **k): return dict(text=text, at=at, color=color, **k)
def ch(id, x, emotion="neutral", pose="idle", **k): return dict(id=id, x=x, emotion=emotion, pose=pose, **k)
def chap(t, n): sh("title", None, text=t, sub=n, hold=1.6)

# 2026 종가 흐름 (네이버 증권 일봉): 2/19 고점 → 3/23 → 4/21 → 9/3 → 11/4 저점
PX = [404500, 290500, 249000, 176000, 139100]

# 인트로 · 돌아왔는데 떨어졌다
sh("crowd", 0, count=30, emotion="excited", set="street", labels=[lab("2026년, 귀환", "돌아왔습니다", "gold", size=130)])
sh("counter", [1, 2], value={"from": 0, "to": 36740, "suffix": "억 원", "at": "3조"}, caption="2026년 1~9월 매출 (DART)", icon="chart_up",
   compare={"text": "작년 1년 치보다 1조 원 넘게", "icon": "trophy", "at": "1조"})
sh("chart", 3, board="chalk", chart={"type": "line", "values": PX, "trend": "down", "show_values": False, "title": "하이브 종가 2026 (네이버 증권)", "at": "주가는"},
   labels=[lab("-65.6%", "65.6%까지", "red", size=150)])
sh("skyline", 4, time="day", labels=[lab("하이브", "하이브입니다", size=180)])
chap("판돈", "1장")
sh("wide", [5, 6], set="office", era="old", wall="sand", time="day", tag="2005년 · 서울", calendar="2005 2",
   chars=[ch("bang", 900, "confident", "present", beats=[{"at": "세웁니다", "pose": "celebrate", "emotion": "excited"}])],
   lower_third={"name": "방시혁", "sub": "빅히트 창업자", "at": "방시혁이"}, labels=[lab("빅히트엔터테인먼트", "빅히트엔터테인먼트라는", "gold", x=1350, y=260)])
sh("closeup", 7, who="bang", side="left", set="office", time="day", emotion="smile", pose="explain", labels=[lab("JYP 공동 창업 출신", "JYP엔터테인먼트를", "cream", x=1350, y=860)])
sh("icon", [8, 9], tag="2013년", icons=[{"name": "heart", "text": "7", "label": "일곱 명의 보이그룹", "at": "일곱"}, {"name": "trophy", "label": "방탄소년단", "at": "방탄소년단입니다"}])
sh("map", [10, 11], places=[{"name": "서울", "x": 1450, "y": 560}, {"name": "미국", "x": 520, "y": 420}], vehicle="plane", at="빌보드",
   labels=[lab("빌보드 싱글 차트 1위", "1위에", "gold"), lab("한국 그룹 처음 (보도)", "처음이었다고", "cream")])
sh("table", [12, 13], hand="bang", items=[{"type": "contract", "title": "주식시장 상장", "text": "빅히트 · 2020년 10월 15일", "at": "+0.2", "stamp": {"text": "공모가 13만 5천 원", "at": "공모가는"}}])
sh("chart", 14, board="white", chart={"type": "bar", "values": [135000, 351000, 258000], "labels": ["공모가", "첫날 최고", "첫날 종가"], "suffix": "원", "title": "상장 첫날 (보도)", "show_values": True, "highlight": 2, "at": "35만"})
sh("closeup", [15, 17], who="m1", side="left", set="home", time="night", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "?", "at": "실수는", "thought": True}, labels=[lab("가장 비싼 실수?", "실수는", "red", x=1350, y=860, size=110)])
sh("wide", [18, 19], set="board", time="day", chars=[ch("m2", 760, "thinking", "point", beats=[{"at": "말고", "pose": "shrug", "emotion": "worried"}])],
   bubble={"who": "m2", "text": "방탄소년단 말고는?", "at": "말고"}, labels=[lab("시장의 질문", "질문은", "cream", x=1400, y=260)])
sh("chart", [20, 21], board="chalk", chart={"type": "bar", "values": [97.4, 87.7], "labels": ["2019년", "2020년 상반기"], "suffix": "%", "title": "매출 중 방탄소년단 비중 (보도)", "show_values": True, "highlight": 0, "at": "97.4%가"})
sh("closeup", 22, who="bang", side="right", set="office", time="dusk", emotion="worried", pose="think", stamp={"text": "그룹 하나", "at": "그룹", "color": "red"})
chap("결정", "2장")
sh("wide", 23, set="board", time="day",
   chars=[ch("bang", 640, "confident", "arms_crossed", beats=[{"at": "바구니를", "pose": "push", "emotion": "excited"}, {"at": "늘리는", "pose": "celebrate", "emotion": "happy"}])],
   props=[{"icon": "gift", "x": 1150, "y": 700, "s": .5, "at": "바구니를"}, {"icon": "gift", "x": 1400, "y": 700, "s": .5, "at": "늘리는"}, {"icon": "gift", "x": 1650, "y": 700, "s": .5, "at": "것이었습니다"}],
   labels=[lab("바구니를 늘린다", "바구니를", "lime", x=1400, y=300)])
sh("icon", 24, tag="2021년 1월", icons=[{"name": "handshake", "label": "네이버 브이라이브 양수", "at": "네이버의"}, {"name": "phone", "label": "팬 플랫폼 위버스", "at": "위버스를"}])
sh("table", [25, 26], items=[{"type": "contract", "title": "상호 변경", "text": "빅히트 → 하이브", "at": "+0.2", "stamp": {"text": "2021년 3월", "at": "하이브로"}},
                            {"type": "letter", "title": "레이블 분할 (7월)", "text": "자회사 빅히트뮤직", "at": "빅히트뮤직이라는"}])
sh("closeup", 27, who="bang", side="left", set="office", time="night", emotion="excited", pose="hips",
   bubble={"who": "bang", "text": "가장 큰 판", "icon": "target", "at": "판돈을"})
sh("table", [28, 29], hand="bang", items=[{"type": "contract", "title": "인수 계약 · 2021년 4월", "text": "이타카 홀딩스 지분 100%", "at": "+0.2", "stamp": {"text": "1조 728억 원", "at": "1조"}}],
   labels=[lab("9억 5천만 달러", "9억", "gold")])
sh("map", 30, places=[{"name": "서울", "x": 1450, "y": 560}, {"name": "미국", "x": 520, "y": 420}], vehicle="plane", at="이타카는",
   labels=[lab("팝스타 매니지먼트 회사 (보도)", "매니지먼트를", "cream")])
sh("crowd", 31, count=20, emotion="happy", set="street", tag="2022년", labels=[lab("르세라핌 · 뉴진스 데뷔", "르세라핌", "pink", size=110)])
sh("counter", [32, 33], value={"from": 0, "to": 4228, "suffix": "억 원", "at": "4,228억"}, caption="에스엠 지분 인수 계약 (DART)", icon="moneybag",
   compare={"text": "지분 14.8%", "icon": "target", "at": "14.8%를"})
sh("versus", [34, 35], colors=["#D9E4F6", "#F6EBB6"], left={"who": "bang", "title": "하이브", "emotion": "confident", "pose": "point", "at": "+0.2"},
   right={"who": "rival", "title": "카카오 · 주당 15만 원", "emotion": "smug", "pose": "hips", "at": "카카오가"},
   labels=[lab("에스엠 쟁탈전", "에스엠", "red", x=960, y=900)])
sh("wide", 36, set="office", era="modern", wall="grey", time="dusk", tag="2023년 3월 12일",
   chars=[ch("bang", 900, "sad", "idle", beats=[{"at": "멈춘다고", "pose": "shrug", "emotion": "tired"}])],
   stamp={"text": "인수 중단", "at": "멈춘다고", "color": "red"})
sh("closeup", [37, 38], who="m1", side="right", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "충격은 어디서?", "at": "충격은", "thought": True})
chap("위기", "3장")
sh("icon", 39, icons=[{"name": "gift", "label": "바구니가 아니라", "at": "+0.2"}, {"name": "heart", "label": "가장 큰 그 한 그룹", "at": "그룹이었습니다"}])
sh("table", 40, items=[{"type": "phone", "title": "2022년 6월 14일 밤", "messages": ["단체 활동, 잠시 쉼", "개인 활동에 집중"], "at": "+0.2"}],
   tag="2022년 6월")
sh("chart", [41, 42], board="white", chart={"type": "bar", "values": [193000, 145000], "labels": ["6월 14일", "6월 15일"], "suffix": "원", "title": "하이브 종가 (보도)", "show_values": True, "highlight": 1, "at": "24.87%"},
   labels=[lab("-24.87%", "24.87%", "red"), lab("시총 약 2조 원 증발", "2조", "red")])
sh("icon", 43, icons=[{"name": "calendar", "top": "입대", "text": "군", "label": "멤버들 차례로 입대", "at": "군에"}, {"name": "hourglass", "label": "공백", "at": "입대합니다"}])
sh("wide", [44, 45], set="office", era="modern", wall="teal", time="night", tag="2024년 4월 22일",
   chars=[ch("m2", 800, "nervous", "stressed")], props=[{"icon": "warning", "x": 1450, "y": 660, "s": .6, "at": "감사에"}],
   labels=[lab("자회사 어도어 감사 착수", "감사에", "red", x=1400, y=280)])
sh("counter", 46, value={"from": 0, "to": 7.81, "suffix": "%", "prefix": "-", "at": "7.81%"}, caption="2024년 4월 22일 하루 하락률 (보도)", icon="chart_down")
sh("table", 47, items=[{"type": "newspaper", "title": "법원 (보도)", "text": "관련 소송 · 일부 1심 판결", "at": "+0.2", "ring_at": "1심"}],
   labels=[lab("2026년 11월 13일", "11월", "gold")])
sh("closeup", 48, who="bang", side="left", set="office", time="night", emotion="worried", pose="think",
   bubble={"who": "bang", "text": "계산서?", "icon": "warning", "at": "계산서가"})
sh("table", 49, items=[{"type": "receipt", "title": "미국 법인 투자 주식 (2025년)", "rows": [["손상차손", "2,796억 원"]], "text": "DART 별도 기준", "at": "+0.2"}],
   stamp={"text": "2,796억 원", "at": "2,796억", "color": "red"})
sh("icon", 50, icons=[{"name": "building", "label": "사들인 회사의 값어치", "at": "+0.2"}, {"name": "chart_down", "label": "장부 값보다 떨어짐", "at": "떨어졌다고"}],
   stamp={"text": "손상차손", "at": "인정하는", "color": "red"})
sh("chart", 51, board="chalk", chart={"type": "bar", "values": [22556, 26499], "labels": ["2024년", "2025년"], "suffix": "억 원", "title": "연간 매출 (DART)", "show_values": True, "highlight": 1, "at": "2조"},
   labels=[lab("사상 최대", "최대였습니다", "lime")])
sh("versus", [52, 53], colors=["#D8F0D8", "#F6C7B6"], left={"who": "m2", "title": "매출 사상 최대", "emotion": "happy", "pose": "celebrate", "at": "+0.2"},
   right={"who": "bang", "title": "영업이익 493억 · -73%", "emotion": "shocked", "pose": "facepalm", "at": "493억"},
   labels=[lab("순이익 -2,544억 원", "2,544억", "red", x=960, y=900)])
chap("베팅", "4장")
sh("crowd", [54, 55], count=30, emotion="excited", set="street", tag="2026년 3월 · 광화문",
   labels=[lab("3년 9개월 만의 새 앨범", "3년", "gold", size=100), lab("광화문 컴백 공연", "광화문에서", "lime", size=100)])
sh("counter", 56, value={"from": 0, "to": 404500, "suffix": "원", "at": "40만"}, caption="2026년 2월 19일 종가 · 올해 최고 (네이버 증권)", icon="chart_up")
sh("closeup", 57, who="m1", side="left", set="home", time="day", emotion="shocked", pose="facepalm", stamp={"text": "15%대 급락", "at": "15%대", "color": "red"},
   labels=[lab("공연 뒤 첫 거래일 (보도)", "첫", "cream", x=1350, y=860)])
sh("map", [58, 59], places=[{"name": "고양", "x": 1450, "y": 560}, {"name": "세계 34개 도시", "x": 560, "y": 400}], vehicle="plane", at="월드투어가",
   labels=[lab("월드투어 85회 (보도)", "85회", "gold")])
sh("wide", [60, 61], set="board", time="night", chars=[ch("bang", 900, "worried", "idle", beats=[{"at": "수사입니다", "pose": "think", "emotion": "nervous"}])],
   labels=[lab("방시혁 의장 수사", "수사입니다", "red", x=1400, y=280)])
sh("table", 62, items=[{"type": "letter", "title": "경찰이 본 혐의 (수사 단계)", "text": "상장 계획 없다고 알려 지분 매각", "at": "+0.2"}])
sh("icon", [63, 64], icons=[{"name": "lock", "label": "4월 21일 구속영장 신청", "at": "신청합니다"}, {"name": "warning", "label": "검찰: 반려 · 재신청도 기각", "at": "돌려보냈고"}])
sh("table", 65, items=[{"type": "newspaper", "title": "9월 3일 (보도)", "text": "5명 불구속 송치", "at": "+0.2", "ring_at": "불구속"}])
sh("icon", 66, icons=[{"name": "book", "text": "경찰", "label": "경찰 판단 (보도)", "at": "+0.2"}, {"name": "moneybag", "label": "부당이득 2,631억 원으로 봄", "at": "2,631억"}])
sh("closeup", 67, who="bang", side="right", set="office", time="day", emotion="calm", pose="present_left",
   labels=[lab("의장 측: 소명해 왔다", "소명해", "cream", x=600, y=300), lab("하이브: 혐의 부인", "부인하고", "cream", x=600, y=860)])
sh("icon", [68, 69], icons=[{"name": "clock", "label": "기소 여부 미정 (11월 23일 보도)", "at": "+0.2"}, {"name": "book", "text": "법원", "label": "유무죄 판단 아직 없음", "at": "유무죄에"}])
sh("chart", [70, 71], board="white", chart={"type": "line", "values": PX, "trend": "down", "show_values": False, "title": "하이브 종가 2026 (네이버 증권)", "at": "주가는"},
   labels=[lab("11월 4일 13만 9,100원", "13만", "red", size=90), lab("-65.6%", "65.6%", "red", size=140)])
chap("성적표", "5장")
sh("closeup", [72, 73], who="m1", side="right", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "누가 이끌었나?", "at": "누구였을까요", "thought": True})
sh("wide", [74, 75], set="office", era="modern", wall="plum", time="day", chars=[ch("bang", 900, "confident", "present")],
   lower_third={"name": "방시혁", "sub": "하이브 이사회 의장 · 최대주주", "at": "의장입니다"}, labels=[lab("지분 28.41%", "28.41%를", "gold", x=1400, y=280)])
sh("closeup", 76, who="park", side="left", set="office", time="day", emotion="smile", pose="present",
   lower_third={"name": "박지원", "sub": "전 대표이사 (2021.7~2024.9)", "at": "박지원이"}, labels=[lab("넥슨 코리아 대표 출신", "넥슨", "cream", x=1350, y=300)])
sh("wide", [77, 78], set="office", era="modern", wall="blue", time="day", chars=[ch("lee", 900, "confident", "present")],
   lower_third={"name": "이재상", "sub": "하이브 대표이사 (2024.9~)", "at": "이재상"}, labels=[lab("구글 · 현대자동차", "구글과", "cream", x=1400, y=280)])
sh("table", 79, hand="bang", items=[{"type": "letter", "title": "임직원 보상 재원 (보도)", "text": "의장 주식 54만여 주 무상 증여", "at": "+0.2"}],
   stamp={"text": "무상 증여", "at": "무상으로", "color": "red"})
sh("counter", 80, value={"from": 0, "to": 2550, "prefix": "약 ", "suffix": "억 원", "at": "2,550억"}, caption="2026년 1분기 주식보상 비용 (보도)", icon="coins",
   compare={"text": "1분기 영업이익 적자", "icon": "chart_down", "at": "적자가"})
sh("icon", 81, icons=[{"name": "book", "text": "성적표", "label": "하이브 성적표", "at": "+0.2"}], stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("chart", [82, 83], board="chalk", chart={"type": "bar", "values": [7963, 26499], "labels": ["2020년", "2025년"], "suffix": "억 원", "title": "연간 매출 (DART)", "show_values": True, "highlight": 1, "at": "7,963억"},
   labels=[lab("3.3배", "3.3배가", "lime", size=130)])
sh("counter", [84, 85], value={"from": 0, "to": 36740, "suffix": "억 원", "at": "3조"}, caption="2026년 1~9월 매출 (DART)", icon="trophy",
   compare={"text": "공연 1조 4,632억 원", "icon": "heart", "at": "공연"})
sh("map", 86, places=[{"name": "한국", "x": 1450, "y": 560}, {"name": "북미", "x": 520, "y": 420}], vehicle="plane", at="북미",
   labels=[lab("북미 1조 5,367억 원 · 41.8%", "41.8%가", "gold")])
sh("chart", [87, 88], board="white", chart={"type": "bar", "values": [4509, 14632], "labels": ["2024년 공연", "2026년 1~9월 공연"], "suffix": "억 원", "title": "공연 매출 (DART)", "show_values": True, "highlight": 1, "at": "4,509억"},
   stamp={"text": "최고의 결정", "at": "잘한", "color": "green"}, labels=[lab("3.2배", "3.2배가", "lime")])
sh("table", [89, 90], items=[{"type": "receipt", "title": "비싼 실수 (진행 중)", "rows": [["이타카 인수", "1조 728억"], ["누적 손상차손", "4,783억"]], "text": "손상차손 (보도)", "at": "+0.2"}],
   stamp={"text": "가장 비싼 실수", "at": "4,783억", "color": "red"})
sh("chart", [91, 92], board="chalk", chart={"type": "bar", "values": [135000, 183400], "labels": ["공모가", "2026.11.20"], "suffix": "원", "title": "하이브 주가 (공모가 · 종가)", "show_values": True, "highlight": 1, "at": "공모가"},
   labels=[lab("+35.9%", "35.9%", "lime")])
sh("counter", [93, 94], value={"from": 0, "to": 79058, "suffix": "억 원", "at": "7조"}, caption="시가총액 (2026년 11월 20일 종가로 계산)", icon="building",
   compare={"text": "올해 꼭대기보다 -54.7%", "icon": "chart_down", "at": "54.7%"})
chap("반전", "6장")
sh("closeup", 95, who="m1", side="left", set="home", time="dusk", emotion="calm", pose="explain")
sh("chart", [96, 97], board="white", chart={"type": "bar", "values": [7272, 15257], "labels": ["2025년 3분기", "2026년 3분기"], "suffix": "억 원", "title": "분기 매출 (DART)", "show_values": True, "highlight": 1, "at": "1조"},
   labels=[lab("영업이익 1,885억 원 흑자", "1,885억", "lime")])
sh("versus", [98, 99], colors=["#D8F0D8", "#F6C7B6"], left={"who": "lee", "title": "장사: 영업이익 1,885억", "emotion": "happy", "pose": "celebrate", "at": "+0.2"},
   right={"who": "m2", "title": "장부 끝줄: -68억", "emotion": "shocked", "pose": "facepalm", "at": "68억"},
   labels=[lab("아직 빨간색", "빨간색입니다", "red", x=960, y=900)])
sh("map", [100, 101], places=[{"name": "서울", "x": 1300, "y": 600}, {"name": "도쿄", "x": 1650, "y": 420}], vehicle="plane", at="키홀더를",
   labels=[lab("키홀더 공개매수 · 최대 1,057억 원", "1,057억", "gold")])
sh("icon", 102, icons=[{"name": "heart", "label": "그룹 하나에 기대지 않으려고", "at": "+0.2"}, {"name": "building", "label": "미국 회사 · 1조 원", "at": "1조"}])
sh("crowd", 103, count=30, emotion="excited", set="street", labels=[lab("다시 끌어올린 건, 귀환 (보도)", "귀환이었다고", "gold", size=100)])
sh("title", [104, 105], text="하이브는 아직, 답을 쓰는 중")
sh("wide", [106, 109], set="office", era="modern", wall="sand", time="day",
   chars=[ch("bang", 600, "happy", "wave"), ch("m1", 960, "happy", "wave"), ch("lee", 1320, "smile", "celebrate")],
   labels=[lab("구독 · 좋아요", "구독과", "lime", x=960, y=230, size=130), lab("출처는 설명란", "출처는", "cream", x=960, y=420)],
   polaroid={"at": "출처는", "who": "m1", "caption": "6년 전 질문, 아직 답을 쓰는 중"})

# 빈 화면 방지(2026-11-20 검수): 그래픽 장면의 첫 요소는 장면 시작 직후에 나오게 하고, 나머지만 대사 낱말에 맞춘다
for d in X:
    k = d.get("kind")
    if k == "icon" and d.get("icons"): d["icons"][0]["at"] = "+0.2"
    if k == "table" and d.get("items"): d["items"][0]["at"] = "+0.2"
    if k == "chart" and d.get("chart"): d["chart"]["at"] = "+0.3"
    if k == "counter" and d.get("value"): d["value"]["at"] = "+0.3"

story = {"title": "하이브_v2", "mood": "dramatic", "cast": {
    "bang": {"skin": "light", "outfit": "sweater", "color": "#2B2B33", "hair": "short", "hair_col": "#1E1A18", "glasses": True},
    "park": {"skin": "fair", "outfit": "suit", "color": "#2E4A8C", "shirt": "#F2F2F2", "tie": "#5A7FC8", "hair": "slick", "hair_col": "#2A2A2A"},
    "lee": {"skin": "tan", "outfit": "suit", "color": "#2F5A4A", "shirt": "#F2F2F2", "tie": "none", "hair": "short", "hair_col": "#3A2C22"},
    "m1": {"skin": "fair", "outfit": "hoodie", "color": "#7A5EA8", "hair": "curly", "hair_col": "#3A2C22"},
    "m2": {"skin": "olive", "outfit": "suit", "color": "#6A6A78", "tie": "#2E2E36", "hair": "bald"},
    "rival": {"skin": "light", "outfit": "suit", "color": "#C9A21E", "shirt": "#F2F2F2", "tie": "#3A3A44", "hair": "short", "hair_col": "#2A2420", "moustache": True}},
  "shots": X}
for d in X:
    if d.get("kind") == "walk":
        for c in d.get("chars", []): c.pop("x", None)
json.dump(story, open(os.path.join(P, "story.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(X), "shots")
