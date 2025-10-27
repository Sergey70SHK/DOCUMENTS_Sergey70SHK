#!/bin/bash

# Автоматический скрипт установки SK English Bot
# Устанавливает все зависимости и настраивает бота

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}"
    echo "=================================================================="
    echo "         🤖 SK English Bot - Автоматическая установка"
    echo "=================================================================="
    echo -e "${NC}"
}

print_step() {
    echo -e "${GREEN}[STEP] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

print_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

print_success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

# Проверка системы
check_system() {
    print_step "Проверка системы..."
    
    # Проверка ОС
    if [[ "$OSTYPE" != "linux-gnu"* ]]; then
        print_warning "Скрипт оптимизирован для Linux. Возможны проблемы на других ОС."
    fi
    
    # Проверка прав root (не обязательно, но лучше)
    if [[ $EUID -eq 0 ]]; then
        print_warning "Скрипт запущен от root. Рекомендуется запускать от обычного пользователя."
    fi
    
    print_success "Система проверена"
}

# Установка системных зависимостей
install_system_deps() {
    print_step "Установка системных зависимостей..."
    
    if command -v apt-get >/dev/null 2>&1; then
        # Ubuntu/Debian
        sudo apt-get update -qq
        sudo apt-get install -y python3 python3-pip python3-venv curl cron
    elif command -v yum >/dev/null 2>&1; then
        # CentOS/RHEL
        sudo yum install -y python3 python3-pip curl cronie
        sudo systemctl enable crond
        sudo systemctl start crond
    elif command -v pacman >/dev/null 2>&1; then
        # Arch Linux
        sudo pacman -S --noconfirm python python-pip curl cronie
    else
        print_warning "Не удалось определить пакетный менеджер. Установите вручную: python3, pip3, curl, cron"
    fi
    
    print_success "Системные зависимости установлены"
}

# Создание виртуального окружения
setup_venv() {
    print_step "Настройка виртуального окружения..."
    
    cd "$SCRIPT_DIR"
    
    if [ -d "bot_env" ]; then
        print_warning "Виртуальное окружение уже существует. Пересоздаем..."
        rm -rf bot_env
    fi
    
    python3 -m venv bot_env
    source bot_env/bin/activate
    
    # Обновляем pip
    pip install --upgrade pip
    
    # Устанавливаем зависимости
    pip install -r requirements.txt
    
    print_success "Виртуальное окружение настроено"
}

# Настройка конфигурации
setup_config() {
    print_step "Настройка конфигурации..."
    
    # Проверяем, есть ли уже настроенный .env
    if [ -f ".env" ] && grep -q "your_bot_token_here" ".env"; then
        echo ""
        echo -e "${YELLOW}⚠️  ВАЖНО: Необходимо настроить токен бота!${NC}"
        echo ""
        echo "1. Перейдите к @BotFather в Telegram"
        echo "2. Создайте нового бота командой /newbot"
        echo "3. Скопируйте полученный токен"
        echo "4. Замените 'your_bot_token_here' в файле .env на ваш токен"
        echo ""
        
        read -p "Введите токен бота (или нажмите Enter для настройки позже): " bot_token
        
        if [ ! -z "$bot_token" ]; then
            sed -i "s/your_bot_token_here/$bot_token/g" .env
            print_success "Токен бота настроен"
        else
            print_warning "Токен не настроен. Настройте его в файле .env перед запуском"
        fi
    fi
    
    # Создаем директории
    mkdir -p logs
    
    print_success "Конфигурация настроена"
}

# Настройка автозапуска
setup_autostart() {
    print_step "Настройка автозапуска..."
    
    echo "Выберите метод автозапуска:"
    echo "1) Cron (рекомендуется для простых случаев)"
    echo "2) Systemd (рекомендуется для продакшена)"
    echo "3) Без автозапуска"
    
    read -p "Ваш выбор (1-3): " choice
    
    case $choice in
        1)
            # Настройка cron
            ./setup_cron.sh
            print_success "Cron настроен"
            ;;
        2)
            # Настройка systemd
            print_warning "Для systemd требуются права root. Скопируйте файл sk-english-bot.service в /etc/systemd/system/"
            echo "Затем выполните:"
            echo "  sudo systemctl daemon-reload"
            echo "  sudo systemctl enable sk-english-bot"
            echo "  sudo systemctl start sk-english-bot"
            ;;
        3)
            print_warning "Автозапуск не настроен"
            ;;
        *)
            print_warning "Неверный выбор. Автозапуск не настроен"
            ;;
    esac
}

# Проверка установки
test_installation() {
    print_step "Тестирование установки..."
    
    # Активируем окружение
    source "$SCRIPT_DIR/bot_env/bin/activate"
    
    # Проверяем health check
    if python3 health_check.py --help >/dev/null 2>&1; then
        print_success "Health check работает"
    else
        print_error "Проблема с health check"
    fi
    
    # Проверяем основной скрипт
    if python3 -c "import telegram; print('Telegram library OK')" >/dev/null 2>&1; then
        print_success "Python библиотеки установлены"
    else
        print_error "Проблема с Python библиотеками"
    fi
    
    print_success "Установка протестирована"
}

# Показать инструкции по запуску
show_usage() {
    echo ""
    echo -e "${BLUE}=================================================================="
    echo "                    🎉 Установка завершена!"
    echo "=================================================================="
    echo -e "${NC}"
    echo ""
    echo "Для запуска бота:"
    echo "  ./start_bot.sh start"
    echo ""
    echo "Другие команды:"
    echo "  ./start_bot.sh status   - проверить статус"
    echo "  ./start_bot.sh stop     - остановить бота"
    echo "  ./start_bot.sh restart  - перезапустить"
    echo "  ./start_bot.sh logs     - показать логи"
    echo "  ./start_bot.sh health   - проверка здоровья"
    echo ""
    echo "Мониторинг:"
    echo "  ./monitor_bot.sh        - ручной мониторинг"
    echo "  python3 health_check.py - проверка здоровья"
    echo ""
    echo -e "${YELLOW}⚠️  НЕ ЗАБУДЬТЕ:${NC}"
    echo "1. Настроить токен бота в файле .env"
    echo "2. Проверить, что бот работает: ./start_bot.sh status"
    echo ""
}

# Основная функция
main() {
    print_header
    
    check_system
    install_system_deps
    setup_venv
    setup_config
    setup_autostart
    test_installation
    show_usage
    
    print_success "🎉 Установка SK English Bot завершена успешно!"
}

# Обработка ошибок
trap 'print_error "Установка прервана"; exit 1' ERR

# Запуск
main "$@"