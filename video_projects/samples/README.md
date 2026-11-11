# 영상 종류 샘플 (각 약 10초)

| 파일 | 종류 | 만든 방법 |
|---|---|---|
| `너굴경제인포그래픽_10s.mp4` | 너굴경제 스타일 인포그래픽 롱폼 | neogul-edit 그대로: `voice --wav-dir` → `project.json`(훅·막대·큰 숫자) → `render`. 원본: `src_neogul/` |
| `모션그래픽_HyperFrames_10s.mp4` | 모션그래픽(엔진) | `_engines/hyperframes` CLI로 HTML+GSAP 렌더. 원본: `src_hyperframes/index.html` |

- 목소리: 여의도여자(Voicebox)는 클라우드에서 쓸 수 없어 **Supertonic-3 F3**로 대신했다. 모션그래픽 샘플은 무음.
- 이미지: 1929년 군중 사진(Wikimedia Commons, 퍼블릭 도메인)만 사용. 그 밖의 그래픽은 직접 그림.
| `3D_Blender_코인_2s.mp4` | 3D 오브젝트(Blender) | `blender-3d` 스킬 `coin` 템플릿, 클라우드 CPU 960×540 확인용 |
| `3D_Blender_막대_3s.mp4` | 3D 막대 차트(Blender) | `blender-3d` 스킬 `bars` 템플릿, 클라우드 CPU 640×360 확인용 |
| `화질키우기_ESRGAN_비교.png` | 화질 키우기 비교 | 바이큐빅 / ESRGAN x4plus / ESRGAN general (튤립 그림 4배 확대 일부) |
