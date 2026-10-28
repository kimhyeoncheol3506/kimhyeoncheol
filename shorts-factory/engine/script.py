"""[2단계] 15초 대본 생성 + 교정(말더듬/같은 말 반복/긴 멈춤 제거) + 타임코드."""
import re

from .hooks import render_template


# ── 교정기 ──────────────────────────────────────────────────────────
def clean_text(raw, rules):
    """교정 대본을 만든다. 반환: (교정문, 제거 로그 리스트)"""
    sc = rules["script"]
    log = []
    text = raw
    for mark in sc["pause_marks"]:
        if mark in text:
            log.append(f"긴 멈춤 제거: '{mark}'")
            text = text.replace(mark, " ")
    text = re.sub(r"\((?:멈춤|침묵)[^)]*\)", " ", text)

    tokens = text.split()
    fillers = set(sc["fillers"])
    out = []
    for i, tok in enumerate(tokens):
        bare = tok.strip(",.!?~")
        if bare in fillers:
            log.append(f"군말 제거: '{tok}'")
            continue
        # 말더듬: '가-가격', '이, 이거' 처럼 다음 단어의 앞부분을 먼저 뱉은 경우
        m = re.match(r"^(\w{1,2})-(\w+)", tok)
        if m and m.group(2).startswith(m.group(1)):
            log.append(f"말더듬 교정: '{tok}'")
            tok = tok[len(m.group(1)) + 1:]
            bare = tok.strip(",.!?~")
        nxt = tokens[i + 1].strip(",.!?~") if i + 1 < len(tokens) else ""
        if bare and len(bare) <= 2 and nxt != bare and nxt.startswith(bare):
            log.append(f"말더듬 제거: '{tok}'")
            continue
        out.append(tok)

    # 같은 말 반복(1~4단어 묶음) 접기
    changed = True
    while changed:
        changed = False
        for n in (4, 3, 2, 1):
            for i in range(len(out) - 2 * n + 1):
                a = [w.strip(",.!?~") for w in out[i:i + n]]
                b = [w.strip(",.!?~") for w in out[i + n:i + 2 * n]]
                if a == b:
                    log.append(f"반복 제거: '{' '.join(out[i + n:i + 2 * n])}'")
                    del out[i:i + n]  # 앞쪽을 지우고 문장부호가 붙은 뒤쪽을 남김
                    changed = True
                    break
            if changed:
                break
    cleaned = re.sub(r"\s+([,.!?])", r"\1", " ".join(out)).strip()
    cleaned = re.sub(r"([,.!?])\1+", r"\1", cleaned)
    return cleaned, log


# ── 대본 생성 ────────────────────────────────────────────────────────
def syllables(text):
    return len(re.sub(r"[\s,.!?~·]", "", text))


def _script_ctx(ctx, hook_text, rules):
    sc = rules["script"]
    c = dict(ctx, hook=hook_text)
    if "price" in ctx and "orig_price" in ctx:
        c["price_line"] = render_template(sc["price_line_with_orig"], c)
    elif "price" in ctx:
        c["price_line"] = render_template(sc["price_line_only"], c)
    else:
        c["price_line"] = sc["price_line_none"]
    c["summary"] = render_template(sc["summary"], c)
    c["cta_line"] = sc["cta_line"]
    return c


def build_script(ctx, hook_text, rules, raw_overrides=None):
    """구조별 대본 + 문장 단위 타임코드. raw_overrides={section: 원본 녹취} 이면 교정해서 사용."""
    sc = rules["script"]
    c = _script_ctx(ctx, hook_text, rules)
    rate, gap, lead = sc["syllables_per_sec"], sc["phrase_gap_sec"], sc["lead_in_sec"]
    sections, warnings, clean_log = [], [], []
    for st in rules["structure"]:
        sid = st["id"]
        conf = sc["sections"][sid]
        if raw_overrides and sid in raw_overrides:
            lines = [s for s in re.split(r"(?<=[!?.])\s+", raw_overrides[sid]) if s.strip()]
        else:
            lines = [render_template(l, c) for l in conf["lines"]]
        phrases = []
        for line in lines:
            cleaned, log = clean_text(line, rules)
            clean_log += [f"[{sid}] {x}" for x in log]
            if cleaned:
                phrases.append(cleaned)

        start, end = st["start"], st["end"]
        if sid == "hook":  # 후킹은 타이핑 타임라인이 시간을 정한다
            timed = [{"text": phrases[0], "start": start, "end": end - 0.05}]
        else:
            window = end - start - lead - gap  # 다음 구간과 사이 숨 포함
            nat = [syllables(p) / rate for p in phrases]
            total = sum(nat) + gap * (len(phrases) - 1)
            scale = (window - gap * (len(phrases) - 1)) / sum(nat)
            scale = max(0.75, min(1.3, scale))
            if total > window:
                warnings.append(f"[{st['label']}] 대본이 {total:.1f}초로 길어요 → 말 속도를 올려 맞춤")
            t = start + lead
            timed = []
            for p, d in zip(phrases, nat):
                d *= scale
                timed.append({"text": p, "start": round(t, 3),
                              "end": round(max(min(t + d, end - 0.2), t + 0.3), 3)})
                t += d + gap
        badges = [b for b in (render_template(x, c) for x in conf.get("badges", [])) if b]
        sections.append({"id": sid, "label": st["label"], "start": start, "end": end,
                         "phrases": timed, "badges": badges, "shots": conf.get("shots", []),
                         "push_in": conf.get("push_in")})
    return {"sections": sections, "warnings": warnings, "clean_log": clean_log}


def tc(sec):
    m, s = divmod(sec, 60)
    return f"{int(m):02d}:{s:05.2f}"


def script_markdown(script, hook):
    lines = ["# 15초 교정 대본", "", f"선택된 후킹: **{hook['text']}** ({hook['type_ko']}, {hook['score']}점)", "",
             "| 타임코드 | 구간 | 멘트(교정본) | 촬영 컷 |", "|---|---|---|---|"]
    for s in script["sections"]:
        for i, p in enumerate(s["phrases"]):
            shot = s["shots"][i] if i < len(s["shots"]) else ""
            lines.append(f"| {tc(p['start'])}–{tc(p['end'])} | {s['label'] if i == 0 else ''} | {p['text']} | {shot} |")
        for b in s.get("badges", []):
            lines.append(f"| {tc(s['start'])}–{tc(s['end'])} | | (화면 배지) {b} | {s['shots'][-1] if s['shots'] else ''} |")
    if script["clean_log"]:
        lines += ["", "## 교정 내역 (말더듬·반복·멈춤 제거)"] + [f"- {x}" for x in script["clean_log"]]
    else:
        lines += ["", "## 교정 내역", "- 제거할 말더듬/반복/멈춤 없음 (자동 생성 대본)"]
    if script["warnings"]:
        lines += ["", "## 주의"] + [f"- {w}" for w in script["warnings"]]
    return "\n".join(lines) + "\n"
