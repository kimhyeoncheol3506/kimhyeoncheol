#!/usr/bin/env bash
# 렌더 대기열: 대기열.txt 순서대로, 음성이 끝난(02_음성/.done) 편을 하나씩 롱폼_만들기.sh --skip-voice 로 렌더·검수·upload_ready 정리. 끝난 편은 upload_ready/<편>/main.mp4.sha256 로 판단.
Q=/home/user/kimhyeoncheol/video_projects/가락시장_시리즈/공통/대기열.txt; V=/home/user/kimhyeoncheol/video_projects; U=/home/user/kimhyeoncheol/upload_ready
while true; do
  N=$(grep -v '^#' "$Q" | while read -r p; do [ -n "$p" ] && [ -f "$V/$p/02_음성/.done" ] && [ ! -f "$U/$p/main.mp4.sha256" ] && [ ! -f "$V/$p/.render_fail" ] && echo "$p" && break; done)
  [ -z "$N" ] && { sleep 60; continue; }
  echo "== $N 렌더 시작 $(date)"
  (cd "$V/$N" && python3 07_그래픽/make_thumb.py > /dev/null 2>&1)
  SHV=""; [ -f "$V/$N/00_data/shorts.txt" ] && SHV="$(cat "$V/$N/00_data/shorts.txt")"; if (cd "$V" && SHORTS="${SHV:-short1}" bash 롱폼_만들기.sh "$N" "$N" --skip-voice > "$N/make.log" 2>&1); then echo "== $N 렌더 끝 $(date)"; else echo "== $N 렌더 실패 $(date)"; touch "$V/$N/.render_fail"; fi
done
