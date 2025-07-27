#!/bin/bash

# Улучшенный скрипт запуска SK English Bot
# С автоматическим восстановлением и мониторингом

set -e  # Выход при любой ошибке

# Конфигурация
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOT_SCRIPT="$SCRIPT_DIR/sk_english_bot.py"
VENV_DIR="$SCRIPT_DIR/bot_env"
LOG_DIR="$SCRIPT_DIR/logs"
PID_FILE="$SCRIPT_DIR/bot.pid"
LOG_FILE="$LOG_DIR/bot.log"
ERROR_LOG="$LOG_DIR/error.log"
RESTART_LOG="$LOG_DIR/restart.log"

# Максимальное количество попыток перезапуска
MAX_RESTARTS=10
RESTART_DELAY=5
HEALTH_CHECK_INTERVAL=30

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция логирования
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "ERROR")
            echo -e "${RED}[$timestamp] ERROR: $message${NC}" | tee -a "$ERROR_LOG"
            ;;
        "INFO")
            echo -e "${GREEN}[$timestamp] INFO: $message${NC}" | tee -a "$LOG_FILE"
            ;;
        "WARN")
            echo -e "${YELLOW}[$timestamp] WARN: $message${NC}" | tee -a "$LOG_FILE"
            ;;
        "DEBUG")
            echo -e "${BLUE}[$timestamp] DEBUG: $message${NC}" | tee -a "$LOG_FILE"
            ;;
    esac
}

# Создание директорий
setup_directories() {
    mkdir -p "$LOG_DIR"
    log_message "INFO" "Создана директория логов: $LOG_DIR"
}

# Проверка зависимостей
check_dependencies() {
    log_message "INFO" "Проверка зависимостей..."
    
    # Проверка Python
    if ! command -v python3 &> /dev/null; then
        log_message "ERROR" "Python3 не найден. Установите Python3."
        exit 1
    fi
    
    # Проверка виртуального окружения
    if [ ! -d "$VENV_DIR" ]; then
        log_message "WARN" "Виртуальное окружение не найдено. Создаем..."
        python3 -m venv "$VENV_DIR"
        source "$VENV_DIR/bin/activate"
        pip install --upgrade pip
        pip install -r "$SCRIPT_DIR/requirements.txt"
        log_message "INFO" "Виртуальное окружение создано и настроено"
    fi
    
    # Проверка основного скрипта
    if [ ! -f "$BOT_SCRIPT" ]; then
        log_message "ERROR" "Скрипт бота не найден: $BOT_SCRIPT"
        exit 1
    fi
    
    # Проверка .env файла
    if [ ! -f "$SCRIPT_DIR/.env" ]; then
        log_message "WARN" ".env файл не найден. Создаем пример..."
        cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
        log_message "WARN" "Пожалуйста, настройте .env файл с вашим BOT_TOKEN"
    fi
    
    log_message "INFO" "Все зависимости проверены"
}

# Активация виртуального окружения
activate_venv() {
    if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
        log_message "INFO" "Виртуальное окружение активировано"
    else
        log_message "ERROR" "Не удалось активировать виртуальное окружение"
        exit 1
    fi
}

# Проверка токена бота
check_bot_token() {
    # Загружаем .env файл
    if [ -f "$SCRIPT_DIR/.env" ]; then
        export $(grep -v '^#' "$SCRIPT_DIR/.env" | xargs)
    fi
    
    if [ -z "$BOT_TOKEN" ]; then
        log_message "ERROR" "BOT_TOKEN не задан. Проверьте .env файл или переменные окружения"
        exit 1
    fi
    
    log_message "INFO" "Токен бота найден"
}

# Проверка здоровья бота
health_check() {
    if [ -f "$SCRIPT_DIR/health_check.py" ]; then
        python3 "$SCRIPT_DIR/health_check.py" > /dev/null 2>&1
        return $?
    else
        log_message "WARN" "Скрипт health_check.py не найден, пропускаем проверку"
        return 0
    fi
}

# Остановка существующего процесса
stop_existing_bot() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            log_message "INFO" "Останавливаем существующий процесс бота (PID: $pid)"
            kill -TERM "$pid" 2>/dev/null || true
            sleep 3
            
            # Если процесс еще живой, убиваем принудительно
            if ps -p "$pid" > /dev/null 2>&1; then
                log_message "WARN" "Принудительно завершаем процесс"
                kill -KILL "$pid" 2>/dev/null || true
            fi
        fi
        rm -f "$PID_FILE"
    fi
}

