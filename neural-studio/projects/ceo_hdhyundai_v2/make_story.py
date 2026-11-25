#!/usr/bin/env python3
"""HD현대 v2 스토리보드 (CEO 시리즈 30편)."""
import json, os
P = os.path.dirname(os.path.abspath(__file__)); X = []
def sh(kind, s, **k):
    d = {"kind": kind}
    if s is not None: d["s"] = s if isinstance(s, list) else [s]
    d.update(k); X.append(d)
def lab(text, at, color="lime", **k): return dict(text=text, at=at, color=color, **k)
def ch(id, x, emotion="neutral", pose="idle", **k): return dict(id=id, x=x, emotion=emotion, pose=pose, **k)
def chap(t, n): sh("title", None, text=t, sub=n, hold=1.6)

# 인트로 · 3조 적자 → 6조 흑자 → 주가 -64% (첫 장면은 세트·인물·글자가 0프레임부터 보이는 world 샷)
sh("wide", 0, set="office", era="modern", wall="grey", time="night", tag="2014년 · 울산",
   chars=[ch("kwon", 760, "worried", "stressed", beats=[{"at": "영업손실을", "pose": "facepalm", "emotion": "shocked"}])],
   props=[{"icon": "chart_down", "x": 1450, "y": 760, "s": 0.8, "at": "+0"}],
   labels=[lab("영업손실 -3조 2,495억", "+0", "red", x=1350, y=260, size=95)])
sh("icon", 1, icons=[{"name": "chart_up", "text": "조 단위", "label": "몇 년 뒤 · 지주회사 영업이익", "at": "+0.2"}])
sh("versus", 2, colors=["#D8F0D8", "#F6C7B6"], left={"who": "m1", "title": "조 단위 이익", "emotion": "happy", "pose": "celebrate", "at": "그런데"},
   right={"who": "m1", "title": "주가는 꼭대기보다 한참 아래", "emotion": "shocked", "pose": "facepalm", "at": "한참"})
sh("skyline", 3, time="dusk", labels=[lab("HD현대", "HD현대", size=150), lab("옛 현대중공업", "옛", "cream", size=90)])
chap("판돈", "1장")
sh("walk", [4, 5], set="street", time="day", tag="1972년 3월 · 울산 미포만", chars=[ch("cjy", 0, "confident", "idle")],
   labels=[lab("모래밭에서 조선소 기공식", "기공식을", "gold", x=1350, y=260)],
   lower_third={"name": "정주영", "sub": "창업주 · 12편 주인공", "at": "정주영"})
sh("icon", 6, icons=[{"name": "book", "text": "12편", "label": "창업주 이야기는 12편", "at": "+0.2"}, {"name": "target", "label": "오늘은 배 쪽만", "at": "배"}])
sh("wide", [7, 8], set="board", time="day", tag="1974년 6월",
   chars=[ch("cjy", 700, "happy", "present", beats=[{"at": "명명식이", "pose": "celebrate", "emotion": "excited"}]), ch("m1", 1250, "smile", "wave")],
   labels=[lab("조선소 준공 + 유조선 2척 명명식", "명명식이", "gold", x=960, y=230, size=85), lab("1호선 애틀랜틱 배런", "애틀랜틱", "lime", x=960, y=400)])
sh("icon", [9, 10], icons=[{"name": "target", "text": "엔진", "label": "1979년 첫 대형 엔진", "at": "+0.2"}, {"name": "trophy", "label": "1980년 첫 군함 울산함", "at": "군함인"}])
sh("table", [11, 12], items=[{"type": "letter", "title": "세 갈래", "text": "상선 · 엔진 · 군함", "at": "+0.2", "ring_at": "세"}],
   stamp={"text": "이미 다 있었다", "at": "이미", "color": "red"})
sh("counter", [13, 14], value={"from": 0, "to": 2226000, "suffix": "톤", "at": "+0.3"}, caption="1983년 한 해 건조량 · 세계 1위 (회사 연혁)", icon="trophy")
sh("map", 15, places=[{"name": "현대그룹", "x": 520, "y": 560}, {"name": "현대중공업그룹", "x": 1400, "y": 520}], vehicle="ship", at="+0.3",
   labels=[lab("2002년 계열 분리 (보도)", "2002년", "gold")])
sh("closeup", [16, 17], who="mj", side="left", set="office", time="day", emotion="calm", pose="arms_crossed",
   lower_third={"name": "정몽준", "sub": "최대주주 · 1988~2014년 국회의원 (DART)", "at": "정몽준이었습니다"},
   labels=[lab("경영은 전문경영인 (보도)", "전문경영인이", "cream", x=1350, y=860, size=80)])
