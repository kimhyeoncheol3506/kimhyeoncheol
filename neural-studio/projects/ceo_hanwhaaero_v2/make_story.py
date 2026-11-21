#!/usr/bin/env python3
"""한화에어로스페이스 v2 스토리보드. 무기 그림 없이 공장·지도·계약서·차트로만 보여 준다."""
import json, os
P = os.path.dirname(os.path.abspath(__file__)); X = []
def sh(kind, s, **k):
    d = {"kind": kind}
    if s is not None: d["s"] = s if isinstance(s, list) else [s]
    d.update(k); X.append(d)
def lab(text, at, color="lime", **k): return dict(text=text, at=at, color=color, **k)
def ch(id, x, emotion="neutral", pose="idle", **k): return dict(id=id, x=x, emotion=emotion, pose=pose, **k)
def chap(t, n): sh("title", None, text=t, sub=n, hold=1.6)

# ── 인트로
sh("counter", 0, value={"from": 0, "to": 79, "suffix": "억 원", "at": "79억"}, caption="2014년 삼성테크윈 연결 영업이익 (DART)", icon="coins")
sh("table", 1, hand="seller", items=[{"type": "contract", "title": "지분 매각", "text": "삼성 → 한화", "at": "삼성은", "stamp": {"text": "매각", "at": "팔았습니다"}}])
sh("counter", 2, value={"from": 0, "to": 30893, "suffix": "억 원", "at": "3조"}, caption="2025년 연결 영업이익 (DART)", icon="trophy", compare={"text": "11년 뒤", "icon": "calendar", "at": "11년"})
sh("chart", 3, board="chalk", chart={"type": "line", "values": [1537000, 1138000, 919000, 1031000, 603000], "trend": "down", "show_values": False, "title": "2026년 주가 (4월 7일 → 11월 20일)", "at": "꼭대기에서"},
   labels=[lab("꼭대기 대비 -60% 넘게", "60%", "red")])
sh("skyline", 4, time="day", labels=[lab("한화에어로스페이스", "한화에어로스페이스입니다", size=140)])
chap("판돈", "1장")
sh("wide", [5, 6, 7], set="office", era="old", wall="sand", time="day", calendar="1977 8", tag="1977년 8월 · 삼성정밀공업",
   chars=[ch("seller", 760, "confident", "present", beats=[{"at": "삼성테크윈으로", "pose": "explain"}])],
   props=[{"icon": "factory", "x": 1400, "y": 690, "s": .6, "at": "삼성정밀공업이었습니다"}],
   labels=[lab("1987 삼성항공", "삼성항공", "gold", x=1350, y=250), lab("2000 삼성테크윈", "삼성테크윈으로", "lime", x=1350, y=400), lab("1987년 5월 상장", "상장은", "cream", x=1350, y=550)])
sh("icon", [8, 9], icons=[{"name": "shopping", "text": "카메라", "label": "카메라", "at": "카메라와"}, {"name": "factory", "label": "항공기 엔진", "at": "엔진"},
   {"name": "calendar", "top": "K9 개발 완료", "text": "1998", "label": "국방과학연구소 주도", "at": "1998년"}])
