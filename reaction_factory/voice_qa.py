"""대본 단계 목소리 검수: 들었을 때 '번역기/로봇' 같은 대사를 TTS 전에 잡는다.

검사 항목
 - 번역투: 그녀/그는/당신/나의/그것은/~하는 것은/~것이다/매우 … (실제 말에서는 거의 안 씀)
 - 문어체 나레이션: '~이다./~했다.' 로 끝나는 해설 (유튜브 나레이션은 '~요/~죠' 구어체)
 - 숨 막히는 문장: 쉼표·마침표 없이 35자 넘게 이어지는 문장 (AI 가 한 호흡에 읽어 억양이 무너짐)
 - 바보 같은 더빙: '와!', '오 마이 갓' 처럼 짧은 감탄사를 더빙 → 원본 소리가 훨씬 자연스러움
 - 영어 잔존: 한글 발음으로 못 바꾼 영어 단어
 - 더빙 길이: 원본 인물이 말한 시간보다 대사가 훨씬 길면 입과 소리가 따로 논다
"""
from __future__ import annotations

import re

from speech_text import to_speech

TRANSLATIONESE = [
    (r"그녀", "'그녀' 는 실제 말에서 안 씀 → 이름이나 '이분/이 친구'"),
    (r"(?<![가-힣])그는(?![가-힣])", "'그는' → 이름이나 '이 친구는'"),
    (r"당신", "'당신' → 생략하거나 '너/여러분'"),
    (r"나의|너의", "'나의/너의' → '내/네'"),
    (r"그것은|이것은", "'그것은/이것은' → '그건/이건'"),
    (r"하는 것은|하는 것이", "'~하는 것은' → '~하는 건/~하는 게'"),
    (r"것이다|것입니다", "'~것이다' → '~거예요/~거죠'"),
    (r"(?<![가-힣])매우(?![가-힣])", "'매우' → '진짜/엄청'"),
    (r"에 대해서|에 관하여", "'~에 대해서' 번역투"),
    (r"할 수 있다고 생각", "'~할 수 있다고 생각한다' 번역투"),
]
WRITTEN_END = re.compile(r"(이다|한다|했다|된다|있다|없다|였다|았다|었다|하였다)[.!]?$")
CHARS_PER_SEC = 7.5  # 한국어 TTS 평균 발화 속도(공백 제외 글자/초)


EXCLAMATIONS = re.compile(r"^(와+|우와+|오+|헐+|대박|미쳤다|세상에|맙소사|오 마이 갓|오 마이 가쉬|와우|아+|으악|꺄+|하하+|헉)[!?.]*$")


def is_exclamation(text: str) -> bool:
    """읽기 형태 기준 6글자 이하이거나 대표 감탄사면 '짧은 감탄사'."""
    spoken, _ = to_speech(text)
    core = re.sub(r"[^가-힣]", "", spoken)
    return len(core) <= 6 or bool(EXCLAMATIONS.match(spoken.strip()))


def lint_segment(seg, fmt: str, index: int) -> list[dict]:
    issues = []
    if seg.type not in ("narration", "dub"):
        return issues
    text = seg.narration.strip()
    for pat, msg in TRANSLATIONESE:
        if re.search(pat, text):
            issues.append(msg)
    if seg.type == "narration":
        for sentence in re.split(r"(?<=[.!?])\s+", text):
            if WRITTEN_END.search(sentence.strip()):
                issues.append(f"문어체 해설 '{sentence.strip()[-12:]}' → '~요/~죠' 구어체")
                break
    for chunk in re.split(r"[,.!?]", text):
        if len(chunk.replace(" ", "")) > 35:
            issues.append("쉼표 없이 너무 긴 문장 → 두 문장으로 나누기")
            break
    _, unknown = to_speech(text)
    if unknown:
        issues.append(f"영어 단어 {', '.join(sorted(set(unknown)))} → 한국에서 쓰는 한글 표기로")
    if seg.type == "dub":
        clip = max(seg.clip_end - seg.clip_start, 0.5)
        est = len(text.replace(" ", "")) / CHARS_PER_SEC
        if est > clip * 1.25:
            issues.append(f"더빙 대사가 원본 발화({clip:.1f}초)보다 김(예상 {est:.1f}초) → 더 짧게")
    return [{"format": fmt, "index": index, "speaker": seg.speaker, "text": text, "issue": m} for m in issues]


def lint(pkg) -> list[dict]:
    out = []
    for script in (pkg.long_form, pkg.short_form):
        for i, seg in enumerate(script.segments):
            out += lint_segment(seg, script.format, i)
    return out


def demote_exclamation_dubs(pkg) -> int:
    """짧은 감탄사 더빙은 원본 소리(+번역 자막)로 바꾼다. AI 가 '와!' 를 연기하면 제일 어색하다."""
    n = 0
    for script in (pkg.long_form, pkg.short_form):
        for seg in script.segments:
            if seg.type == "dub" and is_exclamation(seg.narration):
                seg.type, seg.subtitle_ko, seg.narration = "original", seg.narration, ""
                n += 1
    return n
