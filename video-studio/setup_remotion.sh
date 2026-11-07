#!/usr/bin/env bash
# Remotion 최소 프로젝트 (숫자·데이터 인포그래픽용). /home/user/ext/remotion-test (~480MB node_modules)
set -e
T=/home/user/ext/remotion-test
mkdir -p $T/src
cp -n /home/user/kimhyeoncheol/video-studio/tools/motion_tests/remotion-counter/package.json $T/ 2>/dev/null || true
cp -n /home/user/kimhyeoncheol/video-studio/tools/motion_tests/remotion-counter/src/* $T/src/ 2>/dev/null || true
cd $T
[ -d node_modules/remotion ] || npm install --no-audit --no-fund --loglevel=error remotion@4.0.540 @remotion/cli@4.0.540 react@18.3.1 react-dom@18.3.1 typescript
echo "렌더: cd $T && npx remotion render src/index.ts <Composition> out/x.mp4 --browser-executable=\$(ls -d /opt/pw-browsers/chromium_headless_shell-*/*/ | head -1)headless_shell"
