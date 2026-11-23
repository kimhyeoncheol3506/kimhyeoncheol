#!/usr/bin/env python3
"""한미반도체 v2 스토리보드 (19편). 본보기: ceo_orion_v2/make_story.py"""
import json, os
P = os.path.dirname(os.path.abspath(__file__)); X = []
def sh(kind, s, **k):
    d = {"kind": kind}
    if s is not None: d["s"] = s if isinstance(s, list) else [s]
    d.update(k); X.append(d)
def lab(text, at, color="lime", **k): return dict(text=text, at=at, color=color, **k)
def ch(id, x, emotion="neutral", pose="idle", **k): return dict(id=id, x=x, emotion=emotion, pose=pose, **k)
def chap(t, n): sh("title", None, text=t, sub=n, hold=1.6)

# 인트로 · 주문서 한 장의 역설
sh("counter", 0, value={"from": 0, "to": 94, "suffix": "%", "at": "94%였습니다"}, caption="주문 1건 ÷ 직전 해 매출 (2024년 6월, DART)", icon="moneybag")
sh("wide", 1, set="street", time="dusk", shop="고객사 공장", tag="열 달 뒤",
   chars=[ch("eng", 700, "nervous", "hold", exit="left"), ch("eng2", 1000, "worried", "hold", exit="left")],
   labels=[lab("엔지니어 철수", "불러들였습니다", "red", x=1450, y=280)])
sh("versus", [2], colors=["#D9E4F2", "#F6D0C8"], left={"who": "buyer", "title": "고객 · SK하이닉스", "emotion": "calm", "pose": "arms_crossed", "at": "고객은"},
   right={"who": "kwak", "title": "장비 회사 · 한미반도체", "emotion": "confident", "pose": "hips", "at": "한미반도체입니다"})
sh("skyline", 3, time="day", labels=[lab("한미반도체", "주인공은", size=170), lab("시가총액 14조 원+", "14조", "gold", y=420)])
chap("판돈", "1장")
sh("wide", [4, 5], set="office", era="old", wall="sand", time="day", tag="1980년 · 서울 성수동", calendar="1980",
   chars=[ch("founder", 900, "confident", "present", beats=[{"at": "차립니다", "pose": "celebrate", "emotion": "excited"}])],
   lower_third={"name": "곽노권", "sub": "한미반도체 창업주", "at": "곽노권이"}, labels=[lab("모토로라 13년+ (보도)", "모토로라에서", "cream", x=1400, y=260)])
sh("table", [6, 7], hand="founder", items=[{"type": "contract", "title": "법인 설립", "text": "한미금형", "at": "+0.2", "stamp": {"text": "1980년", "at": "한미금형이었습니다"}}],
   labels=[lab("반도체 칩을 감싸는 틀", "감싸는", "gold")])
sh("closeup", [8, 9], who="founder", side="left", set="office", time="day", emotion="excited", pose="hold",
   bubble={"who": "founder", "text": "우리가 만든다", "icon": "bulb", "at": "핵심"}, labels=[lab("핵심 부품 국산화 (보도)", "국산화했다고", "lime", x=1350, y=860)])
sh("icon", [10, 11], tag="1985년 3월", icons=[{"name": "laptop", "text": "자동화", "label": "첫 자동화 장비", "at": "자동화"}, {"name": "factory", "label": "틀 → 기계", "at": "기계를"}])
sh("wide", [12, 13], set="street", time="day", shop="한미 공장", tag="1997년",
   chars=[ch("founder", 760, "happy", "push", beats=[{"at": "선보입니다", "pose": "present", "emotion": "excited"}])],
   props=[{"icon": "factory", "x": 1400, "y": 690, "s": .7, "at": "장비를"}],
   labels=[lab("자르고 골라 담는 장비", "자르고", "cream", x=1350, y=260), lab("세계 점유율 1위 (회사 설명)", "1위를", "gold", x=1350, y=420)])
