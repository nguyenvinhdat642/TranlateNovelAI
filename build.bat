@echo off
chcp 65001 >nul
title TranslateNovelAI - Build Script

echo.
echo ===============================================
echo 🤖 TranslateNovelAI - Build to EXE
echo ===============================================
echo.

python build_exe.py

pause 