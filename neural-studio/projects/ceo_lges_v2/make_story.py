#!/usr/bin/env python3
"""LG에너지솔루션 v2 스토리보드."""
import json, os
P = os.path.dirname(os.path.abspath(__file__)); X = []
def sh(kind, s, **k):
    d = {"kind": kind}
    if s is not None: d["s"] = s if isinstance(s, list) else [s]
    d.update(k); X.append(d)
def lab(text, at, color="lime", **k): return dict(text=text, at=at, color=color, **k)
def ch(id, x, emotion="neutral", pose="idle", **k): return dict(id=id, x=x, emotion=emotion, pose=pose, **k)
def chap(t, n): sh("title", None, text=t, sub=n, hold=1.6)

# 인트로 · 114조가 몰린 공모주의 역설
sh("counter", 0, value={"from": 0, "to": 114, "suffix": "조 원", "at": "114조"}, caption="2022년 1월 공모주 청약 증거금 (보도)", icon="moneybag")
sh("table", 1, items=[{"type": "newspaper", "title": "증시 새 역사 (보도)", "text": "청약 증거금 사상 최대", "at": "+0.2", "ring_at": "가장"}],
   stamp={"text": "당시 역대 최대", "at": "증거금이었습니다", "color": "red"})
sh("closeup", 2, who="m1", side="left", set="home", time="night", emotion="shocked", pose="facepalm",
   labels=[lab("4년 10개월 뒤", "4년", "cream", x=1350, y=300), lab("공모가보다 싸다", "쌉니다", "red", x=1350, y=860, size=110)])
sh("skyline", 3, time="day", labels=[lab("LG에너지솔루션", "LG에너지솔루션입니다", size=150)])
chap("판돈", "1장")
sh("wide", 4, set="street", time="dusk", shop="연구 단지", tag="1992년 · 영국 출장길",
   chars=[ch("koo", 820, "calm", "hold", walk=[300, 900])])
sh("closeup", 5, who="koo", side="left", set="street", time="dusk", emotion="thinking", pose="think",
   beats=[{"who": "koo", "at": "처음", "pose": "point", "emotion": "shocked"}],
   lower_third={"name": "구본무", "sub": "당시 LG그룹 부회장", "at": "구본무는"},
   labels=[lab("충전해서 다시 쓰는 전지", "충전해서", "gold", x=1350, y=300)])
sh("icon", 6, icons=[{"name": "warning", "label": "쓰고 버리는 건전지", "at": "쓰고"}, {"name": "bulb", "label": "다시 채우는 전지", "at": "채우는"}])
sh("closeup", 7, who="koo", side="left", set="office", era="old", time="day", emotion="excited", pose="present",
   bubble={"who": "koo", "text": "여기에 건다", "icon": "target", "at": "투자하기로"}, labels=[lab("(전해지는 이야기)", "전해집니다", "cream", x=1350, y=860)])
sh("table", [8, 9], items=[{"type": "receipt", "title": "회사 연혁 (공식)", "rows": [["1992년", "연구 착수"], ["1996년", "개발 시작"]], "text": "리튬이온 배터리", "at": "+0.2"}])
sh("wide", [10, 11], set="office", era="old", wall="teal", time="day", tag="1999년 · 한국",
   chars=[ch("sci", 760, "excited", "hold", beats=[{"at": "양산에", "pose": "celebrate", "emotion": "happy"}])],
   props=[{"icon": "factory", "x": 1350, "y": 690, "s": .6, "at": "원통형"}, {"icon": "building", "x": 1620, "y": 690, "s": .5, "at": "미국에"}],
   labels=[lab("1999 원통형 양산", "원통형", "gold", x=1350, y=280), lab("2000 미국 연구법인", "미국에", "cream", x=1450, y=430)])
