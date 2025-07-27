#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SK English Bot - Telegram бот для изучения английского языка
Надежная архитектура с автоматическим восстановлением после ошибок
"""

import asyncio
import json
import logging
import os
import random
import signal
import sys
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
from telegram.error import TimedOut, NetworkError, RetryAfter, BadRequest

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Константы
QUIZ_WAITING, QUIZ_ANSWER = range(2)
MAX_RETRIES = 5
RETRY_DELAY = 5
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

class EnglishBot:
    def __init__(self, token: str):
        self.token = token
        self.application = None
        self.users_data = {}
        self.vocabulary = {}
        self.quiz_data = {}
        self.running = False
        self.restart_count = 0
        self.max_restarts = 10
        
        # Загружаем данные при инициализации
        self.load_data()
        self.load_vocabulary()
    
    def load_data(self):
        """Загрузка пользовательских данных"""
        try:
            if os.path.exists('users_data.json'):
                with open('users_data.json', 'r', encoding='utf-8') as f:
                    self.users_data = json.load(f)
                logger.info(f"Загружены данные {len(self.users_data)} пользователей")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных пользователей: {e}")
            self.users_data = {}
    
    def save_data(self):
        """Сохранение пользовательских данных"""
        try:
            with open('users_data.json', 'w', encoding='utf-8') as f:
                json.dump(self.users_data, f, ensure_ascii=False, indent=2)
            logger.info("Данные пользователей сохранены")
        except Exception as e:
            logger.error(f"Ошибка сохранения данных: {e}")
    
    def load_vocabulary(self):
        """Загрузка словаря"""
        try:
            if os.path.exists('vocabulary.json'):
                with open('vocabulary.json', 'r', encoding='utf-8') as f:
                    self.vocabulary = json.load(f)
            else:
                # Создаем базовый словарь если файл не существует
                self.vocabulary = {
                    "hello": {
                        "translation": "привет",
                        "definition": "a greeting used when meeting someone",
                        "example": "Hello, how are you today?",
                        "level": "beginner"
                    },
                    "beautiful": {
                        "translation": "красивый",
                        "definition": "pleasing the senses or mind aesthetically",
                        "example": "The sunset was beautiful tonight.",
                        "level": "beginner"
                    },
                    "adventure": {
                        "translation": "приключение",
                        "definition": "an unusual and exciting experience or activity",
                        "example": "Their trip to the mountains was a great adventure.",
                        "level": "intermediate"
                    },
                    "magnificent": {
                        "translation": "великолепный",
                        "definition": "extremely beautiful, elaborate, or impressive",
                        "example": "The cathedral was a magnificent sight.",
                        "level": "advanced"
                    }
                }
                self.save_vocabulary()
            logger.info(f"Загружен словарь: {len(self.vocabulary)} слов")
        except Exception as e:
            logger.error(f"Ошибка загрузки словаря: {e}")
            self.vocabulary = {}
    
    def save_vocabulary(self):
        """Сохранение словаря"""
        try:
            with open('vocabulary.json', 'w', encoding='utf-8') as f:
                json.dump(self.vocabulary, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Ошибка сохранения словаря: {e}")
    
    def get_user_data(self, user_id: int) -> Dict:
        """Получение данных пользователя"""
        if str(user_id) not in self.users_data:
            self.users_data[str(user_id)] = {
                'level': 'beginner',
                'words_learned': [],
                'quiz_score': 0,
                'last_activity': datetime.now().isoformat(),
                'daily_words': 0,
                'streak': 0
            }
            self.save_data()
        return self.users_data[str(user_id)]
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        try:
            user = update.effective_user
            user_data = self.get_user_data(user.id)
            
            welcome_text = f"""
🎉 Добро пожаловать в SK English Bot, {user.first_name}!

Я помогу вам изучать английский язык! 

📚 Доступные команды:
/menu - Главное меню
/word - Случайное слово дня
/quiz - Викторина
/level - Изменить уровень
/stats - Ваша статистика
/help - Помощь

