"""PDF 텍스트·표 추출(pdfplumber, MIT). 추출값은 '미검증'이며 원문 페이지와 연결된다.

스캔 PDF(OCR 필요)는 탐지만 하고 값은 추출하지 않는다.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import ParsedFile, ParseError, build_table, detect_base_date, detect_unit


def parse_pdf(path: Path, filename: str, max_rows: int) -> ParsedFile:
    with open(path, "rb") as f:
        if not f.read(5).startswith(b"%PDF"):
            raise ParseError("PDF 형식이 아니거나 손상된 파일입니다.")
    try:
        import pdfplumber
    except ImportError as e:  # pragma: no cover
        raise ParseError("pdfplumber가 설치되어 있지 않습니다.") from e
    try:
        pdf = pdfplumber.open(str(path))
    except Exception as e:
        msg = str(e).lower()
        if "password" in msg or "encrypt" in msg:
            raise ParseError("비밀번호로 보호된 PDF입니다.") from e
        raise ParseError(f"PDF를 열 수 없습니다: {type(e).__name__}") from e

    pages: list[dict[str, Any]] = []
    warnings: list[str] = []
    texts: list[str] = []
    grouped: dict[tuple, dict[str, Any]] = {}
    try:
        for pno, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            needs_ocr = len(page.chars) == 0 and len(page.images) > 0
            pinfo = {"page": pno, "chars": len(page.chars), "needs_ocr": needs_ocr,
                     "text": text[:5000], "tables": 0}
            if needs_ocr:
                warnings.append(f"{pno}페이지는 스캔 이미지로 보입니다. OCR은 지원하지 않습니다(값 미추출).")
            texts.extend(text.splitlines()[:15])
            method = "lines"
            try:
                found = page.find_tables()
                if not found and len(page.chars) > 0:
                    # 괘선 없는 표: 텍스트 정렬 기반 추출(신뢰도 낮음 — 원문 대조 필수)
                    found = page.find_tables({"vertical_strategy": "text", "horizontal_strategy": "text"})
                    method = "text_alignment"
            except Exception:
                found = []
                warnings.append(f"{pno}페이지 표 추출 실패.")
            pinfo["table_method"] = method
            for ti, tbl in enumerate(found, start=1):
                data = tbl.extract()
                if not data:
                    continue
                pinfo["tables"] += 1
                key = tuple((c or "").strip() for c in data[0])
                g = grouped.setdefault(key, {"grid": [], "pos": [], "pages": [], "bboxes": [], "methods": set()})
                g["methods"].add(method)
                skip_header = bool(g["grid"])  # 다음 페이지에서 반복되는 헤더는 제외
                for ri, r in enumerate(data):
                    if skip_header and ri == 0:
                        continue
                    g["grid"].append([(c.strip() if isinstance(c, str) else c) for c in r])
                    g["pos"].append(f"p{pno} 표{ti} r{ri + 1}")
                g["pages"].append(pno)
                g["bboxes"].append({"page": pno, "bbox": [round(x, 1) for x in tbl.bbox]})
            pages.append(pinfo)
    finally:
        pdf.close()

    tables = []
    for i, g in enumerate(grouped.values(), start=1):
        name = f"PDF표{i}(p{g['pages'][0]}-{g['pages'][-1]})"
        t, tw = build_table(name, g["grid"], g["pos"], max_rows,
                            {"pages": g["pages"], "bboxes": g["bboxes"], "review_status": "EXTRACTED_UNVERIFIED",
                             "extraction_method": sorted(g["methods"])})
        warnings.extend(tw)
        if t:
            t.meta["unit"] = detect_unit(texts)
            tables.append(t)
    if not tables:
        warnings.append("PDF에서 표를 추출하지 못했습니다. 원문 텍스트만 제공됩니다.")
    meta = {"page_count": len(pages), "pages": pages, "base_date": detect_base_date(texts, filename),
            "unit": detect_unit(texts), "extraction_status": "EXTRACTED_UNVERIFIED"}
    return ParsedFile("pdf", tables, meta, warnings)
