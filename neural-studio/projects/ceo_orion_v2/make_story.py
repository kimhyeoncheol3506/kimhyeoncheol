#!/usr/bin/env python3
"""오리온 v2 스토리보드."""
import json, os
P = os.path.dirname(os.path.abspath(__file__)); X = []
def sh(kind, s, **k):
    d = {"kind": kind}
    if s is not None: d["s"] = s if isinstance(s, list) else [s]
    d.update(k); X.append(d)
def lab(text, at, color="lime", **k): return dict(text=text, at=at, color=color, **k)
def ch(id, x, emotion="neutral", pose="idle", **k): return dict(id=id, x=x, emotion=emotion, pose=pose, **k)
def chap(t, n): sh("title", None, text=t, sub=n, hold=1.6)

# 인트로 · 50원 과자의 역설
sh("icon", 0, tag="1974년", icons=[{"name": "shopping", "text": "초코파이", "label": "한 개 50원", "at": "50원짜리"}])
sh("counter", 1, value={"from": 0, "to": 67, "suffix": "%", "at": "67%를"}, caption="2025년 해외 매출 비중 (DART 지역 매출로 계산)", icon="chart_up")
sh("table", 2, hand="founder2", items=[{"type": "cash", "text": "5,485억 원", "at": "5,485억"}], stamp={"text": "과자 공장 아님", "at": "아니었습니다", "color": "red"})
sh("skyline", 3, time="day", labels=[lab("오리온", "오리온입니다", size=180)])
chap("판돈", "1장")
sh("wide", [4, 5], set="office", era="old", wall="sand", time="day", tag="1956년 · 서울", calendar="1956 7",
   chars=[ch("founder", 900, "confident", "present", beats=[{"at": "세웁니다", "pose": "celebrate", "emotion": "excited"}])],
   lower_third={"name": "이양구", "sub": "동양제과 창업주", "at": "이양구는"}, labels=[lab("풍국제과 인수 → 동양제과", "풍국제과라는", "gold", x=1350, y=260)])
sh("table", 6, hand="founder", items=[{"type": "contract", "title": "신제품 출시", "text": "초코파이", "at": "+0.2", "stamp": {"text": "1974년 4월", "at": "초코파이를"}}])
sh("closeup", 7, who="founder", side="left", set="office", time="day", emotion="excited", pose="think",
   bubble={"who": "founder", "text": "이 과자다!", "icon": "bulb", "at": "아이디어를"}, labels=[lab("미국 출장길 (일화)", "미국", "cream", x=1350, y=860)])
sh("icon", 8, icons=[{"name": "shopping", "text": "초코파이", "label": "초콜릿 + 빵 과자", "at": "초콜릿을"}, {"name": "coins", "label": "한 개 50원", "at": "50원이었습니다"}])
sh("counter", 9, value={"from": 0, "to": 500, "suffix": "억 개", "at": "500억"}, caption="초코파이 누적 판매 (2025년 보도)", icon="shopping",
   compare={"text": "누적 매출 8조 원", "icon": "moneybag", "at": "8조"})
