# 🚨 Быстрое решение проблем с отключениями

## ⚡ Мгновенное восстановление

```bash
# 1. СТОП-СТАРТ бота
./start_bot.sh restart

# 2. Проверка статуса
./start_bot.sh status

# 3. Диагностика проблем
./diagnose.sh
```

## 🔧 Основные проблемы и решения

### Бот не запускается
```bash
# Проверить токен
grep BOT_TOKEN .env

# Если токен не настроен:
nano .env  # Замените your_bot_token_here на реальный токен

# Переустановить зависимости
./install.sh
```

### Бот постоянно отключается
```bash
# 1. Проверить логи ошибок
./start_bot.sh logs | tail -20

# 2. Сбросить webhook
curl -X POST "https://api.telegram.org/bot$BOT_TOKEN/deleteWebhook"

# 3. Принудительно убить все процессы
pkill -f "sk_english_bot.py"
rm -f bot.pid
./start_bot.sh start

# 4. Полная переустановка
./start_bot.sh stop
rm -rf bot_env logs/*
./install.sh
```

### Проблемы с памятью
```bash
# Уменьшить лимит памяти
echo "MAX_MEMORY_MB=200" >> .env

# Перезапустить с новыми настройками
./start_bot.sh restart
```

### Сетевые проблемы
```bash
# Проверить доступность Telegram
curl -s https://api.telegram.org/bot$BOT_TOKEN/getMe

# Если не работает - настроить прокси или VPN
```

## 🔄 Автоматическое восстановление

### Включить cron мониторинг
```bash
./setup_cron.sh
```

### Или systemd сервис
```bash
sudo cp sk-english-bot.service /etc/systemd/system/
sudo systemctl enable sk-english-bot
sudo systemctl start sk-english-bot
```

## 📊 Мониторинг

### Проверить здоровье бота
```bash
./start_bot.sh health
```

### Смотреть логи в реальном времени
```bash
tail -f logs/bot.log
```

### Статистика ошибок
```bash
grep -i "error\|exception" logs/error.log | tail -10
```

## 🆘 Экстренное восстановление

Если ничего не помогает:

```bash
# 1. Полная очистка
./start_bot.sh stop
pkill -f "sk_english_bot"
rm -rf bot_env logs/* bot.pid bot_status.json

# 2. Переустановка с нуля
./install.sh

# 3. Настройка токена
nano .env

# 4. Запуск
./start_bot.sh start

# 5. Включение мониторинга
./setup_cron.sh
```

## ❓ Получение помощи

1. **Диагностика**: `./diagnose.sh`
2. **Логи**: `./start_bot.sh logs`
3. **Статус**: `./start_bot.sh status`
4. **Health check**: `./start_bot.sh health`

## 🔗 Полезные команды

```bash
# Показать все процессы Python
ps aux | grep python

# Освободить память
sudo sysctl -w vm.drop_caches=3

# Проверить место на диске
df -h

# Проверить загрузку системы
top
```