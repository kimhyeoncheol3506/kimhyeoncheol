"""숫자·기호 읽기와 된소리 표기 회귀 시험.  python tests/test_pronunciation.py  (또는 pytest)"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from facetube.textnorm import to_speech, phrase_breaks   # noqa: E402
from facetube.g2p import tense_hints                     # noqa: E402
from facetube.textnorm import strip_markup               # noqa: E402
from facetube.pron_dict import pron_hints                # noqa: E402
from facetube.pron_learn import misread_words            # noqa: E402

SPEECH = {
    "직원 3명이": "직원 세 명이", "21명": "스물한 명", "75명": "일흔다섯 명", "20살": "스무 살", "30개": "서른 개",
    "1번째": "첫 번째", "12번째": "열두 번째", "2배": "두 배", "2.5배": "이 점 오 배", "5차례": "다섯 차례",
    "2개월": "이 개월", "3시즌": "삼 시즌", "1번 출구": "일 번 출구", "100명": "백 명", "10,980명": "만 구백팔십 명",
    "1시 30분": "한 시 삼십 분", "11시": "열한 시", "13시": "십삼 시", "09:30": "아홉 시 삼십 분", "오후 3:00": "오후 세 시",
    "24시간": "스물네 시간", "6월 10일": "유월 십 일", "지난 10월": "지난 시월",
    "2026.10.16": "이천이십육 년 시월 십육 일", "2026-10": "이천이십육 년 시월",
    "-2.3%": "마이너스 이 점 삼 퍼센트", "+5%": "플러스 오 퍼센트", "4.2%p": "사 점 이 퍼센트포인트", "12.2%": "십이 점 이 퍼센트",
    "1/3": "삼분의 일", "3·1절": "삼일절", "6·25 전쟁": "육이오 전쟁", "미국·중국": "미국 중국",
    "1조 2천억 원": "일조 이천억 원", "1,131억 달러": "천백삼십일억 달러",
    # -ㄹ게요 된소리(현철님 2026-11-02 "보여드릴게요는 보여드릴께요라고 읽어줘 앞으로도 쭉")
    "지금부터 하나씩 보여 드릴게요.": "지금부터 하나씩 보여 드릴께요.", "보여드릴게요": "보여드릴께요", "제가 할게요": "제가 할께요",
    "알려 드릴게.": "알려 드릴께.", "보여 드릴게요, 그럼": "보여 드릴께요, 그럼", "그럴걸요": "그럴껄요", "할수록": "할쑤록",
    "게임": "게임", "이렇게요": "이렇게요", "날씨가 맑게": "날씨가 맑게", "길게 늘어선 줄": "길게 늘어선 줄", "멀게 느껴진다": "멀게 느껴진다",
}
TENSE = {
    "해낼 수 있을까요?": "해낼 쑤 있을까요?", "볼 것입니다": "볼 껏입니다", "갈 거야": "갈 꺼야", "먹을 데가": "먹을 떼가",
    "여의도 증권가는": "여의도 증꿘까는", "주가와 물가": "주까와 물까", "효과와 성과": "효꽈와 성꽈", "갈등": "갈뜽",
    "결정": "결쩡", "발생한 사건": "발쌩한 사껀", "실질": "실찔", "할게요": "할께요", "할수록": "할쑤록", "가능성": "가능썽",
    "관점": "관쩜", "출시": "출씨", "노벨상급": "노벨쌍급",
    # 바뀌면 안 되는 것
    "알다": "알다", "살던 집": "살던 집", "물도 길도": "물도 길도", "서울 거리": "서울 거리", "결과를": "결과를", "말도 안 된다": "말도 안 된다",
}
# 타입캐스트식 전처리(autotag)·영문 약어·발음 직접 지정 (2026-11-03 발음사전)
AUTOTAG = {
    "GDP 성장률": "지디피 성장률", "AI 투자": "에이아이 투자", "KOSPI 지수": "코스피 지수", "Fed 금리": "연준 금리",
    "S&P500": "에스앤피오백", "HBM 가격": "에이치비엠 가격", "M&A 시장": "엠앤에이 시장", "K-반도체": "케이 반도체",
    "3Q 실적": "삼 분기 실적", "2H 전망": "하반기 전망", "25bp 인상": "이십오 베이시스포인트 인상", "21.5p 하락": "이십일 점 오 포인트 하락",
    "010-1234-5678": "공일공, 일이삼사, 오육칠팔", "₩50,000": "오만 원", "84㎡": "팔십사 제곱미터", "원/달러 환율": "원 달러 환율",
    "PER 6배": "피이알 여섯 배", "YoY 12% 증가": "전년 대비 십이 퍼센트 증가",
    "장단기{{장단끼}} 금리": "장단끼 금리",
    "Fed가 금리를": "연준이 금리를", "GDP는": "지디피는", "Fed로": "연준으로", "AI와": "에이아이와", "HBM을": "에이치비엠을",
    "기준금리 3.00%": "기준금리 삼 퍼센트", "3.50%": "삼 점 오 퍼센트", "S&P500과": "에스앤피오백과", "10년 만에": "십 년 만에",
}
DISPLAY = {"장단기{{장단끼}} 금리": "장단기 금리", "[[금리]]가 {{금니}}": "금리가 금니"}
PRON = {
    "기준금리 인상": "기준금니 인상", "영업이익과 순이익": "영엄니익과 순니익", "금융위원회": "금늉위원회",
    "관리비와 연락처": "괄리비와 열락처", "생산량 확대": "생산냥 확대", "실업률": "시럼뉼", "폭락과 급락": "퐁낙과 금낙",
    "협력 관계": "혐녁 관계", "합리적인 판단력": "함니적인 판단녁", "국민연금": "궁민년금",
    "괜찮은 결과": "괜찮은 결과", "리더십": "리더십",
}
TENSE2 = {"시가총액": "시까총액", "유가 급등": "유까 급등", "유가족": "유가족", "평가": "평까", "분양가": "분양까"}
MISREAD = [("기준금리가 올랐습니다", "기준 금니가 올랐습니다", []),
           ("기준금리가 올랐습니다", "기준 근리가 올랐습니다", ["기준금리"])]

BREAKS = {
    "모두가 의심하던 시기에 가장 정확한 예측을 해왔고 그것을 기술로 증명해 냈기 때문입니다.":
        "모두가 의심하던 시기에 가장 정확한 예측을 해왔고, 그것을 기술로 증명해 냈기 때문입니다.",
    "실업률은 지금의 4.2%에서 2030년 12.2%까지 오를 수 있다고 내다봤습니다.":        # 인용 '-다고' 뒤는 끊지 않는다
        "실업률은 지금의 4.2%에서, 2030년 12.2%까지 오를 수 있다고 내다봤습니다.",
    "내 일을 인공지능이 대신할 몫도 28%와 75%로 갈렸습니다.": "내 일을 인공지능이 대신할 몫도 28%와 75%로 갈렸습니다.",
}


def test_speech():
    bad = {k: (to_speech(k), v) for k, v in SPEECH.items() if to_speech(k) != v}
    assert not bad, bad


def test_tense():
    bad = {k: (tense_hints(k), v) for k, v in TENSE.items() if tense_hints(k) != v}
    assert not bad, bad


def test_breaks():
    bad = {k: (phrase_breaks(k), v) for k, v in BREAKS.items() if phrase_breaks(k) != v}
    assert not bad, bad


def test_autotag():
    bad = {k: (to_speech(k), v) for k, v in AUTOTAG.items() if to_speech(k) != v}
    assert not bad, bad


def test_display_keeps_spelling():
    bad = {k: (strip_markup(k), v) for k, v in DISPLAY.items() if strip_markup(k) != v}
    assert not bad, bad


def test_pron_dict():
    bad = {k: (pron_hints(k), v) for k, v in PRON.items() if pron_hints(k) != v}
    bad.update({k: (tense_hints(k), v) for k, v in TENSE2.items() if tense_hints(k) != v})
    assert not bad, bad


def test_misread():
    bad = []
    for spoken, heard, want in MISREAD:
        got = [w["word"] for w in misread_words(spoken, heard)]
        if got != want:
            bad.append((spoken, heard, got, want))
    assert not bad, bad


if __name__ == "__main__":
    for f in (test_speech, test_tense, test_breaks, test_autotag, test_display_keeps_spelling, test_pron_dict, test_misread):
        f()
    print(f"통과: 숫자·기호 {len(SPEECH)}개, 된소리 {len(TENSE) + len(TENSE2)}개, 끊어 읽기 {len(BREAKS)}개, "
          f"약어·전처리 {len(AUTOTAG)}개, 발음사전 {len(PRON)}개")
