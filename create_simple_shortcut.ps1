# VibeShield Sadə UI - Desktop Shortcut

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "VibeShield.lnk"
$TargetPath = Join-Path $ScriptDir "START_SIMPLE.bat"
$IconPath = "C:\Windows\System32\shell32.dll,14"

Write-Host "VibeShield shortcut yaradilir..." -ForegroundColor Cyan

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = $ScriptDir
$Shortcut.IconLocation = $IconPath
$Shortcut.Description = "VibeShield Security Scanner - Sadə UI"
$Shortcut.Save()

Write-Host "[OK] Desktop-da 'VibeShield' ikonu yaradildi!" -ForegroundColor Green
Write-Host "`nIkona double-click edin" -ForegroundColor Yellow
