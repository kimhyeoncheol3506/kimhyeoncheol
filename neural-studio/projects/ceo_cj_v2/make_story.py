#!/usr/bin/env python3
"""CJ제일제당 v2 스토리보드."""
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

# 인트로 · 위기부터: 해외가 국내를 넘은 해의 순손실 4,170억 → 첫 순손실(보도) → 이익 감소 → 주가 (0초부터 그림·글자)
sh("wide", 0, set="street", time="dusk", shop="해외 마트 · K푸드",
   chars=[ch("m1", 700, "excited", "present", beats=[{"at": "순손실을", "pose": "facepalm", "emotion": "shocked"}]), ch("jh", 1250, "worried", "hold")],
   labels=[lab("순손실 4,170억 원", "+0.1", "red", x=1350, y=250, size=110), lab("해외 매출이 국내를 넘은 해", "+0.1", "gold", x=1350, y=410, size=75)])
sh("table", 1, items=[{"type": "newspaper", "title": "CJ제일제당 연간 실적", "text": "출범 뒤 첫 순손실 (보도)", "at": "+0.2", "ring_at": "처음"}],
   stamp={"text": "첫 순손실", "at": "처음", "color": "red"})
sh("versus", 2, colors=["#F6E0B6", "#F6C7B6"], left={"who": "m1", "title": "영업이익 감소", "emotion": "worried", "pose": "stressed", "at": "+0.2"},
   right={"who": "m1", "title": "바이오는 더 크게 흔들", "emotion": "shocked", "pose": "facepalm", "at": "바이오"})
sh("chart", 3, board="chalk", chart={"type": "line", "values": [9, 8, 6.5, 5, 3.5], "trend": "down", "show_values": False, "title": "주가 · 꼭대기에서 절반 넘게", "at": "+0.3"})
sh("skyline", 4, time="day", labels=[lab("CJ제일제당", "CJ제일제당입니다", size=150), lab("설탕 → 밥 · 만두", "설탕", "gold", y=820, size=80)])
sh("closeup", 5, who="m1", side="right", set="home", time="night", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "왜?", "at": "+0.2", "thought": True})
OFF = 2
chap("판돈", "1장")
sh("wide", [4, 5], set="office", era="old", wall="sand", time="day", tag="1953년 11월 · 부산", calendar="1953 11",
   chars=[ch("lee", 900, "confident", "present", beats=[{"at": "만들어", "pose": "celebrate", "emotion": "excited"}])],
   props=[{"icon": "factory", "x": 1500, "y": 760, "s": 0.8, "at": "설탕"}],
   lower_third={"name": "이병철", "sub": "삼성 창업주 · 제일제당 설립", "at": "이병철이"})
sh("icon", 6, icons=[{"name": "book", "text": "1편", "label": "삼성 이야기는 1편에서", "at": "+0.2"}, {"name": "shopping", "text": "설탕", "label": "오늘은 설탕 쪽", "at": "설탕"}])
sh("chart", 7, board="chalk", chart={"type": "bar", "values": [300, 100], "labels": ["수입 설탕", "제일제당 설탕"], "suffix": "환", "title": "설탕 한 근 값 (보도)", "show_values": True, "highlight": 1, "at": "+0.3"})
sh("icon", [8, 9], icons=[{"name": "shopping", "text": "설탕", "label": "설탕", "at": "+0.2"}, {"name": "shopping", "text": "밀가루", "label": "밀가루", "at": "밀가루"}, {"name": "shopping", "text": "조미료", "label": "조미료", "at": "조미료였습니다"}],
   stamp={"text": "재료 파는 회사", "at": "재료를", "color": "red"})
sh("table", [10, 11], items=[{"type": "contract", "title": "독립 경영 선언", "text": "제일제당 · 삼성그룹에서", "at": "+0.2", "stamp": {"text": "1993년", "at": "선언합니다"}},
   {"type": "newspaper", "title": "계열 분리", "text": "1997년 법적 마무리 (보도)", "at": "법적인"}])
sh("wide", 12, set="office", era="modern", wall="blue", time="day",
   chars=[ch("jh", 900, "confident", "present", beats=[{"at": "회장입니다", "pose": "hips"}])],
   lower_third={"name": "이재현", "sub": "CJ 회장 (1993년 제일제당 상무)", "at": "이재현"})