sh("closeup", [10, 11], who="m1", side="left", set="office", time="night", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "?", "at": "실수는", "thought": True}, labels=[lab("가장 비싼 실수?", "실수는", "red", x=1350, y=860, size=110)])
sh("icon", 12, icons=[{"name": "book", "text": "성적표", "label": "한화에어로 성적표", "at": "성적표를"}], stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("wide", 13, set="office", era="modern", wall="grey", time="day", tag="2014년 11월 26일",
   chars=[ch("seller", 640, "calm", "present"), ch("buyer", 1280, "excited", "present", face=-0.6)],
   props=[{"icon": "handshake", "x": 960, "y": 380, "s": .55, "at": "발표를"}])
sh("table", 14, items=[{"type": "receipt", "title": "한화로 넘어가는 회사", "rows": [["삼성테크윈", ""], ["삼성탈레스", ""], ["삼성종합화학", ""], ["삼성토탈", ""]], "text": "모두 4곳", "at": "삼성테크윈"}],
   stamp={"text": "4곳", "at": "네", "color": "red"})
sh("versus", [15, 16], colors=["#BFD9F2", "#F6D9B6"], left={"who": "seller", "title": "삼성 · 전자와 금융", "emotion": "calm", "pose": "present", "at": "삼성은"},
   right={"who": "buyer", "title": "한화 · 방산과 화학", "emotion": "confident", "pose": "hold", "at": "한화는"},
   labels=[lab("1조 9천억 원", "1조", "gold", x=960, y=900)])
sh("counter", 17, value={"from": 0, "to": 8400, "suffix": "억 원", "at": "8,400억"}, caption="삼성테크윈 지분 32.4% 값 (보도)", icon="moneybag")
sh("chart", 18, board="white", chart={"type": "bar", "values": [26156, 79], "labels": ["매출", "영업이익"], "suffix": "억 원", "title": "2014년 삼성테크윈 (연결, DART)", "show_values": True, "highlight": 1, "at": "매출"},
   labels=[lab("겨우 79억 원", "79억", "red")])
sh("crowd", [19, 20], count=20, emotion="nervous", labels=[lab("발표 날 약 -15%", "15%", "red", size=130)])
sh("table", 21, hand="buyer", items=[{"type": "contract", "title": "거래 종결", "text": "삼성테크윈 → 한화테크윈", "at": "거래가", "stamp": {"text": "한화테크윈", "at": "한화테크윈이"}}],
   labels=[lab("2015년 6월 29일", "2015년", "gold")])
sh("closeup", 22, who="buyer", side="right", set="office", time="dusk", emotion="worried", pose="stressed",
   labels=[lab("영업손실 596억 원", "596억", "red", size=110)])
chap("결정", "2장")
sh("closeup", [23, 24], who="m1", side="left", set="office", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "적자 → 3조?", "at": "적자로", "thought": True})
sh("wide", [25, 26], set="office", era="modern", wall="teal", time="day",
   chars=[ch("buyer", 640, "confident", "push", beats=[{"at": "한화디펜스를", "pose": "celebrate", "emotion": "happy"}])],
   props=[{"icon": "factory", "x": 1200, "y": 700, "s": .5, "at": "흩어진"}, {"icon": "factory", "x": 1550, "y": 700, "s": .5, "at": "모으는"}],
   labels=[lab("2018 한화에어로스페이스", "2018년", "gold", x=1380, y=250), lab("2022.11 한화디펜스 합병", "합칩니다", "lime", x=1380, y=400)])
sh("table", 27, hand="buyer", items=[{"type": "contract", "title": "인수", "text": "한화방산 8,521억 원", "at": "8,521억", "stamp": {"text": "합병", "at": "합병을"}}],
   labels=[lab("2023년 4월", "2023년", "gold")])
sh("wide", [28, 29, 30], set="office", era="modern", wall="blue", time="day",
   chars=[ch("kdk", 900, "confident", "present", beats=[{"at": "대표이사에", "pose": "explain"}])],
   lower_third={"name": "김동관", "sub": "한화에어로스페이스 대표이사", "at": "김동관입니다"},
   labels=[lab("2021.3 사내이사", "사내이사가", "cream", x=1450, y=260), lab("2022.9 대표이사", "대표이사에", "lime", x=1450, y=410), lab("2026.8 그룹 수석부회장", "수석부회장입니다", "gold", x=1450, y=560)])
sh("map", [31, 32, 33], places=[{"name": "한국", "x": 1500, "y": 420}, {"name": "호주", "x": 1580, "y": 820}, {"name": "이집트", "x": 620, "y": 470}], vehicle="ship", at="호주",
   labels=[lab("2021.12 호주", "호주", "gold"), lab("2022.2 이집트", "이집트와", "lime")])
sh("icon", 34, icons=[{"name": "calendar", "top": "기본계약", "text": "2022.7", "label": "폴란드 정부", "at": "폴란드"}])
sh("table", [35, 36, 37], hand="buyer", items=[{"type": "contract", "title": "1차 실행계약", "text": "K9 212문 · 3조 2,039억 원", "at": "서명합니다", "stamp": {"text": "서명", "at": "212문"}}],
   labels=[lab("2022년 8월 26일", "8월", "gold"), lab("직전 해 매출의 49.9%", "49.9%", "red")])
