# -*- coding: utf-8 -*-
"""조사표.md = topic.json sources의 원문(시장3x3_시리즈/00_자료/<hash>.txt) + 00_data/데이터_계산.md(경락 집계 근거)"""
import json, os
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H); A = "/home/user/kimhyeoncheol/video_projects/시장3x3_시리즈/00_자료"
CFG = json.load(open(f"{R}/00_data/topic.json", encoding="utf-8"))
L = [f"# 조사표 — {CFG.get('name', '')}", "", "## 데이터 계산 근거", open(f"{R}/00_data/데이터_계산.md", encoding="utf-8").read(), ""]
for h, label in CFG.get("src_texts", []):
    L += [f"## {label}", open(f"{A}/{h}.txt", encoding="utf-8").read()[:16000], ""]
L += ["## 표기 메모", CFG.get("num_note", "")]
open(f"{H}/조사표.md", "w", encoding="utf-8").write("\n".join(L)); print("ok")
