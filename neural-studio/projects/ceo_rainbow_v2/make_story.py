#!/usr/bin/env python3
"""레인보우로보틱스 v2 스토리보드."""
import json, os
P = os.path.dirname(os.path.abspath(__file__)); X = []
def sh(kind, s, **k):
    d = {"kind": kind}
    if s is not None: d["s"] = s if isinstance(s, list) else [s]
    d.update(k); X.append(d)
def lab(text, at, color="lime", **k): return dict(text=text, at=at, color=color, **k)
def ch(id, x, emotion="neutral", pose="idle", **k): return dict(id=id, x=x, emotion=emotion, pose=pose, **k)
def chap(t, n): sh("title", None, text=t, sub=n, hold=1.6)

# 인트로 · 매출 341억, 몸값 8조 (첫 장면은 세트·인물·글자가 0프레임부터 보이는 world 샷)
sh("wide", 0, set="board", time="day", tag="2026년 11월",
   chars=[ch("m1", 700, "shocked", "point", beats=[{"at": "몸값이", "pose": "facepalm", "emotion": "shocked"}]), ch("lee", 1250, "smile", "present")],
   labels=[lab("매출 341억", "+0", "gold", x=1350, y=230, size=110), lab("몸값 8조+", "8조", "red", x=1350, y=400, size=120)])
sh("versus", 1, colors=["#D9D9E6", "#D8F0D8"], left={"who": "sam", "title": "삼성전자가 쓴 돈 3,542억", "emotion": "calm", "pose": "hold", "at": "+0.2"},
   right={"who": "sam", "title": "지금 지분 3조 원+", "emotion": "excited", "pose": "celebrate", "at": "3조"})
sh("skyline", [2, 3], time="day", tag="대전 · 카이스트", labels=[lab("두 발 로봇 한 대", "두", "cream", size=100), lab("레인보우로보틱스", "레인보우로보틱스입니다", size=140)])
chap("판돈", "1장")
sh("wide", [4, 5], set="office", era="old", wall="green", time="day", tag="2004년 · 카이스트 연구실", calendar="2004",
   chars=[ch("oh", 800, "confident", "present", beats=[{"at": "휴보를", "pose": "celebrate", "emotion": "excited"}])],
   props=[{"icon": "laptop", "x": 1500, "y": 760, "s": 0.7, "at": "기계공학과"}],
   lower_third={"name": "오준호", "sub": "카이스트 기계공학과 교수 · 휴보 개발", "at": "오준호"},
   labels=[lab("인간형 로봇 휴보", "휴보를", "gold", x=1350, y=260)])
sh("closeup", 6, who="lee", side="right", set="office", time="day", emotion="smile", pose="hips",
   lower_third={"name": "이정호", "sub": "오 교수의 제자 · 현 대표이사", "at": "이정호라고"}, labels=[lab("(보도)", "보도됐습니다", "cream", x=600, y=860)])
sh("table", [7, 8], hand="oh", items=[{"type": "contract", "title": "주식회사 레인보우 설립", "text": "2011년 2월 10일 · 대전", "at": "+0.2", "stamp": {"text": "설립", "at": "세웁니다"}}],
   labels=[lab("처음 이름: 레인보우", "레인보우였습니다", "gold")])
sh("versus", [9, 10], colors=["#F6E0B6", "#BFD9F2"], left={"who": "oh", "title": "첫 대표 오준호", "emotion": "smile", "pose": "present", "at": "+0.2"},
   right={"who": "lee", "title": "2013년~ 대표 이정호", "emotion": "confident", "pose": "hips", "at": "제자"})
sh("map", [11, 12], places=[{"name": "대전", "x": 1450, "y": 470}, {"name": "미국", "x": 450, "y": 520}], vehicle="plane", at="+0.3",
   labels=[lab("연구용 휴보", "연구용", "gold"), lab("휴보 투 수출 (회사 연혁)", "수출했다고", "lime")])
