# '지금 뜨거운 돈 이슈' 롱폼 3편 — 대본 작업 지시 (2026-11-18, 현철님 요청)

채널: 월급쟁이 재테크 스킬. 모델 2 에디토리얼 파이프라인(neural-studio, style: paper, 여의도여자), '한편으로 끝' 4편과 같은 방식.
속도가 중요하다(뉴스성). 대본만 쓰고, 더빙·렌더는 메인 세션이 한다.

## 먼저 읽을 것
1. `docs/채널규칙_제목썸네일첫15초.md` — 첫 15초·구독 한마디·보고 규칙.
2. `projects/_series_oneshot/BRIEF.md` — 사실 확인·금지 규칙(그대로 지킨다).
3. 본보기 대본: `projects/oneshot_saudi.yaml`(합쳐진 완성본). 머리 필드(slug·name·style·format·auto_beats·brand·title·intro_chapter·voice·thumbnail·summary·tags·disclaimer·say_as·numbers_ok·sources·scenes) 형식과 장면 종류(kind)·sync·source·theme 쓰는 법을 그대로 따른다.
   장면 종류: year chapter doc person quote bars waffle line gauge bignum stairs flip pie timeline stack end (photo 는 쓰지 않는다 — 사진 찾을 시간 없음, 실존 인물 얼굴 금지).

## 결과 파일
- 대본: `projects/<slug>.yaml` 하나(조각 나누지 않아도 됨). `thumbnail: {file: assets/thumbs/<slug>_thumb_3d.png}`.
- 3D 썸네일 설정: `projects/<slug>_thumb3d.json` (형식은 `projects/oneshot_saudi_parts/thumb3d.json`, 도구 README `tools/thumb3d_contrast/README*`). 렌더: `python3 tools/thumb3d_contrast/make.py projects/<slug>_thumb3d.json assets/thumbs/<slug>_thumb_3d.png --work /tmp/t3d_<slug>`. 결과를 Read 로 보고 고친다.
- 어두운 에디토리얼 썸네일 A: `projects/<slug>_make_thumb.py` → `assets/thumbs/<slug>_thumb_A.png` (1280×720). `projects/oneshot_saudi_parts/make_thumb.py` 의 렌더 방식(make_thumb_v2.render)을 쓰되 **어두운 바탕(먹색·짙은 남색) + 큰 숫자 하나 + 글자 6자 이하**, 빨간 붓 밑줄 금지, 채널 배지 금지, 실존 인물 얼굴 금지, 오른쪽 아래 비움. 개미는 작게, 표정 맞을 때만. Read 로 확인, 320×180 에서도 읽히는지 확인. 그다음 `cp assets/thumbs/<slug>_thumb_A.png assets/thumbs/<slug>_thumb_B.png` (B 자리 채움).

## 길이·구성
- 완성 10~13분 → `python3 tools/series_lint.py projects/<slug>.yaml` 예상 길이 **11.0~12.5분**, 오류 0. 장면 65~85개, 판 하나 18초 이하.
- 인트로(intro_chapter) + 4~5장 + 마지막 장 '월급쟁이 행동 원칙'(체크리스트) + 아웃트로(구독·출처 안내 → `감사합니다.` hold 10, kind end).
- 첫 15초: 첫 판 = 결론 숫자(썸네일 숫자와 같게, 첫 10초 화면에 그대로 보이게, sync 숫자 즉시 0~0.2). 판 하나 4~5초(한글 20~25자)로 15초 안에 판 3개 이상. 넷째 판 무렵에 훅: "끝까지 보시면 내 돈에 지금 뭘 해야 하는지 나옵니다." 2~4번째 판 중 하나는 질문(?). 27~35초 지점에 "이런 계산 매주 올립니다. 구독해 두시면 다음 편도 받아 보실 수 있어요." 판(사우디 본보기와 같게). 인사·채널 소개는 30초 이후.
- 제목: 현철님 제목안을 title 로 그대로(필요하면 아주 조금만 다듬고, 다듬었으면 보고). 검색어로 summary·tags 첫머리 시작.

## 사실 규칙 (가장 중요)
- **모든 숫자는 기사·공식 자료로 직접 확인한 것만.** WebSearch/WebFetch 로 찾고, sources 마다 outlet(매체)·title·date(보도 날짜)·url·verified: true·facts(쓴 숫자 문자열 전부). 확인 못한 숫자는 쓰지 않는다(현철님이 준 숫자도 확인 못하면 빼거나 '보도마다 다름'으로 범위 처리).
- 화면 source 표기는 "매체 날짜" (예: "연합뉴스 11/17"). 2026년 보도 수치는 대사나 화면에 '(보도)'·'정부 발표'·'정부안'·'전망'·'추정'을 구분.
- 직접 계산한 숫자(회복률, 총비용 등)는 '계산'이라고 밝히고, 계산 근거(전제)를 화면에 적고, 계산 과정은 yaml 주석에 남긴다. 계산 sources 항목은 outlet "채널 계산(전제: …)", verified: true, facts 에 결과 숫자.
- 숫자는 아라비아 숫자로 쓴다(돈 단위는 엔진이 한자어로 읽음: 팔십 달러). 큰 금액은 "1억 2,000만 원"식. sync.at 낱말에 띄어쓰기 금지, 대사에 실제로 있는 낱말만.
- 투자 권유 아님 고지(disclaimer + 마지막 장 대사 한 줄). 특정 종목 매수·매도 권유 금지.
- 실존 인물은 경제 맥락 사실만, 사생활·스캔들은 한 줄 이하.

## 하지 말 것
- make_editorial.py 실행 금지(더빙·렌더·--stills 모두). git commit/push 금지. tools/·editorial/·facetube/·docs/ 코드·규칙 수정 금지. 다른 편 파일 수정 금지.
- 디스크 여유 약 2GB: 큰 파일 금지, 임시 파일은 /tmp/t3d_<slug>/ 등에만.

## 보고 (마지막 메시지, 한국어, 짧게)
slug · 제목 · 장면 수 · lint 예상 길이 · 챕터 · 첫 문장 · 썸네일 3D/A 문구와 숫자 · 확인 못해서 뺀 숫자 · 보도마다 달라 범위로 쓴 숫자 · lint 결과.
