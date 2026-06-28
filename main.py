import os
import threading
from http.server import SimpleHTTPRequestHandler
from http.server import ThreadingHTTPServer
from pyrogram import Client, filters
from pyrogram.types import Message

import config
import database
from owner_commands import setup_owner_commands
from admin_commands import setup_admin_commands
from user_commands import setup_user_commands

# --- RENDER PORT BINDING FIX (LIGHTWEIGHT WEB SERVER) ---
# Render free service chahti hai ki bot kisi port par listen kare, isliye hum ek background server chalate hain.
class RenderServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is running successfully 24/7!")

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    server = ThreadingHTTPServer(("0.0.0.0", port), RenderServer)
    print(f"ℹ️ Render Web Server started on port {port}")
    server.serve_forever()

# Web server ko alag thread par start karein taaki bot block na ho
web_thread = threading.Thread(target=run_web_server, daemon=True)
web_thread.start()


# --- PYROGRAM BOT CLIENT INITIALIZATION ---
app = Client(
    "rose_management_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)


# --- LOAD ALL COMMANDS SYSTEM ---
setup_owner_commands(app)
setup_admin_commands(app)
setup_user_commands(app)


# --- AUTOMATIC EVENT HANDLERS (GBAN, WELCOME & FILTERS) ---

# 1. Global Ban (GBan) Check & Auto-Filters
@app.on_message(filters.group & ~filters.service, group=1)
async def global_handler(client, message: Message):
    if not message.from_user:
        return

    user_id = message.from_user.id
    chat_id = message.chat.id

    # Security Check: Agar user Globally Ban (GBanned) hai toh use aate hi ban karo
    if await database.is_gbanned(user_id):
        try:
            await message.chat.ban_member(user_id)
            await message.delete() # Uska message delete karein
            return print(f"🛡️ GBanned User {user_id} ko automatic group se uda diya gaya.")
        except Exception:
            pass # Agar bot admin nahi hai toh ignore karega

    # Auto-Filter Check: Agar message text kisi filter se match karta hai
    if message.text:
        word = message.text.strip().lower()
        reply_text = await database.get_filter(chat_id, word)
        if reply_text:
            await message.reply_text(reply_text)


# 2. Welcome Message System (Jab naya member group join kare)
@app.on_message(filters.new_chat_members, group=2)
async def welcome_handler(client, message: Message):
    chat_id = message.chat.id
    
    for member in message.new_chat_members:
        # Agar naya member khud GBanned list mein hai
        if await database.is_gbanned(member.id):
            try:
                await message.chat.ban_member(member.id)
                continue
            except Exception:
                pass

        # Custom welcome message check karein database se
        welcome_text = await database.get_welcome(chat_id)
        if welcome_text:
            # {mention} aur {name} placeholders ko replace karein agar text mein hain
            final_text = welcome_text.replace("{mention}", member.mention).replace("{name}", member.first_name)
            await message.reply_text(final_text)
        else:
            # Default welcome message agar group admin ne set nahi kiya hai
            await message.reply_text(f"👋 Welcome {member.mention} to the group!")


# --- START THE BOT ENGINE ---
if __name__ == "__main__":
    print("🚀 Bot engine starting up...")
    app.run()
  
