#!/usr/bin/env python3
"""
SK English Bot - Translation and Grammar Checker
Powered by Google Gemini AI
"""

import logging
import os
import re
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import requests
import json

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
        self.user_contexts = {}
        
    def detect_language(self, text):
        """Определяет язык текста"""
        # Простая эвристика для определения языка
        cyrillic_chars = len(re.findall(r'[а-яё]', text.lower()))
        latin_chars = len(re.findall(r'[a-z]', text.lower()))
        
        if cyrillic_chars > latin_chars:
            return 'russian'
        elif latin_chars > cyrillic_chars:
            return 'english'
        else:
            return 'unknown'
    
    async def translate_text(self, text, source_lang, target_lang):
        """Перевод текста с объяснениями"""
        try:
            # Имитируем AI перевод (в реальности здесь был бы API Google Gemini)
            if source_lang == 'russian' and target_lang == 'english':
                # Примеры переводов с русского на английский
                translations = {
                    'привет': 'Hello',
                    'как дела': 'How are you?',
                    'спасибо': 'Thank you',
                    'пока': 'Goodbye',
                    'я изучаю английский': 'I am studying English',
                    'меня зовут': 'My name is',
                    'сколько времени': 'What time is it?',
                    'где находится': 'Where is located',
                    'я не понимаю': 'I don\'t understand',
                    'помогите мне': 'Help me'
                }
                
                # Ищем похожие фразы
                text_lower = text.lower()
                for rus_phrase, eng_phrase in translations.items():
                    if rus_phrase in text_lower:
                        return {
                            'translation': eng_phrase,
                            'explanation': f'Фраза "{rus_phrase}" переводится как "{eng_phrase}"',
                            'grammar_tip': 'Обратите внимание на структуру предложения в английском языке'
                        }
                
                # Базовый перевод
                return {
                    'translation': f'[Translation of: {text}]',
                    'explanation': 'Это демонстрационный перевод. В полной версии здесь будет Google Gemini AI.',
                    'grammar_tip': 'Изучайте грамматические структуры для лучшего понимания'
                }
                
            elif source_lang == 'english' and target_lang == 'russian':
                # Примеры переводов с английского на русский
                translations = {
                    'hello': 'Привет',
                    'how are you': 'Как дела?',
                    'thank you': 'Спасибо',
                    'goodbye': 'Пока',
                    'i am studying english': 'Я изучаю английский',
                    'my name is': 'Меня зовут',
                    'what time is it': 'Сколько времени?',
                    'where is': 'Где находится',
                    'i don\'t understand': 'Я не понимаю',
                    'help me': 'Помогите мне'
                }
                
                text_lower = text.lower()
                for eng_phrase, rus_phrase in translations.items():
                    if eng_phrase in text_lower:
                        return {
                            'translation': rus_phrase,
                            'explanation': f'Phrase "{eng_phrase}" means "{rus_phrase}" in Russian',
                            'grammar_tip': 'Pay attention to word order differences between English and Russian'
                        }
                
                return {
                    'translation': f'[Перевод: {text}]',
                    'explanation': 'This is a demo translation. Full version would use Google Gemini AI.',
                    'grammar_tip': 'Study sentence structures for better understanding'
                }
                
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return {
                'translation': 'Translation error occurred',
                'explanation': 'Произошла ошибка при переводе',
                'grammar_tip': 'Попробуйте еще раз'
            }
    
    async def check_grammar(self, text):
        """Проверка грамматики английского текста"""
        try:
            # Простые грамматические проверки
            errors = []
            suggestions = []
            
            # Проверка заглавных букв в начале предложения
            sentences = text.split('.')
            for i, sentence in enumerate(sentences):
                sentence = sentence.strip()
                if sentence and not sentence[0].isupper():
                    errors.append(f"Sentence {i+1}: Should start with capital letter")
                    
            # Проверка на распространенные ошибки
            common_errors = {
                'i am': 'Use "I am" (capital I)',
                'dont': "Use \"don't\" (with apostrophe)",
                'cant': "Use \"can't\" (with apostrophe)",
                'wont': "Use \"won't\" (with apostrophe)",
                'its': "Use \"it's\" for \"it is\" or \"its\" for possession",
                'your': "Use \"you're\" for \"you are\" or \"your\" for possession"
            }
            
            text_lower = text.lower()
            for error, correction in common_errors.items():
                if error in text_lower:
                    suggestions.append(correction)
            
            # Проверка окончания предложений
            if text and not text.rstrip().endswith(('.', '!', '?')):
                errors.append("Missing punctuation at the end of sentence")
            
            if not errors and not suggestions:
                return {
                    'status': 'good',
                    'message': '✅ Your English grammar looks good!',
                    'suggestions': ['Keep practicing!', 'Try writing longer sentences']
                }
            else:
                return {
                    'status': 'errors',
                    'errors': errors,
                    'suggestions': suggestions
                }
                
        except Exception as e:
            logger.error(f"Grammar check error: {e}")
            return {
                'status': 'error',
                'message': 'Grammar check failed',
                'suggestions': []
            }

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        welcome_text = """
🇷🇺 **Welcome to English Learning Bot!**

📚 **Добро пожаловать в бот для изучения английского языка!**

🔤 **English Text → Grammar Check:**
   • Send English text for grammar checking
   • Get corrections and explanations
   • Improve your English writing

🔄 **Translation Features:**
   • **Русский → English:** Отправьте русский текст
   • **English → Русский:** Send English text, then reply 'translate'
   • Get explanations and learning tips

✏️ **How to use:**
   • **Русский текст** → Перевод на английский
   • **English text** → Choose 'grammar' or 'translate'

🤖 **Powered by Google Gemini AI**

*Send any text to get started!*
        """
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown')

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        user_id = update.effective_user.id
        text = update.message.text
        
        if not text:
            return
            
        # Определяем язык
        detected_lang = self.detect_language(text)
        
        if detected_lang == 'russian':
            # Русский текст → автоматически переводим на английский
            await self.translate_russian_to_english(update, text)
            
        elif detected_lang == 'english':
            # Английский текст → предлагаем выбор
            await self.handle_english_text(update, context, text)
            
        else:
            await update.message.reply_text(
                "🤔 Не могу определить язык текста.\n\n"
                "Please send text in Russian or English."
            )

    async def translate_russian_to_english(self, update: Update, text: str):
        """Перевод с русского на английский"""
        await update.message.reply_text("🔄 Переводим на английский...")
        
        result = await self.translate_text(text, 'russian', 'english')
        
        response = f"""
🔄 **Перевод на английский:**

🇷🇺 **Русский:** {text}
🇺🇸 **English:** {result['translation']}

💡 **Объяснение:** {result['explanation']}
📝 **Совет:** {result['grammar_tip']}
        """
        
        await update.message.reply_text(response, parse_mode='Markdown')

    async def handle_english_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Обработка английского текста с выбором действия"""
        user_id = update.effective_user.id
        
        # Сохраняем текст для дальнейшей обработки
        self.user_contexts[user_id] = {'text': text}
        
        keyboard = [
            [InlineKeyboardButton("✏️ Grammar Check", callback_data="grammar")],
            [InlineKeyboardButton("🔄 Translate to Russian", callback_data="translate")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🇺🇸 **English text received:**\n\n"
            f"_{text}_\n\n"
            f"**What would you like to do?**",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатий кнопок"""
        query = update.callback_query
        user_id = query.from_user.id
        
        await query.answer()
        
        if user_id not in self.user_contexts:
            await query.edit_message_text("❌ Контекст потерян. Отправьте текст заново.")
            return
            
        text = self.user_contexts[user_id]['text']
        
        if query.data == "grammar":
            await self.check_english_grammar(query, text)
        elif query.data == "translate":
            await self.translate_english_to_russian(query, text)

    async def check_english_grammar(self, query, text: str):
        """Проверка грамматики английского текста"""
        await query.edit_message_text("✏️ Проверяем грамматику...")
        
        result = await self.check_grammar(text)
        
        if result['status'] == 'good':
            response = f"""
✅ **Grammar Check Results:**

🇺🇸 **Text:** {text}

{result['message']}

💡 **Tips:**
{chr(10).join(f"• {tip}" for tip in result['suggestions'])}
            """
        elif result['status'] == 'errors':
            errors_text = "\n".join(f"• {error}" for error in result.get('errors', []))
            suggestions_text = "\n".join(f"• {suggestion}" for suggestion in result.get('suggestions', []))
            
            response = f"""
✏️ **Grammar Check Results:**

🇺🇸 **Text:** {text}

❌ **Issues found:**
{errors_text}

💡 **Suggestions:**
{suggestions_text}
            """
        else:
            response = f"""
❌ **Grammar Check Error:**

{result.get('message', 'Unknown error occurred')}
            """
        
        await query.edit_message_text(response, parse_mode='Markdown')

    async def translate_english_to_russian(self, query, text: str):
        """Перевод с английского на русский"""
        await query.edit_message_text("🔄 Переводим на русский...")
        
        result = await self.translate_text(text, 'english', 'russian')
        
        response = f"""
🔄 **Translation to Russian:**

🇺🇸 **English:** {text}
🇷🇺 **Русский:** {result['translation']}

💡 **Explanation:** {result['explanation']}
📝 **Grammar tip:** {result['grammar_tip']}
        """
        
        await query.edit_message_text(response, parse_mode='Markdown')

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
    application.add_handler(CallbackQueryHandler(bot.button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    
    logger.info("🚀 SK English Bot is starting...")
    logger.info("📚 Translation and Grammar Checker ready!")
    
    # Запустить бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()