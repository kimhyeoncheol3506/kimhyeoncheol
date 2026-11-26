# -*- coding: utf-8 -*-
"""KAMIS '도매가격(가락시장 경락가격)' 일별 표 수집 — 쿠키 세션 + 요청 간 3초 쉬기. 사용: python3 fetch_garak.py jobs.json → raw/*.html + garak.csv(누적)"""
import csv, html, json, os, re, subprocess, sys, time
H = os.path.dirname(os.path.abspath(__file__)); RAW = f"{H}/raw"; os.makedirs(RAW, exist_ok=True); CJ = f"{RAW}/cj"
UA = "Mozilla/5.0"; BASE = "https://www.kamis.or.kr/customer/price/market/period.do"
def get(url, out):
    for k in range(4):
        r = subprocess.run(["curl", "-s", "-L", "-c", CJ, "-b", CJ, "-m", "60", "-A", UA, "-e", "https://www.kamis.or.kr/customer/main/main.do", "-o", out, "-w", "%{http_code}", url], capture_output=True, text=True)
        if r.stdout == "200" and os.path.getsize(out) > 50000: return True
        time.sleep(8 * (k + 1))
    return False
def parse(p):
    s = open(p, encoding="utf-8", errors="replace").read(); rows = []
    for r in re.findall(r"<tr[^>]*>(.*?)</tr>", s, re.S):
        c = [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", x))).strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)]
        if len(c) == 6 and re.match(r"\d{4}\.\d\d\.\d\d", c[0]): rows.append(c)
    return rows
jobs = json.load(open(sys.argv[1], encoding="utf-8"))
out = f"{H}/garak.csv"; seen = set()
if os.path.exists(out): seen = {tuple(r) for r in csv.reader(open(out, encoding="utf-8"))}
w = csv.writer(open(out, "a", newline="", encoding="utf-8"))
for j in jobs:
    fn = f"{RAW}/{j['code']}_{j['start'].replace('.', '')}_{j['end'].replace('.', '')}.html"
    if not os.path.exists(fn) or os.path.getsize(fn) < 50000:
        ok = get(f"{BASE}?action=daily&startday={j['start']}&endday={j['end']}&marketcode=1&itemcode={j['code']}", fn); time.sleep(3)
        if not ok: print("실패", j); continue
    rows = parse(fn); n = 0
    for r in rows:
        if tuple(r) not in seen: w.writerow(r); seen.add(tuple(r)); n += 1
    print(j["code"], j.get("name", ""), j["start"], j["end"], len(rows), "행, 새", n, flush=True)
