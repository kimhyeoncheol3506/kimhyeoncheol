#!/usr/bin/env python3
"""오뚜기 v2 스토리보드."""
import json, os
P = os.path.dirname(os.path.abspath(__file__)); X = []
OFF = 0  # 2026-11-26 첫 30초 재작성: 인트로 문장이 늘어난 만큼 뒤 장면 문장 번호를 민다
def sh(kind, s, **k):
    d = {"kind": kind}
    if s is not None: d["s"] = [i + OFF for i in (s if isinstance(s, list) else [s])]
    d.update(k); X.append(d)
def lab(text, at, color="lime", **k): return dict(text=text, at=at, color=color, **k)
def ch(id, x, emotion="neutral", pose="idle", **k): return dict(id=id, x=x, emotion=emotion, pose=pose, **k)
def chap(t, n): sh("title", None, text=t, sub=n, hold=1.6)

# 인트로 · 위기부터: 라면값 13년 넘게 동결 → '갓뚜기'(보도) → 황제주였던 주가는 꼭대기보다 한참 아래 → 매출↑ 이익↓ (0초부터 그림·글자)
sh("wide", 0, set="street", time="day", shop="라면 · 식품 매장",
   chars=[ch("shopper", 650, "happy", "hold"), ch("shopper2", 1250, "excited", "celebrate")],
   labels=[lab("라면값 13년 넘게 그대로", "+0.0", "gold", x=960, y=240, size=110)])
sh("closeup", 1, who="m1", side="left", set="home", time="day", emotion="happy", pose="present",
   labels=[lab("'갓뚜기' (보도)", "갓뚜기", "gold", x=1350, y=860, size=110)])
sh("chart", 2, board="chalk", chart={"type": "line", "values": [9, 7.5, 5, 3.5, 2], "trend": "down", "show_values": False, "title": "황제주의 주가 · 꼭대기에서 한참 아래로", "at": "+0.3"})
sh("versus", 3, colors=["#D8F0D8", "#F6C7B6"], left={"who": "m1", "title": "매출 · 계속 커졌다", "emotion": "happy", "pose": "celebrate", "at": "+0.2"},
   right={"who": "m1", "title": "영업이익 · 거꾸로", "emotion": "shocked", "pose": "facepalm", "at": "영업이익은"})
sh("skyline", 4, time="day", labels=[lab("오뚜기", "오뚜기입니다", size=180)])
sh("closeup", 5, who="m2", side="right", set="home", time="night", emotion="thinking", pose="think",
   bubble={"who": "m2", "text": "무슨 일이?", "at": "+0.2", "thought": True})
OFF = 2
chap("판돈", "1장")
sh("walk", 4, set="street", time="day", tag="1969년 5월 · 서울", chars=[ch("founder", 0, "confident", "idle")],
   labels=[lab("1969년 5월", "1969년", "gold", x=960, y=260)])
sh("wide", 5, set="office", era="old", wall="sand", time="day", calendar="1969 5",
   chars=[ch("founder", 900, "confident", "present", beats=[{"at": "세웁니다", "pose": "celebrate", "emotion": "excited"}])],
   lower_third={"name": "함태호", "sub": "오뚜기 창업주 (1930~2016)", "at": "+0.3"}, labels=[lab("풍림상사", "풍림상사라는", "gold", x=1400, y=260)])
sh("icon", 6, icons=[{"name": "shopping", "text": "카레", "label": "첫 제품 · 5월 5일", "at": "+0.2"}])
sh("closeup", 7, who="founder", side="right", set="office", time="day", emotion="excited", pose="present",
   bubble={"who": "founder", "text": "집에서 카레!", "icon": "house", "at": "집에서"}, labels=[lab("서양 고급 요리 → 가루 카레", "가루로", "cream", x=600, y=860, size=80)])
sh("table", 8, hand="founder", items=[{"type": "contract", "title": "신제품", "text": "케챂", "at": "+0.2", "stamp": {"text": "1971년", "at": "케챂이"}},
   {"type": "contract", "title": "신제품", "text": "마요네스", "at": "마요네스가", "stamp": {"text": "1972년 6월", "at": "마요네스가"}}])
