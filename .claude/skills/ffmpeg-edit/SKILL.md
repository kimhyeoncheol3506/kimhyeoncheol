---
name: ffmpeg-edit
description: "FFmpeg로 영상·음성을 자르고, 붙이고, 크기·음량을 맞추고, 자막을 굽고, 프레임을 뽑아 확인한다. 경제2 파이프라인(neogul-edit) 앞뒤의 손질 작업 — 파트 이어 붙이기, 720p 전달본, 쇼츠용 세로 자르기, 엔진 클립 길이 맞추기, 음량 -16 LUFS 맞추기, 프레임 시트로 검수 — 에 쓴다. 'ffmpeg', '영상 자르기/붙이기', '음량 맞춰', '720p로', '세로로', '프레임 뽑아' 같은 요청에 사용."
---

# FFmpeg 편집·렌더

neogul-edit 렌더러도 내부에서 FFmpeg를 쓴다. 이 스킬은 그 **앞뒤 손질**용 레시피 모음이다. 새 영상을 처음부터 만들 때는 neogul-edit을 먼저 쓴다.

- 버전: 6.1 이상 (클라우드 6.1.1). 필터 파일은 7 이상 `-/filter_complex 파일`, 6.x `-filter_complex_script 파일`.
- 한글 경로·텍스트는 셸 인용 대신 파일(srt, ass, 필터 파일)로 넘긴다(neogul-edit "주의"와 같은 이유).
- 결과는 늘 `ffprobe`로 길이·해상도를, 프레임 시트로 화면을 확인한 뒤 넘긴다.

## 자주 쓰는 레시피

| 할 일 | 명령 |
|---|---|
| 길이·해상도 확인 | `ffprobe -v error -show_entries format=duration:stream=codec_type,width,height -of csv=p=0 in.mp4` |
| 구간 자르기(다시 인코딩, 정확) | `ffmpeg -ss 12.5 -to 22.5 -i in.mp4 -c:v libx264 -crf 18 -c:a aac out.mp4` |
| 같은 설정 파트 이어 붙이기(무손실) | `list.txt`에 `file 'part1.mp4'` 줄들 → `ffmpeg -f concat -safe 0 -i list.txt -c copy -movflags +faststart all.mp4` |
| 720p 전달본 | `ffmpeg -i in.mp4 -vf scale=1280:720 -c:v libx264 -preset veryfast -crf 24 -c:a aac -b:a 128k -movflags +faststart out_720p.mp4` |
| 음량 -16 LUFS(R-A3) 측정 | `ffmpeg -i in.mp4 -af ebur128 -f null - 2>&1 \| grep -A1 Integrated` |
| 음량 맞추기 | `ffmpeg -i in.mp4 -af loudnorm=I=-16:TP=-1.5:LRA=11 -c:v copy out.mp4` |
| 엔진 클립 마지막 프레임 늘리기 | `ffmpeg -i clip.mp4 -vf "tpad=stop_mode=clone:stop_duration=30" -an -c:v libx264 -crf 16 -pix_fmt yuv420p hold.mp4` |
| 쇼츠 세로(1080x1920) 가운데 자르기 | `ffmpeg -i in.mp4 -vf "crop=ih*9/16:ih,scale=1080:1920" -c:a copy short.mp4` |
| 쇼츠 세로(흐린 배경 + 원본 전체) | `ffmpeg -i in.mp4 -filter_complex "[0]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=30[b];[0]scale=1080:-2[f];[b][f]overlay=(W-w)/2:(H-h)/2" -c:a copy short.mp4` |
| 자막 굽기 | `ffmpeg -i in.mp4 -vf "subtitles=subs.srt:force_style='FontName=Pretendard,FontSize=22'" out.mp4` (폰트 폴더는 `:fontsdir=...`) |
| 말 빠르기 1.12배(여의도남자) | `ffmpeg -i v.wav -af atempo=1.12 v_fast.wav` |
| 무음 구간 찾기 | `ffmpeg -i v.wav -af silencedetect=n=-38dB:d=0.4 -f null - 2>&1 \| grep silence_` |
| 썸네일 후보 프레임 | `ffmpeg -ss 75 -i in.mp4 -frames:v 1 -q:v 2 thumb.jpg` |

## 검수용 프레임 시트

```bash
python .claude/skills/ffmpeg-edit/scripts/contact_sheet.py in.mp4 sheet.png --n 12 --cols 4
```
영상을 n등분한 지점의 프레임을 한 장에 모은다. 미리보기·최종 렌더·엔진 클립은 모두 이 시트로 직접 보고 글자 넘침, 검은 화면, 박스 위치를 확인한다.

## 규칙
- 원본은 덮어쓰지 않는다(새 파일로 쓰고 확인 후 교체).
- 이어 붙일 파일은 코덱·해상도·fps·음성 설정이 같아야 `-c copy`가 된다. 다르면 다시 인코딩.
- 최종 업로드본은 1080p, 음량 -16 LUFS(±1), `+faststart`.
