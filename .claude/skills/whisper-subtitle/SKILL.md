---
name: whisper-subtitle
description: "faster-whisper로 음성·영상을 받아써서 자막(srt)과 단어 타이밍(json)을 만들고, 대본과 대조해 발음이 틀린 문장을 찾는다. 내레이션 발음 검수, 참고 영상 대사 받아쓰기(너굴분석 보조), 쇼츠 자막 만들기에 쓴다. '받아써', '자막 만들어', '발음 검수', 'whisper', 'srt' 요청에 사용."
---

# faster-whisper 받아쓰기

```bash
python .claude/skills/whisper-subtitle/scripts/transcribe.py <음성/영상> --out <폴더> [--model medium] [--script 대본.txt]
```
- 결과: `<이름>.srt`(한 줄 최대 30자, R-T2), `<이름>.words.json`(단어별 시작·끝), `<이름>.txt`
- `--script` 를 주면 대본 줄과 받아쓰기를 맞춰 보고 `<이름>.check.tsv`(줄 번호, 일치율, 대본, 받아쓰기)를 쓴다. 일치율 0.85 미만은 다시 생성할 후보다.
- 모델: 클라우드 CPU는 `medium`(int8, 실시간의 약 0.5배 속도), 빠른 확인은 `small`. PC에 GPU가 있으면 `--device cuda --compute float16`, 가장 정확한 건 `large-v3`.
- 한국어 숫자는 아라비아 숫자로 받아쓴다("사백"→"400"). 대조할 때는 대본 화면 문장(숫자)과 읽기 문장(한글) 둘 다와 비교해 높은 쪽을 쓴다.

## 쓰임
- **발음 검수(필수)**: 새 내레이션은 전 문장을 대조한다. 낮은 문장은 다시 생성해 더 나은 쪽을 남긴다(`video_projects/경제2/금융의모든것/tools/tts_local.py check`가 같은 방식).
- **참고 영상 받아쓰기**: 너굴분석 때 대사 리듬(분당 글자 수, 문장 길이)을 잴 때. 받아쓴 원문을 우리 대본에 그대로 쓰지 않는다(저작권).
- **자막 파일**: neogul-edit은 대본에서 srt를 만들므로 보통 필요 없다. 대본 없는 영상(쇼츠, 인터뷰)에 쓴다.

## 주의
- 클라우드에서는 PyAV 버전 문제로 파일을 직접 넘기면 실패할 수 있어, 스크립트가 FFmpeg로 16kHz 음성을 뽑아 넘긴다.
- 모델은 처음 실행 때 Hugging Face에서 받는다(medium 약 1.5GB).
