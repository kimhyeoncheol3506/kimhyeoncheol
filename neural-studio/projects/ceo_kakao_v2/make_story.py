#!/usr/bin/env python3
"""카카오 v2 스토리보드."""
import json, os
P = os.path.dirname(os.path.abspath(__file__)); X = []
def sh(kind, s, **k):
    d = {"kind": kind}
    if s is not None: d["s"] = s if isinstance(s, list) else [s]
    d.update(k); X.append(d)
def lab(text, at, color="lime", **k): return dict(text=text, at=at, color=color, **k)
def ch(id, x, emotion="neutral", pose="idle", **k): return dict(id=id, x=x, emotion=emotion, pose=pose, **k)
def chap(t, n): sh("title", None, text=t, sub=n, hold=1.6)

# 인트로 · 역대 최대 이익과 5분의 1 주가의 역설
sh("counter", [0, 1], value={"from": 0, "to": 7320, "suffix": "억 원", "at": "7,320억"}, caption="2025년 영업이익 · 창사 이래 최대 (DART)", icon="trophy",
   compare={"text": "1년 새 +48%", "icon": "chart_up", "at": "48%"})
sh("chart", [2, 3], board="chalk", chart={"type": "bar", "values": [169500, 30650], "labels": ["2021.6.23", "2026.11.20"], "suffix": "원", "title": "카카오 주가 (종가, 네이버)", "show_values": True, "highlight": 1, "at": "주가는"},
   labels=[lab("5분의 1도 안 됨", "5분의", "red")])
sh("skyline", 4, time="day", labels=[lab("카카오", "카카오입니다", size=180)])
chap("판돈", "1장")
sh("wide", [5, 6], set="office", era="old", wall="sand", time="day", tag="1998년 · 서울",
   chars=[ch("kim", 860, "confident", "present", beats=[{"at": "한게임을", "pose": "celebrate", "emotion": "excited"}])],
   props=[{"icon": "laptop", "x": 1450, "y": 690, "s": .6, "at": "온라인"}],
   lower_third={"name": "김범수", "sub": "카카오 창업자", "at": "김범수는"}, labels=[lab("한게임", "한게임을", "gold", x=1450, y=280)])
sh("icon", 7, icons=[{"name": "handshake", "label": "한게임 + 네이버", "at": "네이버와"}, {"name": "building", "label": "NHN 공동대표", "at": "공동대표에"}])
sh("walk", [8, 9], set="street", time="dusk", chars=[ch("kim", 0, "confident", "hold")],
   labels=[lab("큰 회사를 떠나", "떠나", "cream", x=960, y=250), lab("아이위랩", "아이위랩이었습니다", "lime", x=960, y=400, size=110)])
sh("closeup", 10, who="kim", side="left", set="office", time="night", emotion="worried", pose="think",
   labels=[lab("가입자 3만~4만 명", "3만", "red", x=1350, y=860, size=100)])
sh("table", [11, 12], hand="kim", items=[{"type": "phone", "messages": ["카카오톡 출시!", "공짜로 보내기"], "at": "+0.2"}],
   stamp={"text": "2010년 3월", "at": "카카오톡입니다", "color": "red"})