sh("closeup", [12, 13], who="m1", side="left", set="home", time="night", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "?", "at": "실수는", "thought": True}, labels=[lab("가장 비싼 실수?", "실수는", "red", x=1350, y=860, size=110)])
sh("icon", 14, icons=[{"name": "book", "text": "성적표", "label": "끝에 공개", "at": "성적표를"}], stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("closeup", 15, who="sci", side="right", set="office", era="old", time="night", emotion="sad", pose="stressed",
   labels=[lab("돈이 안 된다", "벌어", "red", x=600, y=860, size=110)])
sh("counter", 16, value={"from": 0, "to": 2000, "suffix": "억 원", "at": "2,000억"}, caption="2005년 2차전지 사업 적자, 2,000억 원에 가까움 (보도)", icon="chart_down",
   compare={"text": "돈 안 되는 배터리", "icon": "warning", "at": "적자를"})
sh("wide", 17, set="board", time="night",
   chars=[ch("m2", 650, "angry", "point"), ch("exec2", 1250, "worried", "arms_crossed")],
   bubble={"who": "m2", "text": "접읍시다", "at": "접자는"}, labels=[lab("사업 접자? (보도)", "의견까지", "red", x=960, y=230)])
sh("closeup", [18, 19], who="koo", side="right", set="office", era="old", time="night", emotion="confident", pose="point",
   bubble={"who": "koo", "text": "끈질기게 하면 꼭 성과가 나온다", "at": "끈질기게"}, labels=[lab("(보도된 발언)", "전해집니다", "cream", x=600, y=860)])
sh("table", [20, 21], hand="koo", items=[{"type": "contract", "title": "배터리 사업", "text": "연구개발 계속", "at": "+0.2", "stamp": {"text": "접지 않는다", "at": "대신"}}],
   labels=[lab("판돈을 더 얹다", "얹은", "gold")])
chap("결정", "2장")
sh("map", [22, 23], places=[{"name": "한국", "x": 1450, "y": 560}, {"name": "미국 GM", "x": 520, "y": 420}], vehicle="ship", at="GM의",
   labels=[lab("2009년 GM 볼트", "2009년", "gold"), lab("전기차 배터리 공급", "배터리를", "cream")])
sh("icon", 24, icons=[{"name": "car", "label": "양산형 전기차 배터리", "at": "양산형"}, {"name": "trophy", "label": "세계 최초 (회사 기록)", "at": "세계"}])
sh("closeup", 25, who="sci", side="right", set="office", era="modern", time="day", emotion="excited", pose="celebrate",
   labels=[lab("휴대폰 → 자동차", "자동차를", "lime", x=600, y=860, size=100)])
sh("map", 26, places=[{"name": "난징", "x": 1350, "y": 520}, {"name": "미국", "x": 380, "y": 430}, {"name": "폴란드", "x": 860, "y": 330}], vehicle="plane", at="중국",
   labels=[lab("2004 난징 · 2012 미국 · 2017 폴란드", "폴란드에", "gold", size=70)])
sh("table", [27, 28], items=[{"type": "contract", "title": "LG화학 이사회", "text": "배터리 사업 분할", "at": "+0.2", "stamp": {"text": "2020년 9월 결의", "at": "결의합니다"}}])
sh("versus", [29, 30], colors=["#E6D9D9", "#F6C7B6"], left={"who": "m2", "title": "LG화학", "emotion": "confident", "pose": "hold", "at": "방식이었습니다"},
   right={"who": "sci", "title": "배터리 회사 (100% 자회사)", "emotion": "calm", "pose": "present", "at": "자회사로"},
   labels=[lab("물적분할", "물적분할이었습니다", "red", x=960, y=900)])
sh("crowd", [31, 32], count=22, emotion="angry", set="street",
   labels=[lab("개인 투자자 반발", "반발했습니다", "red", size=110), lab("국민연금도 반대 (보도)", "국민연금도", "cream")])
sh("wide", [33, 34], set="office", era="modern", wall="sand", time="day", tag="2020년 12월 1일",
   chars=[ch("kim1", 900, "confident", "present", beats=[{"at": "출범합니다", "pose": "celebrate", "emotion": "excited"}])],
   stamp={"text": "분할안 통과", "at": "통과됩니다", "color": "green"}, labels=[lab("LG에너지솔루션 출범", "출범합니다", "lime", x=1400, y=260)])
sh("closeup", [35, 36], who="m1", side="right", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "얼마일까?", "at": "얼마로", "thought": True})
sh("counter", 37, value={"from": 0, "to": 5203, "prefix": "1경 ", "suffix": "조 원", "at": "1경"}, caption="2022년 1월 기관 수요예측 주문 (LG 발표)", icon="coins")
sh("crowd", 38, count=26, emotion="excited", set="void", labels=[lab("경쟁률 2,023 대 1", "경쟁률은", "gold", size=120)])
sh("icon", [39, 40], icons=[{"name": "coins", "label": "공모가 30만 원", "at": "30만"}, {"name": "moneybag", "label": "공모 규모 12조 7,500억 원", "at": "12조"}])
sh("counter", 41, value={"from": 0, "to": 1141066, "suffix": "억 원", "at": "114조"}, caption="일반 청약 증거금 (보도)", icon="moneybag")
sh("table", 42, items=[{"type": "newspaper", "title": "청약 증거금 (보도)", "text": "그전 최고 80조 9,017억 원", "at": "+0.2", "stamp": {"text": "기록 경신", "at": "훌쩍"}}])
sh("chart", [43, 44], board="chalk", chart={"type": "bar", "values": [300000, 505000], "labels": ["공모가", "첫날 종가"], "suffix": "원", "title": "2022년 1월 27일 상장 (네이버)", "show_values": True, "highlight": 1, "at": "종가는"},
   labels=[lab("시총 약 118조 원", "118조", "gold")])
