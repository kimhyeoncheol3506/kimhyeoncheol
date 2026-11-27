
# 연애 유튜브 영상 제작 (현철님)
- 스샷·"쇼츠/롱폼/오늘치 만들어" 요청은 `.claude/skills/yeonae-shorts-studio/SKILL.md`의 **상시 규칙**을 그대로 따른다 (스샷이 오면 "읽어주는 영상 vs 삽화 영상?" 하나만 묻고 고른 대로 제작 · 그 외엔 묻지 않음, 세트 전달, ⏸ 롱폼 일시 중단(2026-10-20~, 쇼츠만 · 롱폼 질문/자동 예약 안 함), 막장드라마 포맷, 최종 검수 후 전달, 아이디 별표·파일명 = 영상 제목 전체, 삽화 영상은 장면별 ComfyUI 삽화 + 전달 전 삽화 직접 확인).
- 숫자·비율·그래프 장면은 SKILL 0-1d6 도구 선택(Remotion/HyperFrames/Manim 클립, video-shotcraft 레시피), 설치·명령은 `shorts-studio/motion/README.md`
- 코드: `shorts-studio/` · 변경 이력: `shorts-studio/CHANGELOG.md`

# Aside 공유 스킬
- 지시가 오면 루트 `ASIDE_SKILLS.md` 의 트리거 표를 보고 해당 `.claude/skills/<스킬>/SKILL.md` 와 `CLOUD.md` 를 먼저 읽고 따른다.
- 클라우드(Linux)에서의 차이는 같은 폴더의 `CLOUD.md` 를 따른다.
- `SKILL.md`·scripts·assets 는 Aside 원본이므로 고치지 않는다(다음 동기화 때 덮어씀).
- 목소리: 여의도여자(기본)·마포남자(30대 초반 맑고 밝은 아나운서·MC 톤)·여의도남자(없으면 마포남자). 어떤 TTS든 넣기 직전 `ko_tts.normalize`로 발음 변환, 자막은 원문 (`.claude/skills/ko-tts-pronounce`).