sh("closeup", [13, 15], who="m1", side="left", set="home", time="night", emotion="thinking", pose="think",
   beats=[{"who": "m1", "at": "성적표를", "pose": "point", "emotion": "confident"}], bubble={"who": "m1", "text": "?", "at": "판돈은", "thought": True}, labels=[lab("가장 엉뚱한 판돈?", "엉뚱한", "red", x=1350, y=860, size=110)])
chap("결정", "2장")
sh("icon", 16, icons=[{"name": "laptop", "text": "영화", "label": "답은 영화", "at": "+0.2"}])
sh("wide", 17, set="board", time="day", tag="1995년 4월 · 할리우드",
   chars=[ch("jh", 650, "confident", "present"), ch("dw", 1250, "smile", "idle", beats=[{"at": "드림웍스에", "pose": "wave", "emotion": "happy"}])],
   lower_third={"name": "드림웍스", "sub": "스필버그 등이 세운 신생 영화사", "at": "드림웍스에"})
sh("counter", [18, 19], value={"from": 0, "to": 3, "suffix": "억 달러", "at": "3억"}, caption="제일제당의 드림웍스 투자 (보도)", icon="moneybag",
   compare={"text": "자본금 10억 달러 · 2대 주주", "icon": "trophy", "at": "2대"})
sh("table", 20, hand="jh", items=[{"type": "contract", "title": "드림웍스 투자 계약", "text": "일본 제외 아시아 판권", "at": "+0.2"}],
   stamp={"text": "계약", "at": "판권이었습니다", "color": "red"})
sh("crowd", [21, 22], count=24, emotion="shocked", set="void",
   labels=[lab("설탕 회사가 무슨 문화냐?", "문화냐는", "red", size=100), lab("자충수? (보도)", "자충수라는", "cream")])
sh("icon", [23, 24], icons=[{"name": "laptop", "text": "멀티", "label": "1995년 8월 멀티미디어사업부", "at": "+0.2"}, {"name": "chart_up", "label": "훗날 CJ ENM의 뿌리", "at": "뿌리가"}])
sh("crowd", 25, count=26, emotion="excited", set="street", tag="2019년 5월",
   labels=[lab("기생충 · 칸 황금종려상", "황금종려상을", "gold", size=100), lab("CJ 투자·배급", "배급한", "lime")])
sh("wide", [26, 27], set="street", time="day", shop="편의점", tag="1996년 12월",
   chars=[ch("jh", 760, "confident", "hold", beats=[{"at": "햇반을", "pose": "present", "emotion": "excited"}])],
   labels=[lab("두 번째 판: 밥", "밥이었습니다", "gold", x=1350, y=250), lab("즉석밥 햇반", "햇반을", "lime", x=1350, y=420)])
sh("closeup", 28, who="m1", side="left", set="home", time="day", emotion="shocked", pose="shrug",
   bubble={"who": "m1", "text": "밥을 왜 사 먹어?", "at": "+0.3"}, labels=[lab("첫 반응 (보도)", "반응은", "cream", x=1350, y=860, size=90)])
sh("counter", 29, value={"from": 0, "to": 68, "suffix": "억 4천만 개", "at": "+0.3"}, caption="햇반 누적 판매 (2025년 말, 보도)", icon="gift")
sh("icon", [30, 32], icons=[{"name": "coins", "label": "30년 누적 매출 약 10조 원", "at": "+0.2"}, {"name": "target", "label": "즉석밥 점유율 약 60%", "at": "60%라고"},
   {"name": "trophy", "label": "2025년 1조 1,800억 원 (보도)", "at": "1조"}])
sh("walk", [33, 34], set="street", time="day", chars=[ch("jh", 0, "happy", "idle")],
   labels=[lab("세 번째 판: 만두", "만두였습니다", "gold", x=600, y=260), lab("비비고 → 해외", "해외로", "lime", x=1350, y=260)])
sh("counter", [35, 36], value={"from": 0, "to": 1, "suffix": "조 원", "at": "+0.3"}, caption="2020년 비비고 만두 매출 (회사 발표)", icon="trophy",
   compare={"text": "그중 해외 65%", "icon": "target", "at": "65%였다고"})
sh("closeup", [37, 38], who="jh", side="right", set="office", time="day", emotion="confident", pose="point",
   bubble={"who": "jh", "text": "슈완스", "icon": "target", "at": "슈완스입니다"}, labels=[lab("가장 큰 판", "가장", "gold", x=600, y=860)])
