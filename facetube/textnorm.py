"""대본 마크업 파싱, 자막 줄나눔, TTS용 한국어 읽기 변환, 오타 검사."""
import re

EMPH = re.compile(r"\[\[(.+?)\]\]")

# ---------------------------------------------------------------- 마크업
def strip_markup(s):
    return EMPH.sub(r"\1", s)


def emphasis_spans(s):
    """'[[405잔]]입니다' -> ('405잔입니다', [(0,4)])"""
    out, spans, pos = "", [], 0
    for m in EMPH.finditer(s):
        out += s[pos:m.start()]
        spans.append((len(out), len(out) + len(m.group(1))))
        out += m.group(1)
        pos = m.end()
    out += s[pos:]
    return out, spans


def split_chunks(sentence, max_chars=17, max_lines=2):
    """한 문장을 자막 덩어리(=TTS 단위=컷 단위)로 나눈다. 마크업은 유지."""
    limit = max_chars * max_lines
    # 1차: 쉼표/물음표 등 절 경계
    parts = [p.strip() for p in re.split(r"(?<=[,，…])\s+", sentence.strip()) if p.strip()]
    chunks = []
    for p in parts:
        while len(strip_markup(p)) > limit:
            words = p.split(" ")
            acc = ""
            for i, w in enumerate(words):
                cand = (acc + " " + w).strip()
                if len(strip_markup(cand)) > limit * 0.62 and acc:
                    chunks.append(acc)
                    p = " ".join(words[i:])
                    break
                acc = cand
            else:
                break
        chunks.append(p)
    # 너무 짧은 덩어리(6자 미만)는 이웃과 합친다(TTS가 짧은 말을 뭉개는 것 방지)
    merged, carry = [], ""
    for c in chunks:
        c = (carry + " " + c).strip() if carry else c
        carry = ""
        if len(strip_markup(c)) < 6:
            if merged and len(strip_markup(merged[-1] + c)) <= limit:
                merged[-1] += " " + c
            else:
                carry = c
            continue
        merged.append(c)
    if carry:
        merged.append(carry)
    return merged


def wrap_lines(text, max_chars=17):
    """자막 1덩어리를 최대 2줄로. 어절 단위, 위아래 길이 균형."""
    plain = strip_markup(text)
    if len(plain) <= max_chars:
        return [text]
    words = text.split(" ")
    best, best_cost = [text], 1e9
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        la, lb = len(strip_markup(a)), len(strip_markup(b))
        cost = abs(la - lb) + (100 if max(la, lb) > max_chars + 3 else 0)
        # [[강조]] 를 줄 사이에서 쪼개지 않기
        if a.count("[[") != a.count("]]"):
            cost += 1000
        if cost < best_cost:
            best, best_cost = [a, b], cost
    return best


# ---------------------------------------------------------------- 숫자 읽기
DIG = "영일이삼사오육칠팔구"
NATIVE = {1: "한", 2: "두", 3: "세", 4: "네", 5: "다섯", 6: "여섯", 7: "일곱", 8: "여덟",
          9: "아홉", 10: "열", 11: "열한", 12: "열두", 13: "열세", 14: "열네", 15: "열다섯",
          16: "열여섯", 17: "열일곱", 18: "열여덟", 19: "열아홉", 20: "스무"}
NATIVE_COUNTERS = ("명", "개", "잔", "살", "마리", "번", "가지", "권", "곳", "시간", "달", "병", "그릇", "장")


def _sino_under_10000(n):
    s = ""
    for unit, name in ((1000, "천"), (100, "백"), (10, "십")):
        d = n // unit
        if d:
            s += ("" if d == 1 else DIG[d]) + name
        n %= unit
    if n:
        s += DIG[n]
    return s


def sino(n):
    if n == 0:
        return "영"
    out = ""
    for unit, name in ((10**12, "조"), (10**8, "억"), (10**4, "만")):
        d = n // unit
        if d:
            out += ("" if (d == 1 and name == "만") else _sino_under_10000(d)) + name + " "
        n %= unit
    if n:
        out += _sino_under_10000(n)
    return out.strip()


