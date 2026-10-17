"""3단계: 원본 자막 → Claude 로 [10% 차별화 + 후킹 + 본문 + 아웃트로] 대본 생성.

출력은 Pydantic 스키마로 강제(structured outputs)되므로 편집기가 그대로 읽을 수 있다.
롱폼/숏폼 대본, 소스 타임코드별 컷편집 가이드, 제목·썸네일 문구·설명란까지 한 번에 만든다.
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal

import anthropic
from pydantic import BaseModel, Field

from config import SCRIPT_DIR, settings
from frame_selector import load_catalog
from voice_qa import demote_exclamation_dubs, lint
from utils import console, fmt_hms, load_json, save_json


# ════════════════════════════════════════════════════════════════
#  출력 스키마
# ════════════════════════════════════════════════════════════════
class Segment(BaseModel):
    section: Literal["hook", "intro", "body", "outro"] = Field(
        description="hook=첫 3~5초(숏폼)/첫 15~30초(롱폼) 후킹, intro=상황 소개, body=본문, outro=마무리+구독 유도")
    type: Literal["narration", "original", "dub"] = Field(
        description="narration=해설자 나레이션(원본 소리 작게), original=원본 반응 소리를 그대로 + 번역 자막, "
                    "dub=외국인 대사를 그 인물 목소리(캐릭터 TTS)로 한국어 더빙(원본 소리 약하게 깔림)")
    speaker: str = Field(description="말하는 사람. narration 은 'narrator', dub/original 은 characters 의 name")
    narration: str = Field(description="narration/dub 일 때 말할 한국어 문장(자막에도 그대로 표시). original 이면 빈 문자열")
    emotion: Literal["neutral", "excited", "surprised", "funny", "curious", "calm", "sad"] = Field(
        description="이 대사를 말하는 감정. 목소리 속도·높낮이·연기 강도에 반영된다")
    subtitle_ko: str = Field(description="type=original 일 때 화면에 띄울 원본 대사의 자연스러운 한국어 번역. narration 이면 빈 문자열")
    on_screen_text: str = Field(description="화면 상단 강조 문구(10자 내외). 없으면 빈 문자열")
    source_index: int = Field(description="사용할 원본 영상 번호(0부터)")
    clip_start: float = Field(description="원본에서 가져올 구간 시작(초)")
    clip_end: float = Field(description="원본에서 가져올 구간 끝(초)")
    visual: Literal["clip", "frame"] = Field(description="clip=원본 영상 구간, frame=대표 프레임 이미지(줌인 효과)")
    frame_index: int = Field(description="visual=frame 일 때 사용할 프레임 카탈로그 번호. 아니면 0")
    sfx: Literal["none", "whoosh", "pop", "ding", "boom", "rise", "shutter"] = Field(
        description="세그먼트 시작에 넣을 효과음. whoosh=장면 전환, pop=문구 등장, ding=정답·포인트, "
                    "boom=충격 반응, rise=긴장 고조(결과 직전), shutter=사진 삽입. 남발하지 말고 필요한 곳만")
    edit_note: str = Field(description="편집자용 컷편집 가이드(줌, 효과음, 정지, 강조 등)")


class VideoScript(BaseModel):
    format: Literal["long", "short"]
    title: str
    title_candidates: list[str] = Field(description="클릭을 부르는 제목 후보 5개")
    thumbnail_text: str = Field(description="썸네일에 넣을 큰 글씨(2줄 이내)")
    hook_strategy: str = Field(description="이 영상의 후킹 전략 한 줄")
    segments: list[Segment]
    description: str = Field(description="유튜브 설명란(원본 출처 링크·채널명 표기 포함)")
    tags: list[str]
    pinned_comment: str = Field(description="댓글 참여를 유도하는 고정 댓글")


class Character(BaseModel):
    name: str = Field(description="화면 표기용 이름(예: '존', '미국 아빠')")
    gender: Literal["male", "female"]
    age: Literal["child", "young", "adult", "senior"]
    description: str = Field(description="국적·관계 등 한 줄 소개")


class KeyMoment(BaseModel):
    source_index: int
    time: float
    summary: str
    why_it_works: str


class ScriptPackage(BaseModel):
    source_summary: str = Field(description="원본 영상들의 핵심 내용 요약(5줄 이내)")
    differentiation_point: str = Field(
        description="원본을 그대로 재가공하지 않고 우리 영상만의 10% 차별화 포인트(정보 추가, 관점, 비교, 반전 등)")
    key_moments: list[KeyMoment] = Field(description="반응이 가장 큰 핵심 장면들")
    characters: list[Character] = Field(description="원본에 등장하는 주요 인물(더빙 목소리 배정에 사용)")
    long_form: VideoScript
    short_form: VideoScript


# ════════════════════════════════════════════════════════════════
#  프롬프트
# ════════════════════════════════════════════════════════════════
SYSTEM_PROMPT = """당신은 구독자 100만 '해외 반응/외국인 반응' 유튜브 채널의 메인 작가 겸 편집 감독입니다.
외국인이 한국 문화·음식·제품을 처음 경험하는 원본 영상을 바탕으로, 한국 시청자가 끝까지 보게 되는 영상 대본과 컷편집 지시서를 씁니다.