Ваш текущий уровень: {user_data['level']}
Изученных слов: {len(user_data['words_learned'])}
            """
            
            keyboard = [
                [KeyboardButton("📚 Слово дня"), KeyboardButton("🎯 Викторина")],
                [KeyboardButton("📊 Статистика"), KeyboardButton("⚙️ Настройки")],
                [KeyboardButton("ℹ️ Помощь")]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(welcome_text, reply_markup=reply_markup)
            logger.info(f"Пользователь {user.id} ({user.first_name}) запустил бота")
            
        except Exception as e:
            logger.error(f"Ошибка в start_command: {e}")
            await self.send_error_message(update, "Произошла ошибка при запуске бота")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        try:
            help_text = """
📖 Помощь по боту SK English Bot

🔤 Основные функции:
• Изучение новых слов с переводом и примерами
• Викторины для закрепления знаний
• Отслеживание прогресса
• Адаптация под ваш уровень

📚 Команды:
/start - Перезапуск бота
/word - Получить случайное слово
/quiz - Начать викторину
/level - Изменить уровень (beginner/intermediate/advanced)
/stats - Посмотреть статистику
/help - Эта справка

💡 Советы:
• Изучайте по несколько слов каждый день
• Проходите викторины для закрепления
• Повышайте уровень по мере изучения

