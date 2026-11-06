#!/usr/bin/env bash
# 33편(2시간) 음성 대기열: READY 표시가 있는 부를 1→8 순서로 TTS (장면 캐시라 끊겨도 이어짐)
cd /home/user/kimhyeoncheol/video-studio
while true; do
  pending=0
  for n in 01 02 03 04 05 06 07 08; do
    D=projects/20261106-econ2h-p$n
    [ -f $D/READY ] || { pending=1; continue; }
    total=$(python3 -c "import json;print(len(json.load(open('$D/project.json'))['scenes']))")
    have=$(ls $D/audio 2>/dev/null | grep -v '_v2' | grep -c '\.wav$')
    if [ "$have" -lt "$total" ]; then
      echo "$(date +%H:%M) TTS p$n ($have/$total)"
      ~/.cache/yeouido-tts/venv/bin/python voice/qwen_cloud.py $D/project.json >> $D/tts.log 2>&1
      pending=1
    fi
  done
  [ "$pending" = "0" ] && { echo "all TTS done"; break; }
  sleep 60
done
