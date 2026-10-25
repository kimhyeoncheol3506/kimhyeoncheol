# -*- coding: utf-8 -*-
"""AI 영상 샷 리스트 만들기 (ranking-video v2.8.0)

사용법: python3 -I make_shotlist.py <대본데이터.json> <작업폴더>
출력: <작업폴더>/09_소재/AI영상_샷리스트.md — 섹션마다 만들 클립 수·파일 이름·프롬프트 칸
용도: Pavo AI(app.pavo-ai.work)·Digen AI(digen.ai) 같은 영상 생성 사이트는 사용자 계정으로 로그인해서 쓰는 웹 서비스라
      클로드가 대신 만들 수 없다. 이 표대로 사용자가 클립을 만들어 <작업폴더>/09_소재/video/ 에 넣으면 렌더러가 자동으로 쓴다.
파일 이름: <섹션이름>__01.mp4 (섹션 이름은 대본데이터.json의 name과 같게, 예: 입고__01.mp4). 같은 섹션에 여러 개면 __02, __03.
"""
import json, os, sys

D = json.load(open(sys.argv[1], encoding="utf-8")); proj = sys.argv[2]
rows = []
for s in D["sections"]:
    n_chars = sum(len(x[0]) for x in s["sentences"]); sec = n_chars / 6.5 + 0.3 * len(s["sentences"])
    clips = max(1, round(sec / 30))
    hint = s.get("tagline") or s.get("card_sub") or s.get("card_name") or s.get("label", "")
    first = s["sentences"][0][0]
    rows.append((s["name"], int(sec), clips, hint, first))
L = ["# AI 영상 샷 리스트", "",
     f"영상: {D.get('title','')}", "",
     "## 만드는 법 (사용자가 직접)",
     "1. Pavo AI(https://app.pavo-ai.work/) 또는 Digen AI(https://digen.ai/)에 로그인해서 아래 프롬프트로 클립을 만든다. 클립마다 5~10초, 가로 16:9, 가능하면 720p 이상, **워터마크 없는 플랜인지 확인**.",
     "2. 파일 이름을 `<섹션이름>__01.mp4`로 바꿔 `09_소재/video/` 폴더에 넣는다(섹션 이름은 아래 표의 첫 칸 그대로). 소리는 쓰지 않는다.",
     "3. 클로드에게 \"AI 영상 넣어서 다시 렌더해 줘\"라고 한다. 사진 칸 사이사이(두 번째 칸마다)에 클립이 들어가고, 설명란에는 'AI로 만든 영상' 고지가 자동으로 붙는다.", "",
     "## 쓰기 전에 지킬 것",
     "- **사실을 증명하는 장면에는 쓰지 않는다**(실제 가격·시세·사건·실존 점포·실존 인물). 분위기용 장면(새벽 시장 분위기, 바다, 수조, 일반 생선)만.",
     "- 실제처럼 보이는 합성 영상은 유튜브 업로드 때 '변경되었거나 합성된 콘텐츠'로 표시한다(스튜디오 업로드 화면). 설명란에는 고지 문구가 자동으로 들어간다.",
     "- 두 서비스의 상업적 이용·워터마크·저작권 약관을 가입한 플랜에서 직접 확인한다(클로드가 확인하지 못함).",
     "- 글자·간판·로고가 크게 나오거나 얼굴 클로즈업이 나온 클립은 쓰지 않는다. 손가락·글씨가 깨진 클립도 다시 만든다.", "",
     "## 섹션별 샷 (프롬프트는 영어가 결과가 안정적이다)", "",
     "| 섹션 이름 | 길이(초) | 클립 수 | 파일 이름 | 이 구간 주제 | 프롬프트(직접 채움) |", "|---|---|---|---|---|---|"]
for name, sec, clips, hint, first in rows:
    L.append(f"| {name} | {sec} | {clips} | {name}__01.mp4 | {hint} · \"{first[:24]}…\" | (예: cinematic slow pan of a quiet Korean fish market at night, wet floor, styrofoam boxes, no text, no people close-up) |")
os.makedirs(os.path.join(proj, "09_소재"), exist_ok=True)
out = os.path.join(proj, "09_소재", "AI영상_샷리스트.md"); open(out, "w", encoding="utf-8").write("\n".join(L) + "\n"); print(out)
