"""유튜브 설명란 5000자 상한 맞추기: 설명란은 요약·챕터·주요 출처 이름·그림 저작자만, 전체 출처 링크는 고정 댓글용 블록으로.
사용: python3 projects/_series_oneshot/make_youtube_txt.py <원본 youtube.txt> <출력 txt> <대본 yaml>  (유대인 편 도구를 시리즈용으로 일반화)"""
import re, sys, yaml
src, dst = sys.argv[1], sys.argv[2]
T = open(src, encoding="utf-8").read().splitlines()
proj = yaml.safe_load(open(sys.argv[3], encoding="utf-8"))
title = T[1]
i_desc = T.index("[설명란] ↓ 아래부터 그대로 복사") + 2
i_rel = T.index("🔗 관련 사이트")
i_src = T.index("📚 출처")
intro_ch = T[i_desc:i_rel]                       # 요약 + 챕터
disclaimer = [l for l in T[i_rel:i_src] if l and not l.startswith("·") and not l.startswith("🔗")]
full = []
for l in T[i_src + 1:]:
    if not l.startswith("·"):
        break
    full.append(l)
tags = next(l for l in T if l.startswith("#"))
# 주요 출처: 기관·저자 이름만(쉼표 앞), 중복 제거
names = []
for l in full:
    n = re.split(r",\s*「", l[2:])[0].strip()
    n = re.sub(r"\s*\(.*?\)\s*$", "", n)
    if n not in names:
        names.append(n)
photos = proj.get("photos", [])
by = [p for p in photos if "BY" in p["license"]]
pd = [p for p in photos if "BY" not in p["license"]]

def desc(nmax):
    L = intro_ch + [""] + disclaimer + ["", "📚 주요 출처 (전체 목록·링크는 고정 댓글)"]
    L.append(" / ".join(names[:nmax]) + (" 외" if nmax < len(names) else ""))
    L += ["", "🖼 그림 출처 (Wikimedia Commons)"]
    L += [f"· {p['title']} — {p['author']}, {p['license']}" for p in by]
    L.append(f"· 그 밖의 {len(pd)}점은 퍼블릭 도메인(작품별 링크는 고정 댓글)")
    L += ["", tags]
    return "\n".join(L)

n = len(names)
while len(desc(n)) > 4900:
    n -= 1
D = desc(n)
# 고정 댓글: 유튜브 댓글 1만 자 상한 → 9,000자 단위로 나눔
items = full + ["", "🖼 그림 출처와 이용 조건 (Wikimedia Commons)"] + \
        [f"· {p['title']} — {p['author']}, {p['license']} {p['url']}" for p in photos]
blocks, cur = [], []
for it in items:
    if len("\n".join(cur + [it])) > 9000:
        blocks.append(cur); cur = []
    cur.append(it)
blocks.append(cur)
out = ["[제목]", title, "", "━" * 20, f"[설명란] ↓ 아래부터 그대로 복사 ({len(D)}자 / 상한 5000자)", "━" * 20, D, "━" * 20, "",
       "[해시태그] (앞의 3개가 제목 위에 보임)", tags, ""]
for k, b in enumerate(blocks, 1):
    body = (f"📚 전체 출처 ({k}/{len(blocks)})\n" if k == 1 or len(blocks) > 1 else "") + "\n".join(b).strip()
    out += ["━" * 20, f"[고정 댓글 {k}/{len(blocks)}] ↓ 그대로 복사 ({len(body)}자 / 댓글 상한 10000자)", "━" * 20, body, ""]
open(dst, "w", encoding="utf-8").write("\n".join(out))
print(f"설명란 {len(D)}자 · 주요 출처 {n}/{len(names)} · 고정 댓글 {len(blocks)}개 · 그림 {len(photos)}점(BY-SA {len(by)})")
