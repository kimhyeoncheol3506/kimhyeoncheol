#!/usr/bin/env python3
"""두산에너빌리티 v2 스토리보드."""
import json, os
P = os.path.dirname(os.path.abspath(__file__)); X = []
def sh(kind, s, **k):
    d = {"kind": kind}
    if s is not None: d["s"] = s if isinstance(s, list) else [s]
    d.update(k); X.append(d)
def lab(text, at, color="lime", **k): return dict(text=text, at=at, color=color, **k)
def ch(id, x, emotion="neutral", pose="idle", **k): return dict(id=id, x=x, emotion=emotion, pose=pose, **k)
def chap(t, n): sh("title", None, text=t, sub=n, hold=1.6)

# 인트로 · 1조 빌린 회사의 역설
sh("table", 0, hand="banker", items=[{"type": "cash", "text": "1조 원", "at": "1조"}], stamp={"text": "겨우 버팀", "at": "버텼습니다", "color": "red"},
   labels=[lab("2020년 3월", "2020년", "gold")])
sh("counter", 1, value={"from": 0, "to": 62, "suffix": "배", "at": "62배가"}, caption="2020년 3월 바닥 → 2026년 5월 꼭대기 (수정 종가)", icon="chart_up")
sh("chart", 2, board="white", chart={"type": "line", "values": [136400, 86800, 67100, 82500, 81900, 53600, 40250], "trend": "down", "show_values": False,
   "title": "주가 2026년 5월 → 11월 (네이버 종가)", "at": "꼭대기에서"}, labels=[lab("꼭대기에서 -70%", "70%가", "red")])
sh("skyline", 3, time="day", labels=[lab("두산에너빌리티", "두산에너빌리티입니다", size=150)])
chap("판돈", "1장")
sh("wide", 4, set="office", era="old", wall="sand", time="day", tag="1962년", calendar="1962 9",
   chars=[ch("f1", 900, "confident", "present")], labels=[lab("현대양행", "현대양행입니다", "gold", x=1400, y=260, size=120)])
sh("table", 5, items=[{"type": "contract", "title": "1980년 10월", "text": "현대양행 → 한국중공업", "at": "+0.2", "stamp": {"text": "공기업", "at": "공기업"}}])
sh("icon", [6, 7], icons=[{"name": "factory", "label": "원자로 설비", "at": "원자로"}, {"name": "target", "label": "터빈", "at": "터빈을"},
   {"name": "heart", "label": "전기 기계의 심장", "at": "심장을"}])
sh("wide", [8, 9], set="board", time="day", tag="2000년 12월",
   chars=[ch("official", 650, "calm", "present"), ch("exec1", 1250, "confident", "hold", beats=[{"at": "사들였다고", "pose": "celebrate", "emotion": "happy"}])],
   labels=[lab("민영화", "민간에", "cream", x=960, y=230), lab("지분 36%", "36%를", "gold", x=960, y=380)],
   stamp={"text": "3,057억 원 (보도)", "at": "3,057억", "color": "red"})
sh("versus", [10, 11], colors=["#D9D9E6", "#C9DDF2"], left={"who": "official", "title": "한국중공업", "emotion": "calm", "pose": "idle", "at": "+0.2"},
   right={"who": "exec1", "title": "두산중공업", "emotion": "happy", "pose": "present", "at": "두산중공업으로"},
   labels=[lab("최대주주 = 두산 (2002년~)", "최대주주는", "gold", x=960, y=900)])