sh("table", [14, 15], items=[{"type": "contract", "title": "상호 변경", "text": "한미금형 → 한미 → 한미반도체", "at": "+0.2", "stamp": {"text": "2002년", "at": "2002년엔"}}])
sh("counter", 16, value={"from": 1980, "to": 2005, "suffix": "년", "at": "2005년"}, caption="2005년 7월 유가증권시장 상장 (DART)", icon="chart_up")
sh("closeup", [17, 18], who="m1", side="right", set="home", time="night", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "누구와?", "at": "누구와의", "thought": True}, labels=[lab("가장 비싼 싸움?", "싸움은", "red", x=600, y=860, size=110)])
sh("icon", 19, icons=[{"name": "book", "text": "성적표", "label": "끝에 공개", "at": "성적표를"}], stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("wide", [20, 21], set="office", era="modern", wall="blue", time="day", tag="2007년 8월",
   chars=[ch("founder", 600, "smile", "present"), ch("kwak", 1150, "confident", "idle", beats=[{"at": "대표이사가", "pose": "hips", "emotion": "confident"}])],
   lower_third={"name": "곽동신", "sub": "한미반도체 대표이사 (2007년 8월~)", "at": "곽동신이"}, labels=[lab("1974년생 · 32살", "서른두", "gold", x=960, y=250)])
sh("walk", [22, 23], set="street", time="dusk", chars=[ch("kwak", 0, "calm", "idle")],
   labels=[lab("2023년 12월 창업주 별세", "2023년", "cream", x=960, y=250), lab("2024년 12월 회장 (보도)", "회장에", "gold", x=960, y=400)])
sh("chart", 24, board="white", chart={"type": "bar", "values": [33.62, 55.82], "labels": ["곽동신 회장", "특수관계인 합계"], "suffix": "%", "title": "지분율 (2026년 9월 말, DART)", "show_values": True, "highlight": 0, "at": "33.62%입니다"})
chap("결정", "2장")
sh("closeup", 25, who="kwak", side="left", set="office", time="day", emotion="confident", pose="point",
   bubble={"who": "kwak", "text": "쌓는 기계", "icon": "target", "at": "쌓는"})
sh("icon", [26, 27], icons=[{"name": "brain", "label": "AI 반도체", "at": "+0.2"}, {"name": "building", "label": "HBM = 층층이 쌓은 메모리", "at": "아파트처럼"}])
sh("wide", [28, 29], set="board", time="day",
   chars=[ch("eng", 760, "thinking", "explain", beats=[{"at": "열과", "pose": "push", "emotion": "confident"}, {"at": "TC", "pose": "present", "emotion": "happy"}])],
   props=[{"icon": "target", "x": 1350, "y": 690, "s": .55, "at": "정밀하게"}],
   labels=[lab("열 + 압력", "열과", "red", x=1400, y=260), lab("TC 본더", "본더입니다", "lime", x=1400, y=420, size=120)])
sh("versus", 30, colors=["#F6E0B6", "#D9E4F2"], left={"who": "kwak", "title": "한미반도체 · TC 본더", "emotion": "happy", "pose": "present", "at": "개발하며"},
   right={"who": "buyer", "title": "SK하이닉스 · HBM", "emotion": "smile", "pose": "present_left", "at": "손을"},
   labels=[lab("2015년 (보도)", "2015년", "gold", x=960, y=900)])
sh("table", [31, 32], hand="kwak", items=[{"type": "contract", "title": "신제품", "text": "듀얼 TC 본더", "at": "+0.2", "stamp": {"text": "2017년 장영실상", "at": "장영실상을"}}],
   labels=[lab("두 곳에서 동시에", "동시에", "lime")])
sh("wide", 33, set="office", era="modern", wall="teal", time="day",
   chars=[ch("kwak", 700, "happy", "present"), ch("buyer", 1200, "happy", "present_left")],
   props=[{"icon": "handshake", "x": 960, "y": 640, "s": .55, "at": "함께"}], labels=[lab("2017년 공동 개발 시작 (보도)", "2017년이었다고", "cream", x=960, y=250)])
sh("icon", 34, icons=[{"name": "lock", "label": "HBM 핵심 장비 공급", "at": "+0.2"}, {"name": "target", "label": "사실상 독점 (보도)", "at": "사실상"}])
chap("위기", "3장")
sh("closeup", 35, who="kwak", side="right", set="office", time="dusk", emotion="worried", pose="think", labels=[lab("2023년", "2023년", "red", x=600, y=860, size=120)])
sh("chart", 36, board="chalk", chart={"type": "bar", "values": [3276, 1590], "labels": ["2022년", "2023년"], "suffix": "억 원", "title": "매출 (연결, DART)", "show_values": True, "highlight": 1, "at": "2022년"},
   labels=[lab("반토막", "반토막이", "red")])
sh("counter", 37, value={"from": 1119, "to": 346, "suffix": "억 원", "at": "346억"}, caption="영업이익 2022년 → 2023년 (DART)", icon="chart_down",
   compare={"text": "-69%", "icon": "warning", "at": "69%"})
sh("closeup", 38, who="m1", side="left", set="home", time="day", emotion="thinking", pose="think", bubble={"who": "m1", "text": "?", "at": "이상한", "thought": True})
sh("chart", 39, board="white", chart={"type": "bar", "values": [346, 2672], "labels": ["영업이익", "순이익"], "suffix": "억 원", "title": "2023년 (연결, DART)", "show_values": True, "highlight": 1, "at": "순이익은"},
   labels=[lab("7배 넘게", "일곱", "gold")])
sh("table", [40, 41], items=[{"type": "newspaper", "title": "공시 (2024년 1월)", "text": "HPSP 등 금융자산 투자 수익", "at": "+0.2", "ring_at": "HPSP"}],
   stamp={"text": "본업 아님", "at": "아니었습니다", "color": "red"})
sh("closeup", [42, 43], who="m1", side="right", set="home", time="night", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "무엇이?", "at": "운명을", "thought": True})
sh("title", 44, text="답은 주문서였습니다")
sh("table", [45, 46], hand="buyer", items=[{"type": "contract", "title": "SK하이닉스 주문 (2023년 8월)", "text": "듀얼 TC 본더", "at": "+0.2", "stamp": {"text": "416억 원", "at": "416억"}}],
   labels=[lab("창사 이래 최대 (보도)", "창사", "gold")])
