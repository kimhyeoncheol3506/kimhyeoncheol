#!/usr/bin/env bash
# 33편 렌더·조립 대기열: 음성이 나온 장면부터 렌더, 한 부가 다 되면 정렬→조립→점검
cd /home/user/kimhyeoncheol/video-studio
while true; do
  left=0
  for n in 01 02 03 04 05 06 07 08; do
    D=projects/20261106-econ2h-p$n
    [ -f $D/project.json ] || { left=1; continue; }
    [ -f $D/output/video.mp4 ] && continue
    left=1
    ids=""
    for f in $(find $D/audio -maxdepth 1 -name 's[0-9][0-9][0-9]_*.wav' ! -name '*_v2*' -mmin +0.5 2>/dev/null); do
      id=$(basename $f | cut -d_ -f1); [ -f $D/clips/$id.mp4 ] || ids="$ids,$id"
    done
    ids=${ids#,}
    if [ -n "$ids" ]; then echo "$(date +%H:%M) render p$n $ids"; HF_ROOT=/home/user/hf/crisis python3 $D/build.py render $ids 2>&1 | grep -E "^s[0-9]|Error|Traceback"; fi
    total=$(python3 -c "import json;print(len(json.load(open('$D/project.json'))['scenes']))")
    clips=$(ls $D/clips/s*.mp4 2>/dev/null | wc -l)
    tts_busy=$(ps -eo args | grep -c "[q]wen_cloud.py $D/")
    if [ "$clips" -ge "$total" ] && [ "$tts_busy" = "0" ] && [ -f $D/READY ]; then
      echo "$(date +%H:%M) assemble p$n"
      ~/.cache/yeouido-tts/venv/bin/python voice/align.py $D/project.json > $D/align.log 2>&1
      python3 make_video.py $D/project.json --voice cloud --no-package > $D/make.log 2>&1 && python3 tools/verify_video.py $D/output/video.mp4 | tail -1
      rm -f $D/clips/parts/*.mp4
    fi
  done
  [ "$left" = "0" ] && { echo "all parts assembled"; break; }
  sleep 60
done