sh("closeup", [10, 11], who="m1", side="left", set="home", time="night", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "?", "at": "실수는", "thought": True}, labels=[lab("가장 비싼 실수?", "실수는", "red", x=1350, y=860, size=110)])
sh("icon", 12, icons=[{"name": "book", "text": "성적표", "label": "끝에 공개", "at": "성적표를"}], stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("wide", 13, set="home", time="dusk", tag="1989년", chars=[ch("elder", 700, "sad", "idle"), ch("founder2", 1200, "sad", "idle")],
   props=[{"icon": "calendar", "x": 960, "y": 380, "s": .55, "at": "+0.3"}])
sh("versus", 14, colors=["#D9D9E6", "#F6E0B6"], left={"who": "elder", "title": "맏사위 · 동양그룹", "emotion": "calm", "pose": "present", "at": "그룹은"},
   right={"who": "founder2", "title": "둘째 사위 · 과자", "emotion": "confident", "pose": "hold", "at": "사위가"})
sh("wide", 15, set="office", era="modern", wall="plum", time="day", chars=[ch("founder2", 900, "confident", "present")],
   props=[{"icon": "shopping", "x": 1450, "y": 690, "s": .6, "at": "과자"}],
   lower_third={"name": "담철곤", "sub": "오리온 회장", "at": "담철곤이었습니다"})
sh("closeup", 16, who="lee", side="right", set="office", time="day", emotion="smile", pose="present",
   lower_third={"name": "이화경", "sub": "오리온 부회장 · 창업주 둘째 딸", "at": "이화경은"})
sh("table", 17, items=[{"type": "contract", "title": "상호 변경", "text": "동양제과 → 오리온", "at": "+0.2", "stamp": {"text": "2003년 8월", "at": "2003년"}}])
sh("versus", 18, colors=["#E0E0F0", "#F6D0C0"], left={"who": "m2", "title": "오리온홀딩스 · 지주회사", "emotion": "calm", "pose": "present", "at": "지주회사"},
   right={"who": "founder2", "title": "오리온 · 사업회사", "emotion": "happy", "pose": "point", "at": "사업회사"},
   labels=[lab("2017년 6월 분할", "2017년", "gold", x=960, y=900)])
sh("closeup", 19, who="founder2", side="right", set="office", time="day", emotion="smile", pose="present_left", labels=[lab("오늘의 주인공 = 사업회사 오리온", "사업회사입니다", "lime", x=600, y=860, size=80)])
chap("결정", "2장")
sh("map", [20, 21], places=[{"name": "서울", "x": 1250, "y": 560}, {"name": "베이징", "x": 760, "y": 380}], vehicle="plane", at="베이징에",
   labels=[lab("1993년 베이징 사무소", "1993년", "gold"), lab("한중 수교 다음 해", "수교", "cream")])
sh("wide", [22, 23], set="street", time="day", shop="중국 공장", tag="1997년 · 중국",
   chars=[ch("founder2", 760, "excited", "push", beats=[{"at": "부엌을", "pose": "celebrate", "emotion": "happy"}])],
   props=[{"icon": "factory", "x": 1400, "y": 690, "s": .7, "at": "공장을"}], labels=[lab("현지에 부엌", "부엌을", "lime", x=1350, y=260)])
sh("icon", 24, icons=[{"name": "building", "label": "상하이", "at": "상하이"}, {"name": "building", "label": "광저우", "at": "광저우"}, {"name": "building", "label": "선양", "at": "선양에도"}])
sh("counter", 25, value={"from": 0, "to": 5400, "suffix": "여 명", "at": "5,400여"}, caption="중국 법인 직원 · 공장 6개 (2024년 보도)", icon="factory",
   compare={"text": "그중 한국인 18명", "icon": "heart", "at": "18명뿐이었습니다"})
sh("map", 26, places=[{"name": "한국", "x": 1450, "y": 560}, {"name": "러시아", "x": 520, "y": 340}], vehicle="ship", at="러시아에도",
   labels=[lab("1993년 초코파이 수출", "1993년", "cream")])
sh("wide", 27, set="street", time="day", shop="트베리 공장", tag="2006년 · 러시아", chars=[ch("founder2", 700, "excited", "push")],
   props=[{"icon": "factory", "x": 1250, "y": 690, "s": .6, "at": "트베리에"}, {"icon": "factory", "x": 1600, "y": 690, "s": .55, "at": "노보"}],
   labels=[lab("2006 트베리", "트베리에", "gold", x=1250, y=300), lab("2008 노보", "노보", "gold", x=1600, y=420)])
sh("icon", [28, 29], tag="2005년 · 베트남", icons=[{"name": "handshake", "label": "2005년 법인", "at": "법인을"}, {"name": "factory", "label": "호찌민", "at": "호찌민과"}, {"name": "factory", "label": "하노이", "at": "하노이에"}])
sh("closeup", [30, 31], who="m1", side="right", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "어느 나라?", "at": "나라는", "thought": True})
sh("title", 32, text="한국이 아닙니다")
sh("chart", 33, board="white", chart={"type": "bar", "values": [10967, 13164], "labels": ["한국", "중국"], "suffix": "억 원", "title": "2025년 지역별 매출 (DART)", "show_values": True, "highlight": 1, "at": "중국"},
   labels=[lab("중국이 더 크다", "한국", "red")])
