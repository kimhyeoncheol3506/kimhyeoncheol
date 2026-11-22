# 공용: yt-dlp / ffmpeg 위치 찾기 (Windows winget 설치본, PATH, Linux 모두)
import glob, os, shutil, sys


def find(name, winget_pat):
    p = shutil.which(name)
    if p:
        return p
    hits = glob.glob(os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "WinGet", "Packages", winget_pat), recursive=True)
    if hits:
        return hits[0]
    sys.exit("%s 를 찾을 수 없습니다 (설치 필요)" % name)


YTDLP = find("yt-dlp", r"yt-dlp.yt-dlp*\yt-dlp.exe")
FFMPEG = find("ffmpeg", r"*FFmpeg*\**\bin\ffmpeg.exe")
FFD = os.path.dirname(FFMPEG)
