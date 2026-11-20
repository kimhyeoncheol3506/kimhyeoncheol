#!/usr/bin/env python3
"""셀트리온 v2 전체 스토리보드(story.json) 생성. 문장 번호는 `python3 -m engine sentences <P>` 기준."""
import json, os
P = os.path.dirname(os.path.abspath(__file__))
X = []
def sh(kind, s, **k):
    d = {"kind": kind}
    if s is not None: d["s"] = s if isinstance(s, list) else [s]
    d.update(k); X.append(d)
def lab(text, at, color="lime", **k): return dict(text=text, at=at, color=color, **k)
def ch(id, x, emotion="neutral", pose="idle", **k): return dict(id=id, x=x, emotion=emotion, pose=pose, **k)

# ── 인트로 (첫 1분 승인본 그대로) ──
sh("wide", 0, set="office", era="old", wall="sand", time="day", calendar="첫날 1",
   chars=[ch("mate1", 560, "nervous", "hold"), ch("founder", 960, "confident", "present"), ch("mate2", 1360, "smile", "arms_crossed")],
   labels=[lab("직원 6명", "여섯", x=520, y=260), lab("자본금 5천만 원", "5천만", "cream", x=1300, y=420)])
sh("counter", 1, value={"from": 0, "to": 49.4, "suffix": "조 원", "at": "시가총액은"}, caption="시가총액 · 2026년 11월 20일 종가", icon="chart_up")
sh("icon", 2, icons=[{"name": "coins", "label": "5천만 원", "at": "처음"}, {"name": "moneybag", "label": "49조 4천억 원", "at": "98만"}],
   labels=[lab("약 98만 배", "98만", "red", size=150)])
sh("table", 3, hand="founder", items=[{"type": "contract", "title": "지분 매각 선언", "text": "다국적 제약사에 팔겠다", "at": "창업주는", "stamp": {"text": "매각?", "at": "선언한"}}],
   labels=[lab("2013년 4월", "팔겠다고", "gold")])
sh("title", 4, text="그리고 12년 뒤, 정반대의 일이")
sh("skyline", 5, time="day", labels=[lab("셀트리온", "셀트리온입니다", size=160)])
sh("title", None, text="판돈", sub="1장", hold=1.6)

# ── 1장 · 판돈 ──
sh("table", 6, tag="1999년", items=[{"type": "newspaper", "title": "경제신문", "text": "대우그룹 해체", "at": "대우그룹이", "ring_at": "무너집니다"}])
sh("walk", 7, set="street", time="dusk", chars=[{"id": "founder", "emotion": "sad", "pose": "hold"}],
   lower_third={"name": "서정진", "sub": "셀트리온 창업주", "at": "남자도"})
sh("wide", 8, set="office", era="old", wall="grey", time="night", calendar="다시 1",
   chars=[ch("founder", 760, "confident", "point", beats=[{"at": "다시", "pose": "celebrate", "emotion": "excited"}]), ch("mate1", 1120, "happy"), ch("mate2", 1440, "smile", "wave")],
   labels=[lab("여섯 명, 다시 시작", "여섯", "cream", x=600, y=250)])
sh("versus", 9, colors=["#D6E4F0", "#F2DCC8"],
   left={"who": "founder", "title": "34세 대우차 임원", "emotion": "smug", "pose": "tiphat", "at": "서른네"},
   right={"who": "founder", "title": "45세 맨손", "emotion": "worried", "pose": "pockets", "at": "마흔다섯"})
sh("icon", 10, icons=[{"name": "bulb", "label": "바이오시밀러", "at": "바이오시밀러였습니다"}], chars=[ch("founder", 1500, "thinking", "think")])
sh("versus", 11, colors=["#F6C7B6", "#BFD9F2"],
   left={"who": "exec", "title": "오리지널 바이오 약", "emotion": "smug", "pose": "arms_crossed", "at": "비싼"},
   right={"who": "founder", "title": "똑같이 만든 약", "emotion": "confident", "pose": "present", "at": "똑같이"})