sh("icon", 13, icons=[{"name": "phone", "text": "0원", "label": "공짜 메시지", "at": "공짜로"}, {"name": "heart", "label": "단체방", "at": "단체방까지"}])
sh("counter", 14, value={"from": 0, "to": 1000, "suffix": "만 명", "at": "1,000만"}, caption="카카오톡 가입자 · 출시 1년 만 (보도)", icon="phone")
sh("closeup", [15, 16], who="m1", side="left", set="home", time="night", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "왜 5분의 1?", "at": "주가는", "thought": True}, labels=[lab("국민 앱인데?", "국민이", "red", x=1350, y=860, size=100)])
sh("icon", 17, icons=[{"name": "book", "text": "성적표", "label": "끝에 공개", "at": "성적표를"}], stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("wide", [18, 19], set="office", era="modern", wall="grey", time="dusk",
   chars=[ch("kim", 760, "worried", "shrug", beats=[{"at": "모았지만", "pose": "present", "emotion": "calm"}, {"at": "벌지", "pose": "stressed", "emotion": "nervous"}])],
   props=[{"icon": "moneybag", "x": 1450, "y": 690, "s": .55, "at": "돈은"}],
   labels=[lab("사람은 모았다", "사람은", "lime", x=1400, y=260), lab("돈은 못 벌었다", "벌지", "red", x=1400, y=420)])
sh("table", [20, 21], hand="kim", items=[{"type": "contract", "title": "합병 계약", "text": "카카오 + 다음커뮤니케이션", "at": "+0.2", "stamp": {"text": "2014년 10월", "at": "합병합니다"}}],
   labels=[lab("큰 판", "판을", "gold")])
sh("counter", 22, value={"from": 0, "to": 22.23, "suffix": "%", "at": "22.23%였습니다"}, caption="합병 뒤 김범수 지분 · 최대주주 (DART)", icon="trophy")
sh("icon", 23, icons=[{"name": "building", "label": "다음카카오", "at": "다음카카오였다가"}, {"name": "building", "label": "2015년 9월 카카오", "at": "카카오로"}])
chap("결정", "2장")
sh("closeup", 24, who="kim", side="right", set="office", time="day", emotion="excited", pose="point",
   bubble={"who": "kim", "text": "다음은 음악", "icon": "bulb", "at": "음악이었습니다"})
sh("table", [25, 26], hand="kim", items=[{"type": "contract", "title": "지분 인수 계약", "text": "로엔엔터테인먼트(멜론) 76.4%", "at": "+0.2", "stamp": {"text": "1조 8,700억 원", "at": "8,700억"}}],
   labels=[lab("2016년 1월", "로엔엔터테인먼트를", "gold"), lab("역대 최대 인수 (보도)", "역대", "red")])
sh("icon", 27, icons=[{"name": "car", "label": "택시", "at": "택시"}, {"name": "coins", "label": "은행 · 결제", "at": "은행"}, {"name": "laptop", "label": "게임 · 웹툰", "at": "게임"}])
sh("walk", 28, set="street", time="day", chars=[ch("kim", 0, "happy", "present")],
   labels=[lab("카카오톡이라는 큰길", "큰길", "lime", x=960, y=250), lab("가게를 하나씩", "가게를", "gold", x=960, y=400)])
sh("crowd", 29, count=24, emotion="excited", set="street", labels=[lab("시장이 열광", "열광했습니다", "gold", size=110)])
sh("chart", 30, board="white", chart={"type": "bar", "values": [63.57, 64.15], "labels": ["네이버", "카카오"], "suffix": "조 원", "title": "2021.6.15 시가총액 (보도)", "show_values": True, "highlight": 1, "at": "네이버를"},
   labels=[lab("코스피 시총 3위", "3위에", "red")])
sh("counter", 31, value={"from": 0, "to": 169500, "suffix": "원", "at": "16만"}, caption="2021년 6월 23일 종가 · 역대 최고 (네이버)", icon="chart_up")
sh("icon", 32, icons=[{"name": "trophy", "text": "75조", "label": "그날 시가총액 약 75조 원 (계산)", "at": "75조"}])
sh("closeup", [33, 35], who="m1", side="right", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "가장 위험한 건?", "at": "위험한", "thought": True}, labels=[lab("답은 안에", "안에", "red", x=600, y=860, size=110)])
chap("위기", "3장")
sh("icon", 36, icons=[{"name": "calendar", "top": "2021", "text": "12월", "label": "첫 번째 금", "at": "+0.2"}])
sh("table", [37, 38], items=[{"type": "newspaper", "title": "카카오페이 (보도)", "text": "상장 한 달, 경영진 8명 주식 매도", "at": "+0.2", "ring_at": "먹튀"}],
   stamp={"text": "약 900억 원", "at": "900억", "color": "red"})
sh("wide", [39, 40], set="office", era="modern", wall="blue", time="night", tag="2022년 10월 15일 · 판교",
   chars=[ch("sci", 760, "shocked", "stressed")],
   props=[{"icon": "laptop", "x": 1300, "y": 690, "s": .55, "at": "서버가"}, {"icon": "warning", "x": 1600, "y": 690, "s": .6, "at": "불이"}],
   stamp={"text": "데이터센터 화재", "at": "불이", "color": "red"})
