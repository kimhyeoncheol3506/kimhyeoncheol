#!/usr/bin/env python3
"""농심 v2 스토리보드."""
import json, os
P = os.path.dirname(os.path.abspath(__file__)); X = []
def sh(kind, s, **k):
    d = {"kind": kind}
    if s is not None: d["s"] = s if isinstance(s, list) else [s]
    d.update(k); X.append(d)
def lab(text, at, color="lime", **k): return dict(text=text, at=at, color=color, **k)
def ch(id, x, emotion="neutral", pose="idle", **k): return dict(id=id, x=x, emotion=emotion, pose=pose, **k)
def chap(t, n): sh("title", None, text=t, sub=n, hold=1.6)

sh("closeup", [0, 1], who="elder", side="right", set="home", time="night", emotion="smug", pose="arms_crossed",
   bubble={"who": "elder", "text": "밥 대신 라면?", "at": "밥"})
sh("wide", 2, set="office", era="old", wall="sand", time="day", calendar="1965 9",
   chars=[ch("founder", 900, "confident", "present", beats=[{"at": "라면", "pose": "celebrate", "emotion": "excited"}])],
   props=[{"icon": "factory", "x": 1450, "y": 690, "s": .6, "at": "공장을"}], labels=[lab("자본금 500만 원", "500만", x=600, y=250)])
sh("counter", 3, value={"from": 0, "to": 15400, "suffix": "억 원", "at": "1조"}, caption="2025년 신라면 한 브랜드 매출 (보도)", icon="shopping")
sh("closeup", 4, who="founder", side="left", set="office", time="dusk", emotion="worried", pose="think", bubble={"who": "founder", "text": "?", "at": "웃지", "thought": True})
sh("skyline", 5, time="day", labels=[lab("농심", "농심입니다", size=180)])
chap("판돈", "1장")
sh("wide", [6, 7], set="office", era="old", wall="brick", time="day", tag="1965년 · 서울 신대방동",
   chars=[ch("founder", 760, "excited", "push")], props=[{"icon": "factory", "x": 1350, "y": 690, "s": .7, "at": "기계를"}],
   lower_third={"name": "신춘호", "sub": "농심 창업주", "at": "신춘호는"}, labels=[lab("롯데공업", "롯데공업이었습니다", "gold", x=1350, y=260)])
sh("versus", [8, 9], colors=["#F6C7B6", "#D8F0D8"], left={"who": "elder", "title": "형 · 롯데", "emotion": "angry", "pose": "point", "at": "형은"},
   right={"who": "founder", "title": "동생 · 라면", "emotion": "confident", "pose": "hold", "at": "동생의"})
sh("closeup", [10, 11], who="founder", side="left", set="office", time="night", emotion="worried", pose="think",
   bubble={"who": "founder", "text": "?", "at": "실수는", "thought": True}, labels=[lab("가장 비싼 실수?", "실수는", "red", x=1350, y=860, size=110)])