sh("icon", 13, icons=[{"name": "warning", "label": "연구용 로봇은 잘 안 팔린다", "at": "+0.2"}])
sh("closeup", [14, 16], who="m1", side="left", set="home", time="night", emotion="thinking", pose="think",
   beats=[{"who": "m1", "at": "성적표를", "pose": "point", "emotion": "confident"}], bubble={"who": "m1", "text": "?", "at": "연구실", "thought": True},
   labels=[lab("연구실 회사 → 몸값 8조?", "8조", "red", x=1350, y=860, size=95)])
chap("결정", "2장")
sh("wide", [17, 18], set="street", time="day", shop="다르파 재난 로봇 대회", tag="미국",
   chars=[ch("oh", 700, "confident", "hold"), ch("lee", 1150, "excited", "present", beats=[{"at": "다르파가", "pose": "point"}])],
   labels=[lab("첫 번째 판: 미국", "첫", "gold", x=1450, y=250)])
sh("icon", 19, icons=[{"name": "car", "label": "운전", "at": "+0.2"}, {"name": "target", "label": "밸브 돌리기", "at": "밸브를"}, {"name": "house", "label": "계단 오르기", "at": "계단을"}])
sh("crowd", 20, count=24, emotion="excited", set="street", tag="2015년 6월 · 결선",
   labels=[lab("팀 카이스트 휴보 우승", "우승합니다", "gold", size=110)])
sh("counter", 21, value={"from": 0, "to": 44, "suffix": "분 28초", "at": "+0.3"}, caption="과제 8개 완주 기록 (보도)", icon="clock")
sh("chart", [22, 23], board="chalk", chart={"type": "bar", "values": [200, 100], "labels": ["1위 팀 카이스트", "2위 미국 팀"], "suffix": "만 달러", "title": "결선 상금 (보도)", "show_values": True, "highlight": 0, "at": "+0.3"},
   labels=[lab("2배", "두", "gold")])
sh("closeup", 24, who="oh", side="right", set="office", time="night", emotion="thinking", pose="think",
   labels=[lab("트로피 ≠ 매출", "매출표에", "red", x=600, y=860, size=110)])
sh("wide", [25, 26], set="office", era="modern", wall="blue", time="day",
   chars=[ch("lee", 760, "confident", "present", beats=[{"at": "협동로봇을", "pose": "point", "emotion": "excited"}])],
   props=[{"icon": "factory", "x": 1450, "y": 760, "s": 0.8, "at": "공장이었습니다"}],
   labels=[lab("두 번째 판: 공장", "공장이었습니다", "gold", x=1350, y=250), lab("협동로봇", "협동로봇을", "lime", x=1350, y=420)])
sh("table", [27, 28], items=[{"type": "receipt", "title": "벤처캐피털 투자 (2017년 7월)", "rows": [["투자사", "3곳"], ["규모", "100억 원 (회사)"]], "text": "투자 유치", "at": "+0.2"}],
   stamp={"text": "100억", "at": "100억", "color": "green"})
sh("icon", [29, 30], icons=[{"name": "book", "text": "사명", "label": "2018년 4월 레인보우로보틱스", "at": "+0.2"}, {"name": "laptop", "text": "RB", "label": "2019년 7월 협동로봇 RB 시리즈", "at": "협동로봇"}])
sh("closeup", 31, who="lee", side="left", set="office", time="day", emotion="confident", pose="explain",
   labels=[lab("부품·소프트웨어 직접 (공시)", "부품과", "lime", x=1350, y=860, size=85)])
sh("wide", [32, 33], set="street", time="day", shop="코스닥 상장", tag="2021년 2월 3일",
   chars=[ch("oh", 650, "happy", "wave"), ch("lee", 1150, "excited", "celebrate", beats=[{"at": "기술특례", "pose": "point"}])],
   labels=[lab("기술특례 상장", "기술특례", "gold", x=960, y=230)])
sh("chart", [34, 35], board="white", chart={"type": "bar", "values": [7000, 9000, 10000], "labels": ["희망 하단", "희망 상단", "확정 공모가"], "suffix": "원", "title": "공모가 (DART)", "show_values": True, "highlight": 2, "at": "+0.3"},
   labels=[lab("가격대보다 높게", "높게", "green")])
