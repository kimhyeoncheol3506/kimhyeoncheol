#!/usr/bin/env bash
# 주간 시세 리포트 — 이번 주 회차 만들기 (#4부터 고정 틀)
#   1) 준비:   bash video_projects/주간시세_리포트/이번주_회차.sh 준비 <이번 주 월요일 YYYY-MM-DD>
#              → 음성 엔진·폰트·BGM 복구, 경락 데이터 받기(지난주 월~이번 주 토), 새 회차 폴더(직전 회차 스크립트 복사), 비교표·후보 출력, 고정 썸네일
#   2) 대본:   <회차폴더>/01_대본/build_data.py 의 TOP·UP·문장·weekly 만 이번 주 숫자로 바꾼다(숫자는 00_data/비교.json에서만), build_short.py 문장도
#   3) 만들기: bash video_projects/주간시세_리포트/이번주_회차.sh 만들기 <회차폴더>
#              → 대본·자막 숫자 대조 → 음성(여의도남자 1.12) → 발음 검수 → HyperFrames 렌더 → 검수 → 쇼츠 → 메타데이터(제목·설명란·고정댓글·회차.json)
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"; W="$REPO/video_projects/주간시세_리포트"; SK="$REPO/.claude/skills/ranking-video"
PY="$HOME/.cache/shorts-tts/venv/bin/python"; HFV="npx --yes hyperframes@0.8.214"
restore() {
  [ -x "$PY" ] || bash "$SK/voice/setup_cloud.sh"
  mkdir -p ~/.cache/ranking-video/fonts; cp -n "$REPO"/video_projects/겨울_시즌데이터_킹크랩_대방어_대게/03_장면/hf/assets/fonts/* ~/.cache/ranking-video/fonts/ 2>/dev/null || true
  B="$REPO/video_projects/10월_주간시세_모션그래프/03_장면/audio_assets"; [ -f "$B/sfx/bgm_loop.wav" ] || (mkdir -p "$B" && cd "$B" && python3 -I "$SK/scripts/make_audio_assets.py")
}
case "${1:-}" in
준비)
  M="$2"; SAT=$(date -d "$M +5 day" +%F); M0=$(date -d "$M -7 day" +%F); restore
  python3 -I "$SK/scripts/noryangjin_prices.py" fetch "$W/data" "$M0" "$SAT"
  LAST=$(ls -d "$W"/[0-9][0-9]_2* | sort | tail -1); N=$(( 10#$(basename "$LAST" | cut -c1-2) + 1 ))
  NEW="$W/$(printf %02d $N)_$(date -d "$SAT" +%Y%m%d)"; mkdir -p "$NEW"/{00_data,01_대본,02_음성,03_장면,05_메타데이터,07_그래픽,08_완성영상,09_소재/img_final}
  cp "$LAST/00_data/compare.py" "$NEW/00_data/"; cp "$LAST"/01_대본/{build_data.py,build_short.py,check_sub_numbers.py} "$NEW/01_대본/"
  cp "$LAST"/03_장면/{build_hf.py,mix_audio.py,build_shorts.py} "$NEW/03_장면/"; cp "$LAST"/{05_make_meta.py,02_qa_tts.py} "$NEW/"
  cp -n "$LAST"/09_소재/img_final/* "$NEW/09_소재/img_final/"; sed -i "s#$(basename "$LAST")#$(basename "$NEW")#g" "$NEW"/*.py "$NEW"/03_장면/*.py
  python3 "$NEW/00_data/compare.py" "$M" "$SAT" "$NEW/00_data/비교.json"
  python3 -I "$SK/scripts/make_thumbnail_title.py" --photo "$W/썸네일_고정배경.jpg" --line1 "노량진수산시장" \
    --line2 "이번 주 시세 $(date -d "$M" +%-m/%-d)~$(date -d "$SAT" +%-m/%-d)" --out "$NEW/07_그래픽/썸네일.png"
  echo "새 회차 폴더: $NEW  → 01_대본/build_data.py·build_short.py 를 이번 주 숫자로 바꾼 뒤 '만들기'를 실행하세요." ;;
만들기)
  E="$(cd "$2" && pwd)"; restore; cd "$E"
  python3 01_대본/build_data.py && python3 01_대본/build_short.py
  python3 - <<'PYX'
import json,re
D=json.load(open("01_대본/대본데이터.json")); dm=D["display_map"]; rx=re.compile("|".join(re.escape(a) for a,_ in dm)); mp=dict(dm)
for s in D["sections"]:
    for x in s["sentences"]:
        while len(x)<2: x.append({})
        x[2:]=[rx.sub(lambda m: mp[m.group(0)], x[0])]
json.dump(D,open("01_대본/_자막대조용.json","w"),ensure_ascii=False)
PYX
  python3 01_대본/check_sub_numbers.py _자막대조용.json short1.json
  "$PY" "$SK/voice/make_voice_yeouido.py" 01_대본/대본데이터.json 02_음성 --voice 여의도남자 --speed 1.12
  "$PY" "$SK/voice/make_voice_yeouido.py" 01_대본/short1.json 02_음성_쇼츠/short1 --voice 여의도남자 --speed 1.12
  "$PY" 02_qa_tts.py > 02_음성/qa.log 2>&1 || true; tail -15 02_음성/qa.log
  cd 03_장면 && python3 build_hf.py && python3 mix_audio.py && python3 build_shorts.py short1
  (cd hf && $HFV check --json > ../check.json || true; $HFV render -o ../../08_완성영상/완성영상_1080p.mp4 -f 30 -q standard --quiet .)
  (cd hf_short1 && $HFV render -o ../../08_완성영상/쇼츠_short1.mp4 -f 30 -q standard --quiet .)
  cd .. && for f in 08_완성영상/*.mp4; do python3 -I "$SK/scripts/verify_video.py" "$f" | tail -2; done
  python3 05_make_meta.py
  echo "완료: $E/08_완성영상, 05_메타데이터, 07_그래픽/썸네일.png" ;;
*) sed -n 2,9p "$0"; exit 1 ;;
esac
