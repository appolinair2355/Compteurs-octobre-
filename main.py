import os
import asyncio
import json
import re
import time
from datetime import datetime
from telethon import TelegramClient, events
from dotenv import load_dotenv
from predictor import CardPredictor
from yaml_manager import init_database
from card_counter import CardCounter
from aiohttp import web

load_dotenv()

# ---------- CONFIG ----------
API_ID   = int(os.getenv("API_ID") or 0)
API_HASH = os.getenv("API_HASH") or ""
BOT_TOKEN= os.getenv("BOT_TOKEN") or ""
ADMIN_ID = int(os.getenv("ADMIN_ID") or 0)
PORT     = int(os.getenv("PORT", 10000))

# ---------- GLOBALS ----------
detected_stat_channel  = None
detected_display_channel = int(os.getenv("DISPLAY_CHANNEL") or 0)
CONFIG_FILE   = "bot_config.json"
INTERVAL_FILE = "interval.json"
AUTO_BILAN_MIN = 30
AUTO_TASK      = None

pending_messages = {}          # {message_id: message_text}
database = init_database()
predictor    = CardPredictor()
card_counter = CardCounter()

# Le client sera créé plus tard
client: TelegramClient | None = None

# ---------- CONFIG TOOLS ----------
def load_config():
    global detected_stat_channel, detected_display_channel
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            c = json.load(f)
            detected_stat_channel  = c.get("stat_channel")
            detected_display_channel = c.get("display_channel", detected_display_channel)

def save_config():
    with open(CONFIG_FILE, "w") as f:
        json.dump({"stat_channel": detected_stat_channel, "display_channel": detected_display_channel}, f)

def load_interval():
    global AUTO_BILAN_MIN
    if os.path.exists(INTERVAL_FILE):
        with open(INTERVAL_FILE) as f:
            AUTO_BILAN_MIN = max(1, min(int(json.load(f)), 120))

def save_interval(mins: int):
    with open(INTERVAL_FILE, "w") as f:
        json.dump(mins, f)

# ---------- AUTO-BILAN ----------
async def auto_bilan_loop():
    while True:
        await asyncio.sleep(AUTO_BILAN_MIN * 60)
        if detected_display_channel:
            msg = card_counter.report_and_reset()
            await client.send_message(detected_display_channel, msg)

def restart_auto_bilan():
    global AUTO_TASK
    if AUTO_TASK: AUTO_TASK.cancel()
    AUTO_TASK = asyncio.create_task(auto_bilan_loop())

# ---------- COMMANDS ----------
@client.on(events.NewMessage(pattern="/start"))
async def start(e):
    await e.respond("🎯 Bot **Compteur de cartes** prêt !\nDéveloppé par Sossou Kouamé Appolinaire")

@client.on(events.NewMessage(pattern="/status"))
async def status(e):
    if e.sender_id != ADMIN_ID: return
    load_config()
    await e.respond(f"Stat canal : {detected_stat_channel}\nAffichage canal : {detected_display_channel}\nIntervalle : {AUTO_BILAN_MIN} min")

@client.on(events.NewMessage(pattern=r"/set_stat (-?\d+)"))
async def set_stat(e):
    if e.sender_id != ADMIN_ID or e.is_group: return
    global detected_stat_channel
    detected_stat_channel = int(e.pattern_match.group(1))
    save_config()
    await e.respond("✅ Canal statistiques enregistré.")

@client.on(events.NewMessage(pattern=r"/set_display (-?\d+)"))
async def set_display(e):
    if e.sender_id != ADMIN_ID or e.is_group: return
    global detected_display_channel
    channel_id = int(e.pattern_match.group(1))
    if channel_id > 0 and channel_id > 1000000000:
        channel_id = -1000000000000 - channel_id
    detected_display_channel = channel_id
    save_config()
    await e.respond(f"✅ Canal d'affichage enregistré : {channel_id}")

@client.on(events.NewMessage(pattern=r"/intervalle"))
async def set_interval(e):
    if e.sender_id != ADMIN_ID: return
    try:
        mins = int(e.message.message.split()[1])
        mins = max(1, min(mins, 120))
    except (ValueError, IndexError):
        await e.respond("Usage : `/intervalle 5` (1-120 min)")
        return
    save_interval(mins)
    global AUTO_BILAN_MIN
    AUTO_BILAN_MIN = mins
    restart_auto_bilan()
    await e.respond(f"✅ Bilan automatique toutes les {mins} min")

