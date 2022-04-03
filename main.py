import os
import telethon
import re
import asyncio
import requests
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon import events

SESSION = os.environ.get("SESSION")
TOKEN = os.environ.get("TOKEN")
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
LOG_GROUP = int(os.environ.get("LOG_GROUP"))
CHATS = os.environ.get("CHATS")
CHATS = set(int(x) for x in CHATS.split(" "))

user = TelegramClient(StringSession(SESSION), API_ID, API_HASH)
bot = TelegramClient('bot', API_ID, API_HASH)
user.start()
bot.start(bot_token=TOKEN)

def filter(q):
    card_length = [15, 16, 19]
    cvv_length = [3, 4]
    cc = None
    cvv = None
    expm = None
    expy = None
    for x in q:
        if len(x) in card_length: cc = x
        elif len(x) == 2 and int(x) < 13: expm = x
        elif len(x) == 2 and int(x) > 20 and int(x) < 30: expy = x
        elif len(x) == 4 and int(x) > 2020 and int(x) < 2030: expy = x
        elif len(x) in cvv_length: cvv = x
    return cc, expm, expy, cvv
@user.on(events.NewMessage(chats=CHATS))
async def runner(e):
    bin = "None"
    msg = e.message.message
    numlist = re.findall("\d+", msg)
    if numlist == []: return
    cc, expm, expy, cvv = filter(numlist)
    if cc == None or expm == None or expy == None or cvv == None: return
    bin = cc[0:6]
    try:
        bindata = requests.get(f'https://lookup.binlist.net/{bin}').json()
        finaltxt = f'''**CC:** {cc}|{expm}|{expy}|{cvv}
**BIN:** {bin}
Type: {bindata['type']}
Brand: {bindata['brand']}
Country: {bindata['country']['name']} {bindata['country']['emoji']}
Bank: {bindata['bank']['name']}'''
    except: finaltxt = f'''**CC:** {cc}|{expm}|{expy}|{cvv}
**BIN:** {bin}'''
    await bot.send_message(LOG_GROUP, finaltxt)

user.run_until_disconnected()
