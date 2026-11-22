@echo off
cd /d "C:\Users\Admin\.aside\u\0\sessions\2026-11-20_t4Rg5HxPgwDDQ8VU\tmp\stick_ko\engine"
set PATH=C:\Program Files\nodejs;%PATH%
echo START %TIME% > ..\render_b.log
call npx remotion render Voynich ..\out_b.mp4 --gl=angle --concurrency=4 >> ..\render_b.log 2>&1
echo END %TIME% >> ..\render_b.log
echo DONE>> ..\render_b.log
