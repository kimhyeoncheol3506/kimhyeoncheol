"""돈 단위 앞 숫자는 한자어로 읽는다 (2026-11-16 현철님 지정: 달러·엔·유로 모두). python3 -m pytest neural-studio/tests/test_currency_reading.py"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "..", "video-studio", "voice"))
from facetube.textnorm import to_speech  # noqa: E402
import pronounce  # noqa: E402

CASES = {"80달러": "팔십", "99달러": "구십구", "45달러": "사십오", "20엔": "이십", "90유로": "구십", "30파운드": "삼십", "1달러": "일", "70위안": "칠십"}
NATIVE = ("여든", "아흔", "마흔", "스무", "스물", "서른", "쉰", "예순", "일흔", "한 달러")


def test_model2():
    for t, want in CASES.items():
        out = to_speech(t)
        assert want in out and not any(n in out for n in NATIVE), (t, out)
    assert "세 달" in to_speech("3달 뒤")


def test_model1():
    for t, want in CASES.items():
        out = pronounce.numbers(t)
        assert want in out and not any(n in out for n in NATIVE), (t, out)
