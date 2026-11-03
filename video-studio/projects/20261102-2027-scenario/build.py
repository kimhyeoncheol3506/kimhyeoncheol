"""30편 2027년, 경제는 좋아지는데 당신은 더 가난해집니다 — 현철님 제공 대본 (HyperFrames 모션그래픽 중심)

사용:
  python3 projects/20261102-2027-scenario/build.py plan     # project.json(장면·대사) 생성 → 음성 생성에 사용
  python3 projects/20261102-2027-scenario/build.py render   # 음성 길이에 맞춰 HyperFrames 장면 렌더 → project.json 갱신
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
PJ = "projects/20261102-2027-scenario"

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
Q("좋은 소식부터 드리겠습니다.", "[좋은 소식]부터", "드리겠습니다", size=140)
S("한국은행이 내년 성장률을 올려 잡았습니다.", "chart", headline="한국은행, 내년 성장률 [상향]", badge="개념도 · 실제 수치 아님",
  lines=[dict(name="성장률 전망", color="red", pts=[.3, .32, .35, .4, .55, .7], end="↑ 상향")])
S("증권사들은 코스피 1만을 이야기합니다.", "kpi", kicker="증권사 일부 전망 상단", big="코스피 1만", color="red", size=210)
S("나쁜 소식은, 그 숫자 안에 당신은 없다는 겁니다.", "story", scene="party_outside")
S("오늘은 집, 대출, 그리고 국내 주식. 이 세 가지 숫자로, 경제는 좋아지는데 월급쟁이만 터지는 내년 시나리오를 보여드리겠습니다.", "check", headline="월급쟁이만 터지는 [내년 시나리오]",
  items=[dict(t="[집] — 사고 싶어도 집이 없다", c="gold", no="1"), dict(t="[대출] — 이제 청구서가 온다", c="blue", no="2"), dict(t="[국장] — 코스피 1만? 두 종목 1만", c="red", no="3")])

# ═════════════ 1. 집 ═════════════
CH("01", "집: 사고 싶어도 [집이 없습니다]", "01 · 집 — 사고 싶어도 집이 없다", name="집 — 사고 싶어도 집이 없습니다")
Q("정부가 공급을 늘린다고 했죠. 맞습니다.", "정부가 공급을 늘린다고 했죠", "[맞습니다]", size=110)
S("2032년에요.", "kpi", kicker="새 택지 입주 예상 시점", big="2032년", color="blue", unit="이후가 될 가능성 (보도)", size=240)
S("부동산R114 기준으로, 2027년 서울 아파트 입주 예정 물량은 임대를 빼고 1만 3019가구입니다.", "kpi", kicker="2027년 서울 아파트 입주 예정 (부동산R114, 임대 제외)", big="1만 3019가구", color="blue", size=170)
S("1990년 통계 작성 이후 가장 적은 숫자입니다.", "chart", headline="1990년 통계 작성 이후 [최저]", badge="개념도 · 실제 수치 아님",
  lines=[dict(name="서울 입주 물량", color="blue", pts=[.7, .55, .8, .6, .65, .5, .42, .18], end="역대 최저")])
S2("집계 기관마다 숫자는 조금 다른데요, 한국부동산원과 R114 공동 자료로 봐도 1만 7197호, 서울의 적정 수요 약 4만 5천 호의 38% 수준이라는 분석이 나옵니다.",
   ("집계 기관마다 숫자는 조금 다른데요, 한국부동산원과 R114 공동 자료로 봐도 1만 7197호,", "kpi", dict(kicker="한국부동산원·R114 공동 자료", big="1만 7197호", color="blue", unit="2027년 서울 입주", size=200)),
   ("서울의 적정 수요 약 4만 5천 호의 38% 수준이라는 분석이 나옵니다.", "compare", dict(headline="적정 수요의 [38%] 수준 (보도)",
        left=dict(title="서울 적정 수요", c="mute", rows=["약 4만 5천 호"]), right=dict(title="2027년 입주 (공동 자료)", c="blue", rows=["1만 7197호", "→ 약 38%"]))))
S2("그런데 분양가는 반대로 움직였습니다. 서울 민간아파트 평균 분양가가 3.3제곱미터당 약 6343만 원으로, 처음으로 6천만 원대를 넘었습니다.",
   ("그런데 분양가는 반대로 움직였습니다.", "quote", dict(lines=["그런데 분양가는", "[반대로] 움직였습니다"], size=120)),
   ("서울 민간아파트 평균 분양가가 3.3제곱미터당 약 6343만 원으로, 처음으로 6천만 원대를 넘었습니다.", "kpi", dict(kicker="서울 민간아파트 평균 분양가 (3.3㎡당, HUG)", big="약 6343만 원", color="red", unit="처음으로 6천만 원대", size=160)))
S("정부 대책의 효과는 언제 나올까요? 신규 택지는 착공이 빨라야 2029년 하반기, 입주는 2032년 이후가 될 가능성이 큽니다.", "timeline", headline="대책 효과는 [2032년] 이후",
  events=[dict(when="2027", t="입주 역대 최저", s="", c="blue"), dict(when="2029 하반기", t="빨라야 착공", s="", c="gold"), dict(when="2032~", t="입주 시작", s="가능성", c="red")])
S("입주까지 3년에서 4년이 걸리기 때문에, 어떤 대책을 내도 앞으로 2~3년의 공급 공백은 사실상 확정이라는 지적이 나옵니다.", "story", scene="empty_lot")
S("한번 계산해 보겠습니다. 국민평형 84제곱미터, 약 25평에 이 분양가를 곱하면 약 16억 원입니다.", "flow", headline="계산: 전용 25평 기준 [약 16억]",
  nodes=[dict(t="3.3㎡당 약 6343만 원", s="평균 분양가", c="red", icon="₩"), dict(t="× 약 25평", s="전용 84㎡ 기준", c="gold", icon="×"), dict(t="≈ 약 16억 원", s="공급면적 기준이면 더 비쌈", c="blue", icon="=")], badge="계산값 · 최소 기준")
S("연봉 5천만 원인 사람이 한 푼도 안 쓰고 모아도 32년이 걸립니다.", "story", scene="saving_32")

# ═════════════ 2. 대출 ═════════════
CH("02", "대출: 금리는 올랐고, 이제 [청구서]가 옵니다", "02 · 대출 — 이제 청구서가 온다", name="대출 — 금리는 올랐고, 이제 청구서가 옵니다")
Q("작년엔 ‘영끌’이라고 불렀죠. 내년엔 ‘연체’라고 부릅니다.", "작년엔 [영끌]", "내년엔 {연체}", size=140)
S("한국은행은 올해 기준금리를 다시 올리면서, 보도에 따르면 ‘기준금리 3% 시대’를 다시 열었습니다.", "kpi", kicker="한국은행 기준금리 (보도)", big="3% 시대", color="red", unit="올해 다시 인상", size=210)
S2("10월에는 동결했지만, 시장에서는 인상 재개 전망이 우세하고, 전문가 절반은 최종 금리가 3.75%까지 갈 가능성을 열어 둬야 한다고 봤습니다.",
   ("10월에는 동결했지만, 시장에서는 인상 재개 전망이 우세하고,", "signal", dict(headline="10월은 동결, 그러나", lamps=[dict(c="gold", t="10월 동결", s=""), dict(c="red", t="인상 재개 전망 우세", s="(보도)")])),
   ("전문가 절반은 최종 금리가 3.75%까지 갈 가능성을 열어 둬야 한다고 봤습니다.", "chart", dict(headline="최종 금리 [3.75%] 가능성 (보도)", badge="개념도 · 실제 수치 아님",
        lines=[dict(name="기준금리 경로", color="red", pts=[.3, .3, .45, .55, .55, .65, .75], end="3.75%?")], marks=[dict(x=.66, text="10월 동결", color="gold")])))
S("그 결과가 이미 숫자로 나왔습니다. 9월 신규 주택담보대출 금리가 연 4.88%로, 14년 5개월 만에 가장 높습니다.", "kpi", kicker="9월 신규 주담대 금리 (한국은행)", big="연 4.88%", color="red", unit="14년 5개월 만에 최고", size=210)
S("금리가 0.25%포인트만 올라도, 가계의 이자 부담은 약 3조 3천억 원 늘어납니다.", "flow", headline="0.25%p만 올라도",
  nodes=[dict(t="금리 +0.25%p", s="", c="red", icon="%"), dict(t="가계 이자 부담", s="", c="gold", icon="$"), dict(t="약 +3조 3천억 원", s="(보도)", c="blue", icon="↑")])
S2("연체도 늘고 있습니다. 보도에 따르면 8월 은행 대출 연체율은 0.69%로 9년 10개월 만에 최고였고, 주담대를 뺀 신용대출 등의 연체율은 0.91%였습니다.",
   ("연체도 늘고 있습니다. 보도에 따르면 8월 은행 대출 연체율은 0.69%로 9년 10개월 만에 최고였고,", "kpi", dict(kicker="8월 은행 대출 연체율 (보도)", big="0.69%", color="blue", unit="9년 10개월 만에 최고", size=230)),
   ("주담대를 뺀 신용대출 등의 연체율은 0.91%였습니다.", "compare", dict(headline="연체율, [9년 10개월] 만에 최고 (보도)",
        left=dict(title="은행 대출 전체", c="blue", rows=["0.69%"]), right=dict(title="주담대 뺀 가계대출", c="blue", rows=["0.91%"]))))
S("정부가 내세우는 숫자도 있습니다. GDP 대비 가계부채 비율이 81.1%로 10년 만에 최저라는 겁니다.", "kpi", kicker="GDP 대비 가계부채 비율 (보도)", big="81.1%", color="gold", unit="10년 만에 최저?", size=230)
S("하지만 한국은행 부총재보조차 이것을 GDP 증가에 따른 착시효과라고 했습니다.", "quote", lines=["한국은행 부총재보도", "\"GDP 증가에 따른 [착시효과]\""], size=110)
S("부채 비율이 내려간 건 당신 빚이 줄어서가 아니라, 반도체가 GDP를 키워서입니다.", "scale", headline="비율이 내려간 [진짜 이유]",
  left=dict(t="내 빚 (분자)", s="그대로", c="blue"), right=dict(t="GDP (분모)", s="반도체가 키움", c="red"), tilt=12)
S("분모가 커졌을 뿐, 당신 대출 원금은 그대로입니다.", "story", scene="debt_bill")

# ═════════════ 3. 국장 ═════════════
CH("03", "국장: 코스피 1만? 정확히는 [두 종목 1만]", "03 · 국장 — 두 종목 1만", name="국장 — 코스피 1만? 정확히는 '두 종목 1만'")
Q("증권사 전망을 다 모아 보니 아주 정확했습니다.", "증권사 전망을 다 모아 보니", "아주 [정확]했습니다", size=110)
S("오르거나, 내리거나.", "signal", headline="증권사 전망 총정리",
  lamps=[dict(c="red", t="오르거나", s=""), dict(c="blue", t="내리거나", s="")])
S("주요 증권사의 내년 코스피 예상 범위는 최저 5000에서 최고 1만까지입니다. 위아래가 무려 두 배 차이입니다.", "compare", headline="내년 코스피 전망 범위: [두 배]",
  left=dict(title="최저", c="blue", rows=["약 5000"]), right=dict(title="최고", c="red", rows=["1만"]))
S("코스피는 6월 22일 9114로 역대 최고점을 찍은 뒤 내리막을 탔습니다.", "chart", headline="6월 22일 [9114] 최고점 이후", badge="개념도 · 실제 수치 아님",
  lines=[dict(name="코스피", color="blue", pts=[.4, .6, .8, .95, .78, .6, .5, .38], end="하락세")], marks=[dict(x=.43, text="6월 22일 9114", color="red")])
S("10월 15일에는 하루에만 7.57% 빠지며 5554로 마감했고, 서킷브레이커까지 발동됐습니다.", "kpi", kicker="10월 15일 코스피", big="−7.57%", color="blue", unit="5554 마감 · 서킷브레이커 발동", size=240)
S("올해 외국인 누적 순매도는 연평균 시가총액의 4%로, 2008년 금융위기 때의 4.56%에 근접했습니다.", "compare", headline="외국인 순매도, [금융위기급] (보도)",
  left=dict(title="2008년 금융위기", c="mute", rows=["시총의 4.56%"]), right=dict(title="올해", c="blue", rows=["시총의 약 4%"]))
S2("그리고 가장 중요한 숫자. 삼성전자와 SK하이닉스가 코스피 전체 영업이익에서 차지하는 비중이 올해 65.5%, 내년엔 71.9%까지 커질 전망입니다.",
   ("그리고 가장 중요한 숫자.", "qa", dict(q="가장 [중요한] 숫자")),
   ("삼성전자와 SK하이닉스가 코스피 전체 영업이익에서 차지하는 비중이 올해 65.5%, 내년엔 71.9%까지 커질 전망입니다.", "dual", dict(headline="두 종목이 코스피 이익의 [70%]",
        panels=[dict(title="올해", color="gold", pts=[.2, .65], tag="65.5%", note="삼성전자 + SK하이닉스 비중"), dict(title="내년 (전망)", color="red", pts=[.2, .72], tag="71.9%", note="한국투자증권")])))
S("코스피가 오른다는 말은 사실 ‘삼성과 하이닉스가 오른다’는 말입니다.", "story", scene="two_giants")
Q("당신이 가진 2차전지, 바이오, 테마주 이야기는 그 보고서 어디에도 없습니다.", "당신의 2차전지·바이오·테마주는", "그 보고서 [어디에도] {없습니다}", size=100)

# ═════════════ 엔딩 ═════════════
CH("04", "그래서 [어떡하냐고요?]", "04 · 엔딩 — 올해 안에 정리할 것", name="엔딩 — 그래서 어떡하냐고요?")
S("그래서 어떡하냐고요?", "qa", q="그래서\n[어떡하냐고요?]")
S("경제가 좋아지는 해에 가난해지는 사람들에게는 공통점이 있습니다.", "kpi", kicker="경제가 좋아지는 해에 가난해지는 사람들", big="3가지 공통점", color="gold", size=200)
S("변동금리 대출, 두 종목 빼고 다 들고 있는 계좌, 그리고 ‘내년엔 나아지겠지’라는 기대.", "check", headline="가난해지는 사람들의 [공통점]",
  items=[dict(t="[변동금리] 대출", c="blue"), dict(t="[두 종목 빼고] 다 들고 있는 계좌", c="gold"), dict(t="'[내년엔 나아지겠지]'라는 기대", c="red")])
S("셋 중 하나라도 해당되면 올해가 가기 전에 정리하세요.", "story", scene="check_account")
Q("경제는 당신을 기다려 주지 않지만, 숫자는 거짓말하지 않으니까요.", "경제는 당신을 기다려 주지 않지만", "[숫자는 거짓말하지 않으니까요]", size=100)
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
