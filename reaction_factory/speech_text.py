"""TTS 전용 '읽기 텍스트' 변환기 (한국어 AI 음성이 바보처럼 들리는 1순위 원인 제거).

자막에는 사람이 읽기 좋은 표기("KFC", "3개", "10만 원", "6월")를 그대로 두고,
음성 엔진에는 실제 한국 사람이 소리 내는 형태("케이에프씨", "세 개", "십만 원", "유월")를 넘긴다.

처리 항목
 - 고유어 수사 + 단위:  3개→세 개, 20살→스무 살, 1번째→첫 번째, 2시 30분→두 시 삼십 분
 - 한자어 수사:          2024년→이천이십사 년, 12,000원→만 이천 원, 10만 원→십만 원, 1.5배→일 점 오 배
 - 특수 읽기:            6월→유월, 10월→시월, 30%→삼십 퍼센트, $5→오 달러, 20대→이십 대
 - 영어:                 사전(브랜드·감탄사) → 한글 발음, 대문자 약어 → 알파벳 한글 읽기, 나머지는 경고
 - 기호/인터넷 표현:      ㅋㅋ ㅠㅠ 이모지 ~ … 따옴표 해시태그 제거, !!/?! 정리
 - 사용자 발음 사전:      data/pronunciation.json  {"표기": "읽기"}  (가장 먼저 적용)
"""
from __future__ import annotations

import json
import re
from functools import lru_cache

from config import DATA_DIR

# ─────────────────────────── 숫자 읽기 ───────────────────────────
_SINO = "영일이삼사오육칠팔구"
_NATIVE_UNIT = ["", "한", "두", "세", "네", "다섯", "여섯", "일곱", "여덟", "아홉"]
_NATIVE_TEN = ["", "열", "스물", "서른", "마흔", "쉰", "예순", "일흔", "여든", "아흔"]


def _under_10000(n: int) -> str:
    out = ""
    for value, name in ((1000, "천"), (100, "백"), (10, "십"), (1, "")):
        d, n = divmod(n, value)
        if d:
            out += ("" if d == 1 and name else _SINO[d]) + name
    return out


def sino(n: int) -> str:
    """한자어 수: 12000 → 만 이천, 100000 → 십만, 2024 → 이천이십사."""
    if n == 0:
        return "영"
    groups = []
    for value, name in ((10**12, "조"), (10**8, "억"), (10**4, "만"), (1, "")):
        g, n = divmod(n, value)
        if g:
            word = "" if (g == 1 and name == "만") else _under_10000(g)  # '일만' 대신 '만'
            groups.append(word + name)
    return " ".join(groups)


def native(n: int, before_counter: bool = True) -> str:
    """고유어 수(1~99). 단위 앞에서는 한/두/세/네/스무 형태."""
    if not 0 < n < 100:
        return sino(n)
    t, u = divmod(n, 10)
    if t == 2 and u == 0:
        return "스무" if before_counter else "스물"
    return _NATIVE_TEN[t] + _NATIVE_UNIT[u]


def decimal(s: str) -> str:
    """'1.5' → 일 점 오 (소수점 아래는 한 자리씩)."""
    whole, _, frac = s.partition(".")
    out = sino(int(whole or 0))
    if frac:
        out += " 점 " + " ".join(_SINO[int(d)] for d in frac)
    return out


# 고유어로 읽는 단위 (긴 것부터 매칭)
NATIVE_COUNTERS = sorted("""개 명 마리 살 시 시간 번 번째 째 잔 병 그릇 장 권 대 가지 곳 달 사람 군데 벌 켤레 송이 판
접시 줄 통 채 척 알 봉지 캔 박스 조각 입 숟가락 바퀴 끼 쌍 분이서 놈 쪽 마디 덩이 대접 포기 근 되 말""".split(),
                         key=len, reverse=True)
# 한자어로 읽는 대표 단위 (이 목록 밖의 숫자도 기본은 한자어)
UNIT_WORDS = {"km": "킬로미터", "kg": "킬로그램", "cm": "센티미터", "mm": "밀리미터", "ml": "밀리리터",
              "g": "그램", "m": "미터", "l": "리터", "℃": "도", "°c": "도", "°": "도", "kcal": "킬로칼로리"}
CURRENCY_PREFIX = {"$": "달러", "₩": "원", "€": "유로", "¥": "엔", "£": "파운드"}
_BEN_SINO_NEXT = ("출구", "버스", "선", "트랙", "방", "게이트", "홀")  # '3번 출구' 는 삼 번