sh("table", 12, hand="founder", items=[{"type": "contract", "title": "램시마 허가", "text": "세계 최초 항체 바이오시밀러", "at": "램시마가", "stamp": {"text": "허가", "at": "허가를"}}],
   labels=[lab("약 2천억 원", "2천억"), lab("2012년 7월", "2012년", "gold")])
sh("icon", 13, icons=[{"name": "shopping", "text": "명품", "label": "오리지널", "at": "명품"}, {"name": "shopping", "text": "같은 품질", "label": "훨씬 싸게", "at": "훨씬"}])
sh("icon", 14, icons=[{"name": "vial", "label": "살아 있는 세포", "at": "세포로"}, {"name": "warning", "label": "훨씬 어렵다", "at": "어렵습니다"}])
sh("crowd", 15, count=16, emotion="smug", highlight="founder", labels=[lab("다들 안 된다", "안", "red")])
sh("closeup", [16, 17], who="founder", side="left", set="office", time="night", emotion="worried", pose="think",
   bubble={"who": "founder", "text": "?", "at": "실수는", "thought": True}, labels=[lab("가장 비싼 실수?", "실수는", "red", x=1350, y=860, size=110)])
sh("icon", 18, icons=[{"name": "book", "label": "셀트리온 성적표", "at": "성적표를"}], stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("map", 19, tag="2002년", places=[{"name": "서울", "x": 760, "y": 470}, {"name": "인천 송도", "x": 520, "y": 560}], vehicle="car", at="송도에",
   labels=[lab("부지 약 145억 원", "145억", "gold")])
sh("icon", 20, icons=[{"name": "factory", "label": "공장", "at": "하지만", "on": False}, {"name": "calendar", "top": "첫 매출", "text": "2007", "label": "2007년", "at": "2007년이었습니다"}])
sh("closeup", 21, who="mate1", side="right", set="office", time="night", emotion="tired", pose="stressed", labels=[lab("7년 넘게", "7년이", "red")])
sh("closeup", 22, who="founder", side="left", set="office", time="day", emotion="thinking", pose="think",
   bubble={"who": "founder", "text": "상장?", "at": "어떻게", "thought": True})
sh("table", [23, 24], hand="founder", items=[{"type": "contract", "title": "합병 계약", "text": "(구)셀트리온 + 오알켐", "at": "오알켐이라는", "stamp": {"text": "합병", "at": "합쳐지는"}},
                                              {"type": "letter", "title": "오알켐", "text": "회로기판 약품 회사", "at": "회로기판에"}],
   labels=[lab("2008년", "2008년", "gold")])
sh("wide", [25, 26], set="street", time="day", shop="오알켐",
   chars=[ch("founder", 900, "smug", "present", beats=[{"at": "우회상장이라고", "pose": "point", "emotion": "confident"}])],
   labels=[lab("우회상장", "우회상장이라고", "lime", size=140)])
sh("title", None, text="위기", sub="2장", hold=1.6)

# ── 2장 · 위기 ──
sh("crowd", [27, 28], count=20, emotion="thinking", set="street", labels=[lab("정말 팔리는 약?", "의심이었죠", "cream")])
sh("chart", 29, board="chalk", chart={"type": "line", "values": [8, 7, 7.5, 5, 4, 3], "trend": "down", "show_values": False, "title": "공매도가 노리는 것", "at": "공매도가"},
   who="shorty")
sh("icon", 30, icons=[{"name": "money", "label": "빌려서 판다", "at": "빌려"}, {"name": "chart_down", "label": "싸게 사서 갚는다", "at": "싸게"}])
sh("crowd", 31, count=14, emotion="greedy", highlight="shorty", labels=[lab("줄을 섰다", "줄을", "red")])
sh("wide", 32, set="office", era="modern", wall="blue", time="day", tag="2013년 4월 16일",
   chars=[ch("founder", 960, "angry", "explain", talk=False)], labels=[lab("기자회견", "기자회견을", "gold")])
sh("table", 33, hand="founder", items=[{"type": "contract", "title": "지분 전량 매각", "text": "셀트리온 + 계열사 → 다국적 제약사", "at": "지분을", "stamp": {"text": "다 판다", "at": "팔겠다고"}}])
sh("counter", 34, value={"from": 0, "to": 17000, "suffix": "억 원", "at": "가치는"}, caption="팔겠다던 지분 가치 (보도)", icon="moneybag")
sh("closeup", 35, who="shorty", side="right", set="office", time="night", emotion="shocked", pose="facepalm", bubble={"who": "shorty", "text": "?!", "at": "어떻게"})
sh("icon", [36, 37], icons=[{"name": "chart_up", "label": "4/16 +5.06%", "at": "그날"}, {"name": "chart_down", "label": "4/17 약 -13%", "at": "다음"}, {"name": "chart_down", "label": "4/18 -14.6%", "at": "그다음"}],
   labels=[lab("셀트리온 주가 (보도)", "그날", "cream", x=960, y=200)])
sh("counter", 38, value={"from": 0, "to": 25.7, "suffix": "%", "at": "4분의"}, caption="이틀 동안 사라진 주가 (채널 계산)", icon="chart_down")
sh("table", 39, items=[{"type": "contract", "title": "지분 매각", "text": "다국적 제약사", "at": "결국", "stamp": {"text": "취소", "at": "팔리지"}}])
sh("table", 40, items=[{"type": "letter", "title": "금융당국", "text": "조사", "at": "조사를"}])
sh("map", 41, places=[{"name": "한국", "x": 1450, "y": 470}, {"name": "유럽", "x": 820, "y": 380}], vehicle="plane", at="유럽에",
   labels=[lab("2013년 9월 · 유럽 허가", "유럽에", "gold")])
sh("map", 42, places=[{"name": "한국", "x": 1450, "y": 470}, {"name": "미국", "x": 420, "y": 430}], vehicle="plane", at="미국",
   labels=[lab("2016년 4월 · 미국 허가", "2016년", "gold")])
sh("wide", 43, set="office", era="modern", wall="green", time="day",
   chars=[ch("founder", 820, "excited", "celebrate"), ch("mate1", 1220, "happy", "wave")], props=[{"icon": "vial", "x": 1520, "y": 700, "s": .6, "at": "의심받던"}],
   labels=[lab("유럽 + 미국", "유럽과", "lime")])
sh("title", None, text="결정", sub="3장", hold=1.6)

# ── 3장 · 결정 ──
sh("walk", 44, set="street", time="day", tag="2018년 2월 9일", chars=[{"id": "founder", "emotion": "confident", "pose": "hold"}],
   labels=[lab("코스닥 → 코스피", "코스피로", "lime")])
sh("counter", 45, value={"from": 0, "to": 35.3, "suffix": "조 원", "at": "시가총액은"}, caption="코스피 첫날 시가총액 (보도)", icon="chart_up")
sh("list", 46, number=3, text="코스피 3위", who="founder", emotion="excited", badge="gold")
sh("versus", 47, colors=["#E8E0F0", "#D8F0D8"],
   left={"who": "founder", "title": "2008 남의 회사 빌려 상장", "emotion": "nervous", "pose": "hold", "at": "빌려"},
   right={"who": "founder", "title": "2018 코스피 3위", "emotion": "excited", "pose": "celebrate", "at": "3등이"})
sh("icon", 48, icons=[{"name": "trophy", "label": "동네 1등 → 전국 시상대", "at": "시상대에"}])
sh("chart", 49, board="chalk", chart={"type": "bar", "values": [1809, 18491], "labels": ["2010", "2020"], "unit": "", "suffix": "억", "title": "매출 (보도)", "show_values": True, "at": "매출"})
sh("counter", 50, value={"from": 0, "to": 396239, "suffix": "원", "at": "39만"}, caption="2020년 12월 7일 역대 최고 주가 (보도)", icon="trophy")
sh("closeup", 51, who="founder", side="right", set="office", time="dusk", emotion="worried", pose="stressed")
sh("chart", 52, board="white", chart={"type": "line", "values": [39.6, 33, 28, 24, 21, 19.5], "trend": "down", "show_values": False, "title": "2020.12 → 2021.11 주가 반토막", "at": "반토막이"},
   labels=[lab("시총 약 27조 원 증발", "27조", "red")])
sh("table", [53, 54], items=[{"type": "newspaper", "title": "경제신문", "text": "셀트리온 3사 회계 위반", "at": "회계", "ring_at": "어겼다고"}],
   labels=[lab("2022년 3월", "2022년", "gold")])
sh("versus", 55, colors=["#F6C7B6", "#D8F0D8"],
   left={"who": "exec", "title": "고의", "emotion": "angry", "pose": "point", "at": "고의가"},
   right={"who": "founder", "title": "중과실", "emotion": "nervous", "pose": "shrug", "at": "중과실로"})
sh("table", 56, items=[{"type": "receipt", "title": "과징금", "rows": [["셀트리온", "60억"], ["헬스케어", "60.4억"], ["제약", "9.9억"]], "text": "약 139억", "at": "과징금은"}],
   stamp={"text": "거래정지 면함", "at": "가지", "color": "green"})
sh("closeup", [57, 58], who="mate2", side="left", set="office", time="day", emotion="thinking", pose="think",
   bubble={"who": "mate2", "text": "두 회사를 어떻게?", "at": "흩어진", "thought": True})
sh("icon", 59, icons=[{"name": "factory", "label": "셀트리온 · 만든다", "at": "만들고"}, {"name": "shopping", "text": "판매", "label": "헬스케어 · 판다", "at": "팔았습니다"}])
sh("wide", 60, set="home", wall="teal", time="day", chars=[ch("mate1", 700, "smile", "hold"), ch("mate2", 1220, "smile", "present")],
   props=[{"icon": "vial", "x": 960, "y": 700, "s": .5, "at": "물건을"}])
sh("icon", 61, tag="2023년 12월 28일", icons=[{"name": "handshake", "label": "합병", "at": "하나로"}])
sh("wide", 62, set="office", era="modern", wall="cream", time="day",
   chars=[ch("founder", 960, "happy", "present"), ch("mate1", 620, "happy", "wave"), ch("mate2", 1300, "happy", "wave")],
   labels=[lab("한 지붕", "한", "lime")])
sh("chart", 63, board="white", chart={"type": "bar", "values": [97.04, 2.96], "labels": ["찬성", "그 밖"], "suffix": "%", "title": "셀트리온 주주총회 (보도)", "show_values": True, "highlight": 0, "at": "97%가"},
   labels=[lab("1주 → 약 0.45주", "1주는", "gold", x=1300, y=900)])
sh("chart", [64, 65], board="chalk", chart={"type": "bar", "values": [4920, 11685], "labels": ["2024", "2025"], "suffix": "억", "title": "영업이익 (DART)", "show_values": True, "highlight": 1, "at": "2024년"})
sh("icon", 66, icons=[{"name": "trophy", "label": "매출 4조 + 영업이익 1조", "at": "처음으로"}], stamp={"text": "첫 동시 달성", "at": "함께", "color": "green"})
sh("title", None, text="성적표", sub="4장", hold=1.6)

# ── 4장 · 성적표 ──
sh("closeup", [67, 68], who="founder", side="left", set="office", time="night", emotion="nervous", pose="think",
   labels=[lab("가장 비싼 실수", "실수는", "red", x=1350, y=860, size=110)])
sh("icon", 69, icons=[{"name": "syringe", "label": "짐펜트라", "at": "짐펜트라입니다"}], chars=[ch("founder", 1500, "confident", "present")])
sh("versus", 70, colors=["#E0E8F0", "#D8F0D8"],
   left={"who": "patient", "title": "병원 링거", "emotion": "tired", "pose": "idle", "at": "링거"},
   right={"who": "patient", "title": "집에서 피하주사", "emotion": "happy", "pose": "hold", "at": "피하주사로"})
sh("map", 71, places=[{"name": "한국", "x": 1450, "y": 470}, {"name": "미국", "x": 420, "y": 430}], vehicle="ship", at="미국에서",
   labels=[lab("미국 직접 판매", "직접", "lime")])
sh("icon", 72, icons=[{"name": "calendar", "top": "미국 허가", "text": "2023.10", "label": "허가", "at": "허가를"}, {"name": "calendar", "top": "출시", "text": "2024.3", "label": "출시", "at": "출시됩니다"}])
sh("counter", 73, value={"from": 0, "to": 10000, "suffix": "억 원", "at": "목표는"}, caption="짐펜트라 연매출 목표 (보도)", icon="target")
sh("chart", 74, board="white", chart={"type": "bar", "values": [10000, 7000, 3500], "labels": ["처음", "2024.11", "2025.9"], "suffix": "억", "title": "목표가 내려간 순서 (보도)", "show_values": True, "trend": "down", "at": "7천억"})
sh("counter", 75, value={"from": 0, "to": 1222, "suffix": "억 원", "at": "1,222억"}, caption="2025년 짐펜트라 실제 매출 (보도)", icon="syringe",
   compare={"text": "목표의 약 12%", "icon": "target", "at": "+1.8"})
sh("closeup", 76, who="founder", side="right", set="office", time="night", emotion="sad", pose="facepalm", labels=[lab("약 12%", "12%였습니다", "red")])
sh("wide", [77, 78], set="board", time="day", chars=[ch("founder", 600, "neutral", "present")],
   labels=[lab("숫자로만", "숫자로만", "red", x=1250, y=300, size=140), lab("5천만 원 · 6명", "5천만", "cream", x=1250, y=520)])
sh("chart", 79, board="chalk", chart={"type": "bar", "values": [1809, 41625], "labels": ["2010", "2025"], "suffix": "억", "title": "매출 약 23배 (보도·DART)", "show_values": True, "highlight": 1, "at": "2010년"})
sh("chart", [80, 81], board="white", chart={"type": "bar", "values": [4.35, 49.44], "labels": ["2013.4.16", "2026.11.20"], "suffix": "조", "title": "시가총액 약 11배", "show_values": True, "highlight": 1, "at": "지분을"})
sh("table", [82, 83], items=[{"type": "receipt", "title": "잘한 결정", "rows": [["바이오시밀러", "약 2천억"], ["램시마", "2012"]], "text": "세계 최초", "at": "잘한"}],
   stamp={"text": "최고의 결정", "at": "세계", "color": "green"})
sh("table", [84, 85], items=[{"type": "receipt", "title": "비싼 실수", "rows": [["짐펜트라 목표", "1조 원"], ["실제 2025", "1,222억"]], "text": "약 12%", "at": "비싼"}],
   stamp={"text": "가장 비싼 실수", "at": "실제는", "color": "red"})
sh("counter", 86, value={"from": 0, "to": 46, "prefix": "-", "suffix": "%", "at": "46%"}, caption="2020년 고점 대비 지금 주가 (채널 계산)", icon="chart_down")
sh("title", None, text="반전", sub="5장", hold=1.6)

# ── 5장 · 반전 ──
sh("closeup", [87, 88], who="mate2", side="right", set="office", time="day", emotion="thinking", pose="think",
   bubble={"who": "mate2", "text": "지금은 누가?", "at": "누가", "thought": True})
sh("wide", [89, 90], set="office", era="modern", wall="plum", time="day",
   chars=[ch("ki", 720, "confident", "present"), ch("seo", 1220, "confident", "arms_crossed")],
   labels=[lab("각자대표 2명", "두", "lime", x=960, y=230)])
sh("closeup", 91, who="founder", side="left", set="office", time="day", emotion="calm", pose="hips",
   labels=[lab("회장 · 이사", "회장이자", "gold")])
sh("counter", [92, 93], value={"from": 0, "to": 41142, "suffix": "억 원", "at": "매출은"}, caption="2026년 1~9월 매출 (DART)", icon="chart_up",
   compare={"text": "지난해 1년치의 98.8%", "icon": "calendar", "at": "9개월"})
sh("chart", [94, 95], board="white", chart={"type": "line", "values": [251000, 225000, 199700, 213000], "labels": ["2월", "3월", "4월", "11월"], "show_values": False, "title": "2026년 주가 (보도)", "at": "올해"},
   labels=[lab("약 -20%", "20%", "red")])
sh("title", [96, 97], text="팔겠다던 창업주")
sh("map", 98, tag="2025년", places=[{"name": "한국", "x": 1450, "y": 470}, {"name": "미국 뉴저지", "x": 440, "y": 400}], vehicle="plane", at="뉴저지",
   labels=[lab("일라이릴리 공장 인수", "일라이릴리의", "lime")])
sh("table", 99, hand="founder", items=[{"type": "contract", "title": "공장 인수 계약", "text": "일라이릴리 뉴저지 공장", "at": "인수", "stamp": {"text": "인수", "at": "4,600억"}}],
   labels=[lab("약 4,600억 원", "4,600억", "gold")])
sh("icon", 100, icons=[{"name": "factory", "label": "릴리 약 대신 생산", "at": "공장에서"}, {"name": "moneybag", "label": "약 6,787억 원", "at": "6,787억"}])
sh("versus", 101, colors=["#F6C7B6", "#D8F0D8"],
   left={"who": "founder", "title": "2013 팔리겠다", "emotion": "angry", "pose": "explain", "at": "팔리겠다던"},
   right={"who": "founder", "title": "2025 공장을 산다", "emotion": "smug", "pose": "celebrate", "at": "사는"})
sh("chart", [102, 103], board="chalk", chart={"type": "bar", "values": [4, 49], "labels": ["팔겠다던 날", "지금"], "suffix": "조", "title": "시가총액", "show_values": True, "highlight": 1, "at": "팔겠다던"})
sh("wide", [104, 107], set="office", era="modern", wall="sand", time="day",
   chars=[ch("founder", 700, "happy", "wave"), ch("mate1", 1100, "happy", "wave"), ch("mate2", 1450, "smile", "celebrate")],
   labels=[lab("구독 · 좋아요", "구독과", "lime", x=960, y=230, size=130), lab("출처는 설명란", "출처는", "cream", x=960, y=420)],
   polaroid={"at": "출처는", "who": "founder", "caption": "팔겠다던 회사, 사는 회사가 되다"})

story = {
  "title": "셀트리온_v2",
  "mood": "dramatic",
  "cast": {
    "founder": {"skin": "light", "outfit": "suit", "color": "#3B4A63", "shirt": "#F2F2F2", "tie": "#8C2E2E", "hair": "short", "hair_col": "#2A2420"},
    "mate1": {"skin": "fair", "outfit": "sweater", "color": "#5E8C6A", "hair": "curly", "hair_col": "#3A2C22"},
    "mate2": {"skin": "tan", "outfit": "tshirt", "color": "#C9853A", "hair": "slick", "hair_col": "#1E1A18", "glasses": True},
    "exec": {"skin": "light", "outfit": "suit", "color": "#2E2E36", "hair": "bald", "moustache": True},
    "shorty": {"skin": "olive", "outfit": "suit", "color": "#4A3A5A", "hair": "slick", "hat": "fedora", "hat_col": "#2A2230"},
    "patient": {"skin": "fair", "outfit": "hoodie", "color": "#7FA8D8", "hair": "bun", "hair_col": "#4A3428"},
    "ki": {"skin": "light", "outfit": "suit", "color": "#5A6070", "hair": "short", "hair_col": "#9A9A9A", "glasses": True, "tie": "#2E5A8C"},
    "seo": {"skin": "light", "outfit": "suit", "color": "#2F3A55", "hair": "slick", "hair_col": "#1A1614", "tie": "none"}
  },
  "shots": X
}
# 이름표(처음 나올 때)
for d in X:
    if d.get("kind") == "wide" and any(c.get("id") == "ki" for c in d.get("chars", [])):
        d["lower_third"] = {"name": "기우성 · 서진석", "sub": "셀트리온 각자대표 (2026년)", "at": "기우성"}
json.dump(story, open(os.path.join(P, "story.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(X), "shots")
