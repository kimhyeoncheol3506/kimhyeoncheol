#!/usr/bin/env python3
"""시프트업 v2 스토리보드 (CEO 시리즈 28편)."""
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

# 인트로 · 위기부터: 청약 인파 → 공모가 절반 아래 → 그래도 남기던 회사 → 꺾인 실적 (0초부터 그림·글자)
sh("crowd", 0, count=26, emotion="excited", set="street", labels=[lab("공모주 청약에 몰린 사람들", "+0.1", "gold", size=100)])
sh("closeup", 1, who="m1", side="left", set="home", time="night", emotion="shocked", pose="facepalm",
   stamp={"text": "공모가 절반 아래", "at": "절반", "color": "red"})
sh("wide", 2, set="office", era="modern", wall="teal", time="day",
   chars=[ch("kim", 760, "happy", "present", beats=[{"at": "남겼다는", "pose": "celebrate", "emotion": "excited"}])],
   labels=[lab("판 돈의 절반 넘게가 영업이익", "판", "gold", x=1400, y=300, size=85)])
sh("chart", 3, board="chalk", chart={"type": "line", "values": [5, 7, 8.5, 6, 3.5], "trend": "down", "show_values": False, "title": "그 실적마저 꺾이다", "at": "+0.3"})
sh("closeup", [4, 5], who="kim", side="left", set="office", time="day", emotion="calm", pose="hold",
   beats=[{"who": "kim", "at": "시프트업입니다", "pose": "present", "emotion": "confident"}],
   labels=[lab("만들기만 하는 회사", "만들기만", "cream", x=1350, y=700, size=90), lab("시프트업", "시프트업입니다", "lime", x=1350, y=860, size=140)])
sh("closeup", 6, who="m1", side="right", set="home", time="dusk", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "무슨 일이?", "at": "+0.2", "thought": True})
OFF = 2
chap("판돈", "1장")
sh("wide", [5, 6], set="office", era="old", wall="sand", time="night", tag="한 장의 그림",
   chars=[ch("kim", 900, "thinking", "hold", beats=[{"at": "원화가", "pose": "present", "emotion": "smile"}])],
   props=[{"icon": "laptop", "x": 1450, "y": 760, "s": 0.8, "at": "그림에서"}],
   lower_third={"name": "김형태", "sub": "시프트업 대표 · 게임 원화가 출신", "at": "김형태는"})
sh("table", [7, 8], hand="kim", items=[{"type": "letter", "title": "소프트맥스 (DART)", "text": "1999.1 ~ 2005.9 · 팀장", "at": "+0.2"},
   {"type": "letter", "title": "엔씨소프트 (DART)", "text": "2005.10 ~ 2013.12 · 아트 디렉터", "at": "엔씨소프트로"}])
sh("icon", [9, 10], icons=[{"name": "book", "text": "블소", "label": "블레이드 앤 소울 아트 디렉터 (보도)", "at": "+0.2"}, {"name": "book", "text": "18편", "label": "엔씨 이야기는 18편에서", "at": "18편에서"}])
sh("table", 11, hand="kim", items=[{"type": "contract", "title": "주식회사 시프트업 설립", "text": "2013년 12월 2일 (DART)", "at": "+0.2"}],
   stamp={"text": "창업", "at": "세웁니다", "color": "red"})
sh("closeup", 12, who="kim", side="right", set="office", time="day", emotion="confident", pose="hips",
   labels=[lab("13년째 대표", "13년째", "gold", x=600, y=860, size=120)])
sh("icon", 13, icons=[{"name": "phone", "label": "첫 판돈: 모바일 게임", "at": "+0.2"}])
sh("wide", 14, set="street", time="day", shop="앱 마켓", tag="2016년 10월",
   chars=[ch("kim", 760, "excited", "present", beats=[{"at": "데스티니", "pose": "celebrate", "emotion": "happy"}])],
   labels=[lab("첫 작품: 데스티니 차일드", "데스티니", "gold", x=1350, y=260)])
sh("crowd", 15, count=24, emotion="excited", set="street",
   labels=[lab("양대 마켓 매출 1위", "1위를", "gold", size=110), lab("출시 초기 (DART)", "출시", "cream")])
sh("closeup", [16, 17], who="m1", side="right", set="home", time="dusk", emotion="sad", pose="shrug",
   stamp={"text": "2023.9 서비스 종료", "at": "끝냅니다", "color": "red"})
