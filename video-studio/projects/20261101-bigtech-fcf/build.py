"""28편 구글 시총 660조 증발의 진실 (잉여현금흐름·자본비용) — 현철님 제공 대본 (HyperFrames 모션그래픽 중심)

사용:
  python3 projects/20261101-bigtech-fcf/build.py plan     # project.json(장면·대사) 생성 → 음성 생성에 사용
  python3 projects/20261101-bigtech-fcf/build.py render   # 음성 길이에 맞춰 HyperFrames 장면 렌더 → project.json 갱신
"""
import json
import os
import re
import subprocess
import sys

os.environ.setdefault("HF_LOOK", "sting")  # OPUSCAR 98 No.46 The Sting 룩
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
PJ = "projects/20261101-bigtech-fcf"

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


# ═════════════ 오프닝 ═════════════
_chip = "오프닝"
S("구글 시총 하루 만에 660조 원이 증발했습니다.", "story", scene="news_tv")
S("우리나라 코스피 시가총액 3위부터 10위까지의 기업들이 통째로 사라진 수준입니다.", "kpi", kicker="하루 만에 사라진 구글 시가총액", big="660조 원", color="red", unit="코스피 시총 3위~10위가 통째로 사라진 규모", size=230)
S("아마존도, 인텔도 무너졌습니다.", "dual", headline="아마존도, 인텔도 [무너졌다]", badge="개념도 · 실제 수치 아님",
  panels=[dict(title="아마존", color="blue", pts=[.8, .78, .76, .7, .5, .38, .32], tag="급락", note=""), dict(title="인텔", color="blue", pts=[.85, .84, .83, .8, .4, .22, .18], tag="−28%", note="1970년대 이후 최대 하루 낙폭(보도)")])
S("뉴스 댓글창은 또다시 \"AI는 거품이었다\", \"닷컴버블 시즌 2가 왔다\"며 호들갑입니다.", "story", scene="subway_comments")
Q("하지만 착각하지 마십시오.", "하지만", "[착각]하지 마십시오", size=150)
S("이 영상을 끝까지 보시고 나면, 여러분은 대중이 공포에 떨며 도망칠 때 누구를 매수하고 누구를 걸러야 할지 정확히 판단하는 '상위 1%의 자본가적 시선'을 갖추게 될 겁니다.", "story", scene="check_account")
Q("오늘 이 사태의 본질을 정확히 꿰뚫지 못하면, 여러분의 계좌는 시장의 공포에 쓸려 영원히 바닥을 기게 될 것입니다.", "본질을 꿰뚫지 못하면", "계좌는 공포에 쓸려", "{영원히 바닥}을 깁니다", size=100)
Q("경제학의 기본 원리로 이 거대한 착시를 발라버리겠습니다.", "경제학의 기본 원리로", "이 거대한 [착시]를 발라버리겠습니다", size=100)

# ═════════════ 섹션 1 ═════════════
CH("01", "실적이 좋은데 왜 망하냐고? — [잉여현금흐름]의 경제학", "01 · 잉여현금흐름(FCF)의 경제학", name="실적이 좋은데 왜 망하냐고? — 잉여현금흐름(FCF)의 경제학")
Q("이번 실적 발표의 핵심은 간단합니다.", "이번 실적 발표의", "핵심은 [간단]합니다", size=120)
S("\"얼마나 벌었냐\"가 아니라, \"앞으로 쓸 돈을 감당할 수 있냐\"였습니다.", "compare", headline="시장이 본 것은 [다른 질문]",
  left=dict(title="얼마나 벌었냐", c="blue", rows=["매출·이익 (X)"]), right=dict(title="쓸 돈을 감당하냐", c="red", rows=["현금으로 버틸 수 있나 (O)"]))
S("아마존과 구글 모두 AI 매출은 폭발적으로 늘었습니다.", "chart", headline="AI 매출은 [폭발적으로] 늘었다", badge="개념도 · 실제 수치 아님",
  lines=[dict(name="AI·클라우드 매출", color="red", pts=[.1, .16, .26, .4, .56, .74, .92], end="폭증")])