## 구조 (반드시 이 순서)
1. hook: 가장 강렬한 반응 장면을 맨 앞에 배치하고, 궁금증을 남기는 한 문장. 결론을 먼저 보여 주되 '왜'는 숨긴다.
   - 숏폼: 첫 3초 안에 승부. / 롱폼: 첫 15~30초 안에 "이 영상을 끝까지 봐야 하는 이유"를 제시.
2. intro: 등장인물(국적·상황)과 맥락을 빠르게 소개.
3. body: 원본 흐름을 따라가며 나레이션(narration)과 원본 반응(original)을 번갈아 배치.
   - 반응이 터지는 순간(감탄, 놀람, 웃음, 리액션 대사)은 type=original 로 원본 소리를 들려주고 subtitle_ko 에 번역을 단다.
   - 중간중간 '다음 장면 예고'(오픈 루프)로 이탈을 막는다.
4. outro: 여운이 남는 한 줄 + 자연스러운 구독/댓글 유도.

## 목소리 3종 활용
- narration: 해설자. 맥락·배경지식·오픈 루프 담당.
- original: 감탄사·웃음·비명처럼 '날것의 소리'가 생명인 순간. subtitle_ko 에 번역.
- dub: 의미 전달이 중요한 외국인 대사(평가, 이유 설명)를 그 인물 목소리로 한국어 더빙. 숏폼에서 특히 효과적.
  dub 의 narration 은 원래 대사의 자연스러운 한국어 구어 번역(1~2문장), speaker 는 해당 인물.
  더빙이 어색해지는 원인을 피하라:
   · '와!', '오 마이 갓', 비명·웃음 같은 짧은 감탄사는 절대 dub 하지 말고 original 로 둔다(AI 연기가 제일 티 난다).
   · 대사 길이는 원본 인물이 실제로 말한 시간(clip 길이) 안에 들어가게: 1초당 7글자 이하.
   · 인물의 말투를 유지: 친구끼리 떠드는 장면은 반말, 인터뷰는 존댓말. 자막 같은 딱딱한 문장 금지.
   · 화면 속 인물의 성별·나이와 characters 의 gender/age 를 정확히 맞춘다.
   · emotion 을 실제 표정·상황에 맞게 지정(놀람 → surprised, 신남 → excited, 설명 → neutral).

## 사진·효과음
- 프레임 카탈로그(장면 설명·반응 강도·썸네일 점수)를 보고 나레이션 내용과 맞는 사진을 visual=frame 으로 넣어라.
  같은 원본 구간이 반복되는 것을 피하는 '빈 구간 채우기' 용도로도 쓴다(usable=false 프레임은 쓰지 않는다).
- 효과음(sfx)은 전체 세그먼트의 30~50% 정도에만. hook 첫 컷은 boom 또는 whoosh, 결과 공개 직전은 rise.

## 10% 차별화
원본을 단순 번역·재업로드하지 말고, 한국인만 아는 배경지식, 숫자/가격 비교, 다른 나라와의 비교, 반전 포인트 등
'우리 영상에서만 얻는 정보'를 최소 10% 이상 녹여라. differentiation_point 에 무엇을 더했는지 적는다.

