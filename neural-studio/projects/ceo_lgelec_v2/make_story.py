#!/usr/bin/env python3
"""LG전자 v2 스토리보드."""
import json, os
P = os.path.dirname(os.path.abspath(__file__)); X = []
def sh(kind, s, **k):
    d = {"kind": kind}
    if s is not None: d["s"] = s if isinstance(s, list) else [s]
    d.update(k); X.append(d)
def lab(text, at, color="lime", **k): return dict(text=text, at=at, color=color, **k)
def ch(id, x, emotion="neutral", pose="idle", **k): return dict(id=id, x=x, emotion=emotion, pose=pose, **k)
def chap(t, n): sh("title", None, text=t, sub=n, hold=1.6)

# 인트로 · 라디오 80대 → 89조, 그리고 접자 오른 주가
# 0초 프레임부터 그림이 보이도록 첫 장면은 세트+인물이 있는 wide (빈 바탕 시작 금지)
sh("wide", 0, set="office", era="old", wall="sand", time="day", tag="1959년 · 부산", calendar="1959 11",
   chars=[ch("koo", 820, "confident", "hold", beats=[{"at": "80대였습니다", "pose": "celebrate", "emotion": "excited"}])],
   props=[{"icon": "gift", "x": 1350, "y": 720, "s": .55, "at": "+0.0"}],
   labels=[lab("첫 국산 라디오 80대", "80대였습니다", "gold", x=1400, y=300, size=110)])
sh("counter", 1, value={"from": 0, "to": 89, "suffix": "조 원", "at": "89조"}, caption="2025년 매출 (DART)", icon="trophy")
sh("table", 2, items=[{"type": "newspaper", "title": "2021년 1월 20일", "text": "휴대폰 사업 재검토", "at": "+0.2"}],
   stamp={"text": "주가 +12.8%", "at": "12.8%", "color": "red"})
sh("skyline", 3, time="day", labels=[lab("LG전자", "LG전자입니다", size=170)])
chap("판돈", "1장")
sh("wide", [4, 5], set="office", era="old", wall="sand", time="day", tag="1958년 10월", calendar="1958 10",
   chars=[ch("koo", 900, "confident", "present", beats=[{"at": "세웁니다", "pose": "celebrate", "emotion": "excited"}])],
   lower_third={"name": "구인회", "sub": "금성사 창업주", "at": "구인회는"}, labels=[lab("플라스틱 → 전자", "플라스틱", "gold", x=1400, y=260)])
sh("icon", [6, 7], icons=[{"name": "calendar", "top": "1959", "text": "11월", "label": "국산 라디오 A-501", "at": "A-501을"},
   {"name": "gift", "label": "첫 출고 80대 (보도)", "at": "80대였다고"}])
sh("closeup", [8, 9], who="koo", side="left", set="office", time="day", emotion="excited", pose="present",
   labels=[lab("1966년 흑백 TV", "흑백", "gold", x=1350, y=300), lab("라디오 → 가전", "가전", "lime", x=1350, y=860)])
sh("table", [10, 11], items=[{"type": "contract", "title": "상호 변경", "text": "금성사 → LG전자", "at": "+0.2", "stamp": {"text": "1995년 1월", "at": "LG전자로"}},
   {"type": "newspaper", "title": "배터리 이야기", "text": "16편 LG에너지솔루션", "at": "16편에서"}])
sh("icon", [12, 13], icons=[{"name": "house", "label": "가전", "at": "가전"}, {"name": "phone", "label": "휴대폰", "at": "휴대폰"}, {"name": "car", "label": "자동차", "at": "자동차입니다"}])
sh("closeup", [14, 16], who="m1", side="left", set="home", time="night", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "?", "at": "실수는", "thought": True}, labels=[lab("가장 비싼 실수?", "실수는", "red", x=1350, y=860, size=110)],
   stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("map", 17, places=[{"name": "서울", "x": 1450, "y": 470}, {"name": "미국", "x": 450, "y": 430}], vehicle="plane", at="+0.3",
   labels=[lab("첫 번째 판돈", "판돈은", "gold")])
