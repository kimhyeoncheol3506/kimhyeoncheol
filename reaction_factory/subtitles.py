"""4단계(자막): 타임라인 → 동기화된 .srt + 디자인된 .ass

- 나레이션: TTS 단어 타이밍이 있으면 그 시각에 맞추고, 없으면 글자 수 비례로 배분
- 원본 반응 구간: Claude 가 번역한 subtitle_ko 를 노란 자막으로
- 세그먼트별 on_screen_text: 화면 상단 강조 배너
- 숏폼은 영상 제목을 상단에 고정
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from config import settings
from tts_engine import TimelineItem


@dataclass
class Cue:
    start: float
    end: float
    text: str
    style: str  # Narration | Dub | Original | Banner | Title
    speaker: str = ""  # Dub 자막 위에 붙는 이름표


LAYOUT = {
    # 해상도, 줄당 최대 글자수, 폰트 크기
    "long": {"w": 1920, "h": 1080, "chars": 24, "size": 64, "banner": 72, "title": 0, "margin_v": 70},
    "short": {"w": 1080, "h": 1920, "chars": 13, "size": 86, "banner": 78, "title": 92, "margin_v": 560},
}


def split_text(text: str, max_chars: int) -> list[str]:
    """문장부호 → 쉼표 → 띄어쓰기 순으로 끊어 한 화면에 들어갈 덩어리로."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    sentences = [s.strip() for s in re.split(r"(?<=[.!?…~])\s+", text) if s.strip()]
    chunks: list[str] = []
    for s in sentences:
        while len(s) > max_chars:
            cut = max(s.rfind(",", 0, max_chars + 1), s.rfind(" ", 0, max_chars + 1))
            if cut <= max_chars // 3:
                cut = max_chars
            chunks.append(s[:cut + (1 if s[cut:cut + 1] == "," else 0)].strip())
            s = s[cut + 1:].strip() if s[cut:cut + 1] in (",", " ") else s[cut:].strip()
        if s:
            chunks.append(s)
    return chunks


def _timed_chunks(chunks: list[str], start: float, duration: float, words: list[dict]) -> list[tuple[float, float, str]]:
    out = []
    if words:
        # 단어 타이밍 기반: 덩어리의 누적 글자 비율에 해당하는 단어의 끝 시각을 찾는다
        word_ends, acc = [], 0
        for w in words:
            acc += len(w["text"].replace(" ", ""))
            word_ends.append((acc, w["end"]))
        total_w = acc or 1
        total_c = sum(len(c.replace(" ", "")) for c in chunks) or 1
        pos, t0 = 0, words[0]["start"]
        for c in chunks:
            pos += len(c.replace(" ", ""))
            target = pos / total_c * total_w
            t1 = next((e for a, e in word_ends if a >= target), word_ends[-1][1])
            out.append((start + t0, start + max(t1, t0 + 0.4), c))
            t0 = t1
        return out
    total_c = sum(len(c) for c in chunks) or 1
    t = start
    for c in chunks:
        d = duration * len(c) / total_c
        out.append((t, t + d, c))
        t += d
    return out


def build_cues(timeline: list[TimelineItem], fmt: str, title: str = "") -> list[Cue]:
    lay = LAYOUT[fmt]
    cues: list[Cue] = []
    for item in timeline:
        seg = item.segment
        speech_end = item.start + item.duration
        if item.type in ("narration", "dub"):
            style = "Dub" if item.type == "dub" else "Narration"
            chunks = split_text(seg["narration"], lay["chars"] * 2)
            for s, e, text in _timed_chunks(chunks, item.start, item.duration - 0.25, item.words):
                cues.append(Cue(s, min(e, speech_end), wrap(text, lay["chars"]), style,
                                seg.get("speaker", "") if style == "Dub" else ""))
        elif seg.get("subtitle_ko"):
            chunks = split_text(seg["subtitle_ko"], lay["chars"] * 2)
            for s, e, text in _timed_chunks(chunks, item.start, item.duration, []):
                cues.append(Cue(s, e, wrap(text, lay["chars"]), "Original"))
        if seg.get("on_screen_text"):
            cues.append(Cue(item.start, speech_end, seg["on_screen_text"], "Banner"))
    if fmt == "short" and title and timeline:
        end = timeline[-1].start + timeline[-1].duration
        cues.append(Cue(0, end, wrap(title, 12), "Title"))
    return cues