sh("closeup", 34, who="m1", side="left", set="home", time="day", emotion="shocked", pose="facepalm", labels=[lab("중국에서 20% 더", "20%", "red", x=1350, y=860, size=110)])
sh("counter", 35, value={"from": 0, "to": 19.2, "suffix": "%", "at": "19.2%였다고"}, caption="2024년 중국 법인 영업이익률 (보도)", icon="trophy",
   compare={"text": "5년 연속 매출 1조 원", "icon": "chart_up", "at": "5년"})
chap("위기", "3장")
sh("closeup", 36, who="founder2", side="left", set="office", time="dusk", emotion="worried", pose="think")
sh("chart", 37, board="chalk", chart={"type": "bar", "values": [23863, 13467], "labels": ["전체 매출", "중국"], "suffix": "억 원", "title": "2016년 매출 (DART)", "show_values": True, "highlight": 1, "at": "중국이"},
   labels=[lab("중국 1조 3,467억 원", "1조", "gold")])
sh("icon", 38, icons=[{"name": "target", "text": "56%", "label": "매출의 56%가 한 나라", "at": "56%가"}, {"name": "warning", "label": "한 바구니", "at": "나라에서"}])
sh("wide", 39, set="street", time="night", shop="마트", tag="2017년 · 중국",
   chars=[ch("shopper", 700, "angry", "arms_crossed"), ch("shopper2", 1150, "angry", "point")],
   props=[{"icon": "warning", "x": 1550, "y": 640, "s": .6, "at": "진열대가"}],
   stamp={"text": "사드 보복", "at": "사드", "color": "red"})
sh("table", 40, items=[{"type": "newspaper", "title": "중국 매장 (보도)", "text": "진열대 ↓ · 반품 · 불매", "at": "+0.2", "ring_at": "불매가"}])
sh("chart", 41, board="white", chart={"type": "line", "values": [5, 4.4, 3.6, 3.3], "trend": "down", "show_values": False, "title": "2017년 중국 법인 매출 (현지 화폐)", "at": "중국"},
   labels=[lab("중국 -33.2%", "33.2%", "red")])
sh("counter", 42, value={"from": 0, "to": 1648, "suffix": "억 원", "at": "1,648억"}, caption="2017년 그룹 영업이익 (보도)", icon="chart_down",
   compare={"text": "1년 전보다 -49.5%", "icon": "warning", "at": "49.5%"})
sh("closeup", 43, who="founder2", side="left", set="office", time="night", emotion="shocked", pose="stressed", stamp={"text": "거의 반토막", "at": "반토막입니다", "color": "red"})
sh("wide", [44, 45], set="board", time="day",
   chars=[ch("founder2", 700, "confident", "arms_crossed", beats=[{"at": "남되", "pose": "point", "emotion": "confident"}, {"at": "바구니를", "pose": "celebrate", "emotion": "excited"}])],
   props=[{"icon": "gift", "x": 1350, "y": 700, "s": .55, "at": "바구니를"}, {"icon": "gift", "x": 1600, "y": 700, "s": .55, "at": "키우는"}],
   labels=[lab("짐은 안 싼다", "짐을", "cream", x=1350, y=260), lab("다른 바구니", "바구니를", "lime", x=1400, y=420)])
sh("chart", 46, board="chalk", chart={"type": "bar", "values": [13.3, 13.5], "labels": ["베트남", "러시아"], "suffix": "%", "title": "2017년 매출 증가율 (보도)", "show_values": True, "highlight": 1, "at": "베트남"})
sh("counter", [47, 48], value={"from": 890, "to": 3394, "suffix": "억 원", "at": "3,394억"}, caption="러시아 법인 매출 2020년 → 2025년 (보도·DART)", icon="chart_up",
   compare={"text": "1년 새 +47%", "icon": "trophy", "at": "47%"})
sh("crowd", 49, count=24, emotion="happy", set="street", labels=[lab("러시아 초코파이 2,170억 원", "2,170억", "gold", size=110)])
sh("chart", 50, board="chalk", chart={"type": "bar", "values": [40, 16], "labels": ["해외 전체", "러시아"], "suffix": "억 개", "title": "2024년 초코파이 해외 판매 (보도)", "show_values": True, "highlight": 1, "at": "40억"})
sh("icon", 51, icons=[{"name": "factory", "text": "베트남", "label": "2025년 매출 5,381억 원", "at": "5,381억"}])
sh("chart", 52, board="white", chart={"type": "bar", "values": [13467, 13164], "labels": ["2016년", "2025년"], "suffix": "억 원", "title": "중국 매출 (DART)", "show_values": True, "highlight": 1, "at": "중국"},
   labels=[lab("거의 돌아왔다", "거의", "lime")])
