# directing-stickman-videos: Claude Code 클라우드 메모 (이 세션에서 추가, 2026-11-25)

원본: github.com/kaomei/stickman-video-director (MIT), 커밋 1028782 (2026-11-24). SKILL.md·references·scripts 는 원본 그대로 두고 다른 점만 여기 적는다.

## 설치 상태
- 깃에는 SKILL.md, references, scripts, examples, tests, json/폰트만 있다(약 19MB).
- 이미지·영상·음원(약 540MB)은 `.gitignore` 다. 새 세션에서 렌더하려면 먼저:
  `bash .claude/skills/directing-stickman-videos/CLOUD_fetch_assets.sh`
- B(코드 엔진) 런타임: `cd .claude/skills/directing-stickman-videos && npm ci && node scripts/autopilot.mjs doctor`
  (2026-11-25 이 세션에서는 자동 승인 모드가 외부 패키지 설치를 막아 실행하지 못함. 사용자가 허용하거나 직접 실행해야 함.)
- 크롬: `/opt/pw-browsers/chromium` (playwright install 금지).

## 우리 채널에 쓰는 법
- 《역사, 그날의 진실》 본 제작은 계속 history-truth-shorts(toon2d)로 한다. 이 스킬은
  1) 스타일 비교용 시험 영상(A5 Historical Cartoon, B4 Survival Thriller 의 3초 규칙·오프닝 연출),
  2) 새 채널·새 포맷 실험(B1 미니멀 손그림 설명형, B2 컬러 손그림 심리·습관형),
  3) 사운드 라이브러리(`assets/b-audio-library`, 출처·라이선스 CREDITS.md) 로 쓴다.
- 이미 가져온 것: 사운드·3초 규칙·20초 미리보기는 history-truth-shorts 에 적용됨(references/sound-and-pacing.md).
- 내레이션: 원본은 ElevenLabs(Brian 등)·Gemini TTS 를 쓴다. 키는 채팅에 붙이지 않는다(사용자가 환경 비밀로 등록). 키가 없으면 edge-tts(ko-KR-InJoonNeural/SunHi)로 대체하고 "목소리 다름"을 알린다. 여의도여자는 PC 전용.
- 언어: 원본 기본은 영어. 한국어 영상은 요청에 "Korean narration and captions" 를 명시하고 한글 폰트(Pretendard: ../mystery-cartoon/kits/toon2d/toon2d/fonts) 커버리지를 확인한다(B4·B6 는 폰트 커버리지 검사 스크립트 있음).
- A 엔진(Google Flow·Veo 생성): 크레딧 비용, 실존 인물 이름 거부. 사용자 승인 없이 생성하지 않는다. 한국사 인물은 이름 대신 묘사로 프롬프트.
- 업로드·게시는 하지 않는다(사용자 규칙). 음원 크레딧은 업로드 TXT 설명에 넣는다.
