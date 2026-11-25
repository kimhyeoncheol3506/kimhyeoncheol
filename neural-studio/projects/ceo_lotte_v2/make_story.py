#!/usr/bin/env python3
"""롯데지주(롯데 그룹) v2 스토리보드."""
import json, os
P = os.path.dirname(os.path.abspath(__file__)); X = []
def sh(kind, s, **k):
    d = {"kind": kind}
    if s is not None: d["s"] = s if isinstance(s, list) else [s]
    d.update(k); X.append(d)
def lab(text, at, color="lime", **k): return dict(text=text, at=at, color=color, **k)
def ch(id, x, emotion="neutral", pose="idle", **k): return dict(id=id, x=x, emotion=emotion, pose=pose, **k)
def chap(t, n): sh("title", None, text=t, sub=n, hold=1.6)

# 인트로 · 123층 타워가 담보가 되다 (0프레임부터 도시 그림 + 큰 글자, 3초 안에 도장)
sh("skyline", 0, time="day", cam={"zoom": [1.0, 1.14], "focus": [[960, 545], [1060, 470]]},
   labels=[lab("123층", "+0.0", "gold", x=1420, y=300, size=170), lab("7년 뒤 →", "7년", "cream", x=1420, y=520, size=100)],
   stamp={"text": "담보", "at": "그", "color": "red", "x": 640, "y": 620, "size": 170})
sh("table", 1, hand="bk", items=[{"type": "contract", "title": "담보 계약", "text": "계열사 회사채 2조 원", "at": "+0.2", "stamp": {"text": "지키려고", "at": "지키려던"}}])
sh("icon", 2, icons=[{"name": "building", "label": "롯데 → 롯데지주", "at": "+0.2"}],
   labels=[lab("오늘의 주인공", "주인공은", "gold", size=120)])
chap("판돈", "1장")
sh("wide", [3, 4], set="office", era="old", wall="sand", time="day", tag="1940년대 말 · 일본",
   chars=[ch("fd", 900, "confident", "present", beats=[{"at": "창업주는", "pose": "hold", "emotion": "smile"}])],
   lower_third={"name": "신격호", "sub": "롯데 창업주", "at": "신격호입니다"},
   labels=[lab("껌 하나로 시작 (보도)", "껌", "gold", x=1420, y=260)])
sh("table", [5, 6], hand="fd", items=[{"type": "contract", "title": "롯데제과 설립", "text": "대한민국", "at": "+0.2", "stamp": {"text": "1967년 3월", "at": "롯데제과를"}},
   {"type": "cash", "text": "자본금 3천만 원", "at": "3천만"}])
sh("closeup", [7, 8], who="fd", side="left", set="office", time="day", emotion="calm", pose="think",
   labels=[lab("동생 신춘호 · 라면", "신춘호는", "cream", x=1350, y=320, size=90), lab("→ 농심 편", "농심", "gold", x=1350, y=860, size=110)])
sh("icon", 9, icons=[{"name": "gift", "label": "과자", "at": "+0.2"}, {"name": "building", "label": "백화점 · 호텔", "at": "백화점으로"}, {"name": "heart", "label": "놀이공원", "at": "놀이공원으로"}])
sh("wide", [10, 11], set="street", time="dusk", chars=[ch("fd", 760, "thinking", "think", beats=[{"at": "잠실에", "pose": "point", "emotion": "excited"}])],
   bubble={"who": "fd", "text": "가장 높은 빌딩", "icon": "building", "at": "꿈이", "thought": True},
   labels=[lab("서울 잠실", "잠실에", "gold", x=1450, y=260)])
sh("counter", [12, 13], value={"from": 0, "to": 123, "suffix": "층", "at": "123층"}, caption="롯데월드타워 · 2017년 4월 3일 개장 (보도)", icon="building",
   compare={"text": "높이 555미터", "icon": "target", "at": "555미터입니다"})