sh("table", [39, 40], hand="jh", items=[{"type": "contract", "title": "슈완스 인수 결정", "text": "이사회 2018년 11월 15일", "at": "+0.2", "stamp": {"text": "인수", "at": "결정합니다"}},
   {"type": "receipt", "title": "확정 공시 (DART)", "rows": [["현금 인수", "1조 8,867억 원"], ["공시", "2019년 2월"]], "text": "슈완스", "at": "확정"}],
   stamp={"text": "1조 8,867억", "at": "1조", "color": "red"})
sh("map", 41, places=[{"name": "한국", "x": 1450, "y": 470}, {"name": "미국", "x": 450, "y": 520}], vehicle="ship", at="+0.3",
   labels=[lab("슈완스 유통망 타고 비비고 만두 (보도)", "비비고", "gold")])
sh("table", 42, items=[{"type": "letter", "title": "인수용 미국 법인 (DART)", "text": "대표자: 강신호", "at": "+0.2", "ring_at": "강신호라는"}])
chap("위기", "3장")
sh("closeup", [43, 44], who="m1", side="right", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "몇 %?", "at": "몫은", "thought": True})
sh("counter", [45, 46], value={"from": 0, "to": 51.4, "suffix": "%", "at": "+0.3"}, caption="2025년 식품 매출 중 해외 (회사 발표)", icon="target",
   compare={"text": "해외 5조 9,247억 원", "icon": "coins", "at": "5조"})
