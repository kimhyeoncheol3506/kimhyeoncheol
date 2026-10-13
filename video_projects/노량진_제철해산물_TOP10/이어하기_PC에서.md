# PC에서 이어서 만들기 — 노량진 제철 해산물 TOP10 (여의도남자 목소리)

클라우드 세션은 현철님 PC의 Voicebox에 접속할 수 없어서, **음성 생성부터는 PC에서 실행하는 Claude 세션**에서 이어서 진행합니다.

## 준비 (한 번만)
1. PC에서 Voicebox 앱을 켭니다(`http://127.0.0.1:17493`).
2. 이 저장소를 PC에 받고 작업 브랜치로 바꿉니다.
   ```
   git fetch origin video/noryangjin-top10
   git checkout video/noryangjin-top10
   ```
3. 그 폴더에서 Claude 데스크톱 앱(또는 터미널에서 `claude`)을 열고 이렇게 요청합니다.
   > "video_projects/노량진_제철해산물_TOP10/이어하기_PC에서.md 대로 영상 마무리해줘"

## Claude가 PC에서 할 일 (순서대로)
1. **음성**: `yeouido-voice` 스킬로 `01_대본/scenes_여의도남자.json`(139문장, id = `섹션_문장`)을 생성합니다. 결과 wav 파일을 `09_소재/tts/` 아래에 `00_00.wav` 형식의 이름으로 저장합니다.
2. **발음 검수**: `pip install faster-whisper` 후
   `python .claude/skills/ranking-video/scripts/check_tts.py video_projects/노량진_제철해산물_TOP10/01_대본/대본데이터.json video_projects/노량진_제철해산물_TOP10/09_소재/tts`
   유사도 0.85 미만 문장은 대본을 고쳐 그 문장만 다시 생성합니다.
3. **효과음·BGM**: `09_소재/`에서 `python ../../../.claude/skills/ranking-video/scripts/make_audio_assets.py` → `09_소재/sfx/`
4. **렌더링** (ffmpeg 필요):
   ```
   python .claude/skills/ranking-video/scripts/render_video.py video_projects/노량진_제철해산물_TOP10/01_대본/대본데이터.json video_projects/노량진_제철해산물_TOP10 --tts video_projects/노량진_제철해산물_TOP10/09_소재/tts --img video_projects/노량진_제철해산물_TOP10/09_소재/img --sfx video_projects/노량진_제철해산물_TOP10/09_소재/sfx --work <임시폴더> --jobs 4
   ```
   먼저 `--until 175`로 샘플을 확인한 다음 전체를 렌더링합니다.
5. **메타데이터**: `make_credits.py 09_소재/img <프로젝트>` → `make_description.py <json> <프로젝트>`
6. 결과물: `08_완성영상/완성영상.mp4`(1080p), `…_완성본_720p.mp4`, `07_그래픽/07_썸네일틀/썸네일_VS.png`, `05_메타데이터/설명란_업로드용.txt`, `고정댓글.txt`

## 이미 끝난 것 (클라우드 세션)
- 자료 조사(`01_대본/조사표.md`, 네이버 블로그 최근 3개월 `블로그조사.tsv`), 대본 3,885자(약 9분 반)
- 그래픽 68장: 타이틀 카드, 제철 달력 정보 카드, 요약 카드, **VS 대결형 썸네일**
- 사진 검수 완료 77장(`09_소재/img`, 출처는 meta.json)
