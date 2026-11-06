#!/usr/bin/env bash
# halo-3d-scene 스킬: Three.js 실시간 3D 장면(구름 위 링 레스토랑) 준비. /home/user/ext/halo 에 설치 (node_modules ~170MB + 장면 데이터 ~370MB)
set -e
S=/home/user/kimhyeoncheol/.claude/skills/halo-3d-scene/project
H=/home/user/ext/halo
mkdir -p "$H"
[ -f "$H/package.json" ] || cp -r "$S/." "$H/"
cd "$H"
[ -d node_modules ] || npm install --no-audit --no-fund --loglevel=error
[ -d data ] || npm run data
if ! curl -s -m 2 localhost:5173 >/dev/null; then nohup npx vite --port 5173 > "$H/vite.log" 2>&1 & for i in $(seq 1 30); do curl -s -m 2 localhost:5173 >/dev/null && break; sleep 2; done; fi
echo "준비 완료: $H (개발 서버 http://localhost:5173)"