sh("icon", 41, icons=[{"name": "phone", "label": "카카오톡", "at": "카카오톡과"}, {"name": "coins", "label": "결제", "at": "결제"}, {"name": "car", "label": "택시 호출", "at": "택시"}],
   stamp={"text": "한꺼번에 멈춤", "at": "멈췄습니다", "color": "red"})
sh("closeup", 42, who="m2", side="left", set="office", time="day", emotion="sad", pose="idle",
   lower_third={"name": "남궁훈", "sub": "당시 카카오 각자대표", "at": "남궁훈"}, labels=[lab("나흘 뒤 사임", "물러납니다", "red", x=1350, y=860)])
sh("versus", [43, 46], colors=["#D9D9E6", "#FFF1A8"], left={"who": "rival", "title": "하이브 · 주당 12만 원", "emotion": "confident", "pose": "present", "at": "12만"},
   right={"who": "exec", "title": "카카오 · 주당 15만 원", "emotion": "excited", "pose": "point", "at": "15만"},
   labels=[lab("SM엔터테인먼트 인수전", "SM엔터테인먼트를", "gold", x=960, y=900)])
sh("counter", 47, value={"from": 0, "to": 39.87, "suffix": "%", "at": "39.87%를"}, caption="카카오 + 카카오엔터테인먼트 SM 지분 (보도)", icon="trophy",
   compare={"text": "최대주주", "icon": "target", "at": "최대주주가"})
sh("closeup", 48, who="exec", side="right", set="office", time="night", emotion="worried", pose="stressed", labels=[lab("커다란 청구서", "청구서가", "red", x=600, y=860, size=110)])
sh("table", 49, items=[{"type": "receipt", "title": "2023년 영업권 손상 (보도)", "rows": [["카카오엔터 쪽", "9,245억"], ["그 밖", "5,588억"]], "text": "1조 4,833억", "at": "+0.2"}],
   stamp={"text": "값을 다시 매김", "at": "4,833억", "color": "red"})
sh("counter", 50, value={"from": 0, "to": 18167, "suffix": "억 원", "at": "8,167억"}, caption="2023년 순손실 (DART)", icon="chart_down")
sh("title", 51, text="그리고 법정으로")
sh("table", [52, 53], items=[{"type": "newspaper", "title": "검찰의 시각 (혐의)", "text": "하이브 공개매수 저지 목적 주가 조종 혐의", "at": "+0.2"},
                             {"type": "letter", "title": "2023년 11월", "text": "카카오 법인·임원 기소", "at": "넘겨집니다"}])
sh("icon", [54, 55], icons=[{"name": "calendar", "top": "2024", "text": "7월", "label": "구속", "at": "구속되고"}, {"name": "calendar", "top": "2024", "text": "8월", "label": "기소", "at": "다음"}, {"name": "calendar", "top": "2024", "text": "10월", "label": "보석", "at": "보석으로"}])
sh("wide", [56, 57], set="board", time="day", tag="2025년 10월 21일",
   chars=[ch("kim", 700, "calm", "idle"), ch("exec", 1150, "calm", "idle")],
   stamp={"text": "1심 무죄", "at": "무죄를", "color": "green"}, labels=[lab("검찰 항소", "항소했습니다", "red", x=1450, y=260)])
chap("베팅", "4장")
sh("walk", 58, set="street", time="day", chars=[ch("jung", 0, "confident", "hold")], labels=[lab("사람을 바꾼다", "사람을", "cream", x=960, y=250)])
sh("wide", [59, 60], set="office", era="modern", wall="teal", time="day", chars=[ch("jung", 900, "confident", "present")],
   lower_third={"name": "정신아", "sub": "카카오 대표이사 (2024년 3월~)", "at": "정신아가"}, labels=[lab("카카오벤처스 대표 출신", "카카오벤처스를", "gold", x=1400, y=260)])
sh("closeup", 61, who="jung", side="left", set="office", time="day", emotion="confident", pose="arms_crossed",
   bubble={"who": "jung", "text": "가지치기", "icon": "target", "at": "가지치기였습니다"})