sh("wide", [53, 54], set="street", time="day", shop="새 공장",
   chars=[ch("ceo", 520, "excited", "present")],
   props=[{"icon": "factory", "x": 900, "y": 700, "s": .55, "at": "진천"}, {"icon": "factory", "x": 1250, "y": 700, "s": .55, "at": "트베리"}, {"icon": "factory", "x": 1600, "y": 700, "s": .55, "at": "하노이"}],
   labels=[lab("진천 4,600억", "진천", "gold", x=900, y=330, size=70), lab("트베리 2,400억", "트베리", "gold", x=1250, y=230, size=70), lab("하노이 1,300억", "하노이", "gold", x=1600, y=330, size=70)])
chap("베팅", "4장")
sh("closeup", 55, who="founder2", side="right", set="office", time="night", emotion="confident", pose="hips",
   bubble={"who": "founder2", "text": "다른 판", "icon": "target", "at": "다른"})
sh("table", [56, 57], hand="founder2", items=[{"type": "contract", "title": "지분 인수 계약", "text": "리가켐바이오사이언스 25.73%", "at": "+0.2", "stamp": {"text": "5,485억 원", "at": "5,485억"}}],
   labels=[lab("2024년 3월", "리가켐바이오사이언스의", "gold")])
sh("versus", 58, colors=["#F6E0B6", "#C9E8E4"], left={"who": "founder2", "title": "과자 회사", "emotion": "happy", "pose": "hold", "at": "과자"},
   right={"who": "sci", "title": "신약 개발 회사", "emotion": "smile", "pose": "present", "at": "신약을"},
   labels=[lab("최대주주", "최대주주가", "red", x=960, y=900)])
sh("counter", 59, value={"from": 0, "to": 110, "suffix": "억 개", "at": "110억"}, caption="5,485억 원 ÷ 1974년 초코파이 값 50원 (계산)", icon="shopping")
sh("icon", 60, icons=[{"name": "vial", "label": "2026년 7월 추가 투자", "at": "전환우선주와"}, {"name": "moneybag", "label": "1,250억 원", "at": "1,250억"}])
sh("wide", 61, set="office", era="modern", wall="teal", time="night", chars=[ch("sci", 800, "nervous", "stressed")],
   props=[{"icon": "hourglass", "x": 1350, "y": 690, "s": .55, "at": "시간이"}, {"icon": "syringe", "x": 1600, "y": 690, "s": .5, "at": "신약"}],
   labels=[lab("오래 걸린다", "오래", "cream", x=1450, y=260)])
sh("counter", 62, value={"from": 0, "to": 1598, "suffix": "억 원", "at": "1,598억"}, caption="리가켐바이오 2026년 1~9월 영업손실 (보도)", icon="chart_down")
sh("chart", [63, 64], board="chalk", chart={"type": "bar", "values": [213500, 51700], "labels": ["2026년 3월", "2026.11.20"], "suffix": "원", "title": "리가켐바이오 주가 (보도·네이버)", "show_values": True, "highlight": 1, "at": "21만"})
sh("counter", 65, value={"from": 0, "to": 4841, "suffix": "억 원", "at": "4,841억"}, caption="오리온 보유 보통주 시가 (11월 20일 종가로 계산)", icon="chart_down")
sh("chart", 66, board="white", chart={"type": "bar", "values": [5485, 4841], "labels": ["처음 낸 돈", "지금 가치"], "suffix": "억 원", "title": "리가켐 지분 (DART·계산)", "show_values": True, "highlight": 1, "at": "5,485억"},
   labels=[lab("약 -644억 원", "644억", "red")])
sh("closeup", [67, 68], who="founder2", side="left", set="office", time="day", emotion="calm", pose="arms_crossed",
   labels=[lab("아직 안 팔았다", "팔지", "cream", x=1350, y=300), lab("확정 손실 아님", "확정된", "lime", x=1350, y=860)])