sh("closeup", [12, 13], who="m1", side="left", set="home", time="night", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "?", "at": "무너뜨린", "thought": True}, labels=[lab("무너뜨린 것 / 일으킨 것", "무너뜨린", "red", x=1350, y=860, size=90)])
sh("icon", 14, icons=[{"name": "book", "text": "성적표", "label": "끝에 공개", "at": "성적표를"}], stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("wide", [15, 16], set="office", era="modern", wall="blue", time="day", chars=[ch("park", 900, "confident", "present", beats=[{"at": "2016년", "pose": "hips"}])],
   lower_third={"name": "박지원", "sub": "두산에너빌리티 대표이사 회장", "at": "박지원"},
   labels=[lab("2001년~ 이 회사", "2001년부터", "cream", x=1450, y=260), lab("2016년 대표이사 회장 (보도)", "2016년", "gold", x=1450, y=400, size=70)])
sh("table", [17, 18], items=[{"type": "letter", "title": "공시 · 임원 현황", "text": "대표이사 회장 박지원", "at": "+0.2"}],
   stamp={"text": "최대주주의 특수관계인", "at": "특수관계인이기도", "color": "red"})
chap("결정", "2장")
sh("closeup", [19, 20], who="eng", side="left", set="office", time="day", emotion="excited", pose="present",
   bubble={"who": "eng", "text": "가스터빈", "icon": "target", "at": "가스터빈이었습니다"}, labels=[lab("집채만 한 엔진", "집채만", "lime", x=1350, y=860, size=100)])
sh("map", 21, places=[{"name": "미국", "x": 300, "y": 420}, {"name": "독일", "x": 820, "y": 300}, {"name": "이탈리아", "x": 900, "y": 470},
   {"name": "일본", "x": 1600, "y": 420}, {"name": "한국", "x": 1450, "y": 470}], vehicle="ship", at="미국,",
   labels=[lab("4개 나라만 (보도)", "이탈리아만", "gold")])
sh("icon", 22, icons=[{"name": "shopping", "text": "수입", "label": "한국 = 들여오는 나라", "at": "들여오는"}])
sh("table", [23, 24], hand="park", items=[{"type": "contract", "title": "가스터빈 독자 개발", "text": "직접 만든다", "at": "+0.2", "stamp": {"text": "2013년", "at": "2013년부터"}}],
   labels=[lab("개발비 1조 원+ (보도)", "1조", "gold")])
sh("wide", [25, 26], set="street", time="day", shop="창원 공장", tag="2019년 9월 · 창원",
   chars=[ch("eng", 700, "excited", "push", beats=[{"at": "조립됩니다", "pose": "celebrate", "emotion": "happy"}])],
   props=[{"icon": "factory", "x": 1350, "y": 690, "s": .7, "at": "창원"}],
   labels=[lab("270MW급", "270메가와트급", "gold", x=1350, y=260), lab("부품 4만여 개", "4만여", "cream", x=1350, y=420)])
sh("counter", 27, value={"from": 0, "to": 5, "suffix": "번째", "at": "다섯"}, caption="대형 가스터빈 독자 개발 (2019년 보도)", icon="trophy")
sh("closeup", 28, who="eng", side="right", set="office", time="dusk", emotion="worried", pose="think", labels=[lab("해외 판매 아직 0번", "해외에", "red", x=600, y=860, size=90)])
chap("위기", "3장")
sh("closeup", [29, 30], who="park", side="left", set="office", time="dusk", emotion="worried", pose="think",
   labels=[lab("2018년 순손실 4,217억 원", "4,217억", "red", x=1350, y=860, size=80)])
sh("chart", [31, 32], board="chalk", chart={"type": "bar", "values": [4217, 1044], "labels": ["2018년", "2019년"], "suffix": "억 원", "title": "연결 순손실 (DART)", "show_values": True, "highlight": 1, "at": "2019년에도"},
   labels=[lab("2년 연속 적자", "2년", "red")])
sh("table", [33, 34], items=[{"type": "newspaper", "title": "2020년 3월 11일 (보도)", "text": "휴업 검토", "at": "+0.2", "ring_at": "휴업을"},
   {"type": "letter", "title": "해명 공시", "text": "결정된 것 없음", "at": "공시했습니다"}])
sh("chart", [35, 36], board="white", chart={"type": "line", "values": [4052, 3183, 2753, 2758, 2345, 2190], "trend": "down", "show_values": False,
   "title": "2020년 3월 주가 (수정 종가)", "at": "무너집니다"}, labels=[lab("3월 10일 4,052원", "4,052원이었습니다", "cream")])
sh("counter", 37, value={"from": 4052, "to": 2190, "suffix": "원", "at": "2,190원이"}, caption="2020년 3월 23일 종가 (수정 주가)", icon="chart_down")
sh("closeup", 38, who="m1", side="right", set="home", time="night", emotion="shocked", pose="facepalm", labels=[lab("2주 만에 -46%", "46%가", "red", x=600, y=860, size=110)])
sh("wide", [39, 40], set="board", time="night",
   chars=[ch("park", 650, "worried", "arms_crossed", beats=[{"at": "결정합니다", "pose": "point", "emotion": "confident"}]), ch("banker", 1250, "calm", "present")],
   labels=[lab("산업은행 · 수출입은행", "산업은행과", "cream", x=960, y=230)], stamp={"text": "1조 원", "at": "1조", "color": "red"})
sh("icon", [41, 42], icons=[{"name": "coins", "label": "4월 +8천억 원", "at": "4월에"}, {"name": "moneybag", "label": "6월 +1조 2천억 원", "at": "6월에는"}])
sh("counter", 43, value={"from": 0, "to": 3, "suffix": "조 원", "at": "3조"}, caption="긴급운영자금 차입 한도 (DART)", icon="moneybag")
sh("icon", 44, icons=[{"name": "coins", "label": "외화 채권 상환용 포함", "at": "외화"}, {"name": "moneybag", "label": "채권단 지원 3조 6천억 원 (보도)", "at": "3조"}])
sh("closeup", [45, 46], who="banker", side="right", set="office", time="day", emotion="confident", pose="point",
   bubble={"who": "banker", "text": "조건이 있습니다", "at": "조건이"}, labels=[lab("자구안 3조 원+", "자구안을", "gold", x=600, y=860, size=100)])
sh("table", 47, items=[{"type": "receipt", "title": "그룹 자산 매각 (보도)", "rows": [["클럽모우 골프장", "1,850억"]], "text": "팔 수 있는 건 판다", "at": "+0.2"}])
sh("skyline", 48, time="dusk", tag="서울 동대문", labels=[lab("두산타워 8천억 원 (보도)", "8천억", "gold", size=110)])
sh("closeup", 49, who="park", side="left", set="office", time="night", emotion="sad", pose="idle", labels=[lab("가장 아픈 결정", "아픈", "cream", x=1350, y=860, size=100)])
sh("table", 50, hand="park", items=[{"type": "contract", "title": "지분 매각 계약 (2021년 2월)", "text": "두산인프라코어 지분", "at": "+0.2", "stamp": {"text": "8,500억 원", "at": "8,500억에"}}])
sh("crowd", 51, count=20, emotion="worried", set="street", labels=[lab("주주에게 손", "손을", "cream", size=110)])
sh("chart", [52, 53], board="chalk", chart={"type": "bar", "values": [12125, 11478], "labels": ["2020년 12월", "2022년 2월"], "suffix": "억 원", "title": "유상증자 (DART)", "show_values": True, "highlight": 0, "at": "+0.3"})
sh("counter", [54, 55], value={"from": 0, "to": 8384, "suffix": "억 원", "at": "8,384억"}, caption="2020년 연결 순손실 (DART)", icon="chart_down")
sh("closeup", [56, 57], who="m1", side="left", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "몇 년?", "at": "얼마나", "thought": True})
sh("icon", [58, 59], icons=[{"name": "calendar", "top": "상환 완료", "text": "2022.2.28", "label": "약 2년", "at": "2년입니다"}],
   stamp={"text": "다 갚았다", "at": "갚았다고", "color": "green"})
