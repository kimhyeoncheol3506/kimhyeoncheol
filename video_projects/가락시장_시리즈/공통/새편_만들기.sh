#!/usr/bin/env bash
# 가락시장 시리즈 새 편 폴더 만들기: bash 새편_만들기.sh <편이름>  → video_projects/<편이름>/ (공통 스크립트 복사, topic.json은 직접 작성)
set -e; C="$(cd "$(dirname "$0")" && pwd)"; V="$C/../.."; P="$V/$1"; K="$V/김장배추"
mkdir -p "$P"/{00_data,01_대본,02_음성,03_장면,05_메타데이터,07_그래픽,08_완성영상,09_소재/img_final}
cp "$C"/build_data.py "$C"/build_short.py "$C"/make_조사표.py "$K"/01_대본/check_sub_numbers.py "$P/01_대본/"
cp "$K"/03_장면/{build_hf.py,mix_audio.py,yieldfx.py} "$C"/build_shorts.py "$P/03_장면/"
cp "$K"/02_qa_tts.py "$C"/05_make_meta.py "$P/"; cp "$C"/make_thumb.py "$P/07_그래픽/"
echo "$P"
