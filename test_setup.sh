#!/bin/bash

# Скрипт тестирования настройки SK English Bot

echo "🔧 Проверка настройки SK English Bot..."
echo ""

# Проверка основных компонентов
echo "📋 Проверка компонентов:"

if [ -f "sk_english_bot.py" ]; then
    echo "✅ Основной скрипт бота: НАЙДЕН"
else
    echo "❌ Основной скрипт бота: НЕ НАЙДЕН"
fi

if [ -f ".env" ]; then
    echo "✅ Конфигурационный файл: НАЙДЕН"
    if grep -q "your_bot_token_here" ".env"; then
        echo "⚠️  Токен бота: НЕ НАСТРОЕН (нужен реальный токен)"
    else
        echo "✅ Токен бота: НАСТРОЕН"
    fi
else
    echo "❌ Конфигурационный файл: НЕ НАЙДЕН"
fi

if [ -d "bot_env" ]; then
    echo "✅ Виртуальное окружение: НАЙДЕНО"
else
    echo "❌ Виртуальное окружение: НЕ НАЙДЕНО"
fi

if [ -x "start_bot.sh" ]; then
    echo "✅ Скрипт запуска: НАЙДЕН"
else
    echo "❌ Скрипт запуска: НЕ НАЙДЕН"
fi

echo ""
echo "🚀 Следующие шаги для запуска бота:"
echo ""
echo "1. Получите токен от @BotFather:"
echo "   - Перейдите к https://t.me/BotFather"
echo "   - Отправьте /newbot (для нового бота) или /mybots (для существующего)"
echo "   - Скопируйте токен"
echo ""
echo "2. Настройте токен:"
echo "   nano .env"
echo "   # Замените 'your_bot_token_here' на ваш реальный токен"
echo ""
echo "3. Запустите бота:"
echo "   ./start_bot.sh start"
echo ""
echo "4. Проверьте статус:"
echo "   ./start_bot.sh status"
echo ""

echo "💡 Полезные команды:"
echo "   ./start_bot.sh restart  - перезапуск"
echo "   ./start_bot.sh logs     - просмотр логов"
echo "   ./start_bot.sh health   - проверка здоровья"
echo "   ./diagnose.sh           - диагностика проблем"
echo ""

echo "🔗 Ссылки:"
echo "   BotFather: https://t.me/BotFather"
echo "   Документация: README.md"
echo "   Быстрые исправления: QUICK_FIX.md"
echo ""

echo "✨ После настройки токена бот будет работать 24/7 с автоматическим восстановлением!"