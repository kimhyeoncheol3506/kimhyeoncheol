"""가상 시연 데이터 생성기. 모든 종목코드·금액·계정은 가상이다(실제 회사 데이터 미사용).

python -m finclose.sample_data [출력폴더]
"""
from __future__ import annotations

import csv
import random
import sys
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from openpyxl import Workbook

from .periods import month_end, prev_month_end

N_BONDS = 24


def _bonds() -> list[dict]:
    rnd = random.Random(42)
    out = []
    for i in range(1, N_BONDS + 1):
        usd = i % 8 == 0
        out.append({
            "code": f"KR9TEST{i:05d}",
            "name": (f"가상외화채 {i:02d}" if usd else f"가상{['국고채', '통안채', '은행채', '회사채'][i % 4]} {i:02d}"),
            "currency": "USD" if usd else "KRW",
            "face": Decimal(rnd.choice([1, 2, 3, 5, 10, 20]) * (1_000_000 if usd else 1_000_000_000)),
            "price0": Decimal(rnd.randint(9800, 10250)) + Decimal(rnd.randint(0, 99)) / 100,
            # 편입/소멸 월(2025-01=0): 21~22번은 2026-06 편입, 23~24번은 2026-09 신규, 3번은 2026-06 이후·11번은 2026-08 이후 소멸
            "start": 0 if i <= 20 else (17 if i <= 22 else 20),
            "end": {3: 17, 11: 19}.get(i, 999),
        })
    return out


def _month_index(d: date) -> int:
    return (d.year - 2025) * 12 + d.month - 1  # 2025-01 = 0


def price_at(b: dict, d: date) -> Decimal:
    rnd = random.Random(f"{b['code']}-{d.isoformat()}")
    drift = Decimal(rnd.randint(-60, 60)) / 100 * (_month_index(d) % 5 + 1)
    return (b["price0"] + drift).quantize(Decimal("0.01"))


def eval_amount(face: Decimal, price: Decimal, ccy: str) -> Decimal:
    q = Decimal(1) if ccy == "KRW" else Decimal("0.01")
    return (face * price / 10000).quantize(q, rounding=ROUND_HALF_UP)


def holdings_at(d: date) -> list[dict]:
    mi = _month_index(d)
    out = []
    for b in _bonds():
        if b["start"] <= mi <= b["end"]:
            face = b["face"]
            if b["code"] == "KR9TEST00005" and mi >= 20:   # 2026-09 수량 증가(매수)
                face = face * 2
            out.append({**b, "face": face})
    return out


def _write_xlsx(path: Path, title: str, base: date, header: list[str], rows: list[list], unit: str = "원") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = title
    ws.append([title])
    ws.append([f"기준일: {base.isoformat()}", None, None, f"(단위: {unit})"])
    ws.append([])
    ws.append(header)
    for r in rows:
        ws.append(r)
    wb.save(path)


