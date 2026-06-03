@echo off
setlocal enabledelayedexpansion

set "ROOT=%~dp0"
set "BACKEND=%ROOT%backend"
set "FRONTEND=%ROOT%frontend"

echo.
echo  =======================================
echo   Nexo Lite - Setup Inicial
echo  =======================================
echo.

REM --- 1. Verificar Python ---
echo [1/4] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERRO: Python nao encontrado no PATH.
    echo  Instale em https://python.org e marque "Add to PATH".
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo        %%v encontrado.

REM --- 2. Criar ambiente virtual ---
echo.
echo [2/4] Criando ambiente virtual Python...
if exist "%BACKEND%\.venv\Scripts\python.exe" (
    echo        .venv ja existe - pulando.
) else (
    python -m venv "%BACKEND%\.venv"
    if errorlevel 1 (
        echo  ERRO: Falha ao criar .venv.
        pause
        exit /b 1
    )
    echo        .venv criado com sucesso.
)

REM --- 3. Instalar dependencias Python ---
echo.
echo [3/4] Instalando dependencias Python (aguarde)...
"%BACKEND%\.venv\Scripts\pip.exe" install -r "%BACKEND%\requirements.txt" --prefer-binary -q
if errorlevel 1 (
    echo  ERRO: Falha no pip install. Rodando com saida completa:
    "%BACKEND%\.venv\Scripts\pip.exe" install -r "%BACKEND%\requirements.txt" --prefer-binary
    pause
    exit /b 1
)
echo        Dependencias Python instaladas.

REM --- 4. Instalar dependencias frontend ---
echo.
echo [4/4] Instalando dependencias do frontend (npm install)...
pushd "%FRONTEND%"
call npm install --loglevel=error
if errorlevel 1 (
    echo  ERRO: Falha no npm install.
    popd
    pause
    exit /b 1
)
popd
echo        node_modules instalado.

REM --- Criar .env se nao existir ---
echo.
if not exist "%BACKEND%\.env" (
    copy "%BACKEND%\.env.example" "%BACKEND%\.env" >nul
    echo  AVISO: backend\.env criado a partir do .env.example
    echo.
    echo  IMPORTANTE: Abra o arquivo backend\.env e substitua:
    echo    [YOUR-PASSWORD]    pela senha do seu banco no Supabase
    echo    [YOUR-PROJECT-REF] pelo identificador do seu projeto
    echo.
    echo  Exemplo de URL completa:
    echo  DATABASE_URL=postgresql+psycopg://postgres:minhaSenha@
    echo    db.abcdefgh.supabase.co:5432/postgres
) else (
    echo  .env ja existe - nao sobrescrito.
)

echo.
echo  =======================================
echo   Setup concluido!
echo.
echo   Proximos passos:
echo   1. Configure backend\.env
echo   2. Execute start.bat
echo  =======================================
echo.
pause
