import telebot
import feedparser
import schedule
import time
import os
import json

# ==========================
# إعدادات
# ==========================
TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL = os.environ.get("CHANNEL_ID")

bot = telebot.TeleBot(TOKEN)

# ==========================
# مصادر RSS
# ==========================
RSS_FEEDS = [
    "http://feeds.bbci.co.uk/news/rss.xml",
    "http://rss.cnn.com/rss/edition.rss",
    "https://www.aljazeera.com/xml/rss/all.xml"
]

# ==========================
# ملف التخزين
# ==========================
DATA_FILE = "posted_news.json"

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

posted_news = load_data()

# ==========================
# تنظيف العنوان
# ==========================
def clean_title(title):
    return title.lower().strip()

# ==========================
# جلب الأخبار
# ==========================
def get_news():
    news_items = []

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:5]:
            title = entry.title
            link = entry.link

            news_items.append({
                "title": title,
                "link": link
            })

    return news_items

# ==========================
# نشر خبر بدون تكرار
# ==========================
def post_news():
    global posted_news

    news_list = get_news()

    for news in news_list:
        clean = clean_title(news["title"])

        if clean not in posted_news:
            try:
                message = f"""🌍 {news['title']}

🔗 اقرأ المزيد:
{news['link']}

📰 @darkthu9hts"""

                bot.send_message(CHANNEL, message)

                print("✅ News posted")

                posted_news.append(clean)

                # حفظ فقط آخر 100 خبر
                if len(posted_news) > 100:
                    posted_news = posted_news[-100:]

                save_data(posted_news)

                break

            except Exception as e:
                print(f"❌ Error: {e}")

# ==========================
# الجدولة
# ==========================
schedule.every(3).minutes.do(post_news)

# ==========================
# التشغيل
# ==========================
print("🚀 Ultra News Bot is running...")

post_news()

while True:
    schedule.run_pending()
    time.sleep(10)