#!/usr/bin/env python3
"""쿠팡 v2 스토리보드."""
import json, os
P = os.path.dirname(os.path.abspath(__file__)); X = []
def sh(kind, s, **k):
    d = {"kind": kind}
    if s is not None: d["s"] = s if isinstance(s, list) else [s]
    d.update(k); X.append(d)
def lab(text, at, color="lime", **k): return dict(text=text, at=at, color=color, **k)
def ch(id, x, emotion="neutral", pose="idle", **k): return dict(id=id, x=x, emotion=emotion, pose=pose, **k)
def chap(t, n): sh("title", None, text=t, sub=n, hold=1.6)

# 인트로 · 13년 만의 흑자, 그리고 다시 적자
sh("wide", 0, set="office", era="modern", wall="cream", time="day", tag="2010년 · 한국",
   chars=[ch("founder", 900, "excited", "present", beats=[{"at": "차렸습니다", "pose": "celebrate", "emotion": "happy"}])],
   props=[{"icon": "laptop", "x": 1450, "y": 690, "s": .6, "at": "온라인"}], labels=[lab("온라인 쇼핑몰 창업", "쇼핑몰을", "gold", x=1400, y=260)])
sh("counter", 1, value={"from": 0, "to": 13, "suffix": "년", "at": "13년"}, caption="첫 연간 영업흑자까지 (2010년 → 2023년)", icon="calendar")
sh("closeup", 2, who="m1", side="left", set="home", time="dusk", emotion="worried", pose="think", labels=[lab("오래가지 않았다", "오래가지", "red", x=1350, y=860, size=100)])
sh("counter", 3, value={"from": 0, "to": 13.37, "suffix": "억 달러", "at": "13억"}, caption="2026년 1~9월 순손실 (SEC 10-Q)", icon="chart_down",
   compare={"text": "다시 적자", "icon": "warning", "at": "순손실을"})
sh("skyline", 4, time="day", labels=[lab("쿠팡", "쿠팡입니다", size=180)])
chap("판돈", "1장")
sh("wide", [5, 6], set="office", era="modern", wall="blue", time="day",
   chars=[ch("founder", 900, "confident", "present", beats=[{"at": "최고경영자입니다", "pose": "hips", "emotion": "confident"}])],
   lower_third={"name": "김범석", "sub": "쿠팡 창업자 · CEO (2010년 5월~)", "at": "김범석은"}, labels=[lab("하버드 대학교 졸업", "하버드", "gold", x=1400, y=260)])