S("그런데 왜 주가가 박살이 났을까요?", "qa", q="그런데 왜 주가가\n[박살]이 났을까요?")
S("바로 잉여현금흐름, FCF가 완전히 무너졌기 때문입니다.", "flow", headline="[잉여현금흐름(FCF)] = 진짜 내 손에 쥐는 현금",
  nodes=[dict(t="영업현금흐름", s="장사로 번 현금", c="red", icon="$"), dict(t="설비투자(CAPEX)", s="현금 유출", c="blue", icon="−"), dict(t="잉여현금흐름", s="마이너스면 빚·증자", c="gold", icon="=")])
S("아마존은 7월에 올해 설비투자 계획을 2,200억 달러로 올렸습니다.", "story", scene="datacenter")
S2("클라우드 매출 증가율이 39%로 날아올랐지만, 최근 1년 잉여현금흐름이 무려 마이너스 424억 달러, 우리 돈 약 58조 원으로 떨어졌습니다.",
   ("클라우드 매출 증가율이 39%로 날아올랐지만,", "kpi", dict(kicker="아마존 클라우드(AWS) 매출 증가율", big="+39%", color="red", size=230)),
   ("최근 1년 잉여현금흐름이 무려 마이너스 424억 달러, 우리 돈 약 58조 원으로 떨어졌습니다.", "kpi", dict(kicker="아마존 최근 1년 잉여현금흐름", big="−424억 달러", color="blue", unit="우리 돈 약 58조 원", size=170)))
S("들어온 돈보다 나간 돈이 훨씬 많다는 뜻입니다.", "scale", headline="들어온 돈 < [나간 돈]",
  left=dict(t="들어온 돈", s="영업현금흐름", c="red"), right=dict(t="나간 돈", s="설비투자", c="blue"), tilt=14)
S("구글은 설비투자가 예상보다 적었음에도 더 크게 빠졌습니다.", "qa", q="설비투자는 예상보다 적었는데\n구글은 왜 [더 크게] 빠졌을까?", size=78)
S("유럽 벌금을 내고, 자체 AI 칩인 TPU를 미리 쌓아두느라 3달 동안 들어온 현금보다 설비에 91억 달러를 더 썼습니다.", "flow", headline="구글: 3달 동안 [91억 달러] 더 썼다",
  nodes=[dict(t="유럽 벌금", s="", c="blue", icon="!"), dict(t="자체 AI 칩 TPU 비축", s="", c="gold", icon="▣"), dict(t="잉여현금흐름 −91억 달러", s="3분기", c="blue", icon="↓")])
S("시장 예상치보다 적자 폭이 4배나 컸습니다.", "kpi", kicker="시장 예상치 대비 적자 폭", big="4배", color="blue", size=260)
Q("시장은 묻고 있습니다.", "시장은", "[묻고] 있습니다", size=150)
S("\"너네가 지금 벌어들이는 본업의 현금으로 이 미친 듯이 쏟아붓는 설비투자를 감당할 수 있어?\"", "scale", headline="시장의 질문: [감당할 수 있어?]",
  left=dict(t="본업의 현금", s="", c="red"), right=dict(t="쏟아붓는 설비투자", s="", c="blue"), tilt=12, **{"from": -10}, ease="sine.inOut")

# ═════════════ 섹션 2 ═════════════
CH("02", "금리의 칼날과 [기회비용] — 왜 지금 공포인가", "02 · 금리의 칼날과 기회비용", name="금리의 칼날과 기회비용 — 왜 지금 시장은 공포에 빠졌나")
S("2022년을 기억하십니까?", "qa", q="[2022년]을 기억하십니까?")
S("그때도 잉여현금흐름이 마이너스인데 금리까지 뛰니까 아마존 주가가 반토막이 났습니다.", "chart", headline="2022년: FCF 마이너스 + 금리 급등 = [반토막]", badge="개념도 · 실제 수치 아님",
  lines=[dict(name="금리", color="red", pts=[.1, .14, .3, .5, .66, .78, .82], end="급등"), dict(name="아마존 주가", color="blue", pts=[.85, .82, .7, .55, .45, .4, .42], end="반토막")])
