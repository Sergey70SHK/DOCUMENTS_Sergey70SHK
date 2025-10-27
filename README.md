# SK English Bot 🤖📚

Надежный Telegram бот для изучения английского языка с автоматическим восстановлением после ошибок.

## 🌟 Возможности

- 📚 **Изучение слов**: Получайте новые английские слова с переводом, определением и примерами
- 🎯 **Викторины**: Закрепляйте знания через интерактивные тесты
- 📊 **Статистика**: Отслеживайте свой прогресс в изучении языка
- 🎚️ **Уровни сложности**: Beginner, Intermediate, Advanced
- 🔄 **Автовосстановление**: Бот автоматически перезапускается при ошибках
- 💾 **Сохранение данных**: Весь прогресс сохраняется в JSON файлах

## 🚀 Быстрый старт

### Автоматическая установка (рекомендуется)

```bash
# Запустите автоматический скрипт установки
./install.sh
```

Скрипт автоматически:
- Установит все системные зависимости
- Создаст виртуальное окружение
- Настроит конфигурацию
- Предложит настроить автозапуск
- Протестирует установку

### Ручная установка

#### 1. Создание бота в Telegram

1. Найдите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте `/newbot`
3. Придумайте имя и username для бота
4. Скопируйте полученный токен

#### 2. Установка зависимостей

```bash
# Установите системные пакеты
cd /workspace

# Установите Python зависимости
pip3 install -r requirements.txt
```

### 3. Настройка

```bash
# Скопируйте пример конфигурации
cp .env.example .env

# Отредактируйте .env файл и добавьте ваш токен
nano .env
```

Установите ваш BOT_TOKEN в файле `.env`:
```env
BOT_TOKEN=1234567890:AAEhBOwECOKEOSFmMJdoEKEOFsdfMdo
```

### 4. Запуск

```bash
# Простой запуск
python3 sk_english_bot.py

# Или через скрипт мониторинга
chmod +x monitor_bot.sh
./monitor_bot.sh start
```

## 🔧 Автоматический запуск (systemd)

Для автоматического запуска при загрузке системы:

```bash
# Отредактируйте сервис файл
sudo nano sk-english-bot.service

# Установите правильные пути и токен, затем:
sudo cp sk-english-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable sk-english-bot
sudo systemctl start sk-english-bot

# Проверка статуса
sudo systemctl status sk-english-bot
```

## 📋 Управление ботом

### Использование скрипта мониторинга

```bash
# Запустить бота
./monitor_bot.sh start

# Остановить бота
./monitor_bot.sh stop

# Перезапустить бота
./monitor_bot.sh restart

# Проверить статус
./monitor_bot.sh status

# Запустить мониторинг (автоматический перезапуск)
./monitor_bot.sh monitor
```

### Команды systemd

```bash
# Запуск
sudo systemctl start sk-english-bot

# Остановка
sudo systemctl stop sk-english-bot

# Перезапуск
sudo systemctl restart sk-english-bot

# Статус
sudo systemctl status sk-english-bot

# Логи
sudo journalctl -u sk-english-bot -f
```

## 🤖 Команды бота

### Основные команды:
- `/start` - Запуск бота и главное меню
- `/help` - Справка по использованию
- `/word` - Получить случайное слово дня
- `/quiz` - Начать викторину
- `/level` - Изменить уровень сложности
- `/stats` - Посмотреть свою статистику

### Кнопки меню:
- 📚 **Слово дня** - Новое слово для изучения
- 🎯 **Викторина** - Проверить знания
- 📊 **Статистика** - Ваш прогресс
- ⚙️ **Настройки** - Изменить уровень
- ℹ️ **Помощь** - Справочная информация

## 🐛 Устранение неполадок

### Проблема: Бот не отвечает

1. **Проверьте статус процесса:**
   ```bash
   ./monitor_bot.sh status
   # или
   ps aux | grep sk_english_bot
   ```

2. **Проверьте логи:**
   ```bash
   tail -f bot.log
   # или
   tail -f monitor.log
   ```

3. **Перезапустите бота:**
   ```bash
   ./monitor_bot.sh restart
   ```

### Проблема: Ошибки сети

1. **Проверьте соединение с Telegram:**
   ```bash
   curl -s https://api.telegram.org/bot$BOT_TOKEN/getMe
   ```

2. **Проверьте токен:**
   - Убедитесь, что токен правильный
   - Проверьте, что бот не заблокирован

### Проблема: Высокое потребление памяти

1. **Мониторинг автоматически перезапустит бота при превышении лимита**

2. **Изменить лимит памяти:**
   ```bash
   # В файле monitor_bot.sh измените:
   MAX_MEMORY_MB=1000  # увеличить лимит
   ```

### Проблема: Бот постоянно перезапускается

1. **Проверьте логи ошибок:**
   ```bash
   tail -f bot.log | grep ERROR
   ```

2. **Возможные причины:**
   - Неправильный токен
   - Нет интернет соединения
   - Поврежденные файлы данных
   - Нехватка места на диске

3. **Решение:**
   ```bash
   # Очистите данные если нужно
   rm -f users_data.json vocabulary.json
   
   # Перезапустите
   ./monitor_bot.sh restart
   ```

## 📁 Структура файлов

