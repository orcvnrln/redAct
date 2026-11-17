# VibeShield Desktop Shortcut Yaradici
# Windows Desktop-a ikon elave edir

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$DesktopPath = [Environment]::GetFolderPath("Desktop")
$ShortcutPath = Join-Path $DesktopPath "VibeShield Desktop.lnk"
$TargetPath = Join-Path $ScriptDir "start_vibeshield.bat"
$IconPath = "C:\Windows\System32\shell32.dll,14"  # Shield icon

Write-Host "VibeShield Desktop shortcut yaradilir..." -ForegroundColor Cyan

if (-not (Test-Path $TargetPath)) {
    Write-Host "[XETA] start_vibeshield.bat tapilmadi: $TargetPath" -ForegroundColor Red
    exit 1
}

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = $ScriptDir
$Shortcut.IconLocation = $IconPath
$Shortcut.Description = "VibeShield DevSecOps Desktop Panel"
$Shortcut.Save()

Write-Host "[OK] Shortcut yaradildi: $ShortcutPath" -ForegroundColor Green
Write-Host "`nDesktop-da 'VibeShield Desktop' ikonuna double-click edin" -ForegroundColor Yellow