def write_bond_set(out: Path, d: date, *, errors: bool = False, suffix: str = "") -> dict[str, Path]:
    out.mkdir(parents=True, exist_ok=True)
    pd_ = prev_month_end(d)
    hold = holdings_at(d)
    prev_hold = {h["code"]: h for h in holdings_at(pd_)}
    h_rows, p_rows, c_rows = [], [], []
    for h in hold:
        p_now = price_at(h, d)
        book = eval_amount(h["face"], (h["price0"] - Decimal("15")).quantize(Decimal("0.01")), h["currency"])
        prev_eval = None
        if h["code"] in prev_hold:
            ph = prev_hold[h["code"]]
            prev_eval = eval_amount(ph["face"], price_at(ph, pd_), ph["currency"])
        h_rows.append([h["code"], h["name"], h["face"], book, prev_eval, h["currency"], d])
        p_rows.append([h["code"], "가상평가(주)", d, p_now, h["currency"]])
    for code, ph in prev_hold.items():
        pp = price_at(ph, pd_)
        c_rows.append([code, pp, eval_amount(ph["face"], pp, ph["currency"]), ph["currency"], pd_])
    if errors:
        h_rows.append(list(h_rows[1]))                                   # 중복 종목
        h_rows.append(["KR9TEST99901", "가상미매칭채 01", Decimal("5000000000"), Decimal("5000000000"), None, "KRW", d])  # 단가 없음
        h_rows[4][2] = -h_rows[4][2]                                     # 음수 수량
        h_rows[6][5] = "KRWW"                                            # 잘못된 통화
        h_rows[7][6] = date(d.year, d.month, d.day - 1)                  # 잘못된 기준일
        p_rows[8][3] = None                                              # 단가 누락
        p_rows[9][3] = (p_rows[9][3] / 100).quantize(Decimal("0.0001"))  # 단가 단위 오류(100원당)
        p_rows.append(["KR9TEST99902", "가상평가(주)", d, Decimal("10010.00"), "KRW"])  # 보유하지 않은 단가
    tag = d.strftime("%Y%m%d") + suffix
    paths = {
        "holdings": out / f"보유채권내역_{tag}.xlsx",
        "prices": out / f"외부평가단가_{tag}.xlsx",
        "prior": out / f"전월평가결과_{pd_.strftime('%Y%m%d')}{suffix}.xlsx",
    }
    _write_xlsx(paths["holdings"], "보유채권", d, ["종목코드", "종목명", "보유수량", "장부금액", "전월 평가금액", "통화", "평가기준일"], h_rows)
    _write_xlsx(paths["prices"], "평가단가", d, ["종목코드", "평가기관", "평가기준일", "평가단가", "통화"], p_rows)
    _write_xlsx(paths["prior"], "전월결과", pd_, ["종목코드", "전월 평가단가", "전월 평가금액", "통화", "평가기준일"], c_rows)
    return paths


def write_renamed_holdings(out: Path, d: date) -> Path:
    """형식 변경 시나리오: 시트명·컬럼명 변경 + 컬럼 추가."""
    hold = holdings_at(d)
    rows = [[h["code"], h["name"], h["face"], eval_amount(h["face"], h["price0"] - 15, h["currency"]), None, h["currency"], d, "Y"]
            for h in hold]
    p = out / f"보유채권내역_{d.strftime('%Y%m%d')}_v2.xlsx"
    _write_xlsx(p, "Holdings", d, ["ISIN코드", "종목명", "보유액면", "장부가액", "전월평가액", "통화", "기준일자", "담보제공여부"], rows)
    return p


def write_thousand_unit_holdings(out: Path, d: date) -> Path:
    """금액 단위 오류 시나리오: 장부금액이 천원 단위로 작성됨."""
    hold = holdings_at(d)
    rows = [[h["code"], h["name"], h["face"], (eval_amount(h["face"], h["price0"] - 15, h["currency"]) / 1000).quantize(Decimal(1)),
             None, h["currency"], d] for h in hold]
    p = out / f"보유채권내역_{d.strftime('%Y%m%d')}_천원.xlsx"
    _write_xlsx(p, "보유채권", d, ["종목코드", "종목명", "보유수량", "장부금액", "전월 평가금액", "통화", "평가기준일"], rows, unit="천원")
    return p


def write_journal(out: Path, d: date, *, unbalanced: bool = False) -> dict[str, Path]:
    out.mkdir(parents=True, exist_ok=True)
    lines = [
        ["J0001", 1, d, "1101001", "(가상)현금", Decimal("1500000"), 0, "KRW", "회계팀", "수수료 수취"],
        ["J0001", 2, d, "4101001", "(가상)수수료수익", 0, Decimal("1500000"), "KRW", "회계팀", "수수료 수취"],
        ["J0002", 1, d, "5101001", "(가상)지급수수료", Decimal("320000"), 0, "KRW", "운영팀", "예탁수수료"],
        ["J0002", 2, d, "2101001", "(가상)미지급비용", 0, Decimal("320000"), "KRW", "운영팀", "예탁수수료"],
        ["J0003", 1, d, "1201001", "(가상)외화예금", Decimal("1000.50"), 0, "USD", "자금팀", "외화이자"],
        ["J0003", 2, d, "4201001", "(가상)이자수익", 0, Decimal("1000.50"), "USD", "자금팀", "외화이자"],
    ]
    if unbalanced:
        lines[1][6] = Decimal("1499000")
        lines.append(["J0004", 1, d, "9999999", "(가상)미등록계정", Decimal("100"), Decimal("100"), "KRW", "회계팀", "오류라인"])
    jp = out / f"전표업로드_{d.strftime('%Y%m%d')}{'_오류' if unbalanced else ''}.csv"
    with open(jp, "w", newline="", encoding="cp949") as f:   # 국내 시스템에서 흔한 CP949
        w = csv.writer(f)
        w.writerow(["전표번호", "라인번호", "회계일자", "계정코드", "계정명", "차변금액", "대변금액", "통화", "부서", "적요"])
        for ln in lines:
            w.writerow([x.isoformat() if isinstance(x, date) else x for x in ln])
    cp = out / "계정과목표.csv"
    with open(cp, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["계정코드", "계정명"])
        for code, name in [("1101001", "(가상)현금"), ("4101001", "(가상)수수료수익"), ("5101001", "(가상)지급수수료"),
                           ("2101001", "(가상)미지급비용"), ("1201001", "(가상)외화예금"), ("4201001", "(가상)이자수익")]:
            w.writerow([code, name])
    return {"journal": jp, "coa": cp}


