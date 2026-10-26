@echo off
echo ==========================================
echo Запуск Умного кредитного кабинета
echo ==========================================

where ollama > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ⏳ Ollama не найдена. Начинаем автоматическую загрузку...
    
    REM 
    powershell -Command "Invoke-WebRequest -Uri 'https://ollama.com/download/OllamaSetup.exe' -OutFile 'OllamaSetup.exe'"
    
    if exist OllamaSetup.exe (
        echo ✅ Установщик скачан. Запускаем установку...
        echo Пожалуйста, подтвердите установку в открывшемся окне (нужны права администратора).
        start /wait OllamaSetup.exe
        
        REM 
        timeout /t 5 /nobreak > nul
        
        REM 
        del OllamaSetup.exe
    ) else (
        echo Не удалось скачать установщик.
        echo Открываем страницу скачивания в браузере...
        start https://ollama.com/download/windows
        pause
        exit /b 1
    )
    
    echo Ollama установлена.
)

REM 
curl -s http://localhost:11434 > nul
if %ERRORLEVEL% NEQ 0 (
    echo Запускаем Ollama...
    start /B ollama serve
    timeout /t 5 /nobreak > nul
)

ollama list | findstr "qwen3.5:4b" > nul
if %ERRORLEVEL% NEQ 0 (
    echo Скачиваем модель qwen3.5:4b. Подождите...
    ollama pull qwen3.5:4b
)

echo Запускаем Docker...
docker-compose up --build
pause