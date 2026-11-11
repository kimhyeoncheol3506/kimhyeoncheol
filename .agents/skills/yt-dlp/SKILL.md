---
name: yt-dlp
description: Download videos and extract audio from various platforms using yt-dlp. Use when user provides a video URL, asks to download a video, or when conversation contains video links from YouTube, Twitter/X, Vimeo, TikTok, Instagram, etc.
---

# yt-dlp Video Downloader Skill

This skill provides tools for downloading videos and extracting audio from various platforms using yt-dlp.

## Features

- Download videos from multiple platforms (YouTube, Twitter/X, Vimeo, TikTok, Instagram, Facebook, etc.)
- Extract audio from videos
- Auto-detect video URLs in conversations
- Support for different quality settings and formats

## Usage Patterns

### 1. Command-based Download

When user explicitly asks to download a video:
```
User: Download this video https://youtube.com/watch?v=...
```

**Action**: Extract URL and call download script

### 2. Auto-detection in Conversations

When conversation contains video URLs:
```
User: Check out this video https://twitter.com/... and let me know what you think
```

**Action**: Detect video URL, ask user if they want to download it

### 3. Audio Extraction

When user wants to extract audio only:
```
User: Extract the audio from https://youtu.be/...
```

**Action**: Use audio extraction script

## Available Scripts

Note: Scripts are located in the `scripts/` directory

### download_video.py

Main video downloader with quality and format options.

**Usage**:
```bash
# Download video
scripts/download_video.py <url> -o <output_dir>

# Download with specific quality
scripts/download_video.py <url> --quality 720p
scripts/download_video.py <url> --quality audio  # For audio only

# Custom format selector
scripts/download_video.py <url> --format "bestvideo[height<=1080]+bestaudio/best"

# Extract info only
scripts/download_video.py <url> --info-only
```

**Quality options**: `best`, `1080p`, `720p`, `480p`, `audio`

### extract_audio.py

Extract audio from videos in various formats.

**Usage**:
```bash
# Extract as MP3 (default)
/scripts/extract_audio.py <url> -o <output_dir>

# Extract as M4A
/scripts/extract_audio.py <url> --format m4a

# Custom quality
/scripts/extract_audio.py <url> --quality 320
```

**Formats**: `mp3`, `m4a`, `opus`, `flac`, `wav`

### extract_urls.py

Extract video URLs from text or files.

**Usage**:
```bash
# Extract from text argument
/scripts/extract_urls.py "Check https://youtube.com/watch?v=..."

# Extract from file
/scripts/extract_urls.py <file_path>

# Read from stdin
cat file.txt | /scripts/extract_urls.py
```

## Video Platform Support

The skill recognizes URLs from:
- YouTube (youtube.com, youtu.be)
- Twitter/X (twitter.com, x.com)
- Vimeo (vimeo.com)
- TikTok (tiktok.com)
- Instagram (instagram.com)
- Facebook (facebook.com, fb.watch)
- Twitch (twitch.tv, clips.twitch.tv)
- Dailymotion (dailymotion.com)
- Reddit (reddit.com)
- Streamable (streamable.com)
- And many more supported by yt-dlp

## Workflow

### When User Provides Video URL

1. Extract URL from user's input using `extract_urls.py`
2. Confirm with user what action to take:
   - Download video
   - Extract audio
   - Show video info
3. Execute appropriate script based on user's choice
4. Notify user of success/failure and file location

### When Auto-detecting URLs

1. Scan conversation text with `extract_urls.py` (can process stdin)
2. If video URLs found, ask user: "I found video URLs in this conversation. Would you like me to download them?"
3. If yes, proceed with download workflow
4. If no, continue with conversation

### Handling Multiple URLs

- For single URL: Direct download
- For multiple URLs: Ask user if they want to download all or select specific ones
- Provide option to download as playlist if URLs are from the same source

## Quality and Format Selection

When user doesn't specify preferences:
- Default to best available quality
- For audio: Default to MP3 at 192kbps

When options needed:
```bash
# Ask user for quality preference if not specified
# Options: best (default), 1080p, 720p, 480p, audio

# Ask for format if extracting audio
# Options: mp3 (default), m4a, opus, flac, wav
```

## Error Handling

Common issues and solutions:

1. **yt-dlp not installed**:
   - Check with `yt-dlp --version`
   - Install with `pip install yt-dlp` or `brew install yt-dlp`

2. **ffmpeg not installed** (required for format conversion):
   - Install with `brew install ffmpeg` (macOS)
   - Or `apt install ffmpeg` (Linux)

3. **Video not available**:
   - Check if URL is accessible
   - Some videos may require authentication
   - Age-restricted content may need cookies

4. **Network errors**:
   - Retry download
   - Check internet connection

## Dependencies

- `yt-dlp`: Main video downloader
- `ffmpeg`: Audio/video processing (required for format conversion)
- `python3` with standard library

All scripts are self-contained and use only built-in Python modules.

## 우리 환경 메모 (2026-11-11, 현철님 채널 작업용)
- 설치: `npx skills add https://github.com/lwmxiaobei/yt-dlp-skill --skill yt-dlp` (`.agents/skills/yt-dlp`, `.claude/skills/yt-dlp`는 링크). yt-dlp 본체는 `pip install -U yt-dlp`.
- **클라우드 세션에서 유튜브 영상 다운로드는 막힌다** ("Sign in to confirm you're not a bot"). 그래도 되는 것:
  - 자막: `yt-dlp --js-runtimes node --skip-download --write-auto-subs --sub-langs ko -o sub <URL>` → 대본·구조 분석
  - 썸네일·대표 프레임: `https://i.ytimg.com/vi/<ID>/maxresdefault.jpg`, `.../1.jpg`·`2.jpg`·`3.jpg` (영상 25·50·75% 지점 작은 프레임)
  - 제목·길이·채널: `yt-dlp --js-runtimes node --print "%(title)s | %(duration)s | %(channel)s" <URL>`
- 영상 원본이 꼭 필요하면(컷 리듬 분석 `tools/scene_split.py`, 프레임 비교): 현철님 PC 세션(데스크톱 앱·remote-control)에서 이 스킬 스크립트로 받거나, 현철님이 파일을 직접 첨부. 첨부 영상이 오면 그 영상을 최우선 참고.
- 받은 참고 영상은 저장소에 커밋하지 않는다(저작권·용량). 작업 폴더는 `/tmp/claude-0/hft/ref/` 같은 임시 위치.
