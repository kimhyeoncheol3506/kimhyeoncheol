#!/usr/bin/env python3
"""크래프톤 v2 스토리보드."""
import json, os
P = os.path.dirname(os.path.abspath(__file__)); X = []
def sh(kind, s, **k):
    d = {"kind": kind}
    if s is not None: d["s"] = s if isinstance(s, list) else [s]
    d.update(k); X.append(d)
def lab(text, at, color="lime", **k): return dict(text=text, at=at, color=color, **k)
def ch(id, x, emotion="neutral", pose="idle", **k): return dict(id=id, x=x, emotion=emotion, pose=pose, **k)
def chap(t, n): sh("title", None, text=t, sub=n, hold=1.6)

# 인트로
sh("chart", 0, board="chalk", chart={"type": "bar", "values": [1.89, 3.33], "labels": ["2021년 (상장)", "2025년"], "suffix": "조", "title": "크래프톤 매출 (연결)", "show_values": True, "highlight": 1, "at": "매출이"},
   labels=[lab("+76%", "76%", "lime")])
sh("closeup", 1, who="inv", side="right", set="office", time="day", emotion="shocked", pose="facepalm",
   labels=[lab("주가 공모가 -59%", "59%", "red", size=110)])
sh("crowd", 2, count=30, emotion="nervous", labels=[lab("100명 중 1명", "1명만", "gold", size=140), lab("매출 3조 원", "3조", "lime")])
sh("skyline", 3, time="day", labels=[lab("크래프톤", "크래프톤입니다", size=180)])
chap("판돈", "1장")
sh("wide", 4, set="office", era="old", wall="teal", time="day", tag="2007년 3월 · 블루홀스튜디오",
   chars=[ch("founder", 820, "confident", "present", beats=[{"at": "세웁니다", "pose": "celebrate", "emotion": "excited"}])],
   props=[{"icon": "moneybag", "x": 1400, "y": 700, "s": .6, "at": "사재를"}],
   lower_third={"name": "장병규", "sub": "크래프톤 창업자 · 이사회 의장", "at": "장병규는"})
sh("table", 5, hand="founder", items=[{"type": "letter", "title": "1996년", "text": "네오위즈 공동 창업", "at": "네오위즈를"},
   {"type": "contract", "title": "첫눈 매각", "text": "네이버 · 350억 원", "at": "첫눈을", "stamp": {"text": "매각", "at": "350억"}}])
sh("closeup", 6, who="founder", side="left", set="office", time="dusk", emotion="smug", pose="hips",
   labels=[lab("세 번째 판돈 = 게임", "세", "gold", size=120)])
sh("counter", [7, 8], value={"from": 0, "to": 82, "prefix": "-", "suffix": "억 원", "at": "82억"}, caption="2008년 영업손실 (보도)", icon="chart_down")
sh("icon", [9, 10], tag="2011년", icons=[{"name": "laptop", "text": "테라", "label": "2011년 대작 온라인게임", "at": "테라를"},
   {"name": "chart_down", "label": "2014년 순손실 16억 원", "at": "16억"}])
sh("closeup", 11, who="founder", side="right", set="office", time="night", emotion="worried", pose="think",
   bubble={"who": "founder", "text": "적자…", "at": "적자를", "thought": True})
sh("closeup", [12, 13, 14], who="m1", side="left", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "가장 비싼 실수?", "at": "실수는", "thought": True}, labels=[lab("숫자로만 성적표", "성적표를", "red", x=1350, y=860, size=100)])
sh("counter", [15, 16], value={"from": 0, "to": 514, "suffix": "억 원", "at": "514억"}, caption="2016년 블루홀 매출 · 테라 중심 (보도)", icon="coins",
   compare={"text": "창업 10년째, 아직 대박 없음", "icon": "hourglass", "at": "10년째"})
