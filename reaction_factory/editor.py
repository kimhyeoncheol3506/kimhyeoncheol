"""5단계: 자동 컷편집 + 영상 조립 (FFmpeg).

[원본 컷(인트로/핵심 장면)] + [AI 나레이션] + [디자인 자막(ASS)] + [대표 프레임 이미지 삽입] + [BGM]
→ 업로드용 MP4 (롱폼 1920x1080 / 숏폼 1080x1920) + 썸네일 + 업로드 텍스트

과정
 1) 세그먼트마다 짧은 클립을 렌더링 (같은 해상도/fps/코덱으로 통일)
    - narration: 원본 영상 구간 + 원본 소리 덕킹 + TTS
    - original : 원본 영상 구간 + 원본 소리 그대로 (번역 자막)
    - frame    : 대표 프레임 이미지에 천천히 줌인(Ken Burns) + TTS
 2) 이어 붙이기 → 3) 자막 굽기 + BGM + 라우드니스(-14 LUFS) + 페이드아웃
"""
from __future__ import annotations

import shutil
from pathlib import Path

from config import BGM_DIR, FONT_DIR, OUTPUT_DIR, settings
from script_generator import VideoScript
from subtitles import LAYOUT, make_subtitles
from tts_engine import TimelineItem
from utils import console, has_audio_stream, load_json, media_duration, run_ffmpeg, video_size

FPS = 30
VCODEC = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-r", str(FPS)]
ACODEC = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]


