import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, "/home/user/kimhyeoncheol/.claude/skills/ranking-video/voice")
from pronounce import sino as _s
sino = lambda n: _s(int(n)); DIG = "영일이삼사오육칠팔구"
CFG = json.load(open(f"{ROOT}/00_data/topic.json", encoding="utf-8"))


def dec(v):
    a, _, b = v.partition("."); return sino(int(a)) + (" 점 " + " ".join(DIG[int(c)] for c in b) if b else "")


def won(n):
    r = int(n / 1000 + 0.5); m, k = divmod(r, 10)
    if k == 0: return sino(m * 10000) + " 원", f"{m}만 원"
    return ((sino(m * 10000) + " ") if m else "") + sino(k * 1000) + " 원", ((f"{m}만 ") if m else "") + f"{k}천 원"


def tok(kind, v):
    if kind == "p": return won(int(v))
    if kind == "e": n = int(v); return sino(n).replace("만 천", "만 일천") + " 원", f"{n:,}원"  # '이만 천이백'은 '이천이백'으로 들림 → '이만 일천이백'
    if kind == "pc": return sino(int(v)) + " 퍼센트", f"{v}%"
    if kind == "k": return sino(int(v)) + " 킬로그램", f"{v}kg"
    if kind == "kd": return dec(v) + " 킬로그램", f"{v}kg"
    if kind == "g": return sino(int(v)) + " 그램", f"{v}g"
    if kind == "n": return sino(int(v)), v
    if kind == "kq": return sino(int(v)) + " 킬로그램", f"{int(v):,}kg"
    if kind == "y": return sino(int(v)) + "년", f"{v}년"
    raise ValueError(kind)


SUBFIX = []  # 아래에서 채움


def S(text, **sig):
    tts = re.sub(r"\{(\w+):([^}]+)\}", lambda m: tok(m.group(1), m.group(2))[0], text)
    sub = re.sub(r"\{(\w+):([^}]+)\}", lambda m: tok(m.group(1), m.group(2))[1], text)
    for a, b in sorted(SUBFIX, key=lambda x: -len(x[0])): sub = sub.replace(a, b)
    return [tts, sig, sub]
