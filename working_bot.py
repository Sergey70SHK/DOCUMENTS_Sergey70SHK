#!/usr/bin/env python3
"""
SK English Bot - Рабочая версия
"""

import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SKEnglishBot:
    def __init__(self):
        self.users_data = {}
        
        # Словарь для изучения
        self.vocabulary = {
            "hello": {"translation": "привет", "level": "beginner"},
            "study": {"translation": "изучать", "level": "beginner"},
            "beautiful": {"translation": "красивый", "level": "intermediate"},
            "knowledge": {"translation": "знание", "level": "intermediate"},
            "sophisticated": {"translation": "сложный", "level": "advanced"}
        }
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name or "Friend"
        
        # Инициализация пользователя
        if user_id not in self.users_data:
            self.users_data[user_id] = {
                'name': user_name,
                'level': 'beginner',
                'words_learned': [],
                'score': 0
            }
            
        keyboard = [
            [KeyboardButton("📖 Learn Word"), KeyboardButton("🎯 Quiz")],
            [KeyboardButton("📊 My Stats"), KeyboardButton("ℹ️ Help")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        welcome_text = f"""
🌟 **Welcome to SK English Bot, {user_name}!**

I'm your English learning assistant! 📚

🔥 **What I can do:**
• 📖 Teach you new English words
• 🎯 Test your knowledge with quizzes  
• 📊 Track your learning progress
• 🎚️ Adapt to your skill level

Use the buttons below or type commands:
/learn - learn a new word
/quiz - take a quiz
/stats - see your progress

**Let's start learning English together!** 🚀
        """
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
        
    async def learn_word(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Изучение нового слова"""
        user_id = update.effective_user.id
        
        if user_id not in self.users_data:
            await self.start(update, context)
            return
            
        user_level = self.users_data[user_id]['level']
        learned_words = self.users_data[user_id]['words_learned']
        
        # Найти неизученные слова текущего уровня
        available_words = [
            word for word, data in self.vocabulary.items()
            if data['level'] == user_level and word not in learned_words
        ]
        
        if not available_words:
            await update.message.reply_text(
                f"🎉 **Congratulations!** You've learned all {user_level} level words!\n\n"
                f"Time to level up! 📈"
            )
            return
            
        # Выбрать случайное слово
        import random
        word = random.choice(available_words)
        translation = self.vocabulary[word]['translation']
        
        # Добавить в изученные
        self.users_data[user_id]['words_learned'].append(word)
        self.users_data[user_id]['score'] += 10
        
        learn_text = f"""
📖 **New Word to Learn!**

🔤 **English:** {word.upper()}
🔄 **Russian:** {translation}
🎚️ **Level:** {user_level}

✅ **Word added to your vocabulary!**
📊 **Total learned:** {len(self.users_data[user_id]['words_learned'])} words
🎯 **Score:** +10 points
        """
        
        await update.message.reply_text(learn_text, parse_mode='Markdown')
        
    async def quiz(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Викторина"""
        user_id = update.effective_user.id
        
        if user_id not in self.users_data:
            await self.start(update, context)
            return
            
        learned_words = self.users_data[user_id]['words_learned']
        
        if len(learned_words) < 2:
            await update.message.reply_text(
                "📚 **Learn at least 2 words first!**\n\n"
                "Use 📖 Learn Word to study new vocabulary."
            )
            return
            
        import random
        word = random.choice(learned_words)
        correct_answer = self.vocabulary[word]['translation']
        
        # Создать варианты ответов
        all_translations = [v['translation'] for v in self.vocabulary.values()]
        wrong_answers = [t for t in all_translations if t != correct_answer]
        
        if len(wrong_answers) >= 3:
            wrong_answers = random.sample(wrong_answers, 3)
        else:
            wrong_answers.extend(['собака', 'дом', 'машина'][:3-len(wrong_answers)])
            
        options = [correct_answer] + wrong_answers[:3]
        random.shuffle(options)
        
        # Сохранить данные викторины
        context.user_data['quiz_word'] = word
        context.user_data['quiz_answer'] = correct_answer
        
        quiz_text = f"""
🎯 **Quiz Time!**

What does **{word.upper()}** mean in Russian?
        """
        
        keyboard = []
        for i, option in enumerate(options):
            keyboard.append([InlineKeyboardButton(
                f"{chr(65+i)} {option}", 
                callback_data=f"quiz_{option}"
            )])
            
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(quiz_text, reply_markup=reply_markup, parse_mode='Markdown')
        
    async def quiz_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка ответов викторины"""
        query = update.callback_query
        await query.answer()
        
        if not query.data.startswith("quiz_"):
            return
            
        selected_answer = query.data[5:]  # Remove "quiz_" prefix
        correct_answer = context.user_data.get('quiz_answer')
        word = context.user_data.get('quiz_word')
        
        user_id = query.from_user.id
        
        if selected_answer == correct_answer:
            self.users_data[user_id]['score'] += 20
            result_text = f"""
✅ **Correct!**

🔤 **{word.upper()}** = **{correct_answer}**

🎉 **Great job!** +20 points
🎯 **Total score:** {self.users_data[user_id]['score']} points
            """
        else:
            result_text = f"""
❌ **Wrong answer**

🔤 **{word.upper()}** = **{correct_answer}**
📝 **You selected:** {selected_answer}

💪 **Don't give up! Try again!**
            """
            
        await query.edit_message_text(result_text, parse_mode='Markdown')
        
    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Статистика пользователя"""
        user_id = update.effective_user.id
        
        if user_id not in self.users_data:
            await self.start(update, context)
            return
            
        user_data = self.users_data[user_id]
        total_words = len(user_data['words_learned'])
        
        stats_text = f"""
📊 **Your Learning Statistics**

👤 **Name:** {user_data['name']}
🎚️ **Level:** {user_data['level']}
📚 **Words learned:** {total_words} words
🎯 **Total score:** {user_data['score']} points

🏆 **Achievements:**
{self.get_achievements(user_data)}

Keep up the great work! 💪
        """
        
        await update.message.reply_text(stats_text, parse_mode='Markdown')
        
    def get_achievements(self, user_data):
        """Получить достижения"""
        achievements = []
        total_words = len(user_data['words_learned'])
        
        if total_words >= 1:
            achievements.append("🥉 First word learned!")
        if total_words >= 5:
            achievements.append("🥈 5 words mastered!")
        if total_words >= 10:
            achievements.append("🥇 Vocabulary expert (10+ words)!")
        if user_data['score'] >= 100:
            achievements.append("🎯 High scorer (100+ points)!")
            
        return "\n".join(achievements) if achievements else "Start learning to earn achievements!"
        
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Помощь"""
        help_text = """
🆘 **Help - SK English Bot**

📚 **Available commands:**
/start - start the bot
/learn - learn a new word
/quiz - take a vocabulary quiz
/stats - view your progress

🎮 **How to use:**
1. Start with /learn to build your vocabulary
2. Use /quiz to test your knowledge
3. Track progress with /stats

💡 **Tips:**
• Learn 5-10 words daily
• Take quizzes regularly
• Focus on one level at a time

**Good luck with your English learning!** 🍀
        """
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        text = update.message.text.lower()
        
        if "learn" in text or "📖" in text:
            await self.learn_word(update, context)
        elif "quiz" in text or "🎯" in text:
            await self.quiz(update, context)
        elif "stats" in text or "📊" in text:
            await self.stats(update, context)
        elif "help" in text or "ℹ️" in text:
            await self.help_command(update, context)
        else:
            await update.message.reply_text(
                "🤔 I don't understand. Use the menu buttons or /help for assistance!"
            )

def main():
    """Главная функция"""
    token = os.getenv('BOT_TOKEN')
    if not token:
        logger.error("BOT_TOKEN not found in environment variables!")
        return
        
    # Создать директорию для логов
    os.makedirs('logs', exist_ok=True)
    
    # Создать бота
    bot = SKEnglishBot()
    
    # Создать приложение
    application = Application.builder().token(token).build()
    
    # Добавить обработчики
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("learn", bot.learn_word))
    application.add_handler(CommandHandler("quiz", bot.quiz))
    application.add_handler(CommandHandler("stats", bot.stats))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CallbackQueryHandler(bot.quiz_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    logger.info("🚀 SK English Bot is starting...")
    
    # Запустить бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()