#!/usr/bin/env bash
# 8부 조립이 끝나면: 점검·정리 → 디스크 확보(manim-venv) → 8부 합치기(merge.py, 규칙집 마감 포함)
P=/home/user/kimhyeoncheol/video-studio/projects
cd /home/user/kimhyeoncheol/video-studio
until [ -f $P/20261106-econ2h-p08/output/chapters.json ]; do sleep 30; done
r=$(python3 tools/verify_video.py $P/20261106-econ2h-p08/output/video.mp4 2>&1 | tail -1); echo "p8 verify: $r"
echo "$r" | grep -q "FAIL 0" && { rm -f $P/20261106-econ2h-p08/clips/s*.mp4 $P/20261106-econ2h-p08/audio/*_v2*.wav; touch $P/20261106-econ2h-p08/CLEANED; }
rm -rf /home/user/ext/manim-venv
df -h /home/user | tail -1
echo "merge start $(date +%H:%M)"
python3 tools/econ2h/merge.py 2>&1 | tail -5
echo "merge end $(date +%H:%M)"
python3 tools/verify_video.py $P/20261106-econ2h/output/video.mp4 2>&1 | tail -11
df -h /home/user | tail -1
