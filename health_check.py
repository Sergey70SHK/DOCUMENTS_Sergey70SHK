#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Health Check скрипт для SK English Bot
Проверяет доступность Telegram API и состояние бота
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from telegram import Bot
from telegram.error import TelegramError

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('health_check.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BotHealthChecker:
    def __init__(self, token: str):
        self.token = token
        self.bot = Bot(token=token)
        self.status_file = Path("bot_status.json")
        
    async def check_telegram_api(self) -> bool:
        """Проверяет доступность Telegram API"""
        try:
            response = requests.get(
                "https://api.telegram.org/bot{}/getMe".format(self.token),
                timeout=10
            )
            if response.status_code == 200:
                logger.info("✅ Telegram API доступен")
                return True
            else:
                logger.error(f"❌ Telegram API недоступен: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к Telegram API: {e}")
            return False
    
    async def check_bot_info(self) -> bool:
        """Проверяет информацию о боте"""
        try:
            bot_info = await self.bot.get_me()
            logger.info(f"✅ Бот активен: @{bot_info.username} ({bot_info.first_name})")
            return True
        except TelegramError as e:
            logger.error(f"❌ Ошибка получения информации о боте: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Неожиданная ошибка: {e}")
            return False
    
    async def check_webhook_status(self) -> dict:
        """Проверяет статус webhook"""
        try:
            webhook_info = await self.bot.get_webhook_info()
            status = {
                "url": webhook_info.url,
                "has_custom_certificate": webhook_info.has_custom_certificate,
                "pending_update_count": webhook_info.pending_update_count,
                "last_error_date": webhook_info.last_error_date,
                "last_error_message": webhook_info.last_error_message,
                "max_connections": webhook_info.max_connections,
                "allowed_updates": webhook_info.allowed_updates
            }
            logger.info(f"📡 Webhook статус: {json.dumps(status, indent=2, default=str)}")
            return status
        except Exception as e:
            logger.error(f"❌ Ошибка проверки webhook: {e}")
            return {}
    
    async def test_message_sending(self, chat_id: str = None) -> bool:
        """Тестирует отправку сообщений"""
        if not chat_id:
            logger.info("⚠️ Chat ID не указан, пропускаем тест отправки сообщений")
            return True
            
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text="🔍 Health check test - бот работает нормально!"
            )
            logger.info("✅ Тестовое сообщение отправлено успешно")
            return True
        except TelegramError as e:
            logger.error(f"❌ Ошибка отправки тестового сообщения: {e}")
            return False
    
    def save_status(self, status: dict):
        """Сохраняет статус в файл"""
        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2, default=str, ensure_ascii=False)
            logger.info(f"📁 Статус сохранен в {self.status_file}")
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения статуса: {e}")
    
    def load_previous_status(self) -> dict:
        """Загружает предыдущий статус"""
        try:
            if self.status_file.exists():
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки предыдущего статуса: {e}")
        return {}
    
    async def run_full_check(self, test_chat_id: str = None) -> dict:
        """Запускает полную проверку здоровья бота"""
        logger.info("🔍 Начинаем проверку здоровья бота...")
        
        start_time = datetime.now()
        status = {
            "timestamp": start_time,
            "checks": {}
        }
        
        # Проверка Telegram API
        status["checks"]["telegram_api"] = await self.check_telegram_api()
        
        # Проверка информации о боте
        status["checks"]["bot_info"] = await self.check_bot_info()
        
        # Проверка webhook
        webhook_status = await self.check_webhook_status()
        status["checks"]["webhook"] = webhook_status
        
        # Тест отправки сообщений
        if test_chat_id:
            status["checks"]["message_sending"] = await self.test_message_sending(test_chat_id)
        
        # Общий статус
        all_checks_passed = all([
            status["checks"].get("telegram_api", False),
            status["checks"].get("bot_info", False)
        ])
        
        status["overall_status"] = "healthy" if all_checks_passed else "unhealthy"
        status["duration"] = (datetime.now() - start_time).total_seconds()
        
        # Сохраняем статус
        self.save_status(status)
        
        # Логируем результат
        if all_checks_passed:
            logger.info("✅ Все проверки пройдены успешно!")
        else:
            logger.error("❌ Обнаружены проблемы в работе бота")
        
        return status

async def main():
    """Основная функция"""
    # Получаем токен из переменной окружения или файла .env
    token = os.getenv("BOT_TOKEN")
    
    if not token:
        try:
            # Пытаемся загрузить из .env файла
            if os.path.exists(".env"):
                with open(".env", "r") as f:
                    for line in f:
                        if line.strip().startswith("BOT_TOKEN="):
                            token = line.strip().split("=", 1)[1]
                            break
        except Exception as e:
            logger.error(f"Ошибка чтения .env файла: {e}")
    
    if not token:
        logger.error("❌ Токен бота не найден! Установите переменную BOT_TOKEN или создайте .env файл")
        sys.exit(1)
    
    # Получаем chat_id для тестирования (опционально)
    test_chat_id = os.getenv("TEST_CHAT_ID")
    
    # Создаем checker и запускаем проверку
    checker = BotHealthChecker(token)
    
    try:
        status = await checker.run_full_check(test_chat_id)
        
        # Выводим краткий отчет
        print("\n" + "="*50)
        print("📊 ОТЧЕТ О ЗДОРОВЬЕ БОТА")
        print("="*50)
        print(f"🕐 Время проверки: {status['timestamp']}")
        print(f"⏱️ Длительность: {status['duration']:.2f} сек")
        print(f"🎯 Общий статус: {status['overall_status'].upper()}")
        print("\n📋 Детальные проверки:")
        
        for check_name, check_result in status["checks"].items():
            if isinstance(check_result, bool):
                icon = "✅" if check_result else "❌"
                print(f"  {icon} {check_name}: {'PASS' if check_result else 'FAIL'}")
            elif isinstance(check_result, dict) and check_name == "webhook":
                print(f"  📡 webhook: {json.dumps(check_result, indent=4, default=str)}")
        
        print("="*50)
        
        # Возвращаем код выхода
        sys.exit(0 if status['overall_status'] == 'healthy' else 1)
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при проверке: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())