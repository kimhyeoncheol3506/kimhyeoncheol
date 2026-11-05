# kimhyeoncheol

얼굴없는 유튜브 영상 자동 제작 도구(`facetube/` 롱폼·캐릭터, `shorts/` 세로 쇼츠)와 편집 규칙. 사용법은 `README.md`, 제작 절차는 `.claude/skills/faceless-video/SKILL.md`, 현철님 피드백 규칙은 `.claude/skills/faceless-video/references/내규칙.md`. 참고 유튜브 영상 여러 개를 합쳐 내 영상으로 만들 때는 `.claude/skills/reference-merge-video/SKILL.md`(본보기 `projects/rea_full_neon.yaml`, 더빙·렌더는 PC의 Voicebox에서만). 최종본은 항상 영상·유튜브 텍스트·썸네일 세트를 주제 이름+버전으로 `release/<주제>/` 에 내보낸다: `.claude/skills/video-release/SKILL.md`.

## Agent skills

### Issue tracker

Issues live in GitHub Issues of `kimhyeoncheol3506/kimhyeoncheol` (PRs are not a triage surface). See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-role vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one root `GLOSSARY.md` plus `docs/adr/`, both created lazily by `/domain-modeling`. See `docs/agents/domain.md`.

## 말하는 언어

현철님께 쓰는 글(설명·보고·질문·요약·파일 캡션·커밋 메시지 포함)은 **모두 한국어**로 쓴다. 영어는 프로그램·모델 이름처럼 꼭 필요한 고유명사만 쓴다. (2026-11-05 현철님: "이제 니가 쓰는 글은 모두 한국어로 써")