sh("closeup", [14, 15], who="m1", side="left", set="home", time="night", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "왜 담보?", "at": "담보", "thought": True}, labels=[lab("7년 만에?", "7년", "red", x=1350, y=860, size=110)])
sh("icon", 16, icons=[{"name": "book", "text": "성적표", "label": "끝에 공개", "at": "+0.2"}], stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
chap("결정", "2장")
sh("wide", 17, set="board", time="day", tag="2011년 2월",
   chars=[ch("sdb", 960, "confident", "present", beats=[{"at": "회장에", "pose": "celebrate", "emotion": "excited"}])],
   lower_third={"name": "신동빈", "sub": "롯데그룹 회장 (2011년~)", "at": "신동빈이"})
sh("icon", [18, 20], icons=[{"name": "factory", "label": "1990년 호남석유화학", "at": "+0.2"}, {"name": "factory", "text": "=", "label": "지금의 롯데케미칼", "at": "롯데케미칼입니다"},
   {"name": "lock", "label": "기억!", "at": "기억해"}])
sh("table", [21, 22], items=[{"type": "newspaper", "title": "2015년 여름", "text": "롯데 경영권 다툼", "at": "+0.2"},
   {"type": "newspaper", "title": "8월 17일 일본 롯데홀딩스 주총", "text": "신동빈 회장 안건 모두 통과 (보도)", "at": "통과됐다고"}])
sh("closeup", 23, who="m1", side="right", set="home", time="day", emotion="calm", pose="explain",
   labels=[lab("가족 이야기는 여기까지", "가족", "cream", x=600, y=860, size=90)])
sh("wide", [24, 25], set="office", era="modern", wall="blue", time="day", tag="2015년 10월 30일",
   chars=[ch("sdb", 820, "confident", "hold", beats=[{"at": "판을", "pose": "point", "emotion": "excited"}])],
   bubble={"who": "sdb", "text": "삼성 화학 사자", "icon": "handshake", "at": "사들이기로"})
sh("table", [26, 27], hand="sdb", items=[{"type": "contract", "title": "삼성 화학 계열사 인수", "text": "삼성SDI 화학 부문 · 삼성정밀화학", "at": "+0.2", "stamp": {"text": "3조 원 안팎 (보도)", "at": "3조"}}])
sh("chart", [28, 30], board="chalk", chart={"type": "bar", "values": [16111, 25443, 29297], "labels": ["2015년", "2016년", "2017년"], "suffix": "억", "title": "롯데케미칼 영업이익 (DART)", "show_values": True, "highlight": 2, "at": "+0.3"})
sh("closeup", [31, 32], who="sdb", side="right", set="office", time="day", emotion="happy", pose="celebrate",
   labels=[lab("2년 만에 1.8배", "1.8배입니다", "gold", x=600, y=300, size=110), lab("화학 = 새 기둥", "기둥이", "lime", x=600, y=860, size=110)])
sh("icon", 33, icons=[{"name": "building", "label": "그룹의 뼈대", "at": "+0.2"}, {"name": "target", "label": "두 번째 결정", "at": "뼈대를"}])
sh("table", 34, hand="sdb", items=[{"type": "contract", "title": "지주회사 출범", "text": "롯데지주 · 2017년 10월 1일", "at": "+0.2", "stamp": {"text": "출범", "at": "출범합니다"}}])
sh("wide", [35, 36], set="board", time="day", chars=[ch("sdb", 900, "confident", "hips", beats=[{"at": "11.7%였습니다", "pose": "celebrate", "emotion": "happy"}])],
   labels=[lab("최대주주: 롯데알미늄 → 신동빈", "최대주주는", "cream", x=960, y=230, size=80), lab("지분 11.7%", "11.7%였습니다", "gold", x=960, y=380, size=110)])
sh("counter", 37, value={"from": 0, "to": 74500, "suffix": "원", "at": "7만"}, caption="롯데지주 2017년 10월 31일 종가 (네이버)", icon="chart_up")
chap("위기", "3장")
sh("closeup", 38, who="m1", side="right", set="home", time="dusk", emotion="worried", pose="stressed",
   labels=[lab("같은 해, 다른 곳에서", "같은", "cream", x=600, y=860, size=90)])
sh("wide", 39, set="board", time="day", tag="2017년 2월 27일", chars=[ch("ex", 960, "nervous", "hold")],
   labels=[lab("성주 골프장 → 사드 부지", "골프장을", "cream", x=960, y=250)], stamp={"text": "승인 (보도)", "at": "승인했다고", "color": "red"})
sh("counter", [40, 41], value={"from": 0, "to": 87, "suffix": "곳", "at": "87곳의"}, caption="중국 롯데마트 영업 중단 (2017년 9월 보도)", icon="warning",
   compare={"text": "전체 112곳 가운데", "icon": "shopping", "at": "112곳"})
sh("table", [42, 43], items=[{"type": "cash", "text": "3,600억 원 · 3월 긴급", "at": "+0.2"}, {"type": "cash", "text": "+3,400억 원 (보도)", "at": "3,400억"}],
   stamp={"text": "긴급 투입", "at": "긴급히", "color": "red"})
sh("walk", [44, 45], set="street", time="dusk", chars=[ch("ex", 0, "sad", "idle")],
   labels=[lab("2017년 9월 매각 착수", "매각", "gold", x=600, y=260), lab("이듬해 가을 · 철수 (보도)", "이듬해", "red", x=1350, y=260)])
sh("closeup", [46, 47], who="m1", side="left", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "어디서?", "at": "어디서", "thought": True})
sh("icon", [48, 49], icons=[{"name": "factory", "label": "다시 화학", "at": "+0.2"}, {"name": "car", "label": "전기차 배터리 소재", "at": "배터리에"}])
sh("table", [50, 52], hand="sdb", items=[{"type": "contract", "title": "일진머티리얼즈 인수", "text": "배터리 소재", "at": "+0.2", "stamp": {"text": "2022년 10월 계약", "at": "계약을"}},
   {"type": "receipt", "title": "2023년 3월 거래 종결 (DART)", "rows": [["지분", "53.3%"], ["금액", "2조 7천억 원"]], "text": "2조 7천억", "at": "2023년"}])
