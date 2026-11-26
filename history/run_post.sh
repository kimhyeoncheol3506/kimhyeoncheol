#!/usr/bin/env bash
# 롱폼 후반 작업: check → sfx_bgm → landscape(16:9) → 45MB 이하 2패스 → output/longform/
# 사용: bash history/run_post.sh L02_척준경 2
set -euo pipefail
EP="$1"; N="$2"
ROOT=/home/user/kimhyeoncheol
T=$ROOT/.claude/skills/mystery-cartoon/kits/toon2d
H=$ROOT/.claude/skills/history-truth-shorts/tools
D=$ROOT/history/$EP
S=/tmp/claude-0/-home-user-kimhyeoncheol/4c81a112-a5ef-5cff-97f3-1be743fc4e06/scratchpad
cd "$D"
python3 $T/t2d.py check . 2>&1 | grep -v Fontconfig | tail -4
python3 $H/sfx_bgm.py . --ep "$N" 2>&1 | grep -E "효과음|OUT"
CH=chapters_w.json; [ -f $CH ] || CH=chapters.json
python3 $H/landscape.py . --video final_sfx.mp4 --chapters $CH --out final_169.mp4
O=$ROOT/output/longform/$EP.mp4
rm -f "$O" $S/${EP}p*
nice -n 5 ffmpeg -v error -y -i final_169.mp4 -map 0:v -c:v libx264 -b:v 600k -pass 1 -passlogfile $S/${EP}p -preset medium -an -f null /dev/null
nice -n 5 ffmpeg -v error -y -i final_169.mp4 -map 0:v -map 0:a -dn -c:v libx264 -b:v 600k -pass 2 -passlogfile $S/${EP}p -preset medium -c:a aac -b:a 128k -movflags +faststart "$O"
cp factsheet.md $ROOT/output/longform/${EP}_factsheet.md
cp audio_credits.txt $ROOT/output/longform/${EP}_audio_credits.txt
ffprobe -v error -show_entries format=duration,size -of compact "$O"
echo "POST DONE $EP"
