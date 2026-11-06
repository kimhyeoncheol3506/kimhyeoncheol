"""32편 美 중간선거 민주당 압승 이후 경제 영향 — 근거 기반 추론 (HyperFrames + A4 스틱맨)

사용:
  python3 projects/20261105-midterm-aftermath/build.py plan
  python3 projects/20261105-midterm-aftermath/build.py render [ids]
"""
import json
import os
import re
import subprocess
import sys

os.environ.setdefault("HF_LOOK", "sting")  # OPUSCAR 98 No.46 The Sting 룩
os.environ.setdefault("HF_BG", "scenery")  # v1.16.0 정보 패널 뒤 흐린 풍경 + 움직이는 메시 그라데이션
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
PJ = "projects/20261105-midterm-aftermath"

sc = []
_chip = ""
_intro = None


def CH(no, title, chip, name=None):
    """챕터 시작: 다음 장면에 챕터 카드(2초)를 붙인다"""
    global _chip, _intro
    _chip = chip
    _intro = (no, title, name or re.sub(r"[\[\]{}|‹›]", "", title))


def N(t, s="", c="gold", icon="", **kw):
    return dict(t=t, s=s, c=c, icon=icon, **kw)


def S(text, kind, **p):
    S2(text, (None, kind, p))


def S2(text, *parts):
    """한 문장을 여러 그림으로 나눠 보여 줄 때: parts = (해당 구절, kind, params) ... 구절 길이 비율로 시간 배분"""
    global _intro
    n = len(sc) + 1
    d = {"id": f"s{n:03d}", "text": text, "parts": []}
    for seg, kind, p in parts:
        p = dict(p)
        p.setdefault("chip", _chip)
        d["parts"].append({"seg": seg or text, "kind": kind, "p": p})
    if _intro:
        d["parts"][0]["p"]["intro"] = [_intro[0], _intro[1]]
        d["chapter"] = _intro[2]
        _intro = None
    sc.append(d)


def Q(text, *lines, **kw):
    S(text, "quote", lines=list(lines), **kw)


EX = "개념도 · 실제 수치 아님"

# ═════════════ 오프닝 ═════════════
_chip = "오프닝"
S("같은 선거, 정반대 반응이 나왔습니다.", "quote", lines=["같은 선거", "[정반대] 반응"], size=150)
S("미국 중간선거에서 민주당이 상원과 하원을 모두 가져간 다음 날, 다우지수는 3% 가까이 뛰었습니다.", "kpi", kicker="11월 4일 미국 다우지수 (보도)", big="+3%", color="red", unit="중간선거 다음 날 기준 44년 만의 최대 상승", size=250)
S("그런데 하루 뒤 코스피는 5.28% 떨어졌습니다. 삼성전자는 7.57%, SK하이닉스는 9.46% 빠졌습니다.", "compare", headline="같은 선거, [정반대] 반응",
  left=dict(title="미국 (11월 4일)", c="red", rows=["다우 약 +3%", "S&P500 +1.58%"]), right=dict(title="한국 (11월 5일)", c="blue", rows=["코스피 −5.28%", "SK하이닉스 −9.46%"]))
S("오늘은 이 엇갈린 반응을 근거 다섯 개로 풀고, 2027년 내 계좌에 무슨 일이 생길지 합리적으로 추론해 보겠습니다.", "check", headline="오늘의 [순서]",
  items=[dict(t="[사실] — 무슨 일이 있었나", c="gold", no="1"), dict(t="[근거 5개] — 왜 엇갈렸나", c="blue", no="2"), dict(t="[시나리오 3개] — 2027년 예측", c="red", no="3"), dict(t="[신호 5개] — 무엇을 지켜볼까", c="gold", no="4")])