def _fit_filter(src_w: int, src_h: int, W: int, H: int) -> str:
    """원본을 목표 화면에 맞춘다. 비율이 다르면 흐린 배경 위에 원본을 얹는다(쇼츠 필수 레이아웃)."""
    src_ratio, dst_ratio = src_w / src_h, W / H
    if abs(src_ratio - dst_ratio) < 0.02:
        return f"scale={W}:{H},setsar=1"
    if dst_ratio < 1 < src_ratio:
        # 가로 원본 → 세로 쇼츠: 좌우를 잘라 4:3 정도 크기로 화면 가운데에 크게 보여 준다
        fg_h = min(int(W * 0.75) // 2 * 2, H)
        fg_w = int(fg_h * src_ratio) // 2 * 2
        fg = f"scale={fg_w}:{fg_h},crop={min(fg_w, W)}:{fg_h}"
    else:
        fg = f"scale={W}:{H}:force_original_aspect_ratio=decrease"
    return (f"split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
            f"boxblur=24:6,eq=brightness=-0.12[bg];[b]{fg}[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1")


class Editor:
    def __init__(self, source_dirs: list[Path], fmt: str, run_id: str):
        self.sources = source_dirs
        self.fmt = fmt
        self.W, self.H = LAYOUT[fmt]["w"], LAYOUT[fmt]["h"]
        self.out_dir = OUTPUT_DIR / run_id / fmt
        self.work = self.out_dir / "_work"
        self.work.mkdir(parents=True, exist_ok=True)
        self._cache: dict[int, dict] = {}

    def _src(self, idx: int) -> dict:
        if idx not in self._cache:
            folder = self.sources[idx]
            video = folder / "video.mp4"
            w, h = video_size(video)
            self._cache[idx] = {"video": video, "w": w, "h": h, "duration": media_duration(video),
                                "audio": has_audio_stream(video), "folder": folder}
        return self._cache[idx]

    # ─────────────────────────── 1) 세그먼트 렌더 ───────────────────────────
    def render_segment(self, item: TimelineItem) -> Path:
        seg = item.segment
        out = self.work / f"seg_{item.index:03d}.mp4"
        src = self._src(seg["source_index"])
        dur = item.duration
        frame = None
        if seg["visual"] == "frame":
            frames = sorted((src["folder"] / "frames").glob("frame_*.jpg"))
            if frames:
                frame = frames[min(seg["frame_index"], len(frames) - 1)]

        args: list = []
        if frame is not None:
            args += ["-i", frame]  # 이미지 1장 → zoompan 이 n 프레임을 만들어 낸다
            iw, ih = video_size(frame)
            n = int(dur * FPS) + 1
            vf = (f"[0:v]{_fit_filter(iw, ih, self.W, self.H)},scale={self.W * 2}:{self.H * 2},"
                  f"zoompan=z='min(zoom+0.0009,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                  f":d={n}:s={self.W}x{self.H}:fps={FPS},format=yuv420p[v]")
            src_audio = None
        else:
            start = seg["clip_start"]
            if start + dur > src["duration"]:          # 원본 끝을 넘으면 앞으로 당긴다
                start = max(0.0, src["duration"] - dur)
            if dur > src["duration"]:                   # 원본 자체가 더 짧으면 반복
                args += ["-stream_loop", "-1"]
            args += ["-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", src["video"]]
            zoom = ",scale=iw*1.06:ih*1.06,crop=iw/1.06:ih/1.06" if item.type == "original" else ""
            vf = f"[0:v]{_fit_filter(src['w'], src['h'], self.W, self.H)}{zoom},fps={FPS},format=yuv420p[v]"
            src_audio = "0:a" if src["audio"] else None

        # 오디오 그래프
        inputs_audio = []
        if item.audio:
            args += ["-i", item.audio]
            inputs_audio.append(f"[{1}:a]")
        args += ["-f", "lavfi", "-t", f"{dur:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
        silence_idx = 2 if item.audio else 1

        parts = []
        mix = []
        if src_audio:
            vol = settings.source_duck_volume if item.type == "narration" else 1.0
            parts.append(f"[{src_audio}]aresample=48000,volume={vol}[sa]")
            mix.append("[sa]")
        if item.audio:
            parts.append("[1:a]aresample=48000,volume=1.0[na]")
            mix.append("[na]")
        mix.append(f"[{silence_idx}:a]")
        parts.append(f"{''.join(mix)}amix=inputs={len(mix)}:duration=longest:normalize=0,"
                     f"atrim=0:{dur:.3f},afade=t=in:d=0.05,afade=t=out:st={max(dur - 0.08, 0):.3f}:d=0.08[a]")

        graph = vf + ";" + ";".join(parts)
        run_ffmpeg(args + ["-filter_complex", graph, "-map", "[v]", "-map", "[a]",
                           "-t", f"{dur:.3f}", *VCODEC, *ACODEC, out])
        return out

    # ─────────────────────────── 2) + 3) 조립 ───────────────────────────
    def assemble(self, timeline: list[TimelineItem], script: VideoScript) -> Path:
        console.print(f"[bold]편집[/] {self.fmt} {self.W}x{self.H} · {len(timeline)}컷")
        clips = []
        for item in timeline:
            clips.append(self.render_segment(item))
            console.print(f"  · 컷 {item.index + 1}/{len(timeline)} ({item.type}, {item.duration:.1f}s)", end="\r")
        console.print()

        concat_list = self.work / "concat.txt"
        concat_list.write_text("".join(f"file '{c.name}'\n" for c in clips), encoding="utf-8")
        joined = self.work / "joined.mp4"
        run_ffmpeg(["-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", joined])

        srt, ass = make_subtitles(timeline, self.fmt, self.out_dir, title=script.title)
        total = media_duration(joined)
        final = self.out_dir / f"{self.fmt}_final.mp4"
        self._finalize(joined, ass, total, final)
        self._thumbnail(script, timeline)
        self._upload_text(script)
        shutil.rmtree(self.work, ignore_errors=True)
        console.print(f"[green]✔ 완성[/] {final} ({total:.1f}초)  자막: {srt.name}")
        if self.fmt == "short" and total > 60:
            console.print("[yellow]⚠ 쇼츠가 60초를 넘습니다. 일부 플랫폼(인스타 릴스 등)에서 잘릴 수 있습니다.[/]")
        return final

    def _finalize(self, joined: Path, ass: Path, total: float, final: Path) -> None:
        # 자막 필터는 경로 이스케이프가 까다로워(특히 Windows) 출력 폴더를 작업 디렉터리로 쓰고 상대경로로 넘긴다
        sub = f"subtitles=filename={ass.name}:fontsdir='{_fonts_rel(self.out_dir)}'"
        fade_st = max(total - 0.6, 0)
        vf = f"[0:v]{sub},fade=t=out:st={fade_st:.2f}:d=0.6[v]"
        args: list = ["-i", joined.resolve()]
        bgm = BGM_DIR / settings.bgm_file if settings.bgm_file else None
        if bgm and bgm.exists():
            args += ["-stream_loop", "-1", "-i", bgm.resolve()]
            af = (f"[1:a]volume={settings.bgm_volume},atrim=0:{total:.3f}[bg];"
                  f"[0:a][bg]amix=inputs=2:duration=first:normalize=0,")
        else:
            af = "[0:a]"
        af += f"loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st={fade_st:.2f}:d=0.6,aresample=48000[a]"
        _run_in(self.out_dir, args + ["-filter_complex", vf + ";" + af, "-map", "[v]", "-map", "[a]",
                                      *VCODEC, *ACODEC, "-movflags", "+faststart", final.resolve()])

    def _thumbnail(self, script: VideoScript, timeline: list[TimelineItem]) -> None:
        """대표 프레임 + 썸네일 문구 → thumbnail.jpg (롱폼 1280x720 / 숏폼 1080x1920)."""
        hook = next((t for t in timeline if t.segment["section"] == "hook"), timeline[0])
        frames = sorted((self._src(hook.segment["source_index"])["folder"] / "frames").glob("*.jpg"))
        if not frames:
            return
        frame = frames[min(hook.segment.get("frame_index", 0), len(frames) - 1)]
        W, H = (1280, 720) if self.fmt == "long" else (1080, 1920)
        size = 120 if self.fmt == "long" else 130
        text = script.thumbnail_text.replace("\n", "\\N").replace("{", "(").replace("}", ")")
        ass = self.out_dir / "thumb.ass"
        ass.write_text(f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: T,{settings.subtitle_font},{size},&H0000F0FF,&H000000FF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,10,4,2,40,40,{60 if self.fmt == 'long' else 380},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:10.00,T,,0,0,0,,{text}
""", encoding="utf-8")
        iw, ih = video_size(frame)
        vf = (f"{_fit_filter(iw, ih, W, H)},eq=saturation=1.25:contrast=1.08,"
              f"subtitles=filename=thumb.ass:fontsdir='{_fonts_rel(self.out_dir)}'")
        _run_in(self.out_dir, ["-i", frame.resolve(), "-filter_complex", vf, "-frames:v", "1", "-q:v", "2",
                               (self.out_dir / "thumbnail.jpg").resolve()])
        ass.unlink(missing_ok=True)

    def _upload_text(self, script: VideoScript) -> None:
        body = [f"[제목]\n{script.title}", "[제목 후보]\n" + "\n".join(f"- {t}" for t in script.title_candidates),
                f"[설명]\n{script.description}", "[태그]\n" + ", ".join(script.tags),
                f"[고정 댓글]\n{script.pinned_comment}"]
        (self.out_dir / "upload.txt").write_text("\n\n".join(body) + "\n", encoding="utf-8")


def _fonts_rel(cwd: Path) -> str:
    """자막 필터용 폰트 폴더(상대경로 — Windows 드라이브 문자 ':' 이스케이프 문제 회피)."""
    import os

    return Path(os.path.relpath(FONT_DIR.resolve(), cwd.resolve())).as_posix()


def _run_in(cwd: Path, args: list) -> None:
    import os

    prev = os.getcwd()
    os.chdir(cwd)
    try:
        run_ffmpeg(args)
    finally:
        os.chdir(prev)


def render(script: VideoScript, timeline_path: Path, source_dirs: list[Path], run_id: str) -> Path:
    data = load_json(timeline_path)
    timeline = [TimelineItem(**x) for x in data["items"]]
    return Editor(source_dirs, script.format, run_id).assemble(timeline, script)
