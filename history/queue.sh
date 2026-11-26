#!/usr/bin/env bash
# 롱폼 제작 큐: words → auto_storyboard → plan → (자막 비움) → render → join → run_post
# 사용: bash history/queue.sh L03_화랑세기:3 L04_국호:4 ...
ROOT=/home/user/kimhyeoncheol
T=$ROOT/.claude/skills/mystery-cartoon/kits/toon2d
H=$ROOT/.claude/skills/history-truth-shorts/tools
for item in "$@"; do
  EP=${item%%:*}; N=${item##*:}; D=$ROOT/history/$EP
  cd "$D" || continue
  echo "=== $EP start $(date +%H:%M)"
  [ -f timings.json ] || { echo "no timings $EP"; continue; }
  python3 $T/t2d.py words . --from timings.json --force 2>&1 | tail -1
  python3 $H/auto_storyboard.py . || { echo "sb fail $EP"; continue; }
  python3 $T/t2d.py plan . 2>&1 | grep -v Fontconfig | tail -1
  python3 -c "import json;p=json.load(open('plan.json'));p['captions']=[];json.dump(p,open('plan.json','w'),ensure_ascii=False)"
  for i in $(seq 1 60); do python3 $T/t2d.py render . --workers 4 --budget 500 2>&1 | grep -v Fontconfig | tail -1 > render.log; grep -q DONE render.log && break; done
  python3 $T/t2d.py join . 2>&1 | tail -1
  bash $ROOT/history/run_post.sh "$EP" "$N" 2>&1 | tail -4
  echo "=== $EP end $(date +%H:%M)"
done
