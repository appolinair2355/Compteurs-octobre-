import os, asyncio, json, re, time
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
PORT     = int(os.getenv("PORT") or 10000)

# ---------- GLOBALS ----------
detected_stat_channel  = None
detected_display_channel = int(os.getenv("DISPLAY_CHANNEL") or 0)
CONFIG_FILE   = "bot_config.json"
INTERVAL_FILE = "interval.json"
AUTO_BILAN_MIN = 30
AUTO_TASK      = None

database = init_database()
predictor    = CardPredictor()
card_counter = CardCounter()
client       = TelegramClient(f"bot_session_{int(time.time())}", API_ID, API_HASH)

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
            msg = card_counter.report_and_reset()  # envoie + reset
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
    detected_display_channel = int(e.pattern_match.group(1))
    save_config()
    await e.respond("✅ Canal d’affichage enregistré.")

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

# ---------- MESSAGE HANDLER ----------
@client.on(events.NewMessage())
@client.on(events.MessageEdited())
async def handle(e):
    if e.chat_id != detected_stat_channel: return
    txt = e.message.message or ""
    if "✅" in txt or "🔰" in txt:
        card_counter.add(txt)
        # ===== ENVOI INSTANTANÉ (sans reset) =====
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
    load_config()
    load_interval()
    await create_web()
    await client.start(bot_token=BOT_TOKEN)
    restart_auto_bilan()
    me = await client.get_me()
    print(f"Bot connecté : @{me.username}")
    await client.run_until_disconnected()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