chap("결정", "2장")
sh("wide", [17, 18], set="office", era="modern", wall="grey", time="night",
   chars=[ch("dev", 560, "thinking", "think"), ch("ceo", 960, "confident", "explain"), ch("dev2", 1360, "excited", "hold")],
   labels=[lab("약 30명 팀", "30명짜리", "gold", x=960, y=230, size=130)],
   lower_third={"name": "김창한", "sub": "배틀그라운드 제작 책임자 (현 대표이사)", "at": "김창한입니다"})
sh("crowd", [19, 20, 21], count=30, emotion="nervous",
   labels=[lab("100명 → 1명", "마지막", "red", size=140), lab("배틀그라운드", "배틀그라운드였습니다", "lime", size=130)])
sh("icon", 22, tag="2017년 3월", icons=[{"name": "laptop", "text": "스팀", "label": "세계 최대 게임 장터", "at": "스팀에"},
   {"name": "hourglass", "label": "완성 전에 미리 판매", "at": "미리"}])
sh("counter", 23, value={"from": 0, "to": 1100, "suffix": "만 달러", "at": "1,100만"}, caption="출시 첫 3일 매출 · 약 123억 원 (보도)", icon="money")
sh("chart", [24, 25], board="white", chart={"type": "bar", "values": [100, 200], "labels": ["16일", "39일"], "suffix": "만 장", "title": "배틀그라운드 판매 (보도)", "show_values": True, "highlight": 0, "at": "16일"},
   labels=[lab("미완성인데", "아직", "red")])
sh("counter", [26, 27], value={"from": 514, "to": 6665, "suffix": "억 원", "at": "6,665억"}, caption="2017년 블루홀 매출 (보도)", icon="trophy",
   compare={"text": "영업이익 2,517억 원", "icon": "coins", "at": "영업이익은"}, labels=[lab("1년 전 514억 원", "1년", "cream", x=1450, y=250)])
sh("crowd", [28, 29], count=28, emotion="excited", set="street",
   labels=[lab("동시접속 325만 명", "325만", "lime", size=120), lab("누적 7,500만 장", "7,500만", "gold", size=120)])
sh("skyline", 30, time="dusk", tag="2018년 11월", labels=[lab("블루홀 → 크래프톤", "크래프톤이라는", "gold", size=130)])
sh("table", [31, 32], hand="founder", items=[{"type": "contract", "title": "대표이사 선임", "text": "김창한 · 2020년 6월", "at": "김창한이", "stamp": {"text": "취임", "at": "오릅니다"}}],
   labels=[lab("개발자 출신 첫 대표", "처음이었습니다", "lime")])
sh("counter", [33, 34], value={"from": 0, "to": 18863, "suffix": "억 원", "at": "1조"}, caption="2021년 매출 (보도)", icon="chart_up",
   compare={"text": "해외 매출 94%", "icon": "phone", "at": "94%를"})
sh("closeup", [35, 36], who="inv", side="left", set="office", time="day", emotion="thinking", pose="think",
   bubble={"who": "inv", "text": "그런데 주가는?", "at": "주식시장에서는", "thought": True})
chap("위기", "3장")
sh("wide", [37, 38], set="street", time="day", shop="코스피", tag="2021년 8월 10일 · 상장",
   chars=[ch("founder", 700, "happy", "wave"), ch("ceo", 1150, "excited", "celebrate")],
   labels=[lab("공모가 49만 8천 원", "공모가는", "gold", x=960, y=250, size=120)])
sh("counter", 39, value={"from": 0, "to": 40398, "suffix": "억 원", "at": "4조"}, caption="공모 규모 (보도)", icon="moneybag",
   compare={"text": "공모가 기준 회사 값 약 24조 원", "icon": "building", "at": "24조"})
sh("table", [40, 41], items=[{"type": "letter", "title": "증권신고서 정정", "text": "희망가 꼭대기 55만 7천 → 49만 8천 원", "at": "꼭대기는", "stamp": {"text": "정정", "at": "고치라고"}}])
sh("chart", [42, 43], board="white", chart={"type": "bar", "values": [498000, 448500, 454000], "labels": ["공모가", "첫 거래", "첫날 종가"], "suffix": "원", "title": "상장 첫날 (보도)", "show_values": True, "highlight": 2, "at": "첫"},
   labels=[lab("약 -10%", "10%", "red")])
