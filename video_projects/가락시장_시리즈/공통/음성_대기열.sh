#!/usr/bin/env bash
# 음성 대기열: 대기열.txt에 적힌 편을 차례로(한 번에 하나) 여의도남자 1.12로 생성. 이미 만든 문장은 건너뜀. 다른 음성 작업이 돌고 있으면 기다림.
Q=/home/user/kimhyeoncheol/video_projects/가락시장_시리즈/공통/대기열.txt; V=/home/user/kimhyeoncheol/video_projects
PY=$HOME/.cache/shorts-tts/venv/bin/python; SK=/home/user/kimhyeoncheol/.claude/skills/ranking-video
while true; do
  N=$(grep -v '^#' "$Q" | while read -r p; do [ -n "$p" ] && [ ! -f "$V/$p/02_음성/.done" ] && echo "$p" && break; done)
  [ -z "$N" ] && { echo "대기열 비었음 $(date)"; sleep 60; continue; }
  while pgrep -f make_voice_yeouido.py >/dev/null; do sleep 20; done
  cd "$V/$N" && echo "== $N 시작 $(date)" && \
  "$PY" "$SK/voice/make_voice_yeouido.py" 01_대본/대본데이터.json 02_음성 --voice 여의도남자 --speed 1.12 >> 02_음성_생성.log 2>&1 && \
  for s in $(ls 01_대본/short*.json 2>/dev/null | xargs -n1 basename | sed 's/.json//'); do "$PY" "$SK/voice/make_voice_yeouido.py" 01_대본/$s.json 02_음성_쇼츠/$s --voice 여의도남자 --speed 1.12 >> 02_음성_생성.log 2>&1; done && \
  touch 02_음성/.done && echo "== $N 끝 $(date)"
done
