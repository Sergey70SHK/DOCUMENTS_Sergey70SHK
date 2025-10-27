#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SK English Bot - Исправленная версия
Telegram бот для изучения английского языка
"""

import asyncio
import json
import logging
import os
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.error import TelegramError, TimedOut, NetworkError, RetryAfter

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SKEnglishBot:
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        
        # Данные пользователей
        self.users_data = {}
        self.quiz_data = {}
        
        # Словарь для изучения
        self.vocabulary = {
            "hello": {
                "translation": "привет",
                "definition": "greeting used when meeting someone",
                "example": "Hello, how are you?",
                "level": "beginner"
            },
            "study": {
                "translation": "изучать",
                "definition": "to learn about something by reading, memorizing facts, attending classes",
                "example": "I study English every day",
                "level": "beginner"
            },
            "beautiful": {
                "translation": "красивый",
                "definition": "pleasing the senses or mind aesthetically",
                "example": "She has beautiful eyes",
                "level": "intermediate"
            },
            "knowledge": {
                "translation": "знание",
                "definition": "facts, information, and skills acquired through experience or education",
                "example": "Knowledge is power",
                "level": "intermediate"
            },
            "sophisticated": {
                "translation": "сложный",
                "definition": "having great knowledge or experience",
                "example": "A sophisticated algorithm",
                "level": "advanced"
            }
        }
        
        self.setup_handlers()
        
    def setup_handlers(self):
        """Настройка обработчиков команд и сообщений"""
        # Команды
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("learn", self.learn_command))
        self.application.add_handler(CommandHandler("quiz", self.quiz_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("level", self.level_command))
        
        # Callback кнопки
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Обработка текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name or "Friend"
        
        # Инициализация пользователя
        if user_id not in self.users_data:
            self.users_data[user_id] = {
                'name': user_name,
                'level': 'beginner',
                'words_learned': [],
                'quiz_scores': [],
                'last_active': datetime.now().isoformat(),
                'total_words': 0,
                'total_quizzes': 0
            }
            
        welcome_text = f"""
🌟 Добро пожаловать в SK English Bot, {user_name}!

Я помогу вам изучать английский язык! 📚

🔥 Что я умею:
• 📖 Изучение новых слов с переводом и примерами
• 🎯 Интерактивные викторины для закрепления
• 📊 Отслеживание вашего прогресса
• 🎚️ Разные уровни сложности

Используйте кнопки ниже или команды:
/learn - изучить новое слово
/quiz - пройти викторину
/stats - посмотреть статистику
/level - изменить уровень сложности
        """
        
        # Создаем основное меню
        keyboard = [
            [KeyboardButton("📖 Изучить слово"), KeyboardButton("🎯 Викторина")],
            [KeyboardButton("📊 Статистика"), KeyboardButton("🎚️ Уровень")],
            [KeyboardButton("❓ Помощь")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
        
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help"""
        help_text = """
🆘 Помощь - SK English Bot

📚 Доступные команды:
/start - начать работу с ботом
/learn - изучить новое слово
/quiz - пройти викторину
/stats - посмотреть статистику
/level - изменить уровень (beginner/intermediate/advanced)

🎮 Как пользоваться:
1. Начните с команды /learn чтобы изучить новые слова
2. Используйте /quiz чтобы проверить знания
3. Отслеживайте прогресс через /stats

💡 Советы:
• Изучайте по 5-10 слов в день
• Регулярно проходите викторины
• Повышайте уровень постепенно

❓ Вопросы? Пишите @support (это пример)
        """
        
        await update.message.reply_text(help_text)
        
    async def learn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /learn - изучение нового слова"""
        user_id = update.effective_user.id
        
        if user_id not in self.users_data:
            await self.start_command(update, context)
            return
            
        user_level = self.users_data[user_id]['level']
        learned_words = self.users_data[user_id]['words_learned']
        
        # Фильтруем слова по уровню и исключаем уже изученные
        available_words = [
            word for word, data in self.vocabulary.items()
            if data['level'] == user_level and word not in learned_words
        ]
        
        if not available_words:
            await update.message.reply_text(
                f"🎉 Поздравляю! Вы изучили все слова уровня {user_level}!\n"
                f"Попробуйте повысить уровень командой /level"
            )
            return
            
        # Выбираем случайное слово
        word = random.choice(available_words)
        word_data = self.vocabulary[word]
        
        # Добавляем слово в изученные
        self.users_data[user_id]['words_learned'].append(word)
        self.users_data[user_id]['total_words'] += 1
        self.users_data[user_id]['last_active'] = datetime.now().isoformat()
        
        learn_text = f"""
📖 Новое слово для изучения!

🔤 **{word.upper()}**
🔄 Перевод: **{word_data['translation']}**
📝 Определение: _{word_data['definition']}_
💭 Пример: _{word_data['example']}_
🎚️ Уровень: {word_data['level']}