sh("wide", [18, 20], set="home", wall="plum", time="night",
   chars=[ch("m1", 760, "thinking", "think", beats=[{"at": "성적표를", "pose": "point", "emotion": "confident"}])],
   bubble={"who": "m1", "text": "이익률 60%+?", "at": "이익률", "thought": True},
   labels=[lab("그림쟁이 → 이익률 60%+?", "그림쟁이가", "red", x=1350, y=300, size=90)])
chap("결정", "2장")
sh("title", 21, text="답의 절반: 하지 않기로 한 것")
sh("versus", [22, 23], colors=["#D8F0D8", "#D9D9E6"], left={"who": "kim", "title": "개발: 게임을 만든다", "emotion": "confident", "pose": "present", "at": "개발,"},
   right={"who": "tc", "title": "퍼블리싱: 알리고 판다", "emotion": "smile", "pose": "present_left", "at": "퍼블리싱입니다"})
sh("table", 24, hand="kim", items=[{"type": "contract", "title": "사업 기조 (DART)", "text": "개발만 · 파는 일은 최고의 파트너와", "at": "+0.2"}],
   stamp={"text": "개발만", "at": "원칙을", "color": "red"})
sh("wide", [25, 26], set="board", time="day", tag="2020년 9월",
   chars=[ch("kim", 650, "confident", "present"), ch("tc", 1250, "smile", "idle", beats=[{"at": "투자합니다", "pose": "wave", "emotion": "happy"}])],
   lower_third={"name": "텐센트 계열사", "sub": "에이스빌 · 2020년 9월 투자 (DART)", "at": "텐센트"})
sh("map", [27, 28], places=[{"name": "한국", "x": 1450, "y": 470}, {"name": "일본", "x": 1650, "y": 420}, {"name": "미국", "x": 450, "y": 520}, {"name": "유럽", "x": 900, "y": 330}], vehicle="plane", at="+0.3",
   labels=[lab("니케 · 153개 나라 동시 출시", "153개", "gold"), lab("서비스: 텐센트 계열 퍼블리셔", "퍼블리셔가", "cream")])
sh("counter", 29, value={"from": 0, "to": 7, "suffix": "억 달러", "at": "+0.3"}, caption="출시 뒤 약 1년 매출 (보도)", icon="moneybag")
sh("chart", [30, 31], board="white", chart={"type": "bar", "values": [50.9, 17.7, 14.9, 16.4], "labels": ["일본", "북미", "한국", "그 외"], "suffix": "%", "title": "니케 누적 매출 지역 비중 (2024년 5월, DART)", "show_values": True, "highlight": 0, "at": "+0.3"},
   labels=[lab("만든 곳은 한국, 1위는 일본", "정작", "red")])
sh("icon", 32, icons=[{"name": "trophy", "label": "2022년 7월 유니콘 (DART)", "at": "+0.2"}, {"name": "coins", "label": "기업가치 1조 원", "at": "1조"}])
sh("closeup", [33, 34], who="kim", side="left", set="office", time="day", emotion="confident", pose="point",
   bubble={"who": "kim", "text": "콘솔!", "at": "콘솔이었습니다"}, labels=[lab("두 번째 결정", "두", "gold", x=1350, y=860, size=110)])
sh("table", [35, 37], hand="kim", stamp={"text": "계약", "at": "맺습니다", "color": "red"},
   items=[{"type": "contract", "title": "스텔라 블레이드 퍼블리싱 계약", "text": "소니 · 2023년 10월 (DART)", "at": "+0.2"},
          {"type": "receipt", "title": "세컨드 파티 계약 (DART)", "rows": [["판매", "소니 독점"], ["마케팅비", "보장"], ["개발비", "일부 지원"]], "text": "세컨드 파티", "at": "독점"}])
sh("crowd", [38, 39], count=26, emotion="excited", set="street", tag="2024년 4월 26일",
   labels=[lab("스텔라 블레이드 출시", "+0.3", "gold", size=100), lab("8개 나라 PS 스토어 판매 1위 (DART)", "8개", "lime")])
sh("counter", 40, value={"from": 0, "to": 300, "suffix": "만 장", "at": "+0.3"}, caption="누적 판매 (2025년 6월, 보도)", icon="trophy",
   compare={"text": "PC 버전 2025년 6월 출시", "icon": "laptop", "at": "PC"})
