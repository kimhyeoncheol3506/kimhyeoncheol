"""대본을 Voicebox(Qwen3-TTS)가 자연스럽게 읽도록 '읽는 대로' 바꾼다.

사용:
  python ko_tts.py "삼성전자 HBM 매출이 $1.5B, 전년 대비 23.4% 늘었다."
  python ko_tts.py --file 대본.txt            # 변환문 출력 + 사전에 없는 영어 경고
  python ko_tts.py --test                     # samples.txt 전부 변환해 발음샘플.md 작성
  from ko_tts import normalize                # 다른 스크립트에서 TTS 직전에 호출

자막은 원문을 쓰고, 음성에만 normalize() 결과를 넣는다.
"""
import json, os, re, sys
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "pronounce_dict.json"), encoding="utf-8"))
WORDS = {k: v for k, v in D["words"].items() if not k.startswith("_")}
UNITS = D["units"]
CURRENCY = D["currency"]
NATIVE = sorted(D["native_counters"], key=len, reverse=True)
SINO_EXC = D["sino_exceptions_after_number"]
LETTERS = D["english_letters"]

DIG = "영일이삼사오육칠팔구"
DIG_PHONE = "공일이삼사오육칠팔구"
NAT1 = ["", "한", "두", "세", "네", "다섯", "여섯", "일곱", "여덟", "아홉"]
NAT10 = ["", "열", "스물", "서른", "마흔", "쉰", "예순", "일흔", "여든", "아흔"]
SCALE = {"K": 10**3, "k": 10**3, "M": 10**6, "B": 10**9, "T": 10**12,
         "thousand": 10**3, "million": 10**6, "billion": 10**9, "trillion": 10**12}
NUM = r"\d[\d,]*(?:\.\d+)?"
# 숫자+단위 뒤에 와도 되는 것: 끝, 공백, 문장부호, 조사·어미 첫 글자
AFTER = r"(?=$|[\s.,!?·)\]\"'…~\-/]|이|가|을|를|은|는|도|만|에|의|씩|째|과|와|로|으로|부터|까지|짜리|정도|쯤|당|밖|이상|이하|가량|여|넘|동안|전|후|뒤|안|내|나|씩|라|이다|입니다|였|이었)"


