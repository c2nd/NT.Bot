import telebot
import feedparser
import schedule
import time
import os

# ==========================
# إعدادات البوت
# ==========================
TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL = os.environ.get("CHANNEL_ID")  # @darkthu9hts

bot = telebot.TeleBot(TOKEN)

# ==========================
# مصادر الأخبار (RSS)
# ==========================
RSS_FEEDS = [
    "http://feeds.bbci.co.uk/news/rss.xml",
    "http://rss.cnn.com/rss/edition.rss",
    "https://www.aljazeera.com/xml/rss/all.xml"
]

# ==========================
# تخزين الأخبار المنشورة
# ==========================
posted_links = []

# ==========================
# جلب الأخبار من RSS
# ==========================
def get_news():
    news_items = []

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:5]:  # آخر 5 أخبار من كل مصدر
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
    news_list = get_news()

    for news in news_list:
        if news["link"] not in posted_links:
            try:
                message = f"""🌍 {news['title']}

🔗 اقرأ المزيد:
{news['link']}

📰 @darkthu9hts"""

                bot.send_message(CHANNEL, message)

                print("✅ News posted")

                posted_links.append(news["link"])

                # الاحتفاظ بآخر 50 خبر
                if len(posted_links) > 50:
                    posted_links.pop(0)

                break  # ينشر خبر واحد فقط كل مرة

            except Exception as e:
                print(f"❌ Error: {e}")

# ==========================
# الجدولة (كل 3 دقائق 🔥)
# ==========================
schedule.every(3).minutes.do(post_news)

# ==========================
# التشغيل
# ==========================
print("🚀 Ultra News Bot is running...")

post_news()  # نشر فوري

while True:
    schedule.run_pending()
    time.sleep(10)