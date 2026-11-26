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
_tok0 = tok
def tok(kind, v):
    if kind == "eok":   # 억 단위 금액: 12769 → 일조 이천칠백육십구억 원 / 1조 2,769억 원
        n = int(v); jo, ek = divmod(n, 10000)
        sp = ((sino(jo) + "조 ") if jo else "") + (sino(ek) + "억" if ek else "") ; sb = (f"{jo}조 " if jo else "") + (f"{ek:,}억" if ek else "")
        return sp.strip() + " 원", sb.strip() + " 원"
    if kind == "yr": return sino(int(v)) + "년", f"{v}년"
    return _tok0(kind, v)
_tok1 = tok
def tok(kind, v):
    if kind == "t": n = int(v); return sino(n) + " 톤", f"{n:,}t"
    if kind == "x": return dec(v) + " 배", f"{v}배"
    if kind == "d": a, b = v.split("/"); return sino(int(a)) + "월 " + sino(int(b)) + "일", f"{a}/{b}"
    if kind == "dl": n = int(v); return sino(n) + " 달러", f"{n:,}달러"
    if kind == "u": n, u = v.split("|"); return sino(int(n)) + " " + u, f"{int(n):,}{u}"
    return _tok1(kind, v)
SUBFIX += [("다섯 가지", "5가지"), ("세 가지", "3가지"), ("두 가지", "2가지"), ("두 주", "2주")]
SUBFIX += [(sino(_y) + "년", f"{_y}년") for _y in range(1960, 2031)] + [("십일월", "11월"), ("십이월", "12월"), ("시월", "10월"), ("구월", "9월"), ("일 년", "1년"), ("두 배", "2배"), ("삼 년", "3년"), ("여덟 주", "8주"), ("다섯 단계", "5단계"), ("두 해", "2년"), ("십 년", "10년"), ("영 점 영구 도", "0.09도"), ("오십팔 년", "58년"), ("세 배", "3배"), ("일월 중순", "1월 중순"), ("이틀", "이틀")]
_DAYS = {sino(_n) + "일": f"{_n}일" for _n in range(1, 32)}
import re as _re2
def _dayfix(t):
    return _re2.sub(r"(\d+월) ?((?:" + "|".join(sorted(map(_re2.escape, _DAYS), key=len, reverse=True)) + r"))", lambda m: m.group(1) + " " + _DAYS[m.group(2)], t)
_S0 = S
def S(text, **sig):
    r = _S0(text, **sig); r[2] = _dayfix(r[2]); r[2] = _re2.sub(r"(\d+일)(부터|과|와|까지) (" + "|".join(sorted(map(_re2.escape, _DAYS), key=len, reverse=True)) + r")", lambda m: m.group(1) + m.group(2) + " " + _DAYS[m.group(3)], r[2]); return r
import sys as _sys
_sys.path.insert(0, "/home/user/kimhyeoncheol/video_projects/시장3x3_시리즈/공통")


def r100(n): return int(round(n / 100.0)) * 100


def J(w, a, b):
    c = w[-1]; return w + (a if "가" <= c <= "힣" and (ord(c) - 0xAC00) % 28 else b)


def finish(D, NOTE):
    """대본데이터.json + 00_data/데이터_계산.md(조사표에 들어갈 계산 근거) 저장, 길이 출력"""
    import json as _j
    if __name__ == "short" or _j is None: return
    _j.dump(D, open(f"{HERE}/대본데이터.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(f"{ROOT}/00_data/데이터_계산.md", "w", encoding="utf-8").write(NOTE)
    SECS = D["sections"]; ch = sum(len(x[0].replace(" ", "")) for s_ in SECS for x in s_["sentences"]); n = sum(len(s_["sentences"]) for s_ in SECS)
    print("글자", ch, "문장", n, "예상", round((ch / 6.8 + n * 0.45) / 60 * 753.9 / 720, 1), "분")
    print("'그' 시작:", [x[0][:20] for s_ in SECS for x in s_["sentences"] if x[0].startswith("그")])
