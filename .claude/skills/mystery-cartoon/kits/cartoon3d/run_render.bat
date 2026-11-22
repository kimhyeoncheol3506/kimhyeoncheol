@echo off
cd /d "C:\Users\Admin\.aside\u\0\sessions\2026-11-20_t4Rg5HxPgwDDQ8VU\tmp\A_proj"
set PATH=C:\Program Files\nodejs;%PATH%
set CHROME=C:\Users\Admin\AppData\Local\ms-playwright\chromium-1248\chrome-win64\chrome.exe
node render.mjs frames "0-352" > render.log 2>&1
echo DONE>> render.log
