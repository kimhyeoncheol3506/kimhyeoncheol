# -*- coding: utf-8 -*-
"""사진 넣기: python3 photos.py <프로젝트> 키=wc아이디 ... → 09_소재/img_final/{id}.jpg + pick.json + meta.json(출처)"""
import json, shutil, sys
V = "/home/user/kimhyeoncheol/video_projects"; W = f"{V}/시장3x3_시리즈/00_사진/wc"; P = f"{V}/{sys.argv[1]}/09_소재/img_final"
M = {m["id"]: m for m in json.load(open(f"{W}/meta.json"))}; pick, meta = {}, []
for kv in sys.argv[2:]:
    k, i = kv.split("="); shutil.copy(f"{W}/{i}.jpg", f"{P}/{i}.jpg"); pick[k] = i
    if M[i] not in meta: meta.append(M[i])
json.dump(pick, open(f"{P}/pick.json", "w"), ensure_ascii=False); json.dump(meta, open(f"{P}/meta.json", "w"), ensure_ascii=False, indent=1); print(pick)
