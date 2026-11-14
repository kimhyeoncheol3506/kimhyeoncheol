# 썸네일 '3D 대비형' 도구

채널 기본 썸네일 디자인(`docs/채널규칙_제목썸네일첫15초.md` 2-1, 기준 그림 `assets/thumbs/style_ref/3d_contrast_japan.webp`)을 설정 JSON 하나로 만든다.

```
cd neural-studio
python3 tools/thumb3d_contrast/make.py projects/oneshot_japan_parts/thumb3d.json assets/thumbs/oneshot_japan_thumb_3d.png --work <임시폴더>
#   --samples 40 (기본) · --threads 2 (기본, 다른 렌더와 CPU 나눠 쓰기) · --reuse (Blender 레이어 재사용, HTML 만 다시)
```

- `scene.py` (Blender 4.5, Cycles, 직교 카메라 1단위=100px): 남색 3D 제목 2줄, 빨강/남색 3D 숫자, 전→후 3D 화살표, 소품
  (coins cash peso building shield drums/oil pumpjack chart_down chart_up vault watch pill)을 투명 PNG + 위치 JSON 으로.
- `make.py`: Blender 렌더 → HTML 합성(흰 바탕·빨간 윗띠·유리 구슬·vs·꼬리표·개미 스티커·그림자) → Chrome 캡처 → 1280×720 + 샤픈.
- 설정 항목은 `make.py` 머리 주석. 예시: `projects/oneshot_{japan,swiss,argentina,saudi}_parts/thumb3d.json`.
- 한 장: Blender 약 1분 30초(40샘플, 2스레드, CPU 바쁠 때) + 합성 6초.