@client.on(events.NewMessage(pattern="/bilan"))
async def bilan(e):
    if e.sender_id != ADMIN_ID: return
    msg = card_counter.report_and_reset()
    await e.respond(msg)

@client.on(events.NewMessage(pattern="/reset"))
async def reset(e):
    if e.sender_id != ADMIN_ID: return
    card_counter.reset()
    await e.respond("✅ Compteur remis à zéro.")

@client.on(events.NewMessage(pattern="/deploy"))
async def deploy(e):
    if e.sender_id != ADMIN_ID: return
    import zipfile
    zip_name = "render_deploy.zip"
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as z:
        for f in ["main.py", "predictor.py", "yaml_manager.py", "card_counter.py", "requirements.txt", ".gitignore"]:
            if os.path.exists(f): z.write(f)
    await e.respond("📦 Package Render créé !")
    await client.send_file(e.chat_id, zip_name, caption="🚀 Prêt pour Render")

@client.on(events.NewMessage(pattern="/dep"))
async def dep_render(e):
    if e.sender_id != ADMIN_ID: return
    import zipfile
    zip_name = "de2000.zip"
    try:
        with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as z:
            main_render = open("main.py", encoding="utf-8").read()
            z.writestr("main.py", main_render)
            for f in ["predictor.py", "yaml_manager.py", "card_counter.py", "scheduler.py"]:
                if os.path.exists(f): z.write(f)
            for f in ["requirements.txt", "runtime.txt", ".gitignore"]:
                if os.path.exists(f): z.write(f)
            z.writestr("render.yaml", open("render.yaml").read())
            z.writestr(".env.example", """API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
ADMIN_ID=your_admin_id
DISPLAY_CHANNEL=0
PORT=10000
""")
            z.writestr("README_RENDER.md", open("README_RENDER.md").read())
        await e.respond("📦 Package de2000.zip créé !")
        await client.send_file(e.chat_id, zip_name, caption="🚀 Package de2000.zip prêt pour Render.com")
        if os.path.exists(zip_name): os.remove(zip_name)
    except Exception as ex:
        await e.respond(f"❌ Erreur création package : {ex}")

# ---------- MESSAGE HANDLER ----------
@client.on(events.NewMessage())
async def handle_new(e):
    if e.chat_id != detected_stat_channel: return
    txt = e.message.message or ""
    if "⏰" in txt or "🕐" in txt:
        pending_messages[e.message.id] = txt
        print(f"⏰ Message mis en attente (ID: {e.message.id}): {txt[:50]}...")
        return
    if "✅" in txt or "🔰" in txt:
        await process_finalized_message(txt, e.chat_id)
    else:
        print(f"⏭️ Message non finalisé ignoré : {txt[:50]}...")

@client.on(events.MessageEdited())
async def handle_edited(e):
    if e.chat_id != detected_stat_channel: return
    txt = e.message.message or ""
    if e.message.id in pending_messages:
        if "⏰" not in txt and "🕐" not in txt:
            if "✅" in txt or "🔰" in txt:
                del pending_messages[e.message.id]
                await process_finalized_message(txt, e.chat_id)
            else:
                del pending_messages[e.message.id]
        else:
            pending_messages[e.message.id] = txt

async def process_finalized_message(txt: str, chat_id: int):
    if database.is_message_processed(txt, chat_id):
        print("⏭️ Message déjà traité, ignoré")
        return
    card_counter.add(txt)
    database.mark_message_processed(txt, chat_id)
    instant = card_counter.build_report()
    if detected_display_channel:
        try:
            await client.send_message(detected_display_channel, instant)
            print(f"📈 Instantané envoyé : {instant}")
        except Exception as ex:
            print(f"❌ Erreur envoi instantané : {ex}")

# ---------- WEB SERVER ----------
async def health(request): return web.Response(text="Bot OK")
async def create_web():
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/health", health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"✅ Web server on 0.0.0.0:{PORT}")
    return runner

# ---------- START ----------
async def main():
    global client
    if not (API_ID and API_HASH and BOT_TOKEN):
        raise RuntimeError(
            "API_ID / API_HASH / BOT_TOKEN manquants – "
            "vérifiez les variables d'environnement Render"
        )
    load_config()
    load_interval()
    await create_web()
    client = TelegramClient(
        session=f"bot_session_{int(time.time())}",
        api_id=API_ID,
        api_hash=API_HASH
    )
    await client.start(bot_token=BOT_TOKEN)
    restart_auto_bilan()
    me = await client.get_me()
    print(f"Bot connecté : @{me.username}")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
