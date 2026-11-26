# -*- coding: utf-8 -*-
"""Wikimedia Commons에서 CC BY/CC BY-SA/CC0/PD 사진 찾기 → <out>/<id>.jpg + meta.json (출처·라이선스·작가). 사용: python3 -I commons.py out q.json"""
import json, os, sys, time, urllib.parse, urllib.request, re, html
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True); Q = json.load(open(sys.argv[2], encoding="utf-8"))
UA = {"User-Agent": "garak-video-research/1.0 (educational; contact via project)"}
API = "https://commons.wikimedia.org/w/api.php?"
def get(params):
    for k in range(3):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(API + urllib.parse.urlencode(params), headers=UA), timeout=40))
        except Exception as e:
            time.sleep(5 * (k + 1))
    return {}
meta = json.load(open(f"{OUT}/meta.json")) if os.path.exists(f"{OUT}/meta.json") else []
have = {m["id"] for m in meta}
for sec, qs in Q.items():
    got = sum(1 for m in meta if m["section"] == sec)
    for q in qs:
        if got >= 4: break
        r = get(dict(action="query", format="json", generator="search", gsrsearch=f"{q} filetype:bitmap", gsrnamespace=6, gsrlimit=12, prop="imageinfo", iiprop="url|extmetadata|size", iiurlwidth=1600))
        for p in (r.get("query", {}).get("pages", {}) or {}).values():
            ii = (p.get("imageinfo") or [{}])[0]; em = ii.get("extmetadata", {}); lic = em.get("LicenseShortName", {}).get("value", "")
            if not re.search(r"CC BY|CC0|Public domain|CC-BY", lic, re.I) or re.search(r"NC|ND", lic): continue
            w, h = ii.get("width", 0), ii.get("height", 0)
            if w < 1000 or not h or not (1.2 <= w / h <= 2.1): continue
            pid = f"wc{p['pageid']}"
            if pid in have: continue
            try:
                data = urllib.request.urlopen(urllib.request.Request(ii["thumburl"], headers=UA), timeout=60).read()
            except Exception: continue
            open(f"{OUT}/{pid}.jpg", "wb").write(data); have.add(pid)
            artist = re.sub(r"<[^>]+>", "", html.unescape(em.get("Artist", {}).get("value", "unknown"))).strip()
            meta.append(dict(section=sec, query=q, id=pid, title=p["title"].replace("File:", ""), license=lic, license_version="", creator=artist[:80], foreign=ii.get("descriptionurl", ""), w=w, h=h, source="wikimedia commons"))
            got += 1; time.sleep(1.5)
            if got >= 4: break
        time.sleep(2)
    print(sec, got, flush=True)
json.dump(meta, open(f"{OUT}/meta.json", "w"), ensure_ascii=False, indent=1)