sh("icon", 7, icons=[{"name": "shopping", "text": "장터", "label": "판매자의 물건", "at": "판매자의"}, {"name": "handshake", "label": "마켓플레이스", "at": "마켓플레이스로"}])
sh("closeup", [8, 9], who="m1", side="left", set="home", time="night", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "왜 13년?", "at": "13년이나", "thought": True}, labels=[lab("첫 흑자까지 13년", "13년이나", "red", x=1350, y=860, size=100)])
sh("icon", 10, icons=[{"name": "book", "text": "성적표", "label": "끝에 공개", "at": "성적표를"}], stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("table", 11, hand="founder", items=[{"type": "contract", "title": "직매입 시작", "text": "물건을 직접 사서 판다", "at": "+0.2", "stamp": {"text": "2013년", "at": "직매입을"}}])
sh("wide", 12, set="street", time="day", shop="물류센터", tag="2014년",
   chars=[ch("founder", 700, "excited", "push", beats=[{"at": "시작합니다", "pose": "celebrate", "emotion": "excited"}])],
   props=[{"icon": "car", "x": 1400, "y": 700, "s": .65, "at": "로켓배송을"}], stamp={"text": "로켓배송", "at": "로켓배송을", "color": "red"})
sh("icon", 13, icons=[{"name": "shopping", "text": "직매입", "label": "직접 사들인 물건", "at": "사들인"}, {"name": "factory", "label": "직접 지은 물류센터", "at": "물류센터에서"}, {"name": "car", "label": "직접 고용한 배송 직원", "at": "배송"}])
sh("versus", [14, 15], colors=["#D9D9E6", "#F6E0B6"], left={"who": "m2", "title": "택배 회사에 맡긴다", "emotion": "calm", "pose": "present", "at": "택배"},
   right={"who": "founder", "title": "전부 직접 갖춘다", "emotion": "confident", "pose": "point", "at": "반대로"}, labels=[lab("창고 · 트럭 · 사람", "트럭과", "gold", x=960, y=900)])
sh("table", 16, items=[{"type": "letter", "title": "상장 서류 (S-1)", "text": "물류망에 수십억 달러", "at": "+0.2", "ring_at": "수십억"}])
sh("walk", [17, 18], set="street", time="night", chars=[ch("worker", 0, "happy", "hold")],
   labels=[lab("자정 직전 주문 → 다음 날 무료 배송", "자정", "cream", x=960, y=250, size=80), lab("쿠팡의 판돈", "판돈이었습니다", "lime", x=960, y=420)])
chap("결정", "2장")
sh("closeup", 19, who="founder", side="right", set="office", time="day", emotion="thinking", pose="think",
   bubble={"who": "founder", "text": "큰돈이 필요하다", "icon": "moneybag", "at": "큰돈이"})
sh("wide", 20, set="office", era="modern", wall="teal", time="day",
   chars=[ch("investor", 650, "smile", "present"), ch("founder", 1200, "happy", "hold")],
   props=[{"icon": "handshake", "x": 930, "y": 520, "s": .5, "at": "소프트뱅크였습니다"}], labels=[lab("소프트뱅크", "소프트뱅크였습니다", "gold", x=930, y=250)])
sh("counter", 21, value={"from": 0, "to": 10, "suffix": "억 달러", "at": "10억"}, caption="2015년 6월 소프트뱅크 투자 (보도)", icon="moneybag")
sh("table", 22, hand="investor", items=[{"type": "cash", "text": "20억 달러", "at": "+0.2"}], stamp={"text": "2018년 11월", "at": "비전펀드가", "color": "green"})
sh("counter", [23, 24], value={"from": 0, "to": 10.98, "suffix": "억 달러", "at": "10억"}, caption="2018년 순손실 (상장 서류 S-1)", icon="chart_down",
   compare={"text": "한 해에 10억 달러 넘게", "icon": "warning", "at": "넘게"})
sh("closeup", 25, who="founder", side="left", set="office", time="day", emotion="confident", pose="hips", labels=[lab("속도는 그대로", "속도를", "lime", x=1350, y=860, size=100)])
sh("icon", 26, tag="2019년", icons=[{"name": "gift", "label": "로켓와우 멤버십", "at": "로켓와우"}, {"name": "calendar", "text": "월 회비", "label": "무료 배송", "at": "회비를"}])
sh("crowd", 27, count=26, emotion="happy", set="street", labels=[lab("직접 고용 5만 명+ (2020년 말)", "5만", "gold", size=90)])
sh("counter", 28, value={"from": 0, "to": 41.18, "suffix": "억 달러", "at": "41억"}, caption="창업 뒤 누적 적자 (2020년 말, S-1)", icon="chart_down")
sh("closeup", [29, 30], who="m1", side="right", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "돈은 어디서?", "at": "어디서", "thought": True})
sh("title", 31, text="서울이 아니라, 뉴욕")
sh("wide", [32, 33], set="street", time="day", shop="뉴욕증권거래소", tag="2021년 3월 11일 · 뉴욕",
   chars=[ch("founder", 800, "excited", "present", beats=[{"at": "상장합니다", "pose": "celebrate", "emotion": "excited"}])],
   stamp={"text": "상장", "at": "상장합니다", "color": "red"}, labels=[lab("공모가 35달러", "35달러였습니다", "gold", x=1400, y=300)])
sh("counter", 34, value={"from": 0, "to": 45.5, "suffix": "억 달러", "at": "45억"}, caption="공모 규모: 35달러 × 1억 3천만 주 (계산)", icon="coins")
sh("chart", 35, board="chalk", chart={"type": "bar", "values": [35, 63.5, 49.25], "labels": ["공모가", "첫날 시초가", "첫날 종가"], "suffix": "달러", "title": "2021년 3월 11일 (NYSE)", "show_values": True, "highlight": 2, "at": "63.5달러에"})
sh("counter", 36, value={"from": 0, "to": 845, "suffix": "억 달러", "at": "845억"}, caption="첫날 종가 기준 시가총액 (보도)", icon="trophy")
sh("versus", 37, colors=["#E0E0F0", "#F6D0C0"], left={"who": "founder", "title": "쿠팡 아이엔씨 · 미국 상장사", "emotion": "confident", "pose": "present", "at": "아이엔씨이고"},
   right={"who": "m2", "title": "쿠팡 · 한국 자회사", "emotion": "calm", "pose": "present_left", "at": "자회사입니다"})