sh("crowd", [18, 20], count=22, emotion="thinking", set="void",
   labels=[lab("세계 1위가 왜 3조를 잃었나?", "왜", "red", size=95), lab("끝에 숫자 성적표", "성적표를", "cream")])
chap("위기", "2장")
sh("table", 21, items=[{"type": "newspaper", "title": "2014년 조선업 쇼크", "text": "해양·플랜트 손실 · 수주 급감 (보도)", "at": "+0.2"}])
sh("counter", 22, value={"from": 0, "to": 11000, "suffix": "억 원", "at": "+0.3", "color": "red"}, caption="2014년 2분기 영업손실 · 약 (보도)", icon="chart_down")
sh("wide", 23, set="office", era="modern", wall="blue", time="day",
   chars=[ch("kwon", 960, "confident", "present", enter="left", beats=[{"at": "사장으로", "pose": "hips"}])],
   lower_third={"name": "권오갑", "sub": "현대오일뱅크 사장 → 현대중공업 사장 (2014년, 보도)", "at": "권오갑이"})
sh("table", [24, 25], hand="kwon", items=[{"type": "receipt", "title": "2014년 연간 실적 (DART 연결)", "rows": [["매출", "52조 5,824억"], ["영업손실", "3조 2,495억"]], "text": "창사 이래 최대 적자 (보도)", "at": "+0.2"}],
   stamp={"text": "-3조 2,495억", "at": "3조", "color": "red"})
sh("counter", 26, value={"from": 0, "to": 15401, "suffix": "억 원", "at": "+0.3", "color": "red"}, caption="2015년 영업손실 (DART 연결)", icon="chart_down")
sh("closeup", 27, who="m1", side="left", set="home", time="night", emotion="sad", pose="stressed",
   labels=[lab("도크 가동 중단 · 희망퇴직 (보도)", "도크를", "red", x=1350, y=860, size=80)])
sh("walk", 28, set="street", time="night", tag="2017년 7월 · 군산", chars=[ch("m1", 0, "sad", "idle")],
   labels=[lab("군산조선소 가동 중단", "가동을", "red", x=1350, y=260)])
sh("counter", 29, value={"from": 0, "to": 16419, "suffix": "억 원", "at": "+0.3", "color": "green"}, caption="2016년 영업이익 · 흑자 전환 (DART 연결)", icon="chart_up")
chap("결정", "3장")
sh("closeup", [30, 31], who="m1", side="right", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "뭘 바꿨을까?", "at": "바꾼", "thought": True})
sh("table", [32, 34], hand="kwon", items=[{"type": "contract", "title": "회사 분할 결정 (DART)", "text": "분할기일 2017년 4월 1일", "at": "+0.2", "stamp": {"text": "분할", "at": "나뉩니다"}},
   {"type": "letter", "title": "새 회사 3곳", "text": "전기전자 · 건설장비 · 로봇/투자", "at": "전기전자와"}])