✅ Слово добавлено в ваш словарь!
📊 Всего изучено: {len(self.users_data[user_id]['words_learned'])} слов
        """
        
        await update.message.reply_text(learn_text, parse_mode='Markdown')
        
    async def quiz_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /quiz - викторина"""
        user_id = update.effective_user.id
        
        if user_id not in self.users_data:
            await self.start_command(update, context)
            return
            
        learned_words = self.users_data[user_id]['words_learned']
        
        if len(learned_words) < 4:
            await update.message.reply_text(
                "📚 Для викторины нужно изучить минимум 4 слова!\n"
                "Используйте /learn чтобы изучить больше слов."
            )
            return
            
        # Выбираем случайное слово для викторины
        word = random.choice(learned_words)
        word_data = self.vocabulary.get(word)
        
        if not word_data:
            await update.message.reply_text("❌ Ошибка: слово не найдено в словаре")
            return
            
        # Создаем варианты ответов
        correct_answer = word_data['translation']
        all_translations = [self.vocabulary[w]['translation'] for w in learned_words if w != word]
        
        if len(all_translations) < 3:
            # Добавляем дополнительные варианты
            extra_translations = ['собака', 'дом', 'машина', 'книга', 'дерево', 'вода']
            all_translations.extend([t for t in extra_translations if t != correct_answer])
            
        wrong_answers = random.sample(all_translations, min(3, len(all_translations)))
        options = [correct_answer] + wrong_answers
        random.shuffle(options)
        
        # Сохраняем данные викторины
        quiz_id = f"{user_id}_{int(time.time())}"
        self.quiz_data[quiz_id] = {
            'word': word,
            'correct_answer': correct_answer,
            'options': options,
            'user_id': user_id
        }
        
        quiz_text = f"""
🎯 Викторина!

Что означает слово: **{word.upper()}**?

📝 Определение: _{word_data['definition']}_
💭 Пример: _{word_data['example']}_
        """
        
        # Создаем кнопки с вариантами
        keyboard = []
        for i, option in enumerate(options):
            keyboard.append([InlineKeyboardButton(
                f"{chr(65+i)} {option}", 
                callback_data=f"quiz_{quiz_id}_{i}"
            )])
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(quiz_text, reply_markup=reply_markup, parse_mode='Markdown')
        
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /stats - статистика пользователя"""
        user_id = update.effective_user.id
        
        if user_id not in self.users_data:
            await self.start_command(update, context)
            return
            
        user_data = self.users_data[user_id]
        
        # Подсчитываем статистику
        total_words = len(user_data['words_learned'])
        total_quizzes = len(user_data['quiz_scores'])
        avg_score = sum(user_data['quiz_scores']) / max(1, total_quizzes) if user_data['quiz_scores'] else 0
        
        # Прогресс по уровням
        beginner_words = sum(1 for word in user_data['words_learned'] 
                           if self.vocabulary.get(word, {}).get('level') == 'beginner')
        intermediate_words = sum(1 for word in user_data['words_learned'] 
                               if self.vocabulary.get(word, {}).get('level') == 'intermediate')
        advanced_words = sum(1 for word in user_data['words_learned'] 
                           if self.vocabulary.get(word, {}).get('level') == 'advanced')
        
        stats_text = f"""
📊 Ваша статистика

👤 Имя: {user_data['name']}
🎚️ Уровень: {user_data['level']}

📚 Изучение слов:
• Всего изучено: {total_words} слов
• Beginner: {beginner_words} слов
• Intermediate: {intermediate_words} слов  
• Advanced: {advanced_words} слов

🎯 Викторины:
• Пройдено: {total_quizzes} викторин
• Средний балл: {avg_score:.1f}%

⏰ Последняя активность: {user_data['last_active'][:16]}

