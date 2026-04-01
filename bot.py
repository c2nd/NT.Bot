import telebot
import feedparser
import requests
from bs4 import BeautifulSoup
import time
import json
import os
import random
import re

# ==========================
TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL = os.environ.get("CHANNEL_ID")

try:
    CHANNEL = int(CHANNEL)
except:
    pass

bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")

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
def clean_text(text):
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n+', '\n', text)
    return text.strip()

# ==========================
def extract_article(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        paragraphs = []
        seen = set()

        # BBC
        for p in soup.select("div[data-component='text-block'] p"):
            txt = clean_text(p.get_text())
            if len(txt) > 50 and txt not in seen:
                paragraphs.append(txt)
                seen.add(txt)

        # الجزيرة
        if not paragraphs:
            for p in soup.select("article p"):
                txt = clean_text(p.get_text())
                if len(txt) > 50 and txt not in seen:
                    paragraphs.append(txt)
                    seen.add(txt)

        if not paragraphs:
            return None

        article = "\n\n".join(paragraphs)

        # ✂️ قطع ذكي للنهاية
        article = article.strip()
        if "." in article:
            article = article.rsplit(".", 1)[0] + "."

        return article

    except Exception as e:
        print("Extraction error:", e)
        return None

# ==========================
def generate_hook(text):
    words = text.split()
    if len(words) > 30:
        return " ".join(words[:20]) + "..."
    return text[:120] + "..."

# ==========================
def emoji():
    return random.choice(["🚨","🔥","⚡","🌍"])

# ==========================
def format_news(title, hook, body):
    return f"""*{emoji()} {title}*

🧠 {hook}

> {body.replace("\n", "\n> ")}
"""

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
                article = extract_article(entry.link)
                if not article:
                    continue

                hook = generate_hook(article)
                message = format_news(entry.title, hook, article)

                # تقسيم آمن
                chunks = [message[i:i+4000] for i in range(0, len(message), 4000)]

                for c in chunks:
                    bot.send_message(CHANNEL, c)

                print("✅ CLEAN NEWS POSTED")

                posted.append(key)
                if len(posted) > 300:
                    posted = posted[-300:]

                save_posted(posted)
                break

            except Exception as e:
                print("Error:", e)

# ==========================
print("🚀 CLEAN BOT RUNNING...")

while True:
    post_news()
    time.sleep(60)