sh("title", 47, text="그런데, 다른 숫자들")
sh("chart", [48, 49], board="white", chart={"type": "bar", "values": [14521, 12336], "labels": ["2024년", "2025년"], "suffix": "억", "title": "영업이익 (DART 연결)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("매출 27조 3,426억 · 제자리", "27조", "gold"), lab("-15%", "15%", "red")])
sh("versus", [50, 53], colors=["#F6E0B6", "#F6C7B6"], left={"who": "m1", "title": "식품 영업이익 5,261억 · -15.1%", "emotion": "worried", "pose": "stressed", "at": "식품"},
   right={"who": "m1", "title": "바이오 2,968억 → 1,802억 · -39.3%", "emotion": "shocked", "pose": "facepalm", "at": "바이오"},
   stamp={"text": "-39.3%", "at": "39.3%", "color": "red"})
sh("table", [54, 55], items=[{"type": "newspaper", "title": "2025년 연간 실적", "text": "연결 순손실 4,170억 원", "at": "+0.2", "stamp": {"text": "분할 뒤 첫 순손실 (보도)", "at": "처음"}}])
sh("icon", 56, icons=[{"name": "warning", "label": "유·무형자산 평가 손실 (회사 설명)", "at": "+0.2"}, {"name": "coins", "label": "현금 유출 없음 (보도)", "at": "현금이"}])
sh("closeup", 57, who="m1", side="left", set="home", time="night", emotion="worried", pose="stressed",
   labels=[lab("주가도", "주가도", "red", x=1350, y=860, size=120)])
sh("chart", [58, 60], board="chalk", chart={"type": "bar", "values": [492500, 182500], "labels": ["2021.8.4", "2026.11.20"], "suffix": "원", "title": "주가 (종가, 네이버)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("-62.9%", "62.9%", "red")])
sh("counter", [61, 62], value={"from": 0, "to": 27474, "suffix": "억 원", "at": "+0.3"}, caption="보통주 시가총액 (2026.11.20, 계산)", icon="building",
   compare={"text": "1년 매출의 약 10분의 1", "icon": "warning", "at": "10분의"})
chap("베팅", "4장")
sh("closeup", [63, 64], who="m1", side="right", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "뭘 팔까?", "at": "팔았을까요", "thought": True})
sh("table", [65, 67], hand="kang", stamp={"text": "매각", "at": "14개", "color": "red"}, items=[{"type": "contract", "title": "F&C 14개사 매각 계약", "text": "→ 드 휴스 등 4곳", "at": "+0.2", "stamp": {"text": "2025.10.1", "at": "맺습니다"}},
   {"type": "receipt", "title": "공시 처분 금액 (DART)", "rows": [["처분 금액", "2,109억 원"], ["추가 금액", "2029년 결정"]], "text": "종결 전", "at": "2,109억"}])
sh("icon", [68, 69], icons=[{"name": "hourglass", "label": "추가 금액은 2029년에", "at": "+0.2"}, {"name": "calendar", "top": "2026", "text": "안", "label": "2026년 안 종결 예정", "at": "2026년"}, {"name": "handshake", "label": "나라별 승인 절차", "at": "나라별"}])
sh("closeup", [70, 71], who="kang", side="left", set="office", time="day", emotion="calm", pose="idle",
   beats=[{"who": "kang", "at": "슈완스", "pose": "hold", "emotion": "thinking"}],
   lower_third={"name": "강신호", "sub": "대표이사 (2024년 4월 ~ 2026년 3월)", "at": "강신호는"},
   labels=[lab("슈완스 인수 서류의 그 이름", "슈완스", "cream", x=1350, y=860, size=80)])
sh("wide", [72, 73], set="board", time="day", tag="2026년 3월 24일",
   chars=[ch("yoon", 960, "confident", "present", enter="left", beats=[{"at": "윤석환입니다", "pose": "wave", "emotion": "smile"}])],
   lower_third={"name": "윤석환", "sub": "CJ제일제당 대표이사 (2026년 3월~)", "at": "윤석환입니다"})
sh("closeup", 74, who="yoon", side="right", set="office", time="day", emotion="confident", pose="point",
   bubble={"who": "yoon", "text": "지금 바꾸지 않으면…", "at": "+0.4"}, labels=[lab("(보도)", "말했다고", "cream", x=600, y=860)])
sh("table", [75, 76], hand="yoon", items=[{"type": "contract", "title": "합작법인 출자계약", "text": "CJ × ADM · 사료용 아미노산", "at": "+0.2", "stamp": {"text": "2026.10.2", "at": "맺습니다"}}],
   labels=[lab("두 번째 결정: 바이오", "바이오였습니다", "gold")])
sh("versus", 77, colors=["#F6C7B6", "#D9D9E6"], left={"who": "yoon", "title": "CJ 쪽 63", "emotion": "confident", "pose": "present", "at": "63"},
   right={"who": "adm", "title": "ADM 37", "emotion": "smile", "pose": "idle", "at": "37을"},
   labels=[lab("미국 · 멕시코 · 브라질 사료용 아미노산", "+0.3", "cream", x=960, y=900, size=70)])
sh("icon", 78, icons=[{"name": "warning", "label": "기업결합 신고 · 승인 남음", "at": "+0.2"}])
sh("chart", [79, 81], board="white", chart={"type": "bar", "values": [2576, 3090], "labels": ["2026년 2분기", "2026년 3분기"], "suffix": "억 원", "title": "분기 영업이익 (DART)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("2분기 2,576억", "2,576억", "gold"), lab("+20%", "20%", "green")])
sh("counter", 82, value={"from": 0, "to": 8047, "suffix": "억 원", "at": "+0.3"}, caption="2026년 1~9월 영업이익 (DART 잠정)", icon="chart_down",
   compare={"text": "1년 전(사료 제외)보다 -14.2%", "icon": "warning", "at": "14.2%"})
chap("성적표", "5장")
sh("icon", [83, 84], icons=[{"name": "book", "text": "성적표", "label": "CJ제일제당 성적표", "at": "+0.2"}, {"name": "shopping", "text": "설탕", "label": "시작: 한 근 100환", "at": "100환짜리"}],
   stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("chart", [85, 86], board="chalk", chart={"type": "bar", "values": [273426, 115223], "labels": ["2025년 전체 매출", "식품 매출"], "suffix": "억", "title": "2025년 매출 (DART 연결)", "show_values": True, "highlight": 1, "at": "+0.3"})
sh("table", [87, 88], items=[{"type": "receipt", "title": "잘한 결정", "rows": [["1996년", "햇반"], ["2020년", "비비고 만두 1조"]], "text": "해외 비중 51.4%", "at": "+0.2"}],
   stamp={"text": "최고의 결정", "at": "51.4%", "color": "green"})
sh("closeup", 89, who="m1", side="left", set="home", time="night", emotion="sad", pose="facepalm",
   stamp={"text": "-4,170억", "at": "4,170억", "color": "red"}, labels=[lab("가장 비싼 숫자", "비싼", "cream", x=1350, y=860)])
sh("table", [90, 91], items=[{"type": "receipt", "title": "강신호 대표 취임일 종가", "rows": [["2024.4.1", "311,000원"]], "text": "대표이사 재임 주가", "at": "+0.2"}])
sh("chart", [92, 93], board="white", chart={"type": "bar", "values": [311000, 217500], "labels": ["2024.4.1 취임", "2026.3.24 사임"], "suffix": "원", "title": "강신호 대표 재임 주가 (종가)", "show_values": True, "highlight": 1, "at": "+0.3"},
   stamp={"text": "-30.1%", "at": "30.1%", "color": "red"})
sh("counter", 94, value={"from": 217500, "to": 182500, "suffix": "원", "at": "+0.3"}, caption="윤석환 대표 선임일 → 2026.11.20 종가", icon="chart_down",
   compare={"text": "-16.1%", "icon": "warning", "at": "16.1%"})
sh("icon", 95, icons=[{"name": "building", "label": "최대주주 CJ(주) · 특수관계인 합계 41.81%", "at": "+0.2"}])
chap("반전", "6장")
sh("closeup", 96, who="m1", side="left", set="home", time="dusk", emotion="calm", pose="explain")
sh("crowd", 97, count=20, emotion="shocked", set="void", labels=[lab("1995년 · 3억 달러", "3억", "gold", size=100), lab("설탕 회사가 무슨 문화냐?", "문화냐였습니다", "red", size=95)])
sh("map", 98, places=[{"name": "한국", "x": 1450, "y": 470}, {"name": "미국", "x": 450, "y": 520}, {"name": "유럽", "x": 900, "y": 330}], vehicle="plane", at="+0.3",
   labels=[lab("식품 매출 절반 이상 = 해외", "절반", "gold")])
sh("versus", 99, colors=["#D8F0D8", "#F6C7B6"], left={"who": "jh", "title": "해외 > 국내 (처음)", "emotion": "happy", "pose": "celebrate", "at": "해외"},
   right={"who": "jh", "title": "순손실 (분할 뒤 처음)", "emotion": "sad", "pose": "facepalm", "at": "순손실을"})
sh("closeup", 100, who="yoon", side="right", set="office", time="day", emotion="calm", pose="arms_crossed",
   labels=[lab("바이오 20년+", "바이오에서", "lime", x=600, y=860, size=110)])
sh("title", 101, text="숙제: 많이 파는 것보다 남기는 것")
sh("wide", [102, 105], set="office", era="modern", wall="blue", time="day",
   chars=[ch("jh", 600, "happy", "wave"), ch("m1", 960, "happy", "wave"), ch("yoon", 1320, "smile", "celebrate")],
   labels=[lab("구독 · 좋아요", "구독과", "lime", x=960, y=230, size=130), lab("출처는 설명란", "출처는", "cream", x=960, y=420)],
   polaroid={"at": "출처는", "who": "m1", "caption": "설탕에서 K푸드까지, 숙제는 남기는 것"})

# 빈 화면 방지(2026-11-20 검수): 그래픽 장면의 첫 요소는 장면 시작 직후에 나오게 하고, 나머지만 대사 낱말에 맞춘다
for d in X:
    k = d.get("kind")
    if k == "icon" and d.get("icons"): d["icons"][0]["at"] = "+0.2"
    if k == "table" and d.get("items"): d["items"][0]["at"] = "+0.2"
    if k == "chart" and d.get("chart"): d["chart"]["at"] = "+0.3"
    if k == "counter" and d.get("value"): d["value"]["at"] = "+0.3"

story = {"title": "CJ제일제당_v2", "mood": "dramatic", "cast": {
    "lee": {"skin": "light", "outfit": "suit", "color": "#3A3A3A", "shirt": "#F2F2F2", "tie": "#5A2A2A", "hair": "slick", "hair_col": "#2A2420"},
    "jh": {"skin": "fair", "outfit": "suit", "color": "#2E3A5C", "shirt": "#F2F2F2", "tie": "#C8102E", "hair": "short", "hair_col": "#2A2420", "glasses": True},
    "kang": {"skin": "tan", "outfit": "suit", "color": "#4A4A52", "shirt": "#F2F2F2", "tie": "#2E6FB8", "hair": "short", "hair_col": "#3A3230"},
    "yoon": {"skin": "light", "outfit": "sweater", "color": "#3F6E8C", "hair": "slick", "hair_col": "#2A2420", "glasses": True},
    "dw": {"skin": "fair", "outfit": "tshirt", "color": "#C77A2E", "hair": "long", "hair_col": "#7A5A3A", "hat": "cap", "hat_col": "#1F2A3A"},
    "adm": {"skin": "brown", "outfit": "suit", "color": "#1F4A3A", "tie": "#E0A020", "hair": "bald"},
    "m1": {"skin": "fair", "outfit": "hoodie", "color": "#5E8C6A", "hair": "curly", "hair_col": "#3A2C22"}},
  "shots": X}
for d in X:
    if d.get("kind") == "walk":
        for c in d.get("chars", []): c.pop("x", None)
json.dump(story, open(os.path.join(P, "story.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(X), "shots")
