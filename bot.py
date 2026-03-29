import telebot
import requests
import random
from bs4 import BeautifulSoup
import schedule
import time
import os

# ==========================
# إعدادات البوت
# ==========================
TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL = os.environ.get("CHANNEL_ID")  # لازم يكون @darkthu9hts

bot = telebot.TeleBot(TOKEN)

# ==========================
# جلب اقتباس إنجليزي
# ==========================
def get_english_quote():
    try:
        response = requests.get("https://api.quotable.io/random?tags=dark,philosophy")
        data = response.json()
        text = data.get("content", "")
        author = data.get("author", "")
        return f"{text}\n— {author}"
    except:
        return "Dark thoughts never fade… 🖤"

# ==========================
# جلب اقتباسات عربية
# ==========================
def get_arabic_quotes():
    quotes = []

    # من موقع حكمة
    try:
        res = requests.get("https://hekmah.online/")
        soup = BeautifulSoup(res.text, "html.parser")
        quotes += [q.text.strip() for q in soup.select(".quote-text") if q.text.strip()]
    except:
        pass

    # من موقع آخر
    try:
        res = requests.get("https://www.ekhtaboot.com/ar/quotes")
        soup = BeautifulSoup(res.text, "html.parser")
        quotes += [q.text.strip() for q in soup.select(".quote") if q.text.strip()]
    except:
        pass

    if quotes:
        return random.choice(quotes)
    else:
        return "الأفكار الداكنة تعكس العمق الداخلي… 🌑"

# ==========================
# إضافة إيموجيات
# ==========================
def add_emoji(text):
    emojis = ["🖤","🌑","💀","🔥","🌫️","🕷️"]
    return random.choice(emojis) + " " + text

# ==========================
# تنسيق المنشور
# ==========================
def format_post():
    eng = get_english_quote()
    ara = get_arabic_quotes()

    post = f"""
🖤 Dark Thoughts

{add_emoji(eng)}

{add_emoji(ara)}

🌑 @darkthu9hts
"""
    return post

# ==========================
# النشر
# ==========================
def post_quotes():
    try:
        bot.send_message(CHANNEL, format_post())
        print("✅ تم النشر في القناة!")
    except Exception as e:
        print(f"❌ خطأ: {e}")

# ==========================
# الجدولة (كل 30 دقيقة)
# ==========================
schedule.every(30).minutes.do(post_quotes)

# ==========================
# التشغيل
# ==========================
print("🚀 Bot is running...")

post_quotes()  # نشر فوري عند التشغيل

while True:
    schedule.run_pending()
    time.sleep(10)