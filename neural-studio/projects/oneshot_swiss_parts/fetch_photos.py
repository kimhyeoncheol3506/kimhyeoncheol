"""(이거 한편으로 끝) 스위스 편 — 위키미디어 공용 사진 받기 + 정리.
2026-11-13 작성 당시 위키미디어 API 가 429(요청 과다)로 계속 막혀 일부만 받았다. 다시 돌리면 못 받은 사진만 이어서 받는다.
- 받기: 파일마다 30초 간격, 429 면 90초부터 늘려 가며 재시도. 원본보다 작은 표준 썸네일 크기(330/500/960/1280/1920)만 요청한다.
- 정리: 긴 변 2400px 이하 jpg(3MB 미만)로 projects/media/oneshot_swiss/ 에 저장하고 manifest.yaml · photo_map.yaml 을 다시 쓴다.
- swiss_guard 는 얼굴 클로즈업이 아닌지 눈으로 확인한다(아니면 swiss_guard2 파일로 바꾼다).
- matterhorn(9장 마지막 장면), geneva_watch(3장 제네바 시계)는 후보 파일을 아직 못 정했다. 못 구하면 build 가 quote 장면으로 바꾼다.
사용: python3 projects/oneshot_swiss_parts/fetch_photos.py  → 그다음 build_oneshot_swiss.py · tools/series_lint.py · make_thumb.py"""
import json, os, re, sys, time, urllib.parse, urllib.request
import yaml
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DST = os.path.join(os.path.dirname(HERE), "media", "oneshot_swiss")
RAW = "/tmp/claude-0/sw/dl"   # 원본 임시 보관(저장소 밖)
UA = {"User-Agent": "EduDocResearchBot/1.0 (educational research; contact via commons)"}
PICKS = {  # 키워드 → 위키미디어 공용 파일 (모두 퍼블릭 도메인 · CC)
    "alps_valley": "File:1 lauterbrunnen valley 2012.jpg",
    "alps_village": "File:Village and Alps, Bernese Oberland, Switzerland-LCCN2001702412.jpg",
    "paradeplatz": "File:Zürich (CH), Paradeplatz -- 2011 -- 1381.jpg",
    "bundesbrief": "File:Bundesbrief2.jpg",
    "marignano": "File:Marignan-1515-francois1er.jpg",
    "congress_vienna": "File:Congres de vienne.png",
    "basel_rhine": "File:Der Rhein in Basel.jpg",
    "bundeshaus": "File:Bundeshaus in Bern 2022.jpg",
    "geneva_old": "File:Topographia Helvetiae, Rhaetiae et Valesiae 1654 (1127074).jpg",
    "swiss_guard": "File:St. Peter's Basilica Swiss Guard (48466693296).jpg",
    "swiss_guard2": "File:Pontifical Swiss Guard 2019.jpg",
    "roche_tower": "File:Basel, de Roche Turm Bau 1+2 IMG 1617 2022-05-15 14.19.jpg",
    "chaux_de_fonds": "File:Patrimoine urbain horloger 8.JPG",
    "watch_movement": "File:Stowa Antea ETA 2824 macro (3389998183).jpg",
    "landsgemeinde": "File:Landsgemeinde Glarus, 2009.jpg",
    "gotthard_pass": "File:Gotthardpass 2015-09-21 16.11.11.jpg",
    "geigy_factory": "File:ETH-BIB-Auhafen Muttenz, Schweizerhalle-LBS H1-016072.tif",
    "reislaeufer": "File:Reislaeufer Luzerner Schilling.jpg",
}
KO = {  # 설명란 '사진 출처'용 한글 제목 · 내용
    "alps_valley": ("라우터브루넨 골짜기 (베른 고원)", "Lauterbrunnen valley from Wengen, 2012"),
    "alps_village": ("베른 고원의 마을과 알프스 (포토크롬, 1890년대)", "Photochrom print: village and Alps, Bernese Oberland"),
    "paradeplatz": ("취리히 파라데플라츠", "Paradeplatz, Zurich (bank headquarters square)"),
    "bundesbrief": ("1291년 연방 헌장", "Swiss Federal Charter of 1291"),
    "marignano": ("프라고나르, 〈마리냐노의 프랑수아 1세〉(1836)", "Battle of Marignano, 1515, painted by A.-É. Fragonard (Versailles)"),
    "congress_vienna": ("이자베, 〈빈 회의〉", "The Congress of Vienna after Jean-Baptiste Isabey"),
    "basel_rhine": ("라인강의 바젤", "The Rhine in Basel"),
    "bundeshaus": ("베른 연방 의사당", "Federal Palace (Bundeshaus) in Bern"),
    "geneva_old": ("17세기의 제네바 (『토포그라피아 헬베티아에』, 1654)", "View of Geneva, Topographia Helvetiae (Merian/Zeiller), 1654"),
    "swiss_guard": ("바티칸 교황 근위대", "Pontifical Swiss Guard, St. Peter's Basilica"),
    "swiss_guard2": ("바티칸 교황 근위대", "Pontifical Swiss Guards"),
    "roche_tower": ("바젤의 로슈 타워", "Roche Tower buildings 1 and 2, Basel"),
    "chaux_de_fonds": ("라쇼드퐁의 시계 산업 도시 경관", "La Chaux-de-Fonds watchmaking urban heritage"),
    "watch_movement": ("스위스 ETA 2824 자동 무브먼트", "Macro of an ETA 2824 automatic watch movement"),
    "landsgemeinde": ("글라루스 란츠게마인데 (2009)", "Landsgemeinde in Glarus, 3 May 2009"),
    "gotthard_pass": ("고트하르트 고개와 호스피스", "Gotthard Pass: lake, hospice and post station"),
    "geigy_factory": ("라인강 변의 화학 공장 (1954)", "Auhafen Muttenz and Schweizerhalle, former Geigy factory, 1954"),
    "reislaeufer": ("알프스를 넘는 스위스 용병 (루체른 실링 연대기, 1513)", "Swiss mercenaries crossing the Alps, Luzerner Schilling"),
}


