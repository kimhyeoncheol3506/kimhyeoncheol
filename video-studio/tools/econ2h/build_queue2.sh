#!/usr/bin/env bash
# 33편 렌더·조립 대기열 v2: 지금 대사와 정확히 맞는 음성이 있는 장면만 렌더
cd /home/user/kimhyeoncheol/video-studio
while true; do
  left=0
  for n in 01 02 03 04 05 06 07 08; do
    D=projects/20261106-econ2h-p$n
    [ -f $D/project.json ] || { left=1; continue; }
    [ -f $D/output/video.mp4 ] && continue
    left=1
    ids=$(python3 tools/econ2h/ready_ids.py $D)
    if [ -n "$ids" ]; then echo "$(date +%H:%M) render p$n $ids"; HF_ROOT=/home/user/hf/crisis python3 $D/build.py render $ids 2>&1 | grep -E "^s[0-9]|Error|Traceback"; fi
    total=$(python3 -c "import json;print(len(json.load(open('$D/project.json'))['scenes']))")
    clips=$(ls $D/clips/s*.mp4 2>/dev/null | wc -l)
    tts_busy=$(ps -eo args | grep -c "[q]wen_cloud.py $D/")
    missing=$(python3 -c "
import json,os,sys;sys.path.insert(0,'.');from studio.keys import raw_name
p=json.load(open('$D/project.json'));print(sum(1 for s in p['scenes'] if not os.path.exists('$D/audio/'+raw_name(s))))")
    if [ "$missing" = "0" ] && [ "$clips" -ge "$total" ] && [ "$tts_busy" = "0" ] && [ -f $D/READY ]; then
      echo "$(date +%H:%M) assemble p$n"
      ~/.cache/yeouido-tts/venv/bin/python voice/align.py $D/project.json > $D/align.log 2>&1
      python3 make_video.py $D/project.json --voice cloud --no-package > $D/make.log 2>&1 && python3 tools/verify_video.py $D/output/video.mp4 | tail -1
      rm -f $D/clips/parts/*.mp4
    fi
  done
  [ "$left" = "0" ] && { echo "all parts assembled"; break; }
  sleep 60
done