# ═════════════ 1. 사실 ═════════════
CH("01", "무슨 일이 [있었나]", "01 · 사실 — 무슨 일이 있었나", name="사실 — 블루웨이브와 엇갈린 시장")
S("11월 3일 미국 중간선거에서 민주당이 상원과 하원 과반을 모두 차지했습니다. 이른바 블루웨이브입니다.", "kpi", kicker="2026년 11월 3일 미국 중간선거", big="블루웨이브", color="blue", unit="민주당, 상원·하원 모두 과반", size=200)
S("트럼프 대통령은 결과를 받아들이고 민주당과 일하겠다고 밝혔습니다. 대통령 임기는 2029년 1월까지 그대로입니다.", "timeline", headline="대통령은 그대로, [의회]가 바뀌었다",
  events=[dict(when="2026.11", t="중간선거", s="민주당 상·하원 장악", c="blue"), dict(when="2027.1", t="새 의회 출범", s="", c="gold"), dict(when="2029.1", t="트럼프 임기 끝", s="", c="red")])
S("미국 시장은 크게 올랐습니다. 결과를 두고 다툼이 길어질 거라는 걱정이 사라졌기 때문입니다.", "story", scene="news_tv", relabel={">시총 −660조<": ">다우 +3%<", "M1030,260 L1150,280 L1260,300 L1360,330 L1460,450 L1560,520 L1690,560\" fill=\"none\" stroke=\"#5B93B8\"": "M1030,470 L1150,450 L1260,420 L1360,380 L1460,330 L1560,290 L1690,240\" fill=\"none\" stroke=\"#DE5B41\"", "fill=\"#2a0f12\"": "fill=\"#0f1f2a\""})
S("같은 날 국제 유가는 장중 8% 넘게 떨어졌습니다. 이란 전쟁이 끝날 수 있다는 기대가 커졌다는 분석입니다.", "chart", headline="유가, 장중 [−8%] 넘게 (보도)", badge=EX,
  lines=[dict(name="브렌트유", color="blue", pts=[.7, .72, .75, .73, .74, .42], end="급락")])
S2("한국은 달랐습니다. 선거 당일 코스피는 장중 4% 넘게 밀렸다가 겨우 0.62% 오르며 끝났고, 외국인은 하루에 2조 5천억 원을 팔았습니다.",
   ("한국은 달랐습니다. 선거 당일 코스피는 장중 4% 넘게 밀렸다가 겨우 0.62% 오르며 끝났고,", "kpi", dict(kicker="11월 4일 코스피 (한국거래소)", big="5683.80", color="gold", unit="+0.62% · 장중 한때 −4% 넘게", size=200)),
   ("외국인은 하루에 2조 5천억 원을 팔았습니다.", "kpi", dict(kicker="11월 4일 외국인 코스피 순매도 (보도)", big="2조 5천억 원", color="blue", unit="하루 만에", size=190)))
S("다음 날엔 매도 사이드카까지 걸리면서 코스피가 300포인트 떨어진 5383.80에 마감했습니다.", "kpi", kicker="11월 5일 코스피 (한국거래소)", big="−5.28%", color="blue", unit="5383.80 마감 · 매도 사이드카 발동", size=250)
S("외국인은 3조 4천억 원을 팔았고, 개인이 2조 3천억 원을 받아냈습니다.", "compare", headline="11월 5일 누가 [팔고] 누가 샀나",
  left=dict(title="외국인", c="blue", rows=["약 3조 4천억 원", "순매도"]), right=dict(title="개인", c="red", rows=["약 2조 3천억 원", "순매수"]))
Q("같은 뉴스를 보고, 외국인은 반도체를 팔았고 개인은 그 반도체를 샀습니다. 누가 맞았는지는 근거로 따져 봐야 합니다.", "외국인은 팔고, 개인은 샀다", "누가 맞았는지는 [근거]로", size=110)

# ═════════════ 2. 근거 ═════════════
CH("02", "왜 [엇갈렸나]: 근거 다섯 개", "02 · 근거 — 왜 엇갈렸나", name="근거 다섯 개 — 왜 미국은 오르고 한국은 내렸나")
S("첫 번째 근거, 시장은 결과보다 불확실성을 싫어합니다.", "kpi", kicker="근거 1", big="불확실성 해소", color="gold", unit="누가 이겼느냐보다, 끝났다는 사실", size=170)
S("선거 결과를 두고 소송과 다툼이 이어질까 봐 걱정하던 시장이, 대통령의 승복 한마디에 안도한 겁니다.", "story", scene="shield", relabel={">FCF<": ">승복<"})
S("두 번째 근거, 유가입니다. 기름값이 내려가면 물가가 잡히고, 금리를 내릴 여유가 생깁니다.", "flow", headline="근거 2 · [유가]가 내리면",
  nodes=[dict(t="유가 하락", s="전쟁 종료 기대", c="blue", icon="1"), dict(t="물가 부담 감소", s="", c="gold", icon="2"), dict(t="금리 인하 여유", s="성장주에 유리", c="red", icon="3")])
