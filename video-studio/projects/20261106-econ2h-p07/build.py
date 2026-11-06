"""33편 경제 지식 2시간 완전정리 — 7부 (선진국). 8부로 나눠 만든 뒤 합친다.
사용: python3 projects/20261106-econ2h-p07/build.py plan | render [ids]
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
PJ = "projects/20261106-econ2h-p07"

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

# ═════════════ 7강 선진국 ═════════════
CH("7강", "선진국, [잘사는 나라]의 조건", "7강 · 선진국 — 잘사는 나라의 조건", name="7강 선진국 — 잘사는 나라의 조건")
S("일곱 번째 이야기는 조금 큰 질문입니다. 부자가 되는 가장 빠른 방법이 뭘까요?", "qa", q="부자가 되는\n[가장 빠른 방법]은?")
S("농담 같지만, 경제학자들의 답은 이렇습니다. 부유한 나라에서 태어나는 것.", "quote", lines=["가장 빠른 방법은", "[부유한 나라]에서 태어나는 것"], size=120)
S("세계의 불평등을 연구한 경제학자 브랑코 밀라노비치는, 어느 나라에서 태어났느냐가 평생 소득의 절반 이상을 결정한다고 주장했습니다.", "kpi", kicker="경제학자 브랑코 밀라노비치", big="절반 이상", color="red", unit="태어난 나라가 평생 소득을 좌우한다", size=240)
S("같은 능력, 같은 노력을 가진 사람이라도 어느 나라에서 일하느냐에 따라 버는 돈이 몇 배, 몇십 배씩 차이가 납니다. 개인의 노력보다 나라라는 무대가 훨씬 크다는 거죠.", "dual", headline="같은 노력, [다른 무대]", badge=EX,
  panels=[dict(title="부유한 나라", color="red", pts=[.3, .85], tag="몇십 배", note="같은 일을 해도"), dict(title="가난한 나라", color="blue", pts=[.3, .32], tag="기준", note="같은 능력·노력")])
S("그럼 잘사는 나라와 그렇지 못한 나라는 무엇이 다를까요? 오늘은 세 나라의 이야기로 풀어 보겠습니다. 영국, 한국, 그리고 아르헨티나.", "check", headline="세 나라의 [이야기]",
  items=[dict(t="[영국] — 처음으로 부자가 된 나라", c="gold", no="1"), dict(t="[한국] — 가장 빨리 따라잡은 나라", c="red", no="2"), dict(t="[아르헨티나] — 부자였다가 미끄러진 나라", c="blue", no="3")])
S("먼저 영국입니다. 18세기 후반, 인류 역사상 처음으로 한 나라가 가난의 굴레에서 벗어나기 시작합니다. 산업혁명이죠.", "kpi", kicker="18세기 후반 영국", big="산업혁명", color="gold", unit="인류가 처음 가난의 굴레를 벗어난 사건", size=230)
S("그 전까지 수천 년 동안 인류의 생활 수준은 거의 제자리였습니다. 그런데 산업혁명 이후 몇백 년 사이에 소득이 수십 배로 뛰었어요. 그래프로 그리면 하키 스틱처럼 꺾이죠.", "chart", headline="인류 소득의 [하키 스틱]", badge=EX,
  lines=[dict(name="1인당 소득", color="red", pts=[.1, .1, .1, .1, .11, .12, .2, .45, .85], end="산업혁명 이후")], marks=[dict(x=.7, text="1800년 전후", color="gold")])
S("왜 하필 영국이었을까요? 경제사학자들은 여러 가지 우연이 겹쳤다고 봅니다.", "qa", q="왜 하필\n[영국]이었을까?")
S("첫 번째 우연은 석탄입니다. 영국에는 땅만 파면 나오는 값싼 석탄이 아주 많았어요. 기계를 돌릴 에너지가 싸게 널려 있었던 거죠.", "kpi", kicker="우연 ①", big="값싼 석탄", color="gold", unit="기계를 돌릴 에너지가 싸게 널려 있었다", size=240)
S("두 번째는 비싼 임금입니다. 당시 영국은 무역으로 돈이 돌아서 노동자 임금이 다른 나라보다 높았어요. 사람이 비싸고 석탄이 싸면, 사람 대신 기계를 쓰는 게 이득이죠.", "scale", headline="사람은 비싸고 [석탄은 싸다]",
  left=dict(t="노동자 임금", s="비쌈", c="red"), right=dict(t="석탄 에너지", s="쌈", c="gold"), tilt=-12)
S("그래서 영국 사업가들은 기계를 만들고 개량하는 데 돈을 썼습니다. 다른 나라에서는 사람을 쓰는 게 더 싸서 굳이 기계를 만들 이유가 적었고요.", "story", scene="fab_korea")
S("세 번째는 제도입니다. 1688년 명예혁명 이후 영국에서는 왕이라도 함부로 개인의 재산을 빼앗을 수 없게 됐습니다. 발명하면 특허로 보호받을 수 있었고요.", "timeline", headline="영국을 만든 [제도]",
  events=[dict(when="1688", t="명예혁명", s="왕의 권력 제한", c="gold"), dict(when="1700년대", t="재산권·특허 보호", s="", c="blue"), dict(when="1760~", t="산업혁명", s="", c="red")])
S("내가 열심히 일하고 발명한 것을 빼앗기지 않는다는 믿음. 이게 사람들이 위험을 무릅쓰고 새로운 일에 도전하게 만들었습니다.", "quote", lines=["내 것을 [빼앗기지 않는다]는 믿음이", "도전을 만든다"], size=110)
S("이제 한국입니다. 1960년대 초 우리나라는 세계에서 가장 가난한 나라 중 하나였습니다. 1964년 수출이 처음 1억 달러를 넘었을 때, 그날을 수출의 날로 기념할 정도였죠.", "kpi", kicker="1964년", big="수출 1억 달러", color="blue", unit="이날을 기념해 수출의 날이 생겼다", size=220)
S("그로부터 반세기 남짓 지나, 우리나라 수출은 한 해 6천억 달러를 넘는 나라가 됐습니다. 6천 배가 넘게 늘어난 거예요.", "chart", headline="수출, [6천 배] 넘게", badge=EX,
  lines=[dict(name="한국 수출액", color="red", pts=[.05, .08, .15, .3, .48, .65, .82], end="연 6천억 달러 이상")], marks=[dict(x=.0, text="1964 1억 달러", color="blue")])
S("2017년에는 1인당 국민소득이 3만 달러를 넘었고, 2021년에는 유엔무역개발회의가 우리나라를 선진국 그룹으로 분류했습니다. 개발도상국에서 선진국으로 지위가 바뀐 첫 사례였죠.", "timeline", headline="선진국이 된 [한국]",
  events=[dict(when="1964", t="수출 1억 달러", s="", c="blue"), dict(when="2017", t="1인당 국민소득 3만 달러", s="", c="gold"), dict(when="2021", t="UNCTAD 선진국 그룹", s="", c="red")])
S("한국의 성공에도 운이 따랐습니다. 냉전 시대 미국의 지원, 세계 무역이 빠르게 커지던 시기, 그리고 일본에서 넘어오던 산업들.", "check", headline="한국에 따른 [운]",
  items=[dict(t="냉전 속 [미국의 지원과 시장]", c="gold", no="1"), dict(t="빠르게 커지던 [세계 무역]", c="blue", no="2"), dict(t="일본에서 넘어오던 [산업]", c="red", no="3")])
S("하지만 같은 시기, 같은 기회를 받은 나라들이 모두 성공한 건 아닙니다. 행운만으로는 설명이 안 된다는 거죠.", "quote", lines=["같은 기회를 받은 나라가", "[모두 성공하진 않았다]"], size=120)
S("이번엔 반대 사례, 아르헨티나입니다. 20세기 초 아르헨티나는 세계에서 가장 부유한 나라 중 하나였습니다. 넓은 땅에서 나는 곡물과 소고기를 유럽에 팔았죠.", "kpi", kicker="20세기 초 아르헨티나", big="세계 최고 부국 중 하나", color="gold", unit="곡물·소고기 수출로 번영", size=170)
S("그런데 그 뒤로 백 년 동안 아르헨티나는 계속 미끄러졌습니다. 쿠데타와 정권 교체가 반복되고, 정부가 돈을 마구 찍어 물가가 치솟고, 나라 빚을 여러 번 갚지 못했죠.", "chart", headline="부자였다가 [미끄러진] 나라", badge=EX,
  lines=[dict(name="아르헨티나 상대 소득", color="blue", pts=[.8, .75, .65, .55, .48, .4, .35], end="")], marks=[dict(x=.0, text="1900년대 초", color="gold")])
S("규칙이 자꾸 바뀌는 나라에서는 누구도 길게 투자하지 않습니다. 오늘 번 돈이 내일 휴지가 될 수 있으니까요. 첫 번째 이야기의 믿음 이야기가 여기서도 나옵니다.", "quote", lines=["규칙이 자꾸 바뀌는 나라에선", "[아무도 길게 투자하지 않는다]"], size=110)
S("세 나라를 나란히 놓고 보면 공통된 답이 하나 보입니다. 행운만큼, 아니 행운보다 더 중요한 것. 바로 제도입니다.", "kpi", kicker="잘사는 나라의 핵심 조건", big="제도", color="red", unit="게임의 규칙을 정하는 장치", size=260)
S("2024년 노벨 경제학상은 바로 이 연구에 돌아갔습니다. 대런 애쓰모글루, 사이먼 존슨, 제임스 로빈슨. 나라의 부를 가르는 건 제도라는 연구였죠.", "kpi", kicker="2024년 노벨 경제학상", big="애쓰모글루 · 존슨 · 로빈슨", color="gold", unit="제도가 나라의 부를 가른다", size=130)
S("그들은 제도를 두 종류로 나눴습니다. 많은 사람이 참여하고 기회를 얻는 포용적 제도, 그리고 소수가 부를 빼앗아 가는 착취적 제도.", "compare", headline="[포용적 제도] vs [착취적 제도]",
  left=dict(title="포용적 제도", c="red", rows=["재산권 보호·공정한 규칙", "누구나 도전할 수 있음"]), right=dict(title="착취적 제도", c="blue", rows=["소수가 부를 독점", "도전해도 빼앗김"]))
S("가장 극적인 예가 한반도입니다. 같은 민족, 같은 역사, 같은 문화를 가진 남과 북이 다른 제도를 택하고 70여 년이 흐른 뒤, 밤 위성 사진에서 한쪽은 환하게 빛나고 한쪽은 캄캄합니다.", "dual", headline="같은 민족, [다른 제도]", badge=EX,
  panels=[dict(title="남쪽", color="gold", pts=[.3, .85], tag="환한 밤", note="시장·재산권·개방"), dict(title="북쪽", color="blue", pts=[.3, .15], tag="캄캄한 밤", note="통제·폐쇄")])
S("땅도, 사람도, 문화도 같았는데 결과가 이렇게 달라졌다면, 차이를 만든 건 결국 제도라는 거죠.", "quote", lines=["땅도 사람도 같았다면", "차이를 만든 건 [제도]"], size=120)
S("그런데 여기서 끝이 아닙니다. 가난한 나라가 중간쯤까지 올라오는 건 비교적 쉽지만, 거기서 선진국으로 넘어가는 건 아주 어렵습니다. 이걸 중진국 함정이라고 해요.", "kpi", kicker="많은 나라가 빠지는 함정", big="중진국 함정", color="blue", unit="중간까지는 왔는데, 더는 못 올라간다", size=220)
S("싼 인건비로 공장을 돌려 따라잡는 단계까지는 많은 나라가 성공합니다. 하지만 임금이 오르면 그 방법이 더는 안 통하죠. 그때부터는 새로운 것을 만들어 내야 합니다.", "flow", headline="중진국 함정의 [구조]",
  nodes=[dict(t="싼 인건비로 성장", s="따라잡기", c="gold", icon="1"), dict(t="임금 상승", s="같은 방법이 안 통함", c="blue", icon="2"), dict(t="혁신이 필요", s="못 하면 정체", c="red", icon="3")])
S("중진국을 선진국으로 만드는 힘은 결국 혁신, 그리고 혁신을 가능하게 하는 신뢰입니다. 사람을 믿고, 규칙을 믿고, 내 노력이 보상받는다고 믿는 사회.", "quote", lines=["중진국을 선진국으로 만드는 힘", "[혁신]과 그것을 낳는 [신뢰]"], size=110)
S("경제학에서는 이걸 사회적 자본이라고도 부릅니다. 모르는 사람과도 계약하고 거래할 수 있다는 믿음. 이게 있는 사회는 거래 비용이 낮아서 훨씬 많은 일이 일어나죠.", "kpi", kicker="보이지 않는 자본", big="사회적 자본", color="gold", unit="모르는 사람과도 거래할 수 있다는 믿음", size=220)
S("우리나라가 중진국 함정을 넘을 수 있었던 것도, 높은 교육 수준과 기술 투자, 그리고 민주화로 규칙이 더 공정해진 덕분이라는 분석이 많습니다.", "check", headline="한국이 함정을 [넘은] 힘",
  items=[dict(t="높은 [교육] 수준", c="gold", no="1"), dict(t="꾸준한 [기술 투자] — 반도체·조선·자동차", c="red", no="2"), dict(t="[민주화]와 더 공정해진 규칙", c="blue", no="3")])
S("경제학자들이 나라의 성장을 설명할 때 쓰는 아주 단순한 식이 있습니다. 일하는 사람의 수 곱하기, 한 사람이 만들어 내는 양. 바로 생산성이죠.", "flow", headline="성장의 [단순한 식]",
  nodes=[dict(t="일하는 사람 수", s="인구·고용", c="gold", icon="1"), dict(t="× 생산성", s="한 사람이 만드는 양", c="blue", icon="×"), dict(t="= 나라의 생산", s="", c="red", icon="=")])
S("폴 크루그먼은 이렇게 말했습니다. 생산성이 전부는 아니지만, 길게 보면 거의 전부다. 한 사람이 더 많이, 더 좋은 걸 만들 수 있어야 월급도 오를 수 있으니까요.", "quote", lines=["생산성이 전부는 아니지만", "[길게 보면 거의 전부]", "폴 크루그먼"], size=110)
S("그런데 우리나라는 이 식의 앞부분, 일하는 사람의 수가 줄어드는 시대에 들어섰습니다. 출산율이 세계에서 가장 낮은 수준이니까요.", "chart", headline="일하는 사람이 [줄어드는] 시대", badge=EX,
  lines=[dict(name="생산 가능 인구", color="blue", pts=[.5, .58, .64, .66, .62, .55, .46], end="감소")])
S("일하는 사람이 줄면, 같은 성장을 하려면 생산성이 훨씬 빨리 올라야 합니다. 그래서 우리나라의 잠재성장률이 계속 낮아지고 있다는 분석이 나오는 거죠.", "scale", headline="사람이 줄면 [생산성]이 더 올라야",
  left=dict(t="일하는 사람", s="줄어듦", c="blue"), right=dict(t="생산성", s="더 빨리 올라야", c="red"), tilt=-10)
S("인공지능과 자동화가 그래서 중요합니다. 사람이 줄어드는 만큼 기계와 소프트웨어가 생산성을 끌어올려야 하니까요. 우리 반도체 산업이 이 흐름의 한가운데 있는 것도 우연이 아니죠.", "story", scene="datacenter")
S("결국 한국의 다음 과제는 분명합니다. 사람이 줄어드는 시대에, 한 사람 한 사람의 생산성과 사회의 신뢰를 얼마나 끌어올리느냐.", "quote", lines=["사람이 줄어드는 시대의 과제", "[생산성과 신뢰]"], size=120)
S("작은 나라도 잘살 수 있을까요? 싱가포르와 스위스를 보면 답이 나옵니다. 땅도 좁고 자원도 거의 없지만, 세계에서 가장 잘사는 나라에 꼽히죠.", "compare", headline="작지만 [부유한] 나라",
  left=dict(title="싱가포르", c="red", rows=["좁은 땅·자원 없음", "물류·금융 허브"]), right=dict(title="스위스", c="gold", rows=["산악 국가·자원 없음", "정밀 산업·금융"]))
S("두 나라의 공통점은 깨끗한 정부, 예측 가능한 규칙, 그리고 세계에서 손꼽히는 교육과 기술입니다. 결국 다시 제도와 신뢰로 돌아오죠.", "check", headline="작은 부국의 [공통점]",
  items=[dict(t="[깨끗한 정부]와 낮은 부패", c="gold"), dict(t="[예측 가능한] 규칙", c="blue"), dict(t="[교육·기술]에 대한 꾸준한 투자", c="red")])
S("개인에게 가장 확실한 투자 가운데 하나가 교육이라는 연구도 많습니다. 경제학자들은 교육을 한 해 더 받을 때마다 평생 소득이 몇 퍼센트씩 오른다는 분석을 여러 나라에서 반복해서 내놓았어요.", "chart", headline="교육과 [평생 소득]", badge=EX,
  lines=[dict(name="평생 소득", color="red", pts=[.2, .28, .37, .47, .58, .68], end="")])
S("여기서 말하는 교육은 학위만이 아닙니다. 어른이 된 뒤에 새로 배우는 기술, 경제 공부, 그리고 지금처럼 이런 영상을 들으며 생각을 넓히는 것도 다 포함이죠.", "story", scene="lightbulb", relabel={">외국인 순매도<": ">평생 배우기<", ">PER · 시가총액<": ">실력 = 자산<"})
S("그럼 이 이야기가 우리 같은 개인의 재테크와 무슨 상관일까요? 생각보다 아주 직접적입니다.", "qa", q="나라 이야기가\n[내 재테크]와 무슨 상관?")
S("첫째, 내 자산의 가치는 결국 내가 투자한 나라의 성장을 따라갑니다. 그래서 나라를 고르는 것도 투자의 일부예요. 해외 투자를 함께 생각하는 이유죠.", "flow", headline="재테크 연결 ① · [나라]도 고른다",
  nodes=[dict(t="나라의 성장", s="", c="gold", icon="1"), dict(t="기업 이익·임금", s="", c="blue", icon="2"), dict(t="내 자산 가치", s="", c="red", icon="3")])
S("둘째, 제도가 흔들리는 나라의 자산은 아무리 싸 보여도 조심해야 합니다. 규칙이 바뀌면 하루아침에 가치가 사라질 수 있으니까요.", "kpi", kicker="재테크 연결 ②", big="제도 리스크", color="blue", unit="규칙이 흔들리면 싸 보여도 위험하다", size=220)
S("셋째, 그리고 가장 중요한 연결입니다. 나라에 통하는 원리가 사람에게도 똑같이 통한다는 거예요.", "quote", lines=["나라에 통하는 원리는", "[사람]에게도 통한다"], size=130)
S("싼 노동으로 버티는 데는 한계가 있고, 결국 남들이 못 하는 걸 할 수 있는 실력, 그리고 사람들이 나를 믿게 만드는 신뢰가 소득의 천장을 높입니다.", "compare", headline="사람에게도 [중진국 함정]이 있다",
  left=dict(title="함정에 갇힌 커리어", c="blue", rows=["누구나 할 수 있는 일", "시간만 팔기"]), right=dict(title="함정을 넘는 커리어", c="red", rows=["대체하기 어려운 실력", "쌓이는 신뢰"]))
S("첫 번째 이야기에서 가장 큰 자산은 내 실력이라고 말씀드렸죠. 나라의 혁신처럼, 개인의 실력에 투자하는 것도 가장 수익률 높은 투자일 수 있습니다.", "story", scene="report_read", relabel={">펀드 보고서<": ">나의 실력<"})
S("한국이 중진국 함정을 넘는 데 결정적이었던 산업 하나를 꼽으라면, 많은 분이 반도체를 떠올리실 겁니다.", "kpi", kicker="한국을 바꾼 산업", big="반도체", color="red", unit="1980년대의 무모해 보였던 도전", size=250)
S("1983년, 삼성은 반도체 사업에 본격적으로 뛰어들겠다고 선언합니다. 당시에는 일본과 미국 기업들이 꽉 잡고 있던 시장이라, 무모한 도전이라는 평가가 많았어요.", "timeline", headline="한국 반도체의 [시작]",
  events=[dict(when="1983", t="반도체 본격 진출 선언", s="", c="gold"), dict(when="1980년대 중반", t="D램 개발·적자의 시간", s="", c="blue"), dict(when="1990년대", t="메모리 세계 1위", s="", c="red")])
S("처음 몇 년은 적자의 연속이었습니다. 반도체 값이 폭락하던 시기에는 회사가 휘청일 정도였죠. 그래도 투자를 멈추지 않았고, 결국 1990년대에 메모리 반도체 세계 1위에 오릅니다.", "chart", headline="적자의 시간을 [버틴] 투자", badge=EX,
  lines=[dict(name="반도체 사업 이익", color="red", pts=[.4, .3, .22, .35, .5, .7, .85], end="")])
S("이 이야기에는 오늘의 모든 원리가 들어 있습니다. 위험을 감당할 수 있는 만큼 나눠 지고, 적자의 시간을 버티는 기다림, 그리고 기술이라는 혁신.", "check", headline="반도체 이야기에 담긴 [원리]",
  items=[dict(t="[리스크]를 감당하며 도전", c="gold", no="1"), dict(t="적자의 시간을 [버티는 기다림]", c="blue", no="2"), dict(t="[혁신]으로 함정을 넘음", c="red", no="3")])
S("지금 우리나라 수출에서 반도체가 차지하는 비중은 아주 큽니다. 40여 년 전 무모해 보였던 선택 하나가, 한 나라의 소득을 바꿔 놓은 셈이죠.", "story", scene="fab_korea")
S("일곱 번째 이야기를 정리하겠습니다. 어느 나라에서 태어나느냐가 평생 소득의 절반 이상을 좌우하고, 나라의 부를 가르는 건 행운만큼 제도입니다.", "check", headline="일곱 번째 이야기 정리 ①",
  items=[dict(t="태어난 나라가 [평생 소득의 절반 이상]", c="gold"), dict(t="영국: [석탄·임금·제도]가 겹친 행운", c="blue"), dict(t="잘사는 나라의 핵심은 [포용적 제도]", c="red")])
S("중진국을 선진국으로 만드는 건 혁신과 신뢰이고, 이 원리는 개인에게도 똑같이 통합니다. 내 실력과 신뢰가 내 소득의 천장입니다.", "check", headline="일곱 번째 이야기 정리 ②",
  items=[dict(t="중진국 함정을 넘는 힘: [혁신·신뢰]", c="red"), dict(t="제도가 흔들리면 [자산도 흔들린다]", c="blue"), dict(t="개인에게도: [실력과 신뢰]가 천장", c="gold")])
S("나라 이야기에도 질문이 많았습니다. 세 가지만 보고 갈게요.", "quote", lines=["선진국에 대해", "[자주 받는 질문 세 가지]"], size=130)
S("첫 번째 질문. 그럼 한국 주식보다 미국 주식이 무조건 낫나요? 길게 보면 미국 시장이 더 많이 오른 건 맞습니다. 하지만 앞으로도 그럴지는 아무도 장담할 수 없어요.", "qa", q="미국 주식이\n[무조건] 나을까?")
S("그래서 한 나라에 모두 거는 것보다, 여러 나라에 나눠 담는 게 원칙입니다. 나라도 두 번째 이야기의 분산 대상이에요.", "kpi", kicker="첫 번째 질문의 답", big="나라도 분산", color="gold", unit="한 나라에 모두 걸지 않는다", size=230)
S("두 번째 질문. 인구가 줄면 한국 경제는 끝인가요? 쉽지 않은 숙제인 건 분명합니다. 하지만 인구보다 생산성이 더 중요하다는 걸 이번 이야기에서 봤죠.", "qa", q="인구가 줄면\n[끝]일까?")
S("일하는 사람이 줄어도 한 사람이 만드는 가치가 커지면 소득은 늘 수 있습니다. 결국 교육과 기술, 그리고 제도와 신뢰에 달린 문제예요.", "scale", headline="인구 감소 vs [생산성]",
  left=dict(t="일하는 사람", s="줄어듦", c="blue"), right=dict(t="한 사람의 가치", s="키울 수 있음", c="red"), tilt=-6)
S("세 번째 질문. 개인이 나라를 위해 할 수 있는 게 있나요? 생각보다 많습니다. 규칙을 지키고, 신뢰를 쌓고, 내 실력을 키우는 것. 그 하나하나가 나라의 사회적 자본이 됩니다.", "check", headline="개인이 쌓는 [사회적 자본]",
  items=[dict(t="[규칙]을 지키기", c="gold"), dict(t="[신뢰]를 쌓기 — 약속 지키기", c="blue"), dict(t="[실력]을 키우기", c="red")])
S("결국 나라도 사람도, 수많은 선택이 쌓여 지금의 모습이 됐습니다. 그럼 좋은 선택은 어떻게 할 수 있을까요? 마지막 이야기, 선택입니다.", "quote", lines=["나라도 사람도", "[선택이 쌓인] 결과"], size=130)


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
