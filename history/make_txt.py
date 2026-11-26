# -*- coding: utf-8 -*-
"""롱폼 업로드 TXT 자동 생성: 제목·설명(대본 앞부분 요약)·챕터 시간표·참고 사료·고정 댓글(판결 질문).
사용: python make_txt.py L02_척준경 "주제 해시태그1 해시태그2"
"""
import json, os, re, sys

ROOT = "/home/user/kimhyeoncheol"
EP = sys.argv[1]
TAGS = sys.argv[2].split() if len(sys.argv) > 2 else []
D = os.path.join(ROOT, "history", EP)
lines = [l for l in open(os.path.join(D, "script.txt"), encoding="utf-8").read().splitlines() if l.strip()]
W = json.load(open(os.path.join(D, "words.json"), encoding="utf-8"))
first, acc = {}, 0
for i, l in enumerate(lines):
    first[i] = W[min(acc, len(W) - 1)]["s"]; acc += len(l.split())
ch = json.load(open(os.path.join(D, "chapters.json"), encoding="utf-8"))
sb = json.load(open(os.path.join(D, "storyboard.json"), encoding="utf-8"))
title = sb.get("title", EP)
mmss = lambda t: "%02d:%02d" % (int(t) // 60, int(t) % 60)
stamps, seen = [], set()
for c in ch:
    ln = c.get("line", 0)
    key = (c.get("no"), c.get("title"))
    if key in seen:
        continue
    seen.add(key)
    t = 0 if ln == 0 else first[ln]
    stamps.append("%s %s %s" % (mmss(t), c.get("no", ""), c.get("title", "")))
# 판결 질문: '판결해 주세요' 다음 두 줄
judge = []
for i, l in enumerate(lines):
    if "판결해 주세요" in l:
        judge = [x for x in lines[i + 1:i + 4] if x.endswith("?")][:2]
        break
nxt = lines[-3:] if len(lines) > 3 else []
# 참고 사료: factsheet '근거' 칸에서 『』·「」 항목 수집
fs = open(os.path.join(D, "factsheet.md"), encoding="utf-8").read()
srcs = []
for m in re.findall(r"[『「][^』」]{1,30}[』」]", fs):
    if m not in srcs and "?" not in m and m[1:-1] != title and len(m) <= 22 and "왜" not in m:
        srcs.append(m)
desc = " ".join(lines[:6])
txt = f"""[제목 후보]
1) {title}   ← 추천
2) (대본의 판결 질문을 제목으로) {judge[0] if judge else ''}

[설명]
{desc}
가상의 장면 없이 기록으로만 따라갑니다.

{chr(10).join(stamps)}

참고 사료: {', '.join(srcs[:12])}
※ 장면은 사료를 바탕으로 한 카툰 재연이며, 인물 표정·동작은 각색입니다. '전해집니다'로 말한 부분은 기록으로 확인되지 않은 이야기입니다.
※ 내레이션: AI 음성
(음악·효과음 크레딧: {EP}_audio_credits.txt 내용을 여기에 붙임)

#역사가지운그날 #한국사 #역사 {' '.join('#' + t.lstrip('#') for t in TAGS)}

[고정 댓글]
⚖️ 당신의 판결은?
{chr(10).join('- ' + j for j in judge)}
다음 편: {' '.join(nxt)}
"""
out = os.path.join(ROOT, "output", "longform", EP + ".txt")
open(out, "w", encoding="utf-8").write(txt)
print(out)