sh("chart", [38, 39], board="chalk", chart={"type": "bar", "values": [32039, 34475], "labels": ["2022.8 1차", "2023.12 2차"], "suffix": "억 원", "title": "폴란드 K9 실행계약 (DART)", "show_values": True, "highlight": 1, "at": "2차"},
   labels=[lab("합계 6조 6천억 원+", "6조", "lime")])
sh("icon", 40, icons=[{"name": "coins", "label": "1년 매출의 절반", "at": "절반을"}, {"name": "handshake", "label": "주문 한 번", "at": "한 번에"}])
sh("wide", 41, set="street", time="day", shop="출하장", tag="2022년 10월 19일",
   chars=[ch("worker", 700, "happy", "wave", beats=[{"at": "출하됩니다", "pose": "celebrate", "emotion": "excited"}])],
   props=[{"icon": "factory", "x": 1300, "y": 690, "s": .6, "at": "+0.3"}, {"icon": "car", "x": 1650, "y": 760, "s": .5, "at": "24문이"}],
   labels=[lab("첫 24문 출하", "24문이", "lime", x=1300, y=280)])
sh("table", [42, 43, 44], items=[{"type": "newspaper", "title": "2024년 12월", "text": "한화오션 연결 편입", "at": "편입합니다"},
   {"type": "receipt", "title": "지분 추가 매입", "rows": [["한화오션", "7.3%"], ["금액", "약 1조 3천억"]], "text": "2025년 3월", "at": "7.3%를"}])
sh("chart", [45, 46, 47], board="white", chart={"type": "bar", "values": [78897, 112401, 267029], "labels": ["2023", "2024", "2025"], "suffix": "억 원", "title": "연결 매출 (DART)", "show_values": True, "highlight": 2, "at": "매출은"},
   labels=[lab("영업이익 3조 893억 원", "영업이익은", "gold"), lab("한화오션 합산 효과", "조선", "cream")])
chap("위기", "3장")
sh("wide", [48, 49], set="board", time="day", tag="2025년 3월 20일",
   chars=[ch("buyer", 640, "confident", "present", beats=[{"at": "발표합니다", "pose": "point"}])],
   labels=[lab("유상증자 3조 6천억 원", "3조", "gold", x=1300, y=320, size=110)], stamp={"text": "사상 최대", "at": "최대", "color": "red"})
sh("chart", [50, 51, 52], board="chalk", chart={"type": "bar", "values": [722000, 628000], "labels": ["3월 20일", "3월 21일"], "suffix": "원", "title": "주가 종가 (보도)", "show_values": True, "highlight": 1, "at": "다음"},
   labels=[lab("-13.02%", "13.02%", "red"), lab("시총 약 -4조 2,800억 원", "시가총액", "red")])
sh("crowd", [53, 54], count=22, emotion="angry", set="street", labels=[lab("한 달 전 1조 3천억 원", "1조", "gold", size=110), lab("돈을 어디에?", "쓰임새를", "red", size=130)])
sh("table", [55, 56], items=[{"type": "letter", "title": "금융감독원", "text": "증권신고서 정정 요구", "at": "금융감독원은", "stamp": {"text": "정정 요구 ×2", "at": "두"}}],
   labels=[lab("3월 · 4월", "3월에", "gold")])
sh("versus", [57, 58], colors=["#D8E8F6", "#F6E0B6"], left={"who": "investor", "title": "주주 몫 2조 3천억", "emotion": "worried", "pose": "shrug", "at": "주주에게"},
   right={"who": "buyer", "title": "계열사 3곳 1조 3천억", "emotion": "confident", "pose": "hold", "at": "나머지"},
   labels=[lab("할인 없이 주당 75만 8천 원", "75만", "lime", x=960, y=900)])
sh("counter", [59, 60, 61], value={"from": 0, "to": 42188, "suffix": "억 원", "at": "합치면"}, caption="최종 조달 합계 (DART · 계산)", icon="moneybag",
   compare={"text": "주주 몫 2조 9,188억 · 발행가 68만 4천 원", "icon": "coins", "at": "68만"})
sh("closeup", 62, who="investor", side="right", set="home", time="dusk", emotion="shocked", pose="facepalm",
   labels=[lab("처음보다 +6천억 원", "6천억", "red", size=110)])
