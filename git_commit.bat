@echo off
cd /d "d:\MCP's\ICS-Explotation-MCP"
echo === Git Status ===
git status
echo.
echo === Adding files ===
git add .
echo.
echo === Committing ===
git commit -m "Sync documentation: fix tool counts, add Modbus docs, update to v1.2.0"
echo.
echo === Pushing ===
git push origin main
echo.
echo === Done ===
pause