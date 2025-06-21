@echo off
chcp 65001 >nul
title TranslateNovelAI Build Script

echo.
echo 🏗️ TranslateNovelAI Build Script
echo ========================================
echo.

:: Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python không được tìm thấy!
    echo Vui lòng cài đặt Python và thêm vào PATH
    pause
    exit /b 1
)

:: Kiểm tra pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip không được tìm thấy!
    pause
    exit /b 1
)

echo ✅ Python và pip đã sẵn sàng
echo.

:: Menu lựa chọn
echo Chọn loại build:
echo 1. Build file exe đơn (khuyến nghị)
echo 2. Build thành thư mục
echo 3. Cài đặt dependencies
echo 4. Thoát
echo.
set /p choice="Nhập lựa chọn (1-4): "

if "%choice%"=="1" goto build_onefile
if "%choice%"=="2" goto build_directory
if "%choice%"=="3" goto install_deps
if "%choice%"=="4" goto end
echo ❌ Lựa chọn không hợp lệ!
goto menu

:install_deps
echo.
echo 📦 Cài đặt dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Lỗi cài đặt dependencies!
    pause
    exit /b 1
)
echo ✅ Đã cài đặt dependencies thành công!
echo.
pause
goto menu

:build_onefile
echo.
echo 🚀 Bắt đầu build file exe đơn...
python build.py
goto check_result

:build_directory
echo.
echo 🚀 Bắt đầu build thành thư mục...
python build.py --directory
goto check_result

:check_result
if errorlevel 1 (
    echo.
    echo ❌ Build thất bại!
    echo Vui lòng kiểm tra lỗi ở trên
    pause
    exit /b 1
) else (
    echo.
    echo 🎉 Build thành công!
    echo 📦 File exe có thể được tìm thấy trong thư mục dist/
    if exist "TranslateNovelAI.exe" (
        echo 📦 Hoặc file: TranslateNovelAI.exe
    )
    echo.
    echo Bạn có muốn mở thư mục chứa file exe không? (y/n)
    set /p open_folder=""
    if /i "%open_folder%"=="y" (
        if exist "dist" (
            explorer dist
        ) else (
            explorer .
        )
    )
)

:end
echo.
echo 👋 Cảm ơn bạn đã sử dụng TranslateNovelAI Build Script!
pause 