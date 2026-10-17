"""1단계: 해외 반응 원본 소스 탐색 · 스코어링 · 다운로드.

- YouTube Data API v3 (키가 있으면) 또는 yt-dlp 검색(키 없을 때)으로 후보 수집
- "구독자는 적은데 조회수가 터진" 영상을 점수화해서 랭킹
- 선택한 영상의 mp4 / 자막(타임스탬프) / 메타데이터 / 썸네일 / 대표 프레임 10장 / 많이 본 구간(heatmap) 저장
"""
from __future__ import annotations

import math
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
import yt_dlp

from config import INPUT_DIR, ffmpeg_bin, settings
from utils import console, load_json, media_duration, run_ffmpeg, save_json, slugify

DISCOVERY_DIR = INPUT_DIR / "_discovery"


# ════════════════════════════════════════════════════════════════
#  데이터 모델 + 스코어링
# ════════════════════════════════════════════════════════════════
@dataclass
class Candidate:
    video_id: str
    title: str
    channel_id: str
    channel_title: str
    published_at: str            # ISO8601 UTC
    views: int = 0
    likes: int = 0
    comments: int = 0
    subscribers: int | None = None
    duration_s: float = 0.0
    thumbnail_url: str = ""
    query: str = ""
    # 계산 값
    age_hours: float = 0.0
    views_per_hour: float = 0.0
    views_per_sub: float = 0.0
    engagement: float = 0.0
    score: float = 0.0
    flags: list[str] = field(default_factory=list)

    @property
    def url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.video_id}"

    @property
    def is_short(self) -> bool:
        return 0 < self.duration_s <= 180


def compute_score(c: Candidate, now: datetime | None = None) -> Candidate:
    """가성비 점수(0~100).

    - 조회 속도(시간당 조회수)      45%  : log10, 시간당 1만 회 = 만점
    - 구독자 대비 조회수 배수        40%  : log10, 100배 = 만점  ← "구독자 적은데 터진" 핵심 지표
    - 참여율((좋아요+댓글×3)/조회수) 15%  : 8% = 만점
    """
    now = now or datetime.now(timezone.utc)
    published = datetime.fromisoformat(c.published_at.replace("Z", "+00:00"))
    c.age_hours = max((now - published).total_seconds() / 3600, 1.0)
    c.views_per_hour = c.views / c.age_hours
    subs = max(c.subscribers or 0, 100)
    c.views_per_sub = c.views / subs
    c.engagement = (c.likes + 3 * c.comments) / max(c.views, 1)

    clamp = lambda x: max(0.0, min(1.0, x))  # noqa: E731
    s_speed = clamp(math.log10(max(c.views_per_hour, 1)) / 4)
    s_ratio = clamp(math.log10(c.views_per_sub + 1) / 2)
    s_eng = clamp(c.engagement / 0.08)
    c.score = round(100 * (0.45 * s_speed + 0.40 * s_ratio + 0.15 * s_eng), 1)

    c.flags = []
    if c.views_per_sub >= 3:
        c.flags.append("🔥떡상")
    if c.views_per_hour >= 1000:
        c.flags.append("⚡급상승")
    if c.is_short:
        c.flags.append("📱쇼츠")
    return c


def filter_and_rank(
    cands: list[Candidate], *, max_subs: int, min_views: int, days: int, min_age_hours: float
) -> list[Candidate]:
    now = datetime.now(timezone.utc)
    out = []
    seen = set()
    for c in cands:
        if c.video_id in seen:
            continue
        seen.add(c.video_id)
        compute_score(c, now)
        if c.subscribers is not None and c.subscribers > max_subs:
            continue
        if c.views < min_views:
            continue
        if not (min_age_hours <= c.age_hours <= days * 24):
            continue
        out.append(c)
    return sorted(out, key=lambda c: -c.score)


# ════════════════════════════════════════════════════════════════
#  검색: YouTube Data API v3
# ════════════════════════════════════════════════════════════════
def _iso_duration_to_s(value: str) -> float:
    import re

    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", value or "")
    if not m:
        return 0.0
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