Q("지금 상황이 정확히 그렇습니다.", "지금 상황이", "[정확히] 그렇습니다", size=130)
S("미국 10년물 국채금리가 5% 위를 맴돌고 있습니다.", "story", scene="bank_rate")
S("돈을 빌려 쓰려면 이자 부담이 눈덩이처럼 불어납니다.", "flow", headline="이자 부담은 [눈덩이]처럼",
  nodes=[dict(t="높은 금리", s="", c="red", icon="%"), dict(t="돈을 빌려 설비투자", s="", c="gold", icon="$"), dict(t="이자 부담 눈덩이", s="", c="blue", icon="↑")])
S("실제로 아마존의 이자비용은 1년 새 3배로 폭증했습니다.", "kpi", kicker="아마존 이자비용, 1년 새", big="3배", color="blue", size=260)
Q("여기에 AI가 스스로 물가를 자극해 올린 비용이 또 있습니다.", "여기에 AI가 스스로 물가를 자극해", "올린 비용이 [또] 있습니다", size=96)
S("바로 메모리값 폭등입니다.", "story", scene="memory_store")
S("AI 서버 부품값의 75% 이상이 메모리입니다.", "kpi", kicker="AI 서버 부품값 중 메모리 비중", big="75%+", color="gold", size=250)
S("구글도, 아마존도 이 메모리값 때문에 설비투자 예산을 더 늘려야 했습니다.", "flow", headline="메모리값 ↑ → [설비투자 예산] ↑",
  nodes=[dict(t="메모리값 폭등", s="", c="red", icon="↑"), dict(t="서버 한 대 값 상승", s="", c="gold", icon="▣"), dict(t="설비투자 예산 증액", s="구글·아마존", c="blue", icon="$")])
Q("인텔은 이 메모리 대란 직격탄을 맞았습니다.", "인텔은", "메모리 대란 [직격탄]을 맞았습니다", size=110)
S("AI 쪽으로 메모리가 다 몰리다 보니 PC용 메모리값이 뛰었고, 인텔의 PC 칩 매출은 20% 넘게 꺾였습니다.", "flow", headline="AI가 메모리를 [빨아들이자]",
  nodes=[dict(t="메모리 → AI 서버로 쏠림", s="", c="gold", icon="→"), dict(t="PC용 메모리값 상승", s="", c="red", icon="↑"), dict(t="인텔 PC 칩 매출 하락", s="", c="blue", icon="↓")])
S("벌 돈이 무너지니 다음 날 주가가 28% 넘게 나자빠진 겁니다.", "kpi", kicker="인텔 다음 날 주가", big="−28%", color="blue", unit="벌 돈(이익)이 무너지자", size=260)
Q("시장 참가자들은 AI가 가짜라서 파는 게 아닙니다.", "시장 참가자들은", "AI가 [가짜라서] 파는 게 {아닙니다}", size=110)
S("'고금리 시대에, 이 천문학적인 빚과 비용을 감당하며 살아남을 자가 누구인가'를 계산하며 공포에 질려 있는 것입니다.", "hub", headline="시장이 계산하는 것: [누가 살아남나]", center="고금리 시대",
  chips=[dict(t="천문학적인 빚", c="blue"), dict(t="불어난 이자", c="blue"), dict(t="메모리 비용", c="gold"), dict(t="살아남을 자는?", c="red")], cfs=56)