S("미국 소비자에게는 좋은 소식이라, 미국 증시가 먼저 반응했습니다.", "story", scene="cheers")
S("과거 중간선거 직후를 보면 미국 10년물 금리는 평균 0.1%포인트 내리고, 달러지수는 0.62% 약해졌다는 분석도 있습니다.", "compare", headline="과거 중간선거 직후 [금리·달러] (보도)",
  left=dict(title="미국 10년물 금리", c="blue", rows=["평균 약 −0.1%p"]), right=dict(title="달러지수", c="blue", rows=["평균 −0.62%"]))
S("달러가 약해지면 원화에는 숨통이 트입니다. 수입 물가 부담이 줄고, 외국인이 돌아올 명분도 생깁니다.", "flow", headline="달러 약세가 [한국에 주는 것]",
  nodes=[dict(t="달러 약세", s="", c="blue", icon="1"), dict(t="원화 부담 완화", s="수입 물가↓", c="gold", icon="2"), dict(t="외국인 복귀 명분", s="", c="red", icon="3")])
S("세 번째 근거, 코스피는 사실상 반도체 지수입니다. 삼성전자와 SK하이닉스가 코스피 영업이익의 약 65%를 차지합니다.", "dual", headline="근거 3 · 코스피 = [반도체 지수]",
  panels=[dict(title="두 종목 이익 비중 (올해)", color="gold", pts=[.2, .65], tag="65.5%", note="한국투자증권 전망"), dict(title="내년 (전망)", color="red", pts=[.2, .72], tag="71.9%", note="한국투자증권 전망")])
S("그래서 반도체에 나쁜 소식 하나면, 미국이 올라도 코스피는 떨어질 수 있습니다.", "story", scene="two_giants")
S("네 번째 근거, 데이터센터 규제입니다. 민주당은 데이터센터 때문에 전기요금이 오른다며 규제를 예고해 왔습니다.", "kpi", kicker="근거 4", big="데이터센터 규제", color="blue", unit="전기요금 부담을 기업이 지게 하자는 주장", size=150)
S("보도에 따르면 이번에 당선된 주지사 36명 가운데 34명이 데이터센터 규제를 지지하고, 텍사스 새 주지사 당선인은 신규 건설을 멈추자고 했습니다.", "check", headline="데이터센터에 [부는 바람] (보도)",
  items=[dict(t="새 주지사 [36명 중 34명] 규제 지지", c="blue"), dict(t="[텍사스] 당선인: 신규 건설 일시 중단 주장", c="red"), dict(t="민주당 의원 20명: [전면 중단] 법안 지지", c="gold")])
S("미국에서도 같은 신호가 보였습니다. 선거 다음 날 아마존, 마이크로소프트, 애플은 크게 올랐는데 엔비디아는 떨어졌습니다.", "compare", headline="미국도 [AI 하드웨어]만 콕 집었다 (보도)",
  left=dict(title="올랐다", c="red", rows=["아마존", "마이크로소프트·애플"]), right=dict(title="떨어졌다", c="blue", rows=["엔비디아", "AI 반도체"]))
S("시장 전체가 아니라, 데이터센터에 들어가는 반도체만 골라서 걱정한 겁니다.", "quote", lines=["시장 전체가 아니라", "[AI 반도체]만 골라서 걱정"], size=120)
S("데이터센터가 덜 지어지면 메모리 반도체가 덜 팔린다. 외국인은 이 연결 고리를 보고 반도체부터 팔았습니다.", "flow", headline="외국인이 본 [연결 고리]",
  nodes=[dict(t="데이터센터 규제", s="미국 주·의회", c="blue", icon="1"), dict(t="AI 설비투자 둔화?", s="", c="gold", icon="2"), dict(t="메모리 수요 걱정", s="삼성·하이닉스 매도", c="red", icon="3")])