def search_youtube_api(query: str, *, days: int, max_results: int = 50,
                       region: str | None = None, lang: str | None = None) -> list[Candidate]:
    """search.list(100 유닛) + videos.list(1) + channels.list(1). 하루 기본 할당량 10,000 유닛."""
    from googleapiclient.discovery import build

    yt = build("youtube", "v3", developerKey=settings.youtube_api_key, cache_discovery=False)
    after = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    params = dict(q=query, part="id", type="video", order="viewCount",
                  publishedAfter=after, maxResults=min(max_results, 50))
    if region:
        params["regionCode"] = region
    if lang:
        params["relevanceLanguage"] = lang
    ids = [it["id"]["videoId"] for it in yt.search().list(**params).execute().get("items", [])]
    if not ids:
        return []

    videos = yt.videos().list(part="snippet,statistics,contentDetails", id=",".join(ids)).execute()["items"]
    ch_ids = list({v["snippet"]["channelId"] for v in videos})
    subs: dict[str, int | None] = {}
    for i in range(0, len(ch_ids), 50):
        chs = yt.channels().list(part="statistics", id=",".join(ch_ids[i:i + 50])).execute()
        for ch in chs.get("items", []):
            st = ch["statistics"]
            subs[ch["id"]] = None if st.get("hiddenSubscriberCount") else int(st.get("subscriberCount", 0))

    out = []
    for v in videos:
        sn, st = v["snippet"], v.get("statistics", {})
        thumbs = sn.get("thumbnails", {})
        best = (thumbs.get("maxres") or thumbs.get("high") or thumbs.get("medium") or {}).get("url", "")
        out.append(Candidate(
            video_id=v["id"], title=sn["title"], channel_id=sn["channelId"],
            channel_title=sn["channelTitle"], published_at=sn["publishedAt"],
            views=int(st.get("viewCount", 0)), likes=int(st.get("likeCount", 0)),
            comments=int(st.get("commentCount", 0)), subscribers=subs.get(sn["channelId"]),
            duration_s=_iso_duration_to_s(v["contentDetails"].get("duration", "")),
            thumbnail_url=best, query=query,
        ))
    return out


# ════════════════════════════════════════════════════════════════
#  검색: yt-dlp (API 키 없을 때)
# ════════════════════════════════════════════════════════════════
class _QuietLogger:
    """yt-dlp 오류를 화면에 쏟지 않고 모아 둔다(봇 차단 안내용)."""

    last_error = ""

    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        _QuietLogger.last_error = msg


BOT_HINT = ("유튜브가 봇 확인을 요구합니다. .env 에 YOUTUBE_API_KEY 를 넣거나, "
            "YTDLP_COOKIES_FROM_BROWSER=chrome (또는 edge/firefox) 를 설정하세요.")


def _ydl_base_opts() -> dict:
    opts = {"quiet": True, "no_warnings": True, "noprogress": True, "logger": _QuietLogger()}
    browser = os.getenv("YTDLP_COOKIES_FROM_BROWSER", "").strip()
    if browser:
        opts["cookiesfrombrowser"] = (browser,)
    cookie_file = os.getenv("YTDLP_COOKIES_FILE", "").strip()
    if cookie_file:
        opts["cookiefile"] = cookie_file
    return opts


# YouTube 검색 필터(sp) = 조회수순 정렬 + 업로드 기간 + 동영상만 (protobuf → base64)
_SP_BY_PERIOD = [(1, "CAMSBAgCEAE%3D"), (7, "CAMSBAgDEAE%3D"), (31, "CAMSBAgEEAE%3D"), (365, "CAMSBAgFEAE%3D")]


def search_ytdlp(query: str, *, days: int, max_results: int = 30, workers: int = 6) -> list[Candidate]:
    from urllib.parse import quote_plus

    sp = next((code for limit, code in _SP_BY_PERIOD if days <= limit), _SP_BY_PERIOD[-1][1])
    url = f"https://www.youtube.com/results?search_query={quote_plus(query)}&sp={sp}"
    flat = {**_ydl_base_opts(), "extract_flat": True, "playlistend": max_results}
    with yt_dlp.YoutubeDL(flat) as ydl:
        res = ydl.extract_info(url, download=False)
    ids = [e["id"] for e in (res or {}).get("entries", []) if e and e.get("id")]

    def detail(vid: str) -> Candidate | None:
        try:
            with yt_dlp.YoutubeDL({**_ydl_base_opts(), "skip_download": True}) as ydl:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={vid}", download=False)
        except Exception:
            return None
        ts = info.get("timestamp") or info.get("release_timestamp")
        if ts:
            published = datetime.fromtimestamp(ts, tz=timezone.utc)
        elif info.get("upload_date"):
            published = datetime.strptime(info["upload_date"], "%Y%m%d").replace(tzinfo=timezone.utc)
        else:
            return None
        if published < datetime.now(timezone.utc) - timedelta(days=days):
            return None
        return Candidate(
            video_id=vid, title=info.get("title", ""), channel_id=info.get("channel_id", ""),
            channel_title=info.get("channel", "") or info.get("uploader", ""),
            published_at=published.isoformat(), views=info.get("view_count") or 0,
            likes=info.get("like_count") or 0, comments=info.get("comment_count") or 0,
            subscribers=info.get("channel_follower_count"), duration_s=info.get("duration") or 0,
            thumbnail_url=info.get("thumbnail", ""), query=query,
        )

    _QuietLogger.last_error = ""
    with ThreadPoolExecutor(max_workers=workers) as pool:
        found = [c for c in pool.map(detail, ids) if c]
    if ids and not found and "not a bot" in _QuietLogger.last_error:
        console.print(f"  [yellow]{BOT_HINT}[/]")
    return found


