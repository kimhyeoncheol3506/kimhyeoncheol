"""데스크톱 실행기: 더블클릭 한 번으로 서버를 켜고 전용 앱 창을 연다. 창을 닫으면 서버도 꺼진다.

python -m finclose.desktop            업무 모드 (데이터: 문서/FinClose/data)
python -m finclose.desktop --demo     연습 모드 (데이터: 문서/FinClose/practice-data, 과거 이력 자동 생성)

창: Microsoft Edge 또는 Chrome의 '앱 모드'(주소창 없는 전용 창)를 쓴다. 둘 다 없으면 기본 브라우저를 열고,
화면이 보내는 신호(heartbeat)가 끊기면 종료한다. 서버는 항상 127.0.0.1(이 PC)에서만 열린다.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

APP_NAME = "FinClose"
PORTS = {"work": 8732, "practice": 8733}         # 고정 포트: 앱 설치(PWA)·화면 설정이 매번 유지되도록
HEARTBEAT_TIMEOUT = 180                          # 기본 브라우저 모드에서 화면 신호가 끊긴 뒤 종료까지(초)
FIRST_BEAT_GRACE = 600
log = logging.getLogger("finclose.desktop")


# ----------------------------------------------------------------------------- 공통 도우미

def home_dir() -> Path:
    from .config import user_home_dir
    return Path(os.environ["FINCLOSE_HOME"]) if os.environ.get("FINCLOSE_HOME") else user_home_dir()


QUIET = False   # --no-window(점검·자동 테스트)에서는 오류 창을 띄우지 않음


def notify_error(msg: str) -> None:
    """콘솔이 없는 앱에서도 사용자가 볼 수 있게 오류 창을 띄운다."""
    log.error(msg)
    if QUIET:
        print(msg, file=sys.stderr)
        return
    try:
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.user32.MessageBoxW(0, msg, APP_NAME, 0x10)
            return
        if sys.platform == "darwin":
            subprocess.run(["osascript", "-e", f'display dialog {json.dumps(msg, ensure_ascii=False)} with title "{APP_NAME}" buttons {{"확인"}}'],
                           check=False, timeout=120)
            return
    except Exception:  # noqa: BLE001 — 오류 창 실패는 무시하고 아래 출력으로
        pass
    print(msg, file=sys.stderr)


def setup_logging(home: Path) -> Path:
    (home / "logs").mkdir(parents=True, exist_ok=True)
    path = home / "logs" / "finclose.log"
    h = RotatingFileHandler(path, maxBytes=2_000_000, backupCount=3, encoding="utf-8")
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root = logging.getLogger()
    root.handlers[:] = [h]
    root.setLevel(logging.INFO)
    # 창 모드(콘솔 없음) 실행 파일은 stdout/stderr가 None이다 → 로그 파일로 돌린다
    if sys.stdout is None or sys.stderr is None:
        f = open(path, "a", encoding="utf-8", buffering=1)  # noqa: SIM115 — 프로세스 수명 동안 유지
        sys.stdout = sys.stdout or f
        sys.stderr = sys.stderr or f
    return path


def port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def pick_port(preferred: int) -> int:
    if port_free(preferred):
        return preferred
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def health(port: int, timeout: float = 1.0) -> dict[str, Any] | None:
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=timeout) as r:  # noqa: S310 — 로컬 고정 주소
            return json.loads(r.read().decode())
    except Exception:  # noqa: BLE001
        return None


def open_folder(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    if sys.platform == "win32":
        os.startfile(str(path))  # type: ignore[attr-defined]  # noqa: S606
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])


# ----------------------------------------------------------------------------- 앱 창(브라우저 앱 모드)

def find_browser() -> str | None:
    if os.environ.get("FINCLOSE_BROWSER"):
        return os.environ["FINCLOSE_BROWSER"]
    cands: list[str] = []
    if sys.platform == "win32":
        for base in (os.environ.get("ProgramFiles(x86)"), os.environ.get("ProgramFiles"), os.environ.get("LOCALAPPDATA")):
            if base:
                cands += [rf"{base}\Microsoft\Edge\Application\msedge.exe", rf"{base}\Google\Chrome\Application\chrome.exe"]
    elif sys.platform == "darwin":
        cands += ["/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
                  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                  str(Path.home() / "Applications/Google Chrome.app/Contents/MacOS/Google Chrome")]
    else:
        cands += [shutil.which(n) or "" for n in ("microsoft-edge", "google-chrome", "chromium", "chromium-browser")]
    return next((c for c in cands if c and Path(c).exists()), None)


def launch_window(url: str, profile: Path) -> subprocess.Popen | None:
    exe = find_browser()
    if not exe:
        return None
    profile.mkdir(parents=True, exist_ok=True)
    args = [exe, f"--app={url}", f"--user-data-dir={profile}", "--no-first-run", "--no-default-browser-check",
            "--window-size=1440,920", "--disable-features=Translate"]
    log.info("앱 창 실행: %s", exe)
    return subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ----------------------------------------------------------------------------- 연습 자료

def ensure_practice_files(home: Path) -> Path:
    from .config import BASE_DIR
    from . import sample_data
    dest = home / "연습용 파일"
    if not dest.exists():
        src = BASE_DIR / "sample_data"
        if src.exists():
            shutil.copytree(src, dest, ignore=shutil.ignore_patterns("history"))
        else:
            sample_data.generate_all(dest)
            shutil.rmtree(dest / "history", ignore_errors=True)
    return dest


# ----------------------------------------------------------------------------- 실행

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="FinClose", description="FinClose 데스크톱 실행기")
    ap.add_argument("--demo", action="store_true", help="연습 모드(별도 데이터 폴더 + 과거 이력 자동 생성)")
    ap.add_argument("--no-window", action="store_true", help="창을 열지 않고 서버만 실행(점검용)")
    ap.add_argument("--port", type=int, default=None)
    a = ap.parse_args(argv)

    global QUIET
    QUIET = a.no_window
    mode = "practice" if a.demo else "work"
    home = home_dir()
    try:
        home.mkdir(parents=True, exist_ok=True)
        logfile = setup_logging(home)
    except OSError as e:
        notify_error(f"FinClose 폴더를 만들 수 없습니다: {home}\n{e}")
        return 1
    data_dir = home / ("practice-data" if a.demo else "data")
    os.environ["FINCLOSE_DATA_DIR"] = str(data_dir)
    os.environ["FINCLOSE_HOST"] = "127.0.0.1"
    url_of = lambda p: f"http://127.0.0.1:{p}/"  # noqa: E731

    # 이미 켜져 있으면 창만 다시 연다(같은 데이터를 두 프로그램이 동시에 쓰지 않도록)
    state_file = data_dir / "desktop.json"
    try:
        prev = json.loads(state_file.read_text(encoding="utf-8"))
        h = health(prev["port"])
        if h and h.get("desktop", {}).get("mode") == mode:
            log.info("이미 실행 중(포트 %s) — 창만 엽니다.", prev["port"])
            if not a.no_window and not launch_window(url_of(prev["port"]), home / f".window-{mode}"):
                webbrowser.open(url_of(prev["port"]))
            return 0
    except (OSError, ValueError, KeyError):
        pass

    port = a.port or pick_port(PORTS[mode])
    practice_dir = ensure_practice_files(home)
    stop = threading.Event()
    desktop_info: dict[str, Any] = {
        "mode": mode, "home": str(home), "data_dir": str(data_dir), "practice_files": str(practice_dir),
        "log_file": str(logfile), "last_beat": None, "stop": stop, "open_folder": open_folder, "fallback": False,
    }
    try:
        import uvicorn

        from .api import create_app
        from .config import load_settings
        settings = load_settings()
        settings.port = port
        app = create_app(settings, desktop=desktop_info)
        if a.demo:
            from .config import BASE_DIR
            from .seed_demo import seed
            seed(app.state.svc, BASE_DIR / "sample_data" if (BASE_DIR / "sample_data" / "history").exists()
                 else home / ".practice-source", log=log.info)
    except Exception as e:  # noqa: BLE001 — 사용자에게 보여 줄 시작 실패
        log.exception("시작 실패")
        notify_error(f"FinClose를 시작하지 못했습니다.\n\n{type(e).__name__}: {e}\n\n자세한 기록: {logfile}")
        return 1

    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_config=None, access_log=False))
    t = threading.Thread(target=server.run, name="finclose-server", daemon=True)
    t.start()
    for _ in range(300):
        if server.started or not t.is_alive():
            break
        time.sleep(0.05)
    if not server.started:
        notify_error(f"FinClose 서버를 시작하지 못했습니다(포트 {port}).\n자세한 기록: {logfile}")
        return 1
    state_file.write_text(json.dumps({"port": port, "pid": os.getpid(), "mode": mode}), encoding="utf-8")
    url = url_of(port)
    log.info("FinClose %s 모드 시작: %s (데이터 %s)", mode, url, data_dir)
    print(f"FinClose 실행 중: {url}  (데이터: {data_dir})", flush=True)

    proc = None
    if not a.no_window:
        proc = launch_window(url, home / f".window-{mode}")
        if proc is None:
            desktop_info["fallback"] = True
            webbrowser.open(url)

    def watch_window() -> None:
        assert proc is not None
        started = time.time()
        proc.wait()
        if time.time() - started < 5:
            # 기존 브라우저 프로세스로 넘겨진 경우: 창 감시 대신 화면 신호로 종료 판단
            log.info("앱 창 프로세스가 바로 끝남 → 화면 신호 감시 모드")
            desktop_info["fallback"] = True
            return
        log.info("앱 창이 닫혀 종료합니다.")
        stop.set()

    def watch_heartbeat() -> None:
        started = time.time()
        while not stop.wait(5):
            if not desktop_info["fallback"]:
                continue
            last = desktop_info["last_beat"]
            if last is None and time.time() - started > FIRST_BEAT_GRACE:
                log.info("화면 연결이 없어 종료합니다.")
                stop.set()
            elif last is not None and time.time() - last > HEARTBEAT_TIMEOUT:
                log.info("화면 신호가 끊겨 종료합니다.")
                stop.set()

    if proc is not None:
        threading.Thread(target=watch_window, daemon=True).start()
    if not a.no_window:
        threading.Thread(target=watch_heartbeat, daemon=True).start()

    try:
        while not stop.wait(0.5):
            if not t.is_alive():
                break
    except KeyboardInterrupt:
        pass
    server.should_exit = True
    t.join(timeout=10)
    try:
        state_file.unlink()
    except OSError:
        pass
    if proc is not None and proc.poll() is None:
        proc.terminate()
    log.info("FinClose 종료")
    return 0


if __name__ == "__main__":
    sys.exit(main())
