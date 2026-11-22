param([string]$Title = "작업 완료", [string]$Message = "쇼츠가 완성됐어요")
# Windows 알림(트레이 풍선). Claude Code에서: powershell -File notify.ps1 -Title "..." -Message "..."
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
$n = New-Object System.Windows.Forms.NotifyIcon
$n.Icon = [System.Drawing.SystemIcons]::Information
$n.Visible = $true
$n.ShowBalloonTip(10000, $Title, $Message, [System.Windows.Forms.ToolTipIcon]::Info)
Start-Sleep -Seconds 11
$n.Dispose()