sh("chart", 62, board="white", chart={"type": "bar", "values": [175, 158, 146, 121], "labels": ["2023말", "2024말", "2025말", "2026.9말"], "suffix": "개", "title": "연결 종속회사 수 (DART)", "show_values": True, "highlight": 3, "at": "175개였던"})
sh("table", 63, hand="jung", items=[{"type": "contract", "title": "영업양도", "text": "다음 포털 사업 → 새 회사", "at": "+0.2", "stamp": {"text": "2025년 12월", "at": "넘깁니다"}}])
sh("icon", 64, icons=[{"name": "laptop", "text": "게임", "label": "카카오게임즈", "at": "카카오게임즈의"}, {"name": "handshake", "label": "최대주주 → 라인야후 쪽 (보도)", "at": "라인야후"}])
sh("chart", 65, board="chalk", chart={"type": "bar", "values": [37.93, 14.68], "labels": ["매각 전", "매각 뒤"], "suffix": "%", "title": "카카오의 카카오게임즈 지분 (보도)", "show_values": True, "highlight": 1, "at": "37.93%에서"})
sh("closeup", 66, who="jung", side="right", set="office", time="day", emotion="excited", pose="point",
   bubble={"who": "jung", "text": "AI", "icon": "brain", "at": "인공지능"})
sh("icon", 67, icons=[{"name": "handshake", "label": "오픈AI와 손잡고", "at": "오픈AI와"}, {"name": "phone", "text": "AI", "label": "카카오톡 안에 챗GPT", "at": "챗GPT를"}])
sh("counter", 68, value={"from": 0, "to": 1100, "suffix": "만 명", "at": "1,100만"}, caption="챗GPT 포 카카오 누적 가입자 (2026년 5월, 보도)", icon="phone")
sh("title", 69, text="회사를 둘로")
sh("table", 70, hand="jung", items=[{"type": "contract", "title": "회사분할 결의", "text": "카카오에이아이 / 카카오엑스", "at": "+0.2", "stamp": {"text": "2026년 8월 21일", "at": "결의합니다"}}])
sh("versus", 71, colors=["#FFF1A8", "#D9E2F0"], left={"who": "sci", "title": "카카오에이아이 · 카톡과 AI", "emotion": "excited", "pose": "present", "at": "카카오톡과"},
   right={"who": "exec", "title": "카카오엑스 · 계열사 관리·투자", "emotion": "calm", "pose": "hold", "at": "카카오엑스가"})
sh("icon", 72, icons=[{"name": "calendar", "top": "2027", "text": "2.1", "label": "분할 예정일", "at": "+0.2"}, {"name": "hourglass", "label": "주주총회 남음", "at": "주주총회가"}])
sh("counter", [73, 74], value={"from": 0, "to": 80991, "suffix": "억 원", "at": "8조"}, caption="2025년 매출 · 역대 최대 (DART)", icon="trophy")
sh("icon", 75, icons=[{"name": "trophy", "text": "2,770억", "label": "2026년 2분기 영업이익 · 분기 최대 (카카오)", "at": "2,770억"}])
sh("closeup", 76, who="m1", side="left", set="home", time="day", emotion="shocked", pose="facepalm", labels=[lab("주가는 반대로", "반대로", "red", x=1350, y=860, size=110)])
sh("chart", [77, 78], board="white", chart={"type": "bar", "values": [60100, 30650], "labels": ["2025.12.30", "2026.11.20"], "suffix": "원", "title": "카카오 주가 (종가, 네이버)", "show_values": True, "highlight": 1, "at": "6만"},
   labels=[lab("-49%", "49%", "red", size=130)])
sh("counter", 79, value={"from": 0, "to": 15250, "suffix": "원", "at": "5,250원이"}, caption="2026년 3월 3~4일 이틀 하락폭 (네이버로 계산)", icon="chart_down")
sh("chart", 80, board="chalk", chart={"type": "bar", "values": [38700, 35800], "labels": ["8.20", "8.21 분할 결의"], "suffix": "원", "title": "분할 결의일 주가 (네이버)", "show_values": True, "highlight": 1, "at": "8월"},
   labels=[lab("하루 -7.49%", "7.49%", "red")])
sh("closeup", 81, who="sci", side="right", set="office", time="night", emotion="nervous", pose="think",
   bubble={"who": "sci", "text": "AI는 언제 돈이 될까?", "at": "확신하지", "thought": True}, labels=[lab("시장의 분석 (보도)", "분석이", "cream", x=600, y=860)])
