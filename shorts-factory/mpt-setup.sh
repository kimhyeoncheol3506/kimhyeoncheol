#!/usr/bin/env bash
# MoneyPrinterTurbo 한국어 준비 (처음 한 번)
#  - 서브모듈 내려받기
#  - 한글 자막 폰트(Pretendard Bold) 넣기
#  - config.toml 만들기: Claude(Anthropic)로 대본 작성, Pexels 무료 영상 사용
#
#   ANTHROPIC_API_KEY=sk-ant-... PEXELS_API_KEY=... bash shorts-factory/mpt-setup.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MPT="$HERE/MoneyPrinterTurbo"

git -C "$HERE/.." submodule update --init shorts-factory/MoneyPrinterTurbo

cp "$HERE/assets/fonts/Pretendard-Bold.ttf" "$MPT/resource/fonts/"

if [[ -f "$MPT/config.toml" ]]; then
  echo "config.toml 이 이미 있어 건드리지 않았습니다: $MPT/config.toml"
else
  cp "$MPT/config.example.toml" "$MPT/config.toml"
  # 줄 단위로만 바꾼다 (키 값은 비어 있으면 그대로 둠)
  sed -i.bak \
    -e 's|^llm_provider = .*|llm_provider = "anthropic"|' \
    -e "s|^anthropic_api_key = \"\"|anthropic_api_key = \"${ANTHROPIC_API_KEY:-}\"|" \
    -e "s|^pexels_api_keys = \[\]|pexels_api_keys = [${PEXELS_API_KEY:+\"$PEXELS_API_KEY\"}]|" \
    "$MPT/config.toml"
  rm -f "$MPT/config.toml.bak"
  echo "config.toml 을 만들었습니다: $MPT/config.toml"
fi

cat <<'EOF'

준비 끝. 실행:
  cd shorts-factory/MoneyPrinterTurbo
  docker compose up            # 또는: sh webui.sh  (Python 3.11+ / uv 필요)
  → 브라우저에서 http://localhost:8501

웹 화면에서 고를 것:
  영상 언어  ko-KR
  목소리     ko-KR-SunHiNeural-Female (여) / ko-KR-InJoonNeural-Male (남)
  자막 폰트  Pretendard-Bold.ttf
  화면 비율  9:16 (쇼츠)
EOF
