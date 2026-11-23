#!/usr/bin/env python3
"""에코프로 v2 스토리보드 (15편 · 지주회사 에코프로)."""
import json, os
P = os.path.dirname(os.path.abspath(__file__)); X = []
def sh(kind, s, **k):
    d = {"kind": kind}
    if s is not None: d["s"] = s if isinstance(s, list) else [s]
    d.update(k); X.append(d)
def lab(text, at, color="lime", **k): return dict(text=text, at=at, color=color, **k)
def ch(id, x, emotion="neutral", pose="idle", **k): return dict(id=id, x=x, emotion=emotion, pose=pose, **k)
def chap(t, n): sh("title", None, text=t, sub=n, hold=1.6)

# 인트로 · 직원 한 명 회사의 역설
sh("wide", 0, set="office", era="old", wall="sand", time="day", tag="1998년",
   chars=[ch("founder", 760, "confident", "present"), ch("staff", 1150, "smile", "idle")],
   labels=[lab("직원 한 명", "한", "gold", x=1450, y=260)])
sh("counter", 1, value={"from": 0, "to": 2567, "suffix": "개 종목", "at": "2,567개"}, caption="2023년 주가 상승률 1위 (블룸버그 지수 · 보도)", icon="trophy",
   compare={"text": "그중 1등", "icon": "chart_up", "at": "가장"})
sh("closeup", 2, who="founder", side="left", set="office", time="night", emotion="worried", pose="think",
   stamp={"text": "법정구속", "at": "법정구속된", "color": "red"}, labels=[lab("주가 꼭대기의 여름", "꼭대기를", "cream", x=1350, y=300)])
sh("skyline", 3, time="day", labels=[lab("에코프로", "에코프로입니다", size=180)])
chap("판돈", "1장")
sh("icon", [4, 5], icons=[{"name": "building", "label": "오늘의 에코프로 = 지주회사", "at": "+0.2"}, {"name": "chart_up", "label": "코스닥 상장", "at": "코스닥에"}])
sh("versus", 6, colors=["#CFE3F6", "#D8F0E4"], left={"who": "founder", "title": "에코프로 · 지주회사", "emotion": "confident", "pose": "present", "at": "지주회사"},
   right={"who": "worker", "title": "에코프로비엠 · 양극재", "emotion": "smile", "pose": "hold", "at": "양극재를"},
   labels=[lab("지분 40.83% 최대주주", "40.83%를", "gold", x=960, y=900)])
sh("closeup", 7, who="founder", side="right", set="office", era="modern", time="day", emotion="thinking", pose="think",
   lower_third={"name": "이동채", "sub": "에코프로 창업주", "at": "이동채는"},
   labels=[lab("은행원 약 14년 (보도)", "14년을", "cream", x=600, y=300)])
sh("icon", 8, tag="1997년", icons=[{"name": "book", "text": "교토의정서", "label": "1997년 소식", "at": "+0.2"}, {"name": "bulb", "label": "환경 · 배터리 소재", "at": "환경과"}])
sh("table", [9, 10], hand="founder", items=[{"type": "contract", "title": "회사 설립", "text": "코리아제오륨", "at": "+0.2", "stamp": {"text": "1998년 10월", "at": "세웁니다"}}],
   labels=[lab("첫 직원 1명 (보도)", "여직원", "gold")])
sh("icon", 11, icons=[{"name": "calendar", "text": "2001", "top": "2월", "label": "사명 변경", "at": "+0.2"}, {"name": "heart", "label": "→ 에코프로", "at": "에코프로로"}])
sh("wide", [12, 13], set="street", time="day", shop="오창 공장", tag="충북 오창",
   chars=[ch("founder", 700, "excited", "push", beats=[{"at": "촉매와", "pose": "celebrate", "emotion": "happy"}])],
   props=[{"icon": "factory", "x": 1350, "y": 690, "s": .6, "at": "공장에서"}, {"icon": "warning", "x": 1600, "y": 640, "s": .5, "at": "온실가스를"}],
   labels=[lab("첫 사업 = 공기", "공기였습니다", "lime", x=1400, y=260)])