sh("table", [60, 61], items=[{"type": "contract", "title": "상호 변경", "text": "두산중공업 → 두산에너빌리티", "at": "+0.2", "stamp": {"text": "2022년 3월 29일", "at": "2022년"}}])
chap("베팅", "4장")
sh("walk", [62, 63], set="street", time="dusk", chars=[ch("park", 0, "confident", "hold")],
   labels=[lab("다시 판돈", "판돈을", "lime", x=960, y=250), lab("바람이 반대편에서", "바람이", "cream", x=960, y=400)])
sh("icon", [64, 65], icons=[{"name": "laptop", "text": "AI", "label": "인공지능 · 데이터센터", "at": "인공지능입니다"}, {"name": "warning", "label": "미국 전기 부족 (보도)", "at": "모자라기"}])
sh("wide", [66, 67], set="street", time="day", shop="발전소",
   chars=[ch("eng", 700, "neutral", "explain", beats=[{"at": "손님이", "pose": "celebrate", "emotion": "excited"}]), ch("buyer", 1150, "smile", "wave", enter="right")],
   props=[{"icon": "factory", "x": 1550, "y": 690, "s": .55, "at": "발전소가"}], labels=[lab("해외 손님 등장", "손님이", "lime", x=1400, y=260)])
sh("counter", [68, 69], value={"from": 0, "to": 15000, "suffix": "시간", "at": "1만"}, caption="김포 발전소 가스터빈 실증 (보도)", icon="clock",
   compare={"text": "2023년 상업 운전 (보도)", "icon": "trophy", "at": "상업"})
