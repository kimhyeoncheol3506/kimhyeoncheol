# -*- coding: utf-8 -*-
"""노량진수산 '오늘의 경락시세' 수집 + 주간 비교 (ranking-video v2.4.0, 주간 시세 리포트 시리즈용)

출처: 노량진수산주식회사 수산물가격정보 > 오늘의 경락시세 (https://www.susansijang.co.kr/nsis/miw/ko/info/miw3110)
  - 날짜별 경매 결과: 어종, 산지, 규격, 포장, 수량, 낙찰고가, 낙찰저가, 평균가 (도매 경락가. 소매가가 아님)

사용법:
  python3 -I noryangjin_prices.py fetch <출력폴더> <시작일 YYYY-MM-DD> <끝일 YYYY-MM-DD>
      → <출력폴더>/경락_YYYYMMDD.csv (날짜별, 이미 있으면 건너뜀)
  python3 -I noryangjin_prices.py items <출력폴더> <이번주 끝일> [--min-qty 100]   ← 기본(권장): 품목+상태 단위, kg 경매, 수량 가중 중앙값
      → <출력폴더>/주간품목비교_<끝일>.csv / .md
  python3 -I noryangjin_prices.py week <출력폴더> <이번주 끝일 YYYY-MM-DD> [--min-qty 20]
      → 이번 주(끝일 포함 7일)와 지난주(그 전 7일)를 비교한 <출력폴더>/주간비교_<끝일>.csv / .md
비교 기준: 같은 '품목(어종) + 규격 + 포장 단위'끼리 수량 가중 평균가. 양쪽 주에 모두 거래가 있고 이번 주 수량이 --min-qty 이상인 것만.
"""
import csv, datetime as dt, html, os, re, subprocess, sys, time
from collections import defaultdict

URL = "https://www.susansijang.co.kr/nsis/miw/ko/info/miw3110"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0 Safari/537.36"
COLS = ["어종", "산지", "규격", "포장", "수량", "낙찰고가", "낙찰저가", "평균가"]


def post(data, jar):
    args = ["curl", "-sS", "-m", "30", "-A", UA, "-c", jar, "-b", jar, "-X", "POST", URL]
    for k, v in data.items(): args += ["--data-urlencode", f"{k}={v}"]
    for k in range(4):
        r = subprocess.run(args, capture_output=True, text=True, errors="ignore")
        if r.returncode == 0 and "<table" in r.stdout: return r.stdout
        time.sleep(3 * (k + 1))
    raise RuntimeError("경락시세 페이지를 받지 못함")


def rows_of(h):
    out = []
    for r in re.findall(r"(?s)<tr[^>]*>(.*?)</tr>", h):
        cells = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in re.findall(r"(?s)<td[^>]*>(.*?)</td>", r)]
        if len(cells) == 8: out.append(cells)
    return out


def fetch_day(day, out):
    f = os.path.join(out, f"경락_{day:%Y%m%d}.csv")
    if os.path.exists(f): return f
    jar = os.path.join(out, ".cookie"); subprocess.run(["curl", "-sS", "-m", "30", "-A", UA, "-c", jar, URL, "-o", os.devnull])
    allrows, page, seen = [], 1, set()
    while True:
        h = post({"pageIndex": page, "pageUnit": 10, "pageSize": 10, "kdfshNm": "", "searchDe": f"{day:%Y.%m.%d}"}, jar)
        rows = [r for r in rows_of(h) if "조회된" not in r[0]]
        key = tuple(map(tuple, rows))
        if not rows or key in seen: break
        seen.add(key); allrows += rows; page += 1
        if not re.search(rf"fnList\({page}\)", h): break
        time.sleep(0.6)
    with open(f, "w", encoding="utf-8", newline="") as fp:
        w = csv.writer(fp); w.writerow(["날짜"] + COLS)
        for r in allrows: w.writerow([f"{day:%Y-%m-%d}"] + r)
    print(f"{day:%Y-%m-%d} {len(allrows)}건 ({page - 1}쪽)", flush=True)
    return f


def num(s):
    s = s.replace(",", "").strip()
    try: return float(s)
    except ValueError: return 0.0


def load(out, start, end):
    rows, d = [], start
    while d <= end:
        f = os.path.join(out, f"경락_{d:%Y%m%d}.csv")
        if os.path.exists(f):
            with open(f, encoding="utf-8") as fp: rows += list(csv.DictReader(fp))
        d += dt.timedelta(days=1)
    return rows