sh("icon", [38, 39], icons=[{"name": "target", "label": "B주식 1주 = 29표", "at": "29표가"}, {"name": "trophy", "label": "의결권 74.1% (2025년 말)", "at": "74.1%입니다"}])
chap("위기", "3장")
sh("closeup", 40, who="founder", side="left", set="office", time="dusk", emotion="worried", pose="think")
sh("counter", 41, value={"from": 0, "to": 15.43, "suffix": "억 달러", "at": "15억"}, caption="2021년 순손실 (SEC 10-K)", icon="chart_down",
   compare={"text": "오히려 커졌다", "icon": "warning", "at": "커졌습니다"})
sh("chart", [42, 43], board="white", chart={"type": "bar", "values": [49.25, 9.35], "labels": ["첫날 종가", "2022.5.9 종가"], "suffix": "달러", "title": "쿠팡 주가 (NYSE)", "show_values": True, "highlight": 1, "at": "9.35달러였습니다"},
   labels=[lab("미끄러졌다", "미끄러졌습니다", "red")])
sh("closeup", 44, who="m1", side="left", set="home", time="day", emotion="shocked", pose="facepalm", labels=[lab("공모가의 3분의 1도 안 돼", "3분의", "red", x=1300, y=860, size=90)])
sh("counter", 45, value={"from": 0, "to": 59.35, "suffix": "억 달러", "at": "59억"}, caption="누적 적자 정점 (2022년 6월 말, SEC 10-Q)", icon="chart_down")
sh("wide", [46, 47], set="board", time="day",
   chars=[ch("investor", 600, "angry", "arms_crossed"), ch("m2", 960, "worried", "point"), ch("founder", 1350, "nervous", "stressed")],
   labels=[lab("정말 돈을 벌 수 있나?", "정말", "red", x=960, y=250, size=90)])
sh("closeup", 48, who="founder", side="right", set="office", time="day", emotion="excited", pose="point", labels=[lab("숫자가 돌아선다", "돌아섭니다", "lime", x=600, y=860, size=100)])
chap("베팅", "4장")
sh("counter", [49, 50], value={"from": 0, "to": 7700, "suffix": "만 달러", "at": "7,700만"}, caption="2022년 3분기 첫 분기 영업이익 (SEC 10-Q)", icon="chart_up")
sh("chart", 51, board="chalk", chart={"type": "bar", "values": [62.73, 119.67, 184.06, 205.83, 243.83], "labels": ["2019", "2020", "2021", "2022", "2023"], "suffix": "억 달러", "title": "쿠팡 매출 (SEC)", "show_values": True, "highlight": 4, "at": "243억"})
sh("wide", [52, 53], set="office", era="modern", wall="green", time="day",
   chars=[ch("founder", 800, "confident", "present", beats=[{"at": "첫", "pose": "celebrate", "emotion": "excited"}])],
   labels=[lab("영업이익 4억 7,300만 달러", "4억", "gold", x=1400, y=260)], stamp={"text": "첫 연간 영업흑자", "at": "영업흑자입니다", "color": "green"})
sh("table", [54, 55], items=[{"type": "receipt", "title": "2023년 순이익 (10-K)", "rows": [["순이익", "13억 6천만 달러"], ["그중 세금 혜택", "7억 7,600만 달러"]], "text": "세금 혜택 포함", "at": "+0.2"}])
sh("walk", 56, set="street", time="day", chars=[ch("worker", 0, "happy", "hold")], labels=[lab("적자로 지은 물류센터 → 이익", "이익을", "lime", x=960, y=250)])
sh("table", [57, 58], hand="founder", items=[{"type": "contract", "title": "인수 완료", "text": "파페치 (영국 명품 플랫폼)", "at": "+0.2", "stamp": {"text": "2024년 1월", "at": "파페치"}}])
sh("map", 59, places=[{"name": "한국", "x": 1350, "y": 420}, {"name": "대만", "x": 980, "y": 760}], vehicle="plane", at="대만에서도",
   labels=[lab("대만에서도 로켓배송", "대만에서도", "gold")])