sh("icon", 12, icons=[{"name": "book", "label": "농심 성적표", "at": "성적표를"}], stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("icon", [13, 14], tag="1971년", icons=[{"name": "shopping", "text": "새우깡", "label": "우리나라 첫 스낵", "at": "새우깡을"}])
sh("icon", 15, icons=[{"name": "car", "label": "밀가루 트럭 80여 대", "at": "트럭"}], labels=[lab("4.5톤 × 80여 대", "4.5톤", "gold")])
sh("chart", [16, 17], board="chalk", chart={"type": "bar", "values": [20.6, 425], "labels": ["첫해", "이듬해"], "suffix": "만 박스", "title": "새우깡 생산 (보도)", "show_values": True, "highlight": 1, "at": "첫해"},
   labels=[lab("약 20배", "20배가", "red")])
sh("closeup", [18, 19], who="kid", side="right", set="home", time="day", emotion="happy", pose="wave", bubble={"who": "kid", "text": "아리깡!", "at": "아리랑을"})
sh("table", [20, 21], items=[{"type": "contract", "title": "사명 변경", "text": "롯데공업 → 농심", "at": "농심으로", "stamp": {"text": "농심", "at": "갈라섭니다"}}], labels=[lab("1978년 3월", "1978년", "gold")])
chap("결정", "2장")
sh("closeup", [22, 23], who="m1", side="left", set="office", time="day", emotion="thinking", pose="think", bubble={"who": "m1", "text": "첫 1위 라면은?", "at": "처음", "thought": True})
sh("chart", [24, 25], board="white", chart={"type": "bar", "values": [40.4, 39.6], "labels": ["농심", "삼양"], "suffix": "%", "title": "1985년 3월 라면 점유율 (보도)", "show_values": True, "highlight": 0, "at": "1985년"},
   labels=[lab("신라면 아님", "아닙니다", "red")])
sh("icon", 26, icons=[{"name": "shopping", "text": "너구리", "label": "1982", "at": "너구리"}, {"name": "shopping", "text": "안성탕면", "label": "1983", "at": "안성탕면"}, {"name": "shopping", "text": "짜파게티", "label": "1984", "at": "짜파게티였습니다"}])
sh("table", [27, 28, 29], hand="founder", items=[{"type": "contract", "title": "신라면 출시", "text": "국내 첫 매운맛 라면", "at": "신라면은", "stamp": {"text": "매울 신", "at": "매울"}}], labels=[lab("1986년 10월", "1986년", "gold")])
sh("list", 30, number=1, text="1991년부터 브랜드 1위", who="founder", emotion="excited", badge="gold")
sh("counter", 31, value={"from": 0, "to": 425, "suffix": "억 개", "at": "누적"}, caption="신라면 누적 판매 (2026년 초, 보도)", icon="shopping", compare={"text": "누적 매출 20조 원", "icon": "moneybag", "at": "20조"})
sh("chart", 32, board="chalk", chart={"type": "bar", "values": [55.7, 23.4, 11.3, 9.6], "labels": ["농심", "오뚜기", "삼양", "팔도"], "suffix": "%", "title": "2022년 3분기 회사 점유율 (보도)", "show_values": True, "highlight": 0, "at": "55.7%로"})
sh("map", [33, 34, 35], places=[{"name": "한국", "x": 1450, "y": 470}, {"name": "로스앤젤레스", "x": 440, "y": 430}], vehicle="ship", at="로스앤젤레스에",
   labels=[lab("2005 1공장 · 2022 2공장", "2005년", "gold")])
sh("chart", 36, board="white", chart={"type": "bar", "values": [49.0, 23.3, 17.9], "labels": ["도요스이산", "농심", "닛신"], "suffix": "%", "title": "2020년 미국 라면 점유율 (보도)", "show_values": True, "highlight": 1, "at": "23.3%로"})
sh("icon", 37, icons=[{"name": "shopping", "text": "마트", "label": "진열대 자리 대신", "at": "진열대에서"}, {"name": "factory", "label": "옆에 부엌", "at": "부엌을"}])
sh("crowd", [38, 39], count=20, emotion="excited", tag="2020년 2월", labels=[lab("짜파구리", "짜파구리가", "lime", size=150)])
sh("icon", 40, icons=[{"name": "laptop", "text": "11개 언어", "label": "조리법 영상", "at": "조리법"}])
sh("counter", 41, value={"from": 0, "to": 150, "suffix": "만 달러", "at": "150만"}, caption="2020년 2월 짜파게티 해외 매출 · 월 최대 (보도)", icon="chart_up")
chap("위기", "3장")
sh("closeup", [42, 43], who="founder2", side="left", set="office", time="night", emotion="nervous", pose="stressed")
sh("chart", [44, 45], board="white", chart={"type": "line", "values": [5, 4, 2, 0.5, -0.3], "trend": "down", "show_values": False, "title": "국내 사업 영업이익 (별도)", "at": "24년"},
   stamp={"text": "24년 만의 적자", "at": "적자는", "color": "red"}, labels=[lab("약 -30억 원", "30억", "red")])
sh("icon", 46, icons=[{"name": "money", "label": "밀가루 값 ↑", "at": "밀가루와"}, {"name": "warning", "label": "기름값 ↑", "at": "기름값이"}])
sh("versus", [47, 48], colors=["#F6C7B6", "#E0E0F0"], left={"who": "founder2", "title": "라면 1등", "emotion": "smug", "pose": "present", "at": "1등"},
   right={"who": "founder2", "title": "한국에서 손해", "emotion": "sad", "pose": "facepalm", "at": "손해를"}, labels=[lab("영업이익 -75%", "75%", "red", x=960, y=900)])
sh("map", [49, 50], places=[{"name": "한국", "x": 1450, "y": 470}, {"name": "미국", "x": 440, "y": 430}], vehicle="plane", at="바다",
   labels=[lab("미국 법인 5,243억 원", "5,243억", "lime")])
sh("counter", 51, value={"from": 0, "to": 37, "suffix": "%", "at": "37%를"}, caption="해외 매출 비중 · 회사 발표 (보도)", icon="chart_up")
sh("wide", [52, 53], set="street", time="day", shop="녹산 공장", tag="2026년 10월 · 부산",
   chars=[ch("founder2", 900, "excited", "present")], props=[{"icon": "factory", "x": 1450, "y": 690, "s": .7, "at": "수출"}], labels=[lab("투자 2,043억 원", "2,043억", "gold")])
chap("성적표", "4장")
sh("wide", [54, 55], set="board", time="day", chars=[ch("founder", 600, "neutral", "present")],
   labels=[lab("숫자로만", "숫자로만", "red", x=1250, y=300, size=140), lab("자본금 500만 원", "500만", "cream", x=1250, y=520)])
sh("counter", [56, 57], value={"from": 0, "to": 35143, "suffix": "억 원", "at": "매출은"}, caption="2025년 매출 · 사상 최대 (DART)", icon="trophy", compare={"text": "영업이익 1,839억 원", "icon": "coins", "at": "영업이익은"})
sh("table", [58, 59, 60, 61], items=[{"type": "receipt", "title": "잘한 결정", "rows": [["신라면 2025", "1조5,400억"], ["해외", "66%"]], "text": "전체의 약 44%", "at": "잘한"}], stamp={"text": "최고의 결정", "at": "44%가", "color": "green"})
sh("table", [62, 63], items=[{"type": "receipt", "title": "비싼 실수", "rows": [["2022년 2분기", "국내 적자"], ["영업이익", "-75%"]], "text": "24년 만", "at": "비싼"}], stamp={"text": "가장 비싼 실수", "at": "적자를", "color": "red"})
sh("chart", [64, 65], board="chalk", chart={"type": "bar", "values": [575000, 341000], "labels": ["2024.6.17", "2026.11.20"], "suffix": "원", "title": "농심 주가", "show_values": True, "highlight": 1, "at": "2024년"},
   labels=[lab("약 -41%", "41%", "red")])
chap("반전", "5장")
sh("closeup", [66, 67], who="m1", side="right", set="office", time="day", emotion="thinking", pose="think", bubble={"who": "m1", "text": "지금은 누가?", "at": "누가", "thought": True})
sh("wide", [68, 69, 70], set="office", era="modern", wall="green", time="day", chars=[ch("founder2", 960, "calm", "present")],
   lower_third={"name": "신동원", "sub": "농심 회장 (대표이사 아님)", "at": "신동원"})
sh("wide", 71, set="office", era="modern", wall="blue", time="day", chars=[ch("ceo", 960, "confident", "present")],
   lower_third={"name": "조용철", "sub": "농심 대표이사 (2026년 3월~)", "at": "조용철"})
sh("title", [72, 73, 74], text="40년 넘게 라면 1위")
sh("chart", [75, 76], board="white", chart={"type": "bar", "values": [2.07, 9.2], "labels": ["농심 (11/20)", "삼양식품 (이달 보도)"], "suffix": "조", "title": "시가총액", "show_values": True, "highlight": 1, "at": "삼양식품의"},
   labels=[lab("4배 넘게", "4배가", "red")])
sh("versus", [77, 78], colors=["#D8F0D8", "#F6E0B6"], left={"who": "founder2", "title": "더 많이 판다", "emotion": "smug", "pose": "present", "at": "라면은"},
   right={"who": "rival", "title": "더 빨리 큰다", "emotion": "excited", "pose": "celebrate", "at": "빨리"})
sh("crowd", [79, 80, 81], count=24, emotion="happy", set="street", labels=[lab("세계가 답했다", "세계가", "lime", size=140)])
sh("wide", [82, 85], set="office", era="modern", wall="sand", time="day",
   chars=[ch("founder2", 600, "happy", "wave"), ch("m1", 960, "happy", "wave"), ch("kid", 1320, "smile", "celebrate")],
   labels=[lab("구독 · 좋아요", "구독과", "lime", x=960, y=230, size=130), lab("출처는 설명란", "출처는", "cream", x=960, y=420)],
   polaroid={"at": "출처는", "who": "founder2", "caption": "1위의 다음 질문: 누가 세계에서 더 파나"})

# 빈 화면 방지(2026-11-20 검수): 그래픽 장면의 첫 요소는 장면 시작 직후에 나오게 하고, 나머지만 대사 낱말에 맞춘다
for d in X:
    k = d.get("kind")
    if k == "icon" and d.get("icons"): d["icons"][0]["at"] = "+0.2"
    if k == "table" and d.get("items"): d["items"][0]["at"] = "+0.2"
    if k == "chart" and d.get("chart"): d["chart"]["at"] = "+0.3"
    if k == "counter" and d.get("value"): d["value"]["at"] = "+0.3"

story = {"title": "농심_v2", "mood": "upbeat", "cast": {
    "founder": {"skin": "tan", "outfit": "suit", "color": "#7A3B2E", "shirt": "#F2F2F2", "tie": "#C8242C", "hair": "short", "hair_col": "#2A2420"},
    "elder": {"skin": "light", "outfit": "suit", "color": "#3A3A44", "hair": "slick", "hair_col": "#5A5A5A", "moustache": True},
    "founder2": {"skin": "light", "outfit": "suit", "color": "#8C2E2E", "shirt": "#F2F2F2", "tie": "#2E2E36", "hair": "short", "hair_col": "#3A3A3A", "glasses": True},
    "kid": {"skin": "fair", "outfit": "dress", "color": "#F28C8C", "hair": "bun", "hair_col": "#2A2420"},
    "m1": {"skin": "fair", "outfit": "sweater", "color": "#5E8C6A", "hair": "curly", "hair_col": "#3A2C22"},
    "rival": {"skin": "light", "outfit": "suit", "color": "#E07A2E", "hair": "short", "hair_col": "#1E1A18"},
    "ceo": {"skin": "light", "outfit": "suit", "color": "#2F3A55", "hair": "short", "hair_col": "#7A7A7A", "tie": "#2E5A8C"}},
  "shots": X}
for d in X:
    for c in d.get("chars", []):
        if c.get("id") == "kid": c["s"] = .8
json.dump(story, open(os.path.join(P, "story.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(X), "shots")
