# -*- coding: utf-8 -*-
"""주간 시세 리포트 메타데이터 (#4부터 고정 틀): 제목(고정 형식)·설명란(챕터)·고정댓글·쇼츠 제목·회차.json 갱신.
회차마다 고칠 곳 없음 — 01_대본/대본데이터.json과 03_장면/timeline.json, 09_소재/img_final/meta.json에서 읽는다."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(f'{HERE}/03_장면/timeline.json', encoding='utf-8')); D = json.load(open(f'{HERE}/01_대본/대본데이터.json', encoding='utf-8'))
meta = json.load(open(f'{HERE}/09_소재/img_final/meta.json', encoding='utf-8')); Wk = D["weekly"]
ts = lambda t: f"{int(t // 60):02d}:{int(t % 60):02d}"
md = lambda d: f"{int(d[5:7])}/{int(d[8:])}"
per = f"{md(D['period'][0])}~{md(D['period'][1])}"; cmp = f"{md(D['compare'][0])}~{md(D['compare'][1])}"
mv = {m["name"]: m["ch"] for m in D["movers"]}
ranks = {s["id"]: s for s in D["sections"] if s["kind"] == "rank"}
lab = {'hook': f'오프닝 · {Wk["hook"][0]["name"]} {"▲" if mv[Wk["hook"][0]["name"]] > 0 else "▼"}{abs(round(mv[Wk["hook"][0]["name"]]))}%',
       'title': f'주간 시세 리포트 #{D["episode"]} ({per})', 'overview': f'한눈에 · {D["n"]}품목 (내림 {D["n_down"]} · 오름 {D["n_up"]})',
       'trend': f'{len(Wk["trend"]["head"])}주 흐름', 'up': f'주의! 오른 품목 TOP3 ({" · ".join(Wk["up_names"])})', 'basket': '이번 주 장바구니', 'outro': '요약 · 매주 토요일 시세 정리'}
ch = []
for s in TL['sections']:
    if s['kind'] == 'rank':
        r = ranks[f"rank{s['name'][0]}"]; ch.append(f"{ts(s['start'])} {s['name']} ▼{abs(round(r['data']['변동']))}%")
    else: ch.append(f"{ts(s['start'])} {lab[s['kind']]}")
title = f"노량진수산시장 이번 주 시세 | 싸진 것 TOP5 · 오른 것 TOP3 ({per})"
top = [(n, mv[n]) for n in Wk["recap"]]; ups = [(n, mv[n]) for n in Wk["up_names"]]
desc = (f"이번 주 노량진에서 싸진 것 TOP5와 오른 것 TOP3를 도매 경락가로 정리했습니다 🐟 ({per}, 지난주 {cmp} 대비)\n"
        f"싸진 것: " + " · ".join(f"{i + 1}위 {n} ▼{abs(round(v))}%" for i, (n, v) in enumerate(top)) + "\n"
        f"오른 것: " + " · ".join(f"{n} ▲{round(v)}%" for n, v in ups) + "\n\n⏱ 챕터\n" + "\n".join(ch) + "\n\n"
        "📊 자료: 노량진수산주식회사 오늘의 경락시세 (susansijang.co.kr) — kg 단위 경매의 수량 가중 중앙값, 이번 주(월~토)와 지난주(월~토) 비교\n"
        "※ 영상 속 가격은 도매 경매가(경락가)이며 가게 판매가와 다릅니다. 하루하루 물량과 크기 구성에 따라 값 차이가 큽니다.\n"
        "※ 화면 속 사진은 자유 이용 이미지(CC BY·CC0)이며 일부는 실제 노량진 사진이 아닙니다. 출처는 고정댓글에 있습니다. 내레이션은 AI 음성(여의도남자)입니다.\n\n"
        "📅 매주 토요일, 이번 주 노량진 시세를 정리합니다. 구독해 두면 장보기 전에 받아보실 수 있어요.\n"
        "▶ 매주 노량진 시세 정리는 재생목록/구독으로 받아보세요\n\n#노량진수산시장 #수산물시세 #주간시세\n")
os.makedirs(f'{HERE}/05_메타데이터', exist_ok=True)
open(f'{HERE}/05_메타데이터/설명란_업로드용.txt', 'w', encoding='utf-8').write(desc)
open(f'{HERE}/05_메타데이터/제목.txt', 'w', encoding='utf-8').write(title + "\n")
pin = [f"📊 이번 주({per}) 싸진 것 TOP5 (kg당 경락가 중앙값, 지난주 월~토 대비)"]
for i, k in enumerate(["rank1", "rank2", "rank3", "rank4", "rank5"]):
    r = ranks[k]; d = r["data"]; pin.append(f"{i + 1}위 {Wk['recap'][i]} {d['지난']:,}→{d['이번']:,}원 (▼{abs(round(d['변동']))}%)")
upd = next(s for s in D["sections"] if s["kind"] == "up")["data"]
pin.append("⚠ 오른 것 TOP3: " + " · ".join(f"{n} {d['지난']:,}→{d['이번']:,}원 (▲{round(d['변동'])}%)" for n, d in zip(Wk["up_names"], upd)))
pin += ["", "📅 매주 토요일 이번 주 시세 정리 — 구독·알림 설정해 두면 장보기 전에 받아보세요.", "도매 경락가이며 가게 판매가와 다릅니다. 자료: 노량진수산(주) 오늘의 경락시세", "", "📷 사진 출처"]
for m in meta: pin.append(f"- {m['section']}: \"{m.get('title', '')[:60]}\" by {m.get('creator') or 'unknown'} ({m.get('license', '').upper()} {m.get('license_version', '') or ''}) {m.get('foreign', '')}")
pin.append("- 썸네일 배경: \"Noryangjin Fish Market, Seoul, South Korea\" by Jirka Matousek (CC BY 2.0) https://www.flickr.com/photos/28415633@N00/8393751583")
open(f'{HERE}/05_메타데이터/고정댓글.txt', 'w', encoding='utf-8').write("\n".join(pin) + "\n")
h0 = Wk["hook"][0]["name"]
open(f'{HERE}/05_메타데이터/쇼츠_제목_설명.txt', 'w', encoding='utf-8').write(
    f"[티저 쇼츠] 제목: 이번 주 노량진 {h0} {abs(round(mv[h0]))}% {'하락' if mv[h0] < 0 else '상승'} | 싸진 것 TOP5 ({per}) #노량진수산시장 #수산물시세\n"
    f"설명: 이번 주 싸진 것 1위 {top[0][0]} ▼{abs(round(top[0][1]))}%. TOP5·오른 것 TOP3 전체는 관련 동영상에서 ▶ (본편 연결)\n※ 도매 경락가이며 가게 판매가와 다릅니다. 자료: 노량진수산(주) 오늘의 경락시세\n")
open(f'{HERE}/05_메타데이터/썸네일_가이드.txt', 'w', encoding='utf-8').write(
    "시리즈 고정 틀(#4부터): 주간시세_리포트/썸네일_고정배경.jpg + 금색 '노량진수산시장' + 흰색 '이번 주 시세 M/D~M/D' + 빨간 붓터치 (make_thumbnail_title.py). 매주 날짜만 바꾼다.\n")
R = json.load(open(f'{HERE}/../회차.json', encoding='utf-8')); R = [x for x in R if x['회차'] != D['episode']]
R.append({"회차": D["episode"], "기간": f"{D['period'][0]}~{D['period'][1]}(월~토)", "비교": f"{D['compare'][0]}~{D['compare'][1]}", "폴더": os.path.basename(HERE),
          "1위": Wk["recap"][0], "변동률": top[0][1], "싸진_TOP5": Wk["recap"], "오른_3": Wk["up_names"], "영상_길이": f"{int(TL['total'] // 60)}:{int(TL['total'] % 60):02d}",
          "스타일": "에디토리얼 골드(HyperFrames) · 고정 틀", "제목": title})
json.dump(R, open(f'{HERE}/../회차.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(title); print("\n".join(ch))
