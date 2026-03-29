import telebot
import requests
import random
from bs4 import BeautifulSoup
import schedule
import time

# ==========================
# إعدادات البوت
# ==========================
import os

TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL = int(os.environ.get("CHANNEL_ID"))

bot = telebot.TeleBot(TOKEN)

# ==========================
# جلب اقتباس إنجليزي من Quotable API
# ==========================
def get_english_quote():
    try:
        response = requests.get("https://api.quotable.io/random?tags=dark,philosophy")
        data = response.json()
        text = data.get("content", "")
        author = data.get("author", "")
        return f"{text} — {author}"
    except:
        return "Dark thoughts never fade… 🖤"

# ==========================
# جلب اقتباس عربي من موقع حكمة
# ==========================
def get_arabic_quotes_from_hekmah():
    try:
        url = "https://hekmah.online/"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        quotes = [q.text.strip() for q in soup.select(".quote-text") if q.text.strip()]
        return quotes
    except:
        return []

# ==========================
# جلب اقتباس عربي من موقع اقتباسات أخرى
# ==========================
def get_arabic_quotes_from_ekhtaboot():
    try:
        url = "https://www.ekhtaboot.com/ar/quotes"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, "html.parser")
        quotes = [q.text.strip() for q in soup.select(".quote") if q.text.strip()]
        return quotes
    except:
        return []

# ==========================
# اختيار اقتباس عربي عشوائي
# ==========================
def get_arabic_quote():
    quotes = get_arabic_quotes_from_hekmah() + get_arabic_quotes_from_ekhtaboot()
    if quotes:
        return random.choice(quotes)
    else:
        return "الأفكار الداكنة تعكس العمق الداخلي… 🌑"

# ==========================
# إضافة إيموجيات عشوائية
# ==========================
def add_emoji(text):
    emojis = ["🖤","🌑","💀","🔥","🌫️","🕷️"]
    return random.choice(emojis) + " " + text

# ==========================
# نشر الاقتباسات على القناة
# ==========================
def post_quotes():
    eng = get_english_quote()
    ara = get_arabic_quote()
    try:
        bot.send_message(CHANNEL, add_emoji(eng))
        bot.send_message(CHANNEL, add_emoji(ara))
        print("تم النشر على القناة!")
    except Exception as e:
        print(f"خطأ عند النشر: {e}")

# ==========================
# جدولة النشر
# ==========================
schedule.every(1).hours.do(post_quotes)  # كل ساعة
# يمكن تعديل الجدولة:
# schedule.every(2).hours.do(post_quotes)  # كل ساعتين
# schedule.every().day.at("10:00").do(post_quotes)  # يوميًا الساعة 10 صباحًا

# ==========================
# تشغيل البوت
# ==========================
print("بوت Dark Thoughts يعمل الآن…")
while True:
    schedule.run_pending()
    time.sleep(10)