S("다섯 번째 근거가 가장 중요합니다. 법은 의회만으로 만들 수 없습니다.", "kpi", kicker="근거 5", big="거부권", color="red", unit="대통령 서명 없이는 법이 되지 않는다", size=230)
S("민주당이 관세 폐지 법안이나 데이터센터 중단 법안을 통과시켜도, 트럼프 대통령이 거부권을 쓰면 막힙니다.", "story", scene="veto_stamp")
S2("거부권을 뒤집으려면 상원 100석 중 67석, 하원 435석 중 290석, 그러니까 3분의 2가 필요합니다. 이번 결과는 과반이지 3분의 2가 아닙니다.",
   ("거부권을 뒤집으려면 상원 100석 중 67석, 하원 435석 중 290석, 그러니까 3분의 2가 필요합니다.", "compare", dict(headline="거부권을 뒤집으려면 [3분의 2]",
        left=dict(title="상원", c="blue", rows=["100석 중 67석 필요", "민주당: 과반"]), right=dict(title="하원", c="blue", rows=["435석 중 290석 필요", "민주당: 과반"]))),
   ("이번 결과는 과반이지 3분의 2가 아닙니다.", "quote", dict(lines=["이번 결과는 [과반]이지", "{3분의 2}가 아닙니다"], size=120)))
S("결국 2029년까지 미국은 서로 막는 구조, 분할 정부가 됩니다. 큰 법은 쉽게 바뀌지 않는다는 뜻입니다.", "scale", headline="2029년까지 [분할 정부]",
  left=dict(t="의회: 민주당", s="새 법 추진", c="blue"), right=dict(t="대통령: 트럼프", s="거부권", c="red"), tilt=0)

# ═════════════ 3. 추론 ═════════════
CH("03", "그래서 [무엇이] 바뀌나", "03 · 추론 — 무엇이 바뀌나", name="추론 — 연방 법보다 주 정부가 변수")
Q("근거 다섯 개를 합치면, 첫 번째 결론이 나옵니다.", "근거 다섯 개를 합치면", "[첫 번째 결론]", size=120)
S("전국 단위의 데이터센터 중단이나 관세 폐지가 법으로 확정될 가능성은 낮습니다. 거부권 때문입니다.", "signal", headline="결론 1 · 연방 법은 [쉽게 안 바뀐다]",
  lamps=[dict(c="blue", t="관세 폐지 법", s="거부권에 막힐 가능성"), dict(c="blue", t="전국 데이터센터 중단 법", s="거부권에 막힐 가능성")])
S("하지만 주 정부는 다릅니다. 건설 허가와 전기 연결은 주와 전력회사가 정하기 때문에, 대통령 거부권이 닿지 않습니다.", "compare", headline="결론 2 · 진짜 변수는 [주 정부]",
  left=dict(title="연방 의회", c="mute", rows=["법 → 거부권", "변화 느림"]), right=dict(title="주 정부·전력회사", c="red", rows=["허가·전기 연결", "거부권 없음"]))
S("그래서 데이터센터 투자는 사라지기보다 늦어지거나, 규제가 약한 주와 해외로 옮겨갈 가능성이 큽니다.", "flow", headline="결론 3 · 사라지기보다 [옮겨간다]",
  nodes=[dict(t="규제 강한 주", s="허가 지연", c="blue", icon="1"), dict(t="규제 약한 주", s="투자 이동", c="gold", icon="2"), dict(t="미국 밖", s="중동·아시아 등", c="red", icon="3")])