sh("chart", [63, 64], board="white", chart={"type": "line", "values": [357940, 690278, 805489, 939000, 1099000, 946000, 1432000, 1537000], "trend": "up", "show_values": False, "title": "주가 (2025.1 → 2026.4.7)", "at": "+0.3"},
   labels=[lab("153만 7천 원", "153만", "gold"), lab("시총 약 79조 원", "79조", "lime")])
sh("wide", [65, 66], set="office", era="modern", wall="plum", time="night",
   chars=[ch("buyer", 700, "shocked", "stressed", beats=[{"at": "61%", "pose": "push", "emotion": "nervous"}])],
   props=[{"icon": "chart_down", "x": 1400, "y": 560, "s": .7, "at": "60만"}],
   labels=[lab("60만 3천 원", "60만", "red", x=1400, y=260), lab("7개월 약 -61%", "61%", "red", x=1400, y=860)])
sh("counter", 67, value={"from": 0, "to": 4520, "suffix": "억 원", "at": "4,520억"}, caption="2026년 3분기 영업이익 (보도)", icon="chart_down", compare={"text": "1년 전보다 -46%", "icon": "warning", "at": "46%"})
sh("icon", [68, 69], icons=[{"name": "chart_down", "label": "세전 -1,896억", "at": "1,896억"}, {"name": "chart_down", "label": "순이익 -367억", "at": "367억"},
   {"name": "calendar", "top": "납품", "text": "4분기", "label": "폴란드 K9 2차 등", "at": "4분기로"}])
sh("table", [70, 71], items=[{"type": "receipt", "title": "자기주식 취득 (11월 6일)", "rows": [["주식 수", "22만 주"], ["금액", "1,496억 원"]], "text": "임직원 보상", "at": "22만", "stamp": {"text": "공시", "at": "공시합니다"}}])
sh("wide", [72, 73], set="office", era="modern", wall="green", time="day", tag="2026년 9월",
   chars=[ch("kdk", 640, "calm", "present"), ch("lbh", 1260, "confident", "present", face=-0.6, enter="right")],
   lower_third={"name": "이부환", "sub": "한화에어로스페이스 대표이사 (2026.9~)", "at": "이부환"},
   labels=[lab("각자 대표 2명", "두", "lime", x=960, y=240)])
chap("성적표", "4장")
sh("chart", [74, 75], board="chalk", chart={"type": "bar", "values": [79, 30893], "labels": ["2014", "2025"], "suffix": "억 원", "title": "연결 영업이익 (DART)", "show_values": True, "highlight": 1, "at": "+0.3"},
   stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("counter", [76, 77], value={"from": 0, "to": 393, "suffix": "배", "at": "393배"}, caption="한화오션 포함 · 단순 비교 아님 (계산)", icon="chart_up",
   compare={"text": "별도 영업이익 2조 226억 원", "icon": "coins", "at": "별도"})
sh("table", [78, 79], items=[{"type": "receipt", "title": "가장 잘한 결정", "rows": [["폴란드 1차", "3조 2,039억"], ["직전 해 매출 대비", "49.9%"]], "text": "2022년", "at": "폴란드"}],
   stamp={"text": "최고의 결정", "at": "절반이었습니다", "color": "green"})
sh("table", [80, 81], items=[{"type": "receipt", "title": "가장 비싼 실수", "rows": [["2025.3.21 주가", "-13.02%"], ["시가총액", "약 -4조 2,800억"]], "text": "정정 요구 2번", "at": "비싼"}],
   stamp={"text": "가장 비싼 실수", "at": "정정", "color": "red"})
sh("chart", [82, 83], board="white", chart={"type": "bar", "values": [1537000, 603000], "labels": ["2026.4.7", "2026.11.20"], "suffix": "원", "title": "한화에어로스페이스 주가", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("시총 31조 927억 원", "31조", "lime")])
chap("반전", "5장")
sh("closeup", [84, 85], who="m1", side="right", set="office", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "지금은 얼마?", "at": "얼마일까요", "thought": True}, labels=[lab("8,400억 원에 넘긴 회사", "8,400억", "gold", x=600, y=860)])
sh("counter", [86, 87], value={"from": 0, "to": 26000, "suffix": "억 원", "at": "전체로"}, caption="8,400억 원 ÷ 지분 32.4% (계산)", icon="building",
   compare={"text": "회사 전체 약 2조 6천억 원", "icon": "moneybag", "at": "2조"})
