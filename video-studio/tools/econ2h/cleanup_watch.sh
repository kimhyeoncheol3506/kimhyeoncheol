#!/usr/bin/env bash
# 부 조립이 끝나면(chapters.json 생성) 점검 후 장면 클립·48k 변환 음성 삭제(디스크 확보). 끝난 부 번호를 출력하고 종료.
P=/home/user/kimhyeoncheol/video-studio/projects
end=$((SECONDS+6300))
while [ $SECONDS -lt $end ]; do
  for i in 1 2 3 4 5 6 7 8; do
    d=$P/20261106-econ2h-p0$i
    if [ -f $d/output/chapters.json ] && [ ! -f $d/CLEANED ]; then
      r=$(python3 /home/user/kimhyeoncheol/video-studio/tools/verify_video.py $d/output/video.mp4 2>&1 | tail -1)
      echo "p$i verify: $r"
      if echo "$r" | grep -q "FAIL 0"; then rm -f $d/clips/s*.mp4 $d/audio/*_v2*.wav; touch $d/CLEANED; echo "p$i cleaned"; fi
      exit 0
    fi
  done
  q=$(ps -eo args | grep -cE "[t]ts_queue.sh|[b]uild_queue2.sh")
  [ "$q" -lt 2 ] && { echo "QUEUE_DOWN $q"; exit 0; }
  sleep 60
done
echo "TIMEOUT"