sh("title", 41, text="숫자가 따라왔다")
sh("chart", [42, 45], board="chalk", chart={"type": "bar", "values": [1686, 1111, 2241, 1527], "labels": ["2023 매출", "2023 영업이익", "2024 매출", "2024 영업이익"], "suffix": "억", "title": "실적 (DART)", "show_values": True, "highlight": 3, "at": "+0.3"})
chap("위기", "3장")
sh("closeup", [46, 47], who="m1", side="right", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "얼마에?", "at": "얼마에", "thought": True})
sh("table", [48, 49], items=[{"type": "newspaper", "title": "공모주 청약", "text": "2024년 7월 · 유가증권시장", "at": "+0.2"},
   {"type": "receipt", "title": "공모가 (DART)", "rows": [["희망 범위", "47,000~60,000원"], ["확정", "60,000원"]], "text": "맨 위", "at": "공모가는"}],
   stamp={"text": "6만 원", "at": "6만", "color": "red"})
sh("counter", 50, value={"from": 0, "to": 4350, "suffix": "억 원", "at": "+0.3"}, caption="새 주식 725만 주로 모은 돈 (DART)", icon="moneybag")
sh("crowd", [51, 52], count=30, emotion="excited", set="void",
   labels=[lab("일반 청약 69만 건+", "69만", "gold", size=100), lab("약 341대 1 (계산)", "341대", "lime", size=100)])
sh("wide", [53, 54], set="board", time="day", tag="2024년 7월 11일 · 상장 첫날",
   chars=[ch("kim", 760, "happy", "present", beats=[{"at": "8만", "pose": "celebrate", "emotion": "excited"}]), ch("tc", 1300, "smile", "idle")],
   labels=[lab("장중 89,500원", "8만", "gold", x=1350, y=230), lab("종가 71,000원 · 시총 4조 1,198억", "종가는", "lime", x=1150, y=400, size=80)])
sh("chart", [55, 57], board="white", chart={"type": "line", "values": [67000, 56500, 63400, 55700, 48900, 41050, 35500, 32050, 32900, 30750, 27400],
   "labels": ["24.7", "24.9", "24.12", "25.3", "25.6", "25.9", "25.12", "26.3", "26.6", "26.9", "26.11.20"], "suffix": "원", "title": "분기 말 종가 (네이버 증권)", "trend": "down", "show_values": False, "at": "+0.3"},
   labels=[lab("최고 78,300원 (2024.8.13)", "가장", "gold"), lab("2025년 말 35,500원", "마지막", "red")])
sh("counter", [58, 59], value={"from": 60000, "to": 27400, "suffix": "원", "at": "+0.3", "color": "red"}, caption="공모가 → 2026년 11월 20일 종가", icon="chart_down",
   compare={"text": "-54.3%", "icon": "warning", "at": "54.3%"})
sh("versus", 60, colors=["#D8F0D8", "#F6C7B6"], left={"who": "kim", "title": "상장 첫날 시총 4조 1,198억", "emotion": "happy", "pose": "celebrate", "at": "+0.2"},
   right={"who": "kim", "title": "지금 1조 6,095억", "emotion": "worried", "pose": "stressed", "at": "1조"})
sh("closeup", 61, who="m1", side="left", set="home", time="day", emotion="thinking", pose="think",
   labels=[lab("그런데 실적은 좋았다", "실적은", "lime", x=1350, y=860, size=100)])
sh("counter", [62, 64], value={"from": 0, "to": 1814, "suffix": "억 원", "at": "+0.3"}, caption="2025년 영업이익 (DART)", icon="coins",
   compare={"text": "매출 2,945억의 61.6%", "icon": "trophy", "at": "61.6%가"})
sh("chart", [65, 67], board="chalk", chart={"type": "bar", "values": [1653, 1176, 116], "labels": ["니케", "스텔라 블레이드", "기타"], "suffix": "억", "title": "2025년 게임별 매출 (DART)", "show_values": True, "highlight": 0, "at": "+0.3"},
   stamp={"text": "두 게임 96%", "at": "96%를", "color": "red"})
sh("closeup", [68, 69], who="m1", side="right", set="home", time="dusk", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "몇 곳?", "at": "몇", "thought": True})
sh("table", 70, items=[{"type": "receipt", "title": "2024년 1분기 영업수익 (증권신고서)", "rows": [["텐센트 계열 퍼블리셔", "97.6%"], ["그 밖", "2.4%"]], "text": "한 곳", "at": "+0.2", "ring_at": "97.6%가"}])
sh("versus", [71, 73], colors=["#D8F0D8", "#D9D9E6"], left={"who": "tc", "title": "2대 주주 텐센트 계열 34.48% (2025년 말)", "emotion": "smile", "pose": "present", "at": "+0.2"},
   right={"who": "kim", "title": "최대주주 김형태 38.58% (2026년 9월 말)", "emotion": "confident", "pose": "hips", "at": "최대주주"})