# ════════════════════════════════════════════════════════════════
#  탐색 진입점
# ════════════════════════════════════════════════════════════════
def discover(queries: list[str], *, days: int = 7, max_subs: int = 50_000, min_views: int = 3_000,
             min_age_hours: float = 6, per_query: int = 50, region: str | None = None,
             label: str | None = None, thumbs: int = 10) -> tuple[list[Candidate], Path]:
    """검색어 여러 개를 돌려 후보를 모으고 랭킹 → JSON 저장 + 상위 썸네일 다운로드."""
    use_api = bool(settings.youtube_api_key)
    console.print(f"[bold]소스 탐색[/] ({'YouTube Data API' if use_api else 'yt-dlp 검색'}) "
                  f"· 최근 {days}일 · 구독자 ≤ {max_subs:,} · 조회수 ≥ {min_views:,}")
    pool: list[Candidate] = []
    for q in queries:
        try:
            got = (search_youtube_api(q, days=days, max_results=per_query, region=region) if use_api
                   else search_ytdlp(q, days=days, max_results=min(per_query, 30)))
            console.print(f"  · '{q}' → {len(got)}개")
            pool += got
        except Exception as exc:
            console.print(f"  [red]· '{q}' 검색 실패: {exc}[/]")

    ranked = filter_and_rank(pool, max_subs=max_subs, min_views=min_views,
                             days=days, min_age_hours=min_age_hours)
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    name = f"{stamp}_{slugify(label or queries[0])}"
    out_dir = DISCOVERY_DIR / name
    save_json(out_dir / "ranking.json", {
        "queries": queries, "days": days, "max_subs": max_subs, "min_views": min_views,
        "created": datetime.now().isoformat(timespec="seconds"),
        "results": [{**asdict(c), "url": c.url} for c in ranked],
    })
    _download_thumbnails(ranked[:thumbs], out_dir / "thumbnails")
    return ranked, out_dir


