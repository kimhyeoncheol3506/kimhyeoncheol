---
name: blender-3d
description: "Blender를 화면 없이(headless) 돌려 3D 장면 클립을 렌더한다 — 회전하는 금색 ₩ 코인, 자라 오르는 3D 막대 차트 템플릿이 들어 있다. 훅·챕터 표지·썸네일용 3D 오브젝트, 입체 데이터 장면에 쓴다. '3D', '블렌더', 'Blender', '코인 돌아가는', '입체 차트' 요청에 사용."
---

# Blender 3D

```bash
blender -b -P .claude/skills/blender-3d/scripts/render3d.py -- <템플릿> <출력폴더> [옵션]
```
| 템플릿 | 내용 | 주요 옵션 |
|---|---|---|
| `coin` | 금색 ₩ 코인이 돌면서 다가온다(규칙집 다크 배경) | `--seconds 4` |
| `bars` | 3D 막대가 차례로 튀어 오르고 위에 값이 뜬다. 마지막 막대는 빨강(R-L6) | `--values 128,330,500,1050 --labels 1월,3월,5월,6월` |

공통 옵션: `--res 1920x1080` `--fps 30` `--samples 32` `--gpu`(PC) `--denoise 1`(공식 Blender에서만) `--font <otf>`(기본 Pretendard ExtraBold)
결과: `<출력폴더>/frames/####.png` + `<출력폴더>/<템플릿>.mp4`

## 속도 (Cycles)
| 환경 | 960×540, 샘플 24~32 | 1920×1080, 샘플 32 |
|---|---|---|
| 클라우드 CPU 4코어 | 프레임당 약 2~4초 | 프레임당 약 8~15초 (4초 클립 = 15~30분) |
| PC GPU(`--gpu`) | 프레임당 1초 미만 | 프레임당 1~2초 |
최종본 1080p는 PC GPU에서, 클라우드에서는 540p로 구도·움직임만 확인한다.

## 규칙
- 3D는 **분위기·상징**(돈, 코인, 금고, 막대)용이다. 정확한 수치 비교는 neogul-edit 슬라이드나 Remotion을 쓰고, 3D 막대를 쓸 때도 값 라벨을 반드시 띄운다(원근 때문에 높이 비교가 왜곡된다).
- 배경·색은 규칙집 팔레트(다크 #181614, 상승 빨강, 결론 노랑). 글자는 Pretendard.
- 클립은 엔진 클립 규칙(`video_projects/_engines/README.md`)대로 1920×1080·무음·장면 길이에 맞춰 neogul-edit `slide`의 `image`로 넣는다.
- 우분투 패키지판 Blender(클라우드)는 노이즈 제거기(OpenImageDenoise)가 없어 기본값을 끔. 공식 blender.org 배포판(PC)은 `--denoise 1`로 같은 샘플에서 더 깨끗하다.
- 새 템플릿은 `render3d.py`의 `if tmpl == ...` 블록을 늘려 만든다. 외부 3D 모델을 쓰면 라이선스(CC0 등)를 확인하고 출처를 남긴다.