chap("위기", "3장")
sh("versus", [45, 46], colors=["#F2D6DC", "#D9E2F2"], left={"who": "lgc", "title": "LG화학", "emotion": "angry", "pose": "arms_crossed", "at": "두"},
   right={"who": "rival", "title": "같은 한국 배터리 회사", "emotion": "nervous", "pose": "shrug", "at": "같은"},
   labels=[lab("첫 번째 싸움", "첫", "red", x=960, y=900)])
sh("table", 47, hand="lgc", items=[{"type": "letter", "title": "미국 국제무역위원회 제소", "text": "상대: SK이노베이션 · 영업비밀 침해", "at": "+0.2", "stamp": {"text": "2019년 4월 29일", "at": "제소합니다"}}])
sh("closeup", 48, who="lgc", side="left", set="office", era="modern", time="night", emotion="angry", pose="point",
   bubble={"who": "lgc", "text": "영업비밀 침해!", "at": "영업비밀을"})
sh("wide", 49, set="board", time="day", tag="2021년 2월 10일 · 미국",
   chars=[ch("judge", 960, "calm", "explain", beats=[{"at": "최종", "pose": "point", "emotion": "confident"}])],
   stamp={"text": "침해 인정", "at": "인정하는", "color": "red"})
sh("icon", 50, icons=[{"name": "lock", "label": "SK이노 부품·소재", "at": "+0.2"}, {"name": "calendar", "text": "10년", "label": "미국 수입금지 (보도)", "at": "수입금지를"}])
sh("table", [51, 52], hand="rival", items=[{"type": "receipt", "title": "합의 (2021년 4월)", "rows": [["현금", "1조 원"], ["로열티", "1조 원"]], "text": "현재가치 총 2조 원", "at": "+0.2"}],
   stamp={"text": "총 2조 원", "at": "2조", "color": "green"})
sh("closeup", [53, 54], who="lgc", side="left", set="office", era="modern", time="day", emotion="smug", pose="hips",
   labels=[lab("소송 모두 취하", "취하하고", "cream", x=1350, y=300), lab("10년간 안 다툰다", "다투지", "lime", x=1350, y=860)])
sh("wide", [55, 56], set="street", time="night", shop="GM 볼트", tag="2021년 · 미국",
   chars=[ch("driver", 700, "shocked", "stressed")],
   props=[{"icon": "car", "x": 1300, "y": 700, "s": .6, "at": "볼트에서"}, {"icon": "warning", "x": 1600, "y": 600, "s": .55, "at": "화재가"}],
   labels=[lab("두 번째 싸움 = 안에서", "안에", "red", x=1350, y=260)])
sh("table", 57, items=[{"type": "newspaper", "title": "GM 발표 (2021.10.12)", "text": "LG와 리콜 비용 합의", "at": "+0.2", "ring_at": "합의를"}])
sh("counter", 58, value={"from": 0, "to": 19, "suffix": "억 달러", "at": "19억"}, caption="GM 볼트 리콜 비용 중 LG 부담 최대 (GM 발표)", icon="car",
   compare={"text": "전체 리콜 비용 약 20억 달러", "icon": "warning", "at": "20억"})
