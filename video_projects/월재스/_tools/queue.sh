#!/bin/bash
# 준비된 에피소드부터 make_episode.py 로 차례로 제작. 끝난 편은 <작업폴더>/DONE, 실패는 FAIL.
cd "$(dirname "$0")/.."
SCR=${WOLJE_SCRATCH:-/tmp/claude-0/-home-user-kimhyeoncheol/44362ec3-a63a-5c3d-aec2-d8ee4bace401/scratchpad/wolje}
Q="04_환율IMF수준:money 05_초대형IPO:basic 06_테마주폭락:tension 07_반도체와구글:basic 08_호르무즈와기름값:tension 09_약세장:tension 10_버핏투자법:basic 11_사모신용:tension 12_레버리지ETF:money 13_연준의장교체:money"
while true; do
  left=0; ran=0
  for it in $Q; do e=${it%%:*}; p=${it##*:}; W=$SCR/$e
    [ -f $W/DONE ] || [ -f $W/FAIL ] && continue
    left=1
    if [ -f $e/script/01_본편.txt ] && [ -f $e/research/thumbs.json ] && [ -f $e/research/clips.json ] && [ -f ../../release/$e/설명란_템플릿.txt ] && [ -f $e/research/READY ]; then
      mkdir -p $W; echo "=== $(date +%H:%M) $e 시작 ($p)"
      if python3 _tools/make_episode.py $e --preset $p > $W/run.log 2>&1; then touch $W/DONE; tail -1 $W/run.log; else touch $W/FAIL; echo "!!! $e 실패"; tail -5 $W/run.log; fi
      ran=1; break
    fi
  done
  [ $left = 0 ] && { echo ALLDONE; break; }
  [ $ran = 0 ] && sleep 60
done