chap("성적표", "5장")
sh("closeup", [82, 83], who="m1", side="right", set="home", time="day", emotion="thinking", pose="think",
   bubble={"who": "m1", "text": "주인은 누구?", "at": "주인은", "thought": True})
sh("wide", [84, 85], set="office", era="modern", wall="plum", time="day", chars=[ch("kim", 900, "calm", "present")],
   labels=[lab("여전히 최대주주", "여전히", "gold", x=1400, y=260), lab("특수관계인 합계 24%", "24%입니다", "lime", x=1400, y=420)])
sh("icon", 86, icons=[{"name": "building", "label": "2022년 3월 이사회 퇴진", "at": "+0.2"}, {"name": "brain", "label": "미래이니셔티브센터장 (미등기)", "at": "미래이니셔티브센터장입니다"}])
sh("closeup", 87, who="jung", side="left", set="office", time="day", emotion="smile", pose="present", labels=[lab("2026년 3월 연임", "연임됐습니다", "lime", x=1350, y=860)])
sh("icon", [88, 89], icons=[{"name": "book", "text": "성적표", "label": "카카오 성적표", "at": "성적표를"}, {"name": "phone", "text": "0원", "label": "시작은 공짜 메신저", "at": "공짜"}],
   stamp={"text": "숫자로만", "at": "숫자로만", "color": "red"})
sh("table", [90, 91], items=[{"type": "receipt", "title": "김범수의 판 · 잘한 결정", "rows": [["2010년 3월", "카카오톡"], ["1년 만에", "1,000만 명"]], "text": "가입자 1,000만", "at": "+0.2"}],
   stamp={"text": "최고의 결정", "at": "1,000만", "color": "green"})
sh("counter", 92, value={"from": 0, "to": 75, "suffix": "조 원", "at": "75조"}, caption="2021년 6월 23일 시가총액 (계산)", icon="building")
sh("table", [93, 94], items=[{"type": "receipt", "title": "가장 비싼 숫자", "rows": [["2023년", "영업권 손상"]], "text": "1조 4,833억", "at": "+0.2"}],
   stamp={"text": "인수의 청구서", "at": "4,833억", "color": "red"})
sh("chart", 95, board="white", chart={"type": "bar", "values": [18700, 2314], "labels": ["멜론 인수", "멜론 손상(2023)"], "suffix": "억 원", "title": "멜론 (보도)", "show_values": True, "highlight": 1, "at": "멜론에서도"})
sh("closeup", 96, who="jung", side="right", set="office", time="day", emotion="calm", pose="present", labels=[lab("정신아의 판", "정신아의", "gold", x=600, y=860, size=110)])
sh("chart", [97, 98], board="chalk", chart={"type": "bar", "values": [54400, 30650], "labels": ["2024.3.28 취임일", "2026.11.20"], "suffix": "원", "title": "카카오 주가 (종가, 네이버)", "show_values": True, "highlight": 1, "at": "취임"},
   labels=[lab("약 -44%", "44%", "red")])
sh("counter", [99, 100], value={"from": 4953, "to": 7320, "suffix": "억 원", "at": "7,320억"}, caption="영업이익 2024년 → 2025년 (DART)", icon="chart_up",
   compare={"text": "역대 최대", "icon": "trophy", "at": "역대"})
sh("table", [101, 102], items=[{"type": "receipt", "title": "정신아의 판 · 잘한 결정", "rows": [["2023년 말", "175개"], ["2026년 9월 말", "121개"]], "text": "연결 종속회사 -54개", "at": "+0.2"}],
   stamp={"text": "가지치기", "at": "54개", "color": "green"})
sh("counter", [103, 104], value={"from": 0, "to": 135780, "suffix": "억 원", "at": "13조"}, caption="시가총액 (2026년 11월 20일 종가로 계산)", icon="building",
   compare={"text": "꼭대기의 18%", "icon": "chart_down", "at": "꼭대기의"})
chap("반전", "6장")
sh("closeup", 105, who="m1", side="left", set="home", time="dusk", emotion="calm", pose="explain")
sh("table", 106, items=[{"type": "newspaper", "title": "2026.11.20 (보도)", "text": "서울고법 항소심도 무죄", "at": "+0.2"}],
   stamp={"text": "2심 무죄", "at": "무죄를", "color": "green"})
