import telebot
import feedparser
import requests
from bs4 import BeautifulSoup
import time
import json
import os
import random

# ==========================
TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL = os.environ.get("CHANNEL_ID")

bot = telebot.TeleBot(TOKEN)

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
def emoji():
    return random.choice(["🚨","🔥","⚡","🌍"])

# ==========================
# استخراج الصورة
def get_image(entry):
    if "media_content" in entry:
        return entry.media_content[0]["url"]
    if "media_thumbnail" in entry:
        return entry.media_thumbnail[0]["url"]
    return None

# ==========================
# استخراج الخبر الكامل
def get_full_article(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        paragraphs = []

        # BBC
        for p in soup.select("div[data-component='text-block'] p"):
            paragraphs.append(p.get_text())

        # fallback الجزيرة
        if not paragraphs:
            for p in soup.select("p"):
                text = p.get_text()
                if len(text) > 50:
                    paragraphs.append(text)

        return "\n\n".join(paragraphs[:12])

    except:
        return None

# ==========================
# Hook احترافي (CNN Style)
def generate_hook(text):
    words = text.split()

    if len(words) > 25:
        return " ".join(words[:20]) + "..."
    else:
        return text[:120] + "..."

# ==========================
def post_news():
    global posted

    for feed in RSS_FEEDS:
        data = feedparser.parse(feed)

        for entry in data.entries[:5]:
            key = entry.title.lower()

            if key in posted:
                continue

            try:
                full_text = get_full_article(entry.link)
                if not full_text:
                    continue

                hook = generate_hook(full_text)
                img = get_image(entry)

                # تنسيق احترافي
                message = f"""
{emoji()} {entry.title}

🧠 {hook}

{full_text}
"""

                # صورة + نص
                if img:
                    bot.send_photo(CHANNEL, img, caption=message[:1000])
                else:
                    bot.send_message(CHANNEL, message[:4000])

                print("✅ CNN Style News Posted")

                posted.append(key)
                if len(posted) > 300:
                    posted = posted[-300:]

                save_posted(posted)
                break

            except Exception as e:
                print("Error:", e)

# ==========================
print("🚀 CNN Arabic Bot Running...")

while True:
    post_news()
    time.sleep(60)