#!/usr/bin/env python3
"""에이피알(메디큐브) v2 스토리보드."""
import json, os
P = os.path.dirname(os.path.abspath(__file__)); X = []
def sh(kind, s, **k):
    d = {"kind": kind}
    if s is not None: d["s"] = s if isinstance(s, list) else [s]
    d.update(k); X.append(d)
def lab(text, at, color="lime", **k): return dict(text=text, at=at, color=color, **k)
def ch(id, x, emotion="neutral", pose="idle", **k): return dict(id=id, x=x, emotion=emotion, pose=pose, **k)
def chap(t, n): sh("title", None, text=t, sub=n, hold=1.6)

# 인트로 · 5천만 원 회사가 아모레를 넘다 (첫 장면은 세트·인물·글자가 0프레임부터 보이는 world 샷)
sh("wide", 0, set="street", time="day", shop="K뷰티 매장", tag="2025년 8월",
   chars=[ch("kim", 700, "excited", "present", beats=[{"at": "비싼", "pose": "celebrate", "emotion": "happy"}]), ch("m1", 1250, "shocked", "idle")],
   props=[{"icon": "moneybag", "x": 1500, "y": 760, "s": 0.6, "at": "+0"}],
   labels=[lab("자본금 5천만 원 → 아모레 추월", "+0", "gold", x=1300, y=250, size=85)])
