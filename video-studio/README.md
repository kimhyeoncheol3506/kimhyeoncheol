# video-studio — 경제 영상 1세트 자동 제작

스크린샷 주제 → `project.json`(대본·장면) → **영상 + 썸네일 + 제목 + 설명란 + 태그 + 자막** 한 세트.
목소리는 Voicebox의 **여의도남자**(기본) / **여의도여자**(대화 상대).

## 목소리 엔진 (둘 중 하나, `--voice auto`가 자동 선택)
- **클라우드(모바일만으로 제작)**: `bash setup_cloud.sh` 1회(10~15분) → Qwen3-TTS 직접 구동. 여의도남자는 `assets/voices/여의도남자_기준음성.wav` 복제, 여의도여자는 Sohee 프리셋.
- **PC Voicebox**: 아래 PC 준비 후 Voicebox 앱을 켜 두면 자동으로 사용.

## PC 준비 (PC에서 직접 돌릴 때만, 최초 1회)
1. Python 3.10+ 와 ffmpeg 설치 (Windows: `winget install Gyan.FFmpeg`)
2. `pip install pillow`
3. Voicebox 앱 실행 + 여의도남자/여의도여자 프로필 확인 (`curl http://127.0.0.1:17493/profiles`)

## 실행
```bash
cd video-studio
python make_video.py projects/sample-rate-shorts/project.json          # 목소리 포함 완성본 (엔진 자동 선택)
python make_video.py projects/sample-rate-shorts/project.json --voice cloud   # 클라우드 엔진 지정
python make_video.py projects/sample-rate-shorts/project.json --preview-silent   # 목소리 없이 화면 미리보기
python make_video.py projects/sample-rate-shorts/project.json --thumb-only       # 썸네일·메타데이터만
```
결과: `projects/<이름>/output/` → `video.mp4`, `thumbnail.png`, `thumbnail_shorts.png`(쇼츠), `title.txt`, `description.txt`, `tags.txt`, `subtitles.srt`, `업로드정보.md`.
같은 대사의 음성은 `audio/`에 캐시되어 다시 생성하지 않습니다.

## project.json
```jsonc
{
  "format": "shorts",              // shorts(1080x1920) | long(1920x1080)
  "title": "...", "description": "...", "hashtags": [...], "tags": [...], "sources": [...],
  "header": ["상단 노랑 줄", "상단 흰 줄"],   // 쇼츠 고정 제목
  "channel": {"name": "채널명", "handle": "@핸들"},
  "speed": 1.05,                   // 쇼츠 1.05 권장(빠르면 기계음), 롱폼 1.0
  "voice_speed_by": {"여의도남자": 1.08},  // 목소리별 추가 배속 (롱폼 기본값)
  "bgm": "bgm.mp3",                // 선택: 저작권 확인된 음원, 자동으로 낮은 볼륨 믹스
  "thumbnail": {"theme": "blue|red|green|gold|dark", "emotion": "shock", "line1": "...", "line2": "...",
                "left": {"kind": "calendar", "text": "15일"}, "right": {"kind": "coin"}, "badge": "속보"},
  "scenes": [
    {"id": "s01", "text": "내레이션", "caption": "(선택) 자막을 다르게",
     "voice": "여의도남자|여의도여자", "instruct": "(여자만) 톤 지시", "pause": 0.15, "bg": "#F4E9D8",
     "visual": {"type": "mascot", "emotion": "worried", "pose": "point", "props": [{"kind": "doc", "text": "변동주기", "pos": "right"}], "say": "말풍선"}}
  ]
}
```
**visual 타입**: `mascot`(표정·포즈·소품·말풍선) · `dialogue`(남녀 대화, `context`=괄호 상황 자막) · `title` · `bignumber` · `bars` · `line` · `compare` · `checklist` · `flow` · `icons`
**표정**: neutral, happy, worried, shock, smug, think, angry, sad · **포즈**: normal, point, hands, shrug
**아이콘**: coin, house, calendar, arrow_up, arrow_down, bag, doc, lock, building, chart_up, chart_down, phone, won, flag_kr, flag_us

## 원칙
- 제작 규칙과 벤치마킹 분석: [STYLE_GUIDE.md](STYLE_GUIDE.md)
- 마스코트(둥근 안경·금색 넥타이 '여의도 김대리'와 '박과장')는 코드로 그린 오리지널 캐릭터
- 폰트: Pretendard, Black Han Sans (둘 다 SIL OFL, `assets/fonts/`에 라이선스 포함)
- Voicebox에 연결할 수 없으면 다른 TTS로 대체하지 않고 오류로 멈춤 (`--preview-silent`만 예외)
