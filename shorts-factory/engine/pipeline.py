"""[4단계] 실행 파이프라인:
제품 입력 → 후킹 생성/선택 → 대본 → 타임라인 → ffmpeg 렌더링 → 체크리스트 → 완료 알림"""
import datetime
import json
import re
import urllib.request
from pathlib import Path

from . import ff
from .checklist import checklist_markdown, run_checklist
from .hooks import build_context, generate_hooks
from .render import render, render_stems
from .rules import ROOT, load_rules
from .script import build_script, script_markdown, tc
from .timeline import build_timeline, collect_media, to_toml

OUTPUT = ROOT / "output"


def hooks_markdown(hooks, picked):
    lines = ["# 후킹 문장 15개 + 클릭률 예측 순위", "",
             "| 순위 | 점수 | 유형 | 후킹 문장 (15자 이내) | 글자수 | 점수 근거 |", "|---|---|---|---|---|---|"]
    for h in hooks:
        mark = " ⭐선택" if h is picked else ""
        lines.append(f"| {h['rank']}{mark} | {h['score']} | {h['type_ko']} | {h['text']} | {len(h['text'])} | "
                     f"{', '.join(h['reasons'])} |")
    return "\n".join(lines) + "\n"


def typing_markdown(tl):
    lines = ["", "## 후킹 타이핑 타임라인", "", "| 등장 | 사라짐 | 새 단어 | 화면 자막 |", "|---|---|---|---|"]
    for s in tl["subtitles"]:
        if s["kind"] == "typing":
            lines.append(f"| {s['start']:.2f}s | {s['end']:.2f}s | {s['new_word']} | {s['text']} |")
    return "\n".join(lines) + "\n"


def timeline_markdown(tl):
    L = ["# 편집 타임라인 명세", "", f"규칙 파일: `{tl['meta']['rules_file']}`", "",
         "## 컷 전환", "", "| 컷 | 시작 | 끝 | 길이 | 구간 | 촬영 가이드 | 줌 |", "|---|---|---|---|---|---|---|"]
    for c in tl["cuts"]:
        z = c["zoom"]
        punch = ", ".join(f"+{p['t']:.2f}s→{p['scale']}x" for p in z["punches"])
        L.append(f"| {c['id']} | {tc(c['start'])} | {tc(c['end'])} | {c['end'] - c['start']:.2f}s | {c['section']} | "
                 f"{c['shot']} | {z['from']}→{z['to']}{' / 강조 ' + punch if punch else ''} |")
    L += ["", "## 자막", "", "| 시작 | 끝 | 자막 | 강조 키워드 |", "|---|---|---|---|"]
    for s in tl["subtitles"]:
        L.append(f"| {tc(s['start'])} | {tc(s['end'])} | {s['text']} | {', '.join(dict.fromkeys(s['highlights']))} |")
    L += ["", "## 효과음", "", "| 시점 | 종류 | 파일 | 기준 |", "|---|---|---|---|"]
    for s in tl["sfx"]:
        L.append(f"| {tc(s['t'])} | {s['type']} | `{s['file']}` | {s['anchor']} |")
    b = tl["bgm"]
    L += ["", "## BGM / CTA / 아웃트로", "",
          f"- BGM `{b['file']}`: {b['start_sec']}초부터 {b['fade_in_sec']}초 페이드인 (0~{b['start_sec']}초 무음), 볼륨 {b['volume']}",
          f"- CTA 버튼 '{tl['cta']['button_text']}': {tl['cta']['start_sec']}~{tl['cta']['end']}초, 화면 하단 고정",
          f"- 아웃트로: {tl['outro']['start']}~{tl['outro']['end']}초 로고 + 구매 버튼"]
    return "\n".join(L) + "\n"


def _align_voice(script, voice_path, rules, log):
    segs = ff.speech_segments(voice_path, min_gap=rules["editing"]["cut"]["min_gap_sec"])
    phrases = [p for s in script["sections"] for p in s["phrases"]]
    info = {"file": str(voice_path), "segments": segs, "gap_cuts": [a for a, _ in segs[1:]]}
    if len(segs) == len(phrases):
        for p, (a, b) in zip(phrases, segs):
            p["start"], p["end"] = a, b
        log(f"  · 내레이션 {len(segs)}개 말 구간을 대본 문장에 1:1 정렬")
    else:
        log(f"  · 내레이션 말 구간 {len(segs)}개 ≠ 대본 문장 {len(phrases)}개 → 자막은 예상 타이밍, 컷은 실제 공백 기준")
    return info


def notify(rules, msg, log):
    n = rules.get("notify", {})
    log(("\a" if n.get("bell") else "") + msg)
    if n.get("webhook_url"):
        try:
            req = urllib.request.Request(n["webhook_url"], data=json.dumps({"text": msg}).encode(),
                                         headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=10)
        except Exception as e:  # 알림 실패가 영상 제작을 막지는 않는다
            log(f"  (웹훅 알림 실패: {e})")