```
/workspace/
├── sk_english_bot.py      # Основной файл бота
├── monitor_bot.sh         # Скрипт мониторинга
├── requirements.txt       # Зависимости Python
├── sk-english-bot.service # Systemd сервис
├── .env.example          # Пример конфигурации
├── .env                  # Ваша конфигурация (создается вами)
├── README.md             # Эта документация
├── users_data.json       # Данные пользователей (создается автоматически)
├── vocabulary.json       # Словарь (создается автоматически)
├── bot.log              # Логи бота
├── monitor.log          # Логи мониторинга
├── bot_output.log       # Вывод бота
├── bot.pid              # PID файл
└── requirements_installed.flag # Флаг установки зависимостей
```

## 🔒 Безопасность

1. **Никогда не публикуйте токен бота в открытых репозиториях**
2. **Установите правильные права на файлы:**
   ```bash
   chmod 600 .env
   chmod 755 monitor_bot.sh
   chmod 644 sk_english_bot.py
   ```

3. **Регулярно обновляйте зависимости:**
   ```bash
   pip3 install -r requirements.txt --upgrade
   ```

## 📈 Мониторинг и логи

### Просмотр логов в реальном времени:
```bash
# Логи бота
tail -f bot.log

# Логи мониторинга
tail -f monitor.log

# Системные логи (systemd)
sudo journalctl -u sk-english-bot -f
```

### Анализ производительности:
```bash
# Использование памяти
ps aux | grep sk_english_bot

# Использование диска
du -sh /workspace/

# Статистика сети
netstat -an | grep python3
```

## 🔄 Обновление

1. **Сделайте резервную копию данных:**
   ```bash
   cp users_data.json users_data.json.backup
   cp vocabulary.json vocabulary.json.backup
   ```

2. **Остановите бота:**
   ```bash
   ./monitor_bot.sh stop
   ```

3. **Обновите код:**
   ```bash
   # Скачайте новую версию
   # Замените файлы
   ```

4. **Запустите бота:**
   ```bash
   ./monitor_bot.sh start
   ```

## 🔥 Устранение проблем с отключениями

### Основные причины отключений и решения

#### 1. Проблемы с сетью и API Telegram
```bash
# Проверить доступность Telegram API
./start_bot.sh health

# Посмотреть логи ошибок сети
./start_bot.sh logs | grep -i "network\|timeout\|connection"
```

**Решения:**
- Включен механизм автоматических повторных попыток
- Таймауты настроены на разумные значения  
- Используется exponential backoff для повторных подключений

#### 2. Превышение лимитов памяти
```bash
# Проверить использование памяти
./start_bot.sh status

# Настроить лимит памяти в .env
echo "MAX_MEMORY_MB=300" >> .env
```

#### 3. Проблемы с токеном бота
```bash
# Проверить валидность токена
python3 health_check.py

# Обновить токен в .env файле
nano .env
```

#### 4. Конфликт webhook/polling
```bash
# Сбросить webhook (если используется polling)
curl -X POST "https://api.telegram.org/bot$BOT_TOKEN/deleteWebhook"
```

### Автоматическое восстановление

Бот имеет многоуровневую систему восстановления:

1. **Автоматический перезапуск** - при падении процесса
2. **Health monitoring** - проверка каждые 30 секунд
3. **Memory monitoring** - перезапуск при превышении лимитов
4. **Network recovery** - повторные попытки при сетевых ошибках
5. **Cron backup** - проверка каждые 5 минут через cron

### Включение расширенного мониторинга

```bash
# Настроить cron для автоматического мониторинга
./setup_cron.sh

# Или настроить systemd сервис
sudo cp sk-english-bot.service /etc/systemd/system/
sudo systemctl enable sk-english-bot
sudo systemctl start sk-english-bot
```

### Отладка проблем

```bash
# Полные логи
./start_bot.sh logs 100

# Только ошибки
grep -i "error\|exception\|failed" logs/error.log

# Логи перезапусков
cat logs/restart.log

# Мониторинг в реальном времени
tail -f logs/bot.log
```

### Настройка уведомлений об ошибках

Добавьте в `.env`:
```bash
# ID вашего чата для уведомлений об ошибках
ADMIN_CHAT_ID=ваш_chat_id

# Включить уведомления о критических ошибках  
NOTIFY_ERRORS=true
```

### Быстрое восстановление

Если бот постоянно отключается:

```bash
# 1. Полная переустановка окружения
./start_bot.sh stop
rm -rf bot_env
./install.sh

# 2. Сброс всех настроек
./start_bot.sh stop
rm -f bot.pid bot_status.json
rm -rf logs/*

# 3. Принудительная очистка процессов
pkill -f "sk_english_bot.py"
./start_bot.sh start

# 4. Проверка системных ресурсов
free -h  # память
df -h    # диск
```

## 📞 Поддержка

Если у вас возникли проблемы:

1. **Быстрая диагностика**: `./start_bot.sh health`
2. **Проверьте логи**: `./start_bot.sh logs`
3. **Статус бота**: `./start_bot.sh status`
4. **Перезапуск**: `./start_bot.sh restart`
5. **Полная переустановка**: `./install.sh`

## 📄 Лицензия

MIT License. Вы можете свободно использовать, изменять и распространять этот код.

---

**SK English Bot** - надежное решение для изучения английского языка в Telegram! 🎓✨