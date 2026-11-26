# 여의도여자 재녹음 약속 (PC ↔ 클라우드)

브랜치: `claude/exciting-curie-w62fz4`. 대상: 04~13편.

## PC가 읽는 것
`video_projects/월재스/<편>/voice_lines.json`
```json
[{"id":"L0001","text":"TTS에 넣을 문장(숫자·단위·영문 약어를 한글 읽기로 푼 것)","speed":1.0,"sid":0,"disp":"화면 자막 문장(참고용)"}]
```
- 순서 = 렌더 엔진의 문장 순서. `id`는 L0001부터, `sid`(0부터)는 엔진 내부 번호(PC는 무시해도 됨).
- `text`만 Voicebox에 넣는다. `speed`는 1.0, 강조 문장만 0.95.

## PC가 올리는 것
- `video_projects/월재스/<편>/voice_yeouido/<id>.wav` (48kHz mono 권장. 다른 형식이어도 클라우드가 변환)
- 한 편이 끝나면 `voice_yeouido/DONE` (빈 파일)
- 앞뒤 무음은 자동으로 잘라 내므로 신경 쓰지 않아도 된다.

## 클라우드가 하는 것 (`_tools/yeouido_render.py <편>` 또는 `--scan`)
1. Whisper 받아쓰기 대조(일치율 0.85 미만 = 의심).
2. 의심 문장이 있으면 `voice_yeouido/RERECORD.json` 을 푸시하고 렌더하지 않는다.
   `[{"id":"L0042","text":"…","disp":"…","heard":"받아쓴 내용","score":0.71}]` (파일이 빠진 문장은 `"reason":"파일 없음"`)
   → **PC는 그 id의 wav를 다시 만들어 덮어쓰고, RERECORD.json 을 지운 커밋을 푸시**한다. 그러면 다시 검수한다.
3. 통과하면 새 음성 길이에 맞춰 자막·화면 타이밍을 다시 정렬해 렌더하고,
   `release/<편>/<편>_1080p.mp4` 교체 + 설명란 목차 타임스탬프만 갱신 + `release/<편>/VOICE_YEOUIDO` 빈 파일 푸시.
   썸네일·제목·설명 문구·고정댓글은 바꾸지 않는다.

업로드·게시는 클라우드가 하지 않는다.
