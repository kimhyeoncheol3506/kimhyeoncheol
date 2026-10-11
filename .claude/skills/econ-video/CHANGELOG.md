# econ-video 변경 기록

스킬(`SKILL.md`의 version)과 엔진(`video-studio/VERSION`)은 같은 번호를 쓴다.
- 앞자리(major): 작업 절차나 project.json 형식이 바뀌어 예전 프로젝트가 그대로 동작하지 않을 때
- 가운데(minor): 장면 타입·아이콘·레이아웃 등 기능 추가
- 끝자리(patch): 오류 수정·디자인 미세 조정

## v1.0.0 — 2026-10-11
- 최초 버전
- 절차: 스크린샷 → 롱폼/쇼츠 질문 → 주제 조사 → 방향 예시 3개 질문 → 제작 → 영상·제목·설명란·썸네일 1세트
- 벤치마킹 3편(경제학똑똑·머니치트키·인생 녹음 중) 분석을 제작 규칙으로 정리 (STYLE_GUIDE.md)
- 쇼츠 1080x1920 / 롱폼 1920x1080 레이아웃, 장면 타입 10종, 마스코트 표정 8종·포즈 4종, 아이콘 15종
- 목소리: Voicebox 여의도남자(기본)·여의도여자(대화). 다른 TTS 대체 없음, `--preview-silent`만 예외
- 출력: video.mp4, thumbnail.png(+쇼츠 커버), title/description/tags.txt, subtitles.srt, 업로드정보.md