chap("성적표", "5장")
sh("closeup", [69, 70], who="m1", side="right", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "지금은 누가?", "at": "누가", "thought": True})
sh("wide", 71, set="office", era="modern", wall="green", time="day",
   chars=[ch("founder2", 700, "calm", "present"), ch("lee", 1150, "smile", "idle")],
   labels=[lab("미등기 임원 · 경영 총괄", "미등기", "cream", x=930, y=250)])
sh("closeup", 72, who="heo", side="right", set="office", time="day", emotion="confident", pose="present",
   lower_third={"name": "허인철", "sub": "오리온 부회장 · 사내이사", "at": "허인철"})
sh("wide", 73, set="office", era="modern", wall="blue", time="day",
   chars=[ch("ceo", 900, "confident", "present")],
   lower_third={"name": "이승준", "sub": "오리온 대표이사 (2022년 3월~)", "at": "이승준"})
sh("closeup", 74, who="m2", side="left", set="office", time="day", emotion="calm", pose="present",
   lower_third={"name": "이경재", "sub": "앞선 대표이사 · 베트남 법인장 출신", "at": "이경재는"})
sh("icon", 75, icons=[{"name": "vial", "label": "2009년~ 중국 법인 연구소장", "at": "연구소장을"}, {"name": "brain", "label": "글로벌 연구소장", "at": "글로벌"}],
   labels=[lab("연구원 출신 대표", "연구원", "lime")])
