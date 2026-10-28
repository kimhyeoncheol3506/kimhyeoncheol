# heygen-com/hyperframes 스킬 (설치본)

- 출처: https://github.com/heygen-com/hyperframes (설치한 시점의 main 커밋 1428f87, 2026-10-28)
- 설치 명령: `npx skills add heygen-com/hyperframes --skill hyperframes hyperframes-cli hyperframes-registry media-use -a claude-code -y --copy` (텔레메트리 끔: `DISABLE_TELEMETRY=1 DO_NOT_TRACK=1`)
- 설치한 것(핵심 4개, README 권장): `hyperframes`(HTML→영상 렌더 규약, 먼저 읽기), `hyperframes-cli`, `hyperframes-registry`(블록·컴포넌트 약 450개), `media-use`(음악·효과음·이미지·음성·자막 소재)
- 설치 안 한 것(필요할 때 추가): `figma`, `slideshow`, `remotion-to-hyperframes` → `npx skills add heygen-com/hyperframes --skill <이름> -a claude-code -y --copy`
- `skills-lock.json`(저장소 루트): 설치한 스킬의 출처·해시. 업데이트: `npx skills update`.
- 요구 사항: Node.js 22+ 와 FFmpeg (이 환경에 있음). 크롬은 첫 렌더 때 필요(미시험).
- 선택 기능: HeyGen(`HEYGEN_API_KEY`)·Gemini(`GEMINI_API_KEY`) 키가 있어야 쓰는 클라우드 렌더·음성·아바타·생성 영상. 키가 없으면 무료 로컬 도구 경로를 쓴다. **키 입력·요금 발생은 현철님이 결정**한다.
- 텔레메트리: HyperFrames CLI 는 익명 사용 횟수를 PostHog 로 보낸다. 끄려면 `HYPERFRAMES_NO_TELEMETRY=1` 또는 `DO_NOT_TRACK=1`.
- 우리 프로젝트와의 관계: `shorts/scene.html` 도 같은 원리(시간 t 를 넣으면 같은 화면이 나오는 HTML → 프레임 → mp4)다. HyperFrames 는 그 상위 도구(타임라인 편집·레지스트리·스튜디오 미리보기)로 참고·병행할 수 있다. 우리 쇼츠 공장의 원칙 점검(아래 18% 비움·13자 자막·출처 숫자)은 HyperFrames 에 없으므로 그대로 유지한다.
- 주의: 이 스킬들은 에이전트 권한으로 `npx hyperframes …` 를 실행하라고 안내한다. 설치할 때 위험 패턴(원격 스크립트 실행, 키 탈취, 임의 삭제)과 접속 도메인(HeyGen, Gemini, Openverse 등)을 훑어 이상이 없음을 확인했지만 모든 줄을 읽은 것은 아니다.