def run_pipeline(inp, log=print, choose=None):
    """inp: product, target, benefits, price, orig_price, brand, short, media, voice, hook, render"""
    rules = load_rules()  # 매 실행마다 rules.yaml 을 새로 읽는다
    slug = re.sub(r"[^\w가-힣]+", "_", inp["product"]).strip("_")[:30]
    run_dir = OUTPUT / f"{datetime.datetime.now():%Y%m%d-%H%M%S}_{slug}"
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "input.json").write_text(json.dumps(inp, ensure_ascii=False, indent=2), encoding="utf-8")

    log(f"\n▶ 1/6 후킹 생성 — {inp['product']} / {inp['target']} / {', '.join(inp['benefits'])}")
    ctx = build_context(inp["product"], inp["target"], inp["benefits"], rules, inp.get("price"),
                        inp.get("orig_price"), inp.get("brand"), inp.get("short"))
    hooks = generate_hooks(ctx, rules)
    sel = inp.get("hook", "auto")
    if choose and sel == "auto":
        sel = choose(hooks)
    picked = hooks[int(sel) - 1] if str(sel).isdigit() else hooks[0]
    for h in hooks[:5]:
        log(f"   {h['rank']:>2}. [{h['score']}] {h['type_ko']:<7} {h['text']}")
    log(f"   → 선택: '{picked['text']}' ({picked['type_ko']}, {picked['score']}점)")

    log("▶ 2/6 15초 대본 생성 + 교정")
    raw = inp.get("raw_script")
    script = build_script(ctx, picked["text"], rules, raw_overrides=raw)
    voice = None
    if inp.get("voice"):
        voice = _align_voice(script, Path(inp["voice"]).resolve(), rules, log)

    log("▶ 3/6 편집 타임라인 생성 (rules.yaml 적용)")
    tl = build_timeline(ctx, picked, script, rules, collect_media(inp.get("media")), voice)
    tl["meta"]["hook_rank"] = picked["rank"]
    tl["meta"]["hook_type_id"] = picked["type"]

    (run_dir / "hooks.json").write_text(json.dumps(hooks, ensure_ascii=False, indent=2), encoding="utf-8")
    (run_dir / "a_hooks.md").write_text(hooks_markdown(hooks, picked) + typing_markdown(tl), encoding="utf-8")
    (run_dir / "b_script.md").write_text(script_markdown(script, picked), encoding="utf-8")
    (run_dir / "c_timeline.md").write_text(timeline_markdown(tl), encoding="utf-8")
    (run_dir / "timeline.json").write_text(json.dumps(tl, ensure_ascii=False, indent=2), encoding="utf-8")
    (run_dir / "timeline.toml").write_text(to_toml(tl), encoding="utf-8")

    final, stems = None, None
    font_file, font_name = ff.find_font(rules)
    if inp.get("render", True):
        log("▶ 4/6 ffmpeg 렌더링")
        ff.ensure_default_assets(rules, log)
        log(f"  · 자막 폰트: {font_name}")
        final = render(tl, rules, run_dir, font_file, font_name,
                       Path(inp["voice"]).resolve() if inp.get("voice") else None, log)
        stems = render_stems(tl, rules, run_dir)
    else:
        from .render import build_ass, build_command
        import shlex
        (run_dir / "subs.ass").write_text(build_ass(tl, rules, font_name), encoding="utf-8")
        args = build_command(tl, rules, run_dir, font_file)
        (run_dir / "render.sh").write_text(" \\\n  ".join(shlex.quote(a) for a in args) + "\n", encoding="utf-8")
        log("▶ 4/6 렌더링 건너뜀 (render.sh 만 생성)")

    log("▶ 5/6 시청 이탈 방지 체크리스트")
    items = run_checklist(tl, rules, picked, final, stems)
    (run_dir / "checklist.md").write_text(checklist_markdown(items), encoding="utf-8")
    for i in items:
        log(f"   {'✅' if i['ok'] else '❌'} {i['name']} — {i['detail']}")

    (OUTPUT / "last_run.json").write_text(json.dumps(
        {"input": inp, "run_dir": str(run_dir), "hook": picked}, ensure_ascii=False, indent=2), encoding="utf-8")
    passed = sum(i["ok"] for i in items)
    notify(rules, f"▶ 6/6 완료! {passed}/{len(items)} 체크 통과\n   결과 폴더: {run_dir}"
                  + (f"\n   영상: {final}" if final else ""), log)
    return {"run_dir": run_dir, "final": final, "hooks": hooks, "picked": picked, "checklist": items}
