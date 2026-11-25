#!/usr/bin/env python3
"""고려아연 v2 스토리보드."""
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

# 인트로 · 위기부터: 최대주주+사모펀드 공개매수(보도) → 빚 내 맞불 → 판결·결정 34건 vs 사상 최대 이익 (0초부터 그림·글자)
sh("wide", 0, set="office", era="modern", wall="grey", time="night",
   chars=[ch("yp", 600, "angry", "point"), ch("fund", 960, "confident", "arms_crossed"), ch("choi", 1320, "shocked", "idle")],
   labels=[lab("최대주주 + 사모펀드 · 공개매수 (보도)", "+0.0", "red", x=960, y=240, size=85)])
sh("closeup", 1, who="choi", side="left", set="office", time="night", emotion="angry", pose="point",
   stamp={"text": "맞불 공개매수", "at": "맞불을", "color": "red"}, labels=[lab("빚을 늘려 자기 주식 매수", "빚을", "cream", x=1350, y=860, size=75)])
sh("wide", 2, set="office", era="modern", wall="grey", time="day",
   chars=[ch("yp", 600, "angry", "point"), ch("choi", 1320, "confident", "arms_crossed")],
   labels=[lab("판결·결정 공시 34건", "+0.0", "red", x=960, y=240, size=120)],
   stamp={"text": "34건", "at": "34건입니다", "color": "red"})
sh("closeup", 3, who="worker", side="right", set="office", time="day", emotion="happy", pose="celebrate",
   labels=[lab("창사 이래 최대 영업이익", "창사", "gold", x=600, y=860, size=90)])
sh("versus", 4, colors=["#F6C7B6", "#D8F0D8"], left={"who": "yp", "title": "법정에서는 싸우고", "emotion": "angry", "pose": "point", "at": "+0.2"},
   right={"who": "worker", "title": "공장에서는 돈을 번다", "emotion": "happy", "pose": "celebrate", "at": "공장에서는"})
sh("skyline", 5, time="day", labels=[lab("고려아연", "고려아연입니다", size=180)])
sh("closeup", 6, who="m1", side="right", set="home", time="night", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "무슨 일이?", "at": "+0.2", "thought": True})
OFF = 3
chap("판돈", "1장")
sh("walk", 4, set="street", time="day", tag="1949년", chars=[ch("fchoi", 0, "confident", "idle"), ch("fjang", 0, "happy", "idle")],
   labels=[lab("1949년", "1949년에", "gold", x=960, y=260)])
sh("wide", 5, set="office", era="old", wall="sand", time="day", calendar="1949",
   chars=[ch("fchoi", 700, "happy", "present"), ch("fjang", 1250, "smile", "wave", beats=[{"at": "세웠다고", "pose": "celebrate", "emotion": "excited"}])],
   labels=[lab("두 창업주, 영풍 공동 창업 (보도)", "함께", "gold", x=960, y=250)])
sh("table", 6, hand="fchoi", items=[{"type": "contract", "title": "회사 설립", "text": "고려아연", "at": "+0.2", "stamp": {"text": "1974년 8월", "at": "세워집니다"}}])
sh("icon", 7, icons=[{"name": "car", "label": "철을 덮는 금속", "at": "+0.2"}, {"name": "lock", "label": "녹 방지", "at": "녹슬지"}])
sh("wide", [8, 9], set="office", era="old", wall="cream", time="day", tag="1978년 4월",
   chars=[ch("worker", 700, "excited", "push", beats=[{"at": "돌아갑니다", "pose": "celebrate"}]), ch("fchoi", 1250, "confident", "point")],
   props=[{"icon": "factory", "x": 1500, "y": 520, "s": 0.7, "at": "공장이"}],
   labels=[lab("첫 공장 가동", "공장이", "gold", x=600, y=260), lab("아연 연 5만 톤 (회사)", "5만", "lime", x=1350, y=260)])
sh("chart", 10, board="chalk", chart={"type": "bar", "values": [5, 17], "labels": ["1978년", "1987년"], "suffix": "만 톤", "title": "아연괴 연간 생산 규모 (회사)", "show_values": True, "highlight": 1, "at": "+0.3"})
sh("map", [11, 12], places=[{"name": "한국", "x": 1450, "y": 430}, {"name": "호주 · 썬메탈", "x": 1350, "y": 860}], vehicle="ship", at="+0.3",
   labels=[lab("1996년 호주 법인 (회사)", "1996년에는", "gold"), lab("약 30년 뒤 다시 등장", "30년", "red")])
