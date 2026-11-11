#!/usr/bin/env bash
# 모델 1 더빙 중 컨테이너가 바뀌어도 음성을 잃지 않도록 projects/<폴더>/audio/*.wav 를 cache_backup/<폴더>/ 로 복사해 주기적으로 커밋·푸시한다.
# 사용: bash tools/audio_backup.sh <폴더> [간격초=1800]   ·  되살리기: bash tools/audio_backup.sh <폴더> restore
set -u
cd "$(dirname "$0")/.."
P=$1; ARG=${2:-1800}
SRC=projects/$P/audio; DST=cache_backup/$P
if [ "$ARG" = restore ]; then mkdir -p "$SRC"; cp -n "$DST"/*.wav "$SRC"/ 2>/dev/null; echo "복원: $(ls "$SRC" | wc -l)개"; exit 0; fi
BR=$(git rev-parse --abbrev-ref HEAD)
while true; do
  mkdir -p "$DST"
  [ -d "$SRC" ] && find "$SRC" -maxdepth 1 -name 's[0-9]*_*.wav' ! -name '*_x*' ! -name '*_silent*' -exec cp -n {} "$DST"/ \;
  if [ -n "$(git status --porcelain -- "$DST")" ]; then
    git add -- "$DST" && git commit -q -m "음성 백업: $P ($(ls "$DST" | wc -l)개)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01FimgvnFwUXoVfoVUHJw6eG" -- "$DST" && \
    for i in 1 2 3; do git push -q origin "$BR" && break; sleep $((i*5)); git pull -q --no-rebase origin "$BR"; done
  fi
  ps -eo args | grep -q "[q]wen_cloud.py projects/$P" || { echo "더빙 끝 → 백업 종료"; break; }
  sleep "$ARG"
done
