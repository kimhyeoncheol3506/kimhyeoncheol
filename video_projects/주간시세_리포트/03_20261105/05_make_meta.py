import json
TL=json.load(open('03_장면/timeline.json',encoding='utf-8')); D=json.load(open('01_대본/대본데이터.json',encoding='utf-8'))
ts=lambda t:f"{int(t//60):02d}:{int(t%60):02d}"
lab={'hook':'오프닝 · 방어 ▲52% vs 부시리 ▼45%','title':'주간 시세 리포트 #3','overview':'한눈에 · 48품목 (내림 21 · 오름 26)','trend':'3주 흐름 (#1~#3)','up':'주의! 다시 오른 품목 (암꽃게·방어·삼치)','basket':'이번 주 장바구니','outro':'요약'}
lines=[]
for s in TL['sections']:
    if s['kind']=='rank':
        sec=next(x for x in D['sections'] if x['id']==f"rank{s['name'][0]}")
        lines.append(f"{ts(s['start'])} {s['name']} ▼{abs(round(sec['data']['변동']))}%")
    else: lines.append(f"{ts(s['start'])} {lab[s['kind']]}")
desc=("방어는 52% 올랐는데 닮은꼴 부시리는 45% 내렸다 🐟 노량진 주간 시세 리포트 #3 (11/2~11/5)\n"
"노량진수산 경락시세로 본 이번 주(11/2 월~11/5 목) 싸진 품목 TOP5, 다시 오른 품목 3가지, 3주 흐름, 이번 주 장바구니를 정리했습니다.\n"
"자료: 노량진수산주식회사 오늘의 경락시세(도매 경매가, kg 단위 경매의 수량 가중 중앙값, 지난주 같은 요일 10/26~10/29와 비교)\n\n⏱ 바로가기\n"+"\n".join(lines)+
"\n\n💬 다음 주에 궁금한 품목을 댓글로 남겨 주세요!\n🔔 구독·알림 설정하시면 다음 주 시세 리포트도 가장 먼저 받아보실 수 있어요.\n\n"
"※ 영상 속 가격은 도매 경매가(경락가)이며 가게 판매가와 다릅니다. 하루하루 물량과 크기 구성에 따라 값 차이가 큽니다.\n"
"※ 화면 속 사진은 실제 노량진 매장 사진이 아닌 자유 이용 이미지(CC BY)이며, 출처는 고정댓글에 있습니다. 내레이션은 AI 음성(여의도남자)입니다.\n\n#노량진수산시장 #수산물시세 #주간시세\n")
open('05_메타데이터/설명란_업로드용.txt','w',encoding='utf-8').write(desc)
meta=json.load(open('09_소재/img_final/meta.json',encoding='utf-8'))
th=json.load(open('/tmp/claude-0/-home-user-kimhyeoncheol/f4a2a367-9b3a-5634-92d5-7ea6bcc2bbba/scratchpad/cand.json'))[10]
pin=["📊 이번 주(11/2~11/5) 싸진 품목 TOP5 (kg당 경락가 중앙값, 지난주 같은 요일 대비)",
"1위 부시리 10,000→5,500원 (▼45%) · 2위 흰다리새우 17,600→10,300원 (▼42%) · 3위 대게 24,500→17,100원 (▼30%)",
"4위 줄전갱이 30,700→22,600원 (▼26%) · 5위 수꽃게 14,900→12,100원 (▼19%)",
"⚠ 다시 오른 품목: 암꽃게 ▲61% · 방어 ▲52% · 삼치(선) ▲41%","","도매 경락가이며 가게 판매가와 다릅니다.","","📷 사진 출처 (CC BY)"]
for m in meta: pin.append(f"- {m['section']}: \"{m.get('title','')}\" by {m.get('creator','')} ({m.get('license','').upper()} {m.get('license_version','')}) {m.get('foreign','')}")
pin.append(f"- 썸네일 배경: by {th[4]} (CC BY) {th[5]}")
open('05_메타데이터/고정댓글.txt','w',encoding='utf-8').write("\n".join(pin)+"\n")
open('05_메타데이터/제목_후보 3개.txt','w',encoding='utf-8').write("1. 노량진수산시장 11월 첫째 주 시세변화 (11/2~11/5)\n2. 방어 52% 오를 때 부시리는 45% 내렸다 | 노량진 주간 시세 리포트 #3\n3. 이번 주 노량진 뭐가 싸? 부시리·흰다리새우·대게 내렸다 | 주간 시세 #3 (11/2~11/5)\n")
open('05_메타데이터/썸네일_가이드.txt','w',encoding='utf-8').write("사용자 지정 형식(make_thumbnail_title.py): 시장 사진 + 금색 '노량진수산시장' + 흰색 '11월 첫째 주 시세변화' + 빨간 붓터치. 배경 사진은 CC BY 시장 사진(실제 노량진 아님).\n")
r=[x for x in json.load(open('../회차.json',encoding='utf-8')) if x['회차']!=3]
r.append({"회차":3,"기간":"2026-11-02~2026-11-05(월~목)","비교":"2026-10-26~2026-10-29","폴더":"03_20261105","1위":"부시리(활)","변동률":-45.0,
          "싸진_TOP5":["부시리","흰다리새우","대게","줄전갱이","수꽃게"],"오른_3":["암꽃게","방어","삼치(선)"],"영상_길이":f"{int(TL['total']//60)}:{int(TL['total']%60):02d}","스타일":"에디토리얼 골드(HyperFrames)"})
json.dump(r,open('../회차.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print("\n".join(lines))
