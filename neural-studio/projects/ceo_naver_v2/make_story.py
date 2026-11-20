#!/usr/bin/env python3
"""네이버 v2 스토리보드. 문장 번호는 `python3 -m engine sentences <P>` 기준."""
import json, os
P = os.path.dirname(os.path.abspath(__file__)); X = []
def sh(kind, s, **k):
    d = {"kind": kind}
    if s is not None: d["s"] = s if isinstance(s, list) else [s]
    d.update(k); X.append(d)
def lab(text, at, color="lime", **k): return dict(text=text, at=at, color=color, **k)
def ch(id, x, emotion="neutral", pose="idle", **k): return dict(id=id, x=x, emotion=emotion, pose=pose, **k)
def chap(t, n): sh("title", None, text=t, sub=n, hold=1.6)

sh("wide", 0, set="office", era="old", wall="green", time="night", calendar="첫날 1",
   chars=[ch("founder", 520, "confident", "present"), ch("m1", 820, "happy"), ch("m2", 1100, "smile", "wave"), ch("m3", 1380, "nervous", "hold")],
   labels=[lab("7명 · 퇴직금", "일곱", x=960, y=230)])
sh("chart", 1, board="chalk", chart={"type": "bar", "values": [88, 120350], "labels": ["2000", "2025"], "suffix": "억", "title": "매출 (보도·DART)", "show_values": True, "highlight": 1, "at": "첫해"})
sh("counter", 2, value={"from": 0, "to": 1368, "suffix": "배", "at": "1,368배입니다"}, caption="매출 25년 만에 (채널 계산)", icon="chart_up")
sh("chart", 3, board="white", chart={"type": "bar", "values": [74.2, 24.6], "labels": ["2021.7 꼭대기", "2026.11.20"], "suffix": "조", "title": "시가총액", "show_values": True, "highlight": 1, "at": "시가총액은"},
   labels=[lab("3분의 1", "3분의", "red")])
sh("skyline", 4, time="day", labels=[lab("네이버", "네이버입니다", size=170)])
chap("판돈", "1장")
sh("wide", [5, 6], set="office", era="modern", wall="grey", time="day", tag="1997년",
   chars=[ch("founder", 760, "excited", "point", beats=[{"at": "사내벤처", "pose": "celebrate"}]), ch("boss", 1250, "thinking", "arms_crossed")],
   labels=[lab("사내벤처 1호", "사내벤처", "lime", x=1000, y=230)], lower_third={"name": "이해진", "sub": "네이버 창업자", "at": "직원이"})
sh("walk", 7, set="street", time="day", tag="1999년 6월", chars=[{"id": "founder", "emotion": "confident", "pose": "hold"}, {"id": "m1", "emotion": "happy"}, {"id": "m2", "emotion": "smile"}])
sh("icon", [8, 9], icons=[{"name": "coins", "label": "자본금 5억 원", "at": "자본금은"}, {"name": "moneybag", "label": "5개월 만에 100억 투자", "at": "100억"}])
sh("closeup", [10, 11], who="founder", side="left", set="office", time="night", emotion="worried", pose="think",
   bubble={"who": "founder", "text": "?", "at": "실수는", "thought": True}, labels=[lab("가장 비싼 실수?", "실수는", "red", x=1350, y=860, size=110)])
