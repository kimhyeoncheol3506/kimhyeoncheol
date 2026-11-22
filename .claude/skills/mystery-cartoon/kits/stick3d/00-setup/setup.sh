#!/usr/bin/env bash
# ONE-COMMAND SETUP (Claude runs this first). Idempotent. Works on Linux/Mac cloud containers; no GPU needed.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"; cd "$ROOT"
echo "== env report =="; bash tools/env_report.sh > ENV-REPORT.md 2>&1 || true; head -20 ENV-REPORT.md
command -v node >/dev/null || { echo "NODE MISSING: install Node 18+ (nvm install 22 / apt install nodejs npm) then rerun"; exit 1; }
command -v ffmpeg >/dev/null || { echo "ffmpeg missing: apt-get install -y ffmpeg (or brew install ffmpeg)"; exit 1; }
echo "== python libs =="; (python3 -m pip install -q pocketsphinx numpy pillow 2>&1 || python3 -m pip install -q --break-system-packages pocketsphinx numpy pillow 2>&1) | tail -1 || true
echo "== engine deps =="; cd engine && npm install --no-audit --no-fund --loglevel=error && cd ..
echo "== SFX library (synth, no downloads) =="; python3 tools/voice/make_sfx.py sfx >/dev/null && ls sfx | wc -l
echo "== render flags + benchmark =="
cd engine
GL=swangle; command -v nvidia-smi >/dev/null && GL=angle
echo "$GL" > ../.gl-flag
S=$(date +%s.%N); npx remotion still Main --frame=0 --gl=$GL --scale=0.5 --log=error --output=/tmp/_setup_test.png >/dev/null 2>&1 || { echo "still render FAILED with gl=$GL"; exit 1; }
E=$(date +%s.%N); echo "first still ok with --gl=$GL in $(echo "$E-$S"|bc)s"
echo "SETUP DONE. gl flag=$GL (CPU-only cloud: ~25-35 frames/min at 720x1280 on 4 cores; benchmark before planning)."