sh("chart", 59, board="white", chart={"type": "bar", "values": [910, 6200], "labels": ["2021년 2분기", "3분기"], "suffix": "억 원", "title": "리콜 충당금 (보도)", "show_values": True, "highlight": 1, "at": "910억"})
sh("wide", [60, 61], set="office", era="modern", wall="grey", time="day", tag="2021년 11월",
   chars=[ch("kim1", 600, "calm", "wave", exit="left"), ch("kwon", 1250, "confident", "present", enter="right")],
   labels=[lab("김종현 · 초대 대표", "김종현", "cream", x=600, y=260)],
   lower_third={"name": "권영수", "sub": "대표이사 부회장 (2021년 11월~)", "at": "권영수"})
sh("closeup", [62, 63], who="kwon", side="right", set="office", era="modern", time="day", emotion="confident", pose="arms_crossed",
   labels=[lab("前 LG화학 전지사업본부장", "전지사업본부장을", "gold", x=600, y=300), lab("배터리로 복귀", "돌아온", "lime", x=600, y=860)])
chap("베팅", "4장")
sh("chart", [64, 65], board="chalk", chart={"type": "line", "values": [505000, 624000], "labels": ["상장 첫날", "2022.11.11"], "suffix": "원", "trend": "up", "title": "주가 (종가, 네이버)", "show_values": True, "at": "날았습니다"},
   labels=[lab("시총 약 146조 원", "146조", "gold")])
sh("counter", [66, 67], value={"from": 0, "to": 337455, "suffix": "억 원", "at": "33조"}, caption="2023년 매출 (DART)", icon="trophy",
   compare={"text": "영업이익 2조 1,632억 원", "icon": "chart_up", "at": "영업이익은"})
sh("closeup", 68, who="m1", side="left", set="home", time="dusk", emotion="worried", pose="think",
   bubble={"who": "m1", "text": "전기차가 안 팔린다", "icon": "car", "at": "캐즘이"}, labels=[lab("캐즘", "캐즘이", "red", x=1350, y=860, size=130)])
sh("counter", 69, value={"from": 337455, "to": 256196, "suffix": "억 원", "at": "25조"}, caption="2024년 매출 (DART)", icon="chart_down")
sh("chart", 70, board="white", chart={"type": "bar", "values": [21632, 5754], "labels": ["2023년", "2024년"], "suffix": "억 원", "title": "영업이익 (DART)", "show_values": True, "highlight": 1, "at": "영업이익은"},
   labels=[lab("약 4분의 1", "4분의", "red")])
sh("wide", 71, set="office", era="modern", wall="blue", time="day", tag="2024년 3월",
   chars=[ch("kwon", 600, "calm", "wave", exit="left"), ch("kdm", 1200, "confident", "present", enter="right")],
   lower_third={"name": "김동명", "sub": "대표이사 사장 (2024년 3월~)", "at": "김동명"})
sh("closeup", 72, who="kdm", side="right", set="office", era="modern", time="day", emotion="smile", pose="explain",
   labels=[lab("KAIST 재료공학 박사", "카이스트", "gold", x=600, y=300), lab("前 자동차전지사업부장", "자동차전지사업부장을", "cream", x=600, y=860)])
sh("icon", [73, 74], icons=[{"name": "car", "label": "자동차 말고", "at": "자동차가"}, {"name": "building", "label": "에너지저장장치 (ESS)", "at": "에너지저장장치입니다"}])
sh("table", [75, 76], hand="kdm", items=[{"type": "contract", "title": "공급 계약 (2025년 7월 공시)", "text": "리튬인산철 배터리", "at": "+0.2", "stamp": {"text": "5조 9,442억 원", "at": "5조"}}])
sh("counter", [77, 78], value={"from": 0, "to": 23.2, "suffix": "%", "at": "23.2%에"}, caption="직전 해 매출 대비 계약 한 건 (DART)", icon="target",
   compare={"text": "공급 2027년 8월부터 3년", "icon": "calendar", "at": "2027년"})
sh("wide", 79, set="street", time="day", shop="ESS 단지",
   chars=[ch("kdm", 650, "excited", "present")],
   props=[{"icon": "building", "x": 1200, "y": 700, "s": .55, "at": "에너지저장장치"}, {"icon": "building", "x": 1550, "y": 700, "s": .55, "at": "수주잔고는"}],
   labels=[lab("ESS 수주잔고 약 160GWh (보도)", "수주잔고는", "gold", x=1350, y=260, size=80)])
