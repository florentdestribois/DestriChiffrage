Set-Location "C:\Users\tt\Documents\Developpement logiciel\DestriChiffrage"
Write-Host "=== Checking Python ===" -ForegroundColor Cyan
py --version

Write-Host "`n=== Checking PyInstaller ===" -ForegroundColor Cyan
py -m pip show pyinstaller

Write-Host "`n=== Starting Build ===" -ForegroundColor Cyan
py -m PyInstaller DestriChiffrage.spec --noconfirm 2>&1 | Tee-Object -FilePath "build_log.txt"

Write-Host "`n=== Build Complete ===" -ForegroundColor Cyan
if (Test-Path "dist\DestriChiffrage.exe") {
    Write-Host "SUCCESS: dist\DestriChiffrage.exe created!" -ForegroundColor Green
    Get-Item "dist\DestriChiffrage.exe" | Select-Object Name, Length, LastWriteTime
} else {
    Write-Host "FAILED: exe not found" -ForegroundColor Red
    Write-Host "Check build_log.txt for errors"
}
Read-Host "Press Enter to exit"