sh("versus", 13, colors=["#D6E4F0", "#F2E2C4"], left={"who": "fjang", "title": "영풍: 장씨 집안", "emotion": "calm", "pose": "present", "at": "+0.2"},
   right={"who": "fchoi", "title": "고려아연: 최씨 집안", "emotion": "calm", "pose": "present", "at": "고려아연은"})
sh("closeup", [14, 15], who="m1", side="left", set="home", time="night", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "?", "at": "비싼", "thought": True}, labels=[lab("가장 비싼 값?", "비싼", "red", x=1350, y=860, size=110)])
sh("icon", 16, icons=[{"name": "book", "text": "성적표", "label": "끝에 공개", "at": "+0.2"}], stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("title", 17, text="세계 1위 비철금속 제련 기업 (회사 소개)")
sh("icon", 18, icons=[{"name": "coins", "text": "금·은", "label": "귀금속", "at": "+0.2"}, {"name": "factory", "label": "구리", "at": "구리"}, {"name": "vial", "label": "희소금속", "at": "희소금속까지"}])
sh("wide", [19, 20], set="office", era="modern", wall="blue", time="day",
   chars=[ch("choi", 900, "confident", "present", beats=[{"at": "회장에", "pose": "celebrate", "emotion": "smile"}])],
   lower_third={"name": "최윤범", "sub": "고려아연 회장", "at": "+0.3"},
   labels=[lab("2019년 3월 사장", "사장이", "cream", x=1450, y=260), lab("2022년 회장 (보도)", "회장에", "gold", x=1450, y=400)])
sh("table", 21, hand="choi", items=[{"type": "letter", "title": "트로이카 드라이브", "text": "신재생 · 자원순환 · 이차전지 소재", "at": "+0.2", "stamp": {"text": "새 판", "at": "새"}}])
chap("결정", "2장")
sh("skyline", 22, time="dusk", tag="2024년 9월 13일", labels=[lab("판이 뒤집힌다", "뒤집힙니다", "red", size=150)])
sh("wide", 23, set="board", time="day",
   chars=[ch("yp", 650, "confident", "point"), ch("fund", 1250, "smug", "present")],
   labels=[lab("영풍 + MBK파트너스", "MBK파트너스와", "red", x=960, y=240), lab("공개매수 (보도)", "공개매수에", "gold", x=960, y=400)])
sh("counter", [24, 25], value={"from": 556000, "to": 666000, "suffix": "원", "at": "+0.3"}, caption="2024년 9월 12일 → 13일 종가 (네이버)", icon="chart_up",
   compare={"text": "하루 +19.8%", "icon": "warning", "at": "19.8%"})
sh("closeup", [26, 27], who="choi", side="right", set="office", time="night", emotion="angry", pose="arms_crossed",
   beats=[{"at": "사들이는", "pose": "point", "emotion": "confident"}], labels=[lab("맞불: 자사주 공개매수", "맞불이었습니다", "red", x=600, y=860, size=100)])
sh("table", 28, hand="choi", items=[{"type": "contract", "title": "자기주식 공개매수 (DART)", "text": "한 주 83만 원", "at": "+0.2", "stamp": {"text": "2024년 10월 2일", "at": "결정합니다"}}])
sh("closeup", 29, who="m1", side="left", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "그 돈은?", "icon": "moneybag", "at": "돈은"})
sh("counter", 30, value={"from": 0, "to": 27000, "suffix": "억 원", "at": "+0.3"}, caption="같은 날 단기차입금 증가 결정 (DART)", icon="moneybag")
sh("chart", 31, board="white", chart={"type": "bar", "values": [83, 89], "labels": ["10월 2일", "10월 11일"], "suffix": "만 원", "title": "자사주 공개매수 가격 (DART)", "show_values": True, "highlight": 1, "at": "+0.3"})
sh("walk", 32, set="street", time="dusk", tag="2024년 10월 23일", chars=[ch("choi", 0, "tired", "idle")],
   labels=[lab("공개매수 마감", "끝납니다", "gold", x=960, y=260)])
sh("counter", 33, value={"from": 0, "to": 2040030, "suffix": "주", "at": "+0.3"}, caption="고려아연이 사들인 자기 주식 (DART)", icon="coins")
sh("table", [34, 35], hand="choi", items=[{"type": "receipt", "title": "자사주 공개매수 결과 (DART)", "rows": [["매수 가격", "89만 원"], ["주식 수", "204만 30주"], ["비율", "약 9.85%"]], "text": "1조 8,156억 원", "at": "+0.2"}],
   stamp={"text": "전량 소각", "at": "없애기로", "color": "red"})