def item_name(s):  # '(활)넙치' → 품목 '넙치', 상태 '활'
    m = re.match(r"\((.)\)(.*)", s)
    return (m.group(2).strip(), m.group(1)) if m else (s.strip(), "")


def agg(rows):
    g = defaultdict(lambda: [0.0, 0.0, set(), set()])  # 수량, 금액, 산지, 날짜
    for r in rows:
        nm, st = item_name(r["어종"]); q = num(r["수량"]); p = num(r["평균가"])
        if q <= 0 or p <= 0: continue
        k = (nm, st, r["규격"], r["포장"]); g[k][0] += q; g[k][1] += q * p; g[k][2].add(r["산지"]); g[k][3].add(r["날짜"])
    return {k: dict(qty=v[0], avg=v[1] / v[0], origins=sorted(v[2]), days=len(v[3])) for k, v in g.items()}


def week(out, end, min_qty=20):
    this = agg(load(out, end - dt.timedelta(days=6), end)); last = agg(load(out, end - dt.timedelta(days=13), end - dt.timedelta(days=7)))
    res = []
    for k, a in this.items():
        if k in last and a["qty"] >= min_qty:
            b = last[k]; ch = (a["avg"] - b["avg"]) / b["avg"] * 100
            res.append(dict(품목=k[0], 상태=k[1], 규격=k[2], 포장=k[3], 이번주평균=round(a["avg"]), 지난주평균=round(b["avg"]), 변동률=round(ch, 1),
                            이번주수량=round(a["qty"], 1), 지난주수량=round(b["qty"], 1), 거래일수=a["days"], 산지="/".join(a["origins"][:4])))
    res.sort(key=lambda r: r["변동률"])
    base = os.path.join(out, f"주간비교_{end:%Y%m%d}")
    with open(base + ".csv", "w", encoding="utf-8", newline="") as fp:
        w = csv.DictWriter(fp, fieldnames=list(res[0].keys()) if res else ["품목"]); w.writeheader(); w.writerows(res)
    L = [f"# 노량진 주간 경락시세 비교 — {end - dt.timedelta(days=6):%m/%d}~{end:%m/%d} vs {end - dt.timedelta(days=13):%m/%d}~{end - dt.timedelta(days=7):%m/%d}",
         "", f"출처: 노량진수산주식회사 오늘의 경락시세(도매 경락가, 수량 가중 평균). 비교 품목 {len(res)}개(이번 주 수량 {min_qty} 이상, 두 주 모두 거래).", "",
         "| 품목 | 상태 | 규격 | 포장 | 이번 주 | 지난주 | 변동 | 이번 주 수량 | 산지 |", "|---|---|---|---|---|---|---|---|---|"]
    for r in res:
        L.append(f"| {r['품목']} | {r['상태']} | {r['규격']} | {r['포장']} | {r['이번주평균']:,} | {r['지난주평균']:,} | {r['변동률']:+.1f}% | {r['이번주수량']:,} | {r['산지']} |")
    open(base + ".md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"비교 {len(res)}품목 → {base}.csv/.md")
    for r in res[:8]: print(f"  ↓ {r['품목']}({r['상태']}) {r['규격']} {r['포장']}: {r['지난주평균']:,} → {r['이번주평균']:,} ({r['변동률']:+.1f}%) 수량 {r['이번주수량']}")
    for r in res[-5:][::-1]: print(f"  ↑ {r['품목']}({r['상태']}) {r['규격']} {r['포장']}: {r['지난주평균']:,} → {r['이번주평균']:,} ({r['변동률']:+.1f}%) 수량 {r['이번주수량']}")
    return res


def wmedian(pairs):
    pairs = sorted(pairs); tot = sum(q for _, q in pairs); acc = 0
    for p, q in pairs:
        acc += q
        if acc >= tot / 2: return p
    return pairs[-1][0]


def agg_item(rows):
    """v2.4.0 기본 비교: 품목+상태 단위, kg 포장만, 수량 가중 '중앙값'(큰 물량과 작은 고가 물량이 섞여도 덜 흔들림)"""
    g = defaultdict(lambda: dict(pq=[], days=set(), origins=set()))
    for r in rows:
        if r["포장"].strip().lower() != "kg": continue
        nm, st = item_name(r["어종"]); q = num(r["수량"]); p = num(r["평균가"])
        if q <= 0 or p <= 0: continue
        x = g[(nm, st)]; x["pq"].append((p, q)); x["days"].add(r["날짜"]); x["origins"].add(r["산지"])
    return {k: dict(med=wmedian(v["pq"]), qty=sum(q for _, q in v["pq"]), days=len(v["days"]), origins=sorted(v["origins"]),
                    lo=min(p for p, _ in v["pq"]), hi=max(p for p, _ in v["pq"])) for k, v in g.items()}


def week_item(out, end, min_qty=100, min_days=3):
    this = agg_item(load(out, end - dt.timedelta(days=6), end)); last = agg_item(load(out, end - dt.timedelta(days=13), end - dt.timedelta(days=7)))
    res = []
    for k, a in this.items():
        b = last.get(k)
        if not b or a["qty"] < min_qty or b["qty"] < min_qty / 2 or a["days"] < min_days or b["days"] < min_days: continue
        ch = (a["med"] - b["med"]) / b["med"] * 100
        res.append(dict(품목=k[0], 상태=k[1], 이번주중앙값=round(a["med"]), 지난주중앙값=round(b["med"]), 변동률=round(ch, 1), 이번주수량=round(a["qty"]),
                        지난주수량=round(b["qty"]), 이번주거래일=a["days"], 지난주거래일=b["days"], 이번주범위=f"{a['lo']:,.0f}~{a['hi']:,.0f}", 산지="/".join(a["origins"][:5])))
    res.sort(key=lambda r: r["변동률"])
    base = os.path.join(out, f"주간품목비교_{end:%Y%m%d}")
    with open(base + ".csv", "w", encoding="utf-8", newline="") as fp:
        w = csv.DictWriter(fp, fieldnames=list(res[0].keys())); w.writeheader(); w.writerows(res)
    L = [f"# 노량진 주간 경락시세 — 품목별 비교 {end - dt.timedelta(days=6):%m/%d}~{end:%m/%d} vs 앞 7일", "",
         f"출처: 노량진수산주식회사 오늘의 경락시세(도매). kg 단위 경매만, 수량 가중 중앙값. 조건: 이번 주 {min_qty}kg↑·두 주 모두 {min_days}일↑ 거래. {len(res)}품목.", "",
         "| 품목 | 상태 | 이번 주(원/kg) | 지난주 | 변동 | 이번 주 수량(kg) | 거래일 | 이번 주 범위 | 산지 |", "|---|---|---|---|---|---|---|---|---|"]
    for r in res: L.append(f"| {r['품목']} | {r['상태']} | {r['이번주중앙값']:,} | {r['지난주중앙값']:,} | {r['변동률']:+.1f}% | {r['이번주수량']:,} | {r['이번주거래일']} | {r['이번주범위']} | {r['산지']} |")
    open(base + ".md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"품목 비교 {len(res)}개 → {base}.csv/.md")
    for r in res[:10]: print(f"  ↓ {r['품목']}({r['상태']}) {r['지난주중앙값']:,} → {r['이번주중앙값']:,} ({r['변동률']:+.1f}%) {r['이번주수량']:,}kg {r['이번주거래일']}일 [{r['이번주범위']}] {r['산지']}")
    for r in res[-6:][::-1]: print(f"  ↑ {r['품목']}({r['상태']}) {r['지난주중앙값']:,} → {r['이번주중앙값']:,} ({r['변동률']:+.1f}%) {r['이번주수량']:,}kg {r['이번주거래일']}일 [{r['이번주범위']}] {r['산지']}")
    return res


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "fetch":
        out = a[1]; os.makedirs(out, exist_ok=True)
        d, e = dt.date.fromisoformat(a[2]), dt.date.fromisoformat(a[3])
        while d <= e: fetch_day(d, out); d += dt.timedelta(days=1)
    elif a[0] == "items":  # 기본(권장): 품목 단위 비교
        mq = int(a[a.index("--min-qty") + 1]) if "--min-qty" in a else 100
        week_item(a[1], dt.date.fromisoformat(a[2]), mq)
    elif a[0] == "week":
        mq = int(a[a.index("--min-qty") + 1]) if "--min-qty" in a else 20
        week(a[1], dt.date.fromisoformat(a[2]), mq)
