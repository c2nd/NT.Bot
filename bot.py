import telebot
import feedparser
import requests
import json
import os
import random

# ==========================
TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL = os.environ.get("CHANNEL_ID")  # يمكن أن يكون @channel_name أو Chat ID
bot = telebot.TeleBot(TOKEN)

# ==========================
RSS_FEEDS = [
    "https://www.aljazeera.net/aljazeera/ar/feeds/all.xml",
    "https://feeds.bbci.co.uk/arabic/rss.xml"
]

DATA_FILE = "posted.json"

# ==========================
def load_posted():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_posted(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

posted = load_posted()

# ==========================
def add_emoji():
    return random.choice(["🌍","📰","🔥","⚡","🧠"])

# ==========================
def generate_summary(text):
    """
    توليد وصف جذاب باستخدام AI مجاني
    يمكنك لاحقًا استخدام أي API مجاني للذكاء الاصطناعي
    الآن سنكتفي بتوليد نص قصير عشوائي للتجربة
    """
    words = text.split()[:20]  # أخذ أول 20 كلمة فقط كموجز
    return " ".join(words) + "…"

# ==========================
def fetch_news():
    global posted
    for feed in RSS_FEEDS:
        d = feedparser.parse(feed)
        for entry in d.entries[:5]:  # أول 5 أخبار فقط للتجربة
            key = entry.title.lower()
            if key in posted:
                continue
            # نص جذاب
            message = f"{add_emoji()} {entry.title}\n\n{generate_summary(entry.get('summary', entry.title))}"
            # نشر مع صورة إن وجدت
            if 'media_content' in entry:
                img_url = entry.media_content[0]['url']
                try:
                    bot.send_photo(CHANNEL, img_url, caption=message)
                    print("🖼️ خبر مع صورة نشر:", entry.title)
                except:
                    bot.send_message(CHANNEL, message)
                    print("📄 خبر بدون صورة نشر:", entry.title)
            else:
                bot.send_message(CHANNEL, message)
                print("📄 خبر بدون صورة نشر:", entry.title)
            # تخزين لمنع التكرار
            posted.append(key)
            if len(posted) > 200:
                posted = posted[-200:]
            save_posted(posted)

# ==========================
print("🚀 Arabic News Bot Running…")

# تشغيل مباشر كل دقيقة للتحقق من الأخبار الجديدة
import time
while True:
    fetch_news()
    time.sleep(60)