def write_etf_recon(out: Path, d: date) -> dict[str, Path]:
    """신규 업무 시나리오(B): 내부 ETF 잔고 vs 예탁기관 잔고 — 템플릿 미등록 자료."""
    out.mkdir(parents=True, exist_ok=True)
    rnd = random.Random(7)
    items = [(f"A9{i:05d}", f"가상ETF {i:02d}", rnd.randint(1, 500) * 1000) for i in range(1, 16)]
    a = out / f"내부ETF잔고_{d.strftime('%Y%m%d')}.csv"
    b = out / f"예탁기관ETF잔고_{d.strftime('%Y%m%d')}.csv"
    with open(a, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["종목코드", "종목명", "보유수량", "기준일"])
        for code, name, q in items:
            w.writerow([code, name, q, d.isoformat()])
    with open(b, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["종목코드", "종목명", "보유수량", "기준일"])
        for i, (code, name, q) in enumerate(items):
            if i == 3:
                q += 100            # 수량 차이
            if i == 7:
                continue            # 예탁기관 누락
            w.writerow([code, name, q, d.isoformat()])
        w.writerow(["A9" + "09999", "가상ETF 99", 1000, d.isoformat()])
    return {"left": a, "right": b}


def write_price_pdf(out: Path, d: date) -> Path | None:
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
    except ImportError:
        return None
    p = out / f"외부평가단가_{d.strftime('%Y%m%d')}.pdf"
    rows = [["Code", "Agency", "BaseDate", "Price", "CCY"]]
    for h in holdings_at(d):
        rows.append([h["code"], "VirtualVal", d.isoformat(), f"{price_at(h, d)}", h["currency"]])
    doc = SimpleDocTemplate(str(p), pagesize=A4)
    t = Table(rows)
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.5, colors.black)]))
    doc.build([t])
    return p


def generate_all(out: Path) -> dict[str, object]:
    cur = date(2026, 9, 30)
    res: dict[str, object] = {"current": write_bond_set(out / "bond_2026-09", cur)}
    res["errors"] = write_bond_set(out / "bond_2026-09_errors", cur, errors=True, suffix="_오류")
    for hd in (date(2025, 9, 30), date(2025, 12, 31), date(2026, 6, 30), date(2026, 8, 31)):
        res[f"history_{hd}"] = write_bond_set(out / "history" / hd.isoformat(), month_end(hd))
    res["renamed"] = write_renamed_holdings(out / "format_change", cur)
    res["thousand"] = write_thousand_unit_holdings(out / "unit_error", cur)
    res["journal"] = write_journal(out / "journal", cur)
    res["journal_bad"] = write_journal(out / "journal", cur, unbalanced=True)
    res["etf"] = write_etf_recon(out / "new_workflow_etf", cur)
    (out / "pdf").mkdir(parents=True, exist_ok=True)
    res["pdf"] = write_price_pdf(out / "pdf", cur)
    return res


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / "sample_data"
    r = generate_all(target)
    print(f"가상 시연 데이터 생성 완료: {target}")
    for k, v in r.items():
        print(f"  {k}: {v}")
