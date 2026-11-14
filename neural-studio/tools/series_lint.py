"""대본 yaml 빠른 점검 (렌더·더빙 없이 몇 초) — '이거 한편으로 끝' 시리즈용 (2026-11-13).
make_editorial.py 의 검수 규칙 중 대본만으로 알 수 있는 것을 미리 확인한다.
사용: python3 tools/series_lint.py projects/<slug>.yaml
점검: 장면 종류 · 같은 종류 3연속 · 판 길이 추정(18초 상한, 5.2음절/초) · 숫자 장면 source · 출처 facts 에 없는 숫자 ·
      verified 안 된 출처 · 첫 20초 질문 · 챕터 수 · 총 길이 추정 · sync.at 낱말이 대사에 있는지 · 사진 파일 존재"""
import os
import re
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from facetube.textnorm import to_speech  # noqa: E402

KINDS = set("year chapter doc person quote bars waffle line gauge bignum stairs flip pie photo timeline stack end clip".split())
NUMERIC = {"bars", "waffle", "line", "gauge", "bignum", "stairs"}
RATE = 4.55   # 2026-11-14 실측(스위스 15:07·일본 18:02): 숫자를 읽는 소리로 바꾼 음절 기준 4.5~4.6음절/초, 판마다 약 1.05초 여유


def strip(s):
    return re.sub(r"\{\{.*?\}\}", "", re.sub(r"\[\[|\]\]", "", str(s)))


def strings(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in ("kind", "theme", "cam", "photo", "photo_bg", "color", "fx", "video"):
                continue
            yield from strings(v)
    elif isinstance(o, list):
        for v in o:
            yield from strings(v)
    elif o is not None:
        yield str(o)


def main(path):
    p = yaml.safe_load(open(path, encoding="utf-8"))
    root = os.path.dirname(os.path.dirname(os.path.abspath(path)))
    sc = p["scenes"]
    facts = " ".join(f for s in p.get("sources", []) for f in s.get("facts", [])).replace(",", "")
    allow = {str(x) for x in p.get("numbers_ok", [])}
    errs, warn, unk = [], [], {}
    total, run, prev = 0.0, 0, None
    chapters = 0
    for i, s in enumerate(sc, 1):
        say = s.get("say", "")
        k = (s.get("scene") or {}).get("kind")
        if k not in KINDS:
            errs.append(f"장면{i}: 알 수 없는 kind {k}")
        run = run + 1 if k == prev else 1
        prev = k
        if run >= 3:
            warn.append(f"장면{i}: '{k}' {run}연속")
        syl = len(re.findall(r"[가-힣]", to_speech(strip(say))))
        d = syl / RATE + 1.05 + float(s.get("hold", 0))
        total += d
        if d > 18 and k != "end":
            errs.append(f"장면{i}: 약 {d:.0f}초 (18초 상한) — 나누기")
        if s.get("chapter"):
            chapters += 1
        if k in NUMERIC and not s.get("source"):
            errs.append(f"장면{i}: 숫자 장면에 source 없음")
        for w in (s.get("sync") or {}).get("at", [])[1:]:
            if isinstance(w, str) and " " in w.strip():
                errs.append(f"장면{i}: sync 낱말 '{w}' 에 띄어쓰기 — 낱말 하나만 (make_editorial 이 멈춤)")
            elif isinstance(w, str) and w not in strip(say):
                errs.append(f"장면{i}: sync 낱말 '{w}' 이 대사에 없음")
        for f in ("photo", "photo_bg"):
            v = (s.get("scene") or {}).get(f)
            if isinstance(v, str) and not v.startswith("@") and not os.path.exists(os.path.join(root, v.lstrip("/"))):
                errs.append(f"장면{i}: 사진 파일 없음 {v}")
        for text in [say, *strings(s.get("scene") or {})]:
            for n in re.findall(r"\d[\d,]*(?:\.\d+)?", strip(text)):
                n = n.replace(",", "")
                if n not in facts and n not in allow:
                    unk.setdefault(n, i)
    if not 10 <= total / 60 <= 14.5:
        errs.append(f"예상 길이 {total / 60:.1f}분 — 본편은 10~15분(실제 오차 감안해 14.5분 이하로) [채널규칙 2026-11-13]")
    first = " ".join(s.get("say", "") for s in sc[:4])
    if "?" not in first:
        errs.append("첫 장면들(약 20초)에 질문(?) 없음")
    nv = [s.get("id") for s in p.get("sources", []) if not s.get("verified")]
    if nv:
        errs.append(f"verified 안 된 출처: {nv}")
    if unk:
        errs.append("facts/numbers_ok 에 없는 숫자: " + ", ".join(f"{n}(장면{i})" for n, i in sorted(unk.items(), key=lambda x: x[1])))
    print(f"장면 {len(sc)} · 챕터 {chapters} · 예상 길이 {total / 60:.1f}분 · 출처 {len(p.get('sources', []))}개")
    for e in errs:
        print("❌", e)
    for w in warn:
        print("⚠", w)
    print("통과" if not errs else f"고칠 것 {len(errs)}개")
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