sh("wide", 9, set="home", wall="cream", time="day", chars=[ch("shopper2", 900, "happy", "hold")],
   labels=[lab("냉장고 문 쪽 그 이름", "냉장고", "lime", x=1400, y=260)])
sh("counter", 10, value={"from": 0, "to": 100, "suffix": "억 원", "at": "+0.3"}, caption="1979년 매출, 설립 10년 만 (회사 자료)", icon="coins")
sh("closeup", 11, who="founder", side="right", set="office", time="day", emotion="thinking", pose="think",
   bubble={"who": "founder", "text": "3분이면?", "icon": "clock", "at": "판이"}, labels=[lab("1981년 · 첫 번째 판", "1981년", "gold", x=600, y=260)])
sh("wide", 12, set="office", era="old", wall="cream", time="day", tag="1981년",
   chars=[ch("founder", 700, "confident", "push", beats=[{"at": "레토르트", "pose": "celebrate", "emotion": "excited"}]), ch("worker", 1250, "happy", "hold")],
   stamp={"text": "국내 첫 레토르트 파우치", "at": "레토르트", "color": "red"}, labels=[lab("3분카레", "3분카레였습니다", "gold", x=1350, y=260)])
sh("icon", 13, icons=[{"name": "clock", "label": "끓는 물에 3분", "at": "+0.2"}, {"name": "trophy", "label": "국민 브랜드 (회사 소개)", "at": "국민"}])
sh("counter", 14, value={"from": 0, "to": 83, "suffix": "%", "at": "+0.3"}, caption="국내 분말카레 시장 오뚜기 점유율 (2026년 보도)", icon="trophy")
sh("table", 15, items=[{"type": "newspaper", "title": "분말카레 시장", "text": "출시 뒤 1위 한 번도 안 내줘 (보도)", "at": "+0.2", "ring_at": "1위를"}],
   stamp={"text": "1위", "at": "1위를", "color": "green"})
