"""27편 수익 난 주식 먼저 팔고 물린 것만 남기는 이유 (처분 효과) — 현철님 제공 대본 (HyperFrames 모션그래픽 중심)

사용:
  python3 projects/20261030-disposition-effect/build.py plan     # project.json(장면·대사) 생성 → 음성 생성에 사용
  python3 projects/20261030-disposition-effect/build.py render   # 음성 길이에 맞춰 HyperFrames 장면 렌더 → project.json 갱신
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
PJ = "projects/20261030-disposition-effect"

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


# ═════════════ 오프닝 (후킹) ═════════════
_chip = "오프닝"
ROWS = [dict(n="A 종목", v="+12%", g=True), dict(n="B 종목", v="−31%", g=False), dict(n="C 종목", v="+8%", g=True), dict(n="D 종목", v="−24%", g=False), dict(n="E 종목", v="+15%", g=True)]
S2("내 계좌에 파란 불(손실)이 뜬 건 속이 쓰려 못 보겠고, 빨간 불(수익)이 뜬 건 쌀쌀맞게 먼저 팔아치우고 계십니까?",
   ("내 계좌에 파란 불(손실)이 뜬 건 속이 쓰려 못 보겠고,", "ledger", dict(headline="파란 불은 [못 보겠고]", rows=ROWS, hold=[1, 3], t_sell=0.95, sigh=True)),
   ("빨간 불(수익)이 뜬 건 쌀쌀맞게 먼저 팔아치우고 계십니까?", "ledger", dict(headline="빨간 불은 {먼저 팔아치우고}?", rows=ROWS, sell=[0, 2, 4], hold=[1, 3], t_sell=0.25)))
Q("축하드립니다.", "[축하]드립니다", ant="박수", size=170)
S2("당신이 부자가 되지 못하는 이유는 머리가 나빠서가 아니라, 시장이 가장 좋아하는 '완벽한 호구의 심리'를 그대로 실천하고 있기 때문입니다.",
   ("당신이 부자가 되지 못하는 이유는 머리가 나빠서가 아니라,", "quote", dict(lines=["부자가 되지 못하는 이유는", "머리가 나빠서가 {아니라}"], size=104)),
   ("시장이 가장 좋아하는 '완벽한 호구의 심리'를 그대로 실천하고 있기 때문입니다.", "kpi", dict(kicker="시장이 가장 좋아하는", big="완벽한 호구의 심리", color="gold", unit="그대로 실천하고 있기 때문", size=120, ant="걱정")))
S("오늘 이 영상 끝까지 안 보시면, 여러분의 계좌는 앞으로도 오를 때는 쥐꼬리만큼 먹고, 내릴 때는 폭탄을 다 맞아 깡통이 되는 마법을 매일 경험하시게 될 겁니다.", "compare",
  headline="끝까지 안 보시면 매일 경험하는 마법", left=dict(title="오를 때", c="red", rows=["쥐꼬리만큼 먹고"]), right=dict(title="내릴 때", c="blue", rows=["폭탄을 다 맞아", "깡통이 된다"]))

# ═════════════ 본론 1 ═════════════
CH("01", "대중의 착각 — [처분 효과]와 손실 회피", "01 · 처분 효과와 손실 회피", name="대중의 착각 — 처분 효과와 손실 회피")
S("행동경제학에서는 이걸 '처분 효과(Disposition Effect)'라고 부릅니다.", "kpi", kicker="행동경제학에서는", big="처분 효과", color="gold", unit="Disposition Effect", size=210)
S("인간은 본능적으로 손실을 확정 짓는 고통을, 이익을 실현하는 기쁨보다 수십 배 더 크게 느낍니다.", "scale", headline="고통 vs 기쁨, 저울이 [기웁니다]",
  left=dict(t="이익을 실현하는 기쁨", s="", c="red"), right=dict(t="손실을 확정 짓는 고통", s="훨씬 더 크게 느낌", c="blue"), tilt=14)
S("그래서 어떻게 합니까?", "qa", q="그래서 [어떻게] 합니까?")
S("상투 꼭지에서 물린 주식은 '기다리면 본전 오겠지'라며 가문의 유산처럼 쥐고 있고,", "quote", lines=["상투 꼭지에서 물린 주식은", "'기다리면 본전 오겠지' — [가문의 유산]처럼 쥐고 있고"], ant="걱정", size=86)
S("조금만 수익이 나면 '앗싸!' 하고 팔아서 작은 용돈을 챙깁니다.", "quote", lines=["조금만 수익이 나면", "{'앗싸!'} 하고 팔아서", "작은 용돈을 챙깁니다"], ant="환호", size=100)
S("결과가 어떻게 되죠?", "qa", q="결과가 [어떻게] 되죠?")
S2("계좌에는 쓰레기 같은 부실 주식과 악성 매물만 가득 차고, 우상향하는 진짜 알짜배기 자산은 내 계좌에서 다 쫓겨나게 됩니다.",
   ("계좌에는 쓰레기 같은 부실 주식과 악성 매물만 가득 차고,", "ledger", dict(headline="남는 건 [악성 매물]뿐", rows=ROWS, show_only=[1, 3], hold=[1, 3], t_sell=0.3)),
   ("우상향하는 진짜 알짜배기 자산은 내 계좌에서 다 쫓겨나게 됩니다.", "flow", dict(headline="알짜배기는 [쫓겨납니다]", nodes=[dict(t="우상향하는 진짜 알짜배기", s="", c="red", icon="↑"), dict(t="내 손으로 매도", s="작은 용돈", c="gold", icon="$"), dict(t="내 계좌에서 퇴출", s="", c="blue", icon="→")])))
S("자산이 불어날 리가 있나요?", "qa", q="자산이 [불어날 리]가 있나요?")
Q("내 손으로 황금알을 낳는 거위의 배를 가르고 있는 꼴입니다.", "내 손으로 [황금알을 낳는 거위]의", "배를 가르고 있는 꼴", ant="경고", size=100)

# ═════════════ 본론 2 ═════════════
CH("02", "시장의 잔인한 진실 — 돈이 움직이는 [진짜 알고리즘]", "02 · 시장의 잔인한 진실", name="시장의 잔인한 진실 — 돈이 움직이는 진짜 알고리즘")
Q("시장은 여러분의 감정을 위로해 주는 자선사업가가 아닙니다.", "시장은 여러분의 감정을 위로해 주는", "[자선사업가]가 {아닙니다}", ant="팔짱", size=96)
S("냉혹한 제로섬 게임의 장소예요.", "kpi", kicker="냉혹한", big="제로섬 게임", color="gold", unit="의 장소", size=210)
S("여러분이 두려움에 떨며 던져버린 주식, 손절매하며 눈물 흘린 그 자산들은 다 어디로 갈까요?", "flow", headline="던져버린 주식은 [어디로] 갈까요?",
  nodes=[dict(t="두려움에 던진 주식", s="", c="blue", icon="↓"), dict(t="손절매하며 흘린 눈물", s="그 자산들", c="blue", icon="!"), dict(t="어디로 갈까?", s="", c="gold", icon="?")])
S("시장의 흐름을 꿰뚫고 있는 스마트머니, 즉 기관과 외국인의 곳간으로 고스란히 들어갑니다.", "flow", headline="[스마트머니]의 곳간으로",
  nodes=[dict(t="개인이 던진 물량", s="", c="blue", icon="↓"), dict(t="스마트머니", s="기관과 외국인", c="gold", icon="$"), dict(t="곳간으로 고스란히", s="", c="red", icon="▣")])
S("그들은 폭락장에서도 감정에 휘둘리지 않고 철저하게 가치와 데이터로 움직입니다.", "compare", headline="폭락장에서도 [감정에 휘둘리지] 않는다",
  left=dict(title="스마트머니", c="red", rows=["감정에 휘둘리지 않고", "가치와 데이터로 움직임"]), right=dict(title="개인 투자자", c="blue", rows=["공포에 던지고", "감정으로 움직임"]))
S("반면 개인 투자자들은 '내가 팔면 오르고, 내가 사면 떨어지는' 저주에 걸린 것처럼 행동하죠.", "chart", headline="'내가 팔면 오르고, 내가 사면 떨어진다'", badge="개념도 · 실제 수치 아님",
  lines=[dict(name="주가", color="gold", pts=[.5, .45, .3, .2, .35, .55, .8, .92], end="")], marks=[dict(x=.28, text="내가 판 자리", color="blue"), dict(x=.82, text="내가 산 자리", color="red")])
Q("저주가 아니라 여러분의 '심리적 취약점'을 세력들이 완벽하게 해킹당하고 있는 겁니다.", "저주가 아니라", "여러분의 [심리적 취약점]이", "{완벽하게 해킹}당하고 있습니다", ant="의심", size=92)

# ═════════════ 클로징 ═════════════
CH("03", "뼈때리는 조언 — 이번 주 [액션 플랜]", "03 · 이번 주 액션 플랜", name="뼈때리는 조언 — 이번 주 액션 플랜")
Q("자, 이번 주 여러분의 계좌를 열고 냉정하게 점검해 보십시오.", "이번 주, 계좌를 열고", "[냉정하게 점검]해 보십시오", ant="확인", size=104)
S("지금 가지고 있는 종목이 오를 것 같아서 들고 있습니까, 아니면 손실 본 게 아까워서 눈감고 외면하고 있습니까?", "signal", headline="들고 있는 [진짜 이유]는?",
  lamps=[dict(c="red", t="오를 것 같아서", s="들고 있습니까?"), dict(c="blue", t="손실 본 게 아까워서", s="눈감고 외면하고 있습니까?")])
Q("진짜 부자들의 법칙은 단순합니다.", "진짜 부자들의 법칙은", "[단순]합니다", ant="선언", size=120)
S("'못난 놈은 과감히 도려내고, 잘 나가는 놈의 엉덩이를 끝까지 두드려주는 것.'", "compare", headline="진짜 부자들의 법칙",
  left=dict(title="못난 놈은", c="blue", rows=["과감히 도려낸다"]), right=dict(title="잘 나가는 놈은", c="red", rows=["엉덩이를 끝까지 두드려준다"]))
Q("감정에 지배당하는 순간, 경제적 자유는 평생 화면 너머의 이야기일 뿐입니다.", "감정에 지배당하는 순간", "경제적 자유는 평생", "{화면 너머의 이야기}일 뿐입니다", size=92)
Q("오늘 제 이야기가 뼈를 때렸다면, 좋아요와 구독을 누르시고 다음 주에도 냉정한 경제학의 눈으로 여러분의 지갑을 지켜드리겠습니다.", "뼈를 때렸다면", "[좋아요]와 [구독]을!", "다음 주에도 냉정한 경제학의 눈으로 지갑을 지켜드리겠습니다", ant="인사", size=84)
Q("감사합니다.", "[감사합니다]", ant="인사", size=170)


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