def _download_thumbnails(cands: list[Candidate], folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    for i, c in enumerate(cands, 1):
        urls = [c.thumbnail_url,
                f"https://i.ytimg.com/vi/{c.video_id}/maxresdefault.jpg",
                f"https://i.ytimg.com/vi/{c.video_id}/hqdefault.jpg"]
        for u in filter(None, urls):
            try:
                r = requests.get(u, timeout=15)
                if r.ok and len(r.content) > 2000:
                    (folder / f"{i:02d}_{c.video_id}.jpg").write_bytes(r.content)
                    break
            except requests.RequestException:
                continue


# ════════════════════════════════════════════════════════════════
#  원본 다운로드 (영상 + 자막 + 메타 + 프레임)
# ════════════════════════════════════════════════════════════════
SUB_PRIORITY = ["ko", "en", "en-orig", "en-US", "en-GB"]


def source_dir(video_id: str) -> Path:
    return INPUT_DIR / video_id


def download_source(video_id_or_url: str, *, max_height: int = 1080, frames: int = 10,
                    force: bool = False) -> Path:
    """원본 1개를 input_source/<id>/ 에 저장하고 폴더 경로를 돌려준다. 이미 받았으면 건너뜀."""
    url = video_id_or_url if video_id_or_url.startswith("http") else f"https://www.youtube.com/watch?v={video_id_or_url}"
    with yt_dlp.YoutubeDL({**_ydl_base_opts(), "skip_download": True}) as ydl:
        info = ydl.extract_info(url, download=False)
    vid = info["id"]
    folder = source_dir(vid)
    meta_path = folder / "meta.json"
    if meta_path.exists() and (folder / "video.mp4").exists() and not force:
        console.print(f"[dim]이미 다운로드됨: {folder}[/]")
        return folder
    folder.mkdir(parents=True, exist_ok=True)

    # 자막 언어 선택: 영상 원어 + 한국어 + 영어 (수동 자막 우선)
    manual = info.get("subtitles") or {}
    auto = info.get("automatic_captions") or {}
    want = [info.get("language")] + SUB_PRIORITY
    langs = [l for l in dict.fromkeys(filter(None, want)) if l in manual or l in auto][:3]

    console.print(f"[bold]다운로드[/] {info.get('title')}  (자막: {', '.join(langs) or '없음'})")
    opts = {
        **_ydl_base_opts(),
        "outtmpl": str(folder / "video.%(ext)s"),
        "format": f"bv*[height<={max_height}][ext=mp4]+ba[ext=m4a]/b[height<={max_height}][ext=mp4]/bv*[height<={max_height}]+ba/b",
        "merge_output_format": "mp4",
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitleslangs": langs,
        "subtitlesformat": "json3/vtt/best",
        "writethumbnail": True,
        "postprocessors": [{"key": "FFmpegThumbnailsConvertor", "format": "jpg"}],
    }
    opts["ffmpeg_location"] = ffmpeg_bin()
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])

    video = _normalize_video_name(folder)
    transcript = build_transcript(folder, langs)
    save_json(folder / "transcript.json", transcript)
    (folder / "transcript.txt").write_text(
        "\n".join(f"[{_ts(s['start'])}] {s['text']}" for s in transcript["segments"]), encoding="utf-8")

    duration = media_duration(video)
    frame_paths = extract_keyframes(video, folder / "frames", count=frames, duration=duration)
    meta = {
        "video_id": vid, "url": info.get("webpage_url", url), "title": info.get("title"),
        "description": (info.get("description") or "")[:3000], "channel": info.get("channel"),
        "channel_url": info.get("channel_url"), "subscribers": info.get("channel_follower_count"),
        "views": info.get("view_count"), "likes": info.get("like_count"),
        "comments": info.get("comment_count"), "upload_date": info.get("upload_date"),
        "duration": duration, "language": info.get("language"), "tags": info.get("tags") or [],
        "chapters": [{"start": c["start_time"], "end": c["end_time"], "title": c["title"]}
                     for c in info.get("chapters") or []],
        "highlights": heatmap_peaks(info.get("heatmap") or []),
        "frames": [p.name for p in frame_paths],
        "transcript_lang": transcript.get("lang"),
    }
    save_json(meta_path, meta)
    console.print(f"[green]✔ 저장 완료[/] {folder}")
    return folder


def _normalize_video_name(folder: Path) -> Path:
    target = folder / "video.mp4"
    if target.exists():
        return target
    for p in folder.glob("video.*"):
        if p.suffix.lower() in {".mp4", ".mkv", ".webm", ".mov"}:
            if p.suffix.lower() == ".mp4":
                p.rename(target)
            else:  # 컨테이너만 mp4 로 변환
                run_ffmpeg(["-i", p, "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", target])
                p.unlink()
            return target
    raise FileNotFoundError(f"영상 파일을 찾지 못했습니다: {folder}")


def heatmap_peaks(heatmap: list[dict], top: int = 6) -> list[dict]:
    """'가장 많이 다시 본 구간' 상위 N개 (서로 15초 이상 떨어진 것만)."""
    peaks: list[dict] = []
    for h in sorted(heatmap, key=lambda h: -h.get("value", 0)):
        if all(abs(h["start_time"] - p["start"]) > 15 for p in peaks):
            peaks.append({"start": round(h["start_time"], 1), "end": round(h["end_time"], 1),
                          "intensity": round(h.get("value", 0), 3)})
        if len(peaks) >= top:
            break
    return sorted(peaks, key=lambda p: p["start"])