sh("counter", 36, value={"from": 10000, "to": 26000, "suffix": "원", "at": "+0.3"}, caption="상장 첫날 종가 (네이버)", icon="chart_up",
   compare={"text": "공모가의 2.6배", "icon": "trophy", "at": "공모가의"})
sh("table", [37, 38], items=[{"type": "receipt", "title": "2021년 실적 (DART)", "rows": [["매출", "89억 7천만 원"], ["영업손실", "10억 3천만 원"]], "text": "적자", "at": "+0.2"}])
sh("counter", [39, 40], value={"from": 0, "to": 13, "suffix": "억 원", "at": "+0.3", "color": "green"}, caption="2022년 영업이익 (DART)", icon="chart_up",
   compare={"text": "매출 136억 · 흑자 전환", "icon": "trophy", "at": "흑자로"})
sh("table", [41, 42], hand="lee", items=[{"type": "contract", "title": "제3자배정 유상증자", "text": "대상: 삼성전자 한 곳", "at": "+0.2", "stamp": {"text": "2023.1.3", "at": "결정합니다"}}],
   labels=[lab("세 번째 판: 주주", "주주였습니다", "gold")])
sh("icon", 43, icons=[{"name": "book", "text": "1편", "label": "삼성 이야기는 1편에서", "at": "+0.2"}, {"name": "target", "label": "오늘은 로봇 쪽만", "at": "로봇"}])
sh("counter", [44, 45], value={"from": 0, "to": 590, "suffix": "억 원", "at": "+0.3"}, caption="삼성전자 유상증자 (DART)", icon="moneybag",
   compare={"text": "194만 200주 × 3만 400원", "icon": "coins", "at": "한"})
