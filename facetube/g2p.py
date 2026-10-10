"""간이 한국어 표준발음 변환(소리 나는 대로 적기).
오프라인 TTS가 연음·비음화를 못 하는 문제를 보완하기 위한 재생성 후보용.
예) '몇 잔일까요' -> '멷 짜닐까요', '봅니다' -> '봄니다'"""

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
