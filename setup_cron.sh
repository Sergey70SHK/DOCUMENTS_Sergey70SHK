#!/bin/bash

# Скрипт настройки cron задач для мониторинга SK English Bot

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRON_FILE="/tmp/sk_bot_cron"

echo "Настройка cron задач для SK English Bot..."

# Создаем временный файл с cron задачами
cat > "$CRON_FILE" << EOF
# SK English Bot - Автоматический мониторинг и перезапуск
# Проверка каждые 5 минут
*/5 * * * * $SCRIPT_DIR/monitor_bot.sh >> $SCRIPT_DIR/logs/cron.log 2>&1

# Health check каждые 10 минут
*/10 * * * * cd $SCRIPT_DIR && $SCRIPT_DIR/start_bot.sh health >> $SCRIPT_DIR/logs/health_cron.log 2>&1

# Ротация логов каждый день в 2:00
0 2 * * * find $SCRIPT_DIR/logs -name "*.log" -size +100M -exec gzip {} \; >> $SCRIPT_DIR/logs/rotation.log 2>&1

# Очистка старых логов (старше 30 дней) каждую неделю
0 3 * * 0 find $SCRIPT_DIR/logs -name "*.log.gz" -mtime +30 -delete >> $SCRIPT_DIR/logs/cleanup.log 2>&1

# Перезапуск бота каждый день в 4:00 (для предотвращения накопления проблем)
0 4 * * * cd $SCRIPT_DIR && $SCRIPT_DIR/start_bot.sh restart >> $SCRIPT_DIR/logs/daily_restart.log 2>&1
EOF

# Устанавливаем cron задачи
if crontab -l > /dev/null 2>&1; then
    # Если crontab уже существует, добавляем наши задачи
    (crontab -l 2>/dev/null; echo ""; cat "$CRON_FILE") | crontab -
else
    # Если crontab не существует, создаем новый
    crontab "$CRON_FILE"
fi

# Удаляем временный файл
rm -f "$CRON_FILE"

echo "Cron задачи установлены успешно!"
echo ""
echo "Установленные задачи:"
crontab -l | grep -A 10 "SK English Bot"
echo ""
echo "Для просмотра всех cron задач: crontab -l"
echo "Для удаления cron задач: crontab -r"