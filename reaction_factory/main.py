"""해외반응 숏폼/롱폼 원클릭 생성기 — 진입점.

  python main.py                    # 대화형 '딸깍' 모드 (질문 몇 개 → 완성 영상)
  python main.py auto --yes         # 완전 자동: 주제 자동 선택 → 탐색 → 다운로드 → 대본 → 음성 → 편집
  python main.py topics             # 주제 100개 랭킹 보기
  python main.py discover -q "korean bbq reaction"
  python main.py make --video <유튜브 URL/ID>   # 특정 영상으로 바로 제작
  python main.py resume --run <RUN_ID> [--from tts]
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

from config import OUTPUT_DIR, settings
from utils import console, fmt_hms, human_count, load_json, save_json, slugify

STAGES = ["download", "script", "tts", "edit"]


# ════════════════════════════════════════════════════════════════
#  프로젝트(=한 번의 제작) 상태 파일: output/<run_id>/project.json
# ════════════════════════════════════════════════════════════════
def new_project(label: str, sources: list[str], topic: dict | None, formats: list[str], minutes: float,
                extra: str = "") -> dict:
    run_id = f"{datetime.now():%Y%m%d_%H%M%S}_{slugify(label, 30)}"
    project = {"run_id": run_id, "created": datetime.now().isoformat(timespec="seconds"),
               "sources": sources, "source_dirs": [], "topic": topic, "formats": formats,
               "target_minutes": minutes, "extra_instruction": extra, "done": [], "outputs": {}}
    save_project(project)
    console.print(f"[bold]제작 ID:[/] {run_id}  (이어하기: python main.py resume --run {run_id})")
    return project


def project_path(run_id: str) -> Path:
    return OUTPUT_DIR / run_id / "project.json"


def save_project(p: dict) -> None:
    save_json(project_path(p["run_id"]), p)


def run_pipeline(p: dict, start_from: str | None = None) -> dict:
    from downloader import download_source, import_local

    stages = STAGES[STAGES.index(start_from):] if start_from else [s for s in STAGES if s not in p["done"]]
    from dashboard import show_board, show_result

    for stage in stages:
        show_board(p, current=stage)
        if stage == "download":
            dirs = []
            for s in p["sources"]:
                folder = import_local(s) if Path(s).expanduser().exists() else download_source(s)
                dirs.append(str(folder))
            p["source_dirs"] = dirs
        elif stage == "script":
            from script_generator import generate_script

            _, path = generate_script([Path(d) for d in p["source_dirs"]], topic=p.get("topic"),
                                      target_minutes=p["target_minutes"], run_id=p["run_id"],
                                      extra_instruction=p.get("extra_instruction", ""))
            p["script_path"] = str(path)
            console.print(f"[green]✔ 대본[/] {path}  (사람용: {path.with_suffix('.md')})")
        elif stage == "tts":
            from script_generator import load_package
            from tts_engine import build_voice_track

            pkg = load_package(Path(p["script_path"]))
            chars = [c.model_dump() for c in pkg.characters]
            p["timelines"] = {}
            for fmt in p["formats"]:
                script = pkg.long_form if fmt == "long" else pkg.short_form
                _, tl = build_voice_track(script, p["run_id"], characters=chars)
                p["timelines"][fmt] = str(tl)
        elif stage == "edit":
            from editor import render
            from script_generator import load_package

            pkg = load_package(Path(p["script_path"]))
            for fmt in p["formats"]:
                script = pkg.long_form if fmt == "long" else pkg.short_form
                out = render(script, Path(p["timelines"][fmt]), [Path(d) for d in p["source_dirs"]], p["run_id"])
                p["outputs"][fmt] = str(out)
        if stage not in p["done"]:
            p["done"].append(stage)
        save_project(p)

    show_board(p)
    show_result(p)
    return p


# ════════════════════════════════════════════════════════════════
#  출력 도우미
# ════════════════════════════════════════════════════════════════
def show_topics(db, top: int = 20, category: str | None = None) -> None:
    t = Table(title=f"🔥 터지는 주제 랭킹 {'(' + db.categories[category] + ')' if category else 'TOP ' + str(top)}")
    for col in ("순위", "ID", "카테고리", "주제", "점수", "후킹 앵글"):
        t.add_column(col, overflow="fold")
    for x in db.top(top, category):
        t.add_row(str(x.rank), x.id, f"{x.category_name} #{x.category_rank}", x.title_ko, f"{x.trend_score:.0f}", x.hook_angle)
    console.print(t)


def show_candidates(cands, n: int = 15) -> None:
    t = Table(title="🎯 가성비 소스 랭킹 (구독자 대비 조회수 · 조회 속도 · 참여율)")
    for col in ("#", "점수", "제목", "채널", "구독자", "조회수", "배수", "시간당", "업로드", "길이", ""):
        t.add_column(col, overflow="fold")
    for i, c in enumerate(cands[:n], 1):
        t.add_row(str(i), f"{c.score:.0f}", c.title[:50], c.channel_title[:18], human_count(c.subscribers),
                  human_count(c.views), f"{c.views_per_sub:.1f}x", human_count(int(c.views_per_hour)),
                  f"{c.age_hours / 24:.1f}일 전", fmt_hms(c.duration_s), " ".join(c.flags))
    console.print(t)


def _discover_for_topic(topic, args):
    from downloader import discover

    queries = args.query or topic.search_queries
    cands, folder = discover(queries, days=args.days, max_subs=args.max_subs, min_views=args.min_views,
                             label=topic.title_ko if topic else None)
    console.print(f"[dim]랭킹/썸네일 저장: {folder}[/]")
    return cands


# ════════════════════════════════════════════════════════════════
#  명령들
# ════════════════════════════════════════════════════════════════
def cmd_topics(args) -> None:
    from topics import TopicDB

    db = TopicDB()
    if args.recalibrate:
        topic = db.get(args.recalibrate)
        if not topic:
            sys.exit(f"주제를 찾을 수 없습니다: {args.recalibrate}")
        cands = _discover_for_topic(topic, args)
        before = topic.trend_score
        after = db.recalibrate(topic, [asdict(c) for c in cands])
        db.save()
        console.print(f"'{topic.title_ko}' 점수 {before:.0f} → {after:.0f} (현재 {topic.rank}위)")
        return
    if args.category == "all":
        for key in db.categories:
            show_topics(db, 10, key)
    else:
        show_topics(db, args.top, args.category)
    if args.match:
        for t, s in db.match(args.match):
            console.print(f"  매칭: {t.id} {t.title_ko} (점수 {s:.0f})")


def cmd_discover(args) -> None:
    from topics import TopicDB

    topic = TopicDB().get(args.topic) if args.topic else None
    if not args.query and not topic:
        sys.exit("--query 또는 --topic 을 지정하세요.")
    show_candidates(_discover_for_topic(topic, args), args.show)


def cmd_make(args) -> None:
    """특정 영상(들)로 바로 제작."""
    from topics import TopicDB

    db = TopicDB()
    topic = db.get(args.topic) if args.topic else None
    label = (topic.title_ko if topic else args.video[0].split("=")[-1].split("/")[-1])
    p = new_project(label, args.video, topic.__dict__ if topic else None, _formats(args), args.minutes, args.extra)
    run_pipeline(p)


def cmd_auto(args) -> None:
    """완전 자동: 주제 → 탐색 → 상위 N개 소스 → 제작."""
    from topics import TopicDB

    db = TopicDB()
    topic = db.get(args.topic) if args.topic and args.topic != "auto" else db.auto_pick(use_trends=not args.no_trends)
    console.print(f"[bold]주제:[/] {topic.id} {topic.title_ko}  ([italic]{topic.hook_angle}[/])")
    cands = _discover_for_topic(topic, args)
    if not cands:
        sys.exit("조건에 맞는 영상이 없습니다. --days / --max-subs / --min-views 를 완화해 보세요.")
    show_candidates(cands, 10)
    db.recalibrate(topic, [asdict(c) for c in cands])
    db.save()

    picked = [c for c in cands if not c.is_short or args.allow_shorts][: args.sources] or cands[: args.sources]
    if not args.yes and not Confirm.ask(f"상위 {len(picked)}개 소스로 제작할까요?", default=True):
        return
    p = new_project(topic.title_ko, [c.video_id for c in picked], topic.__dict__, _formats(args), args.minutes, args.extra)
    run_pipeline(p)


def cmd_resume(args) -> None:
    p = load_json(project_path(args.run))
    run_pipeline(p, start_from=args.from_stage)


def cmd_interactive(_args) -> None:
    """질문에 답만 하면 되는 '딸깍' 모드."""
    from topics import TopicDB

    console.rule("[bold cyan]해외반응 영상 자동 생성기")
    if not settings.anthropic_api_key:
        console.print("[red].env 에 ANTHROPIC_API_KEY 가 없습니다. README 의 '빠른 시작'을 먼저 해 주세요.[/]")
        return
    db = TopicDB()
    show_topics(db, 20)
    choice = Prompt.ask("주제 선택 (순위/ID/검색어, 엔터=자동)", default="auto")
    if choice == "auto":
        topic = db.auto_pick()
    else:
        topic = db.get(choice)
        if not topic:
            hits = db.match(choice)
            topic = hits[0][0] if hits else db.auto_pick()
    console.print(f"[bold]→ {topic.title_ko}[/]")

    opts = argparse.Namespace(
        query=None, min_views=3_000,
        days=IntPrompt.ask("최근 며칠 이내 영상?", default=7),
        max_subs=IntPrompt.ask("구독자 상한", default=50_000),
    )
    cands = _discover_for_topic(topic, opts)
    if not cands:
        console.print("[red]조건에 맞는 영상이 없습니다. 기간을 늘리거나 구독자 상한을 올려 보세요.[/]")
        return
    show_candidates(cands, 15)
    sel = Prompt.ask("사용할 영상 번호 (쉼표로 여러 개, 엔터=1)", default="1")
    picked = [cands[int(i) - 1] for i in sel.split(",") if i.strip().isdigit() and 0 < int(i) <= len(cands)]
    fmt = Prompt.ask("만들 형식", choices=["both", "long", "short"], default="both")
    minutes = float(Prompt.ask("롱폼 목표 길이(분)", default="8")) if fmt != "short" else 1
    formats = ["long", "short"] if fmt == "both" else [fmt]
    p = new_project(topic.title_ko, [c.video_id for c in picked], topic.__dict__, formats, minutes)
    run_pipeline(p)


def _formats(args) -> list[str]:
    return ["long", "short"] if args.format == "both" else [args.format]


# ════════════════════════════════════════════════════════════════
def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="해외반응 숏폼/롱폼 원클릭 생성기")
    sub = ap.add_subparsers(dest="cmd")

    def discover_opts(p):
        p.add_argument("-q", "--query", action="append", help="검색어 (여러 번 지정 가능)")
        p.add_argument("--days", type=int, default=7, help="최근 N일 이내 업로드 (기본 7)")
        p.add_argument("--max-subs", type=int, default=50_000, help="구독자 상한 (기본 5만)")
        p.add_argument("--min-views", type=int, default=3_000, help="최소 조회수 (기본 3천)")

    def make_opts(p):
        p.add_argument("--format", choices=["both", "long", "short"], default="both")
        p.add_argument("--minutes", type=float, default=8, help="롱폼 목표 길이(분)")
        p.add_argument("--extra", default="", help="대본에 추가로 요청할 내용")

    p = sub.add_parser("topics", help="주제 100개 랭킹")
    p.add_argument("--top", type=int, default=20)
    p.add_argument("--category", default=None, help="k_food, kpop … 또는 all")
    p.add_argument("--match", help="이 문장과 맞는 주제 찾기")
    p.add_argument("--recalibrate", metavar="TOPIC", help="실제 검색 결과로 이 주제 점수 재계산")
    discover_opts(p)
    p.set_defaults(func=cmd_topics)

    p = sub.add_parser("discover", help="소스 영상 탐색·랭킹")
    p.add_argument("--topic", help="주제 ID/순위 (검색어 자동)")
    p.add_argument("--show", type=int, default=20)
    discover_opts(p)
    p.set_defaults(func=cmd_discover)

    p = sub.add_parser("make", help="지정 영상으로 제작")
    p.add_argument("--video", action="append", required=True, help="유튜브 URL/ID 또는 로컬 mp4 (여러 개 가능)")
    p.add_argument("--topic", help="연결할 주제 ID")
    make_opts(p)
    p.set_defaults(func=cmd_make)

    p = sub.add_parser("auto", help="완전 자동 제작")
    p.add_argument("--topic", default="auto", help="주제 ID/순위, 기본 auto")
    p.add_argument("--sources", type=int, default=1, help="롱폼에 엮을 원본 개수")
    p.add_argument("--allow-shorts", action="store_true", help="원본으로 쇼츠 영상도 허용")
    p.add_argument("--no-trends", action="store_true", help="구글 트렌드 매칭 끄기")
    p.add_argument("--yes", action="store_true", help="확인 질문 없이 진행")
    discover_opts(p)
    make_opts(p)
    p.set_defaults(func=cmd_auto)

    p = sub.add_parser("resume", help="중단된 제작 이어서")
    p.add_argument("--run", required=True, help="output/ 아래 폴더명(run_id)")
    p.add_argument("--from", dest="from_stage", choices=STAGES, help="이 단계부터 다시")
    p.set_defaults(func=cmd_resume)
    return ap


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    try:
        (args.func if args.cmd else cmd_interactive)(args)
    except KeyboardInterrupt:
        console.print("\n[yellow]중단됨. `python main.py resume --run <RUN_ID>` 로 이어서 할 수 있습니다.[/]")
    except RuntimeError as exc:
        console.print(f"\n[red]오류:[/] {exc}")
        console.print("[dim]문제를 고친 뒤 `python main.py resume --run <RUN_ID>` 로 끊긴 단계부터 이어서 할 수 있습니다.[/]")
        sys.exit(1)


if __name__ == "__main__":
    main()
