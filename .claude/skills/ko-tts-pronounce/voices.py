# -*- coding: utf-8 -*-
"""Voicebox 목소리 3종 공통 설정. 발음 사전(ko_tts.normalize)은 목소리와 상관없이 모두 거친다.

- 여의도여자: preset Sohee (qwen_custom_voice) - instruct 로 톤 조절
- 여의도남자: 복제 목소리 (engine qwen) - instruct 없음. 이 PC Voicebox 에는 아직 없음(2026-11-28)
- 마포남자  : preset Dylan (qwen_custom_voice) - 30대 초반 맑고 밝은 아나운서·MC 톤 (2026-11-28 생성)

스크립트에서 목소리 고르기: 환경변수 TTS_VOICE=마포남자 (없으면 각 스크립트 기본값)
"""
import os

INSTRUCT = {
    "여의도여자": ("차분하고 또렷한 뉴스 아나운서 톤, 신뢰감 있게, 보통 속도. 쉼표에서 짧게 끊어 읽고 문장 끝은 자연스럽게 내려 닫는다. "
                "숫자와 핵심 낱말은 또박또박 조금 힘주어 읽는다. 높낮이를 살려 단조롭지 않게, 기계처럼 일정하게 읽지 않는다."),
    "마포남자": ("30대 초반 남성 방송 아나운서이자 예능 MC. 맑고 밝으며 힘 있는 음색, 탁하거나 늙은 느낌 없이 젊고 산뜻하게. "
              "또박또박 정확한 발음, 경쾌하고 생동감 있는 진행 톤, 문장 끝을 시원하게 올려 마무리. "
              "신뢰감 있고 친근한 방송 진행자 말투, 약간 빠른 템포."),
}

ENGINE = {"여의도여자": "qwen_custom_voice", "마포남자": "qwen_custom_voice", "여의도남자": "qwen"}

# 남자 목소리 대체 순서: 여의도남자가 없으면 마포남자
MALE_FALLBACK = ["여의도남자", "마포남자"]


def voice(default="여의도여자"):
    return os.environ.get("TTS_VOICE") or default


def instruct(name, fallback=None):
    """qwen_custom_voice 목소리면 그 목소리 instruct, 복제(qwen) 목소리면 None."""
    if ENGINE.get(name) == "qwen":
        return None
    return INSTRUCT.get(name) or fallback


def pick(profiles_by_name, wanted):
    """원하는 목소리가 Voicebox 에 없으면 같은 성별 대체(여의도남자 -> 마포남자)."""
    if wanted in profiles_by_name:
        return wanted
    if wanted in MALE_FALLBACK:
        for n in MALE_FALLBACK:
            if n in profiles_by_name:
                return n
    return wanted
