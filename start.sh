#!/bin/bash
echo "=========================================="
echo "Запуск Умного кредитного кабинета"
echo "=========================================="

if ! command -v ollama &> /dev/null
then
    echo "Ollama не найдена. Начинаем автоматическую установку..."
    
    OS="$(uname -s)"
    
    if [ "$OS" = "Darwin" ]; then
        echo "🍏 Обнаружена macOS. Скачиваем и устанавливаем Ollama..."
        curl -L https://ollama.com/download/Ollama-darwin.zip -o Ollama-darwin.zip
        unzip -o Ollama-darwin.zip
        cp -R Ollama.app /Applications/
        open /Applications/Ollama.app
        rm -rf Ollama-darwin.zip Ollama.app
        
    elif [ "$OS" = "Linux" ]; then
        echo "🐧 Обнаружен Linux. Устанавливаем Ollama через curl..."
        curl -fsSL https://ollama.com/install.sh | sh
    else
        echo "❌ Ваша ОС не поддерживается для автоустановки."
        echo "Пожалуйста, скачайте Ollama вручную с https://ollama.com"
        exit 1
    fi
    
    echo "✅ Ollama успешно установлена."
    echo "Ждем 5 секунд, пока она инициализируется..."
    sleep 5
fi

if curl -s http://localhost:11434 > /dev/null; then
    echo "Ollama уже запущена."
else
    echo "⏳ Запускаем Ollama в фоне..."
    ollama serve &
    
    for i in {1..10}; do
        if curl -s http://localhost:11434 > /dev/null; then
            echo "Ollama успешно запущена."
            break
        fi
        sleep 1
    done
fi

echo "⏳ Проверяем наличие модели qwen3.5:4b..."
if ! ollama list | grep -q "qwen3.5:4b"; then
    echo "⏳ Модель не найдена. Скачиваем (4 ГБ). Пожалуйста, подождите..."
    ollama pull qwen3.5:4b
    echo "Модель qwen3.5:4b успешно скачана."
else
    echo "Модель qwen3.5:4b уже скачана."
fi

echo "🐳 Запускаем Docker (PostgreSQL + FastAPI)..."
echo "Пожалуйста, подождите..."
docker-compose up --build