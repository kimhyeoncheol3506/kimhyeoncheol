"""TTS 읽기 변환 회귀 테스트:  python -m pytest tests  또는  python tests/test_speech_text.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from speech_text import native, sino, to_speech  # noqa: E402

CASES = [
    ("삼겹살 3인분에 소주 2병 시켰어요.", "삼겹살 삼인분에 소주 두 병 시켰어요."),
    ("고기가 3개 남았는데요", "고기가 세 개 남았는데요"),
    ("20살 대학생 존은", "스무 살 대학생 존은"),
    ("21명이 줄을 섰습니다", "스물한 명이 줄을 섰습니다"),
    ("1번째 메뉴는", "첫 번째 메뉴는"),
    ("2번 먹었어요", "두 번 먹었어요"),
    ("3번 출구로 나가면", "삼 번 출구로 나가면"),
    ("2시 30분에 도착", "두 시 삼십분에 도착"),
    ("3:30에 만나요", "세 시 삼십 분에 만나요"),
    ("2시간 기다렸대요", "두 시간 기다렸대요"),
    ("가격은 12,000원입니다", "가격은 만 이천원입니다"),
    ("10만 원짜리", "십만 원짜리"),
    ("1만 원이면", "만 원이면"),
    ("1억 뷰 돌파", "일억 뷰 돌파"),
    ("2024년에 처음 왔어요", "이천이십사년에 처음 왔어요"),
    ("6월이랑 10월에", "유월이랑 시월에"),
    ("조회수가 30% 늘었어요", "조회수가 삼십 퍼센트 늘었어요"),
    ("미국에선 $5였는데", "미국에선 오 달러였는데"),
    ("1.5배 더 매워요", "일 점 오 배 더 매워요"),
    ("20대 여성들 사이에서", "이십 대 여성들 사이에서"),
    ("서울에서 5km 떨어진", "서울에서 오 킬로미터 떨어진"),
    ("KFC보다 맛있대요", "케이에프씨보다 맛있대요"),
    ("BTS 노래가 나오자", "비티에스 노래가 나오자"),
    ("K-pop 콘서트", "케이팝 콘서트"),
    ("Oh my god! 이게 뭐야", "오 마이 갓! 이게 뭐야"),
    ("KTX 타고 부산까지", "케이티엑스 타고 부산까지"),
    ("ㅋㅋㅋ 진짜 웃겨요ㅠㅠ", "진짜 웃겨요"),
    ("맛있어요~!!", "맛있어요!"),
    ("과연 결과는...?", "과연 결과는?"),
    ("대박🔥🔥 이건 꼭 먹어야 돼요", "대박 이건 꼭 먹어야 돼요"),
    ("\"이건 미쳤다\"라고 말했어요", "이건 미쳤다라고 말했어요"),
    ("3~4개씩 먹었어요", "세네 개씩 먹었어요"),
]


def test_numbers():
    assert sino(12000) == "만 이천"
    assert sino(2024) == "이천이십사"
    assert sino(110000) == "십일만"
    assert native(20) == "스무" and native(99) == "아흔아홉"


def test_cases():
    bad = []
    for src, want in CASES:
        got, _ = to_speech(src)
        if got != want:
            bad.append(f"{src!r}\n   want {want!r}\n   got  {got!r}")
    assert not bad, "\n".join(bad)


def test_unknown_english_flagged():
    _, unknown = to_speech("This is so spicy 진짜")
    assert "spicy" in unknown


if __name__ == "__main__":
    test_numbers()
    test_unknown_english_flagged()
    test_cases()
    print("OK")
