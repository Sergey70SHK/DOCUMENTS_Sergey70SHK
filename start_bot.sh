#!/bin/bash

# SK English Bot - Launcher Script
# Скрипт запуска и управления ботом

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Настройки
PROJECT_DIR="/workspace"
BOT_SCRIPT="sk_english_bot.py"
VENV_DIR="bot_env"
LOG_DIR="logs"
PID_FILE="$LOG_DIR/bot.pid"
ENV_FILE=".env"

# Функции
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_DIR/launcher.log"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_DIR/launcher.log"
}

success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1" | tee -a "$LOG_DIR/launcher.log"
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_DIR/launcher.log"
}

# Создание необходимых директорий
mkdir -p "$LOG_DIR"

# Переход в директорию проекта
cd "$PROJECT_DIR"

# Загрузка переменных окружения из .env файла
load_env() {
    if [[ -f "$ENV_FILE" ]]; then
        log "Загрузка переменных окружения из $ENV_FILE"
        export $(grep -v '^#' "$ENV_FILE" | xargs)
        
        # Проверка что токен установлен
        if [[ -z "$BOT_TOKEN" ]] || [[ "$BOT_TOKEN" == "your_bot_token_here" ]]; then
            error "BOT_TOKEN не установлен или содержит placeholder!"
            error "Отредактируйте файл .env и установите реальный токен от @BotFather"
            exit 1
        fi
        
        success "Переменные окружения загружены"
    else
        error "Файл $ENV_FILE не найден!"
        exit 1
    fi
}

# Проверка зависимостей
check_dependencies() {
    log "Проверка зависимостей..."
    
    # Проверка Python
    if ! command -v python3 &> /dev/null; then
        error "Python3 не установлен!"
        exit 1
    fi
    
    # Проверка виртуального окружения
    if [[ ! -d "$VENV_DIR" ]]; then
        error "Виртуальное окружение не найдено!"
        error "Запустите: python3 -m venv $VENV_DIR && source $VENV_DIR/bin/activate && pip install -r requirements.txt"
        exit 1
    fi
    
    success "Все зависимости проверены"
}

# Активация виртуального окружения
activate_venv() {
    log "Активация виртуального окружения..."
    source "$VENV_DIR/bin/activate"
    success "Виртуальное окружение активировано"
}

# Проверка статуса бота
status() {
    if [[ -f "$PID_FILE" ]]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            success "Бот запущен (PID: $PID)"
            return 0
        else
            warning "PID файл существует, но процесс не найден"
            rm -f "$PID_FILE"
        fi
    fi
    
    # Проверка по имени процесса
    if pgrep -f "$BOT_SCRIPT" > /dev/null; then
        PID=$(pgrep -f "$BOT_SCRIPT")
        warning "Бот запущен без PID файла (PID: $PID)"
        echo "$PID" > "$PID_FILE"
        return 0
    fi
    
    error "Бот не запущен"
    return 1
}

# Запуск бота
start() {
    log "=== Запуск SK English Bot ==="
    
    # Проверка что бот уже не запущен
    if status > /dev/null 2>&1; then
        warning "Бот уже запущен!"
        return 0
    fi
    
    # Загрузка окружения и проверки
    load_env
    check_dependencies
    activate_venv
    
    # Запуск бота
    log "Запуск бота..."
    nohup python3 "$BOT_SCRIPT" > "$LOG_DIR/bot_output.log" 2>&1 &
    BOT_PID=$!
    echo "$BOT_PID" > "$PID_FILE"
    
    # Проверка что бот запустился
    sleep 3
    if ps -p "$BOT_PID" > /dev/null 2>&1; then
        success "Бот успешно запущен (PID: $BOT_PID)"
        
        # Показать последние строки лога
        log "Последние записи лога:"
        tail -5 "$LOG_DIR/bot_output.log" 2>/dev/null || true
    else
        error "Бот не смог запуститься!"
        
        # Показать ошибки
        log "Ошибки при запуске:"
        tail -10 "$LOG_DIR/bot_output.log" 2>/dev/null || true
        
        rm -f "$PID_FILE"
        return 1
    fi
}

# Остановка бота
stop() {
    log "=== Остановка SK English Bot ==="
    
    if [[ -f "$PID_FILE" ]]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            log "Остановка бота (PID: $PID)..."
            kill "$PID"
            
            # Ожидание завершения
            for i in {1..10}; do
                if ! ps -p "$PID" > /dev/null 2>&1; then
                    success "Бот остановлен"
                    rm -f "$PID_FILE"
                    return 0
                fi
                sleep 1
            done
            
            # Принудительная остановка
            warning "Принудительная остановка..."
            kill -9 "$PID" 2>/dev/null || true
            sleep 2
        fi
        rm -f "$PID_FILE"
    fi
    
    # Остановка всех процессов бота
    if pgrep -f "$BOT_SCRIPT" > /dev/null; then
        log "Остановка всех процессов бота..."
        pkill -f "$BOT_SCRIPT" || true
        sleep 2
    fi
    
    success "Бот остановлен"
}

# Перезапуск бота
restart() {
    log "=== Перезапуск SK English Bot ==="
    stop
    sleep 2
    start
}

# Просмотр логов
logs() {
    if [[ -f "$LOG_DIR/bot_output.log" ]]; then
        tail -f "$LOG_DIR/bot_output.log"
    else
        error "Лог файл не найден!"
        exit 1
    fi
}

# Тест бота
test() {
    log "=== Тест SK English Bot ==="
    
    load_env
    check_dependencies
    activate_venv
    
    log "Запуск тестового сеанса (10 секунд)..."
    timeout 10s python3 "$BOT_SCRIPT" || true
    
    success "Тест завершен"
}

# Справка
usage() {
    echo "SK English Bot - Launcher Script"
    echo ""
    echo "Использование: $0 {start|stop|restart|status|logs|test}"
    echo ""
    echo "Команды:"
    echo "  start    - Запустить бота"
    echo "  stop     - Остановить бота"
    echo "  restart  - Перезапустить бота"
    echo "  status   - Проверить статус бота"
    echo "  logs     - Показать логи в реальном времени"
    echo "  test     - Запустить тест бота (10 секунд)"
    echo ""
    echo "Файлы:"
    echo "  Конфигурация: $ENV_FILE"
    echo "  Логи: $LOG_DIR/"
    echo "  PID: $PID_FILE"
}

# Основная логика
case "${1:-}" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    test)
        test
        ;;
    ""|help|--help|-h)
        usage
        ;;
    *)
        error "Неизвестная команда: $1"
        usage
        exit 1
        ;;
esac