def wrap(text: str, width: int) -> str:
    """두 줄 이내로 균형 있게 줄바꿈."""
    if len(text) <= width:
        return text
    mid = len(text) // 2
    spaces = [i for i, ch in enumerate(text) if ch == " "]
    cut = min(spaces, key=lambda i: abs(i - mid)) if spaces else mid
    return text[:cut].strip() + "\n" + text[cut:].strip()


# ─────────────────────────── 파일 쓰기 ───────────────────────────
def _srt_time(t: float) -> str:
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(cues: list[Cue], path: Path) -> Path:
    body = [c for c in cues if c.style in ("Narration", "Dub", "Original")]
    lines = []
    for i, c in enumerate(sorted(body, key=lambda c: c.start), 1):
        text = f"[{c.speaker}] {c.text}" if c.speaker else c.text
        lines += [str(i), f"{_srt_time(c.start)} --> {_srt_time(c.end)}", text, ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _ass_time(t: float) -> str:
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360_000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def _ass_escape(text: str) -> str:
    return text.replace("\n", "\\N").replace("{", "(").replace("}", ")")


def write_ass(cues: list[Cue], path: Path, fmt: str) -> Path:
    lay = LAYOUT[fmt]
    font = settings.subtitle_font
    # 색상: &HAABBGGRR
    styles = [
        f"Style: Narration,{font},{lay['size']},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,2,2,60,60,{lay['margin_v']},1",
        f"Style: Dub,{font},{lay['size']},&H00FFE8A0,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,2,2,60,60,{lay['margin_v']},1",
        f"Style: Original,{font},{lay['size']},&H0000E5FF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,2,2,60,60,{lay['margin_v']},1",
        f"Style: Banner,{font},{lay['banner']},&H00FFFFFF,&H000000FF,&H002B2BE8,&H00000000,-1,0,0,0,100,100,0,0,3,14,0,8,60,60,{60 if fmt == 'long' else 330},1",
        f"Style: Title,{font},{lay['title'] or 80},&H0000F0FF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,7,0,8,50,50,110,1",
    ]
    events = []
    for c in sorted(cues, key=lambda c: (c.start, c.style)):
        text = _ass_escape(c.text)
        if c.speaker:  # 노란 이름표 + 줄바꿈 후 본문 스타일 복귀
            text = f"{{\\fs{int(lay['size'] * 0.75)}\\c&H0000E5FF&}}{_ass_escape(c.speaker)}\\N{{\\r}}" + text
        if c.style in ("Narration", "Dub", "Original"):
            text = "{\\fad(80,60)}" + text
        if c.style == "Banner":
            text = "{\\fad(120,120)} " + text + " "
        layer = 1 if c.style in ("Banner", "Title") else 0
        events.append(f"Dialogue: {layer},{_ass_time(c.start)},{_ass_time(c.end)},{c.style},,0,0,0,,{text}")
    content = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {lay['w']}
PlayResY: {lay['h']}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
{chr(10).join(styles)}

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
{chr(10).join(events)}
"""
    path.write_text(content, encoding="utf-8")
    return path


def make_subtitles(timeline: list[TimelineItem], fmt: str, folder: Path, title: str = "") -> tuple[Path, Path]:
    cues = build_cues(timeline, fmt, title)
    return write_srt(cues, folder / "subtitles.srt"), write_ass(cues, folder / "subtitles.ass", fmt)
