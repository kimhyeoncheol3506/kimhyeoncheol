"""데스크톱 실행기: 창 없이(--no-window) 서버를 띄워 시작·중복 실행·연습 모드·종료를 확인한다."""
import json
import logging
import threading
import time
import urllib.request
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from finclose import desktop
from finclose.api import create_app

HDR = {"X-FinClose-User": quote("이담당"), "X-FinClose-Role": "preparer", "Content-Type": "application/json"}


def _post(port, path):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", data=b"{}", headers=HDR, method="POST")
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.loads(r.read())


@pytest.fixture()
def desk_env(tmp_path, monkeypatch):
    monkeypatch.setenv("FINCLOSE_HOME", str(tmp_path / "home"))
    monkeypatch.delenv("FINCLOSE_DATA_DIR", raising=False)
    root = logging.getLogger()
    saved = root.handlers[:]
    yield tmp_path / "home"
    root.handlers[:] = saved


def _start(args):
    out = {}
    t = threading.Thread(target=lambda: out.setdefault("rc", desktop.main(args)), daemon=True)
    t.start()
    return t, out


def _wait(port, t):
    for _ in range(200):
        h = desktop.health(port, timeout=0.3)
        if h:
            return h
        assert t.is_alive(), "실행기가 시작 중 종료됨"
        time.sleep(0.05)
    raise AssertionError("서버가 뜨지 않음")


def test_work_mode_start_second_instance_and_shutdown(desk_env):
    port = desktop.pick_port(18732)
    t, out = _start(["--no-window", "--port", str(port)])
    h = _wait(port, t)
    assert h["desktop"]["mode"] == "work"
    assert h["data_dir"] == str(desk_env / "data")
    assert (desk_env / "연습용 파일" / "bond_2026-09").is_dir()          # 연습 파일 복사
    assert not (desk_env / "연습용 파일" / "history").exists()
    assert (desk_env / "logs" / "finclose.log").exists()
    state = json.loads((desk_env / "data" / "desktop.json").read_text())
    assert state["port"] == port
    # 두 번째 실행: 새 서버를 띄우지 않고 바로 끝남
    assert desktop.main(["--no-window"]) == 0
    assert _post(port, "/api/desktop/heartbeat")["ok"]
    assert _post(port, "/api/desktop/shutdown")["ok"]
    t.join(timeout=15)
    assert not t.is_alive() and out["rc"] == 0
    assert not (desk_env / "data" / "desktop.json").exists()
    assert desktop.health(port, timeout=0.3) is None


def test_practice_mode_is_separate_and_seeded(desk_env):
    port = desktop.pick_port(18733)
    t, out = _start(["--demo", "--no-window", "--port", str(port)])
    h = _wait(port, t)
    assert h["desktop"]["mode"] == "practice"
    assert h["data_dir"] == str(desk_env / "practice-data")
    req = urllib.request.Request(f"http://127.0.0.1:{port}/api/runs", headers=HDR)
    runs = json.loads(urllib.request.urlopen(req, timeout=10).read())
    assert sum(r["status"] == "FINALIZED" for r in runs) == 4                # 과거 이력 4건
    _post(port, "/api/desktop/shutdown")
    t.join(timeout=15)
    assert out["rc"] == 0
    assert not (desk_env / "data").exists()                                   # 업무 데이터 폴더는 건드리지 않음


def test_desktop_endpoints_absent_in_server_mode(settings):
    c = TestClient(create_app(settings))
    assert c.get("/api/health").json()["desktop"] is None
    assert c.post("/api/desktop/shutdown", json={}, headers=HDR).status_code == 404


def test_open_folder_whitelist(settings, tmp_path):
    opened = []
    info = {"mode": "work", "home": str(tmp_path), "data_dir": str(tmp_path / "d"), "practice_files": str(tmp_path / "p"),
            "log_file": "x", "fallback": False, "last_beat": None, "stop": threading.Event(), "open_folder": opened.append}
    c = TestClient(create_app(settings, desktop=info))
    assert c.post("/api/desktop/open-folder", json={"which": "practice"}, headers=HDR).status_code == 200
    assert c.post("/api/desktop/open-folder", json={"which": "../../etc"}, headers=HDR).status_code == 400
    assert [str(p) for p in opened] == [str(tmp_path / "p")]
    # 사용자 지정 헤더 없이는 거부(다른 웹사이트가 몰래 종료시키지 못함)
    assert c.post("/api/desktop/shutdown", json={}).status_code in (403,)
    assert not info["stop"].is_set()
