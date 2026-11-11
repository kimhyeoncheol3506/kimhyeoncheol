---
name: "neogul-edit"
description: "사용자가 \"너굴편집\" 또는 \"너굴경제 스타일로 편집해줘\"라고 하면 실행. 내레이션 음성/대본과 소스(이미지·영상)를 받아 너굴경제 편집 규칙집(인포그래픽 슬라이드, 하단 박스 자막, 빨간 박스 강조, B-roll 줌+분홍 플래시, 마스코트 컷인, 무음 압축, 효과음 자동 배치)대로 Python+ffmpeg로 롱폼 영상을 자동 편집해 mp4로 만든다. \"너굴분석\"이라고 하면 참고 영상의 컷 간격·무음·음량을 같은 방식으로 측정한다."
---

# 너굴편집

규칙: `references/규칙집.md` (R-코드). 근거: `references/편집분석집.md`. 수치: `scripts/rules.json`. 편집기: `scripts/neogul_edit.py` (표준 라이브러리만 사용, ffmpeg 필요. PATH에 없으면 WinGet 설치본을 자동으로 찾음).

## 실행 순서

1. **입력 확인** (ask_user_question으로 한 번에 묻기): 작업 폴더, 내레이션 형태(완성 음성+srt / 문장별 음성 파일+대본 / 대본만 있으면 Windows TTS 임시 음성), 마스코트·훅 이미지, B-roll 영상. 없는 것은 임시 자료로 진행해도 되는지 묻는다.
2. **음성과 자막 준비**
   - 대본만 있거나 문장별 음성 파일이 있으면: `python scripts/neogul_edit.py voice script.txt --out-dir <폴더> [--wav-dir <문장별음성폴더>] [--voice 여의도여자]` 를 실행하면 voice.wav와 voice.srt가 생긴다 (srt 줄 번호 = 대본 줄 번호).
   - 기본 목소리는 **여의도여자** (Voicebox, http://127.0.0.1:17493)이다. 서버가 꺼져 있으면 `explorer.exe "C:\Program Files\Voicebox\voicebox.exe"` 로 켜고 /profiles 응답을 기다린다(약 20초). 한 문장에 20~50초 걸리므로 셸은 yield_ms로 돌리고 진행 상황을 본다. `--voice`를 빼면 Windows TTS(Heami)로 임시 음성을 만든다.
   - 데모: `demo <폴더> --voice 여의도여자`
   - 강조 자막은 대본/srt 줄에 `**…**`, `!…`, `"…"` 로 표시한다 (R-T3, 영상당 5~10회).
3. **project.json 작성**: `python scripts/neogul_edit.py new <폴더>` 로 템플릿을 만든 뒤 규칙집 0장 뼈대대로 장면을 채운다. 장면마다 `start_line`을 대본 줄에 맞추고, 숫자가 나오는 문장은 `cards`/`bars`/`bignum` 슬라이드로 만들고, 말하는 순간에 맞춰 `highlights`/`pointers`의 `at`을 정한다 (R-P2: 8초 넘게 화면 변화가 없으면 안 됨). 형식은 규칙집 부록에 있다.
4. **미리보기**: `python scripts/neogul_edit.py render <폴더>/project.json --preview` 를 실행하면 960x540 preview.mp4가 나온다. 프레임 몇 장을 뽑아 직접 보고 글자 넘침, 박스 위치, 장면 타이밍을 고친다.
5. **최종 렌더**: `render <폴더>/project.json` 을 실행하면 1080p output.mp4가 나온다. 최종 음량 -16 LUFS인지 확인한다 (ffmpeg ebur128).
6. 결과 mp4를 artifacts에 복사하고 대표 프레임 시트를 보여준다.

## 너굴분석 (참고 영상 측정)

ytultra.com Video Downloader(무료)로 영상 URL을 넣어 링크를 받는다. itag=18(360p, 소리 포함)과 itag=136(720p, 영상만)이 있다. REPL `fetch`에 `&range=시작-끝`을 붙여 3MB씩 나눠 받은 뒤 셸에서 합친다. 그다음 `python scripts/neogul_edit.py analyze <영상.mp4>` 를 실행하면 analysis.json, report.md, 프레임 시트, 스펙트로그램이 나온다. 규칙집과 다른 점이 있으면 rules.json 수치를 고친다.

## 주의

- 너굴경제의 마스코트, 일러스트, 실사 클립을 그대로 쓰지 않는다. 사용자 본인의 캐릭터와 저작권 문제가 없는 자료만 쓴다. 따라 하는 것은 편집 문법뿐이다.
- 폰트는 scripts/fonts의 Pretendard(SIL OFL)를 쓴다. 렌더할 때 _build/fonts로 복사된다.
- 필터 경로는 _build 폴더 기준 상대경로로 만들어 Windows 콜론 문제를 피한다. 한글 텍스트는 셸 here-string을 거치지 말고 파일(project.json/srt)로 전달한다.

## 장면별 도구 선택 (추가 엔진 — 2026-11 추가)

위의 실행 순서·말투(규칙집 9장)·음성(여의도여자)·검수(미리보기 → 최종 렌더, -16 LUFS) 규칙은 그대로 둔다. 아래는 **슬라이드 한 장으로는 부족한 장면**의 클립을 어느 도구로 만들지 정한 것이다. 만든 클립은 `video_projects/_engines/README.md` 방식대로 `slide` 장면의 `image`(mp4, `image_box: [0,0,1920,1080]`)로 넣는다. neogul_edit.py 자체는 고치지 않는다.

| 장면 성격 | 1순위 도구 | 대안 | 메모 |
|---|---|---|---|
| 기본 인포그래픽(카드·막대·큰 숫자·목록) | **neogul-edit 슬라이드** (R-L5) | — | 지금처럼. 대부분의 장면은 여기서 끝낸다 |
| 숫자 카운트업, 막대·선 그래프가 자라는 애니메이션, 데이터 대시보드 | **Remotion** (`_engines/remotion`) | HyperFrames | `remotion-video` 스킬 참고. 회사 규모가 커지면 Remotion 라이선스 확인 |
| 키네틱 타이포(문장이 튀어나오는 강조), 뉴스 헤드라인 모션, 전환 효과, 오버레이 | **HyperFrames** (`_engines/hyperframes`) | Remotion | `hyperframes`·`hyperframes-registry` 스킬(블록 약 450개: 전환·타이틀·차트·지도) |
| 공식·수식, 함수 그래프, 기하·확률 설명(복리, 신용창조 급수, 폰지 기하급수 등) | **Manim** (`_engines/manim`) | — | 한글은 `Text(font="Pretendard")`, 수식은 `MathTex`. 최종은 `-qh`(1080p) |
| 컷 리듬·샷 구성(오프닝 훅, 챕터 전환, 아웃트로의 카메라 무브·리빌) | **video-shotcraft 샷 레시피** (`references/shots/` 124장) | HyperFrames 블록 | 레시피의 *리듬·타이밍*만 빌리고 제품 홍보 전용 흐름(Ink Press 템플릿, 모드 선택 질문)은 경제2 영상에 쓰지 않는다 |
| 효과음 고르기·맞추기 | neogul-edit 자동 효과음(R-S1) | video-shotcraft `sound-design.md` | 새 효과음을 쓰면 출처·라이선스를 설명란에 남긴다 |
| 3D 오브젝트·입체 장면(돌아가는 ₩ 코인, 3D 막대, 금고) | **Blender** (`blender-3d` 스킬) | Remotion | 최종 1080p는 PC GPU. 수치 비교는 3D로 하지 않는다 |
| B-roll 장면 그림·챕터 표지·썸네일 배경(퍼블릭 도메인 그림이 없을 때) | **ComfyUI** (`comfyui-image` 스킬, PC 전용) | 제목 카드(대체) | 영어 프롬프트, 실존 인물·로고·숫자 금지, 'AI 생성 이미지' 표기 |
| 작거나 흐린 그림·사진 키우기 | **Real-ESRGAN** (`upscale-esrgan` 스킬) | — | 긴 변 1280px 미만이면 B-roll·썸네일 전에 키운다 |

### 제작 단계별 공통 도구 (2026-11 추가)
| 단계 | 도구(스킬) | 할 일 |
|---|---|---|
| 참고 영상 분석(너굴분석) | `scene-split`(PySceneDetect) + neogul-edit `analyze` | 컷 목록·분당 컷·장면 길이. 어두운 슬라이드형 영상은 `--threshold 8` |
| 내레이션 발음 검수 | `whisper-subtitle`(faster-whisper) | 대본과 받아쓰기 대조, 일치율 0.85 미만 문장 다시 생성 |
| 렌더 뒤 손질·전달본 | `ffmpeg-edit` | 파트 이어 붙이기, 720p, 쇼츠 세로, 음량 -16 LUFS 확인 |
| 렌더 검수 | `ffmpeg-edit`의 프레임 시트 + `scene-split` 통계 | 글자 넘침·검은 화면 확인, 8초 넘게 그대로인 장면(R-P2) 확인 |

엔진 클립 공통 규칙:
- 1920x1080, 30fps, 무음. 색은 규칙집 팔레트(R-L2, R-L6), 폰트 Pretendard.
- 글자·그래프는 y 880 위쪽(아래는 하단 자막 자리, R-T1).
- 장면 길이에 맞춰 렌더하거나 `tpad=stop_mode=clone`으로 마지막 프레임을 늘린다(짧으면 반복 재생됨).
- R-P2(8초 넘게 화면 변화 없음 금지)는 엔진 클립에도 적용한다.
- 숫자·출처는 대본과 같은 근거만 쓰고, 단순화한 그래프는 화면에 '예시'라고 적는다.
- 미리보기 단계에서 엔진 클립이 들어간 장면 프레임을 반드시 뽑아 본다.
