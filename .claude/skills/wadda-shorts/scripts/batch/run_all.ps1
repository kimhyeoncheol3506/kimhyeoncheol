$env:PYTHONIOENCODING = "utf-8"
Set-Location $PSScriptRoot
# 첫 다운로드가 끝날 때까지 대기
while (Get-CimInstance Win32_Process -Filter "Name='python.exe'" | Where-Object { $_.CommandLine -match 'dl\.py' }) { Start-Sleep 10 }
"== 추가 구간 다운로드"
python -u dl.py | Select-String "FAIL|120|132" | ForEach-Object { $_.Line }
"== 렌더 시작"
python -u batch.py 2>&1 | Select-String "저장|건너뜀|Error|실패|Traceback" | ForEach-Object { $_.Line }
"== 끝"
