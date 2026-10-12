"""FinClose 데스크톱 앱 빌드(PyInstaller). 실행하는 OS용 앱이 만들어진다(Windows에서 빌드 → Windows 앱).

    python packaging/build_desktop.py

결과:
  Windows  dist/FinClose/FinClose.exe (+ 연습모드 실행.cmd)   → installer.iss로 설치 파일 생성
  macOS    dist/FinClose.app
  Linux    dist/FinClose/FinClose
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # finclose/
BACKEND = ROOT / "backend"
DIST_UI = ROOT / "frontend" / "dist"
SEP = ";" if sys.platform == "win32" else ":"


def make_icons(out: Path) -> dict[str, Path]:
    from PIL import Image
    src = Image.open(ROOT / "frontend" / "public" / "icon-512.png")
    ico, icns = out / "finclose.ico", out / "finclose.icns"
    src.save(ico, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    try:
        src.save(icns)
    except Exception:  # noqa: BLE001 — icns 미지원 Pillow면 생략
        icns = None  # type: ignore[assignment]
    return {"ico": ico, "icns": icns}


def main() -> None:
    for st in (sys.stdout, sys.stderr):
        try:
            st.reconfigure(encoding="utf-8", errors="replace")  # 영문 Windows 콘솔(cp1252)에서도 한글 출력
        except (AttributeError, ValueError):
            pass
    if not (DIST_UI / "index.html").exists():
        if shutil.which("npm"):
            subprocess.check_call("npm ci && npm run build", cwd=ROOT / "frontend", shell=True)
        else:
            sys.exit("frontend/dist가 없고 npm도 없습니다.")
    build = ROOT / "build"
    build.mkdir(exist_ok=True)
    icons = make_icons(build)
    if not (ROOT / "sample_data" / "history").exists():
        subprocess.check_call([sys.executable, "-m", "finclose.sample_data", str(ROOT / "sample_data")], cwd=BACKEND)
    icon = icons["ico"] if sys.platform == "win32" else (icons["icns"] or icons["ico"])
    args = [
        sys.executable, "-m", "PyInstaller", str(ROOT / "packaging" / "launcher.py"),
        "--name", "FinClose", "--noconfirm", "--clean", "--onedir",
        "--distpath", str(ROOT / "dist"), "--workpath", str(build / "pyi"), "--specpath", str(build),
        "--paths", str(BACKEND),
        "--add-data", f"{DIST_UI}{SEP}frontend/dist",
        "--add-data", f"{ROOT / 'sample_data'}{SEP}sample_data",
        "--add-data", f"{BACKEND / 'finclose' / 'templates'}{SEP}finclose/templates",
        "--collect-submodules", "uvicorn", "--collect-submodules", "finclose",
        "--collect-all", "pdfplumber", "--collect-all", "pypdfium2", "--collect-all", "pdfminer",
        "--hidden-import", "multipart", "--hidden-import", "python_multipart",
        "--icon", str(icon),
        "--exclude-module", "tkinter", "--exclude-module", "pytest",
    ]
    if sys.platform in ("win32", "darwin"):
        args.append("--windowed")              # 검은 콘솔 창 없이 실행
    if sys.platform == "darwin":
        args += ["--osx-bundle-identifier", "local.finclose.desktop"]
    subprocess.check_call(args, cwd=BACKEND)
    if sys.platform == "win32":
        out = ROOT / "dist" / "FinClose"
        (out / "연습모드 실행.cmd").write_text('@echo off\r\nstart "" "%~dp0FinClose.exe" --demo\r\n', encoding="cp949")
        shutil.copy(ROOT / "TUTORIAL.html", out / "사용설명서.html")
    print("빌드 완료:", ROOT / "dist")


if __name__ == "__main__":
    main()
