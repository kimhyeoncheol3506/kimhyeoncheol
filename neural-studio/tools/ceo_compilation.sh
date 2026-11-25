#!/bin/bash
# CEO 본편 여러 편 → 몰아보기 1편 (본편은 저장소 git 객체에서 바로 흘려 넣음: 디스크 절약)
# 사용: ceo_compilation.sh <재료폴더(card01.png…)> <출력 mp4> 1 2 3 …(편 번호)
set -e
A=$1; OUT=$2; shift 2; EPS=("$@"); R=/home/user/kimhyeoncheol
cd $R; rm -f $A/fifo*; args=(); fc=""; k=0
for n in "${EPS[@]}"; do
  c=$(printf %02d $n); args+=(-loop 1 -framerate 30 -t 3 -i $A/card$c.png); vi=$k; k=$((k+1))
  mkfifo $A/fifo$c; args+=(-thread_queue_size 4096 -i $A/fifo$c); ei=$k; k=$((k+1))
  ( for f in $(git ls-tree -r HEAD --name-only release_upload/ceo/ep$n | grep part | sort); do git show HEAD:$f; done > $A/fifo$c ) &
  fc+="[$vi:v]scale=1920:1080,fps=30,format=yuv420p,setsar=1,fade=t=in:st=0:d=0.3,fade=t=out:st=2.7:d=0.3[cv$c];anullsrc=r=48000:cl=stereo,atrim=0:3,asetpts=N/SR/TB[ca$c];"
  fc+="[$ei:v]scale=1920:1080,fps=30,format=yuv420p,setsar=1[ev$c];[$ei:a]aresample=48000,aformat=channel_layouts=stereo[ea$c];"
done
cat=""; for n in "${EPS[@]}"; do c=$(printf %02d $n); cat+="[cv$c][ca$c][ev$c][ea$c]"; done
fc+="${cat}concat=n=$((${#EPS[@]}*2)):v=1:a=1[v][a]"
nice ffmpeg -v error -y "${args[@]}" -filter_complex "$fc" -map "[v]" -map "[a]" -c:v libx264 -preset veryfast -crf 27 -tune animation \
  -c:a aac -b:a 160k -movflags +faststart "$OUT"
wait; rm -f $A/fifo*