sh("wide", 53, set="office", era="modern", wall="grey", time="day", chars=[ch("ex", 760, "smile", "present")],
   labels=[lab("→ 롯데에너지머티리얼즈", "롯데에너지머티리얼즈로", "gold", x=1350, y=260, size=90)])
sh("icon", [54, 56], icons=[{"name": "vial", "label": "2022년 5월 롯데바이오로직스", "at": "+0.2"}, {"name": "factory", "label": "미국 뉴욕주 의약품 공장", "at": "뉴욕주에"}])
sh("closeup", 57, who="ex", side="right", set="office", time="night", emotion="sad", pose="shrug",
   labels=[lab("롯데헬스케어 · 2024년 12월", "롯데헬스케어는", "cream", x=600, y=300, size=80)], stamp={"text": "해산 결의", "at": "해산을", "color": "red"})
chap("베팅", "4장")
sh("chart", [58, 60], board="white", chart={"type": "bar", "values": [3916, 9145], "labels": ["2023년", "2024년"], "suffix": "억", "title": "롯데케미칼 영업손실 (DART)", "show_values": True, "highlight": 1, "trend": "down", "at": "+0.3"},
   labels=[lab("숫자가 뒤집힌다", "뒤집힙니다", "red")])
sh("crowd", [61, 62], count=24, emotion="nervous", set="street", labels=[lab("2024년 11월 18일 · 유동성 위기설", "위기설이", "red", size=90), lab("롯데지주: 사실무근 (공시)", "사실무근이라고", "lime", size=90)])
sh("table", [63, 65], items=[{"type": "letter", "title": "회사채 약속 (재무 특약)", "text": "3년 이익 ≥ 이자 비용 × 5배", "at": "+0.2"}],
   stamp={"text": "4.3배 (보도)", "at": "4.3배였다고", "color": "red"})
sh("closeup", [66, 67], who="bk", side="left", set="office", time="day", emotion="confident", pose="point",
   bubble={"who": "bk", "text": "미리 갚으세요?", "at": "요구할"}, labels=[lab("대상 2조 450억 원 (보도)", "2조", "red", x=1350, y=860, size=90)])
sh("wide", [68, 69], set="board", time="night", tag="2024년 11월 27일",
   chars=[ch("sdb", 700, "worried", "think", beats=[{"at": "롯데월드타워를", "pose": "present", "emotion": "confident"}]), ch("bk", 1250, "calm", "hold")],
   stamp={"text": "롯데월드타워 담보", "at": "담보로", "color": "red"})