sh("table", [18, 19], hand="exec", items=[{"type": "contract", "title": "제니스 인수 (1995년 7월)", "text": "보통주 57.7%", "at": "+0.2", "stamp": {"text": "3억 5천만 달러", "at": "3억"}}])
sh("closeup", 20, who="exec", side="right", set="office", time="night", emotion="worried", pose="stressed",
   labels=[lab("적자 탈출 실패", "벗어나지", "red", x=600, y=860)])
sh("table", 21, items=[{"type": "newspaper", "title": "1999년 말 (보도)", "text": "미국 법원 회생계획 승인", "at": "+0.2"}],
   stamp={"text": "채권 2억 달러 → 주식", "at": "2억", "color": "red"})
sh("counter", [22, 23], value={"from": 0, "to": 100, "suffix": "%", "at": "100%"}, caption="제니스 지분 (보도)", icon="building",
   compare={"text": "비싼 수업료 · 미국 발판", "icon": "coins", "at": "수업료였지만"})
chap("결정", "2장")
sh("icon", [24, 25], icons=[{"name": "phone", "label": "손바닥만 한 기계", "at": "+0.2"}, {"name": "calendar", "top": "1995", "text": "진출", "label": "휴대폰 시장 진출", "at": "시장에"}])
sh("crowd", [26, 27], count=24, emotion="excited", set="street", tag="2005년 11월",
   labels=[lab("초콜릿폰", "초콜릿폰이", "gold", size=120), lab("누적 1,000만 대+", "1,000만", "lime")])
sh("counter", 28, value={"from": 0, "to": 1, "suffix": "억 대+", "at": "1억"}, caption="한 해 휴대폰 판매 (보도)", icon="phone",
   compare={"text": "한때 세계 3위", "icon": "trophy", "at": "3위까지"})
sh("wide", 29, set="street", time="day", chars=[ch("m1", 900, "shocked", "hold", beats=[{"at": "뒤집힙니다", "pose": "facepalm", "emotion": "shocked"}])],
   labels=[lab("손가락으로 미는 화면", "손가락으로", "gold", x=1400, y=260)])
sh("versus", 30, colors=["#D8F0D8", "#F6C7B6"], left={"who": "exec", "title": "피처폰 · 세계 3위", "emotion": "happy", "pose": "celebrate", "at": "+0.2"},
   right={"who": "exec", "title": "스마트폰 · 점유율 1~2%", "emotion": "shocked", "pose": "facepalm", "at": "점유율은"})
sh("chart", 31, board="chalk", chart={"type": "bar", "values": [140000, 59000], "labels": ["2015년", "2019년"], "suffix": "억", "title": "휴대폰 사업 매출 (보도)", "show_values": True, "highlight": 1, "trend": "down", "at": "+0.3"})
sh("closeup", [32, 33], who="m1", side="right", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "몇 분기?", "at": "몇", "thought": True})
sh("counter", [34, 35], value={"from": 0, "to": 23, "suffix": "분기", "at": "23분기입니다"}, caption="연속 영업적자 · 2015년 2분기부터 (보도)", icon="chart_down",
   compare={"text": "5년 넘게 영업이익 0번", "icon": "warning", "at": "한"})
sh("closeup", 36, who="m1", side="left", set="home", time="night", emotion="shocked", pose="facepalm",
   stamp={"text": "약 5조 원", "at": "5조", "color": "red"}, labels=[lab("쌓인 영업적자 (보도)", "쌓인", "cream", x=1350, y=860)])
chap("위기", "3장")
sh("table", 37, hand="kwon", items=[{"type": "phone", "messages": ["휴대폰 사업 운영 방향", "직원들에게 보낸 이메일"], "at": "+0.2"}],
   lower_third={"name": "권봉석", "sub": "당시 LG전자 사장", "at": "권봉석"})
sh("closeup", 38, who="kwon", side="right", set="office", time="day", emotion="calm", pose="explain",
   bubble={"who": "kwon", "text": "모든 가능성 검토", "at": "가능성을"})