sh("icon", [35, 36], icons=[{"name": "building", "label": "로봇·투자 회사 → 지주회사", "at": "+0.2"}, {"name": "trophy", "label": "지금의 HD현대", "at": "지금의"}])
sh("chart", [37, 38], board="white", chart={"type": "bar", "values": [10.15, 26.60], "labels": ["2016년 말 현대중공업", "2025년 말 HD현대"], "suffix": "%", "title": "정몽준 지분율 (DART)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("26.60%", "26.60%", "gold")])
sh("closeup", 39, who="mj", side="right", set="office", time="day", emotion="calm", pose="hold",
   labels=[lab("쥔 회사가 바뀌자 지분율 2배+", "두", "gold", x=600, y=860, size=85)])
sh("map", [40, 42], places=[{"name": "HD한국조선해양 (중간 지주)", "x": 560, "y": 520}, {"name": "새 현대중공업", "x": 1380, "y": 600}], vehicle="ship", at="+0.3",
   labels=[lab("2019년 6월 물적분할 (DART)", "2019년", "gold")])
sh("wide", [43, 44], set="board", time="day", tag="2019년 3월",
   chars=[ch("kwon", 700, "confident", "present"), ch("m1", 1250, "nervous", "idle")],
   labels=[lab("더 큰 판: 대우조선해양 인수", "대우조선해양을", "gold", x=960, y=230, size=90)])
sh("table", [45, 46], hand="eu", items=[{"type": "letter", "title": "EU 집행위원회 결정", "text": "LNG 운반선 경쟁 축소 우려", "at": "+0.2"}],
   stamp={"text": "불허", "at": "허가하지", "color": "red"})
sh("closeup", 47, who="kwon", side="left", set="office", time="night", emotion="sad", pose="facepalm",
   labels=[lab("인수 무산", "무산됐고", "red", x=1350, y=860, size=120)])
sh("icon", [48, 49], icons=[{"name": "building", "label": "2021년 두산인프라코어", "at": "+0.2"}, {"name": "book", "text": "HD", "label": "2022년 3월 이름: HD현대", "at": "HD현대로"}])
chap("베팅", "4장")
sh("skyline", 50, time="day", labels=[lab("바다의 날씨가 바뀐다", "날씨가", "sky", size=110)])
sh("closeup", [51, 52], who="m1", side="right", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "얼마?", "at": "얼마를", "thought": True})
sh("chart", [53, 55], board="chalk", chart={"type": "bar", "values": [2823, 14341, 39045], "labels": ["2023년", "2024년", "2025년"], "suffix": "억", "title": "HD한국조선해양 영업이익 (DART 연결)", "show_values": True, "highlight": 2, "at": "+0.3"},
   labels=[lab("3조 9,045억", "3조", "green")])
sh("closeup", 56, who="m1", side="left", set="home", time="day", emotion="shocked", pose="celebrate",
   labels=[lab("2년 만에 13배+", "13배가", "green", x=1350, y=860, size=120)])
sh("counter", [57, 58], value={"from": 0, "to": 822369, "suffix": "억 원", "at": "+0.3"}, caption="2025년 말 수주잔고 (DART)", icon="calendar",
   compare={"text": "1년 매출의 약 2.7배", "icon": "hourglass", "at": "2.7배"})
sh("versus", [59, 60], colors=["#E6E6E6", "#D8F0D8"], left={"who": "kis", "title": "2024년 2조 9,832억", "emotion": "calm", "pose": "idle", "at": "+0.3"},
   right={"who": "kis", "title": "2025년 6조 996억", "emotion": "happy", "pose": "celebrate", "at": "6조"},
   stamp={"text": "2배+", "at": "두", "color": "green"})
sh("counter", [61, 62], value={"from": 0, "to": 98791, "suffix": "억 원", "at": "+0.3", "color": "green"}, caption="2026년 1~9월 HD현대 영업이익 (DART 잠정)", icon="chart_up")
sh("crowd", [63, 64], count=28, emotion="excited", set="street", tag="2025년 11월 19일 · 울산",
   labels=[lab("누적 5,000척 인도", "5,000번째", "gold", size=110), lab("1974년 첫 배 이후 (회사 발표)", "1974년", "cream")])
sh("map", 65, places=[{"name": "울산", "x": 1100, "y": 420}, {"name": "필리핀", "x": 900, "y": 760}], vehicle="ship", at="+0.3",
   labels=[lab("5,000번째 = 필리핀 해군 초계함 (보도)", "초계함이었다고", "gold")])
sh("title", 66, text="그룹의 얼굴이 바뀐다")
sh("wide", [67, 69], set="board", time="day", tag="2025년 10월",
   chars=[ch("kis", 960, "confident", "present", enter="left", beats=[{"at": "오릅니다", "pose": "wave", "emotion": "smile"}])],
   lower_third={"name": "정기선", "sub": "HD현대 회장 (2025년~) · 2009년 입사", "at": "정기선이"},
   labels=[lab("전문경영인 → 오너 경영 (평가)", "오너", "cream", x=960, y=230, size=80)])
sh("closeup", 70, who="kwon", side="left", set="office", time="dusk", emotion="calm", pose="tiphat",
   labels=[lab("권오갑 → 명예회장", "명예회장이", "cream", x=1350, y=860, size=95)])
sh("table", [71, 72], hand="mj", items=[{"type": "contract", "title": "주식 증여 (DART 2026.9.3)", "text": "HD현대 280만 주 · 정몽준 → 정기선", "at": "+0.2"},
   {"type": "receipt", "title": "정기선 HD현대 지분", "rows": [["증여 전", "6.12%"], ["증여 뒤", "9.67%"]], "text": "공시 기준", "at": "6.12%에서"}])
sh("closeup", 73, who="kis", side="right", set="office", time="day", emotion="confident", pose="point",
   bubble={"who": "kis", "text": "미국", "icon": "target", "at": "미국이었습니다"})
sh("map", 74, places=[{"name": "울산", "x": 1450, "y": 480}, {"name": "미국", "x": 450, "y": 520}], vehicle="ship", at="+0.3",
   labels=[lab("2025년 8월 미 해군 함정 정비 첫 수주 (보도)", "정비", "gold")])
sh("table", 75, hand="kis", items=[{"type": "contract", "title": "HD Kiewit Shipbuilding", "text": "합작법인 계약 · 2026년 10월 22일 (DART)", "at": "+0.2"}],
   stamp={"text": "미국 새 조선소", "at": "짓기로", "color": "red"})
sh("icon", 76, icons=[{"name": "handshake", "label": "인도 타밀나두 업무협약", "at": "+0.2"}, {"name": "warning", "label": "투자 규모 미확정 (공시)", "at": "아직"}])
sh("wide", [77, 78], set="office", era="modern", wall="teal", time="day", tag="2024년 7월",
   chars=[ch("kis", 760, "confident", "present", beats=[{"at": "사들여", "pose": "celebrate", "emotion": "excited"}])],
   props=[{"icon": "target", "x": 1400, "y": 760, "s": 0.7, "at": "엔진도"}],
   labels=[lab("STX중공업 35.05% → HD현대마린엔진", "35.05%를", "gold", x=1300, y=250, size=75)])
sh("counter", [79, 80], value={"from": 0, "to": 28901, "suffix": "억 원", "at": "+0.3"}, caption="2025년 엔진기계 매출 (HD한국조선해양 연결, DART)", icon="chart_up",
   compare={"text": "1년 전보다 +30.7%", "icon": "trophy", "at": "30.7%"})
sh("icon", 81, icons=[{"name": "handshake", "label": "HD현대중공업 + HD현대미포", "at": "+0.2"}, {"name": "calendar", "top": "2025", "text": "12월", "label": "합병", "at": "합병합니다"}])
sh("table", [82, 83], hand="kis", items=[{"type": "contract", "title": "군산조선소 처분 결정 (DART)", "text": "2026년 6월 26일 · 제이오션중공업", "at": "+0.2", "stamp": {"text": "7,800억", "at": "7,800억"}}],
   labels=[lab("반대로 파는 것", "파는", "cream")])
sh("walk", [84, 85], set="street", time="dusk", tag="군산", chars=[ch("m1", 0, "calm", "idle")],
   labels=[lab("2017년 멈춤 → 2022년 재가동 (보도)", "불황", "cream", x=1350, y=260, size=75), lab("소유권 이전 2026.12.31 예정", "소유권", "gold", x=600, y=260, size=75)])
sh("closeup", [86, 87], who="m1", side="left", set="home", time="day", emotion="confident", pose="explain",
   stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("chart", [88, 90], board="white", chart={"type": "bar", "values": [66300, 479500], "labels": ["2020.3.19", "2025.11.3"], "suffix": "원", "title": "HD한국조선해양 종가 (네이버)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("7.2배", "7.2배입니다", "green")])
sh("counter", [91, 93], value={"from": 310500, "to": 111900, "suffix": "원", "at": "+0.3", "color": "red"}, caption="HD현대 종가 2026.4.30 → 2026.11.25 (네이버)", icon="chart_down",
   compare={"text": "꼭대기보다 -64%", "icon": "warning", "at": "64%"})
sh("versus", 94, colors=["#D8F0D8", "#F6C7B6"], left={"who": "kis", "title": "이익 최대", "emotion": "happy", "pose": "celebrate", "at": "+0.3"},
   right={"who": "kis", "title": "주가 꼭대기의 1/3", "emotion": "worried", "pose": "stressed", "at": "주가는"})
sh("closeup", 95, who="m1", side="right", set="home", time="night", emotion="thinking", pose="shrug",
   labels=[lab("원인 하나로 단정 못 함", "단정하기는", "cream", x=600, y=860, size=90)])
sh("table", 96, items=[{"type": "newspaper", "title": "2026년 7월 (보도)", "text": "캐나다 잠수함 → 독일 회사", "at": "+0.2"}])
sh("closeup", 97, who="kis", side="left", set="office", time="day", emotion="calm", pose="explain",
   labels=[lab("임금 교섭 10월 27일 타결 (보도)", "타결됐다고", "cream", x=1350, y=860, size=75)])
sh("chart", [98, 99], board="chalk", chart={"type": "bar", "values": [249283, 88393], "labels": ["HD현대중공업", "HD현대 (지주)"], "suffix": "억", "title": "시가총액 2026.11.25 (네이버)", "show_values": True, "highlight": 0, "at": "+0.3"},
   labels=[lab("8조 8,393억", "8조", "gold")])
sh("icon", 100, icons=[{"name": "building", "label": "손자 회사 HD현대중공업", "at": "+0.2"}, {"name": "trophy", "label": "지주회사보다 약 2.8배", "at": "2.8배"}])
sh("closeup", 101, who="kwon", side="left", set="office", time="night", emotion="sad", pose="facepalm",
   stamp={"text": "-3조 2,495억", "at": "3조", "color": "red"}, labels=[lab("가장 비싼 숫자", "비싼", "cream", x=1350, y=860)])
sh("table", 102, items=[{"type": "contract", "title": "대우조선해양 인수", "text": "2019년 3월 계약 → 2022년 1월 불허", "at": "+0.2", "stamp": {"text": "무산", "at": "무산된"}}])
sh("counter", [103, 104], value={"from": 0, "to": 60996, "suffix": "억 원", "at": "+0.3", "color": "green"}, caption="가장 잘한 결정 · 2025년 HD현대 영업이익 (DART)", icon="trophy")
sh("icon", 105, icons=[{"name": "building", "label": "최대주주 쪽 지분 37.12% (2026.11 공시)", "at": "+0.2"}])
chap("반전", "6장")
sh("closeup", [106, 107], who="m1", side="left", set="home", time="dusk", emotion="calm", pose="explain",
   labels=[lab("2014년: 바다 위 공장", "바다", "red", x=1350, y=860, size=95)])
sh("walk", 108, set="street", time="day", chars=[ch("kis", 0, "happy", "idle")],
   labels=[lab("다시 일으킨 건: 배 짓기", "배를", "gold", x=1350, y=260)])
sh("map", 109, places=[{"name": "울산 · 1974년", "x": 1450, "y": 480}, {"name": "미국 새 조선소", "x": 450, "y": 520}], vehicle="ship", at="+0.3",
   labels=[lab("5,000척 → 다음은 미국", "미국", "gold")])
sh("title", 110, text="시장은 아직 값을 다 매기지 않았다")
sh("wide", [111, 116], set="office", era="modern", wall="blue", time="day",
   chars=[ch("kis", 600, "smile", "wave"), ch("m1", 960, "happy", "wave"), ch("kwon", 1320, "smile", "celebrate")],
   labels=[lab("구독 · 좋아요", "구독과", "lime", x=960, y=230, size=130), lab("출처는 설명란", "출처는", "cream", x=960, y=420)],
   polaroid={"at": "출처는", "who": "m1", "caption": "3조 적자에서 6조 이익까지, 숙제는 시장의 믿음"})

# 빈 화면 방지(2026-11-20 검수): 그래픽 장면의 첫 요소는 장면 시작 직후에 나오게 하고, 나머지만 대사 낱말에 맞춘다
for d in X:
    k = d.get("kind")
    if k == "icon" and d.get("icons"): d["icons"][0]["at"] = "+0.2"
    if k == "table" and d.get("items"): d["items"][0]["at"] = "+0.2"
    if k == "chart" and d.get("chart"): d["chart"]["at"] = "+0.3"
    if k == "counter" and d.get("value"): d["value"]["at"] = "+0.3"

story = {"title": "HD현대_v2", "mood": "dramatic", "cast": {
    "cjy": {"skin": "tan", "outfit": "suit", "color": "#3A3A3A", "shirt": "#F2F2F2", "tie": "#5A2A2A", "hair": "short", "hair_col": "#2A2420", "hat": "cap", "hat_col": "#E8E2D0"},
    "mj": {"skin": "light", "outfit": "suit", "color": "#2F3E5C", "shirt": "#F2F2F2", "tie": "#7A1F2B", "hair": "slick", "hair_col": "#3A3230"},
    "kwon": {"skin": "tan", "outfit": "suit", "color": "#4A4A52", "shirt": "#F2F2F2", "tie": "#2E6FB8", "hair": "short", "hair_col": "#9A9A9A", "glasses": True},
    "kis": {"skin": "fair", "outfit": "suit", "color": "#1F3A6B", "shirt": "#F2F2F2", "tie": "#00AE42", "hair": "short", "hair_col": "#1E1A18"},
    "eu": {"skin": "light", "outfit": "suit", "color": "#2A3F8F", "tie": "#E0C020", "hair": "bun", "hair_col": "#B08A5A"},
    "m1": {"skin": "fair", "outfit": "hoodie", "color": "#5E8C6A", "hair": "curly", "hair_col": "#3A2C22"}},
  "shots": X}
for d in X:
    if d.get("kind") == "walk":
        for c in d.get("chars", []): c.pop("x", None)
json.dump(story, open(os.path.join(P, "story.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(X), "shots")