def get(url):
    for k in range(10):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90).read()
        except Exception as e:  # 429 등
            print("retry", k, e, url[:100], file=sys.stderr)
            time.sleep(90 + 30 * k)
    raise SystemExit("fail " + url)


def api(title, **kw):
    q = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {"action": "query", "format": "json", "titles": title, "prop": "imageinfo", **kw})
    return list(json.loads(get(q))["query"]["pages"].values())[0]["imageinfo"][0]


def fetch():
    os.makedirs(RAW, exist_ok=True)
    mp = os.path.join(RAW, "meta.json")
    meta = json.load(open(mp)) if os.path.exists(mp) else {}
    for key, title in PICKS.items():
        if key in meta:
            continue
        w = api(title, iiprop="size")["width"]
        sw = max([x for x in (330, 500, 960, 1280, 1920) if x < w] or [0])
        time.sleep(3)
        ii = api(title, iiprop="url|extmetadata", **({"iiurlwidth": sw} if sw else {}))
        m = ii.get("extmetadata", {})
        g = lambda k: re.sub(r"<[^>]+>", "", m.get(k, {}).get("value", "")).strip()
        url = ii.get("thumburl") or ii["url"]
        fn = key + (".png" if url.lower().endswith(".png") else ".jpg")
        open(os.path.join(RAW, fn), "wb").write(get(url))
        meta[key] = {"file": fn, "title": title, "artist": g("Artist"), "license": g("LicenseShortName"),
                     "date": g("DateTimeOriginal"), "desc": g("ImageDescription")[:200], "url": ii["descriptionurl"]}
        json.dump(meta, open(mp, "w"), ensure_ascii=False, indent=1)
        print(key, fn, meta[key]["license"], flush=True)
        time.sleep(30)
    return meta


def organize(meta):
    os.makedirs(DST, exist_ok=True)
    man, pm = [], {}
    for k, m in meta.items():
        im = Image.open(os.path.join(RAW, m["file"])).convert("RGB")
        if max(im.size) > 2400:
            im.thumbnail((2400, 2400))
        fn, q = k + ".jpg", 90
        while True:
            im.save(os.path.join(DST, fn), "JPEG", quality=q)
            if os.path.getsize(os.path.join(DST, fn)) < 3_000_000 or q < 60:
                break
            q -= 8
        t, subj = KO.get(k, (m["title"], m["desc"]))
        man.append({"file": fn, "title": t, "subject": subj, "date": re.sub(r"date QS.*", "", m["date"]).strip(),
                    "author": re.sub(r"\s+", " ", m["artist"]).strip() or "unknown", "license": m["license"], "url": m["url"]})
        pm[k] = fn
    yaml.safe_dump(man, open(os.path.join(DST, "manifest.yaml"), "w", encoding="utf-8"), allow_unicode=True, sort_keys=False, width=200)
    pm.pop("swiss_guard2", None)
    hdr = "# @키워드 → projects/media/oneshot_swiss/ 파일. 장면 내용과 정확히 맞는 퍼블릭 도메인·CC 사진만 (fetch_photos.py 가 씀).\n"
    open(os.path.join(HERE, "photo_map.yaml"), "w", encoding="utf-8").write(hdr + yaml.safe_dump(pm, allow_unicode=True, sort_keys=False))
    print(len(man), "장", sorted(pm))


if __name__ == "__main__":
    organize(fetch() if "--organize-only" not in sys.argv else json.load(open(os.path.join(RAW, "meta.json"))))
