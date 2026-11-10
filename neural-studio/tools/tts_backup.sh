#!/usr/bin/env bash
# 긴 영상 더빙 중 컨테이너가 바뀌어도 음성 캐시를 잃지 않도록, output/<slug>/_work/tts 를 저장소의 cache_backup/<slug>/ 로 복사해 주기적으로 커밋·푸시한다.
# 사용: bash tools/tts_backup.sh <slug> [간격초=1800]   ·  되살리기: bash tools/tts_backup.sh <slug> restore
set -u
cd "$(dirname "$0")/.."
SLUG=$1; ARG=${2:-1800}
SRC=output/$SLUG/_work/tts; DST=cache_backup/$SLUG
if [ "$ARG" = restore ]; then mkdir -p "$SRC"; cp -n "$DST"/* "$SRC"/ 2>/dev/null; echo "복원: $(ls "$SRC" | wc -l)개"; exit 0; fi
BR=$(git rev-parse --abbrev-ref HEAD)
while true; do
  mkdir -p "$DST"
  if [ -d "$SRC" ]; then cp -n "$SRC"/* "$DST"/ 2>/dev/null; fi
  if [ -n "$(git status --porcelain -- "$DST")" ]; then
    git add -- "$DST" && git commit -q -m "음성 캐시 백업: $SLUG ($(ls "$DST" | wc -l)개)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01FimgvnFwUXoVfoVUHJw6eG" -- "$DST" && \
    for i in 1 2 3; do git push -q origin "$BR" && break; sleep $((i*5)); git pull -q --no-rebase origin "$BR"; done
  fi
  pgrep -f "make_editorial.py projects/$SLUG" >/dev/null || [ ! -d "$SRC" ] || { echo "빌드 끝 → 백업 종료"; break; }
  sleep "$ARG"
done