S("한국 반도체는 이미 미국만 보고 장사하지 않습니다. 작년 반도체 수출은 22% 늘어 사상 최대였고, 고객은 전 세계 빅테크입니다.", "kpi", kicker="2025년 한국 반도체 수출 (로이터 보도)", big="+22%", color="red", unit="사상 최대 · 고객은 전 세계 빅테크", size=250)
S("한 증권사 연구원도 미국 밖 수요가 늘 수 있어 반도체는 상대적으로 영향이 작을 거라고 봤습니다.", "quote", lines=["반도체는 미국 밖 수요가 늘 수 있어", "[상대적으로 영향이 작을 것]", "현대차증권 김재승 연구원 발언 요지 (보도)"], size=80)
S("오히려 전력 설비 종목이 더 직접적인 타격을 받을 수 있습니다. 실제로 이날 LS일렉트릭은 13.87% 떨어졌습니다.", "kpi", kicker="11월 5일 전력 설비주 (보도)", big="−13.87%", color="blue", unit="LS일렉트릭 · 데이터센터 규제에 더 직접적", size=240)
S("관세는 어떨까요. 법으로 없애긴 어렵지만, 민주당은 청문회와 예산으로 계속 압박할 겁니다.", "story", scene="hourglass", relabel={">몇 년 뒤<": ">협상 카드<"})
S("수출 기업 입장에서는 관세가 갑자기 더 세질 위험이 줄어든다는 점에서, 장기적으로는 나쁘지 않은 신호입니다.", "scale", headline="관세: 더 세질 위험은 [줄어든다]",
  left=dict(t="관세 폐지", s="가능성 낮음", c="blue"), right=dict(t="관세 추가 인상", s="견제로 부담 커짐", c="red"), tilt=-8)
S("업종별로 보면 그림이 더 선명해집니다. 하나증권은 민주당이 의회를 가져가면 반도체와 함께 2차전지, 신재생에너지가 주목받을 수 있다고 봤습니다.", "compare", headline="업종별 [희비] (하나증권·현대차증권, 보도)",
  left=dict(title="주목받을 수 있는 쪽", c="red", rows=["2차전지", "신재생에너지"]), right=dict(title="단기 조정 가능성", c="blue", rows=["전력 설비", "조선·방산"]))
S("실제로 선거 당일 코스피를 끌어올린 건 2차전지였습니다. 시장은 벌써 업종을 갈아타고 있다는 뜻입니다.", "story", scene="memory_store", relabel={">가격 ↑↑<": ">2차전지 ↑<"})
S("마지막 변수는 돈 문제입니다. 12월 정부 셧다운 위험과 2027년 부채한도 협상이 남아 있습니다.", "timeline", headline="남은 [돈 문제] (보도)",
  events=[dict(when="2026.12", t="셧다운 위험", s="예산 합의 실패 시", c="gold"), dict(when="2027.1", t="새 의회", s="청문회·조사 시작", c="blue"), dict(when="2027", t="부채한도 협상", s="시장 흔들 수 있음", c="red")])

# ═════════════ 4. 역사 ═════════════
CH("04", "역사는 [뭐라고] 말할까", "04 · 역사 — 중간선거 뒤 주가", name="역사 — 중간선거 뒤 주가는 어땠나")
S2("역사도 확인해 보겠습니다. 1950년 이후 미국 중간선거 19번, S&P500은 선거 1년 뒤 19번 모두 올랐고 평균 15.1% 올랐습니다.",
   ("역사도 확인해 보겠습니다. 1950년 이후 미국 중간선거 19번,", "quote", dict(lines=["1950년 이후", "미국 중간선거 [19번]"], size=130)),
   ("S&P500은 선거 1년 뒤 19번 모두 올랐고 평균 15.1% 올랐습니다.", "kpi", dict(kicker="선거 1년 뒤 S&P500 (Pepperstone 분석)", big="19전 19승", color="red", unit="평균 +15.1%", size=220)))
S("코스피도 1982년 이후 11번 중 8번, 선거 한 달 뒤에 올랐습니다. 평균 2.64%입니다.", "dual", headline="코스피, 선거 한 달 뒤 [11번 중 8번] 상승",
  panels=[dict(title="상승한 횟수", color="red", pts=[.2, .73], tag="8번", note="1982~2022년 11번 중 (한국일보 분석)"), dict(title="평균 수익률", color="gold", pts=[.2, .45], tag="+2.64%", note="선거 직전 대비 한 달 뒤")])