sh("icon", [76, 77], icons=[{"name": "book", "text": "성적표", "label": "오리온 성적표", "at": "성적표를"}, {"name": "coins", "label": "시작은 50원", "at": "50원짜리"}],
   stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("counter", 78, value={"from": 0, "to": 33324, "suffix": "억 원", "at": "3조"}, caption="2025년 매출 (DART)", icon="trophy",
   compare={"text": "1년 새 +7.3%", "icon": "chart_up", "at": "7.3%"})
sh("counter", 79, value={"from": 0, "to": 5583, "suffix": "억 원", "at": "5,583억"}, caption="2025년 영업이익 (DART)", icon="coins",
   compare={"text": "영업이익률 16.8%", "icon": "target", "at": "16.8%가"})
sh("chart", 80, board="white", chart={"type": "bar", "values": [67, 69.5], "labels": ["2025년", "2026년 1~9월"], "suffix": "%", "title": "해외 매출 비중 (DART로 계산)", "show_values": True, "highlight": 1, "at": "2025년"})
sh("table", [81, 82], items=[{"type": "receipt", "title": "잘한 결정", "rows": [["1993년", "베이징 사무소"], ["2025년 중국", "1조3,164억"]], "text": "한국보다 +20%", "at": "+0.2"}],
   stamp={"text": "최고의 결정", "at": "1조", "color": "green"})
sh("closeup", 83, who="founder2", side="left", set="office", time="day", emotion="excited", pose="celebrate", labels=[lab("한국보다 +20%", "20%", "lime", x=1350, y=860, size=110)])
sh("table", [84, 85], items=[{"type": "receipt", "title": "비싼 실수 (진행 중)", "rows": [["넣은 돈", "5,485억"], ["지금 가치", "약 4,841억"]], "text": "약 -644억 (미실현)", "at": "+0.2"}],
   stamp={"text": "가장 비싼 실수", "at": "644억", "color": "red"})
sh("chart", [86, 87], board="chalk", chart={"type": "bar", "values": [158000, 116500], "labels": ["2020.8.14", "2026.11.20"], "suffix": "원", "title": "오리온 주가 (종가)", "show_values": True, "highlight": 1, "at": "2020년"},
   labels=[lab("약 -26%", "26%", "red")])
sh("counter", 88, value={"from": 0, "to": 46051, "suffix": "억 원", "at": "4조"}, caption="오리온 시가총액 (2026년 11월 20일)", icon="building")
chap("반전", "6장")
sh("closeup", 89, who="m1", side="left", set="home", time="dusk", emotion="calm", pose="explain")
sh("chart", [90, 91], board="white", chart={"type": "bar", "values": [11.3, 9.4], "labels": ["매출", "영업이익"], "suffix": "%", "title": "2026년 3분기 증가율 (보도)", "show_values": True, "highlight": 0, "at": "매출은"},
   labels=[lab("과자 장사는 잘됐다", "잘됐습니다", "lime")])
sh("versus", [92, 93], colors=["#D8F0D8", "#F6C7B6"], left={"who": "founder2", "title": "영업이익 +9.4%", "emotion": "happy", "pose": "celebrate", "at": "+0.2"},
   right={"who": "sci", "title": "순이익 -44.8%", "emotion": "shocked", "pose": "facepalm", "at": "순이익은"},
   labels=[lab("바이오 관련 손실 약 344억 원", "344억", "red", x=960, y=900)])
sh("counter", 94, value={"from": 0, "to": 23, "suffix": "%", "at": "23%에"}, caption="3분기 영업이익 대비 바이오 관련 손실 (보도)", icon="warning")
sh("walk", [95, 96], set="street", time="dusk", chars=[ch("founder2", 0, "confident", "hold")],
   labels=[lab("다시 중국에서 가장 많이", "중국에서", "lime", x=960, y=250), lab("50년, 국경을 넘어", "국경을", "gold", x=960, y=400)])
sh("title", [97, 98], text="숙제는 과자가 아니라, 약")
sh("wide", [99, 102], set="office", era="modern", wall="sand", time="day",
   chars=[ch("founder2", 600, "happy", "wave"), ch("m1", 960, "happy", "wave"), ch("ceo", 1320, "smile", "celebrate")],
   labels=[lab("구독 · 좋아요", "구독과", "lime", x=960, y=230, size=130), lab("출처는 설명란", "출처는", "cream", x=960, y=420)],
   polaroid={"at": "출처는", "who": "founder2", "caption": "50원 과자로 번 돈, 이제 약에 걸었다"})

# 빈 화면 방지(2026-11-20 검수): 그래픽 장면의 첫 요소는 장면 시작 직후에 나오게 하고, 나머지만 대사 낱말에 맞춘다
for d in X:
    k = d.get("kind")
    if k == "icon" and d.get("icons"): d["icons"][0]["at"] = "+0.2"
    if k == "table" and d.get("items"): d["items"][0]["at"] = "+0.2"
    if k == "chart" and d.get("chart"): d["chart"]["at"] = "+0.3"
    if k == "counter" and d.get("value"): d["value"]["at"] = "+0.3"

story = {"title": "오리온_v2", "mood": "upbeat", "cast": {
    "founder": {"skin": "tan", "outfit": "suit", "color": "#4A3A2E", "shirt": "#F2F2F2", "tie": "#B8862E", "hair": "slick", "hair_col": "#2A2420"},
    "founder2": {"skin": "light", "outfit": "suit", "color": "#2E4A8C", "shirt": "#F2F2F2", "tie": "#C8242C", "hair": "short", "hair_col": "#2A2A2A", "glasses": True},
    "lee": {"skin": "fair", "outfit": "dress", "color": "#9C4A7A", "hair": "bun", "hair_col": "#2A2420"},
    "elder": {"skin": "light", "outfit": "suit", "color": "#3A3A44", "hair": "short", "hair_col": "#5A5A5A", "moustache": True},
    "m1": {"skin": "fair", "outfit": "sweater", "color": "#5E8C6A", "hair": "curly", "hair_col": "#3A2C22"},
    "m2": {"skin": "olive", "outfit": "suit", "color": "#6A6A78", "tie": "#2E2E36", "hair": "bald"},
    "heo": {"skin": "light", "outfit": "suit", "color": "#1F2A3A", "tie": "#7A1E2E", "hair": "short", "hair_col": "#8A8A8A"},
    "ceo": {"skin": "tan", "outfit": "suit", "color": "#2F5A4A", "shirt": "#F2F2F2", "tie": "none", "hair": "short", "hair_col": "#6A6A6A", "glasses": True},
    "sci": {"skin": "light", "outfit": "hoodie", "color": "#F2F2F2", "hair": "long", "hair_col": "#3A2C22", "glasses": True},
    "shopper": {"skin": "fair", "outfit": "tshirt", "color": "#D0703A", "hair": "short", "hair_col": "#1E1A18"},
    "shopper2": {"skin": "fair", "outfit": "sweater", "color": "#8C5EA0", "hair": "long", "hair_col": "#2A2420"}},
  "shots": X}
for d in X:
    if d.get("kind") == "walk":
        for c in d.get("chars", []): c.pop("x", None)
json.dump(story, open(os.path.join(P, "story.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(X), "shots")
