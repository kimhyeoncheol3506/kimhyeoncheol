#!/usr/bin/env bash
# usage: bash env_report.sh [out.md]  -> capabilities of the environment Claude is running in (never assume the user's PC)
out="${1:-ENV-REPORT.md}"
{
echo "# ENV REPORT ($(date -u +%FT%TZ))"
echo "## System"; echo "cores: $(nproc 2>/dev/null || echo ?)"; free -m 2>/dev/null | sed -n 2p; df -h . | tail -1; uname -sr
echo "## GPU"; if command -v nvidia-smi >/dev/null 2>&1; then nvidia-smi -L; else echo "no NVIDIA GPU detected -> assume CPU-only rendering"; fi
echo "## Tools"; for c in node npm ffmpeg ffprobe python3 pip3 git; do printf "%s: " $c; if command -v $c >/dev/null 2>&1; then $c --version 2>&1 | head -1; else echo MISSING; fi; done
echo "## Python libs"; python3 - <<'P'
for m in ("numpy","PIL","cv2","librosa","scipy"):
    try: __import__(m); print(m,"ok")
    except Exception: print(m,"missing")
P
echo "## Network (HTTP status; 000 = blocked/unreachable)"
for h in registry.npmjs.org pypi.org raw.githubusercontent.com github.com fonts.googleapis.com huggingface.co; do code=$(curl -s -m 6 -o /dev/null -w "%{http_code}" -I "https://$h" 2>/dev/null || true); echo "$h -> ${code:-000}"; done
echo "## Chromium"; ls -d /opt/pw-browsers/* 2>/dev/null || (command -v chromium chromium-browser google-chrome 2>/dev/null || echo "none found (Remotion downloads its own if network allows)")
} > "$out"; cat "$out"