## 나레이션 문체
- 친근한 존댓말 구어체("~했는데요", "~거든요", "과연 결과는?"). 한 세그먼트는 1~3문장, 읽는 시간 4~15초.
- 숫자·브랜드 약어는 평소 표기대로 써도 된다("3개", "10만 원", "KFC") — 읽기 변환은 프로그램이 자동으로 한다.
  단, 일반 영어 단어("spicy", "delicious")는 한국어로 바꿔 쓴다("맵다", "맛있다"). 이모지·ㅋㅋ·~ 는 쓰지 않는다.
- 한 문장은 25자 안팎으로 짧게, 의미 단위마다 쉼표. 문장 끝 '?', '!' 를 살려 억양이 생기게 한다.
- 번역투 금지: 그녀/그는/당신/나의/그것은/~하는 것은/~것이다/매우 → 실제 한국 사람이 하는 말로.
- 원본에 없는 사실을 지어내지 않는다. 원본 자막·메타데이터에 근거한 내용만 쓰고, 배경지식은 일반적으로 알려진 사실만.
- 특정 국가·인물을 비하하거나 과장된 국뽕 표현은 피한다.

## 타임코드 규칙
- clip_start/clip_end 는 반드시 해당 원본 영상 길이 안의 값이며, 자막 타임스탬프와 '많이 본 구간(highlights)'을 근거로 고른다.
- type=narration 구간의 clip 길이는 대략 나레이션 길이와 비슷하게(편집기가 나레이션 길이에 맞춰 자른다).
- type=original 구간은 3~12초.
- 숏폼(short_form): 전체 40~58초, 세그먼트 6~10개, 세로 화면용이라 on_screen_text 를 적극 사용.
- 롱폼(long_form): 목표 길이 {target_minutes}분 내외. 세그먼트 수는 길이에 맞게 충분히.

## 설명란
원본 영상 제목·채널명·링크를 출처로 반드시 표기한다."""


def _source_block(i: int, folder: Path) -> str:
    meta = load_json(folder / "meta.json")
    tr = load_json(folder / "transcript.json")
    lines = "\n".join(f"[{s['start']:.1f}-{s['end']:.1f}] {s['text']}" for s in tr["segments"])
    hl = ", ".join(f"{h['start']:.0f}~{h['end']:.0f}초" for h in meta.get("highlights", [])) or "정보 없음"
    frames = "\n".join(
        f"  {c['index']} | {c['time']:.1f}초 | {c['description'] or '-'} | {c['reaction']} | {c['thumbnail_score']} | "
        f"{'O' if c['usable'] else 'X'}" for c in load_catalog(folder)) or "  (없음)"
    ch = ", ".join(f"{c['start']:.0f}초 {c['title']}" for c in meta.get("chapters", [])) or "없음"
    return f"""<source index="{i}">
