# -*- coding: utf-8 -*-
"""가락시장 시리즈 메타데이터: 제목 3안(topic.json), 챕터 설명란(끝에 재생목록), 고정댓글(사진 출처), 쇼츠 제목·설명"""
import json, os, runpy
os.chdir(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open('03_장면/timeline.json', encoding='utf-8')); meta = json.load(open('09_소재/img_final/meta.json', encoding='utf-8'))
G = runpy.run_path('01_대본/build_data.py', run_name="short"); CFG, INFO, NAMES, M, MI, perkg, yoy, r100, uname = (G[k] for k in ("CFG", "INFO", "NAMES", "M", "MI", "perkg", "yoy", "r100", "uname"))
PL = "https://www.youtube.com/playlist?list=PLe7bZbwVOrCE"
ts = lambda t: f"{int(t // 60):02d}:{int(t % 60):02d}"
D = json.load(open('01_대본/대본데이터.json', encoding='utf-8'))
ch = [f"{ts(s['start'])} {x['name']}" for s, x in zip(TL['sections'], D['sections'])]
data = "\n".join(f"- {n} {uname(INFO[n]['unit'])} 상품: 평균 {INFO[n]['t']['avg']:,}원 · kg당 약 {r100(perkg(n)):,}원" + (f" · 작년 대비 {yoy(n):+d}%" if yoy(n) is not None else "") for n in NAMES)
desc = (CFG["desc_intro"] + "\n\n⏱ 챕터\n" + "\n".join(ch) + "\n\n📊 데이터 (가락시장 경락가, 2026.11.12~11.26 평균, 상품 등급)\n" + data + "\n"
        "- 출처: KAMIS 도매가격(가락시장 경락가격) · kg당 = 상자 값 ÷ 상자 무게 · 작년 기록 5일 미만은 비교 안 함\n" + "".join(f"- {x}\n" for x in CFG.get("sources", [])) + "\n"
        "※ 경락가는 새벽 경매의 도매 낙찰가로 동네 가게 판매가와 다릅니다.\n※ 화면 속 사진은 자유 이용 이미지(CC BY·CC0)이며 실제 가락시장 사진이 아닐 수 있습니다. 출처는 고정댓글에 있습니다. 내레이션은 AI 음성(여의도남자)입니다.\n\n"
        f"💬 {CFG['ask']}\n📅 노량진·가락시장 등 전국 시장 도매가를 정리합니다.\n\n{CFG['hashtags']}\n\n▶ 시세 재생목록: {PL}\n")
open('05_메타데이터/설명란_업로드용.txt', 'w', encoding='utf-8').write(desc)
pin = [CFG["pin_head"]] + [f"{n}: kg당 약 {r100(perkg(n)):,}원" + (f" (작년 대비 {yoy(n):+d}%)" if yoy(n) is not None else "") for n in NAMES[:8]] + ["※ 가락시장 도매 경락가(KAMIS)이며 가게 값과 다릅니다.", f"▶ 시세 재생목록 {PL}", "", "📷 사진 출처"]
for m in meta: pin.append(f"- \"{m.get('title', '')[:60]}\" by {m.get('creator') or 'unknown'} ({m.get('license', '').upper()} {m.get('license_version', '') or ''}) {m.get('foreign', '')}")
open('05_메타데이터/고정댓글.txt', 'w', encoding='utf-8').write("\n".join(pin) + "\n")
open('05_메타데이터/제목_후보 3개.txt', 'w', encoding='utf-8').write("".join(f"{i + 1}. {t}\n" for i, t in enumerate(CFG["titles"])))
open('05_메타데이터/쇼츠_제목_설명.txt', 'w', encoding='utf-8').write(f"제목: {CFG['short_title']}\n설명:\n{CFG['short_desc']}\n※ KAMIS 가락시장 경락가(2026.11.12~11.26) 기준 도매가이며 가게 값과 다릅니다.\n▶ 본편: {CFG['titles'][0]}\n▶ 시세 재생목록 {PL}\n")
print("\n".join(ch))