def extract_keyframes(video: Path, out_dir: Path, *, count: int = 10, duration: float | None = None) -> list[Path]:
    """영상 전체에서 고르게 대표 프레임 N장 (앞뒤 5%는 인트로/엔딩이라 제외)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    duration = duration or media_duration(video)
    paths = []
    for i in range(count):
        t = duration * (0.05 + 0.9 * (i + 0.5) / count)
        p = out_dir / f"frame_{i + 1:02d}_{int(t)}s.jpg"
        run_ffmpeg(["-ss", f"{t:.2f}", "-i", video, "-frames:v", "1", "-q:v", "2", p])
        paths.append(p)
    return paths


# ─────────────────────────── 자막 파싱 ───────────────────────────
def build_transcript(folder: Path, langs: list[str]) -> dict:
    """다운로드된 자막 중 우선순위가 가장 높은 것을 [{start, end, text}] 로 변환."""
    files = list(folder.glob("video.*.json3")) + list(folder.glob("video.*.vtt"))
    by_lang = {f.name.split(".")[-2]: f for f in files}
    for lang in langs + list(by_lang):
        f = by_lang.get(lang)
        if not f:
            continue
        segs = parse_json3(f) if f.suffix == ".json3" else parse_vtt(f)
        if segs:
            return {"lang": lang, "segments": merge_segments(segs)}
    return {"lang": None, "segments": []}


def parse_json3(path: Path) -> list[dict]:
    data = load_json(path)
    out = []
    for ev in data.get("events", []):
        text = "".join(s.get("utf8", "") for s in ev.get("segs") or []).replace("\n", " ").strip()
        if not text:
            continue
        start = ev.get("tStartMs", 0) / 1000
        out.append({"start": start, "end": start + ev.get("dDurationMs", 0) / 1000, "text": text})
    return out


def parse_vtt(path: Path) -> list[dict]:
    import re

    out: list[dict] = []
    blocks = path.read_text(encoding="utf-8", errors="replace").split("\n\n")
    tre = re.compile(r"(\d+:)?(\d+):(\d+[.,]\d+)\s+-->\s+(\d+:)?(\d+):(\d+[.,]\d+)")
    last = ""
    for b in blocks:
        lines = b.strip().splitlines()
        tl = next((l for l in lines if "-->" in l), None)
        if not tl or not (m := tre.search(tl)):
            continue
        g = m.groups()
        start = int((g[0] or "0:")[:-1]) * 3600 + int(g[1]) * 60 + float(g[2].replace(",", "."))
        end = int((g[3] or "0:")[:-1]) * 3600 + int(g[4]) * 60 + float(g[5].replace(",", "."))
        text_lines = [re.sub(r"<[^>]+>", "", l).strip() for l in lines[lines.index(tl) + 1:]]
        # 자동 자막의 '롤링' 중복 줄 제거
        new = [l for l in text_lines if l and l != last]
        if not new:
            continue
        last = text_lines[-1]
        out.append({"start": start, "end": end, "text": " ".join(new)})
    return out


def merge_segments(segs: list[dict], max_len: float = 8.0) -> list[dict]:
    """짧게 쪼개진 자막을 최대 max_len 초 단위 문장 덩어리로 합쳐 프롬프트 길이를 줄인다."""
    merged: list[dict] = []
    for s in segs:
        if merged and s["start"] - merged[-1]["start"] < max_len and not merged[-1]["text"].endswith((".", "?", "!")):
            merged[-1]["text"] += " " + s["text"]
            merged[-1]["end"] = max(merged[-1]["end"], s["end"])
        else:
            merged.append({"start": round(s["start"], 2), "end": round(s["end"], 2), "text": s["text"]})
    return merged


def _ts(sec: float) -> str:
    m, s = divmod(int(sec), 60)
    return f"{m:02d}:{s:02d}"


def import_local(path: str | Path, *, frames: int = 10, title: str | None = None) -> Path:
    """내가 가진 영상 파일(직접 촬영본, 허락받은 원본 등)을 소스로 등록. 같은 폴더의 .srt/.vtt 자막도 함께 읽는다."""
    path = Path(path).expanduser().resolve()
    vid = "local_" + slugify(path.stem, 30)
    folder = source_dir(vid)
    folder.mkdir(parents=True, exist_ok=True)
    video = folder / "video.mp4"
    if path.suffix.lower() == ".mp4":
        shutil.copy2(path, video)
    else:
        run_ffmpeg(["-i", path, "-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac", video])

    segments: list[dict] = []
    for ext in (".vtt", ".srt"):
        sub = path.with_suffix(ext)
        if sub.exists():
            segments = merge_segments(parse_vtt(sub))  # SRT 도 타임라인 형식이 같아 그대로 파싱 가능
            break
    save_json(folder / "transcript.json", {"lang": "local" if segments else None, "segments": segments})
    duration = media_duration(video)
    frame_paths = extract_keyframes(video, folder / "frames", count=frames, duration=duration)
    save_json(folder / "meta.json", {
        "video_id": vid, "url": str(path), "title": title or path.stem, "description": "", "channel": "로컬 파일",
        "channel_url": "", "subscribers": None, "views": None, "likes": None, "comments": None,
        "upload_date": None, "duration": duration, "language": None, "tags": [], "chapters": [],
        "highlights": [], "frames": [p.name for p in frame_paths], "transcript_lang": None,
    })
    console.print(f"[green]✔ 로컬 소스 등록[/] {folder}")
    return folder
