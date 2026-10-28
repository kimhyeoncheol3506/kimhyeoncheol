"""[5단계] 시청 이탈 방지 구조 검증 체크리스트 (매 실행 후 자동 점검)."""
from . import ff


def run_checklist(tl, rules, hook, final_mp4=None, stems=None):
    ck, ed = rules["checklist"], rules["editing"]
    items = []

    def add(name, ok, detail):
        items.append({"name": name, "ok": bool(ok), "detail": detail})

    # 1. 첫 3초 자막 노출
    hook_subs = [s for s in tl["subtitles"] if s["start"] < 3.0]
    first = min((s["start"] for s in tl["subtitles"]), default=99)
    covered = sum(min(s["end"], 3.0) - max(s["start"], 0) for s in hook_subs)
    add("첫 3초 자막 노출", first <= ck["first_sub_max_sec"] and covered >= 3.0 - first - 0.05,
        f"첫 자막 {first:.2f}초에 등장, 0~3초 중 {covered:.2f}초 노출")

    # 2. 컷 길이 평균 1.5초 이하
    lens = [c["end"] - c["start"] for c in tl["cuts"]]
    avg = sum(lens) / len(lens)
    add("컷 길이 평균 ≤ %.1f초" % ck["avg_cut_max_sec"], avg <= ck["avg_cut_max_sec"],
        f"컷 {len(lens)}개, 평균 {avg:.2f}초, 최장 {max(lens):.2f}초")

    # 3. 효과음 타이밍 오차 0.1초 이내 (렌더된 효과음 스템에서 실측)
    tol = ck["sfx_tolerance_sec"]
    if stems:
        onsets = ff.detect_onsets(stems[0])
        errs = [min((abs(o - s["t"]) for o in onsets), default=99) for s in tl["sfx"]]
        worst = max(errs) if errs else 0
        add(f"효과음 타이밍 오차 ≤ {tol}초 (실측)", worst <= tol,
            f"효과음 {len(errs)}개, 최대 오차 {worst * 1000:.0f}ms, 평균 {sum(errs) / max(1, len(errs)) * 1000:.0f}ms")
    else:
        anchors = {c["start"] for c in tl["cuts"]} | {e["t"] for e in tl["zoom_events"]} | \
                  {s["start"] for s in tl["subtitles"] if s["kind"] == "typing"}
        worst = max((min(abs(a - s["t"]) for a in anchors) for s in tl["sfx"]), default=0)
        add(f"효과음 타이밍 오차 ≤ {tol}초 (계획값)", worst <= tol, f"최대 오차 {worst * 1000:.0f}ms")

    # ── 추가 점검 ──
    add("후킹 15자 이내", len(hook["text"]) <= 15, f"'{hook['text']}' = {len(hook['text'])}자")
    long_lines = [s["text"] for s in tl["subtitles"] if len(s["text"]) > ed["subtitle"]["max_chars"]]
    add("자막 한 줄 %d자 이내" % ed["subtitle"]["max_chars"], not long_lines,
        "모두 통과" if not long_lines else "초과: " + ", ".join(long_lines))
    zs = [e["zoom"] for e in tl["zoom_events"]]
    add("강조 줌 1.1~1.2배", all(1.1 - 1e-9 <= z <= 1.2 + 1e-9 for z in zs),
        f"강조 {len(zs)}회: " + ", ".join(f"{z:.2f}x" for z in zs))
    if stems:
        peak = ff.peak_between(stems[1], 0, tl["bgm"]["start_sec"] - 0.02)
        add("0~3초 BGM 없음 (실측)", peak < 0.001, f"0~{tl['bgm']['start_sec']}초 BGM 최대 레벨 {peak:.4f}")
    add("CTA 하단 버튼 13~15초", abs(tl["cta"]["start_sec"] - 13.0) < 0.01 and tl["cta"]["end"] >= 14.99,
        f"{tl['cta']['start_sec']}~{tl['cta']['end']}초 '{tl['cta']['button_text']}'")
    add("마지막 1초 로고+구매 버튼", tl["cuts"][-1]["section"] == "outro",
        f"{tl['outro']['start']}~{tl['outro']['end']}초")
    if final_mp4:
        d = ff.probe_duration(final_mp4)
        add("최종 길이 15초", abs(d - tl["video"]["duration"]) <= ck["duration_tolerance_sec"], f"{d:.3f}초")
    return items


def checklist_markdown(items):
    ok = sum(i["ok"] for i in items)
    lines = [f"# 시청 이탈 방지 체크리스트 — {ok}/{len(items)} 통과", "", "| 결과 | 항목 | 측정값 |", "|---|---|---|"]
    lines += [f"| {'✅' if i['ok'] else '❌'} | {i['name']} | {i['detail']} |" for i in items]
    return "\n".join(lines) + "\n"