sh("chart", 47, board="chalk", chart={"type": "bar", "values": [416, 596, 860], "labels": ["2023.8", "2023.9", "2024.2"], "suffix": "억 원", "title": "SK하이닉스 TC 본더 주문 (DART)", "show_values": True, "highlight": 2, "at": "596억"})
sh("wide", 48, set="office", era="modern", wall="green", time="day", tag="2024년 6월 7일",
   chars=[ch("buyer", 700, "confident", "present", beats=[{"at": "1,499억", "pose": "push", "emotion": "excited"}]), ch("kwak", 1250, "shocked", "idle", beats=[{"at": "한", "pose": "celebrate", "emotion": "excited"}])],
   stamp={"text": "1,499억 원", "at": "1,499억", "color": "green"})
sh("counter", [49, 50], value={"from": 0, "to": 94, "suffix": "%", "at": "94%였습니다"}, caption="주문 1,499억 원 ÷ 2023년 매출 1,590억 원 (DART)", icon="trophy",
   compare={"text": "1년 치 매출 = 주문서 한 장", "icon": "book", "at": "주문서"})
sh("map", 51, places=[{"name": "인천", "x": 1450, "y": 520}, {"name": "마이크론 (대만 납품)", "x": 760, "y": 640}], vehicle="plane", at="마이크론에서도",
   labels=[lab("첫 주문 226억 원", "226억", "gold"), lab("2024년 4월", "2024년", "cream")])
sh("chart", 52, board="white", chart={"type": "bar", "values": [1590, 5589], "labels": ["2023년", "2024년"], "suffix": "억 원", "title": "매출 (연결, DART)", "show_values": True, "highlight": 1, "at": "5,589억"},
   labels=[lab("3.5배", "3.5배가", "lime")])
sh("counter", [53, 54], value={"from": 346, "to": 2554, "suffix": "억 원", "at": "2,554억"}, caption="영업이익 2023년 → 2024년 (DART)", icon="chart_up",
   compare={"text": "100원 팔면 46원 남음", "icon": "coins", "at": "46원이"})
chap("베팅", "4장")
sh("closeup", 55, who="kwak", side="left", set="office", time="night", emotion="worried", pose="arms_crossed", labels=[lab("2025년 3월", "2025년", "red", x=1350, y=860, size=110)])
sh("versus", 56, colors=["#D9E4F2", "#F6C7B6"], left={"who": "buyer", "title": "SK하이닉스", "emotion": "calm", "pose": "present", "at": "SK하이닉스에"},
   right={"who": "rival", "title": "경쟁사 한화세미텍", "emotion": "smug", "pose": "hips", "at": "한화세미텍이"},
   labels=[lab("TC 본더 420억 원 (보도)", "420억", "red", x=960, y=900)])
