#!/usr/bin/env bash
# 새 롱폼 폴더: [PATTERN_ONLY=1,3] bash 새편.sh <편이름>  (패턴 엔진 patterns/engine 복사 + 패턴 뽑기)  (보도·데이터 맞춤 대본형, 가락_경매시간 도구 복사)
set -e; C="$(cd "$(dirname "$0")" && pwd)"; V="$C/../.."; P="$V/$1"; T="$V/가락_경매시간"; G="$V/가락_시세보는법"
mkdir -p "$P"/{00_data,01_대본,02_음성,03_장면,05_메타데이터,07_그래픽,08_완성영상,09_소재/img_final}
cp "$T"/01_대본/check_sub_numbers.py "$C"/make_조사표.py "$P/01_대본/"
E=/home/user/kimhyeoncheol/.claude/skills/ranking-video/patterns; cp "$E"/engine/{build_hf.py,mix_audio.py,yieldfx.py,build_shorts.py} "$P/03_장면/"
cp "$T"/02_qa_tts.py "$T"/05_make_meta.py "$P/"; cp "$E"/engine/make_thumb.py "$P/07_그래픽/"
python3 "$E/pick_pattern.py" "$P" ${PATTERN_ONLY:+--only $PATTERN_ONLY}   # 패턴 랜덤(직전 2편 제외), PATTERN_ONLY=1,3 처럼 후보 제한
echo '{"note":"보도·데이터 맞춤 대본 — prices.lock은 calc 단계 생략용"}' > "$P/00_data/prices.lock"
echo "$P"
