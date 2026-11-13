"""(이거 한편으로 끝) 스위스 편 — 머리말(head.yaml) + 장 조각(ch1_3, ch4_6, ch7_9) + 그림 매핑(photo_map.yaml)을 합쳐 projects/oneshot_swiss.yaml 을 만든다.
@키워드 그림 자리표시는 photo_map.yaml(키워드 → projects/media/oneshot_swiss/파일)로 바꾼다. 못 찾은 그림은 지운다(photo 장면은 quote 로 바꾼다).
사용: python3 projects/oneshot_swiss_parts/build_oneshot_swiss.py"""
import os, sys, yaml
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "oneshot_swiss.yaml")
head = yaml.safe_load(open(os.path.join(HERE, "head.yaml"), encoding="utf-8"))
pm_path = os.path.join(HERE, "photo_map.yaml")
pmap = yaml.safe_load(open(pm_path, encoding="utf-8")) if os.path.exists(pm_path) else {}
media = "projects/media/oneshot_swiss/"
scenes, sources, missing, used = list(head.pop("intro")), list(head["sources"]), set(), set()
outro = head.pop("outro")
for part in ("ch1_3", "ch4_6", "ch7_9"):
    d = yaml.safe_load(open(os.path.join(HERE, part + ".yaml"), encoding="utf-8"))
    sources += d.get("sources", [])
    scenes += d["scenes"]
scenes += outro
for s in scenes:
    sc = s["scene"]
    for k in ("photo", "photo_bg"):
        v = sc.get(k)
        if isinstance(v, str) and v.startswith("@"):
            f = pmap.get(v[1:])
            if f:
                sc[k] = "/" + media + f; used.add(f)   # 장면 페이지(/editorial/scene.html) 기준 상대경로가 아니라 웹 루트 기준
            else:
                missing.add(v); sc.pop(k)
                if sc.get("kind") == "photo":  # 그림이 없으면 같은 글을 인용 카드로
                    s["scene"] = {"kind": "quote", "text": sc.get("name", ""), "by": sc.get("role", "")}
                    s.pop("theme", None)
head["sources"] = sources
# 그림 출처는 설명란 '사진 출처 및 이용 조건'에 들어간다
man_path = os.path.join(os.path.dirname(HERE), "media", "oneshot_swiss", "manifest.yaml")
if os.path.exists(man_path):
    man = yaml.safe_load(open(man_path, encoding="utf-8")) or []
    head["photos"] = [{"title": m.get("title", ""), "author": m.get("author", "unknown"), "license": m.get("license", ""), "url": m.get("url", "")}
                      for m in man if m.get("file") in used]
head["scenes"] = scenes
yaml.safe_dump(head, open(OUT, "w", encoding="utf-8"), allow_unicode=True, sort_keys=False, width=200)
import re
syl = sum(len(re.findall(r"[가-힣]", s["say"])) for s in scenes)
print(f"장면 {len(scenes)} · 한글 {syl}자 · 예상 {syl/4.9/60:.0f}분 · 그림 {len(used)}장 · 못 찾은 그림 {sorted(missing)}")