sh("table", 57, hand="kwak", items=[{"type": "letter", "title": "소장 (2024년 12월 4일)", "text": "특허 침해 금지·손해배상", "at": "+0.2", "stamp": {"text": "소송", "at": "소송을"}}])
sh("wide", [58, 59], set="street", time="night", shop="고객사 공장",
   chars=[ch("eng", 620, "nervous", "hold", walk=[900, 200]), ch("eng2", 900, "worried", "hold", walk=[1200, 450]), ch("kwak", 1500, "angry", "point")],
   labels=[lab("엔지니어 수십 명 철수", "수십", "red", x=1300, y=260)])
sh("counter", 60, value={"from": 0, "to": 28, "prefix": "+", "suffix": "%", "at": "28%"}, caption="TC 본더 가격 인상 통보 (보도)", icon="warning")
sh("closeup", 61, who="buyer", side="right", set="office", time="day", emotion="shocked", pose="facepalm", labels=[lab("8년 동맹 (보도)", "8년을", "cream", x=600, y=860, size=110)])
sh("icon", [62, 63], icons=[{"name": "warning", "label": "가장 큰 고객과 싸움", "at": "+0.2"}, {"name": "target", "text": "?", "label": "결과는?", "at": "결과는"}])
sh("closeup", 64, who="kwak", side="right", set="office", time="day", emotion="smile", pose="present_left", labels=[lab("한 달 남짓 만에 봉합", "봉합됩니다", "lime", x=600, y=860)])
sh("table", 65, hand="buyer", items=[{"type": "contract", "title": "SK하이닉스 재주문 (2025년 5월 16일)", "text": "듀얼 TC 본더 그리핀", "at": "+0.2", "stamp": {"text": "428억 원", "at": "428억"}}])
sh("walk", 66, set="street", time="day", chars=[ch("eng", 0, "happy", "hold"), ch("eng2", 0, "smile", "hold")],
   labels=[lab("5월 26일 다시 출근 (보도)", "출근합니다", "lime", x=960, y=250)])
sh("closeup", 67, who="kwak", side="right", set="office", time="day", emotion="thinking", pose="think", labels=[lab("숫자는 달라졌다", "달라졌습니다", "gold", x=600, y=860)])
sh("chart", 68, board="chalk", chart={"type": "bar", "values": [3283, 1114], "labels": ["2024년", "2025년"], "suffix": "억 원", "title": "국내 매출 (DART)", "show_values": True, "highlight": 1, "at": "3,283억"},
   labels=[lab("-66%", "줄었습니다", "red")])
sh("counter", [69, 70], value={"from": 2306, "to": 4653, "suffix": "억 원", "at": "4,653억"}, caption="수출 2024년 → 2025년 (DART)", icon="chart_up",
   compare={"text": "2025년 매출의 81%가 해외", "icon": "target", "at": "81%가"})
sh("chart", 71, board="white", chart={"type": "bar", "values": [5589, 5767], "labels": ["2024년", "2025년"], "suffix": "억 원", "title": "전체 매출 (연결, DART)", "show_values": True, "highlight": 1, "at": "5,767억"},
   labels=[lab("영업이익 2,514억 원", "2,514억", "gold")])
sh("closeup", 72, who="rival", side="left", set="office", time="night", emotion="confident", pose="arms_crossed", labels=[lab("법정 싸움은 진행 중", "법정", "red", x=1350, y=860)])
sh("table", 73, items=[{"type": "letter", "title": "한미 → 한화 (2024.12.4)", "text": "계류 중", "at": "+0.2"}, {"type": "letter", "title": "한화 → 한미 (2025.7.25)", "text": "계류 중", "at": "맞소송을"}],
   stamp={"text": "2026년 9월 말 계류", "at": "계류", "color": "red"})
sh("wide", [74, 75], set="office", era="modern", wall="grey", time="day",
   chars=[ch("kwak", 650, "calm", "arms_crossed"), ch("mediator", 960, "calm", "present"), ch("rival", 1270, "calm", "arms_crossed")],
   labels=[lab("조정 절차 (2026년 11월 보도)", "조정", "cream", x=960, y=250), lab("승패 아님", "이겼다는", "lime", x=960, y=400)])
chap("성적표", "5장")
sh("chart", 76, board="white", chart={"type": "bar", "values": [2512, 1303], "labels": ["매출", "영업이익"], "suffix": "억 원", "title": "2026년 2분기 (연결 잠정, DART)", "show_values": True, "highlight": 1, "at": "2,512억"})
sh("counter", [77, 78], value={"from": 0, "to": 51.9, "suffix": "%", "at": "51.9%가"}, caption="2026년 2분기 영업이익률 (DART로 계산)", icon="target",
   compare={"text": "분기 매출 창사 최대 (보도)", "icon": "trophy", "at": "창사"})