sh("closeup", [14, 15], who="m1", side="left", set="home", time="night", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "?", "at": "실수는", "thought": True}, labels=[lab("가장 비싼 실수?", "실수는", "red", x=1350, y=860, size=110)])
sh("icon", 16, icons=[{"name": "book", "text": "성적표", "label": "끝에 공개", "at": "성적표를"}], stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("table", 17, items=[{"type": "letter", "title": "신사업", "text": "양극재 (배터리 핵심 소재)", "at": "+0.2", "ring_at": "양극재"}],
   stamp={"text": "2004년 10월", "at": "들어섭니다", "color": "red"})
sh("skyline", 18, time="dusk", tag="2007년 7월", labels=[lab("코스닥 상장", "코스닥에", "gold", size=140)])
sh("wide", 19, set="street", time="day", shop="양극소재 1공장", tag="2008년",
   chars=[ch("founder", 650, "confident", "point", beats=[{"at": "삼성SDI에", "pose": "celebrate", "emotion": "excited"}])],
   props=[{"icon": "factory", "x": 1250, "y": 690, "s": .6, "at": "공장을"}, {"icon": "car", "x": 1600, "y": 720, "s": .5, "at": "납품하기"}],
   labels=[lab("삼성SDI 납품", "삼성SDI에", "lime", x=1400, y=260)])
chap("결정", "2장")
sh("icon", [20, 21], icons=[{"name": "target", "text": "전구체", "label": "첫 번째 큰 판", "at": "+0.2"}, {"name": "brain", "label": "양극재 바로 전 단계", "at": "전"}])
sh("wide", 22, set="office", era="modern", wall="teal", time="day", tag="2009년",
   chars=[ch("founder", 800, "excited", "present", beats=[{"at": "일본", "pose": "stressed", "emotion": "shocked"}])],
   props=[{"icon": "chart_down", "x": 1450, "y": 650, "s": .6, "at": "손실이"}],
   labels=[lab("전구체 국산화", "국산화합니다", "lime", x=1350, y=250)])
sh("chart", 23, board="white", chart={"type": "line", "values": [5, 4.2, 3.1, 2.4], "trend": "down", "show_values": False, "title": "일본 업체 가격 인하 → 손실 (보도)", "at": "+0.3"},
   labels=[lab("손실 확대", "손실이", "red")])
sh("counter", 24, value={"from": 0, "to": 60, "suffix": "%", "at": "60%를"}, caption="당시 전구체 사업 = 매출의 60% (보도)", icon="chart_up")
sh("table", 25, hand="founder", items=[{"type": "contract", "title": "사업 정리", "text": "전구체 사업", "at": "+0.2", "stamp": {"text": "접는다", "at": "접고"}}],
   labels=[lab("양극재 하나에 집중", "집중하기로", "lime")])
sh("closeup", [26, 27], who="founder", side="right", set="office", time="dusk", emotion="confident", pose="arms_crossed",
   labels=[lab("매출 절반 이상을 내려놓다", "내려놓은", "cream", x=600, y=300), lab("바구니는 하나", "바구니", "gold", x=600, y=860)])
sh("counter", [28, 29], value={"from": 0, "to": 1000, "suffix": "억 원", "at": "1천억"}, caption="2015년 12월 처음 매출 1천억 원 돌파 (회사 연혁)", icon="trophy")
sh("table", 30, hand="founder", items=[{"type": "contract", "title": "물적분할", "text": "배터리 소재 → 에코프로비엠", "at": "+0.2", "stamp": {"text": "2016년 5월", "at": "만듭니다"}}])
sh("chart", 31, board="chalk", chart={"type": "bar", "values": [1700, 8547], "labels": ["2016년 출범", "2020년"], "suffix": "억 원", "title": "에코프로비엠 매출 (보도)", "show_values": True, "highlight": 1, "at": "+0.3"})
sh("skyline", 32, time="day", tag="2019년 3월", labels=[lab("에코프로비엠 상장", "에코프로비엠이", "gold", size=120)])
sh("versus", 33, colors=["#D8F0E4", "#CFE3F6"], left={"who": "staff", "title": "에코프로에이치엔 · 환경", "emotion": "smile", "pose": "present", "at": "환경"},
   right={"who": "worker", "title": "에코프로비엠 · 배터리", "emotion": "happy", "pose": "hold", "at": "+0.3"},
   labels=[lab("2021년 5월 분할", "2021년", "gold", x=960, y=900)])
sh("wide", 34, set="board", time="day", tag="2021년 11월",
   chars=[ch("founder", 960, "confident", "present", beats=[{"at": "지주회사가", "pose": "celebrate", "emotion": "excited"}])],
   props=[{"icon": "building", "x": 520, "y": 700, "s": .5, "at": "자회사들을"}, {"icon": "building", "x": 1400, "y": 700, "s": .5, "at": "거느리는"}, {"icon": "factory", "x": 1650, "y": 700, "s": .5, "at": "지주회사가"}],
   labels=[lab("지주회사 전환", "지주회사가", "lime", x=960, y=230)])
sh("closeup", [35, 36], who="m1", side="right", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "어디까지?", "at": "어디까지", "thought": True})
sh("chart", [37, 38], board="white", chart={"type": "bar", "values": [15042, 56397], "labels": ["2021년", "2022년"], "suffix": "억 원", "title": "에코프로 연결 매출 (DART)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("세 배가 넘는다", "세", "red")])
sh("counter", [39, 40], value={"from": 0, "to": 6132, "suffix": "억 원", "at": "6,132억"}, caption="2022년 연결 영업이익 (DART)", icon="coins",
   compare={"text": "직원 1명 → 24년", "icon": "clock", "at": "24년"})
chap("위기", "3장")
sh("closeup", 41, who="founder", side="left", set="office", time="night", emotion="nervous", pose="stressed",
   labels=[lab("문제는 꼭대기에서", "꼭대기에서", "red", x=1350, y=860, size=100)])
sh("wide", [42, 43], set="office", era="modern", wall="grey", time="dusk", tag="2022년 3월",
   chars=[ch("founder", 650, "sad", "idle", exit="left"), ch("kim", 1200, "calm", "present", enter="right")],
   lower_third={"name": "김병훈", "sub": "대표이사 (2022년 3월~) · 에코프로비엠 대표 출신", "at": "김병훈이었습니다"})
sh("title", 44, text="혐의는 이렇습니다")
sh("table", 45, items=[{"type": "newspaper", "title": "혐의 요지 (보도)", "text": "공시 전 주식 매매 · 차명·자녀 계좌", "at": "+0.2", "ring_at": "차명과"}],
   labels=[lab("공시 전 매매", "공시되기", "cream"), lab("이득 약 11억 원", "11억", "red")])
sh("icon", 46, tag="2023년 5월 11일 · 2심", icons=[{"name": "lock", "label": "징역 2년 · 법정구속", "at": "+0.2"}, {"name": "moneybag", "label": "벌금 22억 원", "at": "22억"}])
sh("table", 47, items=[{"type": "letter", "title": "대법원 (보도)", "text": "상고 기각 · 형 확정", "at": "+0.2", "stamp": {"text": "2023년 8월 18일 확정", "at": "확정했다고"}}])
sh("closeup", 48, who="song", side="right", set="office", time="day", emotion="confident", pose="present",
   lower_third={"name": "송호준", "sub": "대표이사 (2023년 3월~) · 삼성SDI 부사장 출신", "at": "송호준으로"})
chap("광풍", "4장")
sh("crowd", 49, count=26, emotion="excited", set="street", labels=[lab("주가 폭발", "폭발합니다", "red", size=140)])
sh("counter", 50, value={"from": 0, "to": 1118000, "suffix": "원", "at": "111만"}, caption="2023년 7월 18일 종가 (보도)", icon="chart_up")
sh("icon", 51, icons=[{"name": "trophy", "label": "코스닥 16년 만의 황제주 (보도)", "at": "+0.2"}], stamp={"text": "황제주", "at": "황제주였다고", "color": "red"})
sh("chart", [52, 53], board="chalk", chart={"type": "bar", "values": [1118000, 1293000, 1539000], "labels": ["7.18 종가", "7.25 종가", "7.26 장중"], "suffix": "원", "title": "2023년 7월 에코프로 주가 (보도)", "show_values": True, "highlight": 2, "at": "+0.3"})
sh("versus", 54, colors=["#CFE3F6", "#F6E0B6"], left={"who": "founder", "title": "에코프로", "emotion": "excited", "pose": "celebrate", "at": "+0.3"},
   right={"who": "worker", "title": "에코프로비엠", "emotion": "excited", "pose": "celebrate", "at": "에코프로비엠"},
   labels=[lab("형제 합산 시총 60조 원 (보도)", "60조", "gold", x=960, y=900)])
sh("closeup", 55, who="song", side="right", set="office", time="day", emotion="happy", pose="present_left", labels=[lab("실적도 최대", "실적도", "gold", x=600, y=860)])
sh("counter", [56, 57], value={"from": 0, "to": 72602, "suffix": "억 원", "at": "7조"}, caption="2023년 연결 매출 · 지금까지 최대 (DART)", icon="trophy",
   compare={"text": "영업이익 2,982억 원", "icon": "coins", "at": "2,982억"})
sh("walk", 58, set="street", time="dusk", chars=[ch("investor", 0, "nervous", "hold")],
   labels=[lab("주가 > 실적", "빨리", "red", x=960, y=260)])
sh("chart", 59, board="white", chart={"type": "bar", "values": [1293000, 647000], "labels": ["7.25 종가", "12.28 종가"], "suffix": "원", "title": "2023년 에코프로 주가 (보도)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("꼭대기의 절반", "절반이었다고", "red")])
sh("table", 60, items=[{"type": "contract", "title": "액면분할", "text": "1주 → 5주", "at": "+0.2", "stamp": {"text": "2024년 4월", "at": "액면분할을"}}])
sh("closeup", 61, who="song", side="left", set="office", time="night", emotion="shocked", pose="facepalm", labels=[lab("숫자가 뒤집힌다", "뒤집힙니다", "red", x=1350, y=860)])
sh("chart", 62, board="chalk", chart={"type": "bar", "values": [72602, 31279], "labels": ["2023년", "2024년"], "suffix": "억 원", "title": "연결 매출 (DART)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("1년 만에 -57%", "57%", "red")])
sh("versus", 63, colors=["#D8F0D8", "#F6C7B6"], left={"who": "song", "title": "2023년 영업이익 +2,982억", "emotion": "happy", "pose": "celebrate", "at": "+0.2"},
   right={"who": "song", "title": "2024년 영업손실 -2,930억", "emotion": "shocked", "pose": "stressed", "at": "영업손실"},
   stamp={"text": "적자", "at": "됩니다", "color": "red"})
sh("wide", 64, set="street", time="night", shop="전기차 매장", tag="2024년",
   chars=[ch("shopper", 700, "thinking", "arms_crossed"), ch("shopper2", 1100, "tired", "shrug")],
   props=[{"icon": "car", "x": 1500, "y": 720, "s": .55, "at": "전기차"}, {"icon": "chart_down", "x": 1700, "y": 600, "s": .5, "at": "하락이"}],
   labels=[lab("캐즘 + 원재료 값 하락 (보도)", "캐즘에", "cream", x=1300, y=250)])
chap("성적표", "5장")
sh("closeup", [65, 66], who="m1", side="right", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "다시 일어섰나?", "at": "일어섰을까요", "thought": True})
sh("chart", [67, 68], board="white", chart={"type": "bar", "values": [-2930, 2138], "labels": ["2024년", "2025년"], "suffix": "억 원", "title": "연결 영업이익 (DART)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("매출 3조 4,130억 원", "3조", "gold"), lab("흑자 전환", "흑자로", "lime")])
sh("map", 69, places=[{"name": "한국", "x": 1450, "y": 380}, {"name": "인도네시아", "x": 900, "y": 760}], vehicle="ship", at="인도네시아",
   labels=[lab("니켈 제련소 지분 투자 (보도)", "니켈", "gold")])
sh("counter", 70, value={"from": 0, "to": 24504, "suffix": "억 원", "at": "2조"}, caption="2026년 1~9월 연결 매출 (DART)", icon="coins",
   compare={"text": "영업이익 1,011억 원", "icon": "chart_up", "at": "1,011억"})
sh("walk", 71, set="street", time="day", chars=[ch("investor", 0, "excited", "hold")], labels=[lab("한 번 더", "한", "gold", x=960, y=260)])
sh("crowd", 72, count=20, emotion="excited", set="street", labels=[lab("로봇 · 피지컬 AI 기대 (보도)", "로봇과", "cream"), lab("다시 코스닥 시총 1위", "1위에", "gold", size=110)])
sh("counter", 73, value={"from": 0, "to": 185000, "suffix": "원", "at": "18만"}, caption="2026년 2월 27일 종가 (네이버 증권)", icon="chart_up")
sh("chart", 74, board="chalk", chart={"type": "bar", "values": [185000, 64500], "labels": ["2026.2.27", "2026.11.20"], "suffix": "원", "title": "에코프로 종가 (네이버 증권)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("9개월 만에 -65%", "65%", "red")])
sh("wide", [75, 76], set="office", era="modern", wall="blue", time="day", tag="2026년 10월 19일",
   chars=[ch("song", 650, "calm", "wave", exit="left"), ch("choi", 1200, "confident", "present", enter="right")],
   lower_third={"name": "최상운", "sub": "대표이사 (2026년 10월~)", "at": "최상운으로"})
sh("icon", 77, icons=[{"name": "money", "label": "KB국민은행 지점장 출신", "at": "+0.2"}, {"name": "calendar", "text": "2016", "top": "12월", "label": "에코프로 입사", "at": "2016년"}])
sh("closeup", 78, who="founder", side="left", set="office", time="day", emotion="calm", pose="arms_crossed",
   labels=[lab("최대주주 18.84%", "18.84%를", "gold", x=1350, y=300), lab("공시상 상임고문", "상임고문으로", "cream", x=1350, y=860)])
sh("icon", [79, 80], icons=[{"name": "book", "text": "성적표", "label": "에코프로 성적표", "at": "+0.2"}, {"name": "heart", "label": "시작은 직원 1명", "at": "직원"}],
   stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("versus", 81, colors=["#F6C7B6", "#CFE3F6"], left={"who": "founder", "title": "전구체 (매출 60%) 접고", "emotion": "calm", "pose": "push", "at": "+0.2"},
   right={"who": "worker", "title": "양극재에 모으다", "emotion": "excited", "pose": "celebrate", "at": "양극재에"})
sh("table", 82, items=[{"type": "receipt", "title": "잘한 결정", "rows": [["접은 것", "전구체 (매출 60%)"], ["2015년 매출", "1천억"]], "text": "2023년 7조 2,602억", "at": "+0.2"}],
   stamp={"text": "최고의 결정", "at": "7조", "color": "green"})
sh("closeup", 83, who="founder", side="right", set="office", time="night", emotion="sad", pose="idle",
   labels=[lab("가장 비싼 실수", "실수는", "red", x=600, y=860, size=110)])
sh("icon", 84, icons=[{"name": "moneybag", "label": "보도된 이득 약 11억 원", "at": "+0.2"}, {"name": "lock", "label": "징역 2년 · 벌금 22억 원 확정", "at": "확정된"}])
sh("table", [85, 86], items=[{"type": "receipt", "title": "가장 아픈 해", "rows": [["2023년 영업이익", "2,982억"], ["2024년", "적자"]], "text": "영업손실 2,930억", "at": "+0.2"}],
   stamp={"text": "-2,930억", "at": "2,930억", "color": "red"})
sh("chart", 87, board="white", chart={"type": "line", "values": [253692, 126944, 56408, 90800, 64500], "labels": ["2023.7", "2023.12", "2024.12", "2025.12", "2026.11"], "trend": "down", "show_values": False, "title": "에코프로 수정주가 (네이버)", "at": "+0.3"},
   labels=[lab("꼭대기 대비 약 -75%", "75%", "red")])
sh("counter", 88, value={"from": 0, "to": 87576, "suffix": "억 원", "at": "8조"}, caption="시가총액 (2026년 11월 20일 종가로 계산)", icon="building")
chap("반전", "6장")
sh("closeup", 89, who="m1", side="left", set="home", time="dusk", emotion="calm", pose="explain")
sh("counter", [90, 91], value={"from": 0, "to": 112, "suffix": "억 원", "at": "112억"}, caption="2026년 3분기 연결 영업이익 (보도)", icon="chart_down",
   compare={"text": "1년 전보다 -92.5%", "icon": "warning", "at": "92.5%"})
sh("closeup", 92, who="choi", side="left", set="office", time="night", emotion="worried", pose="think", labels=[lab("전기차 수요 정체 · 광물값 하락 (보도)", "광물", "cream", x=1350, y=860, size=70)])
sh("chart", 93, board="chalk", chart={"type": "bar", "values": [2561, 1236], "labels": ["전기차용", "ESS용"], "suffix": "억 원", "title": "2026년 3분기 에코프로비엠 양극재 매출 (보도)", "show_values": True, "highlight": 1, "at": "+0.3"},
   labels=[lab("ESS 전 분기 대비 +173%", "173%", "lime")])
sh("versus", 94, colors=["#F6C7B6", "#D8F0E4"], left={"who": "choi", "title": "그룹 전체 112억", "emotion": "shocked", "pose": "facepalm", "at": "+0.2"},
   right={"who": "staff", "title": "에코프로에이치엔 113억", "emotion": "excited", "pose": "celebrate", "at": "113억"},
   labels=[lab("113억 원 (보도)", "113억", "lime", x=960, y=900)])
sh("title", 95, text="그룹 전체보다 1억 원 더")
sh("wide", 96, set="street", time="day", shop="환경 공장", tag="처음 사업",
   chars=[ch("staff", 760, "happy", "present", beats=[{"at": "갈라져", "pose": "celebrate", "emotion": "excited"}])],
   props=[{"icon": "factory", "x": 1350, "y": 690, "s": .6, "at": "환경"}],
   labels=[lab("1998년 공기 사업의 뿌리", "공기를", "lime", x=1350, y=260)])
sh("icon", 97, icons=[{"name": "laptop", "text": "반도체", "label": "반도체 호황 (보도)", "at": "+0.2"}, {"name": "chart_up", "label": "주문 증가", "at": "주문이"}])
sh("title", [98, 99], text="그룹을 받친 건, 맨 처음의 공기")
sh("versus", 100, colors=["#E8E0F6", "#CFE3F6"], left={"who": "founder", "title": "창업주 · 은행원 출신", "emotion": "calm", "pose": "present", "at": "창업주가"},
   right={"who": "choi", "title": "지금 대표 · 은행 지점장 출신", "emotion": "confident", "pose": "present_left", "at": "지점장"})
sh("wide", [101, 104], set="office", era="modern", wall="sand", time="day",
   chars=[ch("staff", 600, "happy", "wave"), ch("m1", 960, "happy", "wave"), ch("choi", 1320, "smile", "celebrate")],
   labels=[lab("구독 · 좋아요", "구독과", "lime", x=960, y=230, size=130), lab("출처는 설명란", "출처는", "cream", x=960, y=420)],
   polaroid={"at": "출처는", "who": "staff", "caption": "배터리 회사를 받친 건, 처음의 공기 사업"})

# 빈 화면 방지(2026-11-20 검수): 그래픽 장면의 첫 요소는 장면 시작 직후에 나오게 하고, 나머지만 대사 낱말에 맞춘다
for d in X:
    k = d.get("kind")
    if k == "icon" and d.get("icons"): d["icons"][0]["at"] = "+0.2"
    if k == "table" and d.get("items"): d["items"][0]["at"] = "+0.2"
    if k == "chart" and d.get("chart"): d["chart"]["at"] = "+0.3"
    if k == "counter" and d.get("value"): d["value"]["at"] = "+0.3"

story = {"title": "에코프로_v2", "mood": "dramatic", "cast": {
    "founder": {"skin": "light", "outfit": "suit", "color": "#2E4A8C", "shirt": "#F2F2F2", "tie": "#1F7FC9", "hair": "short", "hair_col": "#3A3A3A", "glasses": True},
    "staff": {"skin": "fair", "outfit": "sweater", "color": "#4FA36B", "hair": "bun", "hair_col": "#2A2420"},
    "worker": {"skin": "tan", "outfit": "hoodie", "color": "#1F6FB2", "hair": "short", "hair_col": "#1E1A18"},
    "kim": {"skin": "olive", "outfit": "suit", "color": "#5A5A66", "tie": "#2E2E36", "hair": "bald"},
    "song": {"skin": "light", "outfit": "suit", "color": "#1F2A3A", "tie": "#7A1E2E", "hair": "slick", "hair_col": "#2A2A2A"},
    "choi": {"skin": "tan", "outfit": "suit", "color": "#2F5A4A", "shirt": "#F2F2F2", "tie": "none", "hair": "short", "hair_col": "#8A8A8A", "glasses": True},
    "m1": {"skin": "fair", "outfit": "sweater", "color": "#8C5E3A", "hair": "curly", "hair_col": "#3A2C22"},
    "investor": {"skin": "fair", "outfit": "tshirt", "color": "#D0703A", "hair": "short", "hair_col": "#1E1A18", "hat": "cap", "hat_col": "#C8242C"},
    "shopper": {"skin": "brown", "outfit": "tshirt", "color": "#6A6A78", "hair": "short", "hair_col": "#1E1A18"},
    "shopper2": {"skin": "fair", "outfit": "sweater", "color": "#8C5EA0", "hair": "long", "hair_col": "#2A2420"}},
  "shots": X}
for d in X:
    if d.get("kind") == "walk":
        for c in d.get("chars", []): c.pop("x", None)
json.dump(story, open(os.path.join(P, "story.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(X), "shots")
