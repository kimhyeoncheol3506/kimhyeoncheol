"""간이 한국어 표준발음 변환(소리 나는 대로 적기).
오프라인 TTS가 연음·비음화를 못 하는 문제를 보완하기 위한 재생성 후보용.
예) '몇 잔일까요' -> '멷 짜닐까요', '봅니다' -> '봄니다'"""
import re

CHO = list("ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ")
JUNG = list("ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ")
JONG = [""] + list("ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ")

SPLIT = {"ㄳ": ("ㄱ", "ㅅ"), "ㄵ": ("ㄴ", "ㅈ"), "ㄶ": ("ㄴ", "ㅎ"), "ㄺ": ("ㄹ", "ㄱ"), "ㄻ": ("ㄹ", "ㅁ"),
         "ㄼ": ("ㄹ", "ㅂ"), "ㄽ": ("ㄹ", "ㅅ"), "ㄾ": ("ㄹ", "ㅌ"), "ㄿ": ("ㄹ", "ㅍ"), "ㅀ": ("ㄹ", "ㅎ"),
         "ㅄ": ("ㅂ", "ㅅ")}
NEUTRAL = {"ㄲ": "ㄱ", "ㅋ": "ㄱ", "ㄳ": "ㄱ", "ㄺ": "ㄱ", "ㅅ": "ㄷ", "ㅆ": "ㄷ", "ㅈ": "ㄷ", "ㅊ": "ㄷ",
           "ㅌ": "ㄷ", "ㅎ": "ㄷ", "ㅍ": "ㅂ", "ㄿ": "ㅂ", "ㅄ": "ㅂ", "ㄵ": "ㄴ", "ㄶ": "ㄴ", "ㄻ": "ㅁ",
           "ㄼ": "ㄹ", "ㄽ": "ㄹ", "ㄾ": "ㄹ", "ㅀ": "ㄹ"}
TENSE = {"ㄱ": "ㄲ", "ㄷ": "ㄸ", "ㅂ": "ㅃ", "ㅅ": "ㅆ", "ㅈ": "ㅉ"}
ASP = {"ㄱ": "ㅋ", "ㄷ": "ㅌ", "ㅂ": "ㅍ", "ㅈ": "ㅊ"}
NASAL = {"ㄱ": "ㅇ", "ㄷ": "ㄴ", "ㅂ": "ㅁ"}


