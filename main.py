import os, telebot
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))
client = Anthropic()

print("🤖 БОТ ЗАПУЩЕН")

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "🌟 Привет! Напиши идею и ответь /analyze")

@bot.message_handler(commands=['analyze'])
def analyze(message):
    if not message.reply_to_message:
        bot.reply_to(message, "❌ Ответь на идею и напиши /analyze")
        return
    
    idea = message.reply_to_message.text
    
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=1500,
        messages=[{"role": "user", "content": f"Проанализируй:\n{idea}"}]
    )
    result = response.content[0].text
    bot.reply_to(message, result[:4000])

@bot.message_handler(func=lambda m: True)
def default(m):
    bot.reply_to(m, "Используй /analyze")

bot.infinity_polling()
