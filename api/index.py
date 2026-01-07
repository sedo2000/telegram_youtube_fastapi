import os
import telebot
import requests
from fastapi import FastAPI, Request

BOT_TOKEN = os.getenv("BOT_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not BOT_TOKEN or not YOUTUBE_API_KEY:
    raise RuntimeError("Missing environment variables")

bot = telebot.TeleBot(BOT_TOKEN)
app = FastAPI()

@bot.message_handler(commands=["start"])
def start(m):
    bot.reply_to(m, "🎬 أرسل اسم الفيديو للبحث في يوتيوب")

@bot.message_handler(func=lambda m: True)
def search(m):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": m.text,
        "key": YOUTUBE_API_KEY,
        "maxResults": 1,
        "type": "video"
    }
    r = requests.get(url, params=params).json()
    if not r.get("items"):
        bot.reply_to(m, "❌ لا توجد نتائج")
        return
    vid = r["items"][0]["id"]["videoId"]
    bot.reply_to(m, f"https://youtu.be/{vid}")

# اختبار السيرفر
@app.get("/")
async def health():
    return {"status": "BOT IS ALIVE"}

# Webhook من Telegram
@app.post("/")
async def webhook(req: Request):
    data = await req.json()
    update = telebot.types.Update.de_json(data)
    bot.process_new_updates([update])
    return {"ok": True}