sh("closeup", [44, 45], who="ceo", side="left", set="office", time="day", emotion="confident", pose="present",
   beats=[{"who": "ceo", "at": "무료로", "pose": "celebrate", "emotion": "excited"}], bubble={"who": "ceo", "text": "이제 무료!", "at": "무료로"}, tag="2022년 1월")
sh("counter", 46, value={"from": 0, "to": 486, "suffix": "%", "prefix": "+", "at": "486%"}, caption="무료화 뒤 새 이용자 증가 (회사 분석, 보도)", icon="chart_up")
sh("versus", 47, colors=["#E0E0F0", "#D8F0D8"], left={"who": "dev", "title": "입장료 받기", "emotion": "neutral", "pose": "hold", "at": "입장료를"},
   right={"who": "dev2", "title": "안에서 팔기", "emotion": "happy", "pose": "present", "at": "간식과"})
sh("chart", 48, board="chalk", chart={"type": "bar", "values": [3.88, 7.14], "labels": ["무료화 전", "무료화 뒤"], "suffix": "%", "title": "피시방 점유율 (보도)", "show_values": True, "highlight": 1, "at": "3.88%에서"})
sh("table", [49, 50, 51], tag="2022년 12월", items=[{"type": "contract", "title": "칼리스토 프로토콜", "text": "우주 공포 게임", "at": "칼리스토", "stamp": {"text": "출시", "at": "프로토콜입니다"}},
   {"type": "receipt", "title": "개발비", "rows": [["추산", "약 2,000억 원"]], "text": "(보도)", "at": "개발비는"}])
sh("chart", [52, 53], board="white", chart={"type": "bar", "values": [200, 300, 500], "labels": ["판매 (추정)", "전망 하단", "전망 상단"], "suffix": "만 장", "title": "칼리스토 프로토콜 판매 (보도)", "show_values": True, "highlight": 0, "at": "판매는"})
sh("closeup", 54, who="ceo", side="right", set="office", time="dusk", emotion="worried", pose="think", tag="2023년 3월 · 주주총회",
   labels=[lab("기대에 못 미쳤다", "인정했습니다", "red", size=110)])
sh("chart", [55, 56], board="chalk", chart={"type": "line", "values": [498000, 567000, 146500], "labels": ["공모가", "최고 (2021.11)", "최저 (2023.10)"], "suffix": "원", "title": "크래프톤 주가 (종가)", "show_values": True, "trend": "down", "at": "주가는"},
   stamp={"text": "-70%", "at": "70%", "color": "red"})
chap("성적표", "4장")
sh("counter", [57, 58], value={"from": 0, "to": 11825, "suffix": "억 원", "at": "1조"}, caption="2024년 영업이익 (DART)", icon="trophy",
   compare={"text": "매출 2조 7,098억 원", "icon": "coins", "at": "영업이익은"})
sh("list", [59, 60], number=1, text="영업이익 첫 1조 원", who="ceo", emotion="excited", badge="gold")
sh("icon", [61, 62], tag="2025년 3월", icons=[{"name": "house", "text": "인조이", "label": "생활 게임", "at": "인조이를"},
   {"name": "clock", "label": "7일 만에 100만 장", "at": "7일"}])
sh("chart", 63, board="white", chart={"type": "bar", "values": [7, 16], "labels": ["인조이", "배틀그라운드"], "suffix": "일", "title": "100만 장까지 걸린 날 (보도)", "show_values": True, "highlight": 0, "at": "16일보다"})
sh("map", [64, 65], places=[{"name": "한국", "x": 900, "y": 520}, {"name": "일본 · 에이디케이", "x": 1400, "y": 470}], vehicle="plane", at="일본",
   labels=[lab("750억 엔 = 7,103억 원", "7,103억", "gold")])
sh("table", [66, 67], hand="ceo", items=[{"type": "contract", "title": "에이디케이 인수", "text": "광고 · 애니메이션 · 2025년 10월", "at": "애니메이션도", "stamp": {"text": "인수 완료", "at": "마무리됐습니다"}}],
   labels=[lab("게임 밖으로", "게임", "lime")])