sh("closeup", [16, 17], who="m1", side="left", set="home", time="night", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "?", "at": "대가는", "thought": True}, labels=[lab("가장 비싼 대가?", "대가는", "red", x=1350, y=860, size=110)])
sh("icon", 18, icons=[{"name": "book", "text": "성적표", "label": "끝에 공개", "at": "+0.2"}], stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
chap("결정", "2장")
sh("closeup", 19, who="founder", side="left", set="office", time="day", emotion="confident", pose="point",
   labels=[lab("두 번째 판: 라면", "라면이었습니다", "gold", x=1350, y=860, size=110)])
sh("table", 20, hand="founder", items=[{"type": "contract", "title": "청보식품 인수", "text": "오뚜기라면 설립", "at": "+0.2", "stamp": {"text": "1987년 11월", "at": "11월"}}])
sh("icon", 21, icons=[{"name": "factory", "label": "튀김용 기름 납품 (보도)", "at": "+0.2"}, {"name": "target", "label": "낯선 땅 아님", "at": "낯선"}])
sh("wide", [22, 23], set="street", time="day", shop="진라면 출시", tag="1988년 3월",
   chars=[ch("shopper", 650, "excited", "hold"), ch("shopper2", 1250, "smile", "point")],
   labels=[lab("순한맛", "순한맛과", "gold", x=600, y=260), lab("매운맛", "매운맛", "red", x=1320, y=260)])
sh("counter", 24, value={"from": 100, "to": 1000, "suffix": "억 원", "at": "+0.3"}, caption="회사 매출: 1979년 → 1988년 (회사 자료)", icon="chart_up")
sh("walk", 25, set="street", time="day", chars=[ch("founder", 0, "happy", "idle")],
   labels=[lab("카레 회사 → 라면 회사", "라면", "lime", x=960, y=260)])
sh("closeup", 26, who="m1", side="right", set="home", time="day", emotion="worried", pose="shrug",
   labels=[lab("좁은 문", "좁았습니다", "red", x=600, y=860, size=110)])
sh("chart", 27, board="chalk", chart={"type": "bar", "values": [1988, 2012], "labels": ["진라면 출시", "라면 시장 2위 (보도)"], "suffix": "년", "title": "2위까지 걸린 시간", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("24년", "24년", "red")])
sh("crowd", [28, 29], count=26, emotion="excited", set="street", tag="2015년 10월",
   labels=[lab("진짬뽕 출시", "진짬뽕이", "gold", size=110), lab("50일 만에 1,000만 개 (보도)", "50일", "lime")])
sh("counter", 30, value={"from": 0, "to": 20, "suffix": "%", "at": "+0.3"}, caption="2015년 오뚜기 라면 시장점유율, 처음 20% 돌파 (보도)", icon="target")
sh("closeup", 31, who="ham", side="right", set="office", time="day", emotion="calm", pose="arms_crossed",
   labels=[lab("세 번째 판: 안 올린다", "아무것도", "gold", x=600, y=860, size=100)])
sh("table", 32, hand="ham", items=[{"type": "receipt", "title": "라면값", "rows": [["2008년 4월", "마지막 인상"], ["그 뒤", "동결"]], "text": "그대로", "at": "+0.2"}],
   stamp={"text": "동결", "at": "올리지", "color": "red"})
sh("icon", 33, icons=[{"name": "chart_down", "label": "2010년 최대 6.7% 인하 (보도)", "at": "+0.2"}])
sh("wide", 34, set="street", time="day", shop="진라면", chars=[ch("shopper", 900, "happy", "hold")],
   labels=[lab("가격표 그대로", "가격표는", "lime", x=1400, y=260)])
sh("closeup", 35, who="hwang", side="left", set="office", time="night", emotion="thinking", pose="think",
   bubble={"who": "hwang", "text": "장부", "icon": "book", "at": "장부에서"})
chap("위기", "3장")
sh("crowd", [36, 37], count=20, emotion="thinking", set="void", labels=[lab("주가 꼭대기는 언제?", "언제였을까요", "gold", size=110)])
sh("counter", [38, 39], value={"from": 0, "to": 1425000, "suffix": "원", "at": "+0.3"}, caption="2016년 1월 22일 종가 (네이버)", icon="trophy",
   compare={"text": "이른바 황제주", "icon": "chart_up", "at": "황제주였습니다"})
sh("chart", [40, 41], board="white", chart={"type": "bar", "values": [49020], "labels": ["2016.1.22 시가총액"], "suffix": "억", "title": "당시 발행주식 수로 계산", "show_values": True, "at": "+0.3"})
sh("table", 42, items=[{"type": "receipt", "title": "2016년 연결 (DART)", "rows": [["매출", "2조 107억"], ["영업이익", "1,425억"]], "text": "역대 최고 주가의 해", "at": "+0.2"}])
sh("walk", 43, set="street", time="dusk", chars=[ch("ham", 0, "sad", "idle")],
   labels=[lab("2016년 9월 12일", "2016년", "cream", x=960, y=260), lab("창업주 별세", "떠납니다", "cream", x=960, y=420)])
sh("table", 44, hand="ham", items=[{"type": "contract", "title": "상속 (DART)", "text": "46만 5,543주", "at": "+0.2", "stamp": {"text": "2016년 12월 22일", "at": "상속받습니다"}}])
sh("wide", 45, set="office", era="modern", wall="blue", time="day", chars=[ch("ham", 900, "calm", "hold")],
   lower_third={"name": "함영준", "sub": "오뚜기 회장 (2010년 3월~)", "at": "+0.3"}, labels=[lab("전체 주식의 13.53%", "13.53%입니다", "gold", x=1450, y=260)])
sh("closeup", 46, who="m1", side="right", set="home", time="day", emotion="shocked", pose="facepalm",
   labels=[lab("화제의 숫자", "화제가", "red", x=600, y=860, size=110)])
sh("counter", 47, value={"from": 0, "to": 1500, "suffix": "억 원", "at": "+0.3"}, caption="상속세 약 1,500억 원 (보도)", icon="moneybag")
sh("table", 48, hand="ham", items=[{"type": "receipt", "title": "상속세 분납 (보도)", "rows": [["시작", "2017년"], ["기간", "5년"]], "text": "약 1,500억 원", "at": "+0.2"}],
   stamp={"text": "분납", "at": "나눠", "color": "red"})
sh("icon", 49, icons=[{"name": "moneybag", "label": "상속세 정면 납부", "at": "+0.2"}, {"name": "shopping", "label": "라면값 동결", "at": "라면값을"}, {"name": "heart", "label": "심장병 어린이 후원", "at": "심장병"}])
sh("counter", 50, value={"from": 0, "to": 4265, "suffix": "명", "at": "+0.3"}, caption="1992년 ~ 2016년 9월 수술 받은 어린이 (회사 자료)", icon="heart")
sh("crowd", 51, count=24, emotion="happy", set="void", labels=[lab("시식 사원 1,800여 명 정규직 (보도)", "1,800여", "lime", size=90)])
sh("title", [52, 53], text="갓(God) + 오뚜기 = 갓뚜기")
sh("wide", 54, set="board", time="day", tag="2017년 7월",
   chars=[ch("ham", 700, "smile", "present"), ch("m2", 1250, "confident", "idle")],
   labels=[lab("대통령·기업인 간담회 초청", "간담회에", "gold", x=960, y=250)])
sh("icon", 55, icons=[{"name": "building", "label": "대기업들 사이", "at": "+0.2"}, {"name": "handshake", "label": "중견기업 (보도)", "at": "중견기업으로"}])
sh("counter", 56, value={"from": 745000, "to": 799000, "suffix": "원", "at": "+0.3"}, caption="2017년 7월 24일 종가 (네이버)", icon="chart_up",
   compare={"text": "하루 +7.25%", "icon": "trophy", "at": "7.25%"})
sh("closeup", 57, who="ham", side="left", set="office", time="dusk", emotion="worried", pose="think",
   labels=[lab("꼭대기는 다시 안 옴", "꼭대기로", "red", x=1350, y=860, size=100)])
sh("table", 58, hand="ham", items=[{"type": "newspaper", "title": "2021년 7월", "text": "라면값 인상 발표", "at": "+0.2", "ring_at": "인상을"}])
sh("icon", 59, icons=[{"name": "shopping", "text": "밀가루", "label": "원재료값 (보도)", "at": "+0.2"}, {"name": "coins", "label": "인건비 (보도)", "at": "인건비가"}])
sh("title", 60, text="13년 4개월 만의 인상")
sh("chart", 61, board="chalk", chart={"type": "bar", "values": [684, 770], "labels": ["인상 전", "2021년 8월"], "suffix": "원", "title": "진라면 값 (보도)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("평균 +11.9%", "11.9%", "red")])
sh("icon", 62, icons=[{"name": "calendar", "top": "2022", "text": "9월", "label": "다시 평균 +11% (보도)", "at": "+0.2"}])
sh("table", 63, hand="ham", items=[{"type": "contract", "title": "흡수합병 (DART)", "text": "오뚜기라면지주 → 오뚜기", "at": "+0.2", "stamp": {"text": "2022년 10월", "at": "흡수합병합니다"}}])
sh("wide", 64, set="office", era="modern", wall="teal", time="day", chars=[ch("ham", 700, "confident", "present"), ch("worker", 1250, "happy", "hold")],
   labels=[lab("오뚜기라면 = 자회사", "자회사가", "lime", x=960, y=250)])
chap("베팅", "4장")
sh("chart", [65, 66], board="white", chart={"type": "bar", "values": [34545, 35391, 36745], "labels": ["2023", "2024", "2025"], "suffix": "억", "title": "연결 매출 (DART)", "show_values": True, "highlight": 2, "at": "+0.3"})
sh("closeup", 67, who="hwang", side="right", set="office", time="night", emotion="nervous", pose="stressed",
   labels=[lab("이익은 거꾸로", "거꾸로", "red", x=600, y=860, size=110)])
sh("chart", 68, board="chalk", chart={"type": "line", "values": [2549, 2220, 1773], "labels": ["2023", "2024", "2025"], "trend": "down", "suffix": "억", "title": "연결 영업이익 (DART)", "show_values": True, "at": "+0.3"})
sh("counter", 69, value={"from": 2549, "to": 1773, "suffix": "억 원", "at": "+0.3"}, caption="영업이익 2023년 → 2025년 (DART)", icon="chart_down",
   compare={"text": "2년 만에 약 -30%", "icon": "warning", "at": "30%"})
sh("table", 70, items=[{"type": "newspaper", "title": "공시 (2026년 2월)", "text": "원가율 상승 · 판매비 증가", "at": "+0.2", "ring_at": "원가율이"}])
sh("counter", 71, value={"from": 1376, "to": 721, "suffix": "억 원", "at": "+0.3"}, caption="연결 순이익 2024년 → 2025년 (DART)", icon="chart_down",
   compare={"text": "-47.6%", "icon": "warning", "at": "47.6%"})
sh("closeup", [72, 74], who="m1", side="left", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "해외는?", "at": "한국", "thought": True})
sh("chart", 75, board="white", chart={"type": "bar", "values": [32648, 4097], "labels": ["국내", "해외"], "suffix": "억", "title": "2025년 매출 (DART)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("해외 약 11%", "11%였습니다", "red")])
sh("crowd", 76, count=10, emotion="neutral", set="void", labels=[lab("10개 중 9개 가까이 국내", "아홉", "gold", size=100)])
sh("icon", 77, icons=[{"name": "factory", "label": "공장에 건다", "at": "+0.2"}])
sh("table", 78, hand="hwang", items=[{"type": "contract", "title": "미국 지주회사 출자 (DART)", "text": "565억 원", "at": "+0.2", "stamp": {"text": "2025년 5월", "at": "공시합니다"}}])
sh("map", [79, 80], places=[{"name": "안양 본사", "x": 1500, "y": 520}, {"name": "캘리포니아 라미라다", "x": 420, "y": 560}], vehicle="plane", at="캘리포니아",
   labels=[lab("북미 첫 공장 (보도)", "북미", "gold"), lab("완공 목표 2027년 말 (보도)", "완공", "lime")])
sh("closeup", [81, 82], who="hwang", side="left", set="office", time="night", emotion="worried", pose="think",
   stamp={"text": "순손실 약 228억", "at": "228억", "color": "red"}, labels=[lab("미국 지주회사 2025년 (DART)", "2025년", "cream", x=1350, y=860, size=80)])
sh("icon", 83, icons=[{"name": "building", "text": "日", "label": "2026년 일본 판매 법인", "at": "+0.2"}])
sh("table", [84, 85], hand="ham", items=[{"type": "contract", "title": "구미 수출 전용 라면 공장 (보도)", "text": "2,000억 원 규모 협약", "at": "+0.2", "stamp": {"text": "~2029년", "at": "2029년까지입니다"}}])
sh("wide", 86, set="office", era="modern", wall="grey", time="day", tag="안양",
   chars=[ch("hwang", 700, "confident", "point"), ch("worker", 1250, "happy", "hold")],
   labels=[lab("도시형 공장 신축", "도시형", "gold", x=1300, y=260)])
sh("chart", 87, board="chalk", chart={"type": "bar", "values": [1570, 1970], "labels": ["처음 공시", "정정 (2026년 2월)"], "suffix": "억", "title": "안양 도시형 공장 투자액 (DART)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("완공 예정 2027년 4월", "완공", "lime")])
sh("closeup", [88, 89], who="ham", side="right", set="office", time="day", emotion="thinking", pose="think",
   bubble={"who": "ham", "text": "결과는?", "at": "결과는", "thought": True})
sh("counter", 90, value={"from": 0, "to": 1174, "suffix": "억 원", "at": "+0.3"}, caption="2026년 3분기 해외 매출 (DART)", icon="chart_up",
   compare={"text": "1년 전보다 +17.6%", "icon": "trophy", "at": "17.6%"})
chap("성적표", "5장")
sh("icon", [91, 92], icons=[{"name": "book", "text": "성적표", "label": "오뚜기 성적표", "at": "+0.2"}, {"name": "shopping", "text": "카레", "label": "시작: 1969년", "at": "1969년"}],
   stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("wide", 93, set="board", time="day",
   chars=[ch("ham", 700, "confident", "present"), ch("hwang", 1250, "smile", "wave")],
   lower_third={"name": "황성만", "sub": "오뚜기 대표이사 사장", "at": "황성만"})
sh("closeup", 94, who="ham", side="left", set="office", time="day", emotion="calm", pose="hips",
   labels=[lab("최대주주 지분 25.07% (DART)", "25.07%를", "gold", x=1350, y=860, size=90)])
sh("chart", [95, 96], board="chalk", chart={"type": "bar", "values": [20107, 36745], "labels": ["2016년", "2025년"], "suffix": "억", "title": "연결 매출 (DART)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("매출 +82.7%", "82.7%", "green")])
sh("counter", 97, value={"from": 1425, "to": 1773, "suffix": "억 원", "at": "+0.3"}, caption="영업이익 2016년 → 2025년 (DART)", icon="chart_up",
   compare={"text": "+24.4%", "icon": "trophy", "at": "24.4%"})
sh("table", [98, 99], items=[{"type": "receipt", "title": "주가 (종가)", "rows": [["2016.12.22", "668,000원"], ["2026.11.25", "287,500원"]], "text": "-57.0%", "at": "+0.2"}],
   stamp={"text": "-57.0%", "at": "57.0%", "color": "red"})
sh("wide", 100, set="office", era="old", wall="cream", time="day", chars=[ch("founder", 900, "happy", "celebrate")],
   stamp={"text": "최고의 결정: 3분카레", "at": "3분카레입니다", "color": "green"})
sh("icon", 101, icons=[{"name": "shopping", "text": "카레", "label": "분말카레 점유율 83% (보도)", "at": "+0.2"}])
sh("closeup", 102, who="hwang", side="right", set="office", time="night", emotion="sad", pose="facepalm",
   stamp={"text": "가장 비싼 대가", "at": "대가는", "color": "red"})
sh("versus", 103, colors=["#D8F0D8", "#F6C7B6"], left={"who": "hwang", "title": "2025년 매출 역대 최대", "emotion": "happy", "pose": "celebrate", "at": "+0.2"},
   right={"who": "hwang", "title": "영업이익 2023년보다 약 -30%", "emotion": "sad", "pose": "facepalm", "at": "30%"})
sh("chart", 104, board="white", chart={"type": "bar", "values": [1579, 1409], "labels": ["2025년 1~9월", "2026년 1~9월"], "suffix": "억", "title": "연결 영업이익 (DART)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("매출 +3.5%", "3.5%", "green"), lab("영업이익 -10.8%", "10.8%", "red")])
sh("counter", 105, value={"from": 553, "to": 363, "suffix": "억 원", "at": "+0.3"}, caption="3분기 영업이익 2025년 → 2026년 (DART)", icon="chart_down",
   compare={"text": "-34.5%", "icon": "warning", "at": "34.5%"})
sh("closeup", 106, who="hwang", side="left", set="office", time="night", emotion="worried", pose="stressed",
   labels=[lab("원료값 · 물류비 (회사 설명, 보도)", "원료값과", "cream", x=1350, y=860, size=80)])
chap("반전", "6장")
sh("walk", 107, set="street", time="dusk", chars=[ch("m1", 0, "calm", "idle")], labels=[lab("처음 그 숫자", "숫자의", "gold", x=960, y=260)])
sh("chart", [108, 109], board="chalk", chart={"type": "bar", "values": [49020, 11523], "labels": ["2016.1.22", "2026.11.25"], "suffix": "억", "title": "시가총액 (계산 · 네이버)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("4분의 1 미만", "4분의", "red")])
sh("icon", [110, 111], icons=[{"name": "coins", "label": "PBR 0.47배 (네이버)", "at": "+0.2"}, {"name": "book", "text": "장부", "label": "순자산의 절반도 안 됨", "at": "절반"}],
   stamp={"text": "0.47배", "at": "0.47배입니다", "color": "red"})
sh("table", [112, 113], hand="hwang", items=[{"type": "contract", "title": "자기주식 소각 결정 (DART)", "text": "7만 2,551주", "at": "+0.2", "stamp": {"text": "약 162억 원", "at": "162억"}}])
sh("title", 114, text="13년 묶은 라면값, 주가는 꼭대기의 약 5분의 1")
sh("closeup", 115, who="ham", side="right", set="office", time="dusk", emotion="calm", pose="present",
   labels=[lab("착한 이름", "착한", "gold", x=600, y=860, size=110)])
sh("map", 116, places=[{"name": "한국", "x": 1450, "y": 520}, {"name": "미국", "x": 420, "y": 560}, {"name": "일본", "x": 1700, "y": 420}], vehicle="ship", at="+0.3",
   labels=[lab("숙제: 한국 밖", "한국", "red")])
sh("wide", [117, 120], set="office", era="modern", wall="blue", time="day",
   chars=[ch("founder", 600, "happy", "wave"), ch("m1", 960, "happy", "wave"), ch("ham", 1320, "smile", "celebrate")],
   labels=[lab("구독 · 좋아요", "구독과", "lime", x=960, y=230, size=130), lab("출처는 설명란", "출처는", "cream", x=960, y=420)],
   polaroid={"at": "출처는", "who": "founder", "caption": "카레로 시작, 숙제는 한국 밖"})

# 빈 화면 방지(2026-11-20 검수): 그래픽 장면의 첫 요소는 장면 시작 직후에 나오게 하고, 나머지만 대사 낱말에 맞춘다
for d in X:
    k = d.get("kind")
    if k == "icon" and d.get("icons"): d["icons"][0]["at"] = "+0.2"
    if k == "table" and d.get("items"): d["items"][0]["at"] = "+0.2"
    if k == "chart" and d.get("chart"): d["chart"]["at"] = "+0.3"
    if k == "counter" and d.get("value"): d["value"]["at"] = "+0.3"

story = {"title": "오뚜기_v2", "mood": "dramatic", "cast": {
    "founder": {"skin": "light", "outfit": "suit", "color": "#3E4A3A", "shirt": "#F2F2F2", "tie": "#C8242C", "hair": "short", "hair_col": "#8A8A8A"},
    "ham": {"skin": "tan", "outfit": "suit", "color": "#1F2E5C", "shirt": "#F2F2F2", "tie": "#B8862E", "hair": "slick", "hair_col": "#2A2420"},
    "hwang": {"skin": "fair", "outfit": "suit", "color": "#5A5A64", "shirt": "#F2F2F2", "tie": "none", "hair": "short", "hair_col": "#3A3A3A", "glasses": True},
    "m1": {"skin": "fair", "outfit": "sweater", "color": "#5E8C6A", "hair": "curly", "hair_col": "#3A2C22"},
    "m2": {"skin": "olive", "outfit": "suit", "color": "#2E2E36", "tie": "#2E6FB8", "hair": "bald"},
    "worker": {"skin": "light", "outfit": "tshirt", "color": "#F2C94C", "hair": "short", "hair_col": "#2A2420", "hat": "cap", "hat_col": "#F2F2F2"},
    "shopper": {"skin": "fair", "outfit": "tshirt", "color": "#D0703A", "hair": "short", "hair_col": "#1E1A18"},
    "shopper2": {"skin": "fair", "outfit": "sweater", "color": "#8C5EA0", "hair": "long", "hair_col": "#2A2420"}},
  "shots": X}
for d in X:
    if d.get("kind") == "walk":
        for c in d.get("chars", []): c.pop("x", None)
json.dump(story, open(os.path.join(P, "story.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(X), "shots")
