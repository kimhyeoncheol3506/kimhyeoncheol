#!/usr/bin/env python3
"""신세계·이마트(신세계 그룹) v2 스토리보드."""
import json, os
P = os.path.dirname(os.path.abspath(__file__)); X = []
def sh(kind, s, **k):
    d = {"kind": kind}
    if s is not None: d["s"] = s if isinstance(s, list) else [s]
    d.update(k); X.append(d)
def lab(text, at, color="lime", **k): return dict(text=text, at=at, color=color, **k)
def ch(id, x, emotion="neutral", pose="idle", **k): return dict(id=id, x=x, emotion=emotion, pose=pose, **k)
def chap(t, n): sh("title", None, text=t, sub=n, hold=1.6)

# 인트로 · 매출 29조 회사의 몸값이 1조 7천억이 안 된다 (0초부터 그림이 보이는 거리 장면으로 시작)
sh("wide", 0, set="street", time="day", shop="대형마트",
   chars=[ch("m1", 700, "happy", "hold"), ch("m2", 1150, "smile", "idle")],
   labels=[lab("1년 매출 약 29조 원", "+0.1", "gold", x=1420, y=260, size=110)])
sh("counter", 1, value={"from": 0, "to": 16995, "suffix": "억 원", "at": "1조"}, caption="이마트 시가총액 · 2026년 11월 25일 종가로 계산", icon="moneybag",
   compare={"text": "1조 7천억 원이 채 안 됨", "icon": "warning", "at": "채"})
sh("versus", 2, colors=["#F6E0B6", "#D9D9E6"],
   left={"who": "m1", "title": "매출 29조 · 몸값은 더 작다", "emotion": "shocked", "pose": "facepalm", "at": "+0.2"},
   right={"who": "m2", "title": "매출 4분의 1 미만 · 몸값은 더 크다", "emotion": "confident", "pose": "hips", "at": "형제"},
   labels=[lab("매출은 4분의 1도 안 되는데", "4분의", "gold", x=960, y=900)])
sh("icon", 3, icons=[{"name": "shopping", "text": "마트", "label": "이마트", "at": "+0.2"}, {"name": "building", "label": "신세계", "at": "신세계입니다"}])
chap("판돈", "1장")
sh("skyline", 4, time="dusk", tag="서울 명동", labels=[lab("백화점 하나에서 시작", "백화점", "cream", size=110)])
sh("icon", 5, icons=[{"name": "calendar", "top": "1955", "text": "12월", "label": "동화백화점 설립", "at": "+0.2"}, {"name": "building", "label": "백화점", "at": "동화백화점으로"}])
sh("table", 6, items=[{"type": "contract", "title": "백화점 인수", "text": "삼성그룹 → 이름은 신세계로", "at": "+0.2", "stamp": {"text": "1963년", "at": "인수해"}}])
sh("closeup", 7, who="lee", side="right", set="office", time="day", emotion="confident", pose="present",
   lower_third={"name": "이명희", "sub": "신세계 총괄회장", "at": "이명희가"}, labels=[lab("이병철의 딸", "딸", "gold", x=600, y=860)])
sh("wide", [8, 9], set="office", era="old", wall="sand", time="day", calendar="1991 11",
   chars=[ch("lee", 900, "confident", "present", beats=[{"at": "발표합니다", "pose": "celebrate", "emotion": "excited"}])],
   labels=[lab("1991년 11월 · 분리 독립 발표", "분리", "lime", x=1400, y=260), lab("1997년 4월 · 계열 분리", "1997년", "cream", x=1400, y=420)])
sh("closeup", 10, who="lee", side="left", set="office", time="day", emotion="thinking", pose="think",
   bubble={"who": "lee", "text": "백화점 말고?", "at": "뜻밖에도", "thought": True})
sh("wide", 11, set="street", time="day", shop="할인점 1호점", tag="1993년 11월 12일 · 서울 창동",
   chars=[ch("m1", 650, "excited", "celebrate"), ch("m2", 1000, "happy", "hold"), ch("lee", 1350, "happy", "present")],
   labels=[lab("이마트 1호점", "1호점이", "gold", x=960, y=230, size=110)])
