#!/usr/bin/env bash
# 데이터 롱폼 한 편 완성 (크리스마스_회장보기 · 킹크랩_무게속임수 같은 구조)
# 사용: bash 롱폼_만들기.sh <프로젝트폴더> <upload_ready 이름> [--skip-voice]
#   calc → 대본·쇼츠 → 조사표·자막 숫자 대조 → 음성(여의도남자 1.12, 없을 때만) → 발음 QA → HF → 믹스 → 쇼츠 → 렌더 → 점검 → 메타 → upload_ready/<이름>/
set -euo pipefail
P="$(cd "$1" && pwd)"; NAME="$2"; SKIPV="${3:-}"
R=/home/user/kimhyeoncheol; SK="$R/.claude/skills/ranking-video"; PY="$HOME/.cache/shorts-tts/venv/bin/python"; HFV="npx --yes hyperframes@0.8.214"
cd "$P"
if [ -f 00_data/prices.lock ]; then echo "가격 고정(prices.lock): $(cat 00_data/prices.lock)"; else python3 00_data/calc.py | tail -3; fi
python3 01_대본/build_data.py && python3 01_대본/build_short.py >/dev/null
python3 01_대본/make_조사표.py && python3 01_대본/check_sub_numbers.py 대본데이터.json short1.json
if [ "$SKIPV" != "--skip-voice" ]; then
  "$PY" "$SK/voice/make_voice_yeouido.py" 01_대본/대본데이터.json 02_음성 --voice 여의도남자 --speed 1.12
  "$PY" "$SK/voice/make_voice_yeouido.py" 01_대본/short1.json 02_음성_쇼츠/short1 --voice 여의도남자 --speed 1.12
fi
mkdir -p 02_음성_쇼츠; "$PY" 02_qa_tts.py > 02_음성/qa.log 2>&1 || true; tail -8 02_음성/qa.log
"$PY" 02_qa_tts.py 01_대본/short1.json 02_음성_쇼츠/short1 > 02_음성_쇼츠/qa.log 2>&1 || true; tail -4 02_음성_쇼츠/qa.log
cd 03_장면 && python3 build_hf.py && python3 mix_audio.py && python3 build_shorts.py short1
(cd hf && $HFV check --json > ../check.json || true; $HFV render -o ../../08_완성영상/완성영상_1080p.mp4 -f 30 -q standard --quiet .)
(cd hf_short1 && $HFV render -o ../../08_완성영상/쇼츠_short1.mp4 -f 30 -q standard --quiet .)
cd .. && for f in 08_완성영상/완성영상_1080p.mp4 08_완성영상/쇼츠_short1.mp4; do python3 -I "$SK/scripts/verify_video.py" "$f" | tail -3; done
python3 05_make_meta.py
U="$R/upload_ready/$NAME"; mkdir -p "$U"
cp 07_그래픽/썸네일_A.png "$U/썸네일_1280x720.png"; cp 07_그래픽/썸네일_B.png "$U/썸네일_B안_1280x720.png"
cp "05_메타데이터/제목_후보 3개.txt" "$U/제목_3안.txt"; cp 05_메타데이터/설명란_업로드용.txt "$U/설명란.txt"; cp 05_메타데이터/고정댓글.txt "$U/고정댓글.txt"
cp 05_메타데이터/쇼츠_제목_설명.txt "$U/쇼츠_제목_설명.txt"; cp 08_완성영상/쇼츠_short1.mp4 "$U/쇼츠.mp4"
ls -la "$U"; echo "완료: $P/08_완성영상/완성영상_1080p.mp4 · $U"
