# -*- coding: utf-8 -*-
"""가락시장 시리즈(보도·공식 자료 편) 메타데이터: topic.json의 제목·설명·출처 + 챕터 + 고정댓글 + 쇼츠"""
import json, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open('00_data/topic.json', encoding='utf-8')); TL = json.load(open('03_장면/timeline.json', encoding='utf-8')); meta = json.load(open('09_소재/img_final/meta.json', encoding='utf-8'))
D = json.load(open('01_대본/대본데이터.json', encoding='utf-8')); PL = "https://www.youtube.com/playlist?list=PLe7bZbwVOrCE"
ts = lambda t: f"{int(t // 60):02d}:{int(t % 60):02d}"
ch = [f"{ts(s['start'])} {x['name']}" for s, x in zip(TL['sections'], D['sections'])]
desc = (CFG["desc"] + "\n\n⏱ 챕터\n" + "\n".join(ch) + "\n\n📰 출처\n" + "".join(f"- {x}\n" for x in CFG["sources"]) + "\n" + CFG["note"] + "\n"
        "※ 화면 속 사진은 자유 이용 이미지(CC0·CC BY)이며 실제 가락시장 사진이 아닐 수 있습니다. 출처는 고정댓글에 있습니다. 내레이션은 AI 음성(여의도남자)입니다.\n\n"
        f"💬 {CFG['ask']}\n📅 노량진·가락시장 등 전국 시장 이야기와 도매가를 정리합니다.\n\n{CFG['hashtags']}\n\n▶ 시세 재생목록: {PL}\n")
open('05_메타데이터/설명란_업로드용.txt', 'w', encoding='utf-8').write(desc)
pin = [CFG["titles"][0], "📰 출처"] + [f"- {x}" for x in CFG["sources"]] + [CFG["note"], f"▶ 시세 재생목록 {PL}", "", "📷 사진 출처"] + [f"- \"{m.get('title', '')[:60]}\" by {m.get('creator') or 'unknown'} ({m.get('license', '').upper()} {m.get('license_version', '') or ''}) {m.get('foreign', '')}" for m in meta]
open('05_메타데이터/고정댓글.txt', 'w', encoding='utf-8').write("\n".join(pin) + "\n")
open('05_메타데이터/제목_후보 3개.txt', 'w', encoding='utf-8').write("".join(f"{i + 1}. {t}\n" for i, t in enumerate(CFG["titles"])))
open('05_메타데이터/쇼츠_제목_설명.txt', 'w', encoding='utf-8').write(f"제목: {CFG['short_title']}\n설명:\n{CFG['short_desc']}\n▶ 본편: {CFG['titles'][0]}\n▶ 시세 재생목록 {PL}\n")
print("\n".join(ch))
