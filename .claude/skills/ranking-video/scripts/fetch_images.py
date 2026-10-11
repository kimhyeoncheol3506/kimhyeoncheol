# -*- coding: utf-8 -*-
"""Openverse에서 CC0·CC BY·퍼블릭도메인 이미지 수집 (ranking-video v1.2.0)

사용법: python3 -I fetch_images.py <출력폴더>  — 섹션별 검색어는 아래 Q를 주제에 맞게 고친다.
결과: <출력폴더>/meta.json(출처·라이선스·저작자) + {id}.jpg. CC BY 이미지는 설명란에 저작자 표시가 필요하다.
"""
import json, os, sys, urllib.parse, urllib.request, urllib.error
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
Q = {
 "인트로": ["fish market auction","sashimi platter","seafood market tanks","raw fish slicing","Noryangjin fish market","fish market seoul","sushi chef knife"],
 "10위 청양수산": ["fish auction","live fish tank","flatfish","fishmonger","white fish sashimi","fish market morning"],
 "9위 삼정튀김집": ["tempura","fried shrimp","deep frying","korean fried food","tempura shrimp"],
 "8위 전라상회": ["tuna sashimi","otoro","nigiri sushi","sushi omakase","tuna belly"],
 "7위 손선장": ["assorted sashimi","aged sashimi","sashimi korea","hoe korean raw fish","sashimi moriawase"],
 "6위 이레상회": ["korean raw fish","sashimi set","sashimi dinner","soy sauce wasabi sashimi","seafood dinner table"],
 "5위 진주식당": ["63 building seoul","han river seoul","yeouido night","seoul skyline han river","hoedeopbap"],
 "4위 해태기아": ["yellowtail sashimi","buri sashimi","amberjack","yellowtail fish","hamachi sashimi"],
 "3위 푸른바다": ["sashimi platter colorful","salmon sashimi","sashimi assortment","raw fish platter","sea bream sashimi"],
 "2위 형제상회": ["moriawase","sashimi plate","sashimi boat","assorted sashimi platter","sliced raw fish"],
 "1위 땅끝마을": ["yellowtail","bangeo","buri","sashimi thick slices","japanese amberjack sashimi"],
 "아웃트로": ["fish market seoul","seagull","seoul night","fish market","seafood market korea"],
}
def search(q):
    u = "https://api.openverse.org/v1/images/?" + urllib.parse.urlencode({"q": q, "license": "cc0,by,pdm", "page_size": 20, "mature": "false"})
    try:
        import time; time.sleep(1.2)
        return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 ranking-video"}), timeout=30))["results"]
    except Exception as e:
        print("ERR", q, e); return []
seen = set(); meta = []
for sec, qs in Q.items():
    got = 0
    for q in qs:
        for r in search(q):
            w, h = r.get("width") or 0, r.get("height") or 0
            if r["id"] in seen or w < 1000 or h == 0 or w / h < 1.2 or w / h > 2.1: continue
            seen.add(r["id"]); got += 1
            meta.append({"section": sec, "query": q, "id": r["id"], "url": r["url"], "license": r["license"], "license_version": r.get("license_version"),
                         "creator": r.get("creator"), "title": r.get("title"), "foreign": r.get("foreign_landing_url"), "source": r.get("source"), "w": w, "h": h})
            if got >= 18: break
        if got >= 18: break
    print(sec, got)
def thumb(u):
    if "upload.wikimedia.org/wikipedia/commons/" in u and "/thumb/" not in u:
        p = u.split("/wikipedia/commons/")[1]; name = p.split("/")[-1]
        return f"https://upload.wikimedia.org/wikipedia/commons/thumb/{p}/1920px-{name}"
    return u
def dl(m):
    import time
    fn = os.path.join(OUT, m["id"] + ".jpg")
    if os.path.exists(fn): return True
    u = f"https://api.openverse.org/v1/images/{m['id']}/thumb/?full_size=true&compressed=false"
    for k in range(3):
        try:
            time.sleep(1.5)
            data = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0 ranking-video"}), timeout=60).read()
            if len(data) > 20000: open(fn, "wb").write(data); return True
            return False
        except urllib.error.HTTPError as e:
            if e.code != 429: return False
            time.sleep(8 * (k + 1))
        except Exception: return False
    return False
ok = [dl(m) for m in meta]
meta = [m for m, o in zip(meta, ok) if o]
json.dump(meta, open(os.path.join(OUT, "meta.json"), "w"), ensure_ascii=False, indent=1)
print("downloaded", len(meta))
