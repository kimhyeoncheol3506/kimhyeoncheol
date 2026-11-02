---
name: rulebook-edit
description: 현철님 채널의 '편집 규칙집'(바로쓰는 심리학 레퍼런스 분해, video-studio/편집규칙집.md)대로 영상을 편집·마감한다. "규칙집대로 편집해줘", "규칙집 적용해줘", "편집 규칙 입혀줘", "구독 범퍼·아웃트로 넣어줘"처럼 한 문장으로 부르면 사용. 완성 영상 마감(구독 팝업·아웃트로 CTA·클릭음), 그림/클립+내레이션+자막만으로 한 편 조립, 새 영상 제작 시 규칙집 기본값 적용을 모두 다룬다.
---

# 편집 규칙집 적용

규칙 원문: `video-studio/편집규칙집.md` (v1.0, 2026-11-02). 실측 근거·한계·장면 단위 분해가 들어 있다. 규칙을 바꾸면 그 문서와 이 스킬을 함께 고친다.

## 한 문장 요청 → 할 일
1. **"OO 영상에 규칙집 적용해줘"** (이미 만든 econ 영상)
   - 해당 프로젝트 `meta.json`(없으면 project.json)에 `"rulebook": true`, `"voice_speed_by": {"여의도남자": 1.0}`, `"scene_pause": 0.45`, `"top_title": "<짧은 제목>"`을 넣는다.
   - `build.py`의 render_all 쉼 계산이 `scene_pause`를 읽는지 확인(20261102-2027-scenario/build.py 방식).
   - `build.py plan` → `voice/align.py` → `build.py render`(2프로세스) → `make_video.py --no-package` → 썸네일 복사 → `studio.package.package()`(버전 +1). 음성은 다시 만들 필요 없다(배속은 후처리).
   - 결과: 자막 70px·20자, 왼쪽 위 제목, 오른쪽 위 둥근 배지, 구독 범퍼(첫 챕터 끝 −5.5초), 아웃트로 CTA(마지막 6초), 클릭음, 설명란 첫 줄 해시태그·AI 활용 문구.
2. **"이 영상 파일에 구독 범퍼랑 아웃트로만 넣어줘"** (아무 mp4)
   - `python video-studio/tools/rulebook_edit.py finish <video.mp4> [--bumper 초] [--out 결과.mp4]`
3. **"이 그림들이랑 녹음으로 규칙집대로 만들어줘"** (소재만 있을 때)
   - `python video-studio/tools/rulebook_edit.py build <그림·클립 폴더> <내레이션.wav> <자막.srt> <out.mp4> --title "제목"`
   - 그림 5~6초 유지(자막 경계에 스냅), 느린 확대(방향 번갈아), 하단 자막 박스, 상단 제목·배지, -14 LUFS, 마지막에 finish.
4. **새 영상 제작** (`econ-motion-video` 스킬과 함께): meta에 위 4개 값을 기본으로 넣고, 대본·장면 설계에서 다음을 지킨다.
   - 한 장면 10초 이하(넘으면 S2로 나누기)
   - 해결책·행동 파트는 좌우 전후 비교(dual/compare)를 우선
   - 스틱맨 장면의 핵심어는 말풍선·라벨로

## 확인
- `tools/verify_video.py` 통과, 범퍼·아웃트로 프레임 2장씩 눈으로 확인(버튼 글자가 □로 깨지지 않는지 — 이모지는 폰트에 없으니 쓰지 않는다).
- 실사 자료 화면은 선택 규칙이다. 상업 이용 가능한 출처가 있을 때만 `clip`으로 넣고 설명란에 출처를 적는다.