제목: {meta['title']}
채널: {meta['channel']} (구독자 {meta.get('subscribers') or '비공개'}) / 조회수 {meta.get('views')}
링크: {meta['url']}
길이: {meta['duration']:.1f}초 ({fmt_hms(meta['duration'])})
많이 다시 본 구간(highlights): {hl}
챕터: {ch}
프레임 카탈로그 (번호 | 시각 | 장면 | 반응 | 썸네일점수 | 사용가능):
{frames}
설명: {meta.get('description', '')[:800]}
자막 언어: {tr.get('lang') or '없음'}
<transcript>
{lines or '(자막 없음 — 메타데이터와 하이라이트만으로 구성)'}
</transcript>
</source>"""


# ════════════════════════════════════════════════════════════════
#  생성
# ════════════════════════════════════════════════════════════════
def generate_script(source_dirs: list[Path], *, topic: dict | None = None, target_minutes: float = 8,
                    run_id: str, extra_instruction: str = "") -> tuple[ScriptPackage, Path]:
    if not settings.anthropic_api_key:
        raise RuntimeError(".env 에 ANTHROPIC_API_KEY 를 넣어 주세요.")
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    topic_txt = ""
    if topic:
        topic_txt = (f"<topic>주제: {topic['title_ko']} (카테고리: {topic['category_name']}, "
                     f"트렌드 점수 {topic['trend_score']})\n추천 후킹 앵글: {topic['hook_angle']}</topic>\n")
    user = (
        topic_txt
        + "\n".join(_source_block(i, d) for i, d in enumerate(source_dirs))
        + "\n\n위 원본으로 롱폼(long_form)과 숏폼(short_form) 대본 패키지를 만들어 주세요."
        + (f"\n추가 요청: {extra_instruction}" if extra_instruction else "")
    )

    console.print(f"[bold]대본 생성[/] {settings.claude_model} (effort={settings.claude_effort}) …")
    # 긴 출력이라 스트리밍 + get_final_message. 정책상 거절되면 서버가 자동으로 대체 모델로 재시도(fallbacks).
    with client.beta.messages.stream(
        model=settings.claude_model,
        max_tokens=64000,
        system=SYSTEM_PROMPT.format(target_minutes=target_minutes),
        messages=[{"role": "user", "content": user}],
        output_format=ScriptPackage,
        output_config={"effort": settings.claude_effort},
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
    ) as stream:
        final = stream.get_final_message()

    if final.stop_reason == "refusal":
        raise RuntimeError(f"Claude 가 요청을 거절했습니다: {getattr(final, 'stop_details', None)}")
    if final.stop_reason == "max_tokens":
        raise RuntimeError("출력이 max_tokens 에서 잘렸습니다. 롱폼 목표 길이를 줄여 다시 시도하세요.")

    pkg = final.parsed_output
    if pkg is None:  # 안전장치: 텍스트 블록을 직접 검증
        text = "".join(b.text for b in final.content if b.type == "text")
        pkg = ScriptPackage.model_validate_json(text)

    pkg = sanitize(pkg, source_dirs)
    u = final.usage
    console.print(f"[dim]토큰: 입력 {u.input_tokens:,} / 출력 {u.output_tokens:,}[/]")
    pkg, issues = polish_speech(client, pkg)
    path = save_package(pkg, run_id)
    save_json(SCRIPT_DIR / f"{run_id}.voice_qa.json", issues)
    return pkg, path


class SpeechFix(BaseModel):
    format: Literal["long", "short"]
    index: int
    narration: str = Field(description="고친 대사(구어체, 짧게, 번역투·영어 없이)")


class SpeechFixes(BaseModel):
    fixes: list[SpeechFix]


def polish_speech(client: anthropic.Anthropic, pkg: ScriptPackage) -> tuple[ScriptPackage, list[dict]]:
    """목소리 검수: 감탄사 더빙 → 원본 전환, 번역투·문어체·긴 문장·영어 잔존 대사를 Claude 가 한 번 더 다듬는다."""
    demoted = demote_exclamation_dubs(pkg)
    if demoted:
        console.print(f"  · 짧은 감탄사 더빙 {demoted}개 → 원본 소리로 전환")
    issues = lint(pkg)
    if not issues:
        console.print("  · 목소리 검수 통과")
        return pkg, []
    console.print(f"  · 목소리 검수: 어색한 대사 {len(issues)}건 → 자동 교정")
    listing = "\n".join(f"- [{x['format']} #{x['index']}] ({x['speaker']}) \"{x['text']}\" → 문제: {x['issue']}" for x in issues)
    try:
        resp = client.beta.messages.parse(
            model=settings.claude_model,
            max_tokens=16000,
            system="당신은 한국어 유튜브 더빙 대본 감수자입니다. 지적된 대사만, 뜻은 유지하고 한국 사람이 실제로 말하듯 고칩니다.",
            messages=[{"role": "user", "content": f"다음 대사들을 고쳐 주세요. 더빙 대사는 원래 길이보다 짧게.\n{listing}"}],
            output_format=SpeechFixes,
            output_config={"effort": "low"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        fixes = resp.parsed_output.fixes if resp.parsed_output else []
    except anthropic.APIError as exc:
        console.print(f"[yellow]대사 교정 실패(원문 유지): {exc}[/]")
        fixes = []
    for f in fixes:
        script = pkg.long_form if f.format == "long" else pkg.short_form
        if 0 <= f.index < len(script.segments) and script.segments[f.index].type in ("narration", "dub"):
            script.segments[f.index].narration = f.narration
    remaining = lint(pkg)
    console.print(f"  · 교정 후 남은 경고 {len(remaining)}건")
    return pkg, remaining


def sanitize(pkg: ScriptPackage, source_dirs: list[Path]) -> ScriptPackage:
    """모델이 낸 타임코드를 실제 원본 길이 안으로 보정한다."""
    durations = [load_json(d / "meta.json")["duration"] for d in source_dirs]
    n_frames = [max(len(load_catalog(d)), 1) for d in source_dirs]
    for script in (pkg.long_form, pkg.short_form):
        clean = []
        for s in script.segments:
            if s.type in ("narration", "dub") and not s.narration.strip():
                continue
            if s.type == "narration":
                s.speaker = "narrator"
            s.source_index = min(max(s.source_index, 0), len(durations) - 1)
            dur = durations[s.source_index]
            s.clip_start = min(max(0.0, s.clip_start), max(dur - 1.0, 0.0))
            s.clip_end = min(max(s.clip_end, s.clip_start + 1.0), dur)
            s.frame_index = min(max(s.frame_index, 0), n_frames[s.source_index] - 1)
            clean.append(s)
        script.segments = clean
    return pkg


def save_package(pkg: ScriptPackage, run_id: str) -> Path:
    path = SCRIPT_DIR / f"{run_id}.json"
    save_json(path, pkg.model_dump())
    (SCRIPT_DIR / f"{run_id}.md").write_text(to_markdown(pkg), encoding="utf-8")
    return path


def load_package(path: Path) -> ScriptPackage:
    data = load_json(path)
    data.setdefault("characters", [])
    for key in ("long_form", "short_form"):  # 예전 버전 대본 파일 호환
        for seg in data[key]["segments"]:
            seg.setdefault("speaker", "narrator")
            seg.setdefault("sfx", "none")
            seg.setdefault("emotion", "neutral")
    return ScriptPackage.model_validate(data)


def to_markdown(pkg: ScriptPackage) -> str:
    """사람이 보는 대본 + 컷편집 가이드."""
    out = ["# 대본 패키지", "", "## 원본 요약", pkg.source_summary, "",
           "## 10% 차별화 포인트", pkg.differentiation_point, "", "## 핵심 장면"]
    out += [f"- 소스{m.source_index} {fmt_hms(m.time)} — {m.summary} _(이유: {m.why_it_works})_" for m in pkg.key_moments]
    out += ["", "## 등장인물(더빙 목소리)"] + [f"- {c.name} ({c.gender}, {c.age}) — {c.description}" for c in pkg.characters]
    for script in (pkg.long_form, pkg.short_form):
        label = "롱폼" if script.format == "long" else "숏폼"
        out += ["", f"## {label}: {script.title}", "",
                "**제목 후보**: " + " / ".join(script.title_candidates),
                f"**썸네일 문구**: {script.thumbnail_text}", f"**후킹 전략**: {script.hook_strategy}", "",
                "| # | 구간 | 종류 | 소스 타임코드 | 나레이션 / 자막 | 화면 문구 | 컷편집 가이드 |",
                "|---|---|---|---|---|---|---|"]
        for i, s in enumerate(script.segments, 1):
            text = {"narration": s.narration, "dub": f"🗣{s.speaker}: {s.narration}"}.get(s.type, f"🎙원본: {s.subtitle_ko}")
            tc = f"S{s.source_index} {fmt_hms(s.clip_start)}~{fmt_hms(s.clip_end)}"
            if s.visual == "frame":
                tc += f" (프레임 {s.frame_index})"
            note = s.edit_note.replace('|', '/') + (f" 🔊{s.sfx}" if s.sfx != "none" else "")
            out.append(f"| {i} | {s.section} | {s.type} | {tc} | {text.replace('|', '/')} | "
                       f"{s.on_screen_text} | {note} |")
        out += ["", "**설명란**", "```", script.description, "```",
                "**태그**: " + ", ".join(script.tags), f"**고정 댓글**: {script.pinned_comment}"]
    return "\n".join(out) + "\n"