sh("counter", 70, value={"from": 0, "to": 6, "suffix": "조 원", "at": "6조"}, caption="롯데월드타워 가치 추산 (보도)", icon="building")
sh("table", [71, 73], hand="bk", items=[{"type": "contract", "title": "담보 제공 (공시)", "text": "롯데물산 → 은행 · 타워와 쇼핑몰", "at": "+0.2", "stamp": {"text": "2조 682억 원", "at": "682억"}}],
   labels=[lab("회사채 다 갚을 때까지", "갚을", "gold")])
sh("crowd", 74, count=18, emotion="calm", set="void", labels=[lab("12월 19일 사채권자 집회", "사채권자", "cream", size=90), lab("14개 모두 원안 가결", "가결됩니다", "lime", size=100)])
sh("chart", [75, 76], board="chalk", chart={"type": "bar", "values": [74500, 19820], "labels": ["2017.10.31", "2024.12.9"], "suffix": "원", "title": "롯데지주 주가 (네이버 종가)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("가장 낮은 종가", "가장", "red")])
sh("icon", [77, 78], icons=[{"name": "trophy", "label": "AA0 · 2023년 초", "at": "+0.2"}, {"name": "chart_down", "label": "A+ · 2025년 6월", "at": "A+가"}],
   labels=[lab("회사채 신용등급 (DART)", "등급은", "cream")])
sh("counter", 79, value={"from": 0, "to": 9431, "suffix": "억 원", "at": "9,431억"}, caption="롯데케미칼 2025년 영업손실 (DART)", icon="chart_down")
sh("chart", 80, board="white", chart={"type": "bar", "values": [9461, 5950], "labels": ["2024년", "2025년"], "suffix": "억", "title": "롯데지주 연결 순손실 (DART)", "show_values": True, "highlight": 0, "at": "+0.3"})
sh("wide", [81, 82], set="office", era="modern", wall="blue", time="day",
   chars=[ch("sdb", 760, "calm", "explain", beats=[{"at": "707억", "pose": "present", "emotion": "smile"}])],
   labels=[lab("담보 2029년 3월까지 (보도)", "2029년", "red", x=1400, y=260, size=90), lab("1~9월 순이익 707억", "707억", "lime", x=1400, y=420, size=90)])
sh("table", [83, 84], items=[{"type": "newspaper", "title": "대표이사 변경 (공시)", "text": "신동빈 · 노준형", "at": "+0.2", "stamp": {"text": "11월 19일", "at": "사임합니다"}}])
chap("성적표", "5장")
sh("icon", [85, 86], icons=[{"name": "book", "text": "성적표", "label": "롯데 성적표", "at": "+0.2"}, {"name": "coins", "label": "시작: 1967년 3천만 원", "at": "3천만"}],
   stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("chart", [87, 89], board="chalk", chart={"type": "bar", "values": [74500, 21700], "labels": ["2017.10.31", "2026.11.25"], "suffix": "원", "title": "롯데지주 주가 (네이버 종가)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("-70.9%", "70.9%", "red", size=130)])
sh("counter", [90, 91], value={"from": 0, "to": 21627, "suffix": "억 원", "at": "2조"}, caption="롯데지주 시가총액 (2026년 11월 25일, 네이버)", icon="trophy",
   compare={"text": "주가순자산비율 0.28배", "icon": "coins", "at": "0.28배로"})
sh("table", [92, 93], items=[{"type": "receipt", "title": "잘한 결정", "rows": [["2015년", "삼성 화학 인수"], ["2년 뒤", "영업이익 1.8배"]], "text": "2조 9,297억", "at": "+0.2"}],
   stamp={"text": "최고의 결정", "at": "1.8배가", "color": "green"})
sh("versus", [94, 95], colors=["#D8F0D8", "#F6C7B6"], left={"who": "sdb", "title": "2017년 영업이익 2조 9,297억", "emotion": "happy", "pose": "celebrate", "at": "같은"},
   right={"who": "sdb", "title": "3년 영업손실 2조 2,493억", "emotion": "sad", "pose": "facepalm", "at": "3년"},
   stamp={"text": "가장 비싼 실수", "at": "바구니입니다", "color": "red"})
sh("counter", [96, 97], value={"from": 0, "to": 22493, "suffix": "억 원", "at": "2조"}, caption="롯데케미칼 2023~2025년 영업손실 합계 (DART로 계산)", icon="chart_down",
   compare={"text": "그 끝: 타워 담보 2조 682억 원", "icon": "building", "at": "682억"})
sh("closeup", [98, 99], who="m1", side="left", set="home", time="dusk", emotion="sad", pose="shrug",
   labels=[lab("중국 롯데마트", "중국", "cream", x=1350, y=320, size=90), lab("112곳 중 87곳 멈춤", "87곳이", "red", x=1350, y=860, size=100)])
sh("icon", 100, icons=[{"name": "building", "label": "롯데지주 지분 13.7%", "at": "+0.2"}], labels=[lab("최대주주 신동빈", "최대주주입니다", "gold")])
chap("반전", "6장")
sh("closeup", 101, who="m1", side="right", set="home", time="day", emotion="calm", pose="explain")
sh("versus", [102, 103], colors=["#D9D9E6", "#F6C7B6"], left={"who": "sdb", "title": "1990년 첫 직장 = 롯데케미칼", "emotion": "calm", "pose": "present", "at": "1990년"},
   right={"who": "fd", "title": "123층 타워 = 그 회사의 담보", "emotion": "worried", "pose": "think", "at": "123층"})
sh("table", [104, 105], items=[{"type": "receipt", "title": "롯데케미칼 2026년 (DART)", "rows": [["1분기", "영업이익"], ["2분기", "영업이익"], ["3분기", "영업손실 2,814억"]], "text": "다시 적자", "at": "+0.2"}],
   stamp={"text": "-2,814억", "at": "2,814억", "color": "red"})
sh("title", 106, text="담보는, 회사채를 다 갚는 날까지")
sh("wide", [107, 111], set="office", era="modern", wall="blue", time="day",
   chars=[ch("fd", 600, "happy", "wave"), ch("m1", 960, "happy", "wave"), ch("sdb", 1320, "smile", "celebrate")],
   labels=[lab("구독 · 좋아요", "구독과", "lime", x=960, y=230, size=130), lab("출처는 설명란", "출처는", "cream", x=960, y=420)],
   polaroid={"at": "출처는", "who": "fd", "caption": "껌으로 시작, 숙제는 화학"})

# 빈 화면 방지(2026-11-20 검수): 그래픽 장면의 첫 요소는 장면 시작 직후에 나오게 하고, 나머지만 대사 낱말에 맞춘다
for d in X:
    k = d.get("kind")
    if k == "icon" and d.get("icons"): d["icons"][0]["at"] = "+0.2"
    if k == "table" and d.get("items"): d["items"][0]["at"] = "+0.2"
    if k == "chart" and d.get("chart"): d["chart"]["at"] = "+0.3"
    if k == "counter" and d.get("value"): d["value"]["at"] = "+0.3"

story = {"title": "롯데_v2", "mood": "dramatic", "cast": {
    "fd": {"skin": "light", "outfit": "suit", "color": "#3B3B44", "shirt": "#F2F2F2", "tie": "#8A1C1C", "hair": "short", "hair_col": "#D8D8D8", "glasses": True},
    "sdb": {"skin": "fair", "outfit": "suit", "color": "#1F2A44", "shirt": "#F2F2F2", "tie": "#DA291C", "hair": "slick", "hair_col": "#3A3A3A"},
    "bk": {"skin": "tan", "outfit": "suit", "color": "#4A5A4A", "tie": "#2E6FB8", "hair": "bald"},
    "ex": {"skin": "olive", "outfit": "sweater", "color": "#8A6A4A", "hair": "bun", "hair_col": "#2A2420"},
    "m1": {"skin": "fair", "outfit": "hoodie", "color": "#5E8C6A", "hair": "curly", "hair_col": "#3A2C22"}},
  "shots": X}
for d in X:
    if d.get("kind") == "walk":
        for c in d.get("chars", []): c.pop("x", None)
json.dump(story, open(os.path.join(P, "story.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(X), "shots")