def sino_int(n: int) -> str:
    """정수를 한자어 수로: 123456789 -> 일억 이천삼백사십오만 육천칠백팔십구"""
    if n == 0:
        return "영"
    def four(x):
        s = ""
        for unit, d in (("천", x // 1000), ("백", x // 100 % 10), ("십", x // 10 % 10)):
            if d:
                s += ("" if d == 1 else DIG[d]) + unit
        if x % 10:
            s += DIG[x % 10]
        return s
    parts, units = [], ["", "만", "억", "조", "경"]
    i = 0
    while n:
        g = n % 10000
        if g:
            w = four(g)
            if i == 1 and g == 1:
                w = ""  # 1만 -> 만
            parts.append(w + units[i])
        n //= 10000
        i += 1
    return " ".join(reversed(parts))


def sino(numstr: str) -> str:
    numstr = numstr.replace(",", "")
    if "." in numstr:
        a, b = numstr.split(".", 1)
        return sino_int(int(a or 0)) + " 점 " + "".join(DIG[int(c)] for c in b)
    if len(numstr) > 1 and numstr.startswith("0"):
        return "".join(DIG_PHONE[int(c)] for c in numstr)
    return sino_int(int(numstr))


def native(n: int, before_counter=True) -> str:
    if n == 20 and before_counter:
        return "스무"
    t, o = divmod(n, 10)
    w = NAT10[t] + NAT1[o]
    return w


def read_with_scale(numstr, scale_word):
    v = Decimal(numstr.replace(",", "")) * SCALE[scale_word]
    if v == v.to_integral_value():
        return sino_int(int(v))
    return sino(format(v.normalize(), "f"))


def money(m):
    sym, num, sc = m.group(1), m.group(2), m.group(3)
    unit = CURRENCY[sym]
    if sc:
        return read_with_scale(num, sc.strip()) + " " + unit
    if unit == "달러" and "." in num and len(num.split(".")[1]) == 2:
        a, b = num.replace(",", "").split(".")
        cents = int(b)
        return sino_int(int(a)) + " 달러" + (f" {sino_int(cents)} 센트" if cents else "")
    return sino(num) + " " + unit


def time_(m):
    h, mi = int(m.group(1)), int(m.group(2))
    if h > 24 or mi > 59:
        return m.group(0)
    if h == 0 or h == 24:
        h12, ampm = 12, "밤 "
    elif h < 12:
        h12, ampm = h, ""
    elif h == 12:
        h12, ampm = 12, "낮 "
    else:
        h12, ampm = h - 12, "오후 "
    s = ampm + native(h12) + " 시"
    if mi:
        s += " " + sino_int(mi) + " 분"
    return s


def date_(y, mo, d):
    s = (sino(y) + " 년 ") if y else ""
    return s + month(int(mo)) + " " + sino_int(int(d)) + " 일"


def month(n):
    return {6: "유월", 10: "시월"}.get(n, sino_int(n) + " 월")


def counter(m):
    num, cnt = m.group(1), m.group(2)
    plain = num.replace(",", "")
    if cnt in NATIVE_SET and "." not in plain and 0 < int(plain) < 100 and not plain.startswith("0"):
        return native(int(plain)) + " " + cnt
    return sino(num) + " " + cnt


def replace_words(text):
    for k in sorted(WORDS, key=len, reverse=True):
        v = WORDS[k]
        if re.search(r"[A-Za-z]", k):
            text = re.sub(r"(?<![A-Za-z])" + re.escape(k) + r"(?![A-Za-z])", v, text)
        else:
            text = text.replace(k, v)
    return text


NATIVE_SET = set(NATIVE)
EN_NUM = {"0": "제로", "1": "원", "2": "투", "3": "쓰리", "4": "포", "5": "파이브", "6": "식스", "7": "세븐", "8": "에잇", "9": "나인", "10": "텐", "11": "일레븐", "12": "트웰브"}
RANGE_UNITS = ["개월", "원", "만원", "억원", "조원", "달러", "년", "월", "일", "분", "초", "세", "층", "회", "위", "주", "점", "도", "만", "억", "조", "천"]
UNKNOWN = []


def normalize(text: str) -> str:
    t = text
    t = t.translate(str.maketrans("０１２３４５６７８９－–—−～〜％＄", "0123456789----~~%$"))
    # 1) 화면비(16:9), 전화번호, 날짜, 시각, 점수
    t = re.sub(r"(?<![\d:])(16|9|1|4|3|21|2|5):(9|16|1|3|4|5|2)(?![\d:])(?=\s*(?:비율|화면|세로|가로|영상|쇼츠|$|[,.)\s]))",
               lambda m: f"{sino(m.group(1))} 대 {sino(m.group(2))}", t)
    t = re.sub(r"(?<!\d)(0\d{1,2})-(\d{3,4})-(\d{4})(?!\d)",
               lambda m: " ".join("".join(DIG_PHONE[int(c)] for c in g) for g in m.groups()), t)
    t = re.sub(r"(?<!\d)(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})\.?(?!\d)",
               lambda m: date_(m.group(1), m.group(2), m.group(3)), t)
    t = re.sub(r"(?<!\d)(\d{1,2}):(\d{2})(?!\d)", time_, t)
    t = re.sub(r"(?<!\d)(\d{1,2}):(\d{1,2})(?![\d])", lambda m: f"{sino(m.group(1))} 대 {sino(m.group(2))}", t)
    def slash(m):
        a, b = int(m.group(1)), int(m.group(2))
        if 1 <= a <= 12 and 1 <= b <= 31 and not (a < b <= 10):
            return month(a) + " " + sino_int(b) + " 일"
        return f"{sino_int(b)}분의 {sino_int(a)}"
    t = re.sub(r"(?<![\d/])(\d{1,2})/(\d{1,2})(?![\d/])", slash, t)
    # 2) 사전 단어
    t = replace_words(t)
    # 2-1) AI 모델 버전: 정수는 영어식(비오 3 -> 비오 쓰리, 지피티-5 -> 지피티 파이브), 소수는 한국식(제미나이 이 점 오)
    am = "|".join(re.escape(x) for x in sorted(D.get("ai_models", []), key=len, reverse=True))
    if am:
        t = re.sub(r"(" + am + r")[\s-]?(\d{1,2})(?![\d.])", lambda m: m.group(1) + " " + EN_NUM.get(m.group(2), m.group(2)), t)
    # 3) 통화 기호 ($1.5B, $100, ₩5,000)
    cur = "|".join(re.escape(c) for c in sorted(CURRENCY, key=len, reverse=True))
    t = re.sub(r"(" + cur + r")\s?(" + NUM + r")(\s?(?:K|M|B|T|thousand|million|billion|trillion)(?![A-Za-z]))?", money, t)
    # 4) 범위 10~20명 -> 10명~20명
    rng = sorted(set(NATIVE) | set(UNITS) | set(RANGE_UNITS), key=len, reverse=True)
    t = re.sub(r"(" + NUM + r")\s?~\s?(" + NUM + r")\s?(" + "|".join(re.escape(u) for u in rng) + ")",
               lambda m: f"{m.group(1)}{m.group(3)}에서 {m.group(2)}{m.group(3)}", t)
    t = re.sub(r"(" + NUM + r")\s?~\s?(" + NUM + r")", r"\1에서 \2", t)
    # 5) 부호
    t = t.replace("▲", " 상승 ").replace("▼", " 하락 ").replace("△", " 플러스 ").replace("▽", " 마이너스 ")
    t = re.sub(r"(?:(?<=^)|(?<=[\s(]))\+(?=\d)", "플러스 ", t)
    t = re.sub(r"(?:(?<=^)|(?<=[\s(]))-(?=\d)", "마이너스 ", t)
    # 6) 숫자 배율 (10K, 3.2B), 숫자+단위기호
    t = re.sub(r"(" + NUM + r")(K|M|B|T)(?![A-Za-z])", lambda m: read_with_scale(m.group(1), m.group(2)), t)
    t = re.sub(r"(" + NUM + r")\s?(thousand|million|billion|trillion)(?![A-Za-z])",
               lambda m: read_with_scale(m.group(1), m.group(2)), t)
    us = "|".join(re.escape(u) for u in sorted(UNITS, key=len, reverse=True) if u not in ("K", "k", "M", "B", "T"))
    t = re.sub(r"(" + NUM + r")\s?(" + us + r")(?![A-Za-z²³])", lambda m: m.group(1) + UNITS[m.group(2)], t)
    # 7) 월(6월 유월, 10월 시월), 예외(3번 출구), 고유어 단위, 나머지 숫자
    t = re.sub(r"(?<![\d.])(\d{1,2})월", lambda m: month(int(m.group(1))) if 1 <= int(m.group(1)) <= 12 else m.group(0), t)
    t = re.sub(r"(?<![\d.])(\d+)번째", lambda m: ("첫" if m.group(1) == "1" else native(int(m.group(1)), False) if int(m.group(1)) < 100 else sino(m.group(1))) + " 번째", t)
    for e in SINO_EXC:
        t = re.sub(r"(" + NUM + r")\s?" + re.escape(e), lambda m: sino(m.group(1)) + " " + e, t)
    nat = "|".join(re.escape(c) for c in NATIVE)
    t = re.sub(r"(?<![\d.])(" + NUM + r")\s?(" + nat + r")" + AFTER, counter, t)
    t = re.sub(r"(" + NUM + r")\s?(?=[가-힣])", lambda m: sino(m.group(1)) + ("" if re.match(r"[십백천만억조경로이가을를은는도에의와과부까보]", m.string[m.end():m.end()+1] or "") else " "), t)
    t = re.sub(NUM, lambda m: sino(m.group(0)), t)
    t = re.sub(r"(?<![가-힣])일([십백천])", r"\1", t)  # 1천 -> 천
    t = re.sub(r"(?<![가-힣])일만", "만", t)  # 1만 -> 만
    # 8) 남은 영어: 대문자 약어는 알파벳으로, 나머지는 경고
    def caps(m):
        w = m.group(0)
        if w.isupper() and len(w) <= 6:
            return "".join(LETTERS[c] for c in w)
        UNKNOWN.append(w)
        return w
    t = re.sub(r"[A-Za-z]+", caps, t)
    # 9) 기호 정리
    t = t.replace("·", ", ").replace("→", ", ").replace("…", "...").replace("/", " ")
    t = re.sub(r"[\[\]{}<>「」『』【】]", " ", t)
    t = re.sub(r"[ \t]{2,}", " ", t)
    return t.strip()


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__); return
    if a[0] == "--test":
        rows = []
        for line in open(os.path.join(HERE, "samples.txt"), encoding="utf-8"):
            line = line.rstrip("\n")
            if not line.strip():
                continue
            if line.startswith("## "):
                rows.append(f"\n{line}\n\n| 원문 | Voicebox에 넣을 문장 |\n|---|---|"); continue
            rows.append(f"| {line} | {normalize(line)} |")
        out = os.path.join(HERE, "발음샘플.md")
        open(out, "w", encoding="utf-8").write("# 발음 샘플 (원문 → 읽는 대로)\n" + "\n".join(rows) + "\n")
        print(out)
    else:
        src = open(a[1], encoding="utf-8").read() if a[0] == "--file" else " ".join(a)
        sys.stdout.reconfigure(encoding="utf-8")
        print(normalize(src))
    if UNKNOWN:
        print("\n[사전에 없는 영어 — pronounce_dict.json words에 추가 권장]:", ", ".join(sorted(set(UNKNOWN))), file=sys.stderr)


if __name__ == "__main__":
    main()
