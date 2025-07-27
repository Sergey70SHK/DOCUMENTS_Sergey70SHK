#!/bin/bash

# Скрипт быстрой диагностики проблем SK English Bot

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Цвета
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}"
    echo "=================================================================="
    echo "       🔍 SK English Bot - Диагностика проблем"
    echo "=================================================================="
    echo -e "${NC}"
}

check_item() {
    local name="$1"
    local command="$2"
    local critical="$3"
    
    echo -n "Проверка $name... "
    
    if eval "$command" >/dev/null 2>&1; then
        echo -e "${GREEN}✅ OK${NC}"
        return 0
    else
        if [ "$critical" = "critical" ]; then
            echo -e "${RED}❌ КРИТИЧЕСКАЯ ОШИБКА${NC}"
        else
            echo -e "${YELLOW}⚠️ ПРЕДУПРЕЖДЕНИЕ${NC}"
        fi
        return 1
    fi
}

# Системная диагностика
system_diagnosis() {
    echo -e "${BLUE}=== СИСТЕМНАЯ ДИАГНОСТИКА ===${NC}"
    
    check_item "Python3" "python3 --version" "critical"
    check_item "pip3" "pip3 --version" "critical"
    check_item "curl" "curl --version" ""
    check_item "cron" "which cron || which crond" ""
    
    # Проверка ресурсов
    echo -n "Свободная память: "
    free -h | grep "Mem:" | awk '{print $7}' | tr -d '\n'
    echo ""
    
    echo -n "Свободное место: "
    df -h "$SCRIPT_DIR" | tail -1 | awk '{print $4}' | tr -d '\n'
    echo ""
    
    echo -n "Загрузка системы: "
    uptime | awk -F'load average:' '{print $2}' | tr -d ' '
    echo ""
}

# Диагностика проекта
project_diagnosis() {
    echo -e "${BLUE}=== ДИАГНОСТИКА ПРОЕКТА ===${NC}"
    
    cd "$SCRIPT_DIR"
    
    check_item "основной скрипт" "test -f sk_english_bot.py" "critical"
    check_item "requirements.txt" "test -f requirements.txt" "critical"
    check_item ".env файл" "test -f .env" "critical"
    check_item "виртуальное окружение" "test -d bot_env" "critical"
    check_item "скрипт запуска" "test -x start_bot.sh" ""
    check_item "скрипт мониторинга" "test -x monitor_bot.sh" ""
    check_item "health check" "test -f health_check.py" ""
    
    # Проверка размеров файлов
    if [ -f "sk_english_bot.py" ]; then
        size=$(stat -f%z "sk_english_bot.py" 2>/dev/null || stat -c%s "sk_english_bot.py" 2>/dev/null || echo "0")
        if [ "$size" -gt 1000 ]; then
            echo -e "Размер основного скрипта: ${GREEN}$size байт ✅${NC}"
        else
            echo -e "Размер основного скрипта: ${RED}$size байт ❌${NC}"
        fi
    fi
}

# Диагностика конфигурации
config_diagnosis() {
    echo -e "${BLUE}=== ДИАГНОСТИКА КОНФИГУРАЦИИ ===${NC}"
    
    if [ -f ".env" ]; then
        # Проверка токена
        if grep -q "your_bot_token_here" ".env"; then
            echo -e "Токен бота: ${RED}НЕ НАСТРОЕН ❌${NC}"
        elif grep -q "BOT_TOKEN=" ".env" && ! grep -q "BOT_TOKEN=$" ".env"; then
            echo -e "Токен бота: ${GREEN}НАСТРОЕН ✅${NC}"
        else
            echo -e "Токен бота: ${RED}НЕ НАЙДЕН ❌${NC}"
        fi
        
        # Другие настройки
        check_item "LOG_LEVEL" "grep -q 'LOG_LEVEL=' .env" ""
        check_item "MAX_MEMORY_MB" "grep -q 'MAX_MEMORY_MB=' .env" ""
    else
        echo -e "Файл .env: ${RED}НЕ НАЙДЕН ❌${NC}"
    fi
}

# Диагностика зависимостей
dependencies_diagnosis() {
    echo -e "${BLUE}=== ДИАГНОСТИКА ЗАВИСИМОСТЕЙ ===${NC}"
    
    if [ -d "bot_env" ]; then
        source "bot_env/bin/activate"
        
        check_item "python-telegram-bot" "python3 -c 'import telegram'" "critical"
        check_item "requests" "python3 -c 'import requests'" "critical"
        check_item "asyncio" "python3 -c 'import asyncio'" "critical"
        
        # Версии пакетов
        echo "Версии ключевых пакетов:"
        python3 -c "
try:
    import telegram
    print(f'  python-telegram-bot: {telegram.__version__}')
except:
    print('  python-telegram-bot: НЕ УСТАНОВЛЕН')

try:
    import requests
    print(f'  requests: {requests.__version__}')
except:
    print('  requests: НЕ УСТАНОВЛЕН')
"
    else
        echo -e "Виртуальное окружение: ${RED}НЕ НАЙДЕНО ❌${NC}"
    fi
}

# Диагностика сети
network_diagnosis() {
    echo -e "${BLUE}=== ДИАГНОСТИКА СЕТИ ===${NC}"
    
    check_item "подключение к интернету" "curl -s --connect-timeout 5 https://google.com" "critical"
    check_item "Telegram API" "curl -s --connect-timeout 10 https://api.telegram.org" "critical"
    
    # Проверка токена если он есть
    if [ -f ".env" ] && grep -q "BOT_TOKEN=" ".env" && ! grep -q "your_bot_token_here" ".env"; then
        token=$(grep "BOT_TOKEN=" ".env" | cut -d'=' -f2)
        if [ ! -z "$token" ] && [ "$token" != "your_bot_token_here" ]; then
            check_item "валидность токена" "curl -s 'https://api.telegram.org/bot$token/getMe' | grep -q '\"ok\":true'" "critical"
        fi
    fi
}

