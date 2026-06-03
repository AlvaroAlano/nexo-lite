@echo off
setlocal enabledelayedexpansion

set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"

echo.
echo  =======================================
echo   Nexo Lite - Iniciando...
echo  =======================================
echo.

REM --- Verificacoes pre-start ---

if not exist "%BACKEND%\.venv\Scripts\python.exe" (
    echo  ERRO: Ambiente virtual nao encontrado.
    echo  Execute setup.bat primeiro.
    echo.
    pause
    exit /b 1
)

if not exist "%BACKEND%\.env" (
    echo  ERRO: backend\.env nao encontrado.
    echo  Execute setup.bat e configure o DATABASE_URL.
    echo.
    pause
    exit /b 1
)

if not exist "%FRONTEND%\node_modules" (
    echo  ERRO: node_modules nao encontrado.
    echo  Execute setup.bat primeiro.
    echo.
    pause
    exit /b 1
)

REM --- Aviso se .env ainda tem placeholder ---
findstr /i "YOUR-PASSWORD" "%BACKEND%\.env" >nul 2>&1
if not errorlevel 1 (
    echo  AVISO: backend\.env ainda tem valores de exemplo!
    echo  Configure DATABASE_URL com seus dados do Supabase.
    echo.
    echo  Abrir backend\.env agora? [S para sim, outra tecla para continuar]
    set /p OPEN="  Opcao: "
    if /i "!OPEN!"=="S" notepad "%BACKEND%\.env"
    echo.
)

REM --- Iniciar Backend na nova janela ---
echo  [1/2] Iniciando Backend  ^>  http://localhost:8000
start "Nexo Backend (FastAPI)" /d "%BACKEND%" cmd /k ".venv\Scripts\activate.bat && echo. && echo Backend: http://localhost:8000 ^| Docs: http://localhost:8000/docs && echo. && uvicorn app.main:app --reload --port 8000"

timeout /t 2 /nobreak >nul

REM --- Iniciar Frontend na nova janela ---
echo  [2/2] Iniciando Frontend ^>  http://localhost:5173
start "Nexo Frontend (Vite)" /d "%FRONTEND%" cmd /k "echo. && echo Frontend: http://localhost:5173 && echo. && npm run dev"

REM --- Abrir browser ---
echo.
echo  Aguardando servidores (5s)...
timeout /t 5 /nobreak >nul
start "" "http://localhost:5173"

echo.
echo  =======================================
echo   Sistema rodando!
echo.
echo   Frontend : http://localhost:5173
echo   Backend  : http://localhost:8000
echo   API Docs : http://localhost:8000/docs
echo.
echo   Feche as janelas "Backend" e "Frontend"
echo   para encerrar.
echo  =======================================
echo.
pause