sh("closeup", 79, who="kwak", side="left", set="office", time="day", emotion="excited", pose="celebrate")
sh("chart", [80, 81], board="chalk", chart={"type": "line", "values": [144500, 300000, 409500], "labels": ["2026.1.2", "2026.3.16", "2026.5.14"], "suffix": "원", "title": "한미반도체 종가 (네이버)", "show_values": True, "highlight": 2, "trend": "up", "at": "40만"},
   labels=[lab("시총 약 39조 원", "39조", "gold")])
sh("table", 82, hand="kwak", items=[{"type": "receipt", "title": "회장 자사주 매입 (보도)", "rows": [["2023년~", "사재"], ["2026년 10월까지", "누적"]], "text": "702억 원", "at": "+0.2"}])
sh("wide", [83, 84], set="street", time="night", shop="증권사",
   chars=[ch("m1", 760, "shocked", "stressed"), ch("shopper", 1150, "worried", "facepalm")],
   stamp={"text": "하루 -12.06%", "at": "12.06%", "color": "red"}, labels=[lab("11월 20일 종가 15만 1,600원", "종가는", "cream", x=960, y=250)])
sh("chart", [85, 86], board="white", chart={"type": "bar", "values": [409500, 151600], "labels": ["2026.5.14", "2026.11.20"], "suffix": "원", "title": "한미반도체 종가 (네이버)", "show_values": True, "highlight": 1, "at": "꼭대기보다"},
   labels=[lab("-63%", "63%", "red"), lab("시총 14조 4,493억", "14조", "gold")])
