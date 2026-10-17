"""5단계: 자동 컷편집 + 영상 조립 (FFmpeg).

[원본 컷(인트로/핵심 장면)] + [AI 나레이션·캐릭터 더빙] + [디자인 자막(ASS)] + [AI 추천 사진 삽입] + [효과음] + [BGM]
→ 업로드용 MP4 (롱폼 1920x1080 / 숏폼 1080x1920) + 썸네일 + 업로드 텍스트

과정
 1) 세그먼트마다 짧은 클립을 렌더링 (같은 해상도/fps/코덱으로 통일)
    - narration: 원본 영상 구간 + 원본 소리 덕킹 + TTS
    - original : 원본 영상 구간 + 원본 소리 그대로 (번역 자막)
    - dub      : 원본 영상 구간 + 원본 소리 약하게 + 인물 목소리 한국어 더빙
    - 같은 장면이 반복되는 나레이션 구간은 AI 추천 사진으로 자동 교체(빈 구간 채우기)
    - frame    : 대표 프레임 이미지에 천천히 줌인(Ken Burns) + TTS
 2) 이어 붙이기 → 3) 자막 굽기 + BGM + 라우드니스(-14 LUFS) + 페이드아웃
 4) 검수용 편집 프로젝트(컷별 mp4 + FCPXML + SRT) 내보내기
"""
from __future__ import annotations

import shutil
from pathlib import Path
from xml.sax.saxutils import escape

