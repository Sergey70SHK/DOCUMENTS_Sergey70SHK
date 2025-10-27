#!/usr/bin/env python3
"""
Простая тестовая версия SK English Bot
"""

import asyncio
import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleBot:
    def __init__(self, token):
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
        
    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(MessageHandler(filters.TEXT, self.echo))
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [KeyboardButton("📖 Learn"), KeyboardButton("🎯 Quiz")],
            [KeyboardButton("📊 Stats")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(
            "🌟 Welcome to SK English Bot!\n\n"
            "I'm working and ready to help you learn English! 📚\n\n"
            "Use /start to see this menu again.",
            reply_markup=reply_markup
        )
        
    async def echo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = update.message.text.lower()
        
        if "learn" in text or "📖" in text:
            await update.message.reply_text(
                "📖 Learning feature!\n\n"
                "Here you would learn new English words.\n"
                "Bot is working correctly! ✅"
            )
        elif "quiz" in text or "🎯" in text:
            await update.message.reply_text(
                "🎯 Quiz feature!\n\n"
                "Here you would take English quizzes.\n"
                "Bot is working correctly! ✅"
            )
        elif "stats" in text or "📊" in text:
            await update.message.reply_text(
                "📊 Stats feature!\n\n"
                "Here you would see your progress.\n"
                "Bot is working correctly! ✅"
            )
        else:
            await update.message.reply_text(
                f"You said: {update.message.text}\n\n"
                "✅ Bot is working! Use the menu buttons or /start"
            )
    
    async def run(self):
        logger.info("🚀 Starting SK English Bot...")
        await self.application.run_polling(timeout=30)

async def main():
    token = os.getenv('BOT_TOKEN')
    if not token:
        logger.error("BOT_TOKEN not found!")
        return
        
    bot = SimpleBot(token)
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())