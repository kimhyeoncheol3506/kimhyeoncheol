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
NATIVE = {1: "한", 2: "두", 3: "세", 4: "네", 5: "다섯", 6: "여섯", 7: "일곱", 8: "여덟", 9: "아홉"}
NATIVE_TENS = {1: "열", 2: "스물", 3: "서른", 4: "마흔", 5: "쉰", 6: "예순", 7: "일흔", 8: "여든", 9: "아흔"}
# 고유어로 세는 단위(1~99). '개월·시즌·시장' 처럼 한자어로 읽는 말은 아래 SINO_AFTER 로 먼저 걸러 낸다
NATIVE_COUNTERS = ("명", "개", "잔", "살", "마리", "번", "가지", "권", "곳", "시간", "시", "달", "병", "그릇", "장", "차례",
                   "군데", "사람", "송이", "켤레", "척", "벌", "배", "통", "채", "알", "대째")
SINO_AFTER = ("개월", "개국", "개사", "개소", "번지", "번호", "번 출구", "시즌", "시장", "시리즈", "장관", "배럴", "통화", "채권", "알파")


def native(n, before_counter=True):
    """1~99 고유어 수(관형형: 한·두·세·네·스무)."""
    t, u = divmod(n, 10)
    if t == 2 and u == 0:
        return "스무" if before_counter else "스물"
    return NATIVE_TENS.get(t, "") + (NATIVE[u] if u else "")


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
    a = after.lstrip()
    if a.startswith("번째") or a.startswith("째"):
        return "첫" if n == 1 else native(n) if n < 100 else sino(n)
    if a.startswith(SINO_AFTER):
        return sino(n)
    if a.startswith("시") and not a.startswith("시간") and n > 12:      # 13시 이상은 한자어(십삼 시)
        return sino(n)
    if a.startswith(NATIVE_COUNTERS) and 0 < n < 100:
        return native(n)
    return sino(n)


def _date(m):
    y, mo, d = int(m.group(1)), int(m.group(2)), m.group(3)
    mon = {6: "유월", 10: "시월"}.get(mo, sino(mo) + " 월")
    return f"{sino(y)} 년 {mon}" + (f" {sino(int(d))} 일" if d else "")


def _symbols(t):
    """숫자 기호를 읽는 말로: 날짜·시각·분수·부호·범위·가운뎃점·%p."""
    t = re.sub(r"(?<![\d.])(\d{4})[.\-/](\d{1,2})(?:[.\-/](\d{1,2}))?\.?(?![\d])", _date, t)          # 2026.10.16 / 2026-10
    t = re.sub(r"(?<![\d:])(\d{1,2}):(\d{2})(?![\d:])",
               lambda m: (native(int(m.group(1))) if 0 < int(m.group(1)) <= 12 else sino(int(m.group(1)))) + " 시"
               + ("" if m.group(2) == "00" else " " + sino(int(m.group(2))) + " 분"), t)                     # 09:30
    t = re.sub(r"(?<![\d/])(\d+)/(\d+)(?![\d/])", lambda m: f"{sino(int(m.group(2)))}분의 {sino(int(m.group(1)))}", t)   # 1/3
    t = re.sub(r"(\d)\s*[~∼]\s*(?=\d)", r"\1에서 ", t)                                                # 10~20%
    t = re.sub(r"(?<![\w\d])-(?=\d)", "마이너스 ", t)
    t = re.sub(r"(?<![\w\d])\+(?=\d)", "플러스 ", t)
    t = re.sub(r"(\d+)·(\d+)", lambda m: "".join(DIG[int(c)] for c in m.group(1) + m.group(2)), t)       # 3·1절·6·25 → 삼일절·육이오
    t = re.sub(r"\s*·\s*", " ", t)                                                                        # 미국·중국
    t = re.sub(r"%p\b|%포인트", "퍼센트포인트", t)
    return t


UNIT_WORDS = {"%": " 퍼센트", "km": " 킬로미터", "kg": " 킬로그램", "m": " 미터", "g": " 그램",
              "℃": " 도", "$": " 달러"}