sh("counter", [68, 69], value={"from": 0, "to": 9172, "suffix": "억 원", "at": "9,172억"}, caption="2026년 주주환원 (보도)", icon="gift")
sh("icon", 70, icons=[{"name": "coins", "label": "자사주 3,000억 원", "at": "자사주"}], stamp={"text": "소각", "at": "없애기로", "color": "red"})
sh("wide", 71, set="board", time="day", chars=[ch("m1", 600, "neutral", "present")],
   labels=[lab("숫자로만", "숫자로만", "red", x=1250, y=300, size=140), lab("성적표", "성적표를", "cream", x=1250, y=520, size=120)])
sh("counter", [72, 73], value={"from": 0, "to": 33266, "suffix": "억 원", "at": "3조"}, caption="2025년 매출 · 사상 최대 (DART)", icon="trophy",
   compare={"text": "영업이익 1조 544억 원", "icon": "coins", "at": "영업이익은"})
sh("chart", 74, board="chalk", chart={"type": "bar", "values": [11825, 10544], "labels": ["2024년", "2025년"], "suffix": "억 원", "title": "영업이익 (DART)", "show_values": True, "highlight": 1, "at": "4분기에"},
   labels=[lab("-10.8%", "10.8%", "red")])
sh("table", [75, 76, 77], items=[{"type": "receipt", "title": "잘한 결정", "rows": [["2016년 매출", "514억"], ["2017년 매출", "6,665억"]], "text": "약 13배", "at": "잘한"}],
   stamp={"text": "최고의 결정", "at": "13배", "color": "green"})
sh("table", [78, 79], items=[{"type": "receipt", "title": "비싼 실수", "rows": [["개발비 (추산)", "약 2,000억"], ["판매 (보도)", "약 200만 장"]], "text": "전망 300만~500만 장", "at": "비싼"}],
   stamp={"text": "가장 비싼 실수", "at": "추산되는데", "color": "red"})
sh("closeup", 80, who="inv", side="left", set="office", time="day", emotion="nervous", pose="stressed",
   labels=[lab("20만 2천 원", "20만", "red", size=130), lab("2026.11.20", "기준", "cream", size=80)])
sh("chart", 81, board="white", chart={"type": "bar", "values": [24, 9.19], "labels": ["상장 때 (공모가)", "2026.11.20"], "suffix": "조", "title": "시가총액", "show_values": True, "highlight": 1, "at": "시가총액은"},
   labels=[lab("절반도 안 됨", "절반도", "red")])
chap("반전", "5장")
sh("closeup", [82, 83], who="m1", side="right", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "지금은 누가?", "at": "누가", "thought": True})
sh("wide", [84, 85], set="office", era="modern", wall="blue", time="day", chars=[ch("ceo", 960, "calm", "present")],
   lower_third={"name": "김창한", "sub": "크래프톤 대표이사 (2020년 6월~ · 3연임)", "at": "김창한입니다"},
   labels=[lab("세 번째 임기", "세", "gold", x=1450, y=280)])
sh("closeup", 86, who="founder", side="left", set="office", time="day", emotion="calm", pose="arms_crossed",
   labels=[lab("최대주주 · 이사회 의장", "최대주주이자", "cream", size=100)])
sh("chart", [87, 88], board="chalk", chart={"type": "bar", "values": [3486, 2250], "labels": ["2025년 3분기", "2026년 3분기"], "suffix": "억 원", "title": "분기 영업이익 (DART 잠정)", "show_values": True, "highlight": 1, "at": "영업이익은"},
   labels=[lab("-35.5%", "35.5%", "red")])
sh("icon", 89, icons=[{"name": "laptop", "text": "컴퓨터판", "label": "배틀그라운드 매출 감소 (보도)", "at": "컴퓨터판"}, {"name": "chart_down", "label": "이익도 함께", "at": "줄었다고"}])
sh("versus", 90, colors=["#D8F0D8", "#F6C7B6"], left={"who": "ceo", "title": "배틀그라운드 흔들", "emotion": "worried", "pose": "stressed", "at": "흔들리면"},
   right={"who": "ceo", "title": "회사 이익도 흔들", "emotion": "nervous", "pose": "shrug", "at": "이익도"})