sh("table", 70, hand="park", items=[{"type": "contract", "title": "가스터빈 공급 계약", "text": "380MW급 2기 · 미국 빅테크", "at": "+0.2", "stamp": {"text": "2025년 10월", "at": "2기"}}])
sh("map", 71, places=[{"name": "창원", "x": 1500, "y": 500}, {"name": "미국", "x": 380, "y": 420}], vehicle="ship", at="미국에",
   labels=[lab("한국산 첫 미국 수출", "처음", "gold"), lab("가스터빈 종주국으로", "미국에", "cream")])
sh("chart", [72, 74], board="white", chart={"type": "bar", "values": [2, 3, 7], "labels": ["2025년 10월", "2025년 12월", "2026년 3월"], "suffix": "기", "title": "미국행 가스터빈 계약 (보도)", "show_values": True, "highlight": 2, "at": "+0.3"},
   labels=[lab("미국에만 12기", "12기가", "lime")])
sh("counter", 75, value={"from": 0, "to": 25, "suffix": "기", "at": "25기였다고"}, caption="가스터빈 누적 공급 계약 (2026년 9월 말, 보도)", icon="trophy")
sh("closeup", [76, 77], who="park", side="right", set="office", time="day", emotion="confident", pose="present_left",
   labels=[lab("두 번째 판돈: 원전", "원전입니다", "gold", x=600, y=300), lab("체코 두코바니", "체코", "cream", x=600, y=860)])
sh("table", [78, 79], items=[{"type": "contract", "title": "두코바니 원자로 설비", "text": "약 4조 9천억 원", "at": "+0.2", "stamp": {"text": "DART", "at": "4조"}},
   {"type": "contract", "title": "터빈 발전기", "text": "7,111억 원", "at": "7,111억"}])
sh("counter", 80, value={"from": 0, "to": 233931, "suffix": "억 원", "at": "23조"}, caption="에너빌리티 부문 수주 잔고 2025년 말 (DART)", icon="book")
sh("icon", 81, icons=[{"name": "target", "text": "SMR", "label": "작은 원전", "at": "SMR입니다"}])
sh("table", 82, hand="park", items=[{"type": "contract", "title": "뉴스케일파워 (보도)", "text": "SMR 원자로 상부 모듈 제작", "at": "+0.2", "stamp": {"text": "2026년 10월 29일", "at": "상부"}}])
sh("crowd", [83, 84], count=24, emotion="excited", set="street", labels=[lab("13만 6,400원", "13만", "gold", size=120), lab("2026년 5월 7일", "2026년", "cream")])
sh("counter", [85, 86], value={"from": 0, "to": 62, "suffix": "배", "at": "62배입니다"}, caption="2020년 3월 바닥 → 2026년 5월 7일 (수정 종가)", icon="chart_up",
   compare={"text": "시가총액 약 87조 원 (계산)", "icon": "building", "at": "87조"})
chap("성적표", "5장")
sh("closeup", [87, 88], who="m1", side="right", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "지금은 누가?", "at": "누가", "thought": True})
sh("wide", [89, 90], set="office", era="modern", wall="teal", time="day",
   chars=[ch("park", 700, "confident", "present"), ch("jung", 1200, "calm", "explain")],
   labels=[lab("대표이사 3명", "대표이사는", "gold", x=960, y=230)], lower_third={"name": "정연인", "sub": "대표이사 부회장 · 운영(COO)", "at": "정연인"})
sh("closeup", [91, 92], who="parks", side="right", set="office", time="day", emotion="calm", pose="present_left",
   lower_third={"name": "박상현", "sub": "대표이사 사장 · 재무(CFO)", "at": "박상현"}, labels=[lab("2021년 3월 대표이사", "2021년", "cream", x=600, y=300)])
