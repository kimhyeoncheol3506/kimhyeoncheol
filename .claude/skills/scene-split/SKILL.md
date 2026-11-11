---
name: scene-split
description: "PySceneDetect로 영상의 컷(장면 바뀜)을 찾아 장면 목록(csv), 장면별 대표 프레임 시트, 장면별 클립을 만든다. 참고 영상의 컷 리듬 분석(너굴분석·reverse 보조), 우리 롱폼의 컷 간격 검수(R-P1·R-P2), 롱폼에서 쇼츠로 쓸 구간 고르기에 쓴다. '장면 나눠', '컷 찾아', '컷 간격', '씬 분할', 'scenedetect' 요청에 사용."
---

# PySceneDetect 장면 나누기

```bash
python .claude/skills/scene-split/scripts/split_scenes.py <영상> --out <폴더> [--threshold 27] [--min 0.6] [--split] [--sheet]
```
- `scenes.csv`: 장면 번호, 시작, 끝, 길이(초)
- `stats.json`: 컷 수, 분당 컷, 장면 길이 중앙값·25%·75%, 8초 넘게 바뀌지 않은 장면 목록
- `--sheet`: 장면마다 가운데 프레임을 모은 `scenes_sheet.png`
- `--split`: 장면마다 `clips/scene_###.mp4` (다시 인코딩, 정확한 컷)

## 감지 방식
- 기본은 내용 변화(ContentDetector, `--threshold` 27) — 실사·일반 유튜브 영상용.
- **우리 롱폼처럼 어두운 슬라이드가 이어지는 영상은 `--threshold 8`**. 시험: 「금융의 모든 것」 처음 180초에서 27은 5장면, 8은 실제와 같은 8장면을 잡았다.
- 페이드가 많은 영상은 `--mode adaptive`, 검은 화면 전환은 `--mode threshold`.
- 너무 잘게 잘리면 `--threshold`를 올리고(30~40), 놓치면 내린다(20 안팎). `--min`은 장면 최소 길이(초).

## 쓰임
- **너굴분석 보조**: neogul-edit `analyze`가 재는 컷 간격과 같이 보고, 규칙집 R-P1(분당 2~3회, 오프닝은 4~5회)과 비교한다.
- **우리 영상 검수**: 렌더 결과에 돌려 `stats.json`의 '8초 넘게 그대로인 장면'이 R-P2 위반인지 본다(강조 요소만 바뀌는 슬라이드는 컷으로 안 잡힐 수 있으니 시트로 직접 확인).
- **쇼츠 구간 고르기**: 장면 목록에서 15~60초 묶음을 고른 뒤 ffmpeg-edit의 세로 레시피로 자른다.
- 다른 채널 영상은 분석(리듬·길이)만 하고, 잘라 낸 클립을 우리 영상에 쓰지 않는다.