S("하지만 이 공식을 그대로 믿으면 안 되는 이유가 있습니다.", "quote", lines=["이 공식을 그대로 믿으면", "[안 되는 이유]"], size=120)
S2("하나증권 분석에 따르면, 선거 전에 이미 많이 오른 해에는 그해 연말까지 평균 2.1% 떨어졌습니다. 올해 미국 증시는 9월 말까지 이미 약 14% 올랐습니다.",
   ("하나증권 분석에 따르면, 선거 전에 이미 많이 오른 해에는 그해 연말까지 평균 2.1% 떨어졌습니다.", "compare", dict(headline="이미 많이 오른 해는 [달랐다] (하나증권)",
        left=dict(title="덜 오른 해", c="red", rows=["연말까지 평균 +8.4%"]), right=dict(title="많이 오른 해", c="blue", rows=["연말까지 평균 −2.1%"]))),
   ("올해 미국 증시는 9월 말까지 이미 약 14% 올랐습니다.", "kpi", dict(kicker="올해 미국 증시, 9월 말까지 (하나증권 보도)", big="+14%", color="red", unit="이미 많이 오른 해", size=250)))
S("2018년이 좋은 예입니다. 그해 민주당이 하원을 되찾았지만, 미중 무역 갈등이 겹치면서 미국 증시는 연말까지 떨어졌습니다.", "timeline", headline="2018년: 선거보다 [무역 갈등]이 셌다",
  events=[dict(when="2018.11", t="민주당 하원 탈환", s="", c="blue"), dict(when="2018.12", t="미중 무역 갈등", s="", c="red"), dict(when="연말", t="미국 증시 하락", s="하나증권 분석", c="blue")])
S("그리고 표본은 고작 열아홉 번입니다. 역사는 방향을 알려 주는 참고서일 뿐, 정답지가 아닙니다.", "story", scene="report_read", relabel={">펀드 보고서<": ">역사 통계<"})

# ═════════════ 5. 시나리오 ═════════════
CH("05", "2027년 [시나리오 세 개]", "05 · 예측 — 시나리오 세 개", name="예측 — 2027년 시나리오 세 개")
S("이제 근거를 모아 2027년을 세 가지로 그려 보겠습니다. 숫자 예측이 아니라, 조건에 따른 방향입니다.", "check", headline="2027년 [세 가지 길]",
  items=[dict(t="[기본] — 서로 막는 미국, 천천히 회복", c="gold", no="A"), dict(t="[나쁜 길] — 주 규제 확산 + 돈 문제", c="blue", no="B"), dict(t="[좋은 길] — 협치 + 유가 안정", c="red", no="C")])
S("기본 시나리오는 분할 정부입니다. 큰 법은 멈추고, 관세는 대부분 유지되며, 유가가 안정되면 물가와 금리 부담이 줄어듭니다.", "flow", headline="A · 기본: [분할 정부]",
  nodes=[dict(t="큰 법 정체", s="거부권", c="mute", icon="1"), dict(t="관세 대부분 유지", s="", c="gold", icon="2"), dict(t="유가 안정 → 금리 여유", s="", c="red", icon="3")])
S("이 경우 코스피는 외국인 매도가 멈추는 시점부터 천천히 회복할 가능성이 큽니다. 반도체 실적이 버텨 준다는 전제에서입니다.", "chart", headline="A · 외국인 매도가 멈추면 [천천히 회복]", badge=EX,
  lines=[dict(name="코스피 (시나리오 A)", color="gold", pts=[.62, .45, .43, .47, .52, .58, .62], end="천천히")])
S("이 길에서 월급쟁이가 확인할 건, 매달 모으는 계획을 하루 뉴스로 바꾸지 않는 것입니다.", "story", scene="calendar_flip", relabel={">12월<": ">매달<", ">31<": ">25<", ">1월<": ">매달<", ">2<": ">25<"})
S("나쁜 시나리오는 텍사스 같은 큰 주들이 실제로 데이터센터 건설을 멈추고, 빅테크가 설비투자를 줄이는 경우입니다.", "story", scene="datacenter")
S("여기에 셧다운이나 부채한도 충돌까지 겹치면, 반도체 비중이 큰 코스피는 한 번 더 크게 흔들릴 수 있습니다.", "chart", headline="B · 나쁜 길: [한 번 더] 흔들림", badge=EX,
  lines=[dict(name="코스피 (시나리오 B)", color="blue", pts=[.62, .45, .5, .38, .3, .36, .42], end="재차 하락")])
