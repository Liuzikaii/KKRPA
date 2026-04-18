@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion

echo ╔══════════════════════════════════════════════════╗
echo ║       KKRPA Desktop Build Script (Windows)      ║
echo ╚══════════════════════════════════════════════════╝
echo.

:: ─── 环境检查 ────────────────────────────────────────
echo [检查] 正在检查构建环境...

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Node.js，请先安装: https://nodejs.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node -v') do echo   Node.js: %%i

where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 npm
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('npm -v') do echo   npm: %%i

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.11+: https://www.python.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo   Python: %%i

echo   环境检查通过!
echo.

:: ─── 获取项目根目录 ──────────────────────────────────
set "ROOT_DIR=%~dp0"
:: 去掉末尾的反斜杠
if "%ROOT_DIR:~-1%"=="\" set "ROOT_DIR=%ROOT_DIR:~0,-1%"

:: ══════════════════════════════════════════════════════
:: Step 1: 构建前端
:: ══════════════════════════════════════════════════════
echo ══════════════════════════════════════════════════
echo  Step 1/3: 构建 Next.js 前端 (静态导出)
echo ══════════════════════════════════════════════════

cd /d "%ROOT_DIR%\frontend"
if %errorlevel% neq 0 (
    echo [错误] 找不到 frontend 目录
    pause
    exit /b 1
)

echo [1.1] 安装前端依赖...
call npm ci
if %errorlevel% neq 0 (
    echo [错误] npm ci 失败
    pause
    exit /b 1
)

echo [1.2] 构建静态文件...
call npm run build
if %errorlevel% neq 0 (
    echo [错误] 前端构建失败
    pause
    exit /b 1
)

echo [完成] 前端已构建 → frontend\out\
echo.

:: ══════════════════════════════════════════════════════
:: Step 2: 打包 Python 后端
:: ══════════════════════════════════════════════════════
echo ══════════════════════════════════════════════════
echo  Step 2/3: 打包 Python 后端 (PyInstaller)
echo ══════════════════════════════════════════════════

cd /d "%ROOT_DIR%\backend"

:: 创建虚拟环境（如不存在）
if not exist "venv" (
    echo [2.1] 创建 Python 虚拟环境...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
)

echo [2.2] 激活虚拟环境并安装依赖...
call venv\Scripts\activate.bat

pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo [错误] pip install 失败
    pause
    exit /b 1
)

echo [2.3] 运行 PyInstaller...
pyinstaller ^
    --name kkrpa-server ^
    --onefile ^
    --noconsole ^
    --hidden-import=app ^
    --hidden-import=app.main ^
    --hidden-import=app.config ^
    --hidden-import=app.database ^
    --hidden-import=app.models ^
    --hidden-import=app.models.user ^
    --hidden-import=app.models.workflow ^
    --hidden-import=app.models.task ^
    --hidden-import=app.models.schedule ^
    --hidden-import=app.api ^
    --hidden-import=app.api.auth ^
    --hidden-import=app.api.workflows ^
    --hidden-import=app.api.tasks ^
    --hidden-import=app.api.schedules ^
    --hidden-import=app.api.license ^
    --hidden-import=app.core ^
    --hidden-import=app.core.auth ^
    --hidden-import=app.core.edition ^
    --hidden-import=app.core.license ^
    --hidden-import=app.core.snowflake ^
    --hidden-import=app.engine ^
    --hidden-import=app.engine.executor ^
    --hidden-import=app.engine.nodes ^
    --hidden-import=app.engine.nodes.base ^
    --hidden-import=app.engine.nodes.python_node ^
    --hidden-import=app.engine.nodes.http_node ^
    --hidden-import=app.engine.nodes.condition_node ^
    --hidden-import=app.engine.nodes.loop_node ^
    --hidden-import=app.engine.nodes.delay_node ^
    --hidden-import=app.workers ^
    --hidden-import=app.workers.workflow_tasks ^
    --hidden-import=app.workers.scheduler ^
    --hidden-import=app.schemas ^
    --hidden-import=app.schemas.schemas ^
    --hidden-import=app.services ^
    --hidden-import=aiosqlite ^
    --hidden-import=sqlalchemy.dialects.sqlite ^
    --hidden-import=sqlalchemy.dialects.sqlite.aiosqlite ^
    --hidden-import=uvicorn ^
    --hidden-import=uvicorn.logging ^
    --hidden-import=uvicorn.loops ^
    --hidden-import=uvicorn.loops.auto ^
    --hidden-import=uvicorn.protocols ^
    --hidden-import=uvicorn.protocols.http ^
    --hidden-import=uvicorn.protocols.http.auto ^
    --hidden-import=uvicorn.protocols.http.h11_impl ^
    --hidden-import=uvicorn.protocols.http.httptools_impl ^
    --hidden-import=uvicorn.protocols.websockets ^
    --hidden-import=uvicorn.protocols.websockets.auto ^
    --hidden-import=uvicorn.lifespan ^
    --hidden-import=uvicorn.lifespan.on ^
    --hidden-import=uvicorn.lifespan.off ^
    --hidden-import=multipart ^
    --hidden-import=passlib.handlers.bcrypt ^
    --hidden-import=email_validator ^
    --hidden-import=jose ^
    --hidden-import=apscheduler ^
    --hidden-import=apscheduler.schedulers.asyncio ^
    --hidden-import=apscheduler.triggers.interval ^
    --hidden-import=apscheduler.triggers.cron ^
    --hidden-import=croniter ^
    --hidden-import=httpx ^
    --hidden-import=RestrictedPython ^
    --hidden-import=snowflake ^
    --add-data "app;app" ^
    --clean ^
    --noconfirm ^
    run_server.py

if %errorlevel% neq 0 (
    echo [错误] PyInstaller 打包失败
    call deactivate
    pause
    exit /b 1
)

call deactivate
echo [完成] 后端已打包 → backend\dist\kkrpa-server.exe
echo.

:: ══════════════════════════════════════════════════════
:: Step 3: 构建 Electron 桌面应用
:: ══════════════════════════════════════════════════════
echo ══════════════════════════════════════════════════
echo  Step 3/3: 构建 Electron 桌面应用
echo ══════════════════════════════════════════════════

cd /d "%ROOT_DIR%\electron"

echo [3.1] 安装 Electron 依赖...
call npm ci
if %errorlevel% neq 0 (
    echo [错误] Electron npm ci 失败
    pause
    exit /b 1
)

echo [3.2] 打包 Windows .exe 安装包...
call npm run build:win
if %errorlevel% neq 0 (
    echo [错误] electron-builder 打包失败
    pause
    exit /b 1
)

echo [完成] Electron 应用已打包
echo.

:: ══════════════════════════════════════════════════════
:: 完成
:: ══════════════════════════════════════════════════════
echo.
echo ╔══════════════════════════════════════════════════╗
echo ║            构建完成! Build Complete!             ║
echo ╠══════════════════════════════════════════════════╣
echo ║                                                  ║
echo ║  安装包位置:  dist\KKRPA Setup *.exe             ║
echo ║                                                  ║
echo ║  直接双击 .exe 即可安装运行!                     ║
echo ║                                                  ║
echo ╚══════════════════════════════════════════════════╝
echo.

:: 打开输出目录
if exist "%ROOT_DIR%\dist" (
    echo 正在打开输出目录...
    explorer "%ROOT_DIR%\dist"
)

pause
