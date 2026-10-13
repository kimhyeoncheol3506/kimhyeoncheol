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
        "OK": "오케이", "CC": "씨씨", "TMI": "티엠아이", "AI": "에이아이", "PC": "피씨", "KTX": "케이티엑스",
        # 경제·금융 (econ-video 추가)
        "ETF": "이티에프", "COFIX": "코픽스", "DSR": "디에스알", "LTV": "엘티브이", "DTI": "디티아이", "ISA": "아이에스에이",
        "IRP": "아이알피", "GDP": "지디피", "CPI": "씨피아이", "PCE": "피씨이", "SEC": "에스이씨", "IPO": "아이피오",
        "PER": "피이알", "PBR": "피비알", "EPS": "이피에스", "ROE": "알오이", "KOSPI": "코스피", "KOSDAQ": "코스닥",
        "FOMC": "에프오엠씨", "Fed": "연준", "IMF": "아이엠에프", "PF": "피에프", "REITs": "리츠", "NAV": "엔에이브이",
        "S&P": "에스앤피 ", "AI반도체": "에이아이 반도체", "HBM": "에이치비엠", "USD": "달러", "KRW": "원"}
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


NUMW = "영일이삼사오육칠팔구십백천만억조"


def won_glue(t: str) -> str:
    """원화 금액은 숫자와 '원'을 붙여 한 덩어리로 읽는다 (현철님 규칙, econ-video v1.5.0).
    '백만 원' → '백만원', '일억 팔천만 원' → '일억팔천만원'. 띄어 쓰면 TTS가 '백만 / 원'처럼 끊어 읽는다.
    '원칙·원금·원리' 같은 다른 낱말 앞에서는 붙이지 않는다."""
    pat = re.compile(rf"((?<![가-힣])(?:[{NUMW}]*[십백천만억조][{NUMW}]*\s+)*[{NUMW}]*[십백천만억조][{NUMW}]*)\s*원(?!칙|금|리|화|래|작|본|룸|자|전|소|장|산|형|두|인(?![데가지걸거])|가(?!량))")
    return pat.sub(lambda m: re.sub(r"\s+", "", m.group(1)) + "원", t)


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
    t = re.sub(r"(\d)\s?%\s?p\b|(\d)\s?%p", lambda m: (m.group(1) or m.group(2)) + " 퍼센트포인트", t)
    t = re.sub(r"(\d+)\s?%", r"\1 퍼센트", t)
    # 소수: 0.25 → 영 점 이오 (소수점 아래는 한 자리씩)
    t = re.sub(r"(\d+)\.(\d+)", lambda m: f"{sino(int(m.group(1)))} 점 " + ("" if len(m.group(2)) < 3 else " ").join(SINO[int(c)] for c in m.group(2)), t)  # 3자리 이상은 한 자씩 띄어 (0.022 → 영 점 영 이 이)
    # 한자어로 읽는 단위 (개월·년·월·일·원·배·주) — 고유어 단위 규칙보다 먼저
    t = re.sub(r"(\d+)\s?(개월|주년|배)", lambda m: f"{sino(int(m.group(1)))} {m.group(2)}", t)
    t = re.sub(r"(\d+)세(?![가-힣])|(\d+)세(?=부터|까지|에|에게|의|는|가|미만|이상|이하|이|와|를)", lambda m: f"{sino(int(m.group(1) or m.group(2)))} 세", t)  # 나이: 0세 → [영 세] ('영세'로 붙지 않게)
    t = re.sub(r"(?<!\d)6월", "유월", t)  # 표준 발음: 6월 [유월], 10월 [시월]
    t = re.sub(r"(?<!\d)10월", "시월", t)
    t = re.sub(r"(?<=\d),(?=\d{3})", "", t)  # 천 단위 쉼표 제거: 1,382 → 1382
    t = numbers(t)
    t = won_glue(t)
    t = re.sub(r"\s+([,.?!])", r"\1", t)
    return re.sub(r"\s{2,}", " ", t).strip()


if __name__ == "__main__":
    s = json.loads((Path(sys.argv[1]) / "script.json").read_text(encoding="utf-8"))
    for sc in s["scenes"]:
        f = fix(sc["say"])
        if f != sc["say"]:
            print(f"{sc['id']}: {sc['say']}\n   → {f}")