sh("table", 12, items=[{"type": "letter", "title": "신세계 사업보고서 연혁 (DART)", "text": "1993.11.12 창동 E-MART 개점", "at": "+0.2", "ring_at": "1호점이라고"}],
   stamp={"text": "대형마트 국내 1호점", "at": "1호점이라고", "color": "red"})
sh("versus", 13, colors=["#E9D8F2", "#D8F0D8"],
   left={"who": "m2", "title": "백화점 · 비싸게", "emotion": "smile", "pose": "hold", "at": "+0.2"},
   right={"who": "m1", "title": "할인점 · 싸게 많이", "emotion": "excited", "pose": "celebrate", "at": "할인점에"})
sh("closeup", [14, 15], who="m1", side="left", set="home", time="night", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "?", "at": "질문", "thought": True}, labels=[lab("가장 비싼 결정?", "비싼", "red", x=1350, y=860, size=110)])
sh("icon", 16, icons=[{"name": "book", "text": "성적표", "label": "끝에 공개", "at": "+0.2"}], stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
chap("결정", "2장")
sh("map", [17, 18], places=[{"name": "일산", "x": 700, "y": 330}, {"name": "부평", "x": 560, "y": 520}, {"name": "안산", "x": 820, "y": 700}, {"name": "분당", "x": 1250, "y": 620}],
   vehicle="car", at="일산", labels=[lab("이마트가 잇따라", "잇따라", "gold")])
sh("icon", 19, icons=[{"name": "calendar", "top": "1997", "text": "2월", "label": "중국 상하이 1호점", "at": "+0.2"}, {"name": "shopping", "text": "上海", "label": "해외 첫 이마트", "at": "상하이에도"}])
sh("wide", [20, 21], set="street", time="dusk", shop="외국계 할인점",
   chars=[ch("wm", 900, "confident", "hips")], lower_third={"name": "월마트", "sub": "미국 · 세계 최대 유통 회사", "at": "월마트입니다"})
sh("table", 22, hand="lee", items=[{"type": "contract", "title": "월마트코리아 지분 100% 인수", "text": "계약 2006년 5월 22일", "at": "+0.2", "stamp": {"text": "통째로", "at": "통째로"}}])
sh("counter", 23, value={"from": 0, "to": 8250, "suffix": "억 원", "at": "+0.3"}, caption="월마트코리아 인수 금액 (DART)", icon="moneybag",
   compare={"text": "점포 16개", "icon": "building", "at": "16개"})
sh("closeup", 24, who="lee", side="left", set="office", time="day", emotion="confident", pose="arms_crossed",
   stamp={"text": "자기자본의 34.4%", "at": "34.4%에", "color": "red"})
sh("walk", 25, set="street", time="dusk", chars=[ch("wm", 0, "sad", "idle")],
   labels=[lab("세계 최대 유통 회사는 떠나고", "떠났고", "red", x=700, y=260), lab("산 쪽은 할인점 1호점 회사", "산", "lime", x=1300, y=420)])
sh("table", [26, 27], items=[{"type": "contract", "title": "인적분할", "text": "대형마트 부문 → 주식회사 이마트", "at": "+0.2", "stamp": {"text": "2011년 5월", "at": "이마트가"}}])
sh("versus", [28, 29], colors=["#E9D8F2", "#F6E0B6"],
   left={"who": "m2", "title": "신세계 · 백화점", "emotion": "smile", "pose": "present", "at": "+0.2"},
   right={"who": "m1", "title": "이마트 · 대형마트", "emotion": "happy", "pose": "present", "at": "대형마트는"},
   labels=[lab("같은 가족 · 상장회사 두 개", "같은", "gold", x=960, y=900)])
sh("icon", 30, icons=[{"name": "factory", "label": "트레이더스", "at": "+0.2"}, {"name": "gift", "label": "노브랜드", "at": "노브랜드"}, {"name": "building", "label": "스타필드", "at": "스타필드로"}])
sh("counter", [31, 32], value={"from": 0, "to": 317500, "suffix": "원", "at": "+0.3"}, caption="2018년 2월 26일 이마트 종가 (네이버 증권)", icon="chart_up",
   compare={"text": "시가총액 8조 원+ (계산)", "icon": "trophy", "at": "8조"})
chap("위기", "3장")
sh("crowd", [33, 34], count=24, emotion="neutral", set="street", labels=[lab("마트 → 휴대폰 화면", "화면에서", "gold", size=110)])
sh("closeup", [35, 36], who="m1", side="right", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "1위 회사는?", "icon": "phone", "at": "할인점", "thought": True})
sh("title", 37, text="답: 사고, 또 사기")
sh("table", [38, 39], hand="jung", items=[{"type": "contract", "title": "프로야구단 지분 100%", "text": "에스케이 와이번스 → 에스에스지 랜더스", "at": "+0.2", "stamp": {"text": "1,000억 원", "at": "1,000억"}}],
   labels=[lab("2021년 2월", "2021년", "gold")])