SAY_AS = {}   # 대본의 say_as: {REA: 알이에이} → 화면은 그대로, 소리만 바꿔 읽는다(make_editorial 이 채움)


def to_speech(text):
    """화면용 문장 -> TTS가 정확히 읽도록 변환한 문장."""
    t = strip_markup(text)
    for k in sorted(SAY_AS, key=len, reverse=True):
        t = re.sub(r"(?<![A-Za-z])" + re.escape(k) + r"(?![A-Za-z])", SAY_AS[k], t)
    t = t.replace("~", " 에서 ").replace("vs", "대").replace("VS", "대")
    t = re.sub(r"\$(\d[\d,\.]*)", lambda m: m.group(1) + "달러", t)
    t = _symbols(t)
    t = re.sub(r"(?<![\d.,])6\s?월", "유월", t)            # 달 이름은 소리가 바뀐다(육월→유월, 십월→시월)
    t = re.sub(r"(?<![\d.,])10\s?월", "시월", t)

    def rep(m):
        num, unit = m.group(1), m.group(2) or ""
        rest = t[m.end():m.end() + 4]
        word = read_number(num, unit + rest if not unit else unit)
        if not unit and re.match(r"[천백십만억조]", rest):          # 2천억 → 이천억(띄우지 않음)
            return word
        return word + (UNIT_WORDS.get(unit, unit) if unit else " ")

    t = re.sub(r"(\d[\d,]*(?:\.\d+)?)(%|km|kg|℃|m(?![a-z])|g(?![a-z]))?", rep, t)
    t = re.sub(r"[\"'“”‘’「」『』()\[\]]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r" ([,.?!])", r"\1", t)
    return t


_CONNECT = re.compile(r"(고|며|면서|면서도|지만|는데|은데|ㄴ데|아서|어서|여서|해서|으면|면|져|니까|다가|도록|듯이)$")
_TOPIC = re.compile(r"(은|는|에서는|에는|에서|으로는|로는)$")
_QUOTE = re.compile(r"(다고|라고|자고|냐고|느냐고)$")       # 인용 '-다고 내다봤다' 는 붙여 읽는다


def phrase_breaks(text, min_sentence_syl=16, min_gap_syl=6):
    """아나운서식 끊어 읽기: 쉼표가 없어도 쉬는 자리에 쉼표를 넣는다(음성 생성용, 화면 자막에는 안 씀).
    기준(voice_ref/ 아나운서 3명 실측, 2026-11-02): 연결어미(-고 -며 -면서도 -져) 뒤, 길게 시작하는 주제어(~는/~에서는) 뒤에서
    0.3~0.8초 쉰다. 짧은 문장은 그대로 두고, 쉼표 사이는 최소 6음절, 마지막 어절 앞에서는 끊지 않는다."""
    out = []
    for sent in re.split(r"(?<=[.?!])\s+", text.strip()):
        ws = sent.split()
        syl = [len(re.findall("[가-힣]", to_speech(w))) or 1 for w in ws]
        if sum(syl) < min_sentence_syl:
            out.append(sent)
            continue
        since, topic_done, new = 0, False, []
        for i, w in enumerate(ws):
            since += syl[i]
            core = re.sub(r"[^\w가-힣%]+$", "", w)
            left = sum(syl[i + 1:])
            brk = False
            if i < len(ws) - 1 and not re.search(r"[,.?!…]$", w) and since >= min_gap_syl and left >= min_gap_syl:
                if _CONNECT.search(core) and len(core) >= 2 and not _QUOTE.search(core):
                    brk = True
                elif not topic_done and _TOPIC.search(core) and since >= 4 and i <= 2:
                    brk, topic_done = True, True
            if re.search(r"[,…]$", w):
                since = 0
            new.append(w + ("," if brk else ""))
            if brk:
                since = 0
        out.append(" ".join(new))
    return " ".join(out)


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