sh("icon", 1, icons=[{"name": "gift", "label": "크림 한 통?", "at": "+0.2"}, {"name": "laptop", "text": "기계", "label": "얼굴에 대는 작은 기계", "at": "기계였습니다"}])
sh("chart", 2, board="chalk", chart={"type": "bar", "values": [464500, 232500], "labels": ["꼭대기 2026.8.31", "2026.11.20"], "suffix": "원", "title": "주가 (종가, 네이버)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("거의 절반", "절반이", "red")])
sh("skyline", 3, time="day", labels=[lab("에이피알 (메디큐브)", "에이피알입니다", size=140)])
chap("판돈", "1장")
sh("wide", 4, set="office", era="modern", wall="sand", time="day", tag="2014년 10월 · 서울", calendar="2014 10",
   chars=[ch("kim", 900, "confident", "present", beats=[{"at": "시작합니다", "pose": "wave", "emotion": "happy"}])])
sh("closeup", [5, 6], who="kim", side="left", set="office", time="day", emotion="confident", pose="hips",
   lower_third={"name": "김병훈", "sub": "창업자 · 대표이사 (공시상 1988년생)", "at": "김병훈"},
   labels=[lab("대표이사 + 최대주주", "최대주주입니다", "gold", x=1350, y=860, size=90)])
sh("counter", 7, value={"from": 0, "to": 5000, "suffix": "만 원", "at": "+0.3"}, caption="설립 자본금 (DART)", icon="moneybag")
sh("table", [8, 9], hand="kim", items=[{"type": "contract", "title": "첫 브랜드", "text": "에이프릴스킨 · 2014년", "at": "+0.2"},
   {"type": "receipt", "title": "설립 첫해 (보도)", "rows": [["매출", "2억 원"]], "text": "첫해", "at": "첫해"}])
sh("icon", [10, 11], icons=[{"name": "shopping", "text": "메디큐브", "label": "2016년 메디큐브", "at": "+0.2"},
   {"name": "shopping", "text": "널디", "label": "패션 브랜드 널디", "at": "널디와"}, {"name": "phone", "label": "셀프 사진관 포토그레이", "at": "포토그레이까지"}])
sh("wide", [12, 13], set="office", era="modern", wall="teal", time="day",
   chars=[ch("kim", 760, "happy", "present", beats=[{"at": "벌인", "pose": "celebrate", "emotion": "excited"}])],
   props=[{"icon": "gift", "x": 1250, "y": 700, "s": 0.5, "at": "+0.2"}, {"icon": "shopping", "x": 1450, "y": 700, "s": 0.5, "at": "옷"}, {"icon": "phone", "x": 1650, "y": 700, "s": 0.5, "at": "사진관까지"}],
   labels=[lab("판을 여러 개", "판을", "gold", x=1450, y=300)])
sh("closeup", [14, 16], who="m1", side="left", set="home", time="night", emotion="thinking", pose="think",
   beats=[{"who": "m1", "at": "성적표를", "pose": "point", "emotion": "confident"}], bubble={"who": "m1", "text": "?", "at": "터진", "thought": True},
   labels=[lab("가장 크게 터진 판?", "터진", "red", x=1350, y=860, size=110)])
chap("결정", "2장")
sh("icon", 17, icons=[{"name": "laptop", "text": "기계", "label": "답은 기계", "at": "+0.2"}])
sh("table", 18, hand="kim", items=[{"type": "contract", "title": "홈 뷰티 디바이스 사업", "text": "메디큐브 에이지알 · 2021년 3월", "at": "+0.2"}],
   stamp={"text": "시작", "at": "시작합니다", "color": "red"})
sh("icon", 19, icons=[{"name": "laptop", "text": "EMS", "label": "첫 제품: 더마 EMS 샷 (회사 발표)", "at": "+0.2"}])
sh("versus", 20, colors=["#F6D6DA", "#D9D9E6"], left={"who": "kim", "title": "화장품", "emotion": "smile", "pose": "present", "at": "+0.2"},
   right={"who": "kim", "title": "전자 기기 · 공장 · 부품", "emotion": "thinking", "pose": "think", "at": "공장도"})
sh("closeup", 21, who="kim", side="right", set="office", time="day", emotion="confident", pose="arms_crossed",
   labels=[lab("남에게 안 맡긴다", "맡기지", "gold", x=600, y=860, size=100)])
sh("icon", 22, icons=[{"name": "calendar", "top": "2022", "text": "9월", "label": "디바이스 연구개발센터", "at": "+0.2"}, {"name": "brain", "label": "기술 직접 개발", "at": "연구개발센터를"}])
sh("wide", 23, set="office", era="modern", wall="grey", time="day", tag="2023년 7월",
   chars=[ch("kim", 760, "confident", "point", beats=[{"at": "준공합니다", "pose": "celebrate", "emotion": "excited"}])],
   props=[{"icon": "factory", "x": 1450, "y": 740, "s": 0.8, "at": "준공합니다"}],
   labels=[lab("에이피알팩토리 1공장", "에이피알팩토리의", "lime", x=1400, y=260)])
sh("closeup", 24, who="kim", side="left", set="office", time="day", emotion="excited", pose="present",
   bubble={"who": "kim", "text": "부스터프로", "icon": "bulb", "at": "부스터프로가"}, labels=[lab("2023년 10월", "+0.3", "cream", x=1350, y=860)])
sh("counter", [25, 26], value={"from": 0, "to": 200, "suffix": "만 대+", "at": "+0.3"}, caption="부스터프로 글로벌 누적 (2025년, 회사 발표)", icon="trophy",
   compare={"text": "에이지알 전체 500만 대+", "icon": "gift", "at": "500만"})
sh("versus", 27, colors=["#D8F0D8", "#F6D6DA"], left={"who": "m1", "title": "기계가 손님을 끌고", "emotion": "excited", "pose": "point", "at": "+0.2"},
   right={"who": "m1", "title": "화장품이 따라 팔린다", "emotion": "happy", "pose": "celebrate", "at": "화장품이"})
sh("chart", [28, 29], board="white", chart={"type": "bar", "values": [27, 71], "labels": ["디바이스", "화장품·뷰티"], "suffix": "%", "title": "2025년 매출 비중 (DART)", "show_values": True, "highlight": 0, "at": "+0.3"})
chap("위기", "3장")
sh("closeup", [30, 31], who="m1", side="right", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "주가는?", "at": "주가는", "thought": True})
sh("table", [32, 33], hand="kim", items=[{"type": "contract", "title": "유가증권시장 상장", "text": "2024년 2월 27일", "at": "+0.2", "stamp": {"text": "상장", "at": "상장합니다"}},
   {"type": "receipt", "title": "공모가 (보도)", "rows": [["공모가", "25만 원"], ["희망 범위 상단", "20만 원"]], "text": "+25%", "at": "공모가는"}])
sh("counter", 34, value={"from": 250000, "to": 317500, "suffix": "원", "at": "+0.3"}, caption="상장 첫날 종가 (보도)", icon="chart_up")
sh("icon", [35, 36], icons=[{"name": "coins", "label": "1주 → 5주 (2024년 10월)", "at": "+0.2"}, {"name": "target", "label": "공모가 = 지금 기준 5만 원", "at": "5만"}])
sh("chart", [37, 39], board="chalk", chart={"type": "bar", "values": [50000, 41000], "labels": ["공모가 (환산)", "2024년 8월 최저"], "suffix": "원", "title": "주가 (DART 월별 주가)", "show_values": True, "highlight": 1, "at": "+0.3"},
   stamp={"text": "-18%", "at": "18%", "color": "red"})
sh("walk", [40, 42], set="street", time="dusk", chars=[ch("kim", 0, "worried", "idle")],
   labels=[lab("2024년 말 종가 5만 원", "5만", "cream", x=600, y=260), lab("열 달 제자리", "제자리였던", "red", x=1350, y=260)])
sh("closeup", [43, 44], who="kim", side="right", set="office", time="night", emotion="worried", pose="stressed",
   labels=[lab("새는 판: 패션", "패션입니다", "red", x=600, y=860, size=110)])
sh("table", 45, items=[{"type": "receipt", "title": "의류 패션 부문 (DART)", "rows": [["2024년 영업손실", "154억 원"]], "text": "적자", "at": "+0.2"}],
   stamp={"text": "-154억", "at": "154억", "color": "red"})
sh("chart", 46, board="white", chart={"type": "bar", "values": [933, 432], "labels": ["2023년", "2025년"], "suffix": "억", "title": "옷·사진관 매출 (DART)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("절반 아래로", "절반", "red")])
sh("icon", 47, icons=[{"name": "warning", "label": "기타 사업 단계적 조정 (보도)", "at": "+0.2"}])
chap("베팅", "4장")
sh("closeup", [48, 49], who="m1", side="left", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "어디?", "at": "어디였을까요", "thought": True})
sh("map", 50, places=[{"name": "한국", "x": 1450, "y": 470}, {"name": "미국", "x": 450, "y": 520}, {"name": "유럽", "x": 900, "y": 330}], vehicle="ship", at="+0.3",
   labels=[lab("답: 바다 건너", "바다", "gold")])
sh("chart", [51, 52], board="chalk", chart={"type": "bar", "values": [39.2, 80.3], "labels": ["2023년", "2025년"], "suffix": "%", "title": "매출 중 수출 비중 (DART 계산)", "show_values": True, "highlight": 1, "at": "+0.3"})
sh("counter", [53, 54], value={"from": 0, "to": 15273, "suffix": "억 원", "at": "+0.3"}, caption="2025년 연결 매출 (DART)", icon="chart_up",
   compare={"text": "1년 전의 두 배 넘게", "icon": "trophy", "at": "두"})
sh("chart", 55, board="white", chart={"type": "bar", "values": [1227, 3655], "labels": ["2024년", "2025년"], "suffix": "억", "title": "영업이익 (DART 연결)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("세 배 가까이", "세", "green")])
sh("crowd", 56, count=22, emotion="excited", set="street", tag="2025년 6월",
   labels=[lab("LG생활건강 시총 추월 (보도)", "넘었다고", "gold", size=95)])
sh("versus", [57, 59], colors=["#F6D6DA", "#D9E6F2"], left={"who": "kim", "title": "에이피알 7조 9,322억", "emotion": "happy", "pose": "celebrate", "at": "7조"},
   right={"who": "amo", "title": "아모레퍼시픽 7조 5,339억", "emotion": "shocked", "pose": "idle", "at": "아모레퍼시픽은"},
   stamp={"text": "추월", "at": "넘어섭니다", "color": "red"})
sh("icon", 60, icons=[{"name": "book", "text": "9편", "label": "아모레퍼시픽 이야기는 9편에서", "at": "+0.2"}])
sh("counter", [61, 62], value={"from": 50000, "to": 231000, "suffix": "원", "at": "+0.3"}, caption="2025년 마지막 거래일 종가 (네이버)", icon="chart_up",
   compare={"text": "1년 사이 4.62배", "icon": "trophy", "at": "4.62배가"})
sh("wide", [63, 64], set="board", time="day", tag="유럽 아마존 직접 진출 (보도)",
   chars=[ch("kim", 760, "confident", "present", beats=[{"at": "유럽", "pose": "point", "emotion": "excited"}]), ch("eu", 1300, "smile", "idle", beats=[{"at": "들어간", "pose": "wave", "emotion": "happy"}])],
   labels=[lab("더 큰 판", "더", "gold", x=1000, y=250)])
sh("map", 65, places=[{"name": "한국", "x": 1450, "y": 470}, {"name": "유럽", "x": 700, "y": 330}], vehicle="plane", at="+0.3",
   labels=[lab("재고 직접 · 비행기로 (보도)", "비행기로", "cream")])
sh("table", [66, 68], items=[{"type": "receipt", "title": "2026년 2분기 (회사 설명)", "rows": [["항공 물류비", "약 300억 원"], ["1년 전 대비", "거의 10배"]], "text": "물류비", "at": "+0.2"}],
   stamp={"text": "10배", "at": "10배입니다", "color": "red"})
sh("closeup", [69, 70], who="kim", side="right", set="office", time="day", emotion="confident", pose="point",
   bubble={"who": "kim", "text": "목표 3조", "icon": "target", "at": "3조"}, labels=[lab("2조 1천억 → 3조 (보도)", "원래", "cream", x=600, y=860, size=85)])
sh("chart", [71, 72], board="white", chart={"type": "bar", "values": [46, 23], "labels": ["북미", "유럽"], "suffix": "%", "title": "2026년 3분기 매출 비중 (회사 발표)", "show_values": True, "highlight": 0, "at": "+0.3"})
sh("counter", [73, 74], value={"from": 0, "to": 21340, "suffix": "억 원", "at": "+0.3"}, caption="2026년 1~9월 매출 (DART)", icon="coins",
   compare={"text": "2025년 1년 치(1조 5,273억)를 넘음", "icon": "trophy", "at": "이미"})
sh("chart", [75, 76], board="chalk", chart={"type": "line", "values": [50000, 231000, 464500], "labels": ["공모가 (환산)", "2025년 말", "2026.8.31"], "suffix": "원", "title": "주가 (종가, 네이버)", "show_values": True, "highlight": 2, "at": "+0.3"},
   labels=[lab("공모가의 9배+", "9배가", "gold")])
sh("closeup", 77, who="m1", side="left", set="home", time="night", emotion="shocked", pose="facepalm",
   stamp={"text": "-17.4%", "at": "17.4%", "color": "red"}, labels=[lab("2026년 10월 13일 하루", "+0.3", "cream", x=1350, y=860, size=85)])
sh("icon", 78, icons=[{"name": "warning", "label": "3분기 이익 기대 아래 전망", "at": "+0.2"}, {"name": "coins", "label": "유럽 물류비 부담 (보도)", "at": "유럽"}])
sh("counter", [79, 80], value={"from": 0, "to": 1606, "suffix": "억 원", "at": "+0.3"}, caption="2026년 3분기 영업이익 (DART 잠정)", icon="chart_down",
   compare={"text": "앞 분기보다 -15.7%", "icon": "warning", "at": "15.7%"})
sh("versus", 81, colors=["#D8F0D8", "#F6C7B6"], left={"who": "kim", "title": "매출: 1년 전의 2배", "emotion": "happy", "pose": "celebrate", "at": "+0.2"},
   right={"who": "kim", "title": "이익: 앞 분기보다 감소", "emotion": "worried", "pose": "stressed", "at": "이익은"})
sh("chart", [82, 83], board="white", chart={"type": "bar", "values": [464500, 232500], "labels": ["2026.8.31", "2026.11.20"], "suffix": "원", "title": "꼭대기 vs 기준일 (종가)", "show_values": True, "highlight": 1, "at": "+0.3"},
   stamp={"text": "-49.9%", "at": "49.9%", "color": "red"})
chap("성적표", "5장")
sh("icon", [84, 85], icons=[{"name": "book", "text": "성적표", "label": "에이피알 성적표", "at": "+0.2"}, {"name": "moneybag", "label": "시작: 자본금 5천만 원", "at": "5천만"}],
   stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("counter", 86, value={"from": 0, "to": 87044, "suffix": "억 원", "at": "+0.3"}, caption="시가총액 (2026.11.20 종가, 계산)", icon="building")
sh("versus", [87, 88], colors=["#F6D6DA", "#D9E6F2"], left={"who": "kim", "title": "에이피알 8조 7,044억", "emotion": "smile", "pose": "hips", "at": "+0.2"},
   right={"who": "amo", "title": "아모레퍼시픽 보통주 8조 1,012억", "emotion": "calm", "pose": "idle", "at": "아모레퍼시픽"})
sh("counter", 89, value={"from": 50000, "to": 232500, "suffix": "원", "at": "+0.3"}, caption="공모가 (환산) → 2026.11.20 종가", icon="chart_up",
   compare={"text": "4.65배", "icon": "trophy", "at": "4.65배가"})
sh("table", [90, 91], items=[{"type": "receipt", "title": "가장 잘한 결정", "rows": [["2021년", "디바이스 시작"], ["부스터프로", "200만 대+"]], "text": "기계", "at": "+0.2"}],
   stamp={"text": "최고의 결정", "at": "200만", "color": "green"})
sh("closeup", [92, 93], who="kim", side="left", set="office", time="night", emotion="sad", pose="facepalm",
   stamp={"text": "-232억", "at": "232억", "color": "red"}, labels=[lab("패션 2년 영업손실 (DART)", "패션입니다", "cream", x=1350, y=860, size=85)])
sh("wide", [94, 95], set="office", era="modern", wall="blue", time="day",
   chars=[ch("kim", 960, "calm", "idle", beats=[{"at": "지분은", "pose": "hips", "emotion": "confident"}])],
   lower_third={"name": "김병훈", "sub": "대표이사 2014년 10월~ · 지분 31.93% (DART)", "at": "+0.3"},
   labels=[lab("대표이사 한 번도 안 바뀜", "바뀌지", "gold", x=960, y=250)])
chap("반전", "6장")
sh("closeup", 96, who="m1", side="left", set="home", time="dusk", emotion="calm", pose="explain")
sh("icon", [97, 98], icons=[{"name": "laptop", "text": "기계", "label": "유명해진 건 기계", "at": "+0.2"}, {"name": "gift", "label": "매출 71%는 화장품·뷰티", "at": "71%는"}])
sh("versus", 99, colors=["#D8F0D8", "#F6C7B6"], left={"who": "kim", "title": "아모레퍼시픽 추월", "emotion": "happy", "pose": "celebrate", "at": "+0.2"},
   right={"who": "m1", "title": "한국 안 매출은 감소", "emotion": "worried", "pose": "shrug", "at": "한국"})
sh("chart", [100, 101], board="chalk", chart={"type": "bar", "values": [3230, 3016], "labels": ["2024년 내수", "2025년 내수"], "suffix": "억", "title": "한국 안 매출 (DART)", "show_values": True, "highlight": 1, "at": "+0.3"},
   stamp={"text": "-6.6%", "at": "6.6%", "color": "red"})
sh("counter", 102, value={"from": 0, "to": 91.6, "suffix": "%", "at": "+0.3"}, caption="2026년 1~9월 수출 비중 (DART 계산)", icon="target")
sh("closeup", 103, who="m1", side="right", set="home", time="dusk", emotion="thinking", pose="shrug",
   labels=[lab("한국 손님 몫 < 10원 중 1원", "한국", "cream", x=600, y=860, size=85)])
sh("title", 104, text="숙제: 많이 파는 것보다 남기는 것")
sh("wide", [105, 108], set="office", era="modern", wall="blue", time="day",
   chars=[ch("kim", 600, "happy", "wave"), ch("m1", 960, "happy", "wave"), ch("eu", 1320, "smile", "celebrate")],
   labels=[lab("구독 · 좋아요", "구독과", "lime", x=960, y=230, size=130), lab("출처는 설명란", "출처는", "cream", x=960, y=420)],
   polaroid={"at": "출처는", "who": "kim", "caption": "5천만 원에서 바다 건너까지, 숙제는 남기는 것"})

# 빈 화면 방지(2026-11-20 검수): 그래픽 장면의 첫 요소는 장면 시작 직후에 나오게 하고, 나머지만 대사 낱말에 맞춘다
for d in X:
    k = d.get("kind")
    if k == "icon" and d.get("icons"): d["icons"][0]["at"] = "+0.2"
    if k == "table" and d.get("items"): d["items"][0]["at"] = "+0.2"
    if k == "chart" and d.get("chart"): d["chart"]["at"] = "+0.3"
    if k == "counter" and d.get("value"): d["value"]["at"] = "+0.3"

story = {"title": "에이피알_v2", "mood": "upbeat", "cast": {
    "kim": {"skin": "fair", "outfit": "sweater", "color": "#3A3A44", "hair": "short", "hair_col": "#2A2420"},
    "amo": {"skin": "light", "outfit": "suit", "color": "#2E4A8C", "shirt": "#F2F2F2", "tie": "#5A6A8C", "hair": "slick", "hair_col": "#3A3230"},
    "eu": {"skin": "fair", "outfit": "tshirt", "color": "#4A7AB8", "hair": "long", "hair_col": "#C8A060"},
    "m1": {"skin": "fair", "outfit": "hoodie", "color": "#5E8C6A", "hair": "curly", "hair_col": "#3A2C22"}},
  "shots": X}
for d in X:
    if d.get("kind") == "walk":
        for c in d.get("chars", []): c.pop("x", None)
json.dump(story, open(os.path.join(P, "story.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(X), "shots")
