"""단계별 진행 보드 + '제작·전달 결과' 리포트 (터미널).

01 영상 자료 → 02 대본 → 03 목소리 → 04 사진·편집 → 05 완성
각 단계가 끝날 때마다 상태와 핵심 수치를 보여 주고, 마지막에 검수 포인트(후킹 속도 등)를 경고한다.
"""
from __future__ import annotations

from pathlib import Path

from rich.panel import Panel
from rich.table import Table

from utils import console, load_json

BOARD = [("download", "01 영상 자료", "원본·자막·AI 사진 평가"),
         ("script", "02 대본", "후킹·본문·더빙·효과음 설계"),
         ("tts", "03 목소리", "무음 제거·캐릭터 목소리"),
         ("edit", "04 사진·편집", "빈 구간 채우기·자막·효과음"),
         ("done", "05 완성", "MP4·썸네일·편집 프로젝트")]

HOOK_LIMIT = {"short": 3.0, "long": 6.0}  # 첫 문장이 이보다 길면 이탈 위험


def collect(p: dict) -> dict[str, list[tuple[str, str]]]:
    """프로젝트 파일들에서 단계별 (항목, 값) 수치를 모은다."""
    rows: dict[str, list[tuple[str, str]]] = {k: [] for k, *_ in BOARD}
    dirs = [Path(d) for d in p.get("source_dirs", [])]
    if dirs:
        frames, rated = 0, 0
        for d in dirs:
            cat = d / "frames.json"
            items = load_json(cat) if cat.exists() else []
            frames += len(items)
            rated += sum(1 for c in items if c.get("description"))
        rows["download"].append(("영상 자료", f"{len(dirs)}개 · 사진 후보 {frames}장 (AI 평가 {rated}장)"))
    if p.get("script_path") and Path(p["script_path"]).exists():
        data = load_json(Path(p["script_path"]))
        chars = ", ".join(c["name"] for c in data.get("characters", [])) or "-"
        for fmt in p["formats"]:
            segs = data["long_form" if fmt == "long" else "short_form"]["segments"]
            rows["script"].append((f"{_label(fmt)} 대본", f"{len(segs)}컷 · 더빙 {sum(s['type'] == 'dub' for s in segs)} · "
                                                         f"원본 {sum(s['type'] == 'original' for s in segs)}"))
        rows["script"].append(("등장인물", chars))
    for fmt, tl in (p.get("timelines") or {}).items():
        st = load_json(Path(tl)).get("stats")
        if st:
            rows["tts"].append((f"{_label(fmt)} 목소리", f"{st['speech']}초 · 무음 제거 {st['silence_removed']}초"))
            hook_ok = st["first_line"] <= HOOK_LIMIT[fmt]
            rows["tts"].append((f"{_label(fmt)} 인트로", f"첫 문장 {st['first_line']}초 ({st['first_line_starts_at']}초에 시작)"
                                + ("" if hook_ok else "  ⚠ 길다")))
            if st.get("voice_warnings"):
                rows["tts"].append((f"{_label(fmt)} 목소리 검수", f"경고 {st['voice_warnings']}건 (timeline.json 의 qa 참고)  ⚠ 확인"))
            if len(st.get("voices", {})) > 1:
                rows["tts"].append(("캐릭터별 목소리", " / ".join(v for k, v in st["voices"].items() if k != "narrator")))
    for fmt, out in (p.get("outputs") or {}).items():
        rep = Path(out).parent / "report.json"
        if rep.exists():
            r = load_json(rep)
            rows["edit"].append((f"{_label(fmt)} 사진·자막", f"사진 {r['photos']}장(빈 구간 채움 {r['auto_filled']}) · "
                                                          f"자막 {r['subtitle_lines']}줄 · 효과음 {r['sfx']}개"))
            rows["done"].append((f"{_label(fmt)}", f"{r['duration']}초 · {Path(out).name}"))
    return rows


def show_board(p: dict, current: str | None = None) -> None:
    done = set(p.get("done", []))
    if p.get("outputs") and "edit" in done:
        done.add("done")
    rows = collect(p)
    t = Table(title=f"제작 진행 · {p['run_id']}", show_lines=False, expand=True)
    t.add_column("단계", no_wrap=True)
    t.add_column("상태", no_wrap=True)
    t.add_column("결과")
    for key, name, desc in BOARD:
        status = "[green]✔ 완료[/]" if key in done else ("[cyan]● 진행 중[/]" if key == current else "[dim]○ 대기[/]")
        detail = "\n".join(f"{a}: {b}" for a, b in rows[key]) or f"[dim]{desc}[/]"
        t.add_row(name, status, detail)
    console.print(t)


def show_result(p: dict) -> None:
    """마지막 '제작·전달 결과' 패널 + 검수 체크리스트."""
    rows = collect(p)
    lines = [f"[bold]{a}[/]  {b}" for key, *_ in BOARD for a, b in rows[key]]
    warns = [f"⚠ {a} — 첫 문장이 길어 이탈 위험. 대본의 hook 문장을 줄이세요." for a, b in rows["tts"]
             if "⚠ 길다" in b]
    warns += [f"⚠ {a} — {b.split('  ')[0]}" for a, b in rows["tts"] if a.endswith("목소리 검수")]
    for fmt, out in (p.get("outputs") or {}).items():
        folder = Path(out).parent
        lines.append(f"[bold]{_label(fmt)} 파일[/]  {out}\n    썸네일 {folder / 'thumbnail.jpg'}\n"
                     f"    업로드 문구 {folder / 'upload.txt'}\n    검수용 편집 프로젝트 {folder / 'edit_project'}")
    body = "\n".join(lines + ([""] + warns if warns else []))
    console.print(Panel(body, title="제작·전달 결과", border_style="green"))
    console.print("[dim]검수 팁: edit_project/timeline.fcpxml 을 DaVinci Resolve 로 열면 컷 단위로 바로 수정할 수 있습니다. "
                  "대본을 고쳤다면 `python main.py resume --run <ID> --from tts`.[/]")


def _label(fmt: str) -> str:
    return "롱폼" if fmt == "long" else "숏폼"
