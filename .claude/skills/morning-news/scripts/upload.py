# -*- coding: utf-8 -*-
"""월급쟁이 재테크 스킬 채널 자동 업로드 (YouTube Data API v3).
사용:
  python upload.py --auth            최초 1회: 브라우저에서 채널 계정으로 로그인/승인 -> token.json 저장, 채널명 출력
  python upload.py <작업폴더>         upload.json 기준으로 롱폼+쇼츠 즉시 공개 업로드 (중복 방지)
비밀파일: C:\\Users\\Admin\\Videos\\morning-news\\secrets\\client_secret.json, token.json
"""
import json, os, sys, time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

ROOT = r"C:\Users\Admin\Videos\morning-news"
SEC = os.path.join(ROOT, "secrets")
CLIENT = os.path.join(SEC, "client_secret.json")
TOKEN = os.path.join(SEC, "token.json")
LEDGER = os.path.join(ROOT, "uploaded.json")
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly"]
EXPECT_CHANNEL = os.environ.get("NEWS_CHANNEL", "월급쟁이 재테크 스킬")


def creds(interactive=False):
    c = None
    if os.path.exists(TOKEN):
        c = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    if c and c.expired and c.refresh_token:
        try:
            c.refresh(Request())
        except Exception as e:
            print("토큰 갱신 실패:", e); c = None
    if not c or not c.valid:
        if not interactive:
            sys.exit("[오류] 유튜브 인증이 필요합니다. PC에서 `python upload.py --auth` 를 실행해 채널 계정으로 승인하세요.")
        if not os.path.exists(CLIENT):
            sys.exit("[오류] %s 가 없습니다 (Google Cloud OAuth 데스크톱 클라이언트 JSON)." % CLIENT)
        flow = InstalledAppFlow.from_client_secrets_file(CLIENT, SCOPES)
        c = flow.run_local_server(port=8765, prompt="consent", access_type="offline", open_browser=os.environ.get("NEWS_NO_BROWSER") != "1")
    os.makedirs(SEC, exist_ok=True)
    open(TOKEN, "w", encoding="utf-8").write(c.to_json())
    return c


def channel_name(yt):
    r = yt.channels().list(part="snippet", mine=True).execute()
    return [(i["id"], i["snippet"]["title"]) for i in r.get("items", [])]


def upload(yt, path, meta, thumb=None):
    body = {"snippet": {"title": meta["title"][:100], "description": meta["description"][:4900], "tags": meta.get("tags", []),
                        "categoryId": "25", "defaultLanguage": "ko", "defaultAudioLanguage": "ko"},
            "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False, "containsSyntheticMedia": False}}
    # 규칙(사용자 2026-11-22): 썸네일 없이 공개 업로드 절대 금지.
    # 비공개로 올리고 -> 썸네일 성공 시에만 공개 전환. 실패하면 비공개 유지 + THUMB_FAIL 출력.
    if not thumb or not os.path.exists(thumb):
        sys.exit("[중단] 썸네일 파일이 없습니다. 썸네일 없이 업로드하지 않습니다(사용자에게 먼저 물어볼 것).")
    req = yt.videos().insert(part="snippet,status", body=body, media_body=MediaFileUpload(path, chunksize=8 * 1024 * 1024, resumable=True))
    resp = None
    while resp is None:
        st, resp = req.next_chunk()
        if st:
            print("  업로드 %d%%" % int(st.progress() * 100), flush=True)
    vid = resp["id"]
    try:
        yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(thumb)).execute()
    except Exception as e:
        print("  THUMB_FAIL 썸네일 설정 실패, 비공개로 둡니다:", str(e)[:200], flush=True)
        return vid
    yt.videos().update(part="status", body={"id": vid, "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False, "containsSyntheticMedia": False}}).execute()
    print("  썸네일 OK -> 공개 전환", flush=True)
    return vid


def main():
    if sys.argv[1:] == ["--auth"]:
        yt = build("youtube", "v3", credentials=creds(True))
        print("승인된 채널:", channel_name(yt)); return
    wd = os.path.abspath(sys.argv[1])
    meta = json.load(open(os.path.join(wd, "upload.json"), encoding="utf-8"))
    ledger = json.load(open(LEDGER, encoding="utf-8")) if os.path.exists(LEDGER) else {}
    yt = build("youtube", "v3", credentials=creds(False))
    chs = channel_name(yt)
    if not any(t == EXPECT_CHANNEL for _, t in chs):
        sys.exit("[중단] 승인된 채널이 '%s'가 아닙니다: %s  -> --auth 를 다시 실행해 올바른 채널을 고르세요." % (EXPECT_CHANNEL, chs))
    for kind in [k for k in ("shorts", "long") if k in meta]:
        key = "%s_%s" % (meta["date"], kind)
        if key in ledger:
            print("[건너뜀] 이미 업로드됨:", key, "https://youtu.be/" + ledger[key]); continue
        m = meta[kind]
        print("업로드 중:", kind, m["title"], flush=True)
        vid = upload(yt, os.path.join(wd, m["file"]), m, os.path.join(wd, m["thumb"]) if m.get("thumb") else None)
        ledger[key] = vid
        json.dump(ledger, open(LEDGER, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        print("  완료: https://youtu.be/%s" % vid, flush=True)


if __name__ == "__main__":
    main()