🏆 Достижения:
{self.get_achievements(user_data)}
        """
        
        await update.message.reply_text(stats_text)
        
    def get_achievements(self, user_data) -> str:
        """Получить достижения пользователя"""
        achievements = []
        
        total_words = len(user_data['words_learned'])
        if total_words >= 10:
            achievements.append("🥉 Изучил 10+ слов")
        if total_words >= 50:
            achievements.append("🥈 Изучил 50+ слов")
        if total_words >= 100:
            achievements.append("🥇 Изучил 100+ слов")
            
        avg_score = sum(user_data['quiz_scores']) / max(1, len(user_data['quiz_scores'])) if user_data['quiz_scores'] else 0
        if avg_score >= 80:
            achievements.append("🎯 Отличник (80%+ в викторинах)")
            
        return "\n".join(achievements) if achievements else "Пока нет достижений"
        
    async def level_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /level - изменение уровня сложности"""
        user_id = update.effective_user.id
        
        if user_id not in self.users_data:
            await self.start_command(update, context)
            return
            
        keyboard = [
            [InlineKeyboardButton("🟢 Beginner", callback_data="level_beginner")],
            [InlineKeyboardButton("🟡 Intermediate", callback_data="level_intermediate")],
            [InlineKeyboardButton("🔴 Advanced", callback_data="level_advanced")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        current_level = self.users_data[user_id]['level']
        
        level_text = f"""
🎚️ Выбор уровня сложности

Ваш текущий уровень: **{current_level}**

🟢 **Beginner** - базовые слова
🟡 **Intermediate** - средний уровень  
🔴 **Advanced** - сложные слова

Выберите подходящий уровень:
        """
        
        await update.message.reply_text(level_text, reply_markup=reply_markup, parse_mode='Markdown')
        
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатий на кнопки"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith("quiz_"):
            await self.handle_quiz_answer(query)
        elif data.startswith("level_"):
            await self.handle_level_change(query)
            
    async def handle_quiz_answer(self, query):
        """Обработка ответа в викторине"""
        data_parts = query.data.split("_")
        quiz_id = "_".join(data_parts[1:-1])
        selected_option = int(data_parts[-1])
        
        if quiz_id not in self.quiz_data:
            await query.edit_message_text("❌ Викторина устарела, попробуйте снова /quiz")
            return
            
        quiz_info = self.quiz_data[quiz_id]
        user_id = quiz_info['user_id']
        correct_answer = quiz_info['correct_answer']
        selected_answer = quiz_info['options'][selected_option]
        
        is_correct = selected_answer == correct_answer
        
        # Обновляем статистику
        if user_id in self.users_data:
            score = 100 if is_correct else 0
            self.users_data[user_id]['quiz_scores'].append(score)
            self.users_data[user_id]['total_quizzes'] += 1
            self.users_data[user_id]['last_active'] = datetime.now().isoformat()
            
        # Формируем ответ
        if is_correct:
            result_text = f"""
✅ **Правильно!**

🔤 {quiz_info['word'].upper()} = {correct_answer}

🎉 Отличная работа! +100 баллов
            """
        else:
            result_text = f"""
❌ **Неправильно**

🔤 {quiz_info['word'].upper()} = {correct_answer}
Вы ответили: {selected_answer}

💪 Не расстраивайтесь, попробуйте еще раз!
            """
            
        # Удаляем использованные данные викторины
        del self.quiz_data[quiz_id]
        
        await query.edit_message_text(result_text, parse_mode='Markdown')
        
    async def handle_level_change(self, query):
        """Обработка смены уровня"""
        user_id = query.from_user.id
        new_level = query.data.split("_")[1]
        
        if user_id in self.users_data:
            self.users_data[user_id]['level'] = new_level
            self.users_data[user_id]['last_active'] = datetime.now().isoformat()
            
        level_names = {
            'beginner': '🟢 Beginner',
            'intermediate': '🟡 Intermediate', 
            'advanced': '🔴 Advanced'
        }
        
        await query.edit_message_text(
            f"✅ Уровень изменен на {level_names[new_level]}!\n\n"
            f"Теперь вы можете изучать слова этого уровня через /learn"
        )
        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        text = update.message.text.lower()
        
        if "изучить слово" in text or "📖" in text:
            await self.learn_command(update, context)
        elif "викторина" in text or "🎯" in text:
            await self.quiz_command(update, context)
        elif "статистика" in text or "📊" in text:
            await self.stats_command(update, context)
        elif "уровень" in text or "🎚️" in text:
            await self.level_command(update, context)
        elif "помощь" in text or "❓" in text:
            await self.help_command(update, context)
        else:
            await update.message.reply_text(
                "🤔 Не понял вас. Используйте кнопки меню или команды:\n"
                "/learn - изучить слово\n"
                "/quiz - викторина\n"
                "/help - помощь"
            )
            
    def save_user_data(self):
        """Сохранение данных пользователей"""
        try:
            with open('user_data.json', 'w', encoding='utf-8') as f:
                json.dump(self.users_data, f, ensure_ascii=False, indent=2)
            logger.info("Данные пользователей сохранены")
        except Exception as e:
            logger.error(f"Ошибка сохранения данных: {e}")
            
    def load_user_data(self):
        """Загрузка данных пользователей"""
        try:
            if os.path.exists('user_data.json'):
                with open('user_data.json', 'r', encoding='utf-8') as f:
                    self.users_data = json.load(f)
                logger.info("Данные пользователей загружены")
        except Exception as e:
            logger.error(f"Ошибка загрузки данных: {e}")
            
    async def run(self):
        """Запуск бота"""
        try:
            # Загружаем данные пользователей
            self.load_user_data()
            
            logger.info("🚀 Запуск SK English Bot...")
            
            # Запускаем бота
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling(
                timeout=30,
                bootstrap_retries=-1,
                read_timeout=30,
                write_timeout=30,
                connect_timeout=30,
                pool_timeout=30
            )
            
            logger.info("✅ SK English Bot успешно запущен!")
            
            # Ждем до получения сигнала остановки
            await self.application.updater.idle()
            
        except Exception as e:
            logger.error(f"Критическая ошибка: {e}")
            raise
        finally:
            # Сохраняем данные при завершении
            self.save_user_data()
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Работа бота завершена")

async def main():
    """Главная функция"""
    # Получаем токен
    token = os.getenv('BOT_TOKEN')
    if not token:
        logger.error("Пожалуйста, установите BOT_TOKEN в переменных окружения")
        return
        
    # Создаем и запускаем бота
    bot = SKEnglishBot(token)
    await bot.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        raise