sh("icon", [74, 75], icons=[{"name": "coins", "label": "마케팅비·수수료는 퍼블리셔 몫", "at": "+0.2"}, {"name": "warning", "label": "두 게임 · 소수 파트너 의존", "at": "하지만"}])
sh("title", 76, text="그리고 2026년, 숫자가 꺾인다")
sh("chart", [77, 79], board="white", chart={"type": "bar", "values": [2301, 1492], "labels": ["2025년 1~9월", "2026년 1~9월"], "suffix": "억", "title": "매출 (DART)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("-35.1%", "35.1%", "red"), lab("영업이익 703억 · -51.2%", "703억", "red")])
sh("versus", [80, 81], colors=["#F6E0B6", "#F6C7B6"], left={"who": "m1", "title": "니케 353억 · -20.6%", "emotion": "worried", "pose": "stressed", "at": "니케"},
   right={"who": "m1", "title": "스텔라 블레이드 59억 · -78.6%", "emotion": "shocked", "pose": "facepalm", "at": "스텔라"},
   labels=[lab("2026년 3분기 (보도)", "+0.3", "cream", x=960, y=900, size=70)])
sh("counter", [82, 83], value={"from": 0, "to": 255, "prefix": "-", "suffix": "억 원", "at": "+0.3", "color": "red"}, caption="2026년 3분기 순손실 (DART 잠정)", icon="chart_down",
   compare={"text": "영업 밖 손실 537억 (보도)", "icon": "warning", "at": "537억"})
chap("베팅", "4장")
sh("wide", [84, 85], set="board", time="day",
   chars=[ch("kim", 900, "confident", "present", beats=[{"at": "다음", "pose": "point", "emotion": "excited"}])],
   labels=[lab("① 주주에게 돌려주기", "주주에게", "gold", x=1450, y=260), lab("② 다음 게임", "다음", "lime", x=1450, y=420)])
sh("table", [86, 88], hand="kim", stamp={"text": "소각", "at": "없애기로", "color": "red"},
   items=[{"type": "contract", "title": "자기주식 취득 신탁 (DART)", "text": "500억 원 · 2025년 5월", "at": "+0.2"},
          {"type": "receipt", "title": "자기 주식 (DART)", "rows": [["신탁 취득", "957,955주"], ["소각 결정", "32만 주 (2026.11)"]], "text": "주주 환원", "at": "사들인"}])
sh("icon", [89, 90], icons=[{"name": "laptop", "text": "PS5", "label": "2024 PS5", "at": "+0.2"}, {"name": "laptop", "text": "PC", "label": "2025 PC", "at": "기계로"},
   {"name": "phone", "label": "2026.11 스위치 2 (보도)", "at": "닌텐도"}])
sh("closeup", 91, who="kim", side="left", set="office", time="night", emotion="confident", pose="present",
   bubble={"who": "kim", "text": "프로젝트 스피릿", "at": "+0.4"}, labels=[lab("다음 판돈", "판돈", "gold", x=1350, y=860, size=110)])
sh("table", [92, 93], hand="kim", items=[{"type": "contract", "title": "프로젝트 스피릿 계약 (DART)", "text": "개발·퍼블리싱 · 2025년 11월", "at": "+0.2"}],
   stamp={"text": "다시 텐센트 계열", "at": "다시", "color": "red"})
sh("icon", 94, icons=[{"name": "hourglass", "label": "공개 시점 조정 (보도)", "at": "+0.2"}, {"name": "calendar", "top": "연내", "text": "?", "label": "원래 계획: 올해 안 공개", "at": "원래"}])
sh("chart", 95, board="chalk", chart={"type": "bar", "values": [55000, 40000], "labels": ["이전", "실적 발표 뒤"], "suffix": "원", "title": "한 증권사 목표 주가 (보도)", "show_values": True, "highlight": 1, "at": "+0.3"})
chap("성적표", "5장")
sh("icon", [96, 97], icons=[{"name": "book", "text": "성적표", "label": "시프트업 성적표", "at": "+0.2"}, {"name": "laptop", "text": "그림", "label": "시작: 그림 한 장", "at": "그림이었습니다"}],
   stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("counter", [98, 99], value={"from": 0, "to": 2945, "suffix": "억 원", "at": "+0.3"}, caption="2025년 매출 (DART)", icon="chart_up",
   compare={"text": "영업이익 1,814억 · 61.6%", "icon": "trophy", "at": "영업이익은"})
sh("table", [100, 101], items=[{"type": "receipt", "title": "가장 잘한 결정", "rows": [["니케 출시", "2022년 11월"], ["2025년 매출", "1,653억 원"]], "text": "니케", "at": "+0.2"}],
   stamp={"text": "최고의 결정", "at": "1,653억", "color": "green"})
sh("chart", [102, 104], board="white", chart={"type": "bar", "values": [60000, 71000, 27400], "labels": ["공모가", "첫날 종가", "2026.11.20"], "suffix": "원", "title": "주가 (DART · 네이버 증권)", "show_values": True, "highlight": 2, "at": "+0.3"},
   stamp={"text": "-61.4%", "at": "61.4%", "color": "red"})
sh("counter", 105, value={"from": 41198, "to": 16095, "suffix": "억 원", "at": "+0.3", "color": "red"}, caption="시가총액: 상장 첫날 → 2026.11.20 (보도 · 계산)", icon="building")
sh("closeup", 106, who="m1", side="left", set="home", time="night", emotion="worried", pose="stressed",
   stamp={"text": "영업이익 -51.2%", "at": "51.2%", "color": "red"}, labels=[lab("2026년 1~9월", "+0.3", "cream", x=1350, y=860)])
chap("반전", "6장")
sh("closeup", 107, who="kim", side="right", set="office", time="dusk", emotion="calm", pose="explain")
sh("counter", 108, value={"from": 0, "to": 616, "suffix": "원", "at": "+0.3"}, caption="1,000원 팔면 남는 영업이익 (2025년, 계산)", icon="coins")
sh("versus", 109, colors=["#D8F0D8", "#F6C7B6"], left={"who": "kim", "title": "팔지 않기로 한 선택 → 높은 이익률", "emotion": "happy", "pose": "celebrate", "at": "+0.2"},
   right={"who": "kim", "title": "두 게임 · 파트너에 묶인 매출", "emotion": "worried", "pose": "shrug", "at": "묶였습니다"})
sh("wide", [110, 111], set="board", time="dusk",
   chars=[ch("kim", 700, "confident", "hips"), ch("tc", 1250, "smile", "present", beats=[{"at": "계약서에도", "pose": "point", "emotion": "smug"}])],
   labels=[lab("최대주주: 김형태", "대표와", "lime", x=700, y=230, size=80), lab("2대 주주: 텐센트 계열", "텐센트", "gold", x=1250, y=230, size=80)],
   props=[{"icon": "book", "x": 960, "y": 780, "s": 0.6, "at": "계약서에도"}])
sh("title", 112, text="숙제: 다음 히트")
sh("wide", [113, 116], set="office", era="modern", wall="teal", time="day",
   chars=[ch("kim", 600, "happy", "wave"), ch("m1", 960, "happy", "wave"), ch("tc", 1320, "smile", "celebrate")],
   labels=[lab("구독 · 좋아요", "구독과", "lime", x=960, y=230, size=130), lab("출처는 설명란", "출처는", "cream", x=960, y=420)],
   polaroid={"at": "출처는", "who": "kim", "caption": "그림 한 장에서 이익률 61.6%까지, 숙제는 다음 히트"})

# 빈 화면 방지(2026-11-20 검수): 그래픽 장면의 첫 요소는 장면 시작 직후에 나오게 하고, 나머지만 대사 낱말에 맞춘다
for d in X:
    k = d.get("kind")
    if k == "icon" and d.get("icons"): d["icons"][0]["at"] = "+0.2"
    if k == "table" and d.get("items"): d["items"][0]["at"] = "+0.2"
    if k == "chart" and d.get("chart"): d["chart"]["at"] = "+0.3"
    if k == "counter" and d.get("value"): d["value"]["at"] = "+0.3"

story = {"title": "시프트업_v2", "mood": "dramatic", "cast": {
    "kim": {"skin": "light", "outfit": "hoodie", "color": "#3F4A5C", "hair": "short", "hair_col": "#2A2420", "glasses": True},
    "tc": {"skin": "fair", "outfit": "suit", "color": "#1F3A5C", "shirt": "#F2F2F2", "tie": "#2E6FB8", "hair": "slick", "hair_col": "#1E1A18"},
    "m1": {"skin": "fair", "outfit": "sweater", "color": "#5E8C6A", "hair": "curly", "hair_col": "#3A2C22"}},
  "shots": X}
for d in X:
    if d.get("kind") == "walk":
        for c in d.get("chars", []): c.pop("x", None)
json.dump(story, open(os.path.join(P, "story.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(X), "shots")