sh("closeup", [107, 108], who="kim", side="left", set="office", time="day", emotion="calm", pose="arms_crossed",
   labels=[lab("전 임원도 무죄 (보도)", "임원도", "lime", x=1350, y=300), lab("상고 여부 미정", "상고할지는", "cream", x=1350, y=860)])
sh("chart", [109, 110], board="white", chart={"type": "bar", "values": [62300, 30650], "labels": ["1심 무죄 날", "2심 무죄 날"], "suffix": "원", "title": "그날의 카카오 주가 (종가, 네이버)", "show_values": True, "highlight": 1, "at": "1심에서"},
   labels=[lab("2025.10.21 → 2026.11.20", "2심에서", "cream")])
sh("versus", 111, colors=["#D8F0D8", "#F6C7B6"], left={"who": "kim", "title": "법정 · 1심 2심 무죄", "emotion": "calm", "pose": "present", "at": "짐은"},
   right={"who": "m1", "title": "주가 · 절반", "emotion": "shocked", "pose": "facepalm", "at": "절반이"})
sh("closeup", 112, who="sci", side="right", set="office", time="day", emotion="thinking", pose="think",
   bubble={"who": "sci", "text": "AI는 언제 돈이 되나?", "at": "AI가", "thought": True})
sh("walk", 113, set="street", time="dusk", chars=[ch("jung", 0, "confident", "hold")],
   labels=[lab("공짜로 국민을 모은 회사", "국민을", "gold", x=960, y=250), lab("숙제: 공짜 앱으로 돈 벌기", "숙제는", "lime", x=960, y=400)])
sh("wide", [114, 117], set="office", era="modern", wall="sand", time="day",
   chars=[ch("kim", 600, "happy", "wave"), ch("m1", 960, "happy", "wave"), ch("jung", 1320, "smile", "celebrate")],
   labels=[lab("구독 · 좋아요", "구독과", "lime", x=960, y=230, size=130), lab("출처는 설명란", "출처는", "cream", x=960, y=420)],
   polaroid={"at": "출처는", "who": "jung", "caption": "국민 메신저, 숙제는 AI로 돈 벌기"})

# 빈 화면 방지(2026-11-20 검수): 그래픽 장면의 첫 요소는 장면 시작 직후에 나오게 하고, 나머지만 대사 낱말에 맞춘다
for d in X:
    k = d.get("kind")
    if k == "icon" and d.get("icons"): d["icons"][0]["at"] = "+0.2"
    if k == "table" and d.get("items"): d["items"][0]["at"] = "+0.2"
    if k == "chart" and d.get("chart"): d["chart"]["at"] = "+0.3"
    if k == "counter" and d.get("value"): d["value"]["at"] = "+0.3"

story = {"title": "카카오_v2", "mood": "upbeat", "cast": {
    "kim": {"skin": "light", "outfit": "sweater", "color": "#3A4A6A", "hair": "short", "hair_col": "#2A2A2A", "glasses": True},
    "jung": {"skin": "fair", "outfit": "suit", "color": "#2F6F8F", "shirt": "#F2F2F2", "tie": "none", "hair": "long", "hair_col": "#2A2420"},
    "m1": {"skin": "fair", "outfit": "hoodie", "color": "#E0B23A", "hair": "curly", "hair_col": "#3A2C22"},
    "m2": {"skin": "olive", "outfit": "suit", "color": "#6A6A78", "tie": "#2E2E36", "hair": "short", "hair_col": "#3A3A3A"},
    "exec": {"skin": "tan", "outfit": "suit", "color": "#4A3A2E", "shirt": "#F2F2F2", "tie": "#C8A020", "hair": "slick", "hair_col": "#1E1A18"},
    "rival": {"skin": "light", "outfit": "suit", "color": "#2A2A36", "shirt": "#F2F2F2", "tie": "#5A5A70", "hair": "bald"},
    "sci": {"skin": "light", "outfit": "hoodie", "color": "#5E8C6A", "hair": "short", "hair_col": "#3A2C22", "glasses": True}},
  "shots": X}
for d in X:
    if d.get("kind") == "walk":
        for c in d.get("chars", []): c.pop("x", None)
json.dump(story, open(os.path.join(P, "story.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(len(X), "shots")
