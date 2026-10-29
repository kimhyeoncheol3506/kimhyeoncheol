# -*- coding: utf-8 -*-
"""설명란(바로가기 시간)·고정댓글·제목 후보·주간시세표를 05_메타데이터/에 만든다. 타임스탬프는 실제 타임라인(timeline.json) 기준."""
import json, os, csv
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
TL = json.load(open(f"{HERE}/timeline.json", encoding="utf-8")); D = json.load(open(f"{ROOT}/01_대본/대본데이터.json", encoding="utf-8"))
OUT = f"{ROOT}/05_메타데이터"; os.makedirs(OUT, exist_ok=True)
sp = {s["id"]: s for s in D["sections"]}; allc = D["allc"]
ts = lambda t: f"{int(t // 60):02d}:{int(t % 60):02d}"
lines = []
for s in TL["sections"]:
    sec = D["sections"][int(s["id"][2:])]
    if s["kind"] == "species":
        c = sec["total"]; lines.append(f"{ts(s['start'])} {sec['state']}어 {sec['name']} {'▲' if c >= 3 else ('▼' if c <= -3 else '■')}{abs(round(c))}%")
    else: lines.append(f"{ts(s['start'])} {s['name']}")
dn = sorted(allc, key=allc.get)[:2]; up = sorted(allc, key=allc.get, reverse=True)[:2]
nm = {s["key"]: s["short"] for s in D["sections"] if s["kind"] == "species"}
f = lambda k: f"{nm[k]} {allc[k]:+.0f}%"
hook = f"한 달 만에 {nm[dn[0]]} {abs(allc[dn[0]]):.0f}% 내리고 {nm[up[0]]} {allc[up[0]]:.0f}% 올랐다"
desc = f"""{hook} 🐟 10월 노량진 활어 12종·선어 6종 주간 시세 흐름
10월 한 달(10/1~10/28) 노량진수산 경락시세를 주 단위 그래프로 움직여 보여드립니다. 품종마다 첫째 주부터 넷째 주까지 kg당 평균 가격과 싼 주·비싼 주를 한눈에 확인하세요.
자료: 수협노량진수산 수산물가격정보 어종별 경락시세(도매 경매가). kg당 단가 = 평균가 ÷ 중량(kg), 품종별 한 달 분포의 상·하위 5% 거래를 뺀 거래량 가중평균. 1주 10/1~7, 2주 10/8~14, 3주 10/15~21, 4주 10/22~28.

⏱ 바로가기
""" + "\n".join(lines) + """

💬 다음에 보고 싶은 품종을 댓글로 남겨 주세요!
🔔 구독·알림 설정하시면 다음 시세 영상도 가장 먼저 받아보실 수 있어요.

※ 영상 속 가격은 도매 경매가(경락가)이며 가게 판매가와 다릅니다. 하루하루 물량과 품질, 크기 구성에 따라 값 차이가 큽니다.
※ (선)오징어는 10/1~7에만 거래돼 주간 흐름이 나오지 않아, 4주 모두 거래된 (선)무늬오징어로 대체했습니다.
※ 거래 물량이 적은 주(300kg 미만)는 화면에 '거래 적음'으로 표시했으니 참고만 해 주세요.
※ 화면 속 어종 그림은 직접 제작한 일러스트이며 실제 사진이 아닙니다. 내레이션은 AI 음성(여의도남자)입니다.

#노량진수산시장 #수산물시세 #주간시세
"""
open(f"{OUT}/설명란_업로드용.txt", "w", encoding="utf-8").write(desc)
rows = ["📊 10월 주간 kg당 평균 경락가(원) · 1주 → 4주 변화"]
for k in sorted(allc, key=allc.get):
    s = next(x for x in D["sections"] if x.get("key") == k); P = s["P"]
    rows.append(f"{s['state']}어 {s['name']}: {P[0]:,} → {P[1]:,} → {P[2]:,} → {P[3]:,} ({allc[k]:+.0f}%)")
rows += ["", "도매 경락가이며 가게 판매가와 다릅니다. 자료: 수협노량진수산 어종별 경락시세."]
open(f"{OUT}/고정댓글.txt", "w", encoding="utf-8").write("\n".join(rows) + "\n")
open(f"{OUT}/제목_후보 3개.txt", "w", encoding="utf-8").write(
    f"1. 10월 노량진 시세, 주마다 이렇게 움직였다 (활어 12종·선어 6종 그래프)\n2. 한 달 만에 {nm[dn[0]]} {abs(allc[dn[0]]):.0f}% 내렸다 | 10월 노량진 주간 시세 흐름\n3. 노량진 10월 시세 총정리: {nm[dn[0]]}·{nm[dn[1]]} 내리고 {nm[up[0]]}·{nm[up[1]]} 올랐다\n")
with open(f"{OUT}/주간시세표.csv", "w", encoding="utf-8-sig", newline="") as fp:
    w = csv.writer(fp); w.writerow(["상태", "품종", "1주(10/1~7)", "2주(10/8~14)", "3주(10/15~21)", "4주(10/22~28)", "1→4주 변화(%)", "1주 물량kg", "2주 물량kg", "3주 물량kg", "4주 물량kg"])
    for s in D["sections"]:
        if s["kind"] == "species": w.writerow([s["state"], s["name"]] + [round(v) for v in s["P"]] + [round(s["total"], 1)] + [round(v) for v in s["K"]])
print("메타데이터 완료")