sh("counter", [40, 41], value={"from": 0, "to": 34404, "suffix": "억 원", "at": "+0.3"}, caption="이베이코리아 지분 80.01% · 2021년 6월 (DART)", icon="moneybag",
   compare={"text": "지마켓 · 옥션 운영사", "icon": "laptop", "at": "지마켓과"})
sh("table", 42, hand="jung", items=[{"type": "receipt", "title": "스타벅스커피코리아 (DART)", "rows": [["추가 지분", "17.5%"], ["금액", "4,742억"]], "text": "지분 67.5%", "at": "+0.2"}],
   stamp={"text": "2021년 7월", "at": "67.5%로", "color": "red"})
sh("chart", 43, board="chalk", chart={"type": "bar", "values": [1000, 34404, 4742], "labels": ["야구단", "이베이코리아", "스타벅스"], "suffix": "억", "title": "2021년 세 건 (DART)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("합계 4조 146억 원", "4조", "gold")])
sh("closeup", [44, 45], who="m1", side="left", set="home", time="night", emotion="shocked", pose="facepalm",
   stamp={"text": "-469억", "at": "469억", "color": "red"}, labels=[lab("2023년 연결 영업손실", "2023년", "cream", x=1350, y=860)])
sh("table", [46, 47], items=[{"type": "newspaper", "title": "2023년 실적", "text": "첫 연간 영업손실 (보도)", "at": "+0.2", "ring_at": "처음"}],
   labels=[lab("신세계건설 손실 (보도)", "신세계건설의", "red")])
sh("versus", 48, colors=["#D8F0D8", "#F6C7B6"],
   left={"who": "m2", "title": "2024년 영업이익 471억", "emotion": "smile", "pose": "idle", "at": "+0.2"},
   right={"who": "m1", "title": "2024년 순손실 5,734억", "emotion": "sad", "pose": "facepalm", "at": "순손실은"})
sh("table", 49, items=[{"type": "letter", "title": "2024 사업보고서 (DART)", "text": "지마켓 쪽 영업권 손상차손 2,691억 원", "at": "+0.2", "ring_at": "2,691억"}])
sh("closeup", 50, who="m1", side="right", set="home", time="night", emotion="worried", pose="stressed",
   stamp={"text": "3년 만에 스스로 깎다", "at": "깎은", "color": "red"})
chap("베팅", "4장")
sh("wide", [51, 52], set="office", era="modern", wall="blue", time="day", tag="2024년 3월 8일",
   chars=[ch("jung", 900, "confident", "present", beats=[{"at": "승진합니다", "pose": "celebrate", "emotion": "excited"}])],
   lower_third={"name": "정용진", "sub": "신세계그룹 회장 (2024년 3월~)", "at": "정용진"},
   labels=[lab("부회장 18년 만 (보도)", "18년", "gold", x=1400, y=260)])
sh("closeup", 53, who="jung", side="right", set="office", time="day", emotion="confident", pose="point",
   bubble={"who": "jung", "text": "정리", "icon": "target", "at": "정리였습니다"})
sh("table", 54, hand="jung", items=[{"type": "contract", "title": "흡수합병", "text": "이마트에브리데이 → 이마트", "at": "+0.2", "stamp": {"text": "2024년 6월", "at": "흡수합병합니다"}}])
sh("wide", [55, 56], set="board", time="day", tag="2024년 12월",
   chars=[ch("jung", 700, "confident", "present"), ch("wm", 1200, "smile", "idle")],
   labels=[lab("지마켓 → 알리익스프레스와 합작회사", "알리익스프레스와", "gold", x=960, y=240, size=70), lab("이마트 쪽 지분 50%", "50%입니다", "lime", x=960, y=400)])
sh("icon", 57, icons=[{"name": "calendar", "top": "2025", "text": "2월", "label": "포괄적 주식 교환", "at": "+0.2"}, {"name": "factory", "label": "신세계건설 → 100% 자회사", "at": "거둬들입니다"}])
sh("chart", [58, 59], board="white", chart={"type": "bar", "values": [471, 3225], "labels": ["2024년", "2025년"], "suffix": "억 원", "title": "이마트 영업이익 (DART)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("6배+", "6배를", "red")])
sh("closeup", [60, 61], who="jung", side="left", set="office", time="day", emotion="smile", pose="hips",
   labels=[lab("2025년 매출 28조 9,704억", "28조", "cream", x=1350, y=300), lab("새는 곳을 막다", "새는", "lime", x=1350, y=860)])
sh("walk", 62, set="street", time="day", chars=[ch("yoo", 0, "confident", "idle")], labels=[lab("또 한 명의 회장", "또", "gold", size=110)])
sh("wide", 63, set="office", era="modern", wall="plum", time="day", tag="2024년 10월 30일",
   chars=[ch("yoo", 900, "confident", "present", beats=[{"at": "승진합니다", "pose": "celebrate", "emotion": "happy"}])],
   lower_third={"name": "정유경", "sub": "신세계 회장 (2024년 10월~)", "at": "정유경"},
   labels=[lab("신세계 회장 승진", "승진합니다", "gold", x=1400, y=260)])
sh("versus", 64, colors=["#F6E0B6", "#E9D8F2"],
   left={"who": "jung", "title": "이마트", "emotion": "confident", "pose": "present", "at": "+0.2"},
   right={"who": "yoo", "title": "백화점 (신세계)", "emotion": "confident", "pose": "present", "at": "백화점을"},
   labels=[lab("계열 분리 발표 (보도)", "계열", "red", x=960, y=900)])
sh("table", 65, items=[{"type": "letter", "title": "2025년 2월 · 이마트 주식 (DART)", "text": "278만 7,582주 · 이명희 → 정용진 (매수)", "at": "+0.2"}],
   stamp={"text": "공시", "at": "공시됐습니다", "color": "red"})
sh("closeup", 66, who="yoo", side="left", set="office", time="day", emotion="calm", pose="hold",
   labels=[lab("신세계 주식 98만 4,518주", "98만", "cream", x=1350, y=300, size=80), lab("이명희 → 정유경 · 증여 (공시)", "증여됐다고", "lime", x=1350, y=860, size=70)])
sh("skyline", [67, 68], time="night", tag="신세계 강남점", labels=[lab("백화점의 무기 · 점포 하나", "무기는", "gold", size=100)])
sh("counter", 69, value={"from": 0, "to": 3, "suffix": "조 원", "at": "+0.3"}, caption="2023년 강남점 1년 거래액 · 백화점 점포 국내 처음 (회사 발표)", icon="trophy")
sh("closeup", 70, who="yoo", side="right", set="office", time="day", emotion="excited", pose="celebrate",
   labels=[lab("주가가 날아오른다", "날아오릅니다", "lime", x=600, y=860)])
sh("chart", [71, 72], board="chalk", chart={"type": "bar", "values": [125900, 776000], "labels": ["2024.12.9", "2026.7.1"], "suffix": "원", "title": "신세계 종가 (네이버 증권)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("2024년 12월 → 2026년 7월", "77만", "gold")])
sh("closeup", 73, who="m1", side="right", set="home", time="day", emotion="shocked", pose="facepalm",
   stamp={"text": "6배+", "at": "6배가", "color": "red"})
sh("crowd", 74, count=26, emotion="excited", set="street", labels=[lab("증시 호황 · 소비 기대 (보도)", "호황에", "gold", size=90)])
sh("counter", [75, 76], value={"from": 0, "to": 5293, "suffix": "억 원", "at": "+0.3"}, caption="신세계 2026년 1~9월 영업이익 (DART)", icon="chart_up",
   compare={"text": "1년 전보다 +72.2%", "icon": "trophy", "at": "72.2%"})
sh("chart", 77, board="white", chart={"type": "bar", "values": [4800, 5293], "labels": ["2025년 한 해", "2026년 9개월"], "suffix": "억 원", "title": "신세계 영업이익 (DART)", "show_values": True, "highlight": 1, "at": "+0.3"})
sh("closeup", 78, who="jung", side="left", set="office", time="night", emotion="worried", pose="stressed",
   labels=[lab("이마트 1~9월 영업이익 1,813억", "1,813억", "cream", x=1350, y=300, size=75), lab("-45.4%", "45.4%", "red", x=1350, y=860, size=110)])
sh("table", [79, 80], items=[{"type": "newspaper", "title": "이마트 2026년 2분기 (DART)", "text": "영업손실 430억 원", "at": "+0.2"},
   {"type": "newspaper", "title": "스타벅스 운영 자회사", "text": "2분기 영업손실 184억 (보도)", "at": "스타벅스를"}],
   stamp={"text": "-430억", "at": "430억", "color": "red"})
chap("성적표", "5장")
sh("icon", [81, 82], icons=[{"name": "book", "text": "성적표", "label": "이마트", "at": "+0.2"}], stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("counter", [83, 84], value={"from": 1, "to": 157, "suffix": "개", "at": "+0.3"}, caption="이마트 국내 대형마트 · 1993년 1개 → 2025년 말 (DART)", icon="building")
sh("closeup", [85, 86], who="lee", side="left", set="office", time="day", emotion="happy", pose="present",
   stamp={"text": "최고의 결정", "at": "할인점", "color": "green"}, labels=[lab("2025년 매출 28조 9,704억", "28조", "lime", x=1350, y=860, size=80)])
sh("table", [87, 88], items=[{"type": "receipt", "title": "가장 비싼 결정 (DART)", "rows": [["이베이코리아 (2021)", "3조 4,404억"], ["영업권 손상 (2024)", "2,691억"]], "text": "3년 만에 깎은 값", "at": "+0.2"}],
   stamp={"text": "가장 비싼 결정", "at": "이베이코리아입니다", "color": "red"})
sh("chart", [89, 90], board="white", chart={"type": "bar", "values": [317500, 62900], "labels": ["2018.2.26", "2026.11.25"], "suffix": "원", "title": "이마트 종가 (네이버 증권)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("-80.2%", "80.2%", "red")])
sh("counter", 91, value={"from": 0, "to": 16995, "suffix": "억 원", "at": "+0.3"}, caption="이마트 시가총액 · 2026년 11월 25일 (계산)", icon="moneybag")
sh("icon", [92, 93], icons=[{"name": "book", "text": "성적표", "label": "신세계", "at": "+0.2"}, {"name": "building", "label": "2025년 매출 6조 9,295억", "at": "6조"}])
sh("chart", 94, board="chalk", chart={"type": "bar", "values": [5293, 1813], "labels": ["신세계", "이마트"], "suffix": "억 원", "title": "2026년 1~9월 영업이익 (DART)", "show_values": True, "highlight": 0, "at": "+0.3"},
   labels=[lab("약 2.9배", "2.9배입니다", "gold")])
sh("versus", [95, 96], colors=["#D8F0D8", "#F6C7B6"],
   left={"who": "yoo", "title": "2026.7.1 · 77만 6천 원", "emotion": "excited", "pose": "celebrate", "at": "+0.2"},
   right={"who": "yoo", "title": "11.25 · 27만 3천 원", "emotion": "worried", "pose": "stressed", "at": "27만"},
   stamp={"text": "-64.8%", "at": "64.8%", "color": "red"})
sh("chart", 97, board="white", chart={"type": "bar", "values": [25785, 16995], "labels": ["신세계", "이마트"], "suffix": "억 원", "title": "시가총액 2026.11.25 (계산)", "show_values": True, "highlight": 0, "at": "+0.3"},
   labels=[lab("차이 8,790억 원", "8,790억", "gold")])
chap("반전", "6장")
sh("closeup", 98, who="m1", side="left", set="home", time="dusk", emotion="calm", pose="explain")
sh("table", [99, 100], items=[{"type": "newspaper", "title": "2024년 10월 30일 (보도)", "text": "이마트 · 백화점 계열 분리 발표", "at": "+0.2"},
   {"type": "letter", "title": "신세계 2026 반기보고서 (DART)", "text": "기업집단 신세계 · 국내 계열사 64개", "at": "공시를"}],
   stamp={"text": "아직 한 집단", "at": "아직", "color": "red"})
sh("closeup", 101, who="jung", side="right", set="office", time="day", emotion="confident", pose="arms_crossed",
   labels=[lab("이마트 대표이사 내정 (분기보고서)", "내정됐다고", "cream", x=600, y=860, size=70)])
sh("icon", 102, icons=[{"name": "shopping", "text": "16", "label": "월마트 점포 16개", "at": "+0.2"}, {"name": "phone", "label": "4조 원+", "at": "4조"}])
sh("versus", 103, colors=["#F6E0B6", "#E9D8F2"],
   left={"who": "m1", "title": "이마트 · 시총 1조 6,995억", "emotion": "sad", "pose": "idle", "at": "+0.2"},
   right={"who": "m2", "title": "신세계 · 시총 2조 5,785억", "emotion": "smile", "pose": "hips", "at": "형제"})
sh("title", 104, text="숙제는 여전히, 화면 속 손님")
sh("wide", [105, 108], set="office", era="modern", wall="blue", time="day",
   chars=[ch("jung", 600, "happy", "wave"), ch("m1", 960, "happy", "wave"), ch("yoo", 1320, "smile", "celebrate")],
   labels=[lab("구독 · 좋아요", "구독과", "lime", x=960, y=230, size=130), lab("출처는 설명란", "출처는", "cream", x=960, y=420)],
   polaroid={"at": "출처는", "who": "m1", "caption": "매출 29조, 몸값은 형제보다 작다"})

# 빈 화면 방지(2026-11-20 검수): 그래픽 장면의 첫 요소는 장면 시작 직후에 나오게 하고, 나머지만 대사 낱말에 맞춘다
for d in X:
    k = d.get("kind")
    if k == "icon" and d.get("icons"): d["icons"][0]["at"] = "+0.2"
    if k == "table" and d.get("items"): d["items"][0]["at"] = "+0.2"
    if k == "chart" and d.get("chart"): d["chart"]["at"] = "+0.3"
    if k == "counter" and d.get("value"): d["value"]["at"] = "+0.3"

story = {"title": "신세계이마트_v2", "mood": "dramatic", "cast": {
    "lee": {"skin": "light", "outfit": "suit", "color": "#6A4C5E", "shirt": "#F2F2F2", "tie": "none", "hair": "bun", "hair_col": "#2A2420"},
    "jung": {"skin": "tan", "outfit": "suit", "color": "#2E3A5C", "shirt": "#F2F2F2", "tie": "#B8892E", "hair": "short", "hair_col": "#2A2420"},
    "yoo": {"skin": "fair", "outfit": "suit", "color": "#3E3A46", "shirt": "#F2F2F2", "tie": "none", "hair": "long", "hair_col": "#3A2C22"},
    "wm": {"skin": "fair", "outfit": "suit", "color": "#1F3A6A", "tie": "#E8B020", "hair": "bald"},
    "m1": {"skin": "fair", "outfit": "hoodie", "color": "#5E8C6A", "hair": "curly", "hair_col": "#3A2C22"},
    "m2": {"skin": "light", "outfit": "hoodie", "color": "#C46A4A", "hair": "short", "hair_col": "#2A2420"}},
  "shots": X}
for d in X:
    if d.get("kind") == "walk":
        for c in d.get("chars", []): c.pop("x", None)
json.dump(story, open(os.path.join(P, "story.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(X), "shots")
