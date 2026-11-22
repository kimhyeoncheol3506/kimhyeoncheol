#!/usr/bin/env bash
# usage: bash bench_render.sh <CompId> [engine_dir=engine]  -> seconds/frame at scale 0.5 and 1.0 (bundling time cancelled out). Use it to choose the technique rung.
C="$1"; cd "${2:-engine}"; t() { local s=$(date +%s.%N); npx remotion render "$C" /tmp/bench.mp4 --frames=0-$1 --scale=$2 --log=error >/dev/null 2>&1; echo "$(date +%s.%N) - $s" | bc; }
for sc in 0.5 1; do a=$(t 9 $sc); b=$(t 39 $sc); echo "scale $sc: $(echo "scale=3; ($b - $a)/30" | bc) s/frame (10 frames took ${a}s, 40 frames ${b}s)"; done
