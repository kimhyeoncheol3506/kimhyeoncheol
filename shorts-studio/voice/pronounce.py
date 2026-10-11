"""발음 교정: TTS에 넣기 직전 '읽는 글'만 한국인이 실제로 말하는 형태로 바꾼다. (자막은 그대로)

  7시 → 일곱 시, 3개 → 세 개, 1통 → 한 통, 1시간 46분 → 한 시간 사십육 분, 25만 원 → 이십오만 원
  MBTI → 엠비티아이, ㅎㅎ → 흐흐, ㅠㅠ → (삭제), X(곱하기/대결) → 엑스
  + voice/lexicon.json : QA에서 반복해서 뭉개진 단어 → 자연스러운 대체어 (계속 누적)

사용: python voice/pronounce.py projects/<프로젝트>   # 바뀌는 부분만 미리보기
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SINO = "영일이삼사오육칠팔구"
NATIVE = {1: "한", 2: "두", 3: "세", 4: "네", 5: "다섯", 6: "여섯", 7: "일곱", 8: "여덟", 9: "아홉", 10: "열",
          11: "열한", 12: "열두", 20: "스무"}
# 고유어 수사로 읽는 단위
NATIVE_UNITS = ["시간", "시", "개", "통", "번", "명", "잔", "살", "마리", "가지", "달", "군데", "권", "병", "곳"]
ABBR = {"MBTI": "엠비티아이", "SNS": "에스엔에스", "LP": "엘피", "DM": "디엠", "ON": "온", "OFF": "오프",
        "OK": "오케이", "CC": "씨씨", "TMI": "티엠아이", "AI": "에이아이", "PC": "피씨", "KTX": "케이티엑스"}
JAMO = [(r"ㅋ{2,}", "크크"), (r"ㅎ{2,}", "흐흐"), (r"ㅠ+|ㅜ+", ""), (r"ㅇㅇ", "응응"), (r"ㄱㄱ", "고고"),
        (r"ㅇㅋ", "오케이"), (r"ㄹㅇ", "리얼"), (r"ㅅㅂ|ㅆㅂ", ""), (r"ㅅㅅ", "그거")]


def sino(n: int) -> str:
    if n == 0:
        return "영"
    out = ""
    for unit, v in (("억", 10 ** 8), ("만", 10 ** 4)):
        q, n = divmod(n, v)
        if q:
            out += (sino(q) if q > 1 or unit != "만" else "") + unit + " "
    for unit, v in (("천", 1000), ("백", 100), ("십", 10)):
        q, n = divmod(n, v)
        if q:
            out += (SINO[q] if q > 1 else "") + unit
    if n:
        out += SINO[n]
    return out.strip()


def native(n: int) -> str | None:
    if n in NATIVE:
        return NATIVE[n]
    if 13 <= n <= 19:
        return "열" + NATIVE[n - 10]
    if 21 <= n <= 29:
        return "스물" + NATIVE[n - 20]
    return None


def numbers(text: str) -> str:
    units = "|".join(sorted(NATIVE_UNITS, key=len, reverse=True))

    def repl_native(m):
        n, u = int(m.group(1)), m.group(2)
        if u == "시간" or n < 30:
            w = native(n)
            if w:
                return f"{w} {u}"
        return f"{sino(n)} {u}"
    text = re.sub(rf"(\d+)\s?({units})(?![가-힣]*(?:장|급))", repl_native, text)
    text = re.sub(r"(\d+)\s?(만|천|백)\s?원", lambda m: f"{sino(int(m.group(1)))}{m.group(2)} 원", text)
    text = re.sub(r"(\d+)", lambda m: sino(int(m.group(1))), text)
    return re.sub(r"\s{2,}", " ", text)


def lexicon():
    f = HERE / "lexicon.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def fix(text: str) -> str:
    t = text.replace("*", "")
    for a, b in lexicon().items():
        if not a.startswith("_"):
            t = t.replace(a, b)
    for pat, rep in JAMO:
        t = re.sub(pat, rep, t)
    for a, b in ABBR.items():
        t = re.sub(rf"(?<![A-Za-z]){a}(?![A-Za-z])", b, t)
    t = re.sub(r"(?<=[가-힣0-9]) ?X ?(?=[가-힣])", " 엑스 ", t)
    t = re.sub(r"(\d+)\s?%", r"\1 퍼센트", t)
    t = numbers(t)
    t = re.sub(r"\s+([,.?!])", r"\1", t)
    return re.sub(r"\s{2,}", " ", t).strip()


if __name__ == "__main__":
    s = json.loads((Path(sys.argv[1]) / "script.json").read_text(encoding="utf-8"))
    for sc in s["scenes"]:
        f = fix(sc["say"])
        if f != sc["say"]:
            print(f"{sc['id']}: {sc['say']}\n   → {f}")
