# 제미나이 옴니 1.2 플래시 팩트시트 — 2026-11-07

롱폼 해설 영상("1부터 100까지", AI 초보 눈높이) 대본용. 아래 [확인]은 2026-11-07 이 세션에서 원문 페이지를 직접 열어 본 것.

## 출처 (모두 [확인])
1. 구글 블로그 「Gemini Omni 1.2 Flash: Fast and cost-effective with longer clips」 2026-11-05, Anish Nangia(구글 딥마인드 PM)
   https://blog.google/innovation-and-ai/technology/developers-tools/introducing-gemini-omni-1-2-flash/
2. 구글 블로그 「Introducing Gemini Omni」 2026-05-19(I/O 2026), Koray Kavukcuoglu
   https://blog.google/innovation-and-ai/models-and-research/gemini-models/gemini-omni/
3. Gemini API 변경 기록 https://ai.google.dev/gemini-api/docs/changelog (2026-06-30 미리보기, 08-27 1.1 정식, 11-05 1.2 정식)
4. Gemini API 모델 문서 https://ai.google.dev/gemini-api/docs/models/gemini-omni-flash
5. Gemini API 가격표 https://ai.google.dev/gemini-api/docs/pricing#gemini-omni-1.2-flash
6. Gemini API 사용 한도 https://ai.google.dev/gemini-api/docs/rate-limits
7. Gemini API 옴니 가이드 https://ai.google.dev/gemini-api/docs/omni
8. 구글 딥마인드 모델 소개 https://deepmind.google/models/gemini-omni/

## 핵심 사실
- 옴니 = "무엇이든 넣으면 무엇이든 만드는" 모델, 영상부터. 이미지·오디오·영상·글을 섞어 넣고, 대화로 고친다. "영상판 나노 바나나". 첫 모델이 옴니 플래시. 이미지·오디오 출력은 나중에. (2, 8)
- 5월 19일: 제미나이 앱·구글 플로우(AI Plus·Pro·Ultra 구독자, 전 세계), 유튜브 쇼츠·유튜브 크리에이트 앱은 무료로 시작. API는 몇 주 뒤. (2)
- 6월 30일 API 미리보기(3~10초), 8월 27일 1.1 정식(영상 늘리기, 첫·끝 프레임, 360p/720p/1080p/4K — 1080p·4K는 업스케일). (3)
- 11월 5일 1.2 정식 (1, 3):
  - 한 번에 최대 15초(1.1은 10초), 3~15초를 1초 단위로.
  - 참고 이미지 최대 6장으로 인물·물건 일관성, 짧은 동작 영상(최대 3초)·소리 단서도 참고. 얼굴·옷·포장 글씨·브랜드 색 유지.
  - 예: 모델 사진 1장 + 옷 3벌 앞뒤 사진 → 15초 가상 피팅(360도 회전).
  - 첫·끝 프레임 사이 잇기, 영상 늘리기: 한 번에 3~10초씩, 총 30초까지.
  - 대화로 여러 번 고치기(15초 전체): 제품·배경·조명·날씨·화면 비율 바꾸기. 예: 천막→참나무 숲→흰 말 마구간→시장 축제→돌 성, 인물 연기·갑옷 반사·구도 유지.
  - 말소리: 자연스러운 대사, 입 모양 맞춤, 여러 사람 목소리 구분(1초 목소리 참고로 배역별 연결).
  - 카메라: FPV 드론처럼 광장→청동문→판테온 돔 구멍까지 한 번에(컷 없음), 해안 클로즈업→섬 전경 10초 줌아웃.
  - API 가격 30% 내림: 영상 출력 100만 토큰당 17.50 → 12달러, 720p 초당 약 0.07달러(10초 약 0.70, 15초 약 1.04), 360p 0.023, 1080p 0.104, 4K 0.209달러/초. 입력 1.50달러. 무료 등급 없음.
  - 유료 사용 한도 두 배. 1단계 분당 8회·하루 40회, 2단계 16·200, 3단계 40·2,000.
  - 12월 3일부터 1.1 요청은 자동으로 1.2로(1.2 가격).
  - 쓰는 곳: Gemini API·AI 스튜디오, 구글 클라우드, 플로우, 구글 비즈(구글 계정·워크스페이스로 15초 영상 추가 비용 없음), 제미나이 앱(15초는 AI 울트라부터 순차), 구글 광고, Gemini for business.
  - 구글이 밝힌 아직 약한 곳: 빠른 스포츠 동작, 빠른 대본 바꾸기, 복잡한 물리.
  - 결과물엔 보이지 않는 SynthID 워터마크(+앱·플로우·유튜브는 C2PA). 제미나이 앱에서 확인, 크롬·검색은 곧.
- 처음 발표 때 능력 예시(2, 8): 물리(구슬 연쇄 트랙), 지식(점토 단백질 접힘 설명 영상, 알파벳 26개 물건), 낙서→실사 영상, "나를 이 캐릭터로", 거울을 만지면 물결, 음악에 맞춰 아파트 불 켜짐, 내 아바타(내 목소리). 목소리 바꾸는 편집은 아직 시험 중.

## 참고 영상(현철님 스크린샷, 자막 못 받음 → 제목·썸네일만)
- AI Revolution 13:15 / AnassKartit 15:29 「Omni Flash 1.2 vs 1.1: 10 Rounds, 30% Cheaper, But 1.1 Won…」 / Adrian 4:10 「vs Seedance 2.5」 / AI with Surya 4:55 / ElevenLabs 0:25 「live on ElevenCreative」 / 오토 이완성 3:41 「말 한마디로 배경이 바뀐다? 한 번에 15초·가격 30% 내림」 / 코드브릿지 4:48 「15초 영상보다 중요한 변화」 / Aivoxy 3:19 「vs Seedance 2.5」 / Subhan Kaladi 10:07 「1.2 vs 1.1」 / Lifey Guy 8:11 「8분 만에 모든 기능」
- 가져올 것: 말 한마디 배경 바꾸기 시연(이완성), 1.1 vs 1.2 라운드 대결 틀(AnassKartit — 결과는 확인 못 해 "제목에서"로만), 판테온 FPV 장면 소개(코드브릿지), 기능 총정리 목록(Lifey Guy).
