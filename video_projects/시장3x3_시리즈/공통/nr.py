# -*- coding: utf-8 -*-
"""노량진수산(주) 경락시세 일별 수집본(주간시세_리포트/data/경락_YYYYMMDD.csv) 집계 도우미.
열: 날짜,어종,산지,규격,포장,수량,낙찰고가,낙찰저가,평균가 — 평균가는 포장 단위(kg면 kg당) 값.
wavg: 수량 가중 평균(같은 포장 단위끼리만)."""
import csv, glob, os
D = "/home/user/kimhyeoncheol/video_projects/주간시세_리포트/data"


def rows(fish, start, end, pack=None):
    """fish: 어종 칸 정확히 일치(예: '(활)방어') 또는 목록. start/end: 'YYYYMMDD' 포함 범위."""
    fs = {fish} if isinstance(fish, str) else set(fish); out = []
    for p in sorted(glob.glob(f"{D}/경락_*.csv")):
        d = os.path.basename(p)[3:11]
        if not (start <= d <= end): continue
        for r in csv.DictReader(open(p, encoding="utf-8")):
            if r["어종"] in fs and (pack is None or r["포장"] == pack):
                try: r["q"] = float(r["수량"].replace(",", "")); r["avg"] = float(r["평균가"].replace(",", "")); r["d"] = d
                except ValueError: continue
                if r["q"] > 0 and r["avg"] > 0: out.append(r)
    return out


def wavg(rs):
    q = sum(r["q"] for r in rs); return (round(sum(r["q"] * r["avg"] for r in rs) / q) if q else None), q


def days(rs): return sorted({r["d"] for r in rs})


def by(rs, key):
    g = {}
    for r in rs: g.setdefault(key(r), []).append(r)
    return g


def daily(rs): return {d: wavg(v)[0] for d, v in sorted(by(rs, lambda r: r["d"]).items())}