def _dec(ch):
    o = ord(ch) - 0xAC00
    if 0 <= o < 11172:
        return [CHO[o // 588], JUNG[(o % 588) // 28], JONG[o % 28]]
    return None


def _enc(c, j, f):
    return chr(0xAC00 + CHO.index(c) * 588 + JUNG.index(j) * 28 + JONG.index(f))


def pronounce(text):
    syl = [_dec(ch) or ch for ch in text]
    n = len(syl)
    for i in range(n):
        a = syl[i]
        if not isinstance(a, list) or not a[2]:
            continue
        # 다음 한글 음절 찾기(공백 1칸까지 허용, 연음은 붙어있을 때만)
        k, space = i + 1, False
        if k < n and syl[k] == " ":
            k, space = k + 1, True
        if k >= n or not isinstance(syl[k], list):
            a[2] = NEUTRAL.get(a[2], a[2])
            continue
        b = syl[k]
        f, c = a[2], b[0]
        if c == "ㅇ" and not space:                       # 연음
            if f == "ㅇ":
                continue
            if f == "ㅎ":
                a[2] = ""
                continue
            if f in ("ㄶ", "ㅀ"):
                a[2], b[0] = "", SPLIT[f][0]
            elif f in SPLIT:
                a[2], b[0] = SPLIT[f]
            else:
                a[2], b[0] = "", f
            continue
        if f == "ㅎ" and c in ASP and not space:           # 격음화 ㅎ+ㄱ
            a[2], b[0] = "", ASP[c]
            continue
        if f in ("ㄶ", "ㅀ") and c in ASP and not space:
            a[2], b[0] = SPLIT[f][0], ASP[c]
            continue
        nf = NEUTRAL.get(f, f)
        if c == "ㅎ" and nf in ASP and not space:          # 격음화 ㄱ+ㅎ
            a[2], b[0] = "", ASP[nf]
            continue
        if c in ("ㄴ", "ㅁ") and nf in NASAL:              # 비음화
            a[2] = NASAL[nf]
            continue
        if nf in ("ㄱ", "ㄷ", "ㅂ") and c in TENSE:         # 경음화
            a[2], b[0] = nf, TENSE[c]
            continue
        if (nf, c) in (("ㄴ", "ㄹ"), ("ㄹ", "ㄴ")) and not space:  # 유음화
            a[2], b[0] = "ㄹ", "ㄹ"
            continue
        a[2] = nf
    return "".join(_enc(*s) if isinstance(s, list) else s for s in syl)


# ---------------------------------------------------------------- 된소리(경음화) 표기
# 철자로는 안 보이는데 소리는 된소리가 되는 곳만 '소리 나는 대로' 고쳐 적는다(음성 생성용. 화면 자막은 그대로).
# 받침 ㄱㄷㅂ 뒤 된소리(학교→학꾜)처럼 철자로 예측되는 것은 TTS 가 스스로 하므로 건드리지 않는다.
TENSE_WORDS = {   # 사이시옷·한자어 경음(표준발음법 제28·29항류). 긴 말부터 바꾼다
    "증권가": "증꿘까", "증권": "증꿘", "채권": "채꿘", "여권": "여꿘", "인권": "인꿘", "주권": "주꿘",
    "주가": "주까", "물가": "물까", "원가": "원까", "단가": "단까", "정가": "정까",
    "효과": "효꽈", "성과": "성꽈", "사건": "사껀", "조건": "조껀", "요건": "요껀", "안건": "안껀",
    "인기": "인끼", "문법": "문뻡", "헌법": "헌뻡", "불법": "불뻡", "글자": "글짜", "등기": "등끼",
    "관점": "관쩜", "시점": "시쩜", "장점": "장쩜", "단점": "단쩜", "초점": "초쩜", "강점": "강쩜", "문제점": "문제쩜", "쟁점": "쟁쩜",
    "가능성": "가능썽", "생산성": "생산썽", "수익성": "수익썽", "안정성": "안정썽", "효율성": "효율썽", "중요성": "중요썽",
    "필요성": "필요썽", "변동성": "변동썽", "유동성": "유동썽", "건전성": "건전썽", "투명성": "투명썽", "불확실성": "불확실썽",
    "신뢰성": "신뢰썽", "정확성": "정확썽", "인간성": "인간썽",
    # 가격 '-가(價)' (2026-11-03 발음사전). '매매가·전세가·판매가·목표가'는 '~가(조사)'와 겹쳐 빼 둠
    "평가": "평까", "시가총액": "시까총액", "종가": "종까", "호가": "호까", "유가": "유까", "유가족": "유가족",
    "분양가": "분양까", "감정가": "감정까", "낙찰가": "낙찰까", "기준가": "기준까", "적정가": "적정까", "인건비": "인껀비",
}
_DEP = {"수": r"(가|는|도|를|밖에|록|$)", "것": r".*", "거": r"(야|예요|에요|죠|다|라|니|든|면|고|는|를|가|의|예|$)", "데": r"(가|는|도|에|서|$)",
        "바": r"(가|는|를|로|와|에|$)", "줄": r"(을|이|은|도|$)", "적": r"(이|은|도|$)"}
_TENSE_CHO = {"ㄱ": "ㄲ", "ㄷ": "ㄸ", "ㅂ": "ㅃ", "ㅅ": "ㅆ", "ㅈ": "ㅉ"}
_NO_TENSE_NEXT = set("다지자죠더든듯도던서세")   # ㄹ 받침 + 이 음절이면 대개 용언 활용(알다, 살던, 물도) → 그대로


def _tense_first(w):
    d = _dec(w[0])
    if not d or d[0] not in _TENSE_CHO:
        return w
    return _enc(_TENSE_CHO[d[0]], d[1], d[2]) + w[1:]


def _dict_sub(table, text):
    """사전 치환을 한 번에(긴 낱말 우선, 바꾼 자리는 다시 안 바꿈: '유가족'은 '유가'보다 먼저 잡혀 그대로 남는다)."""
    if not table:
        return text
    rx = re.compile("|".join(re.escape(k) for k in sorted(table, key=len, reverse=True)))
    return rx.sub(lambda m: table[m.group(0)], text)


def tense_hints(text):
    text = _dict_sub(TENSE_WORDS, text)
    ws = text.split(" ")
    for i in range(1, len(ws)):                          # ① -ㄹ 관형형 + 의존명사: 할 수 → 할 쑤, 볼 것 → 볼 껏
        prev = re.sub(r"[^가-힣]", "", ws[i - 1])
        if not prev or (_dec(prev[-1]) or ["", "", ""])[2] != "ㄹ" or re.search(r"[,.?!…]$", ws[i - 1]):
            continue
        for dep, tail in _DEP.items():
            if ws[i].startswith(dep) and re.fullmatch(tail, re.sub(r"[,.?!…]+$", "", ws[i][len(dep):])):
                ws[i] = _tense_first(ws[i])
                break
    out = []
    for w in ws:                                         # ② 한 낱말 안 ㄹ + ㄷㅅㅈ(한자어): 갈등→갈뜽, 결정→결쩡, 할게→할께
        s = list(w)
        core = re.sub(r"[,.?!…]+$", "", w)
        for j in range(1, len(s)):
            a, b = _dec(s[j - 1]), _dec(s[j])
            if not (a and b and a[2] == "ㄹ"):
                continue
            if b[0] in ("ㄷ", "ㅅ", "ㅈ") and s[j] not in _NO_TENSE_NEXT:
                s[j] = _enc(_TENSE_CHO[b[0]], b[1], b[2])
            elif core[j:] in ("게", "걸", "게요", "걸요") or core[j:].startswith("수록"):   # 할게요→할께요, 할수록→할쑤록
                s[j] = _enc(_TENSE_CHO[b[0]], b[1], b[2])
        out.append("".join(s))
    return " ".join(out)