def read_number(numstr, after=""):
    numstr = numstr.replace(",", "")
    if "." in numstr:
        a, b = numstr.split(".", 1)
        return sino(int(a)) + " 점 " + "".join(DIG[int(c)] for c in b)
    n = int(numstr)
    if after.startswith(NATIVE_COUNTERS) and 0 < n <= 20:
        return NATIVE[n]
    return sino(n)


UNIT_WORDS = {"%": " 퍼센트", "km": " 킬로미터", "kg": " 킬로그램", "m": " 미터", "g": " 그램",
              "℃": " 도", "$": " 달러"}


def to_speech(text):
    """화면용 문장 -> TTS가 정확히 읽도록 변환한 문장."""
    t = strip_markup(text)
    t = t.replace("~", " 에서 ").replace("vs", "대").replace("VS", "대")
    t = re.sub(r"\$(\d[\d,\.]*)", lambda m: m.group(1) + "달러", t)

    def rep(m):
        num, unit = m.group(1), m.group(2) or ""
        rest = t[m.end():m.end() + 4]
        word = read_number(num, unit + rest if not unit else unit)
        return word + (UNIT_WORDS.get(unit, unit) if unit else " ")

    t = re.sub(r"(\d[\d,]*(?:\.\d+)?)(%|km|kg|℃|m(?![a-z])|g(?![a-z]))?", rep, t)
    t = re.sub(r"[\"'“”‘’「」『』()\[\]]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r" ([,.?!])", r"\1", t)
    return t


def hangul_only(s):
    return re.sub(r"[^가-힣a-zA-Z]", "", s)


def cer(ref, hyp):
    r, h = hangul_only(to_speech(ref)), hangul_only(to_speech(hyp))   # 숫자 표기 차이는 오류로 안 침
    if not r:
        return 0.0
    prev = list(range(len(h) + 1))
    for i, rc in enumerate(r, 1):
        cur = [i] + [0] * len(h)
        for j, hc in enumerate(h, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (rc != hc))
        prev = cur
    return prev[-1] / len(r)


# ---------------------------------------------------------------- 자막 오타 검사
COMMON_TYPOS = {
    "몇일": "며칠", "어떻해": "어떡해", "웬지": "왠지", "금새": "금세", "할께": "할게",
    "되요": "돼요", "됬": "됐", "안되": "안 돼", "어의없": "어이없", "희안": "희한",
    "역활": "역할", "설겆이": "설거지", "오랫만": "오랜만", "왠만": "웬만", "일일히": "일일이",
    "깨끗히": "깨끗이", "곰곰히": "곰곰이", "틈틈히": "틈틈이", "구지": "굳이", "어떻게든지간에": "어떻게든",
    "문안하": "무난하", "애기하": "얘기하", "얘기를하": "얘기를 하", "바램": "바람",
    "들어나": "드러나", "낳았다": "나았다(병) / 낳았다(출산) 확인", "로써": "로서/로써 확인",
}


def lint_subtitle(text):
    """자막 텍스트 문제 목록."""
    issues = []
    plain = strip_markup(text)
    for bad, good in COMMON_TYPOS.items():
        if bad in plain and not good.endswith("확인"):
            issues.append(f"맞춤법 의심 '{bad}' → '{good}'")
    if "  " in plain:
        issues.append("이중 공백")
    if re.search(r"\b(\S+) \1\b", plain):
        issues.append("같은 단어 반복: " + re.search(r"\b(\S+) \1\b", plain).group(0))
    if text.count("[[") != text.count("]]"):
        issues.append("강조 괄호 짝 안 맞음")
    if re.search(r"[A-Za-z가-힣][.?!][가-힣]", plain):
        issues.append("문장부호 뒤 띄어쓰기 없음")
    if re.search(r"[ㄱ-ㅎㅏ-ㅣ]", plain):
        issues.append("자모만 있는 글자(오타 의심)")
    return issues