# ═════════════ 섹션 3 ═════════════
CH("03", "살아남는 자의 법칙 — [버티는 힘]은 어디서 오나", "03 · 살아남는 자의 법칙", name="살아남는 자의 법칙 — 버티는 힘은 어디서 나오는가")
S("그렇다면 이 폭락장에서도 버텨낸 기업들은 뭐가 달랐을까요?", "qa", q="폭락장에서도 버텨낸 기업은\n[뭐가] 달랐을까?")
S("답은 명확합니다. 시장이 던진 질문에 정확히 답을 내놓았기 때문입니다.", "quote", lines=["답은 명확합니다", "시장의 질문에 [정확히 답]을 내놓았다"], size=104)
S("딱 세 가지 유형 중 하나였습니다.", "kpi", kicker="버텨낸 기업", big="3가지 유형", color="gold", size=200)
S2("첫째, 본업의 현금으로 때우는 자입니다. 마이크로소프트는 3달 동안 580억 달러를 벌어들여 설비에 쏟아붓고도 186억 달러의 잉여현금흐름 플러스를 지켜냈습니다.",
   ("첫째, 본업의 현금으로 때우는 자입니다.", "check", dict(headline="버텨낸 기업의 3가지 유형", items=[dict(t="본업의 현금으로 [때우는 자]", c="red", no="1")])),
   ("마이크로소프트는 3달 동안 580억 달러를 벌어들여 설비에 쏟아붓고도 186억 달러의 잉여현금흐름 플러스를 지켜냈습니다.", "compare", dict(headline="① 예: 마이크로소프트 (3달)",
        left=dict(title="벌어들인 현금", c="red", rows=["580억 달러"]), right=dict(title="설비투자 후 남은 FCF", c="red", rows=["+186억 달러"]))))
S("둘째, 돈이 모자라도 '끝나는 날짜'를 명확히 제시한 자, 오라클입니다.", "check", headline="버텨낸 기업의 3가지 유형",
  items=[dict(t="본업의 현금으로 때우는 자", c="mute", no="1"), dict(t="[끝나는 날짜]를 제시한 자 — 오라클", c="gold", no="2")])
S("지금 현금이 모자라도, 언제 잉여현금흐름이 플러스로 돌아서며 추가 조달은 얼마로 끝나는지 명확한 로드맵을 주니 시장은 환호했습니다.", "timeline", headline="② 로드맵을 준 기업에 시장은 [환호]",
  events=[dict(when="지금", t="현금 부족", s="추가 조달 필요", c="blue"), dict(when="중간", t="추가 조달 끝", s="규모를 미리 공개", c="gold"), dict(when="이후", t="FCF 플러스 전환", s="날짜를 제시", c="red")])
S("셋째, 애초에 크게 안 쓰는 자, 애플입니다.", "check", headline="버텨낸 기업의 3가지 유형",
  items=[dict(t="본업의 현금으로 때우는 자", c="mute", no="1"), dict(t="끝나는 날짜를 제시한 자", c="mute", no="2"), dict(t="애초에 [크게 안 쓰는 자] — 애플", c="teal", no="3")])
S("거대한 설비투자 리스크에서 비껴나 있어 사상 최고가를 기록했습니다.", "kpi", kicker="③ 설비투자 리스크에서 비껴난 애플", big="사상 최고가", color="red", size=170)
S("반면, 구글과 아마존, 메타는 \"내년엔 더 크게 쓰겠다\"고 선언해 놓고 구체적인 숫자는 꽁꽁 숨겼습니다.", "compare", headline="반면 구글·아마존·메타는",
  left=dict(title="말한 것", c="gold", rows=["\"내년엔 더 크게 쓰겠다\""]), right=dict(title="숨긴 것", c="blue", rows=["구체적인 숫자"]))
