#!/usr/bin/env python3
"""사이트(Pavo AI, Digen AI 등)에서 만들어 와야 할 소재 요청서를 만든다.

  python tools/list_media_requests.py projects/<이름>.yaml

프로젝트 YAML 의 장면(롱폼 scenes / 쇼츠 beats) 중 media 가 있는 것을 읽어,
  - 파일이 아직 없으면 '만들어 올 것'
  - 있으면 '확인됨'
으로 표시하고, media.request 에 적힌 프롬프트·비율·길이·도구를 표로 정리해 projects/<이름>_media_requests.md 로 저장한다.
YAML 예)
  media:
    path: media/<이름>/b3.mp4            # 파일을 넣을 자리(프로젝트 파일 기준 상대 경로)
    ai: true
    tool: Pavo AI                         # style.yaml external_tools 에 있는 이름
    model: Agnes Video 2.5 Flash
    generated_on: "2026-10-25"            # 만든 날(만든 뒤에 적기)
    request: {prompt: "...", seconds: 5, aspect: "9:16", note: "..."}
"""
import os
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
RULES = [
    "화면 속 글자·로고·워터마크를 넣어 달라고 하지 않는다(AI 글자는 깨진다. 글자는 우리가 얹는다)",
    "실존 인물·유명 캐릭터·상표를 닮게 만들지 않는다(초상권·상표 문제)",
    "소리는 쓰지 않는다(내레이션이 주인공). 소리 없는 옵션이 있으면 끈다",
    "한 컷에 한 동작, 4~8초. 짧아도 우리가 반복 재생하지만 같은 동작이 어색하게 끊기지 않게",
    "만든 뒤 파일 이름은 요청서의 '저장 위치' 그대로, 그리고 YAML 의 generated_on 을 채운다",
    "사이트의 AI 표시(워터마크)는 가리거나 지우지 않는다. 우리 영상에도 'AI 생성' 배지가 자동으로 붙는다",
]


def items(proj):
    for i, b in enumerate(proj.get("beats") or []):
        if b.get("media"):
            yield f"쇼츠 장면{i} ({b.get('role', '')})", b["media"], (b.get("say") or ""), "9:16 세로(또는 1:1)"
    for i, sc in enumerate(proj.get("scenes") or []):
        if sc.get("media"):
            say = sc.get("say") or ""
            say = " ".join(say) if isinstance(say, list) else say
            yield f"롱폼 장면{i} ({sc.get('type', '')})", sc["media"], say, "16:9 가로"


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    ypath = Path(sys.argv[1]).resolve()
    proj = yaml.safe_load(open(ypath, encoding="utf-8"))
    reg = yaml.safe_load(open(ROOT / "style.yaml", encoding="utf-8")).get("external_tools", {})
    base = ypath.parent
    rows, todo = [], 0
    for label, md, say, default_aspect in items(proj):
        p = Path(md.get("path", ""))
        full = p if p.is_absolute() else (base / p)
        have = full.exists()
        todo += 0 if have else 1
        req = md.get("request") or {}
        tk = str(md.get("tool", "")).lower()
        info = next((v for k, v in reg.items() if k in tk or v["name"].lower() in tk), None)
        rows.append((label, md, say, req, have, full, info, default_aspect))
    out = [f"# 소재 요청서: {proj.get('title') or ypath.stem}", "",
           f"- 프로젝트: `{ypath.name}`  ·  필요한 소재 {len(rows)}개 중 **아직 없는 것 {todo}개**", "",
           "## 만들 때 지킬 것", *[f"- {r}" for r in RULES], ""]
    for label, md, say, req, have, full, info, asp in rows:
        out += [f"## {label}  {'✅ 파일 있음' if have else '⬜ 만들어 올 것'}",
                f"- 저장 위치: `{full.relative_to(ROOT) if str(full).startswith(str(ROOT)) else full}`",
                f"- 이 장면 대사: {say.strip() or '(없음)'}",
                f"- 사이트/모델: {md.get('tool', '(미정)')} / {md.get('model', '(미정)')}"
                + (f"  — 약관 확인 {info['terms_checked']}" if info and info.get("terms_checked") else "  — ⚠ 약관(상업 이용) 미확인" if info else "  — ⚠ 등록 안 된 도구"),
                f"- 비율/길이: {req.get('aspect', asp)} / {req.get('seconds', '5')}초",
                f"- 프롬프트: {req.get('prompt', '(미작성 — media.request.prompt 에 적어 주세요)')}"]
        if req.get("note"):
            out.append(f"- 메모: {req['note']}")
        if info and info.get("label"):
            out.append(f"- 이 도구의 표시 규정: {info['label']}")
        out.append("")
    dst = ypath.with_name(ypath.stem + "_media_requests.md")
    dst.write_text("\n".join(out), encoding="utf-8")
    print("\n".join(out))
    print(f"\n저장: {dst}")
    return 0 if todo == 0 else 3


if __name__ == "__main__":
    sys.exit(main())
