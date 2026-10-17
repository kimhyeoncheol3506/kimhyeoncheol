"""대본 목소리 검수 테스트:  python tests/test_voice_qa.py"""
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from voice_qa import is_exclamation, lint_segment  # noqa: E402


def seg(text, typ="narration", s=0.0, e=10.0):
    return SimpleNamespace(type=typ, narration=text, speaker="narrator", clip_start=s, clip_end=e)


def issues(text, **kw):
    return [x["issue"] for x in lint_segment(seg(text, **kw), "short", 0)]


def test_translationese():
    assert any("그녀" in i for i in issues("그녀는 매우 놀랐습니다."))
    assert any("것이다" in i for i in issues("이건 최고의 경험이 될 것이다."))


def test_written_style_narration():
    assert any("문어체" in i for i in issues("존은 삼겹살을 처음 먹었다."))
    assert not issues("존은 삼겹살을 처음 먹었는데요.")


def test_long_sentence_and_english():
    assert any("긴 문장" in i for i in issues("오늘은 미국에서 온 친구가 한국의 길거리 음식을 하나도 빠짐없이 전부 먹어 보는 날인데요"))
    assert any("spicy" in i for i in issues("이건 진짜 spicy 해요"))


def test_dub_length():
    assert any("더빙 대사" in i for i in issues("이건 미국에서는 절대로 먹을 수 없는 맛이라서 정말 놀랐어", typ="dub", s=0, e=1.5))


def test_exclamation():
    assert is_exclamation("Oh my god!") and is_exclamation("와!!") and not is_exclamation("나 이거 매일 먹을 수 있어!")


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("OK")