sh("icon", 12, icons=[{"name": "book", "label": "네이버 성적표", "at": "성적표를"}], stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("closeup", [13, 14], who="m1", side="right", set="office", time="night", emotion="tired", pose="stressed",
   bubble={"who": "m1", "text": "돈은 언제 벌지?", "at": "검색은", "thought": True})
sh("icon", 15, tag="2000년", icons=[{"name": "laptop", "text": "검색", "label": "네이버컴", "at": "네이버컴은"}, {"name": "handshake", "label": "합병", "at": "합칩니다"}, {"name": "gift", "label": "한게임", "at": "한게임과"}])
sh("versus", 16, colors=["#D6E4F0", "#F6E0B6"], left={"who": "founder", "title": "검색 회사", "emotion": "smile", "pose": "present", "at": "검색"},
   right={"who": "gamer", "title": "고스톱 게임 회사", "emotion": "excited", "pose": "celebrate", "at": "고스톱"})
sh("chart", 17, board="chalk", chart={"type": "bar", "values": [88, 21474], "labels": ["2000", "2011"], "suffix": "억", "title": "매출 (보도)", "show_values": True, "highlight": 1, "at": "합병"})
sh("crowd", [18, 19], count=18, emotion="thinking", tag="2002년", labels=[lab("지식iN", "지식iN이", size=150)])
sh("icon", 20, icons=[{"name": "book", "label": "도서관 대신", "at": "도서관에"}, {"name": "brain", "label": "손님이 쓰는 책", "at": "손님들이"}])
sh("versus", 21, colors=["#E0E0F0", "#D8F0D8"], left={"who": "rival", "title": "검색 1위 야후", "emotion": "smug", "pose": "arms_crossed", "at": "야후를"},
   right={"who": "founder", "title": "네이버", "emotion": "excited", "pose": "celebrate", "at": "넘어섭니다"})
sh("table", [22, 23], items=[{"type": "newspaper", "title": "경제신문", "text": "NHN 코스닥 상장", "at": "코스닥에", "ring_at": "505"}], labels=[lab("경쟁률 505 대 1", "505", "gold")])
sh("counter", 24, value={"from": 0, "to": 74880, "suffix": "억 원", "at": "시가총액"}, caption="2007년 5월 코스닥 시총 1위 (보도)", icon="trophy")
chap("결정", "2장")
sh("closeup", [25, 26], who="founder", side="right", set="office", time="day", emotion="thinking", pose="think", bubble={"who": "founder", "text": "왜 일본?", "at": "일본에서", "thought": True})
sh("wide", [27, 28], set="street", time="night", shop="도쿄", tag="일본",
   chars=[ch("founder", 900, "sad", "pockets", beats=[{"at": "방향을", "pose": "point", "emotion": "confident"}])], labels=[lab("방향 전환", "방향을", "lime")])
sh("icon", 29, tag="2011년 6월 23일", icons=[{"name": "phone", "label": "메신저 라인", "at": "라인이"}], chars=[ch("founder", 1500, "excited", "present")])
sh("crowd", 30, count=26, emotion="happy", labels=[lab("19개월 만에 1억 명", "1억", "lime")])
sh("map", [31, 32], places=[{"name": "도쿄", "x": 1300, "y": 460}, {"name": "뉴욕", "x": 420, "y": 400}], vehicle="plane", at="뉴욕과",
   labels=[lab("동시 상장 · 약 1조 300억 엔", "시가총액은", "gold")])
sh("versus", [33, 34], colors=["#D8F0D8", "#F6E0B6"], left={"who": "founder", "title": "검색 · 네이버", "emotion": "confident", "pose": "present", "at": "검색은"},
   right={"who": "gamer", "title": "게임 · NHN엔터", "emotion": "smile", "pose": "wave", "at": "게임은"})
sh("walk", 35, set="street", time="dusk", chars=[{"id": "founder", "emotion": "calm", "walk": [900, 200]}, {"id": "gamer", "emotion": "calm", "walk": [1000, 1700]}])
sh("icon", [36, 37], tag="2021년 3월", icons=[{"name": "phone", "label": "라인", "at": "라인은"}, {"name": "handshake", "label": "반반 합작", "at": "반반씩"}, {"name": "laptop", "text": "Yahoo", "label": "일본 야후", "at": "야후와"}])
chap("위기", "3장")
sh("counter", [38, 39], value={"from": 0, "to": 465000, "suffix": "원", "at": "46만"}, caption="2021년 7월 26일 장중 최고 (보도)", icon="trophy",
   compare={"text": "시총 74조 · 코스피 3위", "icon": "chart_up", "at": "시가총액은"})
sh("closeup", 40, who="founder", side="left", set="office", time="dusk", emotion="worried", pose="stressed")
sh("chart", [41, 42], board="white", chart={"type": "line", "values": [465, 400, 330, 260, 200, 158.5], "trend": "down", "show_values": False, "title": "2021.7 → 2022.10 주가", "at": "1년"},
   labels=[lab("약 -66%", "66%가", "red")])
sh("table", [43, 44], items=[{"type": "newspaper", "title": "도쿄 신문", "text": "라인야후 정보 유출", "at": "감염되면서", "ring_at": "51만"}], labels=[lab("약 51만 9천 건", "51만", "red")])
sh("table", [45, 46, 47], items=[{"type": "letter", "title": "일본 총무성 행정지도", "text": "자본 관계 재검토", "at": "총무성은", "stamp": {"text": "압박", "at": "압박으로"}}],
   labels=[lab("2024년 3월 · 4월", "2024년", "gold")])
sh("closeup", 48, who="m2", side="right", set="office", time="night", emotion="nervous", pose="think", bubble={"who": "m2", "text": "팔까?", "at": "결과는", "thought": True})
sh("wide", [49, 50], set="office", era="modern", wall="blue", time="day", chars=[ch("founder", 700, "confident", "arms_crossed"), ch("partner", 1250, "neutral", "arms_crossed")],
   labels=[lab("지분 50 : 50 유지", "반반입니다", "lime", x=960, y=230)])
sh("icon", 51, icons=[{"name": "laptop", "text": "라인야후", "label": "시스템 분리 완료", "at": "분리를"}, {"name": "lock", "label": "2026년 3월", "at": "2026년"}])
chap("성적표", "4장")
sh("closeup", [52, 53], who="founder", side="left", set="office", time="night", emotion="nervous", pose="think", labels=[lab("가장 비싼 실수", "실수는", "red", x=1350, y=860, size=110)])
sh("table", [54, 55], hand="founder", items=[{"type": "contract", "title": "왓패드 인수", "text": "캐나다 웹소설 플랫폼", "at": "왓패드를", "stamp": {"text": "인수", "at": "6,533억"}}], labels=[lab("약 6,533억 원", "6,533억", "gold")])
sh("chart", [56, 57], board="white", chart={"type": "bar", "values": [6330, 2698], "labels": ["손상 전", "손상 후"], "suffix": "억", "title": "왓패드 장부 가치 (보도)", "show_values": True, "trend": "down", "at": "3,632억"},
   labels=[lab("-3,632억 원", "깎아", "red")])
sh("closeup", 58, who="m3", side="right", set="office", time="day", emotion="thinking", pose="explain")
sh("chart", 59, board="chalk", chart={"type": "line", "values": [194, 189, 182, 176.5], "trend": "down", "show_values": False, "title": "포쉬마크 인수 발표일 주가", "at": "포쉬마크"},
   labels=[lab("하루 -8.97%", "8.97%", "red")])
sh("icon", [60, 61], icons=[{"name": "chart_up", "label": "포쉬마크 흑자 전환 (보도)", "at": "흑자로"}, {"name": "book", "label": "웹툰 나스닥 상장", "at": "나스닥에"}])
sh("wide", [62, 63], set="board", time="day", chars=[ch("founder", 600, "neutral", "present")],
   labels=[lab("숫자로만", "숫자로만", "red", x=1250, y=300, size=140), lab("7명 · 5억 원", "일곱", "cream", x=1250, y=520)])
sh("chart", [64, 65], board="chalk", chart={"type": "bar", "values": [88, 120350], "labels": ["2000", "2025"], "suffix": "억", "title": "매출 (보도·DART)", "show_values": True, "highlight": 1, "at": "2000년"},
   labels=[lab("영업이익 2조 2,081억", "영업이익은", "gold")])
sh("table", [66, 67], items=[{"type": "receipt", "title": "잘한 결정", "rows": [["라인 1억 명", "19개월"], ["상장", "뉴욕·도쿄"]], "text": "라인", "at": "잘한"}], stamp={"text": "최고의 결정", "at": "동시", "color": "green"})
sh("table", [68, 69], items=[{"type": "receipt", "title": "비싼 실수", "rows": [["왓패드 인수", "6,533억"], ["손상", "3,632억"]], "text": "-57%", "at": "비싼"}], stamp={"text": "가장 비싼 실수", "at": "깎았습니다", "color": "red"})
sh("counter", [70, 71], value={"from": 0, "to": 65, "prefix": "-", "suffix": "%", "at": "65%"}, caption="2021년 꼭대기 대비 지금 주가 (채널 계산)", icon="chart_down",
   compare={"text": "시총 약 50조 원 감소", "icon": "warning", "at": "50조"})
chap("반전", "5장")
sh("closeup", [72, 73], who="m2", side="right", set="office", time="day", emotion="thinking", pose="think", bubble={"who": "m2", "text": "지금은 누가?", "at": "누가", "thought": True})
sh("wide", [74, 75], set="office", era="modern", wall="cream", time="day", chars=[ch("ceo", 960, "confident", "present")],
   lower_third={"name": "최수연", "sub": "네이버 대표 (2022년~)", "at": "최수연"}, labels=[lab("1981년생 · 2005년 입사", "1981년생으로", "gold")])
sh("walk", 76, set="office", time="day", chars=[{"id": "founder", "emotion": "confident", "pose": "hold"}], labels=[lab("이사회 의장 복귀", "의장으로", "lime")])
sh("chart", [77, 78], board="white", chart={"type": "bar", "values": [4.03, 9.6], "labels": ["창업자", "국민연금"], "suffix": "%", "title": "지분 (DART)", "show_values": True, "highlight": 1, "at": "창업자의"})
sh("title", 79, text="처음 이야기의 끝")
sh("icon", 80, icons=[{"name": "trophy", "label": "매출 12조 · 영업이익 2조", "at": "역대"}], stamp={"text": "역대 최대", "at": "최대", "color": "green"})
sh("chart", [81, 82], board="chalk", chart={"type": "bar", "values": [74.2, 24.6], "labels": ["2021.7", "2026.11.20"], "suffix": "조", "title": "시가총액", "show_values": True, "highlight": 1, "at": "시가총액은"},
   labels=[lab("3분의 1", "3분의", "red")])
sh("versus", [83, 84, 85], colors=["#D8F0D8", "#F6C7B6"], left={"who": "founder", "title": "가장 많이 번 해", "emotion": "excited", "pose": "celebrate", "at": "역대"},
   right={"who": "founder", "title": "꼭대기의 3분의 1", "emotion": "sad", "pose": "shrug", "at": "3분의"})
sh("wide", [86, 89], set="office", era="modern", wall="sand", time="day",
   chars=[ch("founder", 600, "happy", "wave"), ch("m1", 960, "happy", "wave"), ch("m2", 1320, "smile", "celebrate")],
   labels=[lab("구독 · 좋아요", "구독과", "lime", x=960, y=230, size=130), lab("출처는 설명란", "출처는", "cream", x=960, y=420)],
   polaroid={"at": "출처는", "who": "founder", "caption": "가장 많이 번 해, 3분의 1 가격"})

# 빈 화면 방지(2026-11-20 검수): 그래픽 장면의 첫 요소는 장면 시작 직후에 나오게 하고, 나머지만 대사 낱말에 맞춘다
for d in X:
    k = d.get("kind")
    if k == "icon" and d.get("icons"): d["icons"][0]["at"] = "+0.2"
    if k == "table" and d.get("items"): d["items"][0]["at"] = "+0.2"
    if k == "chart" and d.get("chart"): d["chart"]["at"] = "+0.3"
    if k == "counter" and d.get("value"): d["value"]["at"] = "+0.3"

story = {"title": "네이버_v2", "mood": "mystery", "cast": {
    "founder": {"skin": "light", "outfit": "suit", "color": "#2F5D3A", "shirt": "#F2F2F2", "tie": "none", "hair": "short", "hair_col": "#1E1A18", "glasses": True},
    "m1": {"skin": "fair", "outfit": "hoodie", "color": "#5A7FC8", "hair": "curly", "hair_col": "#3A2C22"},
    "m2": {"skin": "tan", "outfit": "sweater", "color": "#C9853A", "hair": "bun", "hair_col": "#2A2420"},
    "m3": {"skin": "light", "outfit": "tshirt", "color": "#8C5A9A", "hair": "slick", "hair_col": "#1E1A18"},
    "boss": {"skin": "light", "outfit": "suit", "color": "#2E2E36", "hair": "bald", "moustache": True},
    "gamer": {"skin": "fair", "outfit": "hoodie", "color": "#D8574A", "hair": "short", "hair_col": "#2A2420", "hat": "cap", "hat_col": "#2A2A3A"},
    "rival": {"skin": "light", "outfit": "suit", "color": "#6A3FA0", "hair": "slick", "hair_col": "#3A2C22"},
    "partner": {"skin": "light", "outfit": "suit", "color": "#4A4A55", "hair": "short", "hair_col": "#5A5A5A", "glasses": True},
    "ceo": {"skin": "fair", "outfit": "suit", "color": "#2F3A55", "hair": "long", "hair_col": "#1E1A18", "tie": "none"}},
  "shots": X}
json.dump(story, open(os.path.join(P, "story.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(X), "shots")
