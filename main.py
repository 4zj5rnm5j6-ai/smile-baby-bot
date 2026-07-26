import os
import telebot
import anthropic
from dotenv import load_dotenv
from inspect import signature

load_dotenv()

print("anthropic version:", getattr(anthropic, "__version__", "unknown"))

bot = telebot.TeleBot(os.getenv("TELEGRAM_TOKEN"))

# Robust Anthropic client initialization to support multiple SDK versions
api_key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_API_KEY".lower())
ClientClass = getattr(anthropic, "Anthropic", None) or getattr(anthropic, "Client", None)

if ClientClass is None:
    # As a last resort, try to import by name used in older/newer SDKs
    try:
        from anthropic import Anthropic as ClientClass  # type: ignore
    except Exception:
        ClientClass = None

if ClientClass is None:
    raise RuntimeError("Не удалось найти класс клиента в библиотеке anthropic")

# Inspect signature and instantiate safely (don't pass unsupported kwargs like 'proxies')
try:
    sig = signature(ClientClass)
    params = sig.parameters
    if "api_key" in params or "api_key" in (p.lower() for p in params):
        client = ClientClass(api_key=api_key) if api_key else ClientClass()
    else:
        client = ClientClass()
except Exception:
    # Fallback: try no-arg constructor
    try:
        client = ClientClass()
    except Exception as e:
        raise RuntimeError(f"Не удалось создать экземпляр клиента Anthropic: {e}")

print("Anthropic client created:", type(client))

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

    try:
        # Old SDK interface
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=1500,
            messages=[{"role": "user", "content": f"Проанализируй:\n{idea}"}]
        )
        # Try to extract text in the old response format
        result = getattr(response, "content", None)
        if result:
            # result might be a list with .text
            try:
                text = result[0].text
            except Exception:
                text = str(result)
        else:
            # Fallback: stringify the whole response
            text = str(response)
    except Exception as e:
        # If old interface fails, show error to logs and re-raise a friendly message
        print("Error calling Anthropic API (old interface):", e)
        raise

    bot.reply_to(message, text[:4000])

@bot.message_handler(func=lambda m: True)
def default(m):
    bot.reply_to(m, "Используй /analyze")

bot.infinity_polling()