# ─────────────────────────── 영어 ───────────────────────────
LETTERS = dict(zip("ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                   "에이 비 씨 디 이 에프 지 에이치 아이 제이 케이 엘 엠 엔 오 피 큐 알 에스 티 유 브이 더블유 엑스 와이 지".split()))
EN_WORDS = {
    "oh my god": "오 마이 갓", "omg": "오 마이 갓", "oh my gosh": "오 마이 가쉬", "so good": "쏘 굿",
    "wow": "와우", "yes": "예스", "no": "노", "ok": "오케이", "okay": "오케이", "yeah": "예", "hi": "하이",
    "hello": "헬로", "thank you": "땡큐", "thanks": "땡스", "sorry": "쏘리", "bro": "브로", "guys": "가이즈",
    "amazing": "어메이징", "delicious": "딜리셔스", "crazy": "크레이지", "insane": "인세인", "perfect": "퍼펙트",
    "k-pop": "케이팝", "kpop": "케이팝", "k-food": "케이푸드", "k-drama": "케이드라마", "k-beauty": "케이뷰티",
    "youtube": "유튜브", "youtuber": "유튜버", "netflix": "넷플릭스", "instagram": "인스타그램", "tiktok": "틱톡",
    "shorts": "쇼츠", "vlog": "브이로그", "iphone": "아이폰", "galaxy": "갤럭시", "samsung": "삼성",
    "hyundai": "현대", "kia": "기아", "bts": "비티에스", "blackpink": "블랙핑크", "newjeans": "뉴진스",
    "bbq": "비비큐", "kfc": "케이에프씨", "mcdonald's": "맥도날드", "mcdonalds": "맥도날드", "starbucks": "스타벅스",
    "7-eleven": "세븐일레븐", "gs25": "지에스 이십오", "wifi": "와이파이", "wi-fi": "와이파이",
    "korea": "코리아", "korean": "코리안", "seoul": "서울", "busan": "부산", "jeju": "제주",
    "vs": "대", "cctv": "씨씨티비", "atm": "에이티엠", "sns": "에스엔에스", "ai": "에이아이",
    "tv": "티비", "pc": "피씨", "usa": "유에스에이", "uk": "유케이", "ktx": "케이티엑스", "dmz": "디엠지",
    "mbti": "엠비티아이", "sos": "에스오에스", "diy": "디아이와이", "ceo": "씨이오",
}

# ─────────────────────────── 정규식 ───────────────────────────
_EMOJI = re.compile("[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F900-\U0001F9FF️‍]+")
_KOR_SLANG = re.compile(r"[ㅋㅎ]{2,}|[ㅠㅜ]{1,}|ㄷㄷ+|ㄱㄱ+|ㅇㅇ+|ㄹㅇ")
_NUM = r"\d{1,3}(?:,\d{3})+|\d+"


@lru_cache(maxsize=1)
def user_dictionary() -> dict[str, str]:
    path = DATA_DIR / "pronunciation.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("_")}


def _int(s: str) -> int:
    return int(s.replace(",", ""))


def _replace_english(text: str, unknown: list[str]) -> str:
    # 여러 단어 표현 먼저, 그다음 단어 단위
    for phrase in sorted((k for k in EN_WORDS if " " in k), key=len, reverse=True):
        text = re.sub(rf"(?i)\b{re.escape(phrase)}\b", EN_WORDS[phrase], text)

    def word(m: re.Match) -> str:
        w = m.group(0)
        key = w.lower()
        if key in EN_WORDS:
            return EN_WORDS[key]
        if w.isupper() and 2 <= len(w.replace("-", "")) <= 6:          # 약어: KTX → 케이티엑스
            return "".join(LETTERS.get(ch, "") for ch in w if ch.isalpha())
        unknown.append(w)
        return w

    return re.sub(r"[A-Za-z][A-Za-z'\-]*[A-Za-z]|[A-Z]", word, text)


def _replace_numbers(text: str) -> str:
    # 시각 3:30 → 세 시 삼십 분
    text = re.sub(r"(?<!\d)([01]?\d|2[0-4]):([0-5]\d)(?!\d)",
                  lambda m: f"{native(int(m.group(1)))} 시" + (f" {sino(int(m.group(2)))} 분" if int(m.group(2)) else ""),
                  text)
    # 통화 기호 $5, $4.99
    text = re.sub(rf"([$₩€¥£])\s?({_NUM})(\.\d+)?",
                  lambda m: f"{decimal(m.group(2).replace(',', '') + (m.group(3) or ''))} {CURRENCY_PREFIX[m.group(1)]}",
                  text)
    # 퍼센트
    text = re.sub(rf"({_NUM})(\.\d+)?\s?%", lambda m: f"{decimal(m.group(1).replace(',', '') + (m.group(2) or ''))} 퍼센트", text)
    # 범위 3~4개 → 서너/세네 처럼 고유어 두 개 (단위는 뒤 규칙에서)
    text = re.sub(rf"({_NUM})\s?[~\-]\s?({_NUM})(?=\s?(?:{'|'.join(NATIVE_COUNTERS)}))",
                  lambda m: f"{native(_int(m.group(1)))}{native(_int(m.group(2)))} ", text)
    text = re.sub(rf"({_NUM})\s?~\s?({_NUM})", lambda m: f"{sino(_int(m.group(1)))}에서 {sino(_int(m.group(2)))}", text)
    # 월: 6월 유월, 10월 시월
    text = re.sub(r"(?<![\d.])(\d{1,2})\s?월", lambda m: {6: "유월", 10: "시월"}.get(int(m.group(1)), f"{sino(int(m.group(1)))}월"), text)
    # 첫 번째
    text = re.sub(r"(?<!\d)1\s?(번째|째)", "첫 번째", text)
    # 만/억/천 단위가 붙은 숫자: 10만 → 십만, 1만 → 만, 1억 → 일억
    text = re.sub(rf"({_NUM})(\.\d+)?\s?(조|억|만|천|백)",
                  lambda m: ("" if (m.group(3) in "만천백" and m.group(1) == "1" and not m.group(2))
                             else decimal(m.group(1).replace(",", "") + (m.group(2) or ""))) + m.group(3), text)

    # 숫자 + 고유어 단위
    def counter(m: re.Match) -> str:
        n, unit, after = _int(m.group(1)), m.group(2), text[m.end():m.end() + 4]
        if unit == "대" and n >= 10 and n % 10 == 0:          # 20대 → 이십 대 (나이대)
            return f"{sino(n)} {unit}"
        if unit == "번" and after.strip().startswith(_BEN_SINO_NEXT):
            return f"{sino(n)} {unit}"
        if unit == "시" and n > 24:
            return f"{sino(n)} {unit}"
        return f"{native(n)} {unit}"

    text = re.sub(rf"({_NUM})\s?({'|'.join(NATIVE_COUNTERS)})(?![가-힣])|({_NUM})\s?({'|'.join(NATIVE_COUNTERS)})(?=[은는이가을를도만에의와과요])",
                  lambda m: counter(_Fake(m)), text)
    # 숫자 + 단위 기호
    text = re.sub(rf"({_NUM})(\.\d+)?\s?({'|'.join(map(re.escape, sorted(UNIT_WORDS, key=len, reverse=True)))})(?![A-Za-z])",
                  lambda m: f"{decimal(m.group(1).replace(',', '') + (m.group(2) or ''))} {UNIT_WORDS[m.group(3).lower()]}",
                  text, flags=re.I)
    # 소수
    text = re.sub(r"(\d+)\.(\d+)", lambda m: decimal(m.group(0)) + " ", text)
    # 나머지 숫자는 한자어
    text = re.sub(_NUM, lambda m: sino(_int(m.group(0))), text)
    return text


class _Fake:
    """두 갈래 정규식(group 1,2 또는 3,4)을 하나로 다루기 위한 얇은 래퍼."""

    def __init__(self, m: re.Match):
        self._m = m

    def group(self, i: int) -> str:
        return self._m.group(i) or self._m.group(i + 2)

    def end(self) -> int:
        return self._m.end()


def _clean_symbols(text: str) -> str:
    text = _EMOJI.sub("", text)
    text = _KOR_SLANG.sub("", text)
    text = re.sub(r"[\"“”‘’'`「」『』#*_]", "", text)
    text = re.sub(r"[\[\]()<>{}]", " ", text)
    text = re.sub(r"(\.\s?){2,}|…+", ", ", text)             # 말줄임 → 짧은 쉼
    text = re.sub(r"[!！]{2,}", "!", text)
    text = re.sub(r"[?？]{2,}", "?", text)
    text = re.sub(r"[?？][!！]+|[!！]+[?？]", "?", text)
    text = re.sub(r"(?<=[가-힣a-zA-Z])~+(?!\d)", "", text)      # 맛있어요~ → 맛있어요
    text = re.sub(r"(?<!\d)~+|~+(?!\d)", " ", text)            # 숫자 사이(3~4)는 범위라 남김
    text = text.replace("&", " 앤 ").replace("+", " 플러스 ").replace("/", " ").replace("·", " ").replace("=", " ")
    text = re.sub(r"\s+([,.!?])", r"\1", text)
    text = re.sub(r"([,.!?])(?=[^\s,.!?\d])", r"\1 ", text)    # 12,000 / 1.5 는 건드리지 않음
    text = re.sub(r",\s*([.!?])", r"\1", text)
    return re.sub(r"\s{2,}", " ", text).strip(" ,")


def to_speech(text: str) -> tuple[str, list[str]]:
    """자막용 표기 → TTS 읽기 텍스트. (읽기 텍스트, 한글로 못 바꾼 영어 단어 목록)"""
    unknown: list[str] = []
    for src, dst in sorted(user_dictionary().items(), key=lambda kv: -len(kv[0])):
        text = text.replace(src, dst)
    text = _clean_symbols(text)
    text = _replace_numbers(text)          # 숫자를 먼저: '20km' 의 km 를 단위로 읽게
    text = _replace_english(text, unknown)
    text = re.sub(r"\s+([,.!?])", r"\1", text)
    return re.sub(r"\s{2,}", " ", text).strip(), unknown