sh("icon", [87, 88], icons=[{"name": "book", "text": "성적표", "label": "한미반도체 성적표", "at": "+0.2"}, {"name": "factory", "label": "시작은 금형 회사", "at": "성수동의"}],
   stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("chart", [89, 90], board="chalk", chart={"type": "bar", "values": [11194, 144493], "labels": ["2022년 말", "2026.11.20"], "suffix": "억 원", "title": "시가총액 (계산)", "show_values": True, "highlight": 1, "at": "1조"},
   labels=[lab("약 13배", "13배입니다", "lime")])
sh("counter", [91, 92], value={"from": 0, "to": 4831, "suffix": "억 원", "at": "4,831억"}, caption="2026년 1~9월 매출 (연결 잠정, DART)", icon="coins",
   compare={"text": "영업이익 2,296억 · 직원 744명", "icon": "heart", "at": "직원은"})
sh("table", [93, 94], items=[{"type": "receipt", "title": "잘한 결정", "rows": [["2015년", "TC 본더 개발"], ["2024년 6월", "주문 1,499억"]], "text": "직전 해 매출의 94%", "at": "+0.2"}],
   stamp={"text": "최고의 결정", "at": "1,499억", "color": "green"})
sh("closeup", 95, who="buyer", side="right", set="office", time="day", emotion="smile", pose="present", labels=[lab("10년 약 6,000억 원 (보도)", "6,000억", "gold", x=600, y=860, size=100)])
sh("icon", 96, icons=[{"name": "warning", "label": "가장 비싼 싸움", "at": "+0.2"}, {"name": "handshake", "label": "2025년 · SK하이닉스와 갈등", "at": "갈등입니다"}])
sh("table", 97, items=[{"type": "receipt", "title": "가장 비싼 싸움 (2025년)", "rows": [["한화세미텍 수주", "420억 (보도)"], ["국내 매출", "-66%"]], "text": "고객과의 갈등", "at": "+0.2"}],
   stamp={"text": "국내 매출 -66%", "at": "66%", "color": "red"})
sh("versus", 98, colors=["#F6C7B6", "#D8F0D8"], left={"who": "buyer", "title": "국내 -66%", "emotion": "sad", "pose": "shrug", "at": "+0.2"},
   right={"who": "kwak", "title": "해외 2배 · 영업이익 2,514억", "emotion": "happy", "pose": "celebrate", "at": "해외"})
chap("반전", "6장")
sh("closeup", 99, who="m1", side="left", set="home", time="dusk", emotion="calm", pose="explain")
sh("table", 100, hand="buyer", items=[{"type": "contract", "title": "SK하이닉스 주문 (2026년 6월)", "text": "HBM4용 TC 본더", "at": "+0.2", "stamp": {"text": "442억 원", "at": "442억"}}])
sh("wide", [101, 102], set="office", era="modern", wall="cream", time="day", tag="2026년 10월 30일",
   chars=[ch("buyer", 700, "smile", "hold", beats=[{"at": "감사패를", "pose": "present", "emotion": "happy"}]), ch("kwak", 1250, "happy", "idle", beats=[{"at": "감사패를", "pose": "celebrate", "emotion": "excited"}])],
   props=[{"icon": "trophy", "x": 960, "y": 620, "s": .55, "at": "감사패를"}], labels=[lab("HBM 양산 공로 (보도)", "공로였다고", "gold", x=960, y=250)])
sh("versus", 103, colors=["#F6C7B6", "#D8F0D8"], left={"who": "eng", "title": "2025년 4월 · 철수", "emotion": "worried", "pose": "hold", "at": "+0.2"},
   right={"who": "kwak", "title": "2026년 10월 · 감사패", "emotion": "happy", "pose": "celebrate", "at": "감사패를"},
   labels=[lab("1년 반", "1년", "lime", x=960, y=900)])
sh("walk", 104, set="street", time="dusk", chars=[ch("founder", 0, "smile", "idle"), ch("kwak", 0, "confident", "hold")],
   labels=[lab("금형 → HBM 장비", "기계를", "lime", x=960, y=250), lab("46년", "46년", "gold", x=960, y=400)])
sh("title", [105, 106], text="고객과는 싸워 이겼다. 주가는 -63%")
sh("wide", [107, 110], set="office", era="modern", wall="sand", time="day",
   chars=[ch("founder", 600, "happy", "wave"), ch("m1", 960, "happy", "wave"), ch("kwak", 1320, "smile", "celebrate")],
   labels=[lab("구독 · 좋아요", "구독과", "lime", x=960, y=230, size=130), lab("출처는 설명란", "출처는", "cream", x=960, y=420)],
   polaroid={"at": "출처는", "who": "kwak", "caption": "고객과 싸우고, 감사패를 받았다"})

# 빈 화면 방지(2026-11-20 검수): 그래픽 장면의 첫 요소는 장면 시작 직후에 나오게 하고, 나머지만 대사 낱말에 맞춘다
for d in X:
    k = d.get("kind")
    if k == "icon" and d.get("icons"): d["icons"][0]["at"] = "+0.2"
    if k == "table" and d.get("items"): d["items"][0]["at"] = "+0.2"
    if k == "chart" and d.get("chart"): d["chart"]["at"] = "+0.3"
    if k == "counter" and d.get("value"): d["value"]["at"] = "+0.3"

story = {"title": "한미반도체_v2", "mood": "dramatic", "cast": {
    "founder": {"skin": "tan", "outfit": "suit", "color": "#4A3A2E", "shirt": "#F2F2F2", "tie": "#B8862E", "hair": "short", "hair_col": "#8A8A8A", "glasses": True},
    "kwak": {"skin": "light", "outfit": "suit", "color": "#1F3F8C", "shirt": "#F2F2F2", "tie": "#D0202C", "hair": "slick", "hair_col": "#2A2A2A"},
    "buyer": {"skin": "fair", "outfit": "suit", "color": "#C0392B", "shirt": "#F2F2F2", "tie": "#F29B1E", "hair": "short", "hair_col": "#3A2C22"},
    "rival": {"skin": "olive", "outfit": "suit", "color": "#E07A1F", "shirt": "#F2F2F2", "tie": "#2E2E36", "hair": "bald"},
    "eng": {"skin": "fair", "outfit": "hoodie", "color": "#4A6A8C", "hair": "short", "hair_col": "#1E1A18", "hat": "cap", "hat_col": "#1F3F8C"},
    "eng2": {"skin": "tan", "outfit": "tshirt", "color": "#5E8C6A", "hair": "curly", "hair_col": "#2A2420"},
    "mediator": {"skin": "light", "outfit": "suit", "color": "#6A6A78", "tie": "#2E2E36", "hair": "short", "hair_col": "#5A5A5A", "glasses": True},
    "m1": {"skin": "fair", "outfit": "sweater", "color": "#8C5EA0", "hair": "long", "hair_col": "#3A2C22"},
    "shopper": {"skin": "fair", "outfit": "tshirt", "color": "#D0703A", "hair": "short", "hair_col": "#1E1A18"}},
  "shots": X}
for d in X:
    if d.get("kind") == "walk":
        for c in d.get("chars", []): c.pop("x", None)
json.dump(story, open(os.path.join(P, "story.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(X), "shots")
