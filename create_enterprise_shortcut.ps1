# Create desktop shortcut for VibeShield Enterprise
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\VibeShield Enterprise.lnk")
$Shortcut.TargetPath = "python.exe"
$Shortcut.Arguments = "vibeshield_enterprise.py"
$Shortcut.WorkingDirectory = "$PSScriptRoot\desktop_app"
$Shortcut.IconLocation = "shell32.dll,21"
$Shortcut.Description = "VibeShield Enterprise Security Scanner"
$Shortcut.Save()
Write-Host "Desktop shortcut created: VibeShield Enterprise" -ForegroundColor Green
