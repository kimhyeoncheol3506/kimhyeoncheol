#!/usr/bin/env bash
# usage: bash forensics.sh <reference-video> [outdir]   (run ONCE per reference; then LOOK at the sheets)
set -e; V="$1"; O="${2:-analysis/$(basename "${V%.*}")}"; mkdir -p "$O"; D="$(cd "$(dirname "$0")" && pwd)"
ffprobe -v error -show_format -show_streams -of json "$V" > "$O/probe.json"
ffmpeg -hide_banner -i "$V" -af loudnorm=print_format=json -f null - 2> "$O/loudnorm.txt" || true
ffmpeg -hide_banner -i "$V" -af silencedetect=noise=-38dB:d=0.1 -f null - 2> "$O/silence.txt" || true
python3 "$D/scene_cuts.py" "$V" "$O/scenes.json"
python3 "$D/contact_sheets.py" "$V" "$O/sheets" --fps 1
python3 "$D/palette.py" "$V" "$O/palette.json"
python3 "$D/motion_stats.py" "$V" "$O/motion.json"
python3 "$D/audio_onsets.py" "$V" "$O/audio_onsets.json" || true
python3 "$D/summarize.py" "$O"