sh("chart", [60, 61], board="white", chart={"type": "bar", "values": [243.83, 302.68, 345.34], "labels": ["2023", "2024", "2025"], "suffix": "억 달러", "title": "쿠팡 매출 (SEC 10-K)", "show_values": True, "highlight": 2, "at": "302억"})
sh("counter", 62, value={"from": 0, "to": 5.5, "suffix": "배", "at": "5.5배입니다"}, caption="매출 2019년 62억 7,300만 → 2025년 345억 3,400만 달러 (계산)", icon="chart_up")
sh("crowd", 63, count=30, emotion="happy", set="street", labels=[lab("직접 고용 약 10만 8천 명 (2025년 말)", "10만", "gold", size=80)])
sh("icon", [64, 65], icons=[{"name": "coins", "label": "2025년 영업이익 4억 7,300만 달러", "at": "4억"}, {"name": "moneybag", "label": "순이익 2억 800만 달러", "at": "순이익은"}, {"name": "trophy", "label": "3년 연속 흑자", "at": "3년"}])
chap("성적표", "5장")
sh("closeup", [66, 67], who="m1", side="right", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "무슨 일이?", "at": "무슨", "thought": True})
sh("wide", 68, set="office", era="modern", wall="grey", time="night", tag="2025년 11월",
   chars=[ch("staff", 800, "shocked", "stressed")], props=[{"icon": "laptop", "x": 1350, "y": 690, "s": .6, "at": "고객"}, {"icon": "warning", "x": 1600, "y": 640, "s": .5, "at": "무단"}],
   stamp={"text": "무단 접근", "at": "무단", "color": "red"})
sh("counter", 69, value={"from": 0, "to": 3300, "suffix": "만 개", "at": "3,300만"}, caption="정보가 빠져나간 계정 (회사 공시, SEC 10-K)", icon="lock",
   compare={"text": "이름 · 전화번호 · 주소 · 이메일", "icon": "phone", "at": "이름"})
sh("icon", 70, icons=[{"name": "lock", "label": "결제 정보 · 로그인 정보는 빠짐", "at": "결제"}], labels=[lab("회사 설명", "회사는", "cream")])
sh("counter", 71, value={"from": 0, "to": 3755, "suffix": "만 명", "at": "3,755만"}, caption="회원 + 비회원 (개인정보보호위원회 발표)", icon="warning")
sh("versus", [72, 73], colors=["#D9D9E6", "#C9E8E4"], left={"who": "park", "title": "박대준 · 사임 (2025.12.10)", "emotion": "sad", "pose": "idle", "at": "박대준"},
   right={"who": "rogers", "title": "해롤드 로저스 · 임시 대표", "emotion": "calm", "pose": "present", "at": "로저스가"})
sh("icon", 74, icons=[{"name": "gift", "label": "1인당 5만 원어치 이용권", "at": "5만"}])
sh("chart", 75, board="chalk", chart={"type": "bar", "values": [5000, 5000, 20000, 20000], "labels": ["쿠팡 상품", "쿠팡이츠", "여행", "명품"], "suffix": "원", "title": "이용권 5만 원 구성 (보도)", "show_values": True, "highlight": 0, "at": "5천"})
sh("counter", [76, 77], value={"from": 0, "to": 12, "suffix": "억 달러", "at": "12억"}, caption="이용권 규모 (회사 공시, SEC 10-Q)", icon="gift",
   compare={"text": "사용 종료 2026년 4월 중순", "icon": "calendar", "at": "끝났습니다"})
sh("wide", [78, 79], set="board", time="day", tag="2026년 6월 10일",
   chars=[ch("official", 700, "angry", "point", beats=[{"at": "의결했습니다", "pose": "push", "emotion": "angry"}]), ch("official2", 1200, "calm", "arms_crossed")],
   labels=[lab("과징금 6,246억 8,100만 원", "6,246억", "red", x=960, y=250, size=90)], stamp={"text": "역대 최대", "at": "역대", "color": "red"})
