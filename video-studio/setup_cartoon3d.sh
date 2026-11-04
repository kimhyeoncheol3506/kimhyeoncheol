#!/usr/bin/env bash
# cartoon-3d-short 스킬용 Remotion 프로젝트를 /home/user/ext/remotion-shorts 에 만든다 (node_modules ~350MB).
# 버전 고정 이유: React 19 + @react-three/fiber 9 + @react-three/postprocessing 3 조합은 이 컨테이너의
# 소프트웨어 WebGL에서 후처리(잉크·렌즈블러)를 거치면 화면이 통째로 비었다. React 18 + fiber 8 + postprocessing 2로 정상.
set -e
S=/home/user/kimhyeoncheol/.claude/skills/cartoon-3d-short/templates
P=/home/user/ext/remotion-shorts
mkdir -p "$P/src/videos" "$P/scripts" "$P/public/bridge/kenney" /home/user/ext/remotion-tmp
cp "$S/project/package.json" "$S/project/tsconfig.json" "$P/"
cp "$S/project/index.ts" "$S/project/Root.tsx" "$P/src/"
[ -d "$P/src/videos/bridge" ] || cp -r "$S/bridge" "$P/src/videos/bridge"
cp "$S/scripts/"* "$P/scripts/"
cd "$P" && npm install --no-audit --no-fund --loglevel=error --legacy-peer-deps
echo "준비 완료: $P"
echo "스틸 예: cd $P && CHROME_PATH=\$(ls -d /opt/pw-browsers/chromium_headless_shell-*/*/)headless_shell REMOTION_TMP=/home/user/ext/remotion-tmp node scripts/bridge-stills.mjs out/test/x_ 100,900 0.5"