# Запуск бота
start_bot() {
    local restart_count=0
    
    while [ $restart_count -lt $MAX_RESTARTS ]; do
        log_message "INFO" "Запуск бота (попытка $((restart_count + 1))/$MAX_RESTARTS)..."
        
        # Запускаем бота в фоне
        nohup python3 "$BOT_SCRIPT" > "$LOG_FILE" 2> "$ERROR_LOG" &
        local bot_pid=$!
        
        # Сохраняем PID
        echo "$bot_pid" > "$PID_FILE"
        log_message "INFO" "Бот запущен с PID: $bot_pid"
        
        # Даем боту время на запуск
        sleep 10
        
        # Проверяем, что процесс еще работает
        if ! ps -p "$bot_pid" > /dev/null 2>&1; then
            log_message "ERROR" "Бот завершился сразу после запуска"
            restart_count=$((restart_count + 1))
            echo "$(date): Restart $restart_count due to immediate exit" >> "$RESTART_LOG"
            sleep $RESTART_DELAY
            continue
        fi
        
        # Проверяем здоровье бота
        if ! health_check; then
            log_message "ERROR" "Health check не пройден"
            kill "$bot_pid" 2>/dev/null || true
            restart_count=$((restart_count + 1))
            echo "$(date): Restart $restart_count due to failed health check" >> "$RESTART_LOG"
            sleep $RESTART_DELAY
            continue
        fi
        
        log_message "INFO" "Бот успешно запущен и прошел проверку здоровья"
        
        # Мониторинг работы бота
        monitor_bot "$bot_pid"
        
        # Если мы здесь, значит бот упал
        restart_count=$((restart_count + 1))
        echo "$(date): Restart $restart_count due to bot crash" >> "$RESTART_LOG"
        
        if [ $restart_count -lt $MAX_RESTARTS ]; then
            log_message "WARN" "Бот упал, перезапускаем через $RESTART_DELAY секунд..."
            sleep $RESTART_DELAY
        fi
    done
    
    log_message "ERROR" "Достигнуто максимальное количество перезапусков ($MAX_RESTARTS). Останавливаем."
    exit 1
}

# Мониторинг работы бота
monitor_bot() {
    local bot_pid="$1"
    local last_health_check=$(date +%s)
    
    while ps -p "$bot_pid" > /dev/null 2>&1; do
        sleep 5
        
        # Периодическая проверка здоровья
        local current_time=$(date +%s)
        if [ $((current_time - last_health_check)) -ge $HEALTH_CHECK_INTERVAL ]; then
            if ! health_check; then
                log_message "ERROR" "Health check не пройден во время работы, перезапускаем бота"
                kill "$bot_pid" 2>/dev/null || true
                return 1
            fi
            last_health_check=$current_time
        fi
    done
    
    log_message "WARN" "Процесс бота ($bot_pid) завершился"
    rm -f "$PID_FILE"
    return 1
}

# Показать статус
show_status() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            log_message "INFO" "Бот работает (PID: $pid)"
            
            # Показываем статистику
            local uptime=$(ps -o etime= -p "$pid" | tr -d ' ')
            local memory=$(ps -o rss= -p "$pid" | tr -d ' ')
            memory_mb=$((memory / 1024))
            
            echo "  Время работы: $uptime"
            echo "  Использование памяти: ${memory_mb}MB"
            
            # Запускаем health check
            if health_check; then
                log_message "INFO" "Health check: PASSED"
            else
                log_message "WARN" "Health check: FAILED"
            fi
        else
            log_message "WARN" "PID файл существует, но процесс не найден"
            rm -f "$PID_FILE"
        fi
    else
        log_message "INFO" "Бот не запущен"
    fi
}

# Показать логи
show_logs() {
    local lines="${1:-50}"
    
    echo "=== Основные логи (последние $lines строк) ==="
    if [ -f "$LOG_FILE" ]; then
        tail -n "$lines" "$LOG_FILE"
    else
        echo "Лог файл не найден"
    fi
    
    echo ""
    echo "=== Логи ошибок (последние $lines строк) ==="
    if [ -f "$ERROR_LOG" ]; then
        tail -n "$lines" "$ERROR_LOG"
    else
        echo "Лог ошибок не найден"
    fi
    
    echo ""
    echo "=== Логи перезапусков ==="
    if [ -f "$RESTART_LOG" ]; then
        tail -n 20 "$RESTART_LOG"
    else
        echo "Лог перезапусков не найден"
    fi
}

# Основная функция
main() {
    local action="${1:-start}"
    
    setup_directories
    
    case "$action" in
        "start")
            log_message "INFO" "=== Запуск SK English Bot ==="
            check_dependencies
            activate_venv
            check_bot_token
            stop_existing_bot
            start_bot
            ;;
        "stop")
            log_message "INFO" "=== Остановка SK English Bot ==="
            stop_existing_bot
            log_message "INFO" "Бот остановлен"
            ;;
        "restart")
            log_message "INFO" "=== Перезапуск SK English Bot ==="
            stop_existing_bot
            sleep 2
            "$0" start
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "${2:-50}"
            ;;
        "health")
            activate_venv
            check_bot_token
            if health_check; then
                log_message "INFO" "Health check: PASSED"
                exit 0
            else
                log_message "ERROR" "Health check: FAILED"
                exit 1
            fi
            ;;
        "install")
            log_message "INFO" "=== Установка зависимостей ==="
            check_dependencies
            log_message "INFO" "Установка завершена"
            ;;
        *)
            echo "Использование: $0 {start|stop|restart|status|logs|health|install}"
            echo ""
            echo "Команды:"
            echo "  start   - Запустить бота"
            echo "  stop    - Остановить бота"
            echo "  restart - Перезапустить бота"
            echo "  status  - Показать статус бота"
            echo "  logs    - Показать логи (можно указать количество строк)"
            echo "  health  - Проверить здоровье бота"
            echo "  install - Установить зависимости"
            exit 1
            ;;
    esac
}

# Обработка сигналов
trap 'log_message "INFO" "Получен сигнал завершения"; stop_existing_bot; exit 0' SIGTERM SIGINT

# Запуск
main "$@"