❓ Если бот не отвечает, попробуйте команду /start
            """
            await update.message.reply_text(help_text)
            
        except Exception as e:
            logger.error(f"Ошибка в help_command: {e}")
            await self.send_error_message(update, "Ошибка при показе справки")
    
    async def word_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /word"""
        try:
            user_data = self.get_user_data(update.effective_user.id)
            level = user_data['level']
            
            # Фильтруем слова по уровню пользователя
            level_words = {k: v for k, v in self.vocabulary.items() 
                          if v.get('level', 'beginner') == level}
            
            if not level_words:
                level_words = self.vocabulary
            
            word, data = random.choice(list(level_words.items()))
            
            word_text = f"""
📚 Слово дня: *{word.upper()}*

🔤 Перевод: {data['translation']}
📝 Определение: {data['definition']}
💬 Пример: _{data['example']}_
📊 Уровень: {data.get('level', 'beginner')}
            """
            
            # Добавляем слово в изученные
            if word not in user_data['words_learned']:
                user_data['words_learned'].append(word)
                user_data['daily_words'] += 1
                self.save_data()
            
            # Кнопки для действий
            keyboard = [
                [InlineKeyboardButton("🎯 Викторина с этим словом", callback_data=f"quiz_{word}")],
                [InlineKeyboardButton("📚 Еще слово", callback_data="another_word")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                word_text, 
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в word_command: {e}")
            await self.send_error_message(update, "Ошибка при получении слова")
    
    async def quiz_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /quiz"""
        try:
            user_data = self.get_user_data(update.effective_user.id)
            
            if len(user_data['words_learned']) < 3:
                await update.message.reply_text(
                    "📚 Сначала изучите больше слов! Используйте /word для изучения новых слов."
                )
                return
            
            # Выбираем случайное слово из изученных
            word = random.choice(user_data['words_learned'])
            word_data = self.vocabulary.get(word)
            
            if not word_data:
                await update.message.reply_text("❌ Ошибка: слово не найдено в словаре")
                return
            
            # Создаем варианты ответов
            correct_answer = word_data['translation']
            all_translations = [v['translation'] for v in self.vocabulary.values() 
                              if v['translation'] != correct_answer]
            
            if len(all_translations) < 3:
                # Если недостаточно вариантов, добавляем простые
                all_translations.extend(['собака', 'дом', 'машина', 'книга'])
            
            wrong_answers = random.sample(all_translations, 3)
            options = [correct_answer] + wrong_answers
            random.shuffle(options)
            
            # Сохраняем данные викторины
            quiz_id = f"{update.effective_user.id}_{int(time.time())}"
            self.quiz_data[quiz_id] = {
                'word': word,
                'correct_answer': correct_answer,
                'options': options
            }
            
            quiz_text = f"""
🎯 Викторина!

Что означает слово: *{word.upper()}*?

Определение: _{word_data['definition']}_
Пример: _{word_data['example']}_
            """
            
            # Создаем кнопки с вариантами
            keyboard = []
            for i, option in enumerate(options):
                keyboard.append([InlineKeyboardButton(
                    f"{chr(65+i)}. {option}", 
                    callback_data=f"quiz_answer_{quiz_id}_{option}"
                )])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                quiz_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Ошибка в quiz_command: {e}")
            await self.send_error_message(update, "Ошибка при создании викторины")
    
    async def level_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /level"""
        try:
            keyboard = [
                [InlineKeyboardButton("🟢 Начинающий", callback_data="level_beginner")],
                [InlineKeyboardButton("🟡 Средний", callback_data="level_intermediate")],
                [InlineKeyboardButton("🔴 Продвинутый", callback_data="level_advanced")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            user_data = self.get_user_data(update.effective_user.id)
            current_level = user_data['level']
            
            await update.message.reply_text(
                f"📊 Текущий уровень: {current_level}\n\nВыберите новый уровень:",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Ошибка в level_command: {e}")
            await self.send_error_message(update, "Ошибка при смене уровня")
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /stats"""
        try:
            user_data = self.get_user_data(update.effective_user.id)
            
            stats_text = f"""
📊 Ваша статистика:

🎯 Уровень: {user_data['level']}
📚 Слов изучено: {len(user_data['words_learned'])}
🏆 Очки викторины: {user_data['quiz_score']}
📅 Слов сегодня: {user_data['daily_words']}
🔥 Дней подряд: {user_data['streak']}

🎖️ Достижения:
{'🥇 Первые шаги' if len(user_data['words_learned']) >= 1 else '⭕ Изучите первое слово'}
{'🥈 Ученик' if len(user_data['words_learned']) >= 10 else '⭕ Изучите 10 слов'}
{'🥉 Знаток' if len(user_data['words_learned']) >= 50 else '⭕ Изучите 50 слов'}
{'🏆 Мастер' if user_data['quiz_score'] >= 100 else '⭕ Наберите 100 очков в викторинах'}
            """
            
            await update.message.reply_text(stats_text)
            
        except Exception as e:
            logger.error(f"Ошибка в stats_command: {e}")
            await self.send_error_message(update, "Ошибка при показе статистики")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на инлайн кнопки"""
        try:
            query = update.callback_query
            await query.answer()
            
            data = query.data
            
            if data.startswith("quiz_answer_"):
                await self.handle_quiz_answer(query, data)
            elif data.startswith("level_"):
                await self.handle_level_change(query, data)
            elif data == "another_word":
                await self.handle_another_word(query)
            elif data.startswith("quiz_"):
                await self.handle_word_quiz(query, data)
                
        except Exception as e:
            logger.error(f"Ошибка в button_callback: {e}")
            try:
                await query.edit_message_text("❌ Произошла ошибка при обработке кнопки")
            except:
                pass
    
    async def handle_quiz_answer(self, query, data: str):
        """Обработка ответа на викторину"""
        try:
            parts = data.split("_", 3)
            if len(parts) < 4:
                await query.edit_message_text("❌ Ошибка в данных викторины")
                return
                
            quiz_id = f"{parts[2]}_{parts[3].split('_')[0]}"
            user_answer = "_".join(parts[3].split('_')[1:])
            
            if quiz_id not in self.quiz_data:
                await query.edit_message_text("❌ Викторина устарела, начните новую")
                return
            
            quiz = self.quiz_data[quiz_id]
            correct_answer = quiz['correct_answer']
            word = quiz['word']
            
            user_data = self.get_user_data(query.from_user.id)
            
            if user_answer == correct_answer:
                user_data['quiz_score'] += 10
                result_text = f"✅ Правильно!\n\n*{word.upper()}* = {correct_answer}"
                
                # Добавляем мотивационное сообщение
                motivations = [
                    "Отлично! 🎉", "Великолепно! 🌟", "Превосходно! 🏆",
                    "Так держать! 💪", "Молодец! 👏"
                ]
                result_text = f"{random.choice(motivations)} " + result_text
                
            else:
                result_text = f"❌ Неправильно.\n\nПравильный ответ: *{word.upper()}* = {correct_answer}\nВаш ответ: {user_answer}"
            
            self.save_data()
            
            # Кнопка для новой викторины
            keyboard = [[InlineKeyboardButton("🎯 Еще викторина", callback_data="new_quiz")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                result_text,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
            # Удаляем данные викторины
            del self.quiz_data[quiz_id]
            
        except Exception as e:
            logger.error(f"Ошибка в handle_quiz_answer: {e}")
            await query.edit_message_text("❌ Ошибка при обработке ответа")
    
    async def handle_level_change(self, query, data: str):
        """Обработка смены уровня"""
        try:
            new_level = data.split("_")[1]
            user_data = self.get_user_data(query.from_user.id)
            user_data['level'] = new_level
            self.save_data()
            
            level_names = {
                'beginner': 'Начинающий 🟢',
                'intermediate': 'Средний 🟡',
                'advanced': 'Продвинутый 🔴'
            }
            
            await query.edit_message_text(
                f"✅ Уровень изменен на: {level_names[new_level]}"
            )
            
        except Exception as e:
            logger.error(f"Ошибка в handle_level_change: {e}")
            await query.edit_message_text("❌ Ошибка при смене уровня")
    
    async def handle_another_word(self, query):
        """Обработка запроса нового слова"""
        try:
            # Имитируем команду /word
            class FakeUpdate:
                def __init__(self, user, message):
                    self.effective_user = user
                    self.message = message
            
            class FakeMessage:
                def __init__(self, chat_id):
                    self.chat_id = chat_id
                    
                async def reply_text(self, text, reply_markup=None, parse_mode=None):
                    await query.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
            
            fake_update = FakeUpdate(query.from_user, FakeMessage(query.message.chat_id))
            await self.word_command(fake_update, None)
            
        except Exception as e:
            logger.error(f"Ошибка в handle_another_word: {e}")
            await query.edit_message_text("❌ Ошибка при получении нового слова")
    
    async def message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        try:
            text = update.message.text
            
            if text == "📚 Слово дня":
                await self.word_command(update, context)
            elif text == "🎯 Викторина":
                await self.quiz_command(update, context)
            elif text == "📊 Статистика":
                await self.stats_command(update, context)
            elif text == "⚙️ Настройки":
                await self.level_command(update, context)
            elif text == "ℹ️ Помощь":
                await self.help_command(update, context)
            else:
                # Обработка произвольного текста как поиска слова
                word = text.lower().strip()
                if word in self.vocabulary:
                    data = self.vocabulary[word]
                    response = f"""
📚 Слово: *{word.upper()}*

🔤 Перевод: {data['translation']}
📝 Определение: {data['definition']}
💬 Пример: _{data['example']}_
                    """
                    await update.message.reply_text(response, parse_mode='Markdown')
                else:
                    await update.message.reply_text(
                        f"🔍 Слово '{word}' не найдено в словаре.\n"
                        "Используйте /word для изучения новых слов!"
                    )
                    
        except Exception as e:
            logger.error(f"Ошибка в message_handler: {e}")
            await self.send_error_message(update, "Ошибка при обработке сообщения")
    
    async def send_error_message(self, update: Update, error_text: str):
        """Отправка сообщения об ошибке пользователю"""
        try:
            error_msg = f"❌ {error_text}\n\nПопробуйте команду /start для перезапуска бота."
            if update.message:
                await update.message.reply_text(error_msg)
            elif update.callback_query:
                await update.callback_query.message.reply_text(error_msg)
        except Exception as e:
            logger.error(f"Не удалось отправить сообщение об ошибке: {e}")
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("word", self.word_command))
        self.application.add_handler(CommandHandler("quiz", self.quiz_command))
        self.application.add_handler(CommandHandler("level", self.level_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.message_handler))
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Глобальный обработчик ошибок"""
        logger.error(f"Exception while handling an update: {context.error}")
        
        # Специальная обработка разных типов ошибок
        if isinstance(context.error, RetryAfter):
            logger.warning(f"Rate limited. Sleeping for {context.error.retry_after} seconds")
            await asyncio.sleep(context.error.retry_after)
        elif isinstance(context.error, TimedOut):
            logger.warning("Request timed out")
        elif isinstance(context.error, NetworkError):
            logger.warning("Network error occurred")
        elif isinstance(context.error, BadRequest):
            logger.warning(f"Bad request: {context.error}")
        else:
            logger.error(f"Unexpected error: {context.error}")
        
        # Попытка уведомить пользователя об ошибке
        if update and hasattr(update, 'effective_chat'):
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ Произошла временная ошибка. Бот восстанавливается..."
                )
            except Exception:
                pass
    
    async def shutdown_handler(self, signum, frame):
        """Обработчик корректного завершения работы"""
        logger.info(f"Получен сигнал {signum}. Завершаем работу...")
        self.running = False
        
        if self.application:
            await self.application.stop()
            
        # Сохраняем данные перед выходом
        self.save_data()
        logger.info("Бот остановлен")
        sys.exit(0)
    
    async def run_with_restart(self):
        """Запуск бота с автоматическим перезапуском при ошибках"""
        while self.restart_count < self.max_restarts:
            try:
                logger.info(f"Запуск бота (попытка {self.restart_count + 1})")
                
                # Создаем приложение
                self.application = Application.builder().token(self.token).build()
                
                # Настраиваем обработчики
                self.setup_handlers()
                self.application.add_error_handler(self.error_handler)
                
                # Устанавливаем обработчики сигналов
                signal.signal(signal.SIGINT, lambda s, f: asyncio.create_task(self.shutdown_handler(s, f)))
                signal.signal(signal.SIGTERM, lambda s, f: asyncio.create_task(self.shutdown_handler(s, f)))
                
                self.running = True
                
                # Запускаем бота
                await self.application.initialize()
                await self.application.start()
                await self.application.updater.start_polling(
                    drop_pending_updates=True,
                    timeout=30,
                    read_timeout=30,
                    write_timeout=30,
                    connect_timeout=30
                )
                
                logger.info("SK English Bot запущен и готов к работе!")
                
                # Ждем завершения
                while self.running:
                    await asyncio.sleep(1)
                    
                break
                
            except Exception as e:
                self.restart_count += 1
                logger.error(f"Критическая ошибка: {e}")
                logger.info(f"Перезапуск через {RETRY_DELAY} секунд...")
                
                if self.application:
                    try:
                        await self.application.stop()
                    except:
                        pass
                
                if self.restart_count < self.max_restarts:
                    await asyncio.sleep(RETRY_DELAY)
                else:
                    logger.error("Достигнуто максимальное количество перезапусков")
                    break
    
    async def run(self):
        """Основной метод запуска"""
        try:
            await self.run_with_restart()
        except KeyboardInterrupt:
            logger.info("Получен сигнал прерывания")
        finally:
            # Финальное сохранение данных
            self.save_data()
            logger.info("Работа бота завершена")

async def main():
    """Главная функция"""
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        logger.error("Пожалуйста, установите BOT_TOKEN в переменных окружения")
        return
    
    bot = EnglishBot(BOT_TOKEN)
    await bot.run()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Программа прервана пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")