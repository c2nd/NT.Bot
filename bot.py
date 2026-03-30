import telebot
import feedparser
import schedule
import time
import os
import json
import requests
import random

# ==========================
# إعدادات
# ==========================
TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL = os.environ.get("CHANNEL_ID")
TRANSLATE_URL = os.environ.get("TRANSLATE_URL")
SHORT_API = os.environ.get("SHORT_API")  # shrinkme.io أو exe.io API

bot = telebot.TeleBot(TOKEN)

# ==========================
# RSS الأخبار
# ==========================
RSS_FEEDS = [
    "http://feeds.bbci.co.uk/news/rss.xml",
    "http://rss.cnn.com/rss/edition.rss",
    "https://www.aljazeera.com/xml/rss/all.xml"
]

# ==========================
# التخزين لتجنب التكرار
# ==========================
DATA_FILE = "posted.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

posted = load_data()

# ==========================
# ملخص الخبر (Hook AI)
# ==========================
def summarize(text):
    # استخدم API لترجمة + تلخيص، أو نسخة بسيطة الآن:
    # النص الأصلي → 120 حرف تقريبًا
    return text[:120] + "..." if len(text) > 120 else text

# ==========================
# ترجمة إلى العربية
# ==========================
def translate(text):
    try:
        res = requests.post(TRANSLATE_URL, json={
            "q": text,
            "source": "en",
            "target": "ar"
        })
        return res.json()["translatedText"]
    except:
        return text

# ==========================
# اختصار الرابط فقط
# ==========================
def shorten(url):
    try:
        api_url = f"https://shrinkme.io/api?api={SHORT_API}&url={url}"
        res = requests.get(api_url)
        return res.json()["shortenedUrl"]
    except:
        return url

# ==========================
# جلب الأخبار
# ==========================
def get_news():
    news = []
    for feed in RSS_FEEDS:
        parsed = feedparser.parse(feed)
        for entry in parsed.entries[:5]:
            news.append({
                "title": entry.title,
                "link": entry.link
            })
    return news

# ==========================
# نشر الأخبار
# ==========================
def post_news():
    global posted

    news_list = get_news()

    for item in news_list:
        key = item["title"].lower()

        if key not in posted:
            try:
                short_text = summarize(item["title"])
                ar_text = translate(short_text)
                short_link = shorten(item["link"])

                message = f"{ar_text}\n{short_link}"

                bot.send_message(CHANNEL, message)
                print("✅ News posted")

                posted.append(key)
                if len(posted) > 200:
                    posted = posted[-200:]

                save_data(posted)
                break

            except Exception as e:
                print(e)

# ==========================
# الجدولة
# ==========================
schedule.every(3).minutes.do(post_news)

print("🚀 Smart News Bot Running...")

post_news()

while True:
    schedule.run_pending()
    time.sleep(10)