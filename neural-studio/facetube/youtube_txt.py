"""유튜브 올리기 세트(youtube.txt) — 최종 영상과 항상 함께 만든다(현철님 2026-11-04).

한 파일에 그대로 복사해 붙일 수 있게: ① 제목 ② 설명란(요약·챕터·관련 사이트·깃허브) ③ 해시태그 ④ 출처.
대본 yaml 에서 쓰는 칸:
  title, title_alt(후보 제목 목록, 선택), summary, intro_chapter, disclaimer, tags,
  links:  [{name, url}]   관련 사이트(공식 사이트·다운로드 등). 없으면 sources 의 주소를 쓴다.
  github: [{name, url}]   깃허브 주소. 없으면 칸을 만들지 않는다(없는 주소를 지어내지 않는다).
  sources: [{outlet, title, date, url, verified}]   출처.
  references: [{name, url}]  참고한 영상(내용·팁을 배운 유튜브 영상). 출처 아래에 함께 적는다.
유튜브 제한: 제목 100자, 설명란 5000자, 해시태그 15개(넘으면 전부 무시됨), 챕터는 00:00 시작·3개 이상·각 10초 이상.
"""
import datetime

LINE = "━━━━━━━━━━━━━━━━━━━━"


def _chapters_ok(ch):
    return len(ch) >= 3 and ch[0][0] == 0 and all(b - a >= 10 for (a, _), (b, _) in zip(ch, ch[1:]))


def build(proj, chapters=(), extra_sections=()):
    """chapters: [(초, 이름)] — 첫 항목이 0초가 아니면 intro_chapter 를 앞에 붙인다. 반환: (본문, 경고 목록)"""
    warn = []
    ch = list(chapters)
    if ch and ch[0][0] > 0.5:
        ch.insert(0, (0.0, proj.get("intro_chapter", "들어가며")))
    ch = [(0.0 if i == 0 else a, b) for i, (a, b) in enumerate(ch)]
    title = proj["title"].strip()
    if len(title) > 100:
        warn.append(f"제목 {len(title)}자 (유튜브 상한 100자)")
    tags = [t if t.startswith("#") else "#" + t for t in proj.get("tags", [])]
    if len(tags) > 15:
        warn.append(f"해시태그 {len(tags)}개 → 15개만 남김(16개 이상이면 유튜브가 전부 무시)")
        tags = tags[:15]
    links = proj.get("links") or [{"name": s.get("outlet", ""), "url": s["url"]} for s in proj.get("sources", []) if s.get("url")]
    gh = proj.get("github") or []

    D = [proj.get("summary", "").strip(), ""]
    if ch:
        if not _chapters_ok(ch):
            warn.append("챕터 조건(00:00 시작·3개 이상·각 10초 이상)을 못 맞춤 → 유튜브에서 챕터가 안 생길 수 있음")
        D += ["⏱ 챕터"] + [f"{int(a // 60):02d}:{int(a % 60):02d} {b}" for a, b in ch] + [""]
    if links:
        D += ["🔗 관련 사이트"] + [f"· {l['name']} : {l['url']}" for l in links] + [""]
    if gh:
        D += ["💻 깃허브"] + [f"· {g['name']} : {g['url']}" for g in gh] + [""]
    for head, rows in extra_sections:
        D += [head] + list(rows) + [""]
    if proj.get("disclaimer"):
        D += [proj["disclaimer"].strip(), ""]
    srcs = proj.get("sources", [])
    if srcs:
        D.append("📚 출처" if all(s.get("verified") for s in srcs) else "📚 출처 (⚠ 원문 미확인 포함)")
        D += [f"· {s.get('outlet', '')}, 「{s.get('title', '')}」 ({s.get('date', '')}) {s.get('url', '')}".rstrip() for s in srcs] + [""]
    refs = proj.get("references") or []
    if refs:
        D += ["🎬 참고한 영상"] + [f"· {r['name']} {r['url']}" for r in refs] + [""]
    D.append(" ".join(tags))
    desc = "\n".join(D).strip()
    if len(desc) > 5000:
        warn.append(f"설명란 {len(desc)}자 (유튜브 상한 5000자)")

    T = [f"[제목]", title]
    for alt in proj.get("title_alt") or []:
        T.append(f"  (후보) {alt}")
    T += ["", LINE, "[설명란] ↓ 아래부터 그대로 복사", LINE, desc, LINE, "",
          "[해시태그] (앞의 3개가 제목 위에 보임)", " ".join(tags), ""]
    if srcs:
        T += ["[출처]"] + [f"· {s.get('outlet', '')}, 「{s.get('title', '')}」 ({s.get('date', '')}) {s.get('url', '')}"
                          + ("" if s.get("verified") else "  ⚠ 원문 미확인") for s in srcs] + [""]
    if refs:
        T += ["[참고한 영상]"] + [f"· {r['name']} {r['url']}" for r in refs] + [""]
    T.append(f"(자동 생성 {datetime.date.today()} · 제목 {len(title)}자 · 설명란 {len(desc)}자 · 해시태그 {len(tags)}개)")
    return "\n".join(T) + "\n", warn


def write(out_dir, proj, chapters=(), extra_sections=(), log=print):
    txt, warn = build(proj, chapters, extra_sections)
    (out_dir / "youtube.txt").write_text(txt, encoding="utf-8")
    for w in warn:
        log(f"  ⚠ youtube.txt: {w}")
    return warn
