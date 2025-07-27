#!/bin/bash

# Скрипт мониторинга SK English Bot
# Проверяет работу бота и перезапускает его при необходимости

BOT_NAME="sk_english_bot.py"
LOG_FILE="/workspace/monitor.log"
PID_FILE="/workspace/bot.pid"
MAX_MEMORY_MB=500
CHECK_INTERVAL=60

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

check_bot_process() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        else
            log_message "Процесс бота (PID: $PID) не найден"
            rm -f "$PID_FILE"
            return 1
        fi
    else
        return 1
    fi
}

check_memory_usage() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            MEMORY_KB=$(ps -o rss= -p "$PID" 2>/dev/null | tr -d ' ')
            if [ -n "$MEMORY_KB" ]; then
                MEMORY_MB=$((MEMORY_KB / 1024))
                if [ "$MEMORY_MB" -gt "$MAX_MEMORY_MB" ]; then
                    log_message "Высокое потребление памяти: ${MEMORY_MB}MB (лимит: ${MAX_MEMORY_MB}MB)"
                    return 1
                fi
            fi
        fi
    fi
    return 0
}

start_bot() {
    cd /workspace || exit 1
    
    # Проверяем наличие токена
    if [ -z "$BOT_TOKEN" ]; then
        log_message "ОШИБКА: BOT_TOKEN не установлен"
        return 1
    fi
    
    # Устанавливаем зависимости если нужно
    if [ ! -f "requirements_installed.flag" ]; then
        log_message "Устанавливаем зависимости..."
        pip3 install -r requirements.txt && touch requirements_installed.flag
    fi
    
    log_message "Запускаем бота..."
    nohup python3 "$BOT_NAME" > bot_output.log 2>&1 &
    BOT_PID=$!
    echo "$BOT_PID" > "$PID_FILE"
    log_message "Бот запущен с PID: $BOT_PID"
    
    # Ждем несколько секунд и проверяем, что процесс действительно запустился
    sleep 5
    if ! ps -p "$BOT_PID" > /dev/null 2>&1; then
        log_message "ОШИБКА: Не удалось запустить бота"
        rm -f "$PID_FILE"
        return 1
    fi
    
    return 0
}

stop_bot() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            log_message "Останавливаем бота (PID: $PID)..."
            kill -TERM "$PID"
            
            # Ждем корректного завершения
            for i in {1..10}; do
                if ! ps -p "$PID" > /dev/null 2>&1; then
                    break
                fi
                sleep 1
            done
            
            # Принудительно завершаем если не остановился
            if ps -p "$PID" > /dev/null 2>&1; then
                log_message "Принудительно останавливаем бота..."
                kill -KILL "$PID"
            fi
        fi
        rm -f "$PID_FILE"
        log_message "Бот остановлен"
    fi
}

restart_bot() {
    log_message "Перезапускаем бота..."
    stop_bot
    sleep 3
    start_bot
}

check_network() {
    # Проверяем доступность Telegram API
    if ! curl -s --connect-timeout 10 https://api.telegram.org > /dev/null; then
        log_message "Нет соединения с Telegram API"
        return 1
    fi
    return 0
}

# Основной цикл мониторинга
main_loop() {
    log_message "Запуск мониторинга SK English Bot..."
    
    while true; do
        if ! check_bot_process; then
            log_message "Бот не работает, запускаем..."
            if check_network; then
                start_bot
            else
                log_message "Нет сетевого соединения, пропускаем запуск"
            fi
        elif ! check_memory_usage; then
            log_message "Перезапускаем бота из-за высокого потребления памяти"
            restart_bot
        else
            # Проверяем, что бот отвечает (можно добавить проверку через API)
            log_message "Бот работает нормально"
        fi
        
        sleep "$CHECK_INTERVAL"
    done
}

# Обработка параметров командной строки
case "$1" in
    start)
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    restart)
        restart_bot
        ;;
    status)
        if check_bot_process; then
            PID=$(cat "$PID_FILE")
            MEMORY_KB=$(ps -o rss= -p "$PID" 2>/dev/null | tr -d ' ')
            MEMORY_MB=$((MEMORY_KB / 1024))
            echo "SK English Bot работает (PID: $PID, память: ${MEMORY_MB}MB)"
        else
            echo "SK English Bot не работает"
        fi
        ;;
    monitor)
        main_loop
        ;;
    *)
        echo "Использование: $0 {start|stop|restart|status|monitor}"
        echo ""
        echo "Команды:"
        echo "  start   - Запустить бота"
        echo "  stop    - Остановить бота"
        echo "  restart - Перезапустить бота"
        echo "  status  - Показать статус бота"
        echo "  monitor - Запустить мониторинг (основной режим)"
        exit 1
        ;;
esac