sh("icon", 80, icons=[{"name": "lock", "label": "개인정보 유출", "at": "유출과"}, {"name": "laptop", "text": "기록", "label": "다른 사이트 접속 기록 수집", "at": "기록을"}])
sh("table", 81, items=[{"type": "letter", "title": "행정소송 (2026.10.7)", "text": "서울행정법원 · 진행 중", "at": "+0.2", "ring_at": "진행"}])
sh("icon", [82, 83], icons=[{"name": "book", "text": "성적표", "label": "김범석 창업자", "at": "성적표를"}, {"name": "calendar", "text": "2010~", "label": "2010년부터 지금까지", "at": "지금까지입니다"}],
   stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("chart", 84, board="white", chart={"type": "bar", "values": [62.73, 345.34], "labels": ["2019년", "2025년"], "suffix": "억 달러", "title": "매출 (SEC)", "show_values": True, "highlight": 1, "at": "345억"})
sh("counter", 85, value={"from": 0, "to": 13, "suffix": "년", "at": "13년입니다"}, caption="창업에서 첫 연간 영업흑자까지", icon="hourglass")
sh("table", [86, 87], items=[{"type": "receipt", "title": "잘한 결정", "rows": [["2014년", "로켓배송 시작"], ["2025년 4분기", "구매 고객 2,460만 명"]], "text": "로켓배송", "at": "+0.2"}],
   stamp={"text": "최고의 결정", "at": "2,460만", "color": "green"})
sh("closeup", 88, who="founder", side="left", set="office", time="night", emotion="sad", pose="facepalm", stamp={"text": "가장 비싼 실수", "at": "실수는", "color": "red"})
sh("table", 89, items=[{"type": "receipt", "title": "비싼 실수", "rows": [["과징금 처분", "6,246억 원"], ["이용권", "약 12억 달러"]], "text": "정보 유출 사고", "at": "+0.2"}])
sh("chart", [90, 91], board="chalk", chart={"type": "bar", "values": [35, 14.27], "labels": ["공모가", "2026.11.20 종가"], "suffix": "달러", "title": "쿠팡 주가 (NYSE)", "show_values": True, "highlight": 1, "at": "14.27달러입니다"},
   labels=[lab("약 -59%", "59%", "red")])
sh("counter", [92, 93], value={"from": 0, "to": 256, "suffix": "억 달러", "at": "256억"}, caption="쿠팡 시가총액 (2026년 11월 20일, 계산)", icon="building",
   compare={"text": "약 34조 원 (환율 1,335원)", "icon": "coins", "at": "34조"})
chap("반전", "6장")
sh("closeup", 94, who="m1", side="left", set="home", time="dusk", emotion="calm", pose="explain")
sh("wide", [95, 96], set="street", time="night", shop="물류센터", tag="2026년 7월 · 인천",
   chars=[ch("worker", 650, "shocked", "stressed")], props=[{"icon": "warning", "x": 1400, "y": 640, "s": .65, "at": "큰불이"}],
   labels=[lab("화재 손실 2억 4,800만 달러", "2억", "red", x=1350, y=260, size=80)])
sh("chart", 97, board="white", chart={"type": "bar", "values": [242, 556, 450], "labels": ["1분기", "2분기", "3분기"], "suffix": "백만 달러", "title": "2026년 분기 영업손실 (SEC 10-Q)", "show_values": True, "highlight": 1, "at": "1분기부터"},
   labels=[lab("세 분기 연속 영업손실", "연속", "red")])
sh("counter", [98, 99], value={"from": 0, "to": 99.62, "suffix": "억 달러", "at": "99억"}, caption="2026년 3분기 매출 (SEC 10-Q)", icon="chart_up",
   compare={"text": "1년 전보다 +7%", "icon": "trophy", "at": "7%"})
sh("crowd", 100, count=22, emotion="worried", set="street", labels=[lab("고객 수 증가 둔화", "느려졌고", "red", size=100), lab("회사: 사고 영향", "영향을", "cream")])
sh("counter", 101, value={"from": 0, "to": 17.22, "suffix": "억 달러", "at": "17억"}, caption="2023~2025년 순이익 합계 (SEC·계산)", icon="moneybag")
sh("versus", [102, 103], colors=["#D8F0D8", "#F6C7B6"], left={"who": "founder", "title": "3년 순이익 +17.22억 달러", "emotion": "happy", "pose": "celebrate", "at": "+0.2"},
   right={"who": "founder", "title": "2026년 9개월 -13.37억 달러", "emotion": "shocked", "pose": "facepalm", "at": "순손실은"},
   labels=[lab("3년 치의 약 78%", "78%입니다", "red", x=960, y=900)])
sh("chart", 104, board="chalk", chart={"type": "bar", "values": [41.18, 59.35, 40.21, 53.58], "labels": ["2020 말", "2022.6 말", "2025 말", "2026.9 말"], "suffix": "억 달러", "title": "누적 적자 (SEC)", "show_values": True, "highlight": 3, "at": "53억"})
sh("title", 105, text="13년 만의 흑자, 다시 적자까지 3년도 안 걸렸다")
sh("wide", [106, 109], set="office", era="modern", wall="sand", time="day",
   chars=[ch("founder", 600, "happy", "wave"), ch("m1", 960, "happy", "wave"), ch("worker", 1320, "smile", "celebrate")],
   labels=[lab("구독 · 좋아요", "구독과", "lime", x=960, y=230, size=130), lab("출처는 설명란", "출처는", "cream", x=960, y=420)],
   polaroid={"at": "출처는", "who": "founder", "caption": "13년 걸린 흑자, 다시 적자로"})

# 빈 화면 방지(2026-11-20 검수): 그래픽 장면의 첫 요소는 장면 시작 직후에 나오게 하고, 나머지만 대사 낱말에 맞춘다
for d in X:
    k = d.get("kind")
    if k == "icon" and d.get("icons"): d["icons"][0]["at"] = "+0.2"
    if k == "table" and d.get("items"): d["items"][0]["at"] = "+0.2"
    if k == "chart" and d.get("chart"): d["chart"]["at"] = "+0.3"
    if k == "counter" and d.get("value"): d["value"]["at"] = "+0.3"

story = {"title": "쿠팡_v2", "mood": "upbeat", "cast": {
    "founder": {"skin": "light", "outfit": "suit", "color": "#2E3A4A", "shirt": "#F2F2F2", "tie": "none", "hair": "short", "hair_col": "#2A2A2A"},
    "investor": {"skin": "fair", "outfit": "suit", "color": "#5A5A66", "tie": "#C8242C", "hair": "bald"},
    "worker": {"skin": "tan", "outfit": "hoodie", "color": "#3A7BC8", "hair": "short", "hair_col": "#1E1A18", "hat": "cap", "hat_col": "#3A7BC8"},
    "m1": {"skin": "fair", "outfit": "sweater", "color": "#5E8C6A", "hair": "curly", "hair_col": "#3A2C22"},
    "m2": {"skin": "olive", "outfit": "suit", "color": "#6A6A78", "tie": "#2E2E36", "hair": "short", "hair_col": "#5A5A5A"},
    "staff": {"skin": "light", "outfit": "tshirt", "color": "#8C5EA0", "hair": "long", "hair_col": "#2A2420", "glasses": True},
    "park": {"skin": "light", "outfit": "suit", "color": "#3A3A44", "tie": "#1F2A3A", "hair": "short", "hair_col": "#3A3A3A", "glasses": True},
    "rogers": {"skin": "fair", "outfit": "suit", "color": "#1F2A3A", "tie": "#7A1E2E", "hair": "slick", "hair_col": "#8A6A4A"},
    "official": {"skin": "light", "outfit": "suit", "color": "#2F5A4A", "tie": "#2E2E36", "hair": "short", "hair_col": "#6A6A6A"},
    "official2": {"skin": "tan", "outfit": "dress", "color": "#9C4A7A", "hair": "bun", "hair_col": "#2A2420"}},
  "shots": X}
for d in X:
    if d.get("kind") == "walk":
        for c in d.get("chars", []): c.pop("x", None)
json.dump(story, open(os.path.join(P, "story.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(X), "shots")