sh("wide", [91, 92], set="office", era="modern", wall="sand", time="day", tag="2026년 3월 · 주주총회",
   chars=[ch("inv", 620, "angry", "point"), ch("ceo", 1250, "confident", "explain", beats=[{"at": "증명하겠다고", "pose": "present", "emotion": "confident"}])],
   labels=[lab("성과로 증명", "증명하겠다고", "lime", x=960, y=250, size=120)])
sh("counter", [93, 94], value={"from": 0, "to": 36330, "suffix": "억 원", "at": "3조"}, caption="2026년 1~3분기 매출 (DART 잠정)", icon="chart_up",
   compare={"text": "작년 1년 3조 3,266억 원 돌파", "icon": "trophy", "at": "작년"})
sh("chart", 95, board="white", chart={"type": "bar", "values": [79.4, 20.6], "labels": ["게임", "광고"], "suffix": "%", "title": "2026년 1~3분기 매출 구성 (DART)", "show_values": True, "highlight": 1, "at": "광고에서"})
sh("title", 96, text="마지막 반전")
sh("crowd", 97, count=30, emotion="happy", labels=[lab("살아남았다", "살아남았습니다", "lime", size=150)])
sh("closeup", [98, 99], who="inv", side="right", set="office", time="dusk", emotion="thinking", pose="think",
   labels=[lab("공모가의 41%", "41%", "red", size=120), lab("두 번째 생존자?", "두", "gold", size=110)])
sh("wide", [100, 103], set="office", era="modern", wall="green", time="day",
   chars=[ch("founder", 600, "happy", "wave"), ch("ceo", 960, "happy", "wave"), ch("dev", 1320, "smile", "celebrate")],
   labels=[lab("구독 · 좋아요", "구독과", "lime", x=960, y=230, size=130), lab("출처는 설명란", "출처는", "cream", x=960, y=420)],
   polaroid={"at": "출처는", "who": "ceo", "caption": "살아남은 회사의 다음 질문: 두 번째 생존자"})

# 빈 화면 방지(2026-11-20 검수): 그래픽 장면의 첫 요소는 장면 시작 직후에 나오게 하고, 나머지만 대사 낱말에 맞춘다
for d in X:
    k = d.get("kind")
    if k == "icon" and d.get("icons"): d["icons"][0]["at"] = "+0.2"
    if k == "table" and d.get("items"): d["items"][0]["at"] = "+0.2"
    if k == "chart" and d.get("chart"): d["chart"]["at"] = "+0.3"
    if k == "counter" and d.get("value"): d["value"]["at"] = "+0.3"

story = {"title": "크래프톤_v2", "mood": "upbeat", "cast": {
    "founder": {"skin": "light", "outfit": "sweater", "color": "#2F4A6B", "hair": "short", "hair_col": "#2A2420", "glasses": True},
    "ceo": {"skin": "light", "outfit": "hoodie", "color": "#D9A21B", "hair": "curly", "hair_col": "#1E1A18"},
    "dev": {"skin": "tan", "outfit": "tshirt", "color": "#2E8C86", "hair": "bun", "hair_col": "#3A2C22"},
    "dev2": {"skin": "fair", "outfit": "hoodie", "color": "#8C3A5E", "hair": "long", "hair_col": "#5A3A22"},
    "inv": {"skin": "light", "outfit": "suit", "color": "#4A4A55", "shirt": "#F2F2F2", "tie": "#B02A2A", "hair": "slick", "hair_col": "#6A6A6A", "moustache": True},
    "m1": {"skin": "fair", "outfit": "sweater", "color": "#5E8C6A", "hair": "short", "hair_col": "#3A2C22"}},
  "shots": X}
json.dump(story, open(os.path.join(P, "story.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(X), "shots")