sh("chart", [88, 89, 90], board="chalk", chart={"type": "bar", "values": [2.6, 31.1, 79.3], "labels": ["2014 매각가 기준", "2026.11.20", "2026.4.7 꼭대기"], "suffix": "조", "title": "회사 전체 값 (계산)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("약 12배", "12배입니다", "lime"), lab("30배 넘게", "30배가", "gold"), lab("단순 비교 아님", "단순", "cream")])
sh("title", [91, 92], text="폴란드 첫 K9은 한화가 아니었다")
sh("table", [93, 94], hand="seller", items=[{"type": "contract", "title": "K9 수출 계약", "text": "폴란드 · 120문 · 3억 2천만 달러", "at": "폴란드와", "stamp": {"text": "삼성테크윈", "at": "삼성테크윈이었습니다"}}],
   labels=[lab("2014년 12월 17일", "2014년", "gold"), lab("매각 발표 3주 뒤", "3주", "red")])
sh("versus", 95, colors=["#BFD9F2", "#F6D9B6"], left={"who": "seller", "title": "판 회사", "emotion": "shocked", "pose": "facepalm", "at": "삼성이"},
   right={"who": "buyer", "title": "가장 큰 해외 손님", "emotion": "happy", "pose": "celebrate", "at": "손님은"})
sh("wide", [96, 99], set="office", era="modern", wall="sand", time="day",
   chars=[ch("seller", 560, "happy", "wave"), ch("m1", 960, "happy", "wave"), ch("buyer", 1360, "smile", "celebrate")],
   labels=[lab("구독 · 좋아요", "구독과", "lime", x=960, y=230, size=130), lab("출처는 설명란", "출처는", "cream", x=960, y=420)],
   polaroid={"at": "출처는", "who": "seller", "caption": "판 회사의 큰 손님은 삼성 시절에 왔다"})

# 빈 화면 방지(2026-11-20 검수): 그래픽 장면의 첫 요소는 장면 시작 직후에 나오게 하고, 나머지만 대사 낱말에 맞춘다
for d in X:
    k = d.get("kind")
    if k == "icon" and d.get("icons"): d["icons"][0]["at"] = "+0.2"
    if k == "table" and d.get("items"): d["items"][0]["at"] = "+0.2"
    if k == "chart" and d.get("chart"): d["chart"]["at"] = "+0.3"
    if k == "counter" and d.get("value"): d["value"]["at"] = "+0.3"

story = {"title": "한화에어로스페이스_v2", "mood": "dramatic", "cast": {
    "seller": {"skin": "light", "outfit": "suit", "color": "#2F4A7A", "shirt": "#F2F2F2", "tie": "#9AB8E0", "hair": "slick", "hair_col": "#3A3A3A"},
    "buyer": {"skin": "tan", "outfit": "suit", "color": "#C2562A", "shirt": "#F2F2F2", "tie": "#2E2E36", "hair": "short", "hair_col": "#2A2420"},
    "kdk": {"skin": "light", "outfit": "suit", "color": "#33363F", "shirt": "#F2F2F2", "tie": "#D9772B", "hair": "short", "hair_col": "#1E1A18"},
    "lbh": {"skin": "fair", "outfit": "suit", "color": "#4F5B66", "shirt": "#F2F2F2", "tie": "none", "hair": "short", "hair_col": "#6A6A6A", "glasses": True},
    "m1": {"skin": "fair", "outfit": "sweater", "color": "#5E8C6A", "hair": "curly", "hair_col": "#3A2C22"},
    "investor": {"skin": "olive", "outfit": "hoodie", "color": "#7A5EA8", "hair": "long", "hair_col": "#2A2420"},
    "worker": {"skin": "brown", "outfit": "tshirt", "color": "#E0B23A", "hair": "short", "hair_col": "#1E1A18", "hat": "cap", "hat_col": "#C2562A"}},
  "shots": X}
json.dump(story, open(os.path.join(P, "story.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(X), "shots")