chap("성적표", "5장")
sh("closeup", [80, 81], who="m1", side="right", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "성적은?", "at": "성적은", "thought": True})
sh("counter", [82, 83], value={"from": 0, "to": 96434, "suffix": "억 원", "at": "9조"}, caption="2026년 3분기 매출 (DART)", icon="chart_up",
   compare={"text": "분기 기준 사상 최대", "icon": "trophy", "at": "사상"})
sh("chart", [84, 85], board="white", chart={"type": "bar", "values": [236718, 237586], "labels": ["2025년 1년", "2026년 1~9월"], "title": "매출 (DART)", "show_values": False, "highlight": 1, "at": "매출은"},
   labels=[lab("23조 7,586억 원", "23조", "gold"), lab("이미 작년보다 많다", "이미", "lime")])
sh("counter", [86, 87], value={"from": 0, "to": 6616, "suffix": "억 원", "at": "6,616억"}, caption="2026년 1~9월 영업이익 (DART)", icon="chart_down",
   compare={"text": "1년 전보다 -54.9%", "icon": "warning", "at": "54.9%"})
sh("icon", 88, icons=[{"name": "book", "text": "성적표", "label": "LG에너지솔루션 성적표", "at": "성적표를"}], stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("table", [89, 90], items=[{"type": "receipt", "title": "권영수 대표 시절 (종가)", "rows": [["상장 첫날", "505,000원"], ["퇴임일", "414,500원"]], "text": "약 -18%", "at": "+0.2"}],
   stamp={"text": "약 -18%", "at": "18%", "color": "red"})
sh("chart", [91, 92], board="chalk", chart={"type": "bar", "values": [414500, 297500], "labels": ["김동명 취임일", "2026.11.20"], "suffix": "원", "title": "주가 (종가, 네이버)", "show_values": True, "highlight": 1, "at": "취임일"},
   labels=[lab("약 -28%", "28%", "red")])
sh("counter", [93, 94], value={"from": 0, "to": 696150, "suffix": "억 원", "at": "69조"}, caption="시가총액 (2026년 11월 20일 종가로 계산)", icon="building",
   compare={"text": "2022년 11월 꼭대기보다 약 -52%", "icon": "chart_down", "at": "52%"})
sh("table", 95, hand="koo", items=[{"type": "receipt", "title": "잘한 결정", "rows": [["1992년", "배터리 연구"], ["2005년 적자", "접지 않음"]], "text": "배터리 베팅", "at": "+0.2"}],
   stamp={"text": "최고의 결정", "at": "베팅입니다", "color": "green"})
sh("closeup", 96, who="sci", side="left", set="office", era="modern", time="day", emotion="excited", pose="celebrate",
   labels=[lab("2023년 매출 33조 원", "33조", "lime", x=1350, y=860, size=110)])
sh("wide", [97, 98], set="street", time="night", shop="리콜 센터",
   chars=[ch("driver", 650, "angry", "point"), ch("kwon", 1150, "worried", "stressed")],
   props=[{"icon": "car", "x": 1600, "y": 700, "s": .55, "at": "볼트"}],
   stamp={"text": "가장 비싼 실수", "at": "실수는", "color": "red"}, labels=[lab("최대 19억 달러", "19억", "gold", x=1350, y=260, size=110)])
sh("icon", [99, 100], icons=[{"name": "building", "label": "LG화학", "at": "LG화학입니다"}, {"name": "lock", "label": "지분 79.38% (2025년 말)", "at": "79.38%를"}])
chap("반전", "6장")
sh("closeup", 101, who="m1", side="left", set="home", time="dusk", emotion="calm", pose="explain")
sh("counter", [102, 103], value={"from": 0, "to": 7560, "suffix": "억 원", "at": "7,560억"}, caption="2026년 3분기 영업이익 (DART)", icon="chart_up",
   compare={"text": "숫자만 보면 반등", "icon": "trophy", "at": "반등입니다"})
sh("chart", [104, 105], board="white", chart={"type": "bar", "values": [7560, 4169], "labels": ["영업이익", "미국 생산 보조금"], "suffix": "억 원", "title": "2026년 3분기 (DART·보도)", "show_values": True, "highlight": 1, "at": "4,169억"},
   labels=[lab("약 55%", "55%", "red")])
sh("versus", 106, colors=["#D8F0D8", "#F6C7B6"], left={"who": "kdm", "title": "보조금 포함 7,560억", "emotion": "smile", "pose": "present", "at": "+0.2"},
   right={"who": "m2", "title": "보조금 빼면 3,391억 · 3.7%", "emotion": "worried", "pose": "think", "at": "3,391억"})
sh("counter", 107, value={"from": 0, "to": -2969, "suffix": "억 원", "at": "2,969억", "color": "red"}, caption="2026년 3분기 순손실 (DART)", icon="chart_down")
sh("walk", [108, 109], set="street", time="dusk", chars=[ch("koo", 0, "calm", "hold")],
   labels=[lab("1992 → 2026, 34년의 베팅", "34년의", "gold", x=960, y=250), lab("이익 절반 이상 = 미국 세금 공제", "절반", "red", x=960, y=400)])
sh("title", 110, text="공모가 30만 원보다 2,500원 싸다")
sh("wide", [111, 114], set="office", era="modern", wall="sand", time="day",
   chars=[ch("kdm", 600, "happy", "wave"), ch("m1", 960, "happy", "wave"), ch("sci", 1320, "smile", "celebrate")],
   labels=[lab("구독 · 좋아요", "구독과", "lime", x=960, y=230, size=130), lab("출처는 설명란", "출처는", "cream", x=960, y=420)],
   polaroid={"at": "출처는", "who": "kdm", "caption": "114조 몰린 공모주, 이익 절반은 보조금"})

# 빈 화면 방지(2026-11-20 검수): 그래픽 장면의 첫 요소는 장면 시작 직후에 나오게 하고, 나머지만 대사 낱말에 맞춘다
for d in X:
    k = d.get("kind")
    if k == "icon" and d.get("icons"): d["icons"][0]["at"] = "+0.2"
    if k == "table" and d.get("items"): d["items"][0]["at"] = "+0.2"
    if k == "chart" and d.get("chart"): d["chart"]["at"] = "+0.3"
    if k == "counter" and d.get("value"): d["value"]["at"] = "+0.3"

story = {"title": "LG에너지솔루션_v2", "mood": "upbeat", "cast": {
    "koo": {"skin": "light", "outfit": "suit", "color": "#3A3A44", "shirt": "#F2F2F2", "tie": "#A50034", "hair": "short", "hair_col": "#2A2A2A", "glasses": True},
    "kim1": {"skin": "tan", "outfit": "suit", "color": "#4A4A58", "shirt": "#F2F2F2", "tie": "#2E4A8C", "hair": "short", "hair_col": "#2A2420"},
    "kwon": {"skin": "light", "outfit": "suit", "color": "#1F2A3A", "shirt": "#F2F2F2", "tie": "#7A1E2E", "hair": "slick", "hair_col": "#8A8A8A", "glasses": True},
    "kdm": {"skin": "tan", "outfit": "suit", "color": "#2F5A4A", "shirt": "#F2F2F2", "tie": "none", "hair": "short", "hair_col": "#3A3A3A", "glasses": True},
    "lgc": {"skin": "fair", "outfit": "suit", "color": "#6B6B6B", "tie": "#A50034", "hair": "short", "hair_col": "#2A2A2A"},
    "rival": {"skin": "olive", "outfit": "suit", "color": "#C0503A", "tie": "#2E2E36", "hair": "curly", "hair_col": "#2A2420"},
    "judge": {"skin": "light", "outfit": "suit", "color": "#22222A", "tie": "#2E2E36", "hair": "bald", "moustache": True},
    "m1": {"skin": "fair", "outfit": "sweater", "color": "#5E8C6A", "hair": "curly", "hair_col": "#3A2C22"},
    "m2": {"skin": "olive", "outfit": "suit", "color": "#6A6A78", "tie": "#2E2E36", "hair": "bald"},
    "exec2": {"skin": "light", "outfit": "suit", "color": "#3A4A5A", "tie": "#B8862E", "hair": "short", "hair_col": "#5A5A5A"},
    "sci": {"skin": "light", "outfit": "hoodie", "color": "#F2F2F2", "hair": "long", "hair_col": "#3A2C22", "glasses": True},
    "driver": {"skin": "fair", "outfit": "tshirt", "color": "#D0703A", "hair": "short", "hair_col": "#1E1A18"}},
  "shots": X}
for d in X:
    if d.get("kind") == "walk":
        for c in d.get("chars", []): c.pop("x", None)
json.dump(story, open(os.path.join(P, "story.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(X), "shots")