from config import BGM_DIR, FONT_DIR, OUTPUT_DIR, settings
from frame_selector import best_thumbnail, load_catalog
from script_generator import VideoScript
from sfx import sfx_path
from subtitles import LAYOUT, make_subtitles
from tts_engine import TimelineItem
from utils import console, has_audio_stream, load_json, media_duration, run_ffmpeg, save_json, video_size

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
            # 원본/더빙 구간은 6% 펀치인(정확히 목표 해상도로 다시 자름 — 반올림으로 크기가 어긋나지 않게)
            zw, zh = int(self.W * 1.06) // 2 * 2, int(self.H * 1.06) // 2 * 2
            zoom = f",scale={zw}:{zh},crop={self.W}:{self.H},setsar=1" if item.type in ("original", "dub") else ""
            vf = f"[0:v]{_fit_filter(src['w'], src['h'], self.W, self.H)}{zoom},fps={FPS},format=yuv420p[v]"
            src_audio = "0:a" if src["audio"] else None

        # 오디오: 원본(덕킹) + TTS + 효과음 + 무음 베이스
        parts, mix = [], []
        if src_audio:
            vol = {"narration": settings.source_duck_volume, "dub": settings.dub_duck_volume}.get(item.type, 1.0)
            parts.append(f"[{src_audio}]aresample=48000,volume={vol}[sa]")
            mix.append("[sa]")
        n_in = 1
        if item.audio:
            args += ["-i", item.audio]
            parts.append(f"[{n_in}:a]aresample=48000[na]")
            mix.append("[na]")
            n_in += 1
        fx = sfx_path(seg.get("sfx", "none"))
        if fx:
            args += ["-i", fx]
            parts.append(f"[{n_in}:a]aresample=48000,volume={settings.sfx_volume}[fx]")
            mix.append("[fx]")
            n_in += 1
        args += ["-f", "lavfi", "-t", f"{dur:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
        mix.append(f"[{n_in}:a]")
        parts.append(f"{''.join(mix)}amix=inputs={len(mix)}:duration=longest:normalize=0,"
                     f"atrim=0:{dur:.3f},afade=t=in:d=0.05,afade=t=out:st={max(dur - 0.08, 0):.3f}:d=0.08[a]")

        graph = vf + ";" + ";".join(parts)
        run_ffmpeg(args + ["-filter_complex", graph, "-map", "[v]", "-map", "[a]",
                           "-t", f"{dur:.3f}", *VCODEC, *ACODEC, out])
        return out

    # ─────────────────────────── 빈 구간 채우기 ───────────────────────────
    def fill_gaps(self, timeline: list[TimelineItem]) -> int:
        """나레이션 구간이 이미 보여 준 원본 장면을 또 쓰면, 아직 안 쓴 AI 추천 사진으로 바꾼다."""
        used_ranges: dict[int, list[tuple[float, float]]] = {}
        used_frames: dict[int, set[int]] = {}
        for item in timeline:  # 대본이 직접 고른 사진은 먼저 '사용됨' 처리
            seg = item.segment
            if seg["visual"] == "frame":
                used_frames.setdefault(seg["source_index"], set()).add(seg["frame_index"])
        filled = 0
        for item in timeline:
            seg = item.segment
            idx = seg["source_index"]
            if seg["visual"] != "clip":
                continue
            src = self._src(idx)
            start = min(seg["clip_start"], max(0.0, src["duration"] - item.duration))
            end = start + item.duration
            ranges = used_ranges.setdefault(idx, [])
            overlap = sum(max(0.0, min(end, b) - max(start, a)) for a, b in ranges)
            if item.type != "original" and overlap > 0.6 * item.duration:
                catalog = [c for c in load_catalog(src["folder"])
                           if c["usable"] and c["index"] not in used_frames.get(idx, set())]
                if catalog:
                    pick = min(catalog, key=lambda c: abs(c["time"] - seg["clip_start"]) - c["reaction"] * 2)
                    seg.update(visual="frame", frame_index=pick["index"], auto_filled=True)
                    if seg.get("sfx", "none") == "none":
                        seg["sfx"] = "shutter"
                    used_frames.setdefault(idx, set()).add(pick["index"])
                    filled += 1
                    continue
            ranges.append((start, end))
        return filled

    # ─────────────────────────── 2) + 3) 조립 ───────────────────────────
    def assemble(self, timeline: list[TimelineItem], script: VideoScript) -> Path:
        console.print(f"[bold]편집[/] {self.fmt} {self.W}x{self.H} · {len(timeline)}컷")
        filled = self.fill_gaps(timeline)
        if filled:
            console.print(f"  · 빈 구간 채우기: 반복 장면 {filled}곳을 AI 추천 사진으로 교체")
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
        self._export_project(clips, srt, script)
        shutil.rmtree(self.work, ignore_errors=True)
        segs = [t.segment for t in timeline]
        save_json(self.out_dir / "report.json", {
            "duration": round(total, 1), "cuts": len(timeline),
            "photos": sum(s["visual"] == "frame" for s in segs), "auto_filled": filled,
            "sfx": sum(s.get("sfx", "none") != "none" for s in segs),
            "dubbed": sum(t.type == "dub" for t in timeline),
            "original": sum(t.type == "original" for t in timeline),
            "subtitle_lines": sum(1 for line in srt.read_text(encoding="utf-8").split("\n\n") if line.strip()),
        })
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
        frame = best_thumbnail(self._src(hook.segment["source_index"])["folder"])  # AI 썸네일 점수 1위
        if frame is None:
            return
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

    def _export_project(self, clips: list[Path], srt: Path, script: VideoScript) -> None:
        """검수·수정용 편집 프로젝트: 컷별 mp4(자막 없음) + FCPXML 타임라인 + SRT.

        DaVinci Resolve(무료)·Final Cut 에서 FCPXML 을 열면 컷이 순서대로 놓이고,
        CapCut/Premiere 에는 segments 폴더 영상과 SRT 를 그대로 끌어다 놓으면 된다.
        """
        proj = self.out_dir / "edit_project"
        seg_dir = proj / "segments"
        shutil.rmtree(proj, ignore_errors=True)
        seg_dir.mkdir(parents=True)
        shutil.copy2(srt, proj / "subtitles.srt")
        assets, spine, offset = [], [], 0
        for i, clip in enumerate(clips):
            target = seg_dir / clip.name
            shutil.move(str(clip), target)
            frames = max(1, round(media_duration(target) * FPS))
            uri = target.resolve().as_uri()
            assets.append(f'    <asset id="a{i}" name="{target.stem}" src="{uri}" start="0s" duration="{frames}/{FPS}s" '
                          f'hasVideo="1" hasAudio="1" format="r0" audioSources="1" audioChannels="2" audioRate="48000"/>')
            spine.append(f'          <asset-clip ref="a{i}" name="{target.stem}" offset="{offset}/{FPS}s" '
                         f'duration="{frames}/{FPS}s" format="r0" tcFormat="NDF"/>')
            offset += frames
        title = escape(script.title)
        (proj / "timeline.fcpxml").write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE fcpxml>
<fcpxml version="1.8">
  <resources>
    <format id="r0" frameDuration="1/{FPS}s" width="{self.W}" height="{self.H}"/>
{chr(10).join(assets)}
  </resources>
  <library>
    <event name="{title}">
      <project name="{title} ({self.fmt})">
        <sequence format="r0" duration="{offset}/{FPS}s" tcStart="0s" tcFormat="NDF" audioLayout="stereo" audioRate="48k">
          <spine>
{chr(10).join(spine)}
          </spine>
        </sequence>
      </project>
    </event>
  </library>
</fcpxml>
""", encoding="utf-8")

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