sh("icon", [93, 94], icons=[{"name": "book", "text": "성적표", "label": "두산에너빌리티 성적표", "at": "성적표를"}, {"name": "moneybag", "label": "시작은 1조 원 차입", "at": "1조"}],
   stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("counter", [95, 96], value={"from": 0, "to": 170579, "suffix": "억 원", "at": "17조"}, caption="2025년 연결 매출 (DART · 자회사 포함)", icon="trophy",
   compare={"text": "영업이익 7,627억 원", "icon": "coins", "at": "7,627억"})
sh("closeup", 97, who="m1", side="left", set="home", time="day", emotion="calm", pose="explain", labels=[lab("두산밥캣 등 자회사 포함", "두산밥캣", "cream", x=1350, y=860, size=80)])
sh("chart", [98, 99], board="white", chart={"type": "bar", "values": [7627, 8090], "labels": ["2025년 한 해", "2026년 1~9월"], "suffix": "억 원", "title": "연결 영업이익 (DART)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("아홉 달 만에 넘었다", "아홉", "lime")])
sh("table", [100, 101], items=[{"type": "receipt", "title": "잘한 결정", "rows": [["2013년~", "1조 원+ (보도)"], ["미국 수출", "12기 (보도)"]], "text": "가스터빈", "at": "+0.2"}],
   stamp={"text": "최고의 결정", "at": "12기가", "color": "green"})
sh("closeup", [102, 103], who="park", side="left", set="office", time="night", emotion="sad", pose="stressed",
   labels=[lab("순손실 8,384억 원", "8,384억", "red", x=1350, y=300, size=80), lab("지분 매각 8,500억 원", "8,500억에", "cream", x=1350, y=860, size=80)],
   stamp={"text": "가장 비싼 대가", "at": "대가는", "color": "red"})
sh("counter", 104, value={"from": 0, "to": 23603, "suffix": "억 원", "at": "2조"}, caption="유상증자 두 번 합계 (DART · 계산)", icon="coins")
sh("chart", [105, 107], board="chalk", chart={"type": "bar", "values": [2190, 136400], "labels": ["2020년 3월 23일", "2026년 5월 7일"], "suffix": "원", "title": "주가 (수정 종가)", "show_values": True, "highlight": 1, "at": "+0.3"})
chap("반전", "6장")
sh("closeup", 108, who="m1", side="left", set="home", time="dusk", emotion="calm", pose="explain")
sh("table", [109, 110], items=[{"type": "newspaper", "title": "2026년 10월 29일 (보도)", "text": "체코 원전 시공 협상 종료", "at": "+0.2", "ring_at": "시공"},
   {"type": "letter", "title": "원자로 설비 계약", "text": "영향 없음 (회사 설명)", "at": "영향이"}])
sh("counter", [111, 112], value={"from": 0, "to": 6.02, "prefix": "-", "suffix": "%", "at": "6.02%"}, caption="11월 6일 코스피 하루 (보도)", icon="chart_down",
   compare={"text": "인공지능 투자 걱정 (보도)", "icon": "warning", "at": "인공지능"})
sh("chart", [113, 114], board="white", chart={"type": "bar", "values": [53100, 45150], "labels": ["11월 4일", "11월 6일"], "suffix": "원", "title": "두산에너빌리티 종가 (네이버)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("이틀 만에", "이틀", "red")])
sh("closeup", [115, 116], who="park", side="right", set="office", time="night", emotion="shocked", pose="facepalm",
   labels=[lab("11월 20일 4만 250원", "4만", "cream", x=600, y=300, size=80)], stamp={"text": "꼭대기 대비 -70.5%", "at": "70.5%", "color": "red"})
sh("chart", [117, 118], board="chalk", chart={"type": "bar", "values": [873725, 257826], "labels": ["2026년 5월 7일", "2026년 11월 20일"], "suffix": "억 원", "title": "시가총액 (종가로 계산)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("60조 원+ 사라짐", "60조", "red")])
sh("counter", 119, value={"from": 0, "to": 91, "prefix": "+", "suffix": "%", "at": "91%"}, caption="3분기 영업이익 증가율 (보도)", icon="chart_up")
sh("versus", 120, colors=["#D8F0D8", "#F6C7B6"], left={"who": "eng", "title": "3분기 영업이익 +91% (보도)", "emotion": "happy", "pose": "celebrate", "at": "+0.2"},
   right={"who": "m1", "title": "주가는 하락", "emotion": "shocked", "pose": "facepalm", "at": "걱정과"},
   labels=[lab("AI 덕분에 / AI 걱정에", "인공지능", "gold", x=960, y=900)])
sh("chart", 121, board="white", chart={"type": "bar", "values": [3, 23.4], "labels": ["2020년 빌린 돈 한도", "2025년 말 일감"], "suffix": "조 원", "title": "빌린 돈 vs 일감 (DART)", "show_values": False, "highlight": 1, "at": "+0.3"},
   labels=[lab("3조 → 23조", "23조", "lime")])
sh("title", 122, text="숫자는 좋아졌는데, 주가는 꼭대기의 3분의 1 아래")
sh("wide", [123, 126], set="office", era="modern", wall="sand", time="day",
   chars=[ch("park", 600, "happy", "wave"), ch("m1", 960, "happy", "wave"), ch("eng", 1320, "smile", "celebrate")],
   labels=[lab("구독 · 좋아요", "구독과", "lime", x=960, y=230, size=130), lab("출처는 설명란", "출처는", "cream", x=960, y=420)],
   polaroid={"at": "출처는", "who": "park", "caption": "3조 빌려 버틴 회사, 일감 23조·주가는 1/3"})

# 빈 화면 방지(2026-11-20 검수): 그래픽 장면의 첫 요소는 장면 시작 직후에 나오게 하고, 나머지만 대사 낱말에 맞춘다
for d in X:
    k = d.get("kind")
    if k == "icon" and d.get("icons"): d["icons"][0]["at"] = "+0.2"
    if k == "table" and d.get("items"): d["items"][0]["at"] = "+0.2"
    if k == "chart" and d.get("chart"): d["chart"]["at"] = "+0.3"
    if k == "counter" and d.get("value"): d["value"]["at"] = "+0.3"

story = {"title": "두산에너빌리티_v2", "mood": "dramatic", "cast": {
    "f1": {"skin": "tan", "outfit": "suit", "color": "#4A3A2E", "shirt": "#F2F2F2", "tie": "#B8862E", "hair": "slick", "hair_col": "#2A2420"},
    "official": {"skin": "light", "outfit": "suit", "color": "#3A3A44", "tie": "#2E2E36", "hair": "short", "hair_col": "#5A5A5A", "moustache": True},
    "exec1": {"skin": "fair", "outfit": "suit", "color": "#1F4E8C", "shirt": "#F2F2F2", "tie": "#C8242C", "hair": "short", "hair_col": "#2A2A2A"},
    "park": {"skin": "light", "outfit": "suit", "color": "#0F3D7A", "shirt": "#F2F2F2", "tie": "#7AB8E8", "hair": "short", "hair_col": "#2A2A2A", "glasses": True},
    "jung": {"skin": "tan", "outfit": "suit", "color": "#5A5A66", "tie": "#2E5A4A", "hair": "bald"},
    "parks": {"skin": "olive", "outfit": "suit", "color": "#2F4A3A", "shirt": "#F2F2F2", "tie": "none", "hair": "slick", "hair_col": "#3A3A3A"},
    "banker": {"skin": "fair", "outfit": "suit", "color": "#6A6A78", "tie": "#B8862E", "hair": "bun", "hair_col": "#2A2420", "glasses": True},
    "eng": {"skin": "tan", "outfit": "tshirt", "color": "#E07A2E", "hair": "short", "hair_col": "#1E1A18", "hat": "cap", "hat_col": "#1E5AA8"},
    "buyer": {"skin": "brown", "outfit": "hoodie", "color": "#3A3A3A", "hair": "curly", "hair_col": "#1E1A18"},
    "m1": {"skin": "fair", "outfit": "sweater", "color": "#5E8C6A", "hair": "curly", "hair_col": "#3A2C22"}},
  "shots": X}
for d in X:
    if d.get("kind") == "walk":
        for c in d.get("chars", []): c.pop("x", None)
json.dump(story, open(os.path.join(P, "story.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(X), "shots")
