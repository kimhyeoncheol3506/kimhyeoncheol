# CLAUDE.md

## 국내 페이스리스 <경제2> 채널 — 영상 편집 기본값

- **경제2 영상 편집은 `neogul-edit` 스킬과 규칙집 R-코드를 따른다, 기본 목소리는 여의도여자.**
  - 스킬: `.claude/skills/neogul-edit/SKILL.md`
  - 규칙집(기본 편집 스타일): `.claude/skills/neogul-edit/references/규칙집.md` (R-P·R-A·R-S·R-T·R-L … 코드)
  - 수치: `.claude/skills/neogul-edit/scripts/rules.json` / 근거: `references/편집분석집.md`
- 사용자가 **"너굴편집"**(또는 "너굴경제 스타일로 편집해줘")이라고 하면 `neogul-edit` 스킬을 실행한다. "너굴분석"은 같은 스킬의 참고 영상 측정 기능이다.
- 목소리: 여의도여자 (Voicebox, `http://127.0.0.1:17493`, `--voice 여의도여자`). Voicebox는 현철님 PC에서만 돌아가므로 클라우드 세션에서는 음성 생성을 건너뛰고 템플릿·미리보기까지만 한다.
- 편집기는 ffmpeg **6.1 이상에서 동작**한다 (버전을 확인해 7 이상은 `-/filter_complex`, 6 이하는 `-filter_complex_script`를 자동 선택).
- 너굴경제의 마스코트·일러스트·실사 클립은 쓰지 않는다. 따라 하는 것은 편집 문법뿐이다 (SKILL.md "주의").