# Диагностика процессов
process_diagnosis() {
    echo -e "${BLUE}=== ДИАГНОСТИКА ПРОЦЕССОВ ===${NC}"
    
    # Поиск запущенных процессов бота
    if pgrep -f "sk_english_bot.py" >/dev/null; then
        echo -e "Процесс бота: ${GREEN}ЗАПУЩЕН ✅${NC}"
        pids=$(pgrep -f "sk_english_bot.py")
        for pid in $pids; do
            echo "  PID: $pid"
            if ps -p "$pid" -o etime= >/dev/null 2>&1; then
                uptime=$(ps -p "$pid" -o etime= | tr -d ' ')
                echo "  Время работы: $uptime"
            fi
            if ps -p "$pid" -o rss= >/dev/null 2>&1; then
                memory=$(ps -p "$pid" -o rss= | tr -d ' ')
                memory_mb=$((memory / 1024))
                echo "  Память: ${memory_mb}MB"
            fi
        done
    else
        echo -e "Процесс бота: ${RED}НЕ ЗАПУЩЕН ❌${NC}"
    fi
    
    # Проверка PID файла
    if [ -f "bot.pid" ]; then
        pid=$(cat "bot.pid")
        if ps -p "$pid" >/dev/null 2>&1; then
            echo -e "PID файл: ${GREEN}КОРРЕКТНЫЙ ($pid) ✅${NC}"
        else
            echo -e "PID файл: ${RED}УСТАРЕВШИЙ ($pid) ❌${NC}"
        fi
    else
        echo -e "PID файл: ${YELLOW}НЕ НАЙДЕН ⚠️${NC}"
    fi
}

# Диагностика логов
logs_diagnosis() {
    echo -e "${BLUE}=== ДИАГНОСТИКА ЛОГОВ ===${NC}"
    
    # Проверка логов
    log_files=("logs/bot.log" "logs/error.log" "logs/restart.log")
    
    for log_file in "${log_files[@]}"; do
        if [ -f "$log_file" ]; then
            size=$(stat -f%z "$log_file" 2>/dev/null || stat -c%s "$log_file" 2>/dev/null || echo "0")
            if [ "$size" -gt 0 ]; then
                echo -e "$(basename "$log_file"): ${GREEN}СУЩЕСТВУЕТ (${size} байт) ✅${NC}"
                
                # Последние ошибки
                if [[ "$log_file" == *"error.log" ]]; then
                    errors=$(tail -n 10 "$log_file" 2>/dev/null | grep -i "error\|exception\|failed" | wc -l)
                    if [ "$errors" -gt 0 ]; then
                        echo -e "  Недавние ошибки: ${RED}$errors ❌${NC}"
                    else
                        echo -e "  Недавние ошибки: ${GREEN}0 ✅${NC}"
                    fi
                fi
            else
                echo -e "$(basename "$log_file"): ${YELLOW}ПУСТОЙ ⚠️${NC}"
            fi
        else
            echo -e "$(basename "$log_file"): ${YELLOW}НЕ НАЙДЕН ⚠️${NC}"
        fi
    done
}

# Рекомендации по исправлению
show_recommendations() {
    echo -e "${BLUE}=== РЕКОМЕНДАЦИИ ===${NC}"
    
    echo "На основе диагностики рекомендуем:"
    echo ""
    
    # Проверяем основные проблемы
    if [ ! -f ".env" ] || grep -q "your_bot_token_here" ".env"; then
        echo -e "${RED}🔧 КРИТИЧНО: Настройте токен бота в .env файле${NC}"
        echo "   Выполните: nano .env"
        echo ""
    fi
    
    if [ ! -d "bot_env" ]; then
        echo -e "${RED}🔧 КРИТИЧНО: Установите зависимости${NC}"
        echo "   Выполните: ./install.sh"
        echo ""
    fi
    
    if ! pgrep -f "sk_english_bot.py" >/dev/null; then
        echo -e "${YELLOW}🚀 Запустите бота${NC}"
        echo "   Выполните: ./start_bot.sh start"
        echo ""
    fi
    
    if [ ! -f "logs/bot.log" ] || [ ! -s "logs/bot.log" ]; then
        echo -e "${YELLOW}📝 Настройте логирование${NC}"
        echo "   Выполните: mkdir -p logs"
        echo ""
    fi
    
    echo -e "${GREEN}💡 Для автоматического мониторинга:${NC}"
    echo "   ./setup_cron.sh"
    echo ""
    echo -e "${GREEN}📊 Для непрерывного мониторинга:${NC}"
    echo "   ./start_bot.sh status"
    echo "   tail -f logs/bot.log"
}

# Основная функция
main() {
    print_header
    
    system_diagnosis
    echo ""
    
    project_diagnosis
    echo ""
    
    config_diagnosis
    echo ""
    
    dependencies_diagnosis
    echo ""
    
    network_diagnosis
    echo ""
    
    process_diagnosis
    echo ""
    
    logs_diagnosis
    echo ""
    
    show_recommendations
    
    echo ""
    echo -e "${BLUE}=================================================================="
    echo "           🔍 Диагностика завершена"
    echo "=================================================================="
    echo -e "${NC}"
}

# Запуск
main "$@"