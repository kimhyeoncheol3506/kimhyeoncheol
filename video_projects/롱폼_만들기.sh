#!/usr/bin/env bash
# 데이터 롱폼 한 편 완성 (크리스마스_회장보기 · 킹크랩_무게속임수 같은 구조)
# 사용: [SHORTS="short1 short2 short3"] bash 롱폼_만들기.sh <프로젝트폴더> <upload_ready 이름> [--skip-voice]   (쇼츠 여러 편이면 쇼츠1.mp4… · 07_그래픽/썸네일_세로.png 있으면 같이 복사)
#   calc → 대본·쇼츠 → 조사표·자막 숫자 대조 → 음성(여의도남자 1.12, 없을 때만) → 발음 QA → HF → 믹스 → 쇼츠 → 렌더 → 점검 → 메타 → upload_ready/<이름>/
set -euo pipefail
P="$(cd "$1" && pwd)"; NAME="$2"; SKIPV="${3:-}"
R=/home/user/kimhyeoncheol; SK="$R/.claude/skills/ranking-video"; PY="$HOME/.cache/shorts-tts/venv/bin/python"; HFV="npx --yes hyperframes@0.8.214"
SH="${SHORTS:-short1}"
cd "$P"
if [ -f 00_data/prices.lock ]; then echo "가격 고정(prices.lock): $(cat 00_data/prices.lock)"; else python3 00_data/calc.py | tail -3; fi
python3 01_대본/build_data.py && python3 01_대본/build_short.py >/dev/null
python3 01_대본/make_조사표.py && python3 01_대본/check_sub_numbers.py 대본데이터.json $(for s in $SH; do echo $s.json; done)
if [ "$SKIPV" != "--skip-voice" ]; then
  "$PY" "$SK/voice/make_voice_yeouido.py" 01_대본/대본데이터.json 02_음성 --voice 여의도남자 --speed 1.12
  for s in $SH; do "$PY" "$SK/voice/make_voice_yeouido.py" 01_대본/$s.json 02_음성_쇼츠/$s --voice 여의도남자 --speed 1.12; done
fi
mkdir -p 02_음성_쇼츠; "$PY" 02_qa_tts.py > 02_음성/qa.log 2>&1 || true; tail -8 02_음성/qa.log
for s in $SH; do "$PY" 02_qa_tts.py 01_대본/$s.json 02_음성_쇼츠/$s > 02_음성_쇼츠/qa_$s.log 2>&1 || true; tail -4 02_음성_쇼츠/qa_$s.log; done
cd 03_장면 && python3 build_hf.py && python3 mix_audio.py && for s in $SH; do python3 build_shorts.py $s; done
(cd hf && $HFV check --json > ../check.json || true; $HFV render -o ../../08_완성영상/완성영상_1080p.mp4 -f 30 -q standard --quiet .)
for s in $SH; do (cd hf_$s && $HFV render -o ../../08_완성영상/쇼츠_$s.mp4 -f 30 -q standard --quiet .); done
cd .. && for f in 08_완성영상/완성영상_1080p.mp4 $(for s in $SH; do echo 08_완성영상/쇼츠_$s.mp4; done); do python3 -I "$SK/scripts/verify_video.py" "$f" | tail -3; done
python3 05_make_meta.py
U="$R/upload_ready/$NAME"; mkdir -p "$U"
cp 07_그래픽/썸네일_A.png "$U/썸네일_1280x720.png"; cp 07_그래픽/썸네일_B.png "$U/썸네일_B안_1280x720.png"
cp "05_메타데이터/제목_후보 3개.txt" "$U/제목_3안.txt"; cp 05_메타데이터/설명란_업로드용.txt "$U/설명란.txt"; cp 05_메타데이터/고정댓글.txt "$U/고정댓글.txt"
cp 05_메타데이터/쇼츠_제목_설명.txt "$U/쇼츠_제목_설명.txt"; set -- $SH; if [ $# -eq 1 ]; then cp 08_완성영상/쇼츠_$1.mp4 "$U/쇼츠.mp4"; else i=1; for s in $SH; do cp 08_완성영상/쇼츠_$s.mp4 "$U/쇼츠$i.mp4"; i=$((i+1)); done; fi
[ -f pattern.txt ] && cp pattern.txt "$U/pattern.txt" || true   # 패턴 번호·이름 (patterns/pick_pattern.py)
[ -f 07_그래픽/썸네일_세로.png ] && cp 07_그래픽/썸네일_세로.png "$U/쇼츠_세로썸네일_1080x1920.png" || true
# 본편 mp4: Aside가 PC에서 받도록 90MB씩 나눠 커밋(main.mp4.part-aa…) + 원본 sha256
rm -f "$U"/main.mp4.part-*; cp 08_완성영상/완성영상_1080p.mp4 "$U/main.mp4"
(cd "$U" && sha256sum main.mp4 > main.mp4.sha256 && split -b 90M main.mp4 main.mp4.part- && rm main.mp4 && cat main.mp4.part-* | sha256sum -c <(sed 's/main.mp4/-/' main.mp4.sha256))
ls -la "$U"; echo "완료: $P/08_완성영상/완성영상_1080p.mp4 · $U"