S("이 길에서는 반도체 한 업종에만 쏠린 계좌가 가장 크게 흔들립니다. 내 계좌의 반도체 비중부터 확인해야 하는 이유입니다.", "kpi", kicker="시나리오 B에서 확인할 것", big="반도체 비중", color="blue", unit="내 계좌가 한 업종에 얼마나 쏠려 있나", size=190)
S("좋은 시나리오는 대통령과 의회가 협치하고, 전쟁이 끝나 유가가 내려가며, 금리 인하가 빨라지는 경우입니다.", "chart", headline="C · 좋은 길: [협치 + 유가 안정]", badge=EX,
  lines=[dict(name="코스피 (시나리오 C)", color="red", pts=[.62, .45, .55, .63, .7, .76, .82], end="회복")])
S("이 길이라면 이번에 크게 떨어진 업종이 먼저 반등할 수 있습니다. 하나증권도 연말에는 많이 오른 종목보다 낙폭이 큰 종목을 보라고 했습니다.", "kpi", kicker="시나리오 C에서 볼 것 (하나증권 보도)", big="낙폭 과대주", color="red", unit="많이 오른 종목보다 많이 떨어진 종목", size=190)
S("세 시나리오 중 무엇이 될지는, 지금부터 나올 다섯 가지 신호로 알 수 있습니다.", "quote", lines=["어느 길로 갈지는", "[다섯 가지 신호]가 알려 줍니다"], size=110)

# ═════════════ 6. 신호 ═════════════
CH("06", "지켜볼 [신호 다섯 개]", "06 · 신호 — 무엇을 지켜볼까", name="신호 다섯 개와 월급쟁이 대응법")
S("첫째, 외국인 순매도가 멈추는지. 올해 외국인은 코스피에서 약 210조 원을 팔았습니다. 이 흐름이 꺾이는지가 핵심입니다.", "kpi", kicker="신호 1 · 올해 외국인 코스피 순매도 (보도)", big="약 210조 원", color="blue", unit="매도가 멈추는 날이 회복의 출발점", size=200)
S("둘째, 빅테크의 설비투자 계획. 내년 초 실적 발표에서 데이터센터 투자를 줄이는지 보세요.", "kpi", kicker="신호 2", big="빅테크 설비투자", color="gold", unit="내년 초 실적 발표에서 확인", size=170)
S("셋째, 텍사스 같은 큰 주에서 실제로 규제 법이 만들어지는지. 공약과 법은 다릅니다.", "kpi", kicker="신호 3", big="주 정부 규제 법", color="red", unit="공약이 실제 법이 되는지", size=180)
S("넷째, 12월 셧다운과 내년 부채한도. 정부 예산이 멈추거나 나라 빚 한도를 두고 싸우면, 시장은 다시 불확실성을 싫어할 겁니다.", "kpi", kicker="신호 4", big="셧다운 · 부채한도", color="gold", unit="합의되면 안도, 충돌하면 다시 흔들림", size=150)
S("다섯째, 국제 유가. 전쟁이 정말 끝나 유가가 계속 내려가면, 물가와 금리 부담이 줄어 좋은 시나리오에 가까워집니다.", "chart", headline="신호 5 · [국제 유가]", badge=EX,
  lines=[dict(name="유가가 이렇게 가면", color="blue", pts=[.72, .5, .46, .42, .38], end="시나리오 C 쪽"), dict(name="다시 오르면", color="red", pts=[.72, .5, .55, .63, .7], end="시나리오 B 쪽")])
S("다섯 신호를 한 장에 정리하면 이렇습니다.", "check", headline="지켜볼 [신호 다섯 개]",
  items=[dict(t="[외국인] 순매도 멈춤", c="blue", no="1"), dict(t="[빅테크] 설비투자 유지", c="gold", no="2"), dict(t="[주 정부] 규제 법 여부", c="red", no="3"), dict(t="[셧다운·부채한도] 합의", c="gold", no="4"), dict(t="[유가] 안정", c="blue", no="5")])
