---
name: halo-3d-scene
description: Three.js 실시간 3D 장면(구름바다 위 눈 덮인 봉우리 사이의 콘크리트 링 레스토랑, 블루아워)과 그 장면에서 뽑는 드론 촬영 영상. GitHub Leonxlnx/halo-above-the-clouds(MIT) 원본. "구름 위 3D 장면", "드론샷", "halo 장면", "3D 오프닝·배경 영상"을 만들 때, 또는 실제 지형·볼륨 구름·하늘·블룸 후처리를 갖춘 Three.js 장면을 참고할 때 사용.
---

# Halo Above the Clouds (3D 장면 · 드론 영상)

- 원본은 https://github.com/Leonxlnx/halo-above-the-clouds (MIT)이다.
- 이 폴더의 `project/`에 소스 전체가 있다. 장면 데이터(약 370MB)와 node_modules는 넣지 않았다.
- 리눅스용으로 고친 곳이 하나 있다. `tools/shot.mjs`에서 환경변수 `SOFT_GL=1`을 주면 SwiftShader 소프트웨어 WebGL로 돈다.

## 무엇이 들어 있나
- **지형**: 브리엔처 로트호른(스위스)의 실제 고도 데이터를 쓴다. 240km 원경부터 0.39m 근경까지 겹쳐 쌓았다. 눈과 바위는 Poly Haven 텍스처로 칠한다.
- **링 구조물**: 지름 110m 링 레스토랑, 다리 2개, 유리 파빌리온이 있다. 조명은 LED와 창문 빛이다.
- **구름**: 볼륨 레이마칭으로 그린 곡면 구름바다다. 아래에서 마을 불빛이 비친다.
- **하늘**: CC0 HDRI 2개를 구운 하늘 돔과 박명 대기 원근이 있다.
- **계곡 불빛**: 마을과 도로 불빛 약 11만 7천 개가 호수에 비친다.
- **후처리**: HDR 블룸, 필름 그레이드, 그레인.
- **영상**: `src/timeline.js`에 45초, 11컷 자유비행 카메라 경로가 있다.
- **시점**: `src/views.js`에 카메라 시점이 있다. 실시간 뷰어에서는 숫자키 1~9, 0, −로 고른다.

## 준비
```bash
bash video-studio/setup_halo.sh   # /home/user/ext/halo 설치, 데이터 받기, 개발 서버(5173) 실행
```

## 프레임 렌더 (이 클라우드: GPU 없음)
```bash
cd /home/user/ext/halo
SOFT_GL=1 CHROME=/opt/pw-browsers/chromium-1194/chrome-linux/chrome \
  node tools/render.mjs --out out/clip --w 1920 --h 1080 --K 1 --jpg --start 300 --end 449   # 10~15초 구간
ffmpeg -framerate 30 -i out/clip/f_%05d.jpg -c:v libx264 -pix_fmt yuv420p -crf 18 clip.mp4
```
- 30fps 기준이다. 프레임 번호 = 초 × 30. `--times 2,15.5`를 주면 그 시각의 한 장만 렌더한다.
- 속도는 960×540, K=1에서 한 장에 약 48초다(2026-11-06 실측). 1080p는 그 약 4배다.
  - 45초 전체(1350장)는 이 환경에서 18시간 이상 걸린다. 오프닝용 3~5초 클립만 뽑는다.
  - `--K 4~8`(모션 블러·안티에일리어싱)은 GPU 있는 PC에서만 쓴다. README 기준 Radeon 780M에서 K 8이 한 장에 5초다.
- 렌더는 이미 있는 프레임을 건너뛴다. 끊겨도 같은 명령으로 이어 간다.

## 우리 영상에서 쓰는 법
- 경제 영상의 오프닝, 챕터 사이 전환, "구름 위", "꼭대기", "불확실성의 안개" 같은 은유 장면의 배경 클립으로 쓴다. 장면 종류는 `clip`이다.
- 카메라 경로를 바꾸려면 `src/timeline.js`의 SHOTS를 새로 쓰고, 시점을 바꾸려면 `src/views.js`를 바꾼다.
- 시간대나 색감은 `src/post.js`의 그레이드와 `src/config.js`에서 바꾼다.
- 고정 규칙은 그대로 지킨다.
  - 목소리는 여의도남자, 캐릭터는 여의도 개미다.
  - 자막은 편집 규칙집을 따른다.
  - 썸네일은 사이버·3D(`tools/thumb_cyber.py`)다.
  - 이 장면은 배경으로만 쓴다.
- 출처는 설명란에 적는다: "3D 장면: Leonxlnx/halo-above-the-clouds (MIT)". 하늘 HDRI와 텍스처는 Poly Haven CC0다.

## 함정
- 개발 서버(`npx vite --port 5173`)가 켜져 있어야 렌더된다. 끝나면 끈다. pid를 찾아 kill하고, `pkill -f`는 쓰지 않는다.
- 첫 로드에 셰이더 컴파일이 오래 걸린다. 렌더 스크립트가 `APP.ready`까지 기다린다.
- 디스크가 빠듯하다. 데이터 370MB와 node_modules 170MB를 다 쓰면 `/home/user/ext/halo`를 지운다. `setup_halo.sh`로 다시 만들 수 있다.
