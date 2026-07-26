import os, telebot, dropbox
from anthropic import Anthropic
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))
client = Anthropic()
dbx = dropbox.Dropbox(os.getenv("DROPBOX_TOKEN"))

print("🤖 БОТ ЗАПУЩЕН")

@bot.message_handler(commands=['start'])
def start(m):
    print(f"📨 /start от {m.from_user.username}")
    bot.reply_to(m, "🌟 Привет! Напиши идею и ответь /analyze")

@bot.message_handler(commands=['analyze'])
def analyze(message):
    print(f"🔍 /analyze от {message.from_user.username}")
    
    if not message.reply_to_message:
        print("❌ Нет reply_to_message")
        bot.reply_to(message, "❌ Ответь на сообщение с идеей")
        return
    
    idea = message.reply_to_message.text
    print(f"📝 Идея: {idea[:50]}...")
    
    status = bot.send_message(message.chat.id, "⏳ Анализирую...")
    
    try:
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=1500,
            messages=[{"role": "user", "content": f"Проанализируй идею:\n{idea}"}]
        )
        result = response.content[0].text
        print(f"✅ Ответ получен: {len(result)} символов")
        
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dbx.files_upload(result.encode(), f"/Smile_Baby_Bot/Analysis/idea_{ts}.txt", mode=dropbox.files.WriteMode('overwrite'))
        print("💾 Сохранено в Dropbox")
        
        bot.edit_message_text(chat_id=message.chat.id, message_id=status.message_id, text=result[:4000])
        bot.send_message(message.chat.id, "✅ Готово!")
        
    except Exception as e:
        print(f"⚠️ ОШИБКА: {e}")
        bot.reply_to(message, f"❌ Ошибка: {str(e)[:100]}")

@bot.message_handler(func=lambda m: True)
def default(m):
    bot.reply_to(m, "Используй /analyze")

print("🔄 Бот готов к сообщениям...")
bot.infinity_polling()