S("그리고 월급쟁이가 지금 할 일은 하나입니다. 하루 폭락에 놀라 파는 게 아니라, 내 계좌가 반도체 한 업종에 얼마나 쏠려 있는지 확인하는 겁니다.", "story", scene="check_account")
Q("선거는 하루에 끝나지만, 정책은 2년 동안 이어집니다.", "선거는 하루에 끝나지만", "[정책은 2년] 동안 이어집니다", size=110)
S("오늘 영상이 도움이 되셨다면 구독과 좋아요 부탁드립니다. 감사합니다.", "story", scene="wave")


# ═════════════ 출력 ═════════════
def project(clip_paths=None):
    scenes = []
    for s in sc:
        d = {"id": s["id"], "text": s["text"], "visual": {"type": "clip", "path": (clip_paths or {}).get(s["id"], f"{PJ}/clips/_pending.mp4")}}
        if s.get("chapter"):
            d["chapter"] = s["chapter"]
        scenes.append(d)
    meta = json.load(open(os.path.join(HERE, "meta.json"), encoding="utf-8"))
    return dict(meta, scenes=scenes)


def render_all(only=None):
    import hf_econ as H
    sys.path.insert(0, ROOT)
    from studio import tts
    pj = json.load(open(os.path.join(HERE, "project.json"), encoding="utf-8"))
    audio_dir = os.path.join(HERE, "audio")
    clips_dir = os.path.join(HERE, "clips")
    os.makedirs(clips_dir, exist_ok=True)
    paths = {}
    by_id = {s["id"]: s for s in pj["scenes"]}
    for i, s in enumerate(sc):
        if only and s["id"] not in only:
            continue
        scene = by_id[s["id"]]
        audio, real = tts.scene_audio(scene, pj, audio_dir, False)
        nxt = sc[i + 1] if i + 1 < len(sc) else None
        sp = float(pj.get("scene_pause", 0.30))
        pause = max(0.45, sp + 0.2) if nxt and nxt.get("chapter") else sp
        T = round((tts.duration(audio) + pause) * 30) / 30
        parts = s["parts"]
        tot = sum(len(re.sub(r"\s", "", p["seg"])) for p in parts)
        outs = []
        for k, part in enumerate(parts):
            frac = len(re.sub(r"\s", "", part["seg"])) / tot
            Dp = round(T * frac * 30) / 30
            if k == len(parts) - 1:
                Dp = round((T - sum(round(T * len(re.sub(r"\s", "", q["seg"])) / tot * 30) / 30 for q in parts[:-1])) * 30) / 30
            if part["p"].get("intro"):
                Dp = max(Dp, 3.0)
            outs.append(H.render(os.environ.get("HF_ROOT", "/home/user/hf/crisis"), f"{s['id']}p{k}", part["kind"], part["p"], Dp, os.path.join(clips_dir, "parts")))
        if len(outs) == 1:
            final = os.path.join(clips_dir, f"{s['id']}.mp4")
            if not os.path.exists(final) or os.path.realpath(final) != os.path.realpath(outs[0]):
                subprocess.run(["cp", outs[0], final], check=True)
        else:
            final = os.path.join(clips_dir, f"{s['id']}.mp4")
            lst = final + ".txt"
            open(lst, "w").write("".join(f"file '{o}'\n" for o in outs))
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", final], check=True)
        paths[s["id"]] = f"{PJ}/clips/{s['id']}.mp4"
        print(f"{s['id']} {T:.1f}s {[p['kind'] for p in parts]}", flush=True)
    return paths


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "plan"
    if cmd == "plan":
        json.dump(project(), open(os.path.join(HERE, "project.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("scenes:", len(sc), "chars:", sum(len(re.sub(r"\s", "", s["text"])) for s in sc))
    elif cmd == "render":
        only = set(sys.argv[2].split(",")) if len(sys.argv) > 2 else None
        paths = render_all(only)
        allp = {s["id"]: f"{PJ}/clips/{s['id']}.mp4" for s in sc}
        json.dump(project(allp), open(os.path.join(HERE, "project.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