sh("chart", 46, board="chalk", chart={"type": "bar", "values": [32600, 41550], "labels": ["2023.1.2", "2023.1.3"], "suffix": "원", "title": "종가 (네이버)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("+27.5%", "27.5%", "green")])
sh("wide", [47, 48], set="board", time="day", tag="2023년 3월 15일",
   chars=[ch("sam", 700, "confident", "present", beats=[{"at": "삽니다", "pose": "hold", "emotion": "smug"}]), ch("oh", 1250, "smile", "idle")],
   lower_third={"name": "삼성전자", "sub": "레인보우로보틱스 주주 (2023년~)", "at": "삼성전자는"},
   labels=[lab("누적 약 868억 · 약 15%", "868억", "gold", x=960, y=230)])
sh("table", [49, 50], hand="sam", items=[{"type": "contract", "title": "주주간계약 (2023.3.15)", "text": "콜옵션: 정한 산식 값으로 사 갈 권리", "at": "+0.2", "ring_at": "콜옵션입니다"}],
   stamp={"text": "콜옵션", "at": "콜옵션입니다", "color": "red"})
sh("closeup", [51, 52], who="sam", side="right", set="office", time="day", emotion="smug", pose="hold",
   beats=[{"who": "sam", "at": "의무는", "pose": "shrug", "emotion": "calm"}],
   bubble={"who": "sam", "text": "살 권리", "at": "권리입니다"}, stamp={"text": "권리 · 의무 아님", "at": "의무는", "color": "red", "x": 600})
sh("chart", [53, 54], board="white", chart={"type": "bar", "values": [30400, 86400], "labels": ["삼성전자 매입가", "2023.3.15 종가"], "suffix": "원", "title": "한 주 값 (DART·네이버)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("2.8배", "삼성전자가", "gold")])
chap("위기", "3장")
sh("closeup", [55, 56], who="m1", side="right", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "장부에는?", "at": "장부에는", "thought": True})
sh("counter", [57, 59], value={"from": 0, "to": 445.9, "suffix": "억 원", "at": "+0.3", "color": "red"}, caption="2023년 영업손실 (DART)", icon="chart_down",
   compare={"text": "매출 152억의 약 3배", "icon": "warning", "at": "세"})
sh("table", [60, 61], items=[{"type": "newspaper", "title": "손익구조 변동 공시 (DART)", "text": "전환사채 콜옵션 배정 → 회계상 비용", "at": "+0.2", "stamp": {"text": "현금 유출 없음", "at": "현금이"}}])
sh("chart", [62, 63], board="chalk", chart={"type": "bar", "values": [136, 153, 193], "labels": ["2022년", "2023년", "2024년"], "suffix": "억", "title": "매출 (DART 연결)", "show_values": True, "highlight": 2, "at": "+0.3"},
   labels=[lab("장사도 쉽지 않았다", "장사", "cream")])
sh("closeup", [64, 65], who="lee", side="left", set="office", time="night", emotion="worried", pose="stressed",
   labels=[lab("2024년 영업손실 29억 8천만", "영업손실은", "red", x=1350, y=760, size=80), lab("흑자 복귀 X", "흑자로", "cream", x=1350, y=900, size=80)])
sh("walk", [66, 67], set="street", time="day", chars=[ch("lee", 0, "confident", "idle")],
   labels=[lab("네 발 로봇", "네", "gold", x=600, y=260), lab("핵심 부품 100% 직접 (공시)", "핵심", "lime", x=1350, y=260)])
sh("icon", [68, 69], icons=[{"name": "laptop", "text": "RB-Y1", "label": "2024년 8월 모바일 휴머노이드", "at": "+0.2"}, {"name": "gift", "label": "바퀴 + 두 팔", "at": "두"}])
chap("베팅", "4장")
sh("closeup", [70, 71], who="m1", side="left", set="home", time="night", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "콜옵션 언제?", "at": "콜옵션은", "thought": True})
sh("table", [72, 73], hand="sam", items=[{"type": "contract", "title": "콜옵션 행사 · 주식양수도", "text": "삼성전자 ← 창업자들", "at": "+0.2"}],
   stamp={"text": "2024.12.31", "at": "행사했다고", "color": "red"})
sh("wide", [74, 75], set="office", era="modern", wall="grey", time="dusk",
   chars=[ch("oh", 960, "calm", "wave", beats=[{"at": "물러납니다", "pose": "tiphat"}], exit="right")],
   lower_third={"name": "오준호", "sub": "삼성전자 미래로봇추진단장 (삼성전자 발표)", "at": "단장을"},
   labels=[lab("이사 사임", "물러납니다", "cream", x=1350, y=250)])
sh("counter", [76, 77], value={"from": 0, "to": 2674, "suffix": "억 원", "at": "+0.3"}, caption="콜옵션 양수도 대금 (DART)", icon="moneybag",
   compare={"text": "393만 5,814주", "icon": "coins", "at": "대금은"})
sh("table", [78, 79], items=[{"type": "receipt", "title": "1주당 가액 (DART)", "rows": [["가중평균", "6만 7,956원"], ["정한 방법", "2023년 계약 산식"]], "text": "콜옵션 단가", "at": "+0.2"}])
sh("chart", [80, 82], board="white", chart={"type": "bar", "values": [162700, 211500], "labels": ["2024.12.30", "2025.1.2"], "suffix": "원", "title": "종가 (네이버)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("+30%", "30%", "green")])
sh("wide", [83, 85], set="board", time="day", tag="2025년 3월 12일",
   chars=[ch("sam", 760, "happy", "present", beats=[{"at": "최대주주는", "pose": "celebrate", "emotion": "excited"}]), ch("lee", 1250, "smile", "idle")],
   stamp={"text": "최대주주 삼성전자 35%", "at": "35%입니다", "color": "red"})
sh("icon", [86, 87], icons=[{"name": "coins", "label": "대금 전액 자기 돈 (공시)", "at": "+0.2"}, {"name": "lock", "label": "남은 주식도 콜옵션 가능", "at": "남은"}])
sh("closeup", 88, who="sam", side="left", set="office", time="day", emotion="confident", pose="present",
   labels=[lab("삼성전자 출신 재무 책임자 (공시)", "재무", "lime", x=1350, y=860, size=80)])
sh("versus", 89, colors=["#D9D9E6", "#F6C7B6"], left={"who": "sam", "title": "삼성전자 AI 기술", "emotion": "confident", "pose": "present", "at": "+0.2"},
   right={"who": "lee", "title": "레인보우 로봇 기술", "emotion": "excited", "pose": "present", "at": "로봇"},
   labels=[lab("휴머노이드 개발 앞당기기", "휴머노이드", "gold", x=960, y=900, size=70)])
sh("wide", 90, set="board", time="day", tag="2026년 7월",
   chars=[ch("sam", 700, "happy", "present", beats=[{"at": "함께", "pose": "celebrate"}]), ch("lee", 1250, "excited", "wave")],
   props=[{"icon": "handshake", "x": 960, "y": 700, "s": 0.7, "at": "함께"}],
   labels=[lab("로봇 공동 개발 (보도)", "개발한다고", "lime", x=960, y=230)])
sh("closeup", 91, who="m1", side="right", set="home", time="day", emotion="excited", pose="point",
   labels=[lab("주가는 더 달렸다", "달렸습니다", "green", x=600, y=860, size=110)])
sh("counter", [92, 94], value={"from": 10000, "to": 880000, "suffix": "원", "at": "+0.3", "color": "green"}, caption="2026.2.26 종가 · 상장 뒤 최고 (네이버)", icon="chart_up",
   compare={"text": "공모가의 88배 · 시총 약 17조", "icon": "trophy", "at": "88배입니다"})
chap("성적표", "5장")
sh("icon", 95, icons=[{"name": "book", "text": "성적표", "label": "레인보우로보틱스 성적표", "at": "+0.2"}], stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("chart", [96, 98], board="chalk", chart={"type": "bar", "values": [193, 341], "labels": ["2024년", "2025년"], "suffix": "억", "title": "매출 (DART 연결)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("+76.4%", "76.4%", "green"), lab("영업손실 24억 8천만", "영업손실은", "red")])
sh("versus", [99, 101], colors=["#D8F0D8", "#F6C7B6"], left={"who": "lee", "title": "2026년 1~9월 매출 약 353억", "emotion": "happy", "pose": "celebrate", "at": "+0.2"},
   right={"who": "lee", "title": "영업손실 53억 7천만", "emotion": "worried", "pose": "stressed", "at": "영업손실은"},
   labels=[lab("작년 한 해치 돌파", "아홉", "gold", x=960, y=900, size=80)])
sh("chart", [102, 104], board="white", chart={"type": "bar", "values": [880000, 451500], "labels": ["2026.2.26", "2026.11.24"], "suffix": "원", "title": "종가 (네이버)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("-48.7%", "48.7%", "red")])
sh("counter", [105, 106], value={"from": 0, "to": 87590, "suffix": "억 원", "at": "+0.3"}, caption="시가총액 (2026.11.24 종가, 계산)", icon="building",
   compare={"text": "한 해 매출의 250배+", "icon": "warning", "at": "250배가"})
sh("table", [107, 109], hand="oh", items=[{"type": "receipt", "title": "오준호 성적표", "rows": [["2004년", "휴보"], ["2015년", "세계 대회 우승"], ["2025년", "최대주주 → 삼성전자"]], "text": "창업 교수", "at": "+0.2"}],
   stamp={"text": "최대주주 이전", "at": "넘어갔습니다", "color": "red"})
sh("chart", [110, 112], board="chalk", who="lee", chart={"type": "bar", "values": [54, 341], "labels": ["2020년", "2025년"], "suffix": "억", "title": "이정호 대표 · 매출 (DART)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("6배+", "여섯", "green")])
sh("closeup", 113, who="lee", side="right", set="office", time="night", emotion="thinking", pose="arms_crossed",
   labels=[lab("영업 흑자: 2022년 한 번", "흑자는", "red", x=600, y=860, size=90)])
sh("wide", 114, set="board", time="day",
   chars=[ch("lee", 700, "confident", "present", beats=[{"at": "들인", "pose": "point"}]), ch("sam", 1250, "smile", "idle")],
   stamp={"text": "최고의 결정", "at": "결정은", "color": "green"})
sh("counter", [115, 117], value={"from": 3542, "to": 30657, "suffix": "억 원", "at": "+0.3", "color": "green"}, caption="삼성전자 투자 합계 → 지분 가치 (11.24 종가, 계산)", icon="moneybag",
   compare={"text": "아직 안 판 계산상 숫자", "icon": "hourglass", "at": "아직"})
sh("closeup", [118, 119], who="m1", side="left", set="home", time="night", emotion="sad", pose="facepalm",
   stamp={"text": "-445억 9천만", "at": "영업손실", "color": "red"}, labels=[lab("가장 비싼 숫자", "비싼", "cream", x=1350, y=860)])
chap("반전", "6장")
sh("skyline", 120, time="dusk", tag="대전")
sh("wide", [121, 122], set="office", era="old", wall="green", time="day", tag="2004년 → 2015년",
   chars=[ch("oh", 900, "happy", "present", beats=[{"at": "상금을", "pose": "celebrate", "emotion": "excited"}])],
   labels=[lab("첫걸음", "첫걸음을", "gold", x=1400, y=260), lab("200만 달러", "200만", "lime", x=1400, y=430)])
sh("versus", [123, 124], colors=["#D9D9E6", "#F6E0B6"], left={"who": "sam", "title": "최대주주 삼성전자", "emotion": "confident", "pose": "arms_crossed", "at": "+0.2"},
   right={"who": "oh", "title": "창업 교수 → 삼성 로봇 조직 (보도)", "emotion": "calm", "pose": "present", "at": "교수는"})
sh("chart", 125, board="white", chart={"type": "bar", "values": [341, 87590], "labels": ["2025년 매출", "시가총액"], "suffix": "억", "title": "매출 vs 몸값", "show_values": True, "highlight": 1, "at": "+0.3"})
sh("title", 126, text="숙제: 잘 걷는 로봇 → 돈 버는 로봇")
sh("wide", [127, 130], set="office", era="modern", wall="blue", time="day",
   chars=[ch("oh", 600, "happy", "wave"), ch("m1", 960, "happy", "wave"), ch("lee", 1320, "smile", "celebrate")],
   labels=[lab("구독 · 좋아요", "구독과", "lime", x=960, y=230, size=130), lab("출처는 설명란", "출처는", "cream", x=960, y=420)],
   polaroid={"at": "출처는", "who": "lee", "caption": "걷는 로봇에서 버는 로봇으로"})

# 빈 화면 방지: 그래픽 장면의 첫 요소는 장면 시작 직후에 나오게 하고, 나머지만 대사 낱말에 맞춘다
for d in X:
    k = d.get("kind")
    if k == "icon" and d.get("icons"): d["icons"][0]["at"] = "+0.2"
    if k == "table" and d.get("items"): d["items"][0]["at"] = "+0.2"
    if k == "chart" and d.get("chart"): d["chart"]["at"] = "+0.3"
    if k == "counter" and d.get("value"): d["value"]["at"] = "+0.3"

story = {"title": "레인보우로보틱스_v2", "mood": "upbeat", "cast": {
    "oh": {"skin": "light", "outfit": "sweater", "color": "#7A5A3A", "hair": "short", "hair_col": "#B8B8B8", "glasses": True},
    "lee": {"skin": "fair", "outfit": "suit", "color": "#2E3A5C", "shirt": "#F2F2F2", "tie": "#DC3D31", "hair": "short", "hair_col": "#2A2420"},
    "sam": {"skin": "tan", "outfit": "suit", "color": "#1F2A5A", "shirt": "#F2F2F2", "tie": "#2E6FB8", "hair": "slick", "hair_col": "#2A2420"},
    "m1": {"skin": "fair", "outfit": "hoodie", "color": "#5E8C6A", "hair": "curly", "hair_col": "#3A2C22"}},
  "shots": X}
for d in X:
    if d.get("kind") == "walk":
        for c in d.get("chars", []): c.pop("x", None)
json.dump(story, open(os.path.join(P, "story.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(X), "shots")