S("시장은 '끝을 알 수 없는 블랙홀'에 공포를 느꼈고, 모르는 만큼 주가에서 먼저 털어낸 것입니다.", "story", scene="blackhole")
S("한국 증시가 3.48% 폭락하고 외국인이 하이닉스와 삼성전자를 던진 이유도 여기에 있습니다.", "kpi", kicker="같은 날 코스피", big="−3.48%", color="blue", unit="외국인, SK하이닉스·삼성전자 매도", size=230)
S("빅테크가 설비에 쓰는 돈이 곧 우리 메모리 반도체 기업들의 매출이기 때문입니다.", "story", scene="fab_korea")
S("미국의 '쓸 돈 걱정'이 국장의 '벌 돈 걱정'으로 직결된 것입니다.", "flow", headline="미국의 쓸 돈 걱정 = 국장의 [벌 돈 걱정]",
  nodes=[dict(t="미국 빅테크", s="쓸 돈 걱정", c="blue", icon="$"), dict(t="설비투자 축소 우려", s="", c="gold", icon="↓"), dict(t="한국 메모리 기업", s="벌 돈 걱정", c="blue", icon="▣")])

# ═════════════ 결론 ═════════════
CH("04", "우매함에서 벗어나 [행동할 시점]", "04 · 결론 — 행동할 시점", name="결론 — 우매함에서 벗어나 행동할 시점")
Q("결국 핵심은 단순합니다.", "결국 핵심은", "[단순]합니다", size=140)
S("AI 수요는 계약 잔고로 폭발적으로 쌓이고 있습니다.", "chart", headline="AI 수요는 [계약 잔고]로 쌓인다", badge="개념도 · 실제 수치 아님",
  lines=[dict(name="계약 잔고", color="red", pts=[.1, .18, .3, .45, .6, .78, .93], end="폭증")])
S("장기적으로 AI는 진실입니다.", "kpi", kicker="장기적으로", big="AI는 진실", color="red", size=200)
Q("하지만 '시간'이 문제입니다.", "하지만", "[시간]이 문제입니다", size=150)
S("설비는 지금 당장 현금으로 사야 하는데, 고객들이 계약한 돈은 몇 년에 걸쳐 들어옵니다.", "story", scene="hourglass")
S("그 돈이 들어올 때까지 누가, 어떻게 버티느냐의 싸움입니다.", "timeline", headline="[버티기] 싸움",
  events=[dict(when="지금", t="설비 현금 지출", s="", c="blue"), dict(when="1~2년", t="버티는 구간", s="현금이 방패", c="gold"), dict(when="몇 년 뒤", t="계약 대금 유입", s="", c="red")])
S("누가 끝까지 버텨낼지, 그 진짜 첫 번째 성적표는 내년 2월 4분기 실적 발표 때 나옵니다.", "kpi", kicker="첫 번째 성적표", big="내년 2월", color="gold", unit="4분기 실적 발표", size=200)
S("구글은 클라우드 계약 잔고가 설비투자보다 빨리 느는지, 아마존은 설비투자가 계획대로 꺾이는지, 메모리값의 상방이 어디인지 눈여겨보십시오.", "check", headline="2월에 [눈여겨볼] 것",
  items=[dict(t="구글: 클라우드 계약 잔고가 [설비투자보다 빨리] 느는가", c="red"), dict(t="아마존: 설비투자가 [계획대로 꺾이는가]", c="gold"), dict(t="메모리값: [상방]은 어디인가", c="blue")])
S("대중이 \"AI 끝났다\"며 공포에 질려 도망칠 때, 냉정하게 잉여현금흐름의 방패를 쥔 기업을 선별해 내는 자만이 다음 대세 상승장의 승자가 될 것입니다.", "story", scene="shield")
Q("오늘 영상이 여러분의 뇌를 깨우치는 날카로운 무기가 되었길 바랍니다.", "오늘 영상이 여러분의", "[날카로운 무기]가 되었길 바랍니다", size=110)
Q("유익하셨다면 구독과 좋아요, 알림 설정 부탁드립니다.", "유익하셨다면", "[구독] · [좋아요] · [알림 설정]", size=110)
S("감사합니다!", "story", scene="wave")


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
        pause = 0.45 if nxt and nxt.get("chapter") else 0.30
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
