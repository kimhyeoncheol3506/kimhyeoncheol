# -*- coding: utf-8 -*-
"""조사표.md = 보도 4건 원문 텍스트(본문 확인) + 출처 URL — 자막 숫자는 이 원문에 있어야 함"""
import os
H = os.path.dirname(os.path.abspath(__file__))
SRC = [("b3a9dc", "서울신문 2026-11-11 이영숙 시의원 행감", "https://go.seoul.co.kr/news/newsView.php?id=20261111500398"), ("e3fdc1", "데일리환경 2026-11-25 최형규 시의원 행감", "https://www.dailyt.co.kr/newsView/dlt202611250045"),
       ("fd2d6b", "신아일보 2026-10-23 송옥주 의원 국감", "https://www.shinailbo.co.kr/news/articleView.html?idxno=5075330"), ("748e63", "더데일리이코노미 2026-11-03", "https://www.thedailyeconomy.kr/news/articleView.html?idxno=6633")]
L = ["# 조사표 — 가락시장 현대화·이전 논의 (보도 원문, 2026-11-26 수집)", "", "- 표기 메모: 1조 2,769억 = 12769억 · 6,830억 · 2,829억 · 5,939억 · 4,437억 · 8,332억 · 5,107억 · 7,115억 · 344억 3,800만 · 79억 6,600만 · 3억 1,300만 · 4,154억(1,638·2,183·333) · 550억 · 407억 · 2018·2031·2033·2009·2015·2024·2027·2039·2051·2011·2025·2030년 · 24개월 · 3년 · 17년 · 9년 · 3차례 · 1단계 2단계 3단계 4단계 · 채소1동 채소2동 · 5가지 3가지 · 2배", ""]
for f, t, u in SRC: L += [f"## {t}", u, open(f"{H}/{f}.txt", encoding="utf-8").read()[:20000], ""]
open(f"{H}/조사표.md", "w", encoding="utf-8").write("\n".join(L)); print("ok")
