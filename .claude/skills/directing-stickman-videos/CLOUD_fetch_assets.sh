#!/usr/bin/env bash
# directing-stickman-videos 무거운 미디어(이미지·영상·음원, 약 540MB)를 원본 저장소의 고정 커밋에서 복원한다.
# 깃에는 SKILL.md·references·scripts·json 만 커밋하고 미디어는 .gitignore (용량 때문). 새 세션에서 한 번 실행.
# 사용: bash .claude/skills/directing-stickman-videos/CLOUD_fetch_assets.sh
set -euo pipefail
REV=1028782a   # 2026-11-24 가져온 커밋 (kaomei/stickman-video-director)
HERE="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git clone -q --filter=blob:none --sparse https://github.com/kaomei/stickman-video-director.git "$TMP/svd"
git -C "$TMP/svd" sparse-checkout set skills/directing-stickman-videos/assets
git -C "$TMP/svd" checkout -q "$REV" 2>/dev/null || echo "고정 커밋을 못 찾아 최신 main 으로 진행"
cp -an "$TMP/svd/skills/directing-stickman-videos/assets/." "$HERE/assets/"
du -sh "$HERE/assets"
echo "ASSETS OK"
