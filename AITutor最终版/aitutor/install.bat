@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================================
::  AITutor 一键安装脚本 (Windows)
::  自动检测环境 → 创建虚拟环境 → 安装依赖 → 配置 API Key
:: ============================================================

echo.
echo ╔══════════════════════════════════════════╗
echo ║   🤖 AI导师 安装程序 v2.1               ║
echo ║   基于多智能体协作的 AI 课程助教          ║
echo ╚══════════════════════════════════════════╝
echo.

cd /d "%~dp0"
set "SCRIPT_DIR=%~dp0"
set "VENV_DIR=%SCRIPT_DIR%.venv"

:: ---- 1. 检测 Python ----
echo 🔍 [1/5] 检测 Python 环境...
set "PYTHON="
for %%c in (python3.11 python3.12 python3 python) do (
    where %%c >nul 2>&1
    if !errorlevel!==0 (
        for /f "tokens=2" %%v in ('%%c --version 2^>^&1') do (
            set "ver=%%v"
        )
        for /f "tokens=1,2 delims=." %%a in ("!ver!") do (
            set "major=%%a"
            set "minor=%%b"
        )
        if !major! geq 3 if !minor! geq 11 (
            set "PYTHON=%%c"
            echo    ✅ 找到 %%c ^(版本 !ver!^)
            goto :found_python
        )
    )
)
:found_python
if "%PYTHON%"=="" (
    echo    ❌ 未找到 Python 3.11+，请先安装：
    echo       官网: https://www.python.org/downloads/
    echo       Microsoft Store 也可安装。
    pause
    exit /b 1
)

:: ---- 2. 创建虚拟环境 ----
echo.
echo 📦 [2/5] 创建虚拟环境...
if exist "%VENV_DIR%" (
    echo    ⚠️  .venv 已存在，跳过创建。
) else (
    "%PYTHON%" -m venv "%VENV_DIR%"
    if !errorlevel!==0 (
        echo    ✅ 虚拟环境创建完成。
    ) else (
        echo    ❌ 虚拟环境创建失败。
        pause
        exit /b 1
    )
)

call "%VENV_DIR%\Scripts\activate.bat"

:: ---- 3. 安装依赖 ----
echo.
echo 📥 [3/5] 安装 Python 依赖...
pip install -r "%SCRIPT_DIR%requirements.txt" --quiet
if !errorlevel!==0 (
    echo    ✅ 依赖安装成功。
) else (
    echo    ❌ 依赖安装失败，请检查网络连接。
    echo    你可以稍后手动运行：pip install -r requirements.txt
    pause
    exit /b 1
)

:: ---- 4. 配置 API Key ----
echo.
echo 🔑 [4/5] 配置 LLM API Key...
if exist "%SCRIPT_DIR%.env" (
    echo    ⚠️  .env 已存在，跳过配置。
    echo    如需修改请直接编辑 aitutor\.env
) else (
    copy "%SCRIPT_DIR%.env.example" "%SCRIPT_DIR%.env" >nul
    echo.
    set /p api_key="   请输入你的 API Key（回车跳过，稍后手动配置）: "
    if not "!api_key!"=="" (
        powershell -Command "(Get-Content '%SCRIPT_DIR%.env') -replace 'your-api-key-here', '!api_key!' | Set-Content '%SCRIPT_DIR%.env'"
        echo    ✅ API Key 已写入 .env
    ) else (
        echo    📝 已生成 .env 模板，请稍后编辑填入 API Key。
    )
)

:: ---- 5. 生成桌面快捷方式 ----
echo.
echo 🔗 [5/5] 生成快捷启动方式...
set "DESKTOP_FILE=%USERPROFILE%\Desktop\AITutor.bat"

(
echo @echo off
echo cd /d "%SCRIPT_DIR%"
echo if exist "%VENV_DIR%\Scripts\activate.bat" call "%VENV_DIR%\Scripts\activate.bat"
echo echo 🚀 启动 AITutor...
echo bash run.sh 2^>nul ^|^| (
echo     echo Bash 未安装，尝试直接启动...
echo     start "" python -m streamlit run frontend/app.py --server.port 8501
echo     cd backend
echo     start "" python -m uvicorn main:app --port 8000
echo )
echo echo.
echo echo ✅ 浏览器打开 http://localhost:8501
echo pause
) > "%DESKTOP_FILE%"

echo    ✅ 桌面快捷方式已创建：%DESKTOP_FILE%

:: ---- 完成 ----
echo.
echo ╔══════════════════════════════════════════╗
echo ║   🎉 安装完成！                         ║
echo ║                                          ║
echo ║   启动方式：                             ║
echo ║   1. 双击桌面 AITutor.bat               ║
echo ║   2. 终端运行：cd aitutor ^&^& bash run.sh ║
echo ║                                          ║
echo ║   浏览器打开 http://localhost:8501       ║
echo ╚══════════════════════════════════════════╝
echo.

pause