sh("wide", 36, set="office", era="modern", wall="teal", time="day", tag="2024년 10월 30일",
   chars=[ch("park", 900, "confident", "present")],
   labels=[lab("일반공모 유상증자", "유상증자를", "gold", x=1400, y=260), lab("373만 2,650주 (DART)", "373만", "lime", x=1400, y=400)])
sh("counter", [37, 38], value={"from": 1543000, "to": 1081000, "suffix": "원", "at": "+0.3"}, caption="2024년 10월 29일 → 30일 종가 (네이버)", icon="chart_down",
   compare={"text": "하루 -29.9%", "icon": "warning", "at": "29.9%"})
sh("table", 39, items=[{"type": "newspaper", "title": "2024년 11월 13일", "text": "유상증자 철회 (DART)", "at": "+0.2", "ring_at": "철회합니다"}],
   stamp={"text": "철회", "at": "철회합니다", "color": "red"})
sh("chart", [40, 41], board="chalk", chart={"type": "bar", "values": [24041, 71969], "labels": ["2023년 말", "2024년 말"], "suffix": "억", "title": "연결 부채총계 (DART)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("약 3배", "세", "red")])
chap("위기", "3장")
sh("crowd", [42, 44], count=22, emotion="thinking", set="void", labels=[lab("지금 누가 이기고 있나?", "이기고", "gold", size=110), lab("판단은 엇갈린다", "엇갈리고", "red")])
sh("wide", [45, 46], set="board", time="day", tag="2025년 1월 · 임시주총",
   chars=[ch("yp", 650, "angry", "stressed"), ch("choi", 1250, "calm", "present")],
   labels=[lab("영풍 의결권 제한 (보도)", "제한된", "red", x=960, y=250)])
sh("icon", [47, 48], icons=[{"name": "book", "text": "상법", "label": "상호주 조항", "at": "+0.2"}, {"name": "lock", "label": "10% 넘게 → 의결권 묶임", "at": "넘게"}, {"name": "building", "text": "호주", "label": "호주 자회사 (판결문)", "at": "호주"}])
sh("table", 49, items=[{"type": "contract", "title": "서울중앙지법 가처분 (DART)", "text": "임시주총 결의 일부 효력정지", "at": "+0.2", "stamp": {"text": "2025년 3월 7일", "at": "결정을"}}])
sh("icon", 50, icons=[{"name": "lock", "label": "새 사외이사 7명 직무정지 (DART)", "at": "+0.2"}])
sh("closeup", 51, who="choi", side="left", set="office", time="day", emotion="calm", pose="think",
   labels=[lab("서울고법·대법원에서 일부 바뀜 (DART)", "일부", "cream", x=1350, y=860, size=80)])
sh("wide", [52, 53], set="board", time="day", tag="2025년 3월 28일 · 정기주총",
   chars=[ch("yp", 650, "worried", "point"), ch("choi", 1250, "confident", "arms_crossed")],
   labels=[lab("영풍: 의결권 행사 허용 가처분", "가처분을", "gold", x=960, y=250)])
sh("table", 54, items=[{"type": "newspaper", "title": "대법원 (DART)", "text": "영풍 측 재항고 기각", "at": "+0.2", "ring_at": "기각합니다"}],
   stamp={"text": "2026년 4월 2일", "at": "기각합니다", "color": "green"})
sh("title", 55, text="2026년 11월 12일, 1심은 다른 판단")
sh("table", 56, items=[{"type": "contract", "title": "서울중앙지법 1심 (DART)", "text": "2025년 3월 정기주총 결의 취소", "at": "+0.2", "stamp": {"text": "권리남용", "at": "권리남용이라며"}}])
sh("closeup", [57, 58], who="park", side="right", set="office", time="night", emotion="nervous", pose="present",
   stamp={"text": "항소", "at": "항소했습니다", "color": "red"}, labels=[lab("11월 24일 항소 (DART)", "11월", "cream", x=600, y=860, size=90)])
sh("versus", [59, 60], colors=["#F6C7B6", "#D8F0D8"], left={"who": "yp", "title": "11월 12일 1심: 주총 결의 취소", "emotion": "smile", "pose": "point", "at": "+0.2"},
   right={"who": "choi", "title": "11월 13일 서울고법: 신주 무효 청구 기각", "emotion": "smile", "pose": "present", "at": "서울고법이"})
sh("table", 61, hand="yp", items=[{"type": "letter", "title": "가처분 신청 (2026년 11월 16일)", "text": "대표이사·이사 직무집행정지", "at": "+0.2"}])
sh("closeup", 62, who="m1", side="left", set="home", time="night", emotion="worried", pose="think",
   stamp={"text": "진행 중", "at": "진행", "color": "red"}, labels=[lab("2026년 11월 25일 기준", "기준", "cream", x=1350, y=860, size=90)])
sh("icon", 63, icons=[{"name": "warning", "label": "증선위 회계 제재 (2026년 6월)", "at": "+0.2"}])
sh("counter", 64, value={"from": 0, "to": 84, "suffix": "억 원", "at": "+0.3"}, caption="회사 과징금 확정 (DART, 약 84억 원)", icon="money")
chap("베팅", "4장")
sh("closeup", 65, who="choi", side="left", set="office", time="day", emotion="confident", pose="point",
   labels=[lab("전혀 다른 판", "다른", "gold", x=1350, y=860, size=110)])
sh("map", 66, places=[{"name": "한국", "x": 1600, "y": 470}, {"name": "미국 테네시", "x": 420, "y": 500}], vehicle="plane", at="+0.3",
   labels=[lab("2025년 12월 15일 공시 (DART)", "공시합니다", "gold")])
sh("counter", 67, value={"from": 0, "to": 7432, "suffix": "백만 달러", "at": "+0.3"}, caption="미국 제련소 총 투자 규모 (DART)", icon="factory",
   compare={"text": "우리 돈 약 10.9조 원", "icon": "moneybag", "at": "10.9조"})
sh("icon", [68, 69], icons=[{"name": "factory", "label": "아연 · 납 · 구리", "at": "+0.2"}, {"name": "coins", "text": "금·은", "label": "귀금속", "at": "금과"}, {"name": "calendar", "top": "2027", "text": "~2029", "label": "단계적 건설", "at": "건설은"}])
sh("table", [70, 71], hand="choi", items=[{"type": "contract", "title": "제3자배정 유상증자 (DART)", "text": "220만 9,716주 · 2조 8,508억 원", "at": "+0.2", "stamp": {"text": "미국 합작법인", "at": "배정한"}}])
sh("counter", 72, value={"from": 0, "to": 210, "suffix": "백만 달러", "at": "+0.3"}, caption="미국 상무부 반도체 지원법 보조금 예정 (DART)", icon="moneybag")
sh("closeup", 73, who="yp", side="right", set="office", time="night", emotion="angry", pose="point",
   labels=[lab("신주 발행 금지 가처분", "가처분을", "red", x=600, y=860, size=100)])
sh("table", 74, items=[{"type": "newspaper", "title": "서울중앙지법 (DART)", "text": "신주발행금지 가처분 기각", "at": "+0.2", "ring_at": "기각했고"}],
   stamp={"text": "2025년 12월 24일", "at": "기각했고", "color": "green"})
sh("walk", 75, set="street", time="dusk", chars=[ch("yp", 0, "worried", "idle")],
   labels=[lab("본안 소송: 진행 중", "본안", "red", x=960, y=260), lab("2026년 11월 25일 기준", "기준", "cream", x=960, y=420)])
sh("wide", 76, set="office", era="modern", wall="green", time="day",
   chars=[ch("worker", 700, "excited", "celebrate"), ch("worker2", 1250, "happy", "hold")],
   props=[{"icon": "coins", "x": 960, "y": 700, "s": 0.6, "at": "벌었습니다"}], labels=[lab("그사이 공장은", "공장은", "gold", x=960, y=250)])
sh("chart", [77, 78], board="white", chart={"type": "bar", "values": [120529, 165879], "labels": ["2024년", "2025년"], "suffix": "억", "title": "연결 매출 (DART)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("+37.6%", "37.6%", "green")])
sh("counter", 79, value={"from": 7235, "to": 12319, "suffix": "억 원", "at": "+0.3"}, caption="연결 영업이익 2024년 → 2025년 (DART)", icon="chart_up",
   compare={"text": "+70.3% · 사상 최대", "icon": "trophy", "at": "70.3%"})
sh("icon", 80, icons=[{"name": "coins", "text": "금·은", "label": "귀금속 가격·판매량", "at": "+0.2"}, {"name": "vial", "label": "전략광물", "at": "전략광물의"}])
sh("chart", [81, 82], board="chalk", chart={"type": "line", "values": [556000, 2115000], "labels": ["2024.9.12", "2026.2.25"], "trend": "up", "suffix": "원", "title": "종가 (네이버)", "show_values": True, "at": "+0.3"},
   labels=[lab("약 3.8배", "3.8배입니다", "green")])
chap("성적표", "5장")
sh("closeup", [83, 84], who="m1", side="right", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "지금은?", "at": "얼마일까요", "thought": True})
sh("counter", [85, 86], value={"from": 2115000, "to": 753000, "suffix": "원", "at": "+0.3"}, caption="종가: 2026년 2월 25일 → 11월 25일 (네이버)", icon="chart_down",
   compare={"text": "꼭대기보다 -64.4%", "icon": "warning", "at": "64.4%"})
sh("table", 87, items=[{"type": "newspaper", "title": "한국경제 (2026년 7월)", "text": "3월 은값 급락, 주가도 하락 (보도)", "at": "+0.2", "ring_at": "은값이"}])
sh("chart", [88, 90], board="white", chart={"type": "bar", "values": [2734, 1417], "labels": ["2025년 3분기", "2026년 3분기"], "suffix": "억", "title": "분기 영업이익 (DART)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("-48.2%", "48.2%", "red")])
sh("closeup", 91, who="park", side="left", set="office", time="night", emotion="worried", pose="stressed",
   labels=[lab("금속 가격 · 환율 (회사 설명, 보도)", "환율이", "cream", x=1350, y=860, size=80)])
sh("chart", [92, 93], board="chalk", chart={"type": "bar", "values": [12319, 14748], "labels": ["2025년 한 해", "2026년 1~9월"], "suffix": "억", "title": "연결 영업이익 (DART)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("9개월 만에 넘었다", "넘었습니다", "green")])
sh("icon", 94, icons=[{"name": "book", "text": "성적표", "label": "고려아연 성적표", "at": "+0.2"}], stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("counter", [95, 96], value={"from": 97045, "to": 165879, "suffix": "억 원", "at": "+0.3"}, caption="연결 매출 2023년 → 2025년 (DART)", icon="chart_up",
   compare={"text": "약 +71%", "icon": "trophy", "at": "71%"})
sh("table", [97, 98], items=[{"type": "receipt", "title": "연결 영업이익 (DART)", "rows": [["2023년", "6,599억"], ["2025년", "1조 2,319억"]], "text": "약 +87%", "at": "+0.2"}],
   stamp={"text": "+87%", "at": "87%", "color": "green"})
sh("wide", [99, 100], set="office", era="modern", wall="blue", time="day",
   chars=[ch("choi", 900, "calm", "present", beats=[{"at": "33.5%", "pose": "hips", "emotion": "smile"}])],
   labels=[lab("2022년 말 56만 4천 원", "56만", "cream", x=1450, y=260), lab("지금 75만 3천 원 · +33.5%", "33.5%", "gold", x=1450, y=400)])
sh("counter", 101, value={"from": 0, "to": 157173, "suffix": "억 원", "at": "+0.3"}, caption="시가총액 2026년 11월 25일 (네이버)", icon="building")
sh("wide", [102, 103], set="office", era="modern", wall="green", time="day",
   chars=[ch("choi", 700, "happy", "celebrate"), ch("worker", 1250, "excited", "hold")],
   stamp={"text": "최고의 결정: 아연 밖으로", "at": "나간", "color": "green"})
sh("closeup", 104, who="choi", side="right", set="office", time="night", emotion="sad", pose="facepalm",
   stamp={"text": "가장 비싼 값: 분쟁", "at": "분쟁입니다", "color": "red"})
sh("versus", [105, 107], colors=["#F6C7B6", "#E6DDF2"], left={"who": "choi", "title": "자사주 공개매수 1조 8,156억 · 부채 약 3배", "emotion": "worried", "pose": "stressed", "at": "+0.2"},
   right={"who": "yp", "title": "영풍·MBK 측도 큰돈 (보도)", "emotion": "worried", "pose": "stressed", "at": "영풍과"})
sh("table", [108, 109], hand="park", items=[{"type": "receipt", "title": "주주환원 (DART)", "rows": [["2025년 결산 배당", "주당 2만 원"], ["2026년 11월 4일", "자사주 소각 결정"]], "text": "24만 6,665주", "at": "+0.2"}],
   stamp={"text": "소각", "at": "없애기로", "color": "green"})
chap("반전", "6장")
sh("walk", 110, set="street", time="dusk", chars=[ch("m1", 0, "calm", "idle")], labels=[lab("처음 그 숫자", "숫자의", "gold", x=960, y=260)])
sh("crowd", [111, 112], count=24, emotion="shocked", set="void",
   labels=[lab("판결·결정 34건", "34건", "red", size=110), lab("사상 최대 이익 · 주가 약 3분의 1", "꼭대기의", "gold")])
sh("table", 113, items=[{"type": "newspaper", "title": "남은 다툼", "text": "항소심 · 가처분 · 본안 소송", "at": "+0.2", "ring_at": "남아"}],
   stamp={"text": "진행 중", "at": "남아", "color": "red"})
sh("versus", 114, colors=["#D6E4F0", "#F2E2C4"], left={"who": "fjang", "title": "1949년: 함께 시작", "emotion": "happy", "pose": "wave", "at": "+0.2"},
   right={"who": "yp", "title": "지금: 법원에서", "emotion": "worried", "pose": "arms_crossed", "at": "법원에서"})
sh("title", [115, 116], text="녹슬고 있는 건 금속이 아니라, 70년 넘은 동업")
sh("wide", [117, 120], set="office", era="modern", wall="blue", time="day",
   chars=[ch("fchoi", 600, "happy", "wave"), ch("m1", 960, "happy", "wave"), ch("fjang", 1320, "smile", "celebrate")],
   labels=[lab("구독 · 좋아요", "구독과", "lime", x=960, y=230, size=130), lab("출처는 설명란", "출처는", "cream", x=960, y=420)],
   polaroid={"at": "출처는", "who": "fchoi", "caption": "아연은 녹을 막는다. 동업은?"})

# 빈 화면 방지(2026-11-20 검수): 그래픽 장면의 첫 요소는 장면 시작 직후에 나오게 하고, 나머지만 대사 낱말에 맞춘다
for d in X:
    k = d.get("kind")
    if k == "icon" and d.get("icons"): d["icons"][0]["at"] = "+0.2"
    if k == "table" and d.get("items"): d["items"][0]["at"] = "+0.2"
    if k == "chart" and d.get("chart"): d["chart"]["at"] = "+0.3"
    if k == "counter" and d.get("value"): d["value"]["at"] = "+0.3"

story = {"title": "고려아연_v2", "mood": "dramatic", "cast": {
    "fchoi": {"skin": "light", "outfit": "suit", "color": "#3E4A3A", "shirt": "#F2F2F2", "tie": "#1271BB", "hair": "short", "hair_col": "#8A8A8A"},
    "fjang": {"skin": "tan", "outfit": "suit", "color": "#5C3A2E", "shirt": "#F2F2F2", "tie": "#B8862E", "hair": "bald", "glasses": True},
    "choi": {"skin": "fair", "outfit": "suit", "color": "#1F2E5C", "shirt": "#F2F2F2", "tie": "#1E973A", "hair": "slick", "hair_col": "#2A2420", "glasses": True},
    "park": {"skin": "light", "outfit": "suit", "color": "#5A5A64", "shirt": "#F2F2F2", "tie": "none", "hair": "short", "hair_col": "#3A3A3A"},
    "yp": {"skin": "olive", "outfit": "suit", "color": "#2E2E36", "shirt": "#F2F2F2", "tie": "#C8242C", "hair": "short", "hair_col": "#1E1A18"},
    "fund": {"skin": "fair", "outfit": "suit", "color": "#4A2E5C", "shirt": "#F2F2F2", "tie": "#E28207", "hair": "curly", "hair_col": "#3A2C22"},
    "m1": {"skin": "fair", "outfit": "sweater", "color": "#5E8C6A", "hair": "curly", "hair_col": "#3A2C22"},
    "worker": {"skin": "light", "outfit": "tshirt", "color": "#F2C94C", "hair": "short", "hair_col": "#2A2420", "hat": "cap", "hat_col": "#F2F2F2"},
    "worker2": {"skin": "brown", "outfit": "tshirt", "color": "#4C8CF2", "hair": "short", "hair_col": "#1E1A18", "hat": "cap", "hat_col": "#E28207"}},
  "shots": X}
for d in X:
    if d.get("kind") == "walk":
        for c in d.get("chars", []): c.pop("x", None)
json.dump(story, open(os.path.join(P, "story.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(X), "shots")