sh("chart", 39, board="white", chart={"type": "bar", "values": [148000, 167000], "labels": ["2021.1.19", "2021.1.20"], "suffix": "원", "title": "LG전자 종가 (네이버)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("+12.8%", "12.8%", "red")])
sh("crowd", 40, count=18, emotion="excited", set="void", labels=[lab("시장은 박수", "박수를", "gold", size=120)])
sh("wide", [41, 42], set="board", time="day", tag="2021년 4월 5일",
   chars=[ch("kwon", 900, "confident", "present", beats=[{"at": "끝내기로", "pose": "push", "emotion": "calm"}]), ch("exec", 1350, "worried", "idle")],
   stamp={"text": "휴대폰 종료", "at": "끝내기로", "color": "red"})
sh("table", [43, 44], items=[{"type": "contract", "title": "영업정지 공시 (DART)", "text": "경쟁 심화 · 지속적 사업 부진", "at": "+0.2", "stamp": {"text": "핵심 사업 집중", "at": "집중이었습니다"}}])
sh("counter", [45, 46], value={"from": 0, "to": 52171, "suffix": "억 원", "at": "2,171억"}, caption="휴대폰 사업 2020년 매출 (DART)", icon="phone",
   compare={"text": "회사 전체 매출의 8.2%", "icon": "target", "at": "8.2%였습니다"})
sh("walk", [47, 48], set="street", time="dusk", chars=[ch("eng", 0, "sad", "idle")],
   labels=[lab("26년 만에 막", "막을", "cream", x=700, y=260), lab("다른 사업본부로", "사업본부와", "lime", x=1300, y=260)])
sh("closeup", 49, who="m1", side="left", set="home", time="dusk", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "빈자리는?", "at": "빈자리는", "thought": True})
chap("베팅", "4장")
sh("icon", [50, 51], icons=[{"name": "car", "label": "답: 자동차", "at": "+0.2"}, {"name": "calendar", "top": "2013", "text": "8년 전", "label": "이미 깔린 판돈", "at": "8년"}])
sh("table", [52, 53], hand="exec", items=[{"type": "contract", "title": "흡수합병 (DART)", "text": "브이이엔에스 · 자동차 설계", "at": "+0.2", "stamp": {"text": "2013년 7월", "at": "흡수합병합니다"}}])
sh("wide", [54, 55], set="office", era="modern", wall="blue", time="day",
   chars=[ch("eng", 700, "confident", "present"), ch("exec", 1200, "smile", "idle", beats=[{"at": "VS사업본부입니다", "pose": "point", "emotion": "excited"}])],
   labels=[lab("VS사업본부", "VS사업본부입니다", "gold", x=960, y=250)])
sh("icon", 56, icons=[{"name": "car", "label": "자동차 회사 X", "at": "+0.2"}, {"name": "factory", "label": "자동차 안의 부품 O", "at": "부품을"}])
sh("map", [57, 58], places=[{"name": "서울", "x": 1450, "y": 470}, {"name": "오스트리아", "x": 620, "y": 380}], vehicle="plane", at="+0.3",
   labels=[lab("ZKW 지분 70%", "70%에", "gold"), lab("9,845억 원", "9,845억", "lime")])
sh("icon", 59, icons=[{"name": "car", "text": "EV", "label": "전기차 모터 사업 분할", "at": "+0.2"}, {"name": "handshake", "label": "엘지마그나이파워트레인", "at": "엘지마그나이파워트레인을"}])
sh("counter", [60, 61], value={"from": 0, "to": 9364, "suffix": "억 원", "at": "9,364억"}, caption="2021년 VS 영업손실 (DART)", icon="chart_down",
   compare={"text": "오래 돈을 까먹은 판", "icon": "warning", "at": "까먹었습니다"})
sh("closeup", [62, 63], who="exec", side="left", set="office", time="day", emotion="excited", pose="celebrate",
   stamp={"text": "첫 흑자 1,696억", "at": "1,696억", "color": "green"}, labels=[lab("2022년", "2022년", "gold", x=1350, y=300)])
sh("crowd", 64, count=20, emotion="excited", set="void",
   labels=[lab("성과급 550% (보도)", "550%를", "gold", size=110)])
sh("closeup", 65, who="eng", side="right", set="office", time="day", emotion="smile", pose="shrug",
   labels=[lab("그동안은 위로금", "위로금을", "cream", x=600, y=860)])
sh("chart", [66, 67], board="white", chart={"type": "bar", "values": [1696, 1158, 5590], "labels": ["2022년", "2024년", "2025년"], "suffix": "억", "title": "VS 영업이익 (DART)", "show_values": True, "highlight": 2, "at": "+0.3"},
   labels=[lab("역대 최대", "최대였습니다", "red"), lab("매출 11조+", "11조", "gold")])
sh("wide", [68, 69], set="office", era="modern", wall="grey", time="day", tag="2022년 1월",
   chars=[ch("cho", 900, "confident", "present", beats=[{"at": "대표이사에", "pose": "wave", "emotion": "smile"}])],
   lower_third={"name": "조주완", "sub": "LG전자 대표 (2022.1~2026.3)", "at": "조주완"})
sh("counter", 70, value={"from": 0, "to": 892009, "suffix": "억 원", "at": "+0.3"}, caption="2025년 매출 · 사상 최대 (DART)", icon="trophy")
sh("chart", 71, board="chalk", chart={"type": "bar", "values": [34197, 24784], "labels": ["2024년", "2025년"], "suffix": "억", "title": "영업이익 (DART)", "show_values": True, "highlight": 1, "trend": "down", "at": "+0.3"},
   labels=[lab("-27.5%", "27.5%", "red")])
sh("table", [72, 73], items=[{"type": "newspaper", "title": "2025년 4분기", "text": "영업손실 약 1,090억 원", "at": "+0.2", "ring_at": "1,090억"}],
   stamp={"text": "9년 만의 적자", "at": "9년", "color": "red"})
sh("icon", 74, icons=[{"name": "warning", "label": "희망퇴직 비용", "at": "+0.2"}, {"name": "coins", "label": "미국 관세 (보도)", "at": "관세가"}])
sh("closeup", [75, 76], who="cho", side="right", set="office", time="night", emotion="worried", pose="facepalm",
   labels=[lab("TV·모니터 -7,509억", "7,509억", "red", x=600, y=860, size=100)])
sh("map", [77, 78], places=[{"name": "서울", "x": 1450, "y": 420}, {"name": "인도", "x": 650, "y": 560}], vehicle="plane", at="+0.3",
   labels=[lab("지분 15% 매각", "15%를", "gold"), lab("약 1조 8천억 원 (보도)", "1조", "lime")])
sh("icon", 79, icons=[{"name": "laptop", "text": "로봇", "label": "베어로보틱스", "at": "+0.2"}, {"name": "target", "label": "지분 61.14%", "at": "61.14%를"}])
sh("wide", [80, 81], set="board", time="day", tag="2026년 3월",
   chars=[ch("cho", 650, "smile", "wave"), ch("ryu", 1250, "confident", "present", enter="right", beats=[{"at": "류재철", "pose": "wave", "emotion": "smile"}])],
   lower_third={"name": "류재철", "sub": "LG전자 대표 (2026.3~)", "at": "류재철"})
sh("closeup", [82, 83], who="ryu", side="left", set="office", time="day", emotion="confident", pose="hips",
   labels=[lab("2016년 에어컨 담당 상무", "상무에서", "cream", x=1350, y=300, size=80), lab("생활가전 사업본부장", "사업본부장을", "lime", x=1350, y=860)])
chap("성적표", "5장")
sh("icon", [84, 85], icons=[{"name": "book", "text": "성적표", "label": "지금 성적은?", "at": "+0.2"}])
sh("counter", [86, 87], value={"from": 0, "to": 713778, "suffix": "억 원", "at": "+0.3"}, caption="2026년 1~9월 매출 (DART)", icon="chart_up",
   compare={"text": "1년 전보다 +9.2%", "icon": "coins", "at": "9.2%"})
sh("chart", [88, 89], board="chalk", chart={"type": "bar", "values": [25874, 40347], "labels": ["2025년 1~9월", "2026년 1~9월"], "suffix": "억", "title": "영업이익 (DART)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("+55.9%", "55.9%", "red")])
sh("versus", 90, colors=["#F6C7B6", "#D8F0D8"], left={"who": "ryu", "title": "2025년 TV·모니터 -7,509억", "emotion": "sad", "pose": "facepalm", "at": "+0.2"},
   right={"who": "ryu", "title": "2026년 1~9월 +7,379억", "emotion": "happy", "pose": "celebrate", "at": "7,379억"})
sh("counter", [91, 92], value={"from": 0, "to": 5931, "suffix": "억 원", "at": "5,931억"}, caption="VS 영업이익 2026년 1~9월 (DART)", icon="car",
   compare={"text": "2025년 한 해(5,590억)를 넘음", "icon": "trophy", "at": "넘었습니다"})
sh("closeup", 93, who="ryu", side="right", set="office", time="night", emotion="worried", pose="think",
   labels=[lab("3분기 7,819억 · 전분기 절반", "7,819억", "red", x=600, y=860, size=90)])
sh("icon", [94, 95], icons=[{"name": "book", "text": "성적표", "label": "숫자로만", "at": "+0.2"}, {"name": "gift", "label": "시작: 라디오 80대", "at": "80대였습니다"}],
   stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("table", [96, 97], items=[{"type": "receipt", "title": "조주완 대표 재임 주가", "rows": [["2022.1.7", "137,500원"], ["2026.3.23", "109,500원"]], "text": "-20.4%", "at": "+0.2"}],
   stamp={"text": "약 -20%", "at": "20%", "color": "red"})
sh("chart", 98, board="white", chart={"type": "bar", "values": [109500, 128700], "labels": ["2026.3.23", "2026.11.20"], "suffix": "원", "title": "류재철 대표 취임 뒤 종가 (네이버)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("약 +18%", "18%", "green")])
sh("icon", 99, icons=[{"name": "building", "label": "시가총액 약 21조 원", "at": "+0.2"}])
sh("table", [100, 101], items=[{"type": "receipt", "title": "가장 잘한 결정 · 전장", "rows": [["2021년", "-9,364억"], ["2025년", "+5,590억"]], "text": "VS 영업이익 (DART)", "at": "+0.2"}],
   stamp={"text": "최고의 결정", "at": "5,590억", "color": "green"})
sh("closeup", [102, 103], who="m1", side="left", set="home", time="night", emotion="shocked", pose="facepalm",
   stamp={"text": "가장 비싼 실수", "at": "휴대폰입니다", "color": "red"}, labels=[lab("휴대폰 누적 영업적자 약 5조", "5조", "cream", x=1350, y=860, size=90)])
sh("icon", [104, 105], icons=[{"name": "building", "label": "최대주주 · 지주회사 LG", "at": "+0.2"}, {"name": "coins", "label": "지분 35.26%", "at": "35.26%를"}])
chap("반전", "6장")
sh("closeup", 106, who="m1", side="right", set="home", time="dusk", emotion="calm", pose="explain")
sh("counter", [107, 108], value={"from": 0, "to": 88000, "suffix": "원", "at": "+0.3"}, caption="2026년 1월 12일 종가 · 연중 최저 (네이버)", icon="chart_down")
sh("crowd", 109, count=30, emotion="excited", set="street",
   labels=[lab("하루 +30% 가까이 × 3번", "세", "gold", size=100)])
sh("closeup", 110, who="m1", side="right", set="home", time="day", emotion="excited", pose="point",
   bubble={"who": "m1", "text": "로봇!", "at": "로봇"}, labels=[lab("젠슨 황 방한 기대 (보도)", "젠슨", "lime", x=600, y=860, size=80)])
sh("chart", [111, 112], board="chalk", chart={"type": "bar", "values": [88000, 392500], "labels": ["2026.1.12", "2026.6.2"], "suffix": "원", "title": "LG전자 종가 (네이버)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("약 4.5배", "4.5배가", "red")])
sh("wide", [113, 114], set="street", time="night", chars=[ch("m1", 900, "excited", "celebrate", beats=[{"at": "67.2%", "pose": "facepalm", "emotion": "shocked"}])],
   stamp={"text": "-67.2%", "at": "67.2%", "color": "red"}, labels=[lab("11월 20일 12만 8,700원", "12만", "cream", x=1450, y=260, size=80)])
sh("versus", 115, colors=["#D8F0D8", "#F6E0B6"], left={"who": "ryu", "title": "영업이익 +55.9%", "emotion": "confident", "pose": "present", "at": "+0.2"},
   right={"who": "m1", "title": "급등 이유: 기대 (보도)", "emotion": "excited", "pose": "celebrate", "at": "기대였습니다"})
sh("title", 116, text="라디오 → TV → 휴대폰 → 자동차")
sh("table", 117, items=[{"type": "newspaper", "title": "2021년 1월 20일", "text": "휴대폰 접을 수도", "at": "+0.2"}],
   stamp={"text": "+12.8%", "at": "12.8%", "color": "red"})
sh("closeup", 118, who="ryu", side="left", set="office", time="dusk", emotion="thinking", pose="think",
   bubble={"who": "ryu", "text": "로봇?", "at": "로봇에", "thought": True},
   labels=[lab("4.5배", "4.5배로", "gold", x=1350, y=300), lab("실적표에 아직 줄 없음", "줄도", "cream", x=1350, y=860, size=80)])
sh("wide", [119, 122], set="office", era="modern", wall="blue", time="day",
   chars=[ch("eng", 600, "happy", "wave"), ch("m1", 960, "happy", "wave"), ch("ryu", 1320, "smile", "celebrate")],
   labels=[lab("구독 · 좋아요", "구독과", "lime", x=960, y=230, size=130), lab("출처는 설명란", "출처는", "cream", x=960, y=420)],
   polaroid={"at": "출처는", "who": "ryu", "caption": "라디오 80대에서 89조, 다음 판돈은 로봇?"})

# 빈 화면 방지(2026-11-20 검수): 그래픽 장면의 첫 요소는 장면 시작 직후에 나오게 하고, 나머지만 대사 낱말에 맞춘다
for d in X:
    k = d.get("kind")
    if k == "icon" and d.get("icons"): d["icons"][0]["at"] = "+0.2"
    if k == "table" and d.get("items"): d["items"][0]["at"] = "+0.2"
    if k == "chart" and d.get("chart"): d["chart"]["at"] = "+0.3"
    if k == "counter" and d.get("value"): d["value"]["at"] = "+0.3"

story = {"title": "LG전자_v2", "mood": "dramatic", "cast": {
    "koo": {"skin": "light", "outfit": "suit", "color": "#4A3F35", "shirt": "#F2F2F2", "tie": "#7A1E2E", "hair": "short", "hair_col": "#2A2420", "glasses": True},
    "exec": {"skin": "tan", "outfit": "suit", "color": "#2E3A5C", "shirt": "#F2F2F2", "tie": "#A50034", "hair": "slick", "hair_col": "#2A2420"},
    "kwon": {"skin": "fair", "outfit": "suit", "color": "#3A3A44", "shirt": "#F2F2F2", "tie": "#2E6FB8", "hair": "short", "hair_col": "#4A4A4A"},
    "cho": {"skin": "light", "outfit": "suit", "color": "#1F2A3A", "shirt": "#F2F2F2", "tie": "none", "hair": "short", "hair_col": "#1E1A18", "glasses": True},
    "ryu": {"skin": "tan", "outfit": "suit", "color": "#5A4A3A", "shirt": "#F2F2F2", "tie": "#A50034", "hair": "bald"},
    "eng": {"skin": "olive", "outfit": "sweater", "color": "#6A8CA8", "hair": "bun", "hair_col": "#2A2018"},
    "m1": {"skin": "fair", "outfit": "hoodie", "color": "#5E8C6A", "hair": "curly", "hair_col": "#3A2C22"}},
  "shots": X}
for d in X:
    if d.get("kind") == "walk":
        for c in d.get("chars", []): c.pop("x", None)
json.dump(story, open(os.path.join(P, "story.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(X), "shots")
