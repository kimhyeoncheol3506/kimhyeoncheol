# CLAUDE.md

## Aside 공유 스킬
- 지시가 오면 루트 `ASIDE_SKILLS.md` 의 트리거 표를 보고 해당 `.claude/skills/<스킬>/SKILL.md` 를 먼저 읽고 따른다.
- 클라우드(Linux)에서의 차이는 같은 폴더의 `CLOUD.md` 를 따른다.
- `SKILL.md`·scripts·assets 는 Aside 원본이므로 고치지 않는다(다음 동기화 때 덮어씀).

## 프로젝트 메모

- 역사 그날의 진실 / 역사 쇼츠 / 한국사 쇼츠 → history-truth-shorts 스킬
- 지시가 오면 ASIDE_SKILLS.md 트리거 표를 보고 .claude/skills/<스킬>/SKILL.md 와 CLOUD.md 를 먼저 읽고 따른다.
- "스틱맨"만 말하면 mystery-cartoon(B 엔진), "스틱맨 비디오 디렉터"·스타일 코드(A1~A8, B1~B8)를 말하면 directing-stickman-videos.
- [사용자 승인 규칙] 역사가 지운 그날 채널의 업로드·썸네일·예약 변경은 Aside 역사 채팅(KXdg)만 한다. 이 세션은 영상·썸네일 파일 제작까지만(썸네일은 이름 썸네일 규칙: tools/thumb_name.py), 직접 업로드·예약·Studio 변경 금지.
- [목소리 3종·발음 사전 2026-11-28] 기본 여의도여자, TTS_VOICE=마포남자(너굴은 --voice 마포남자), 여의도남자 없으면 마포남자. 어떤 TTS(클라우드 edge-tts·gTTS 포함)든 넣기 직전에 `.claude/skills/ko-tts-pronounce/ko_tts.py` 의 normalize() 를 거치고, 자막은 원문.
