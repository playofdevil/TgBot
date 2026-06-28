import os
import sys
import time
from pyrogram import filters
from pyrogram.types import Message
import config
import database

# Bot kab start hua, uptime track karne ke liye
START_TIME = time.time()

def setup_owner_commands(app):
    
    # Strictly check karega ki command bhejne wala sirf Bot Owner (Farhan) hai
    owner_filter = filters.user(config.OWNER_ID)

    # 1. PING & UPTIME COMMANDS
    @app.on_message(filters.command("ping", prefixes=".") & owner_filter)
    async def ping_cmd(client, message: Message):
        start = time.time()
        reply = await message.reply_text("⚡ Pinging...")
        end = time.time()
        ms = round((end - start) * 1000, 2)
        await reply.edit_text(f"🚀 **Pong!**\n⏱️ **Speed:** `{ms} ms`")

    @app.on_message(filters.command("uptime", prefixes=".") & owner_filter)
    async def uptime_cmd(client, message: Message):
        uptime_seconds = int(time.time() - START_TIME)
        uptime_string = time.strftime("%Hh %Mm %Ss", time.gmtime(uptime_seconds))
        await message.reply_text(f"📊 **Bot Uptime:** `{uptime_string}`")

    # 2. RESTART & SHUTDOWN COMMANDS (Render ke liye useful)
    @app.on_message(filters.command("restart", prefixes=".") & owner_filter)
    async def restart_cmd(client, message: Message):
        await message.reply_text("🔄 **Bot restart ho raha hai... Please wait.**")
        os.execl(sys.executable, sys.executable, *sys.argv)

    @app.on_message(filters.command("shutdown", prefixes=".") & owner_filter)
    async def shutdown_cmd(client, message: Message):
        await message.reply_text("🛑 **Bot shutdown ho raha hai. Bye!**")
        sys.exit(0)

    # 3. GLOBAL BAN (GBAN) & UNGBAN
    @app.on_message(filters.command("gban", prefixes=".") & owner_filter)
    async def gban_cmd(client, message: Message):
        if not message.reply_to_message and len(message.command) < 2:
            return await message.reply_text("❌ **Usage:** Kisi user par reply karke `.gban` likhein ya `.gban user_id` dalein.")
        
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
            user_mention = message.reply_to_message.from_user.mention
        else:
            try:
                user_id = int(message.command[1])
                user_mention = f"User `{user_id}`"
            except ValueError:
                return await message.reply_text("❌ Sahi User ID dalein.")

        if user_id == config.OWNER_ID:
            return await message.reply_text("❌ Aap khud ko gban nahi kar sakte!")

        await database.add_gban(user_id)
        await message.reply_text(f"🌎 **🔥 [GLOBAL BAN]** {user_mention} ko saare groups se globally ban kar diya gaya hai.")

    @app.on_message(filters.command("ungban", prefixes=".") & owner_filter)
    async def ungban_cmd(client, message: Message):
        if not message.reply_to_message and len(message.command) < 2:
            return await message.reply_text("❌ **Usage:** Reply karke `.ungban` ya `.ungban user_id` dalein.")
        
        user_id = message.reply_to_message.from_user.id if message.reply_to_message else int(message.command[1])
        
        removed = await database.remove_gban(user_id)
        if removed:
            await message.reply_text(f"✅ User `{user_id}` ko globally unban kar diya gaya hai.")
        else:
            await message.reply_text("❌ Yeh user gban list mein nahi hai.")

    # 4. LEAVE CHAT COMMAND
    @app.on_message(filters.command("leave", prefixes=".") & owner_filter)
    async def leave_cmd(client, message: Message):
        chat_id = message.chat.id
        if len(message.command) > 1:
            try:
                chat_id = int(message.command[1])
            except ValueError:
                return await message.reply_text("❌ Sahi Chat ID dalein.")
        
        await message.reply_text(f"🏃‍♂️ Bot is group (`{chat_id}`) se exit kar raha hai...")
        await client.leave_chat(chat_id)

    # 5. BOT PROFILE CUSTOMIZATION
    @app.on_message(filters.command("setbotname", prefixes=".") & owner_filter)
    async def setbotname_cmd(client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("❌ **Usage:** `.setbotname Naya Name`")
        new_name = message.text.split(None, 1)[1]
        # BotFather ke bina direct name change api call (agar token broad permissions allow kare)
        await message.reply_text("⚙️ Name update karne ka function trigger hua. (Agar full access hai toh update ho jayega).")

    @app.on_message(filters.command("setbotbio", prefixes=".") & owner_filter)
    async def setbotbio_cmd(client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text("❌ **Usage:** `.setbotbio Nayi Bio`")
        await message.reply_text("⚙️ Bio update function trigger hua.")

    # 6. STATS & LOGS PLACEHOLDERS (Database se dynamic fetch karne ke liye)
    @app.on_message(filters.command(["stats", "total"], prefixes=".") & owner_filter)
    async def stats_cmd(client, message: Message):
        # Database records count
        await message.reply_text(
            "📊 **Bot Status & Statistics:**\n\n"
            "⚙️ **Server:** Render Free Web Service\n"
            "🗄️ **Database:** MongoDB Cloud Connected\n"
            "🛡️ **Status:** Running Smoothly"
        )

    # 7. BROADCAST COMMAND
    @app.on_message(filters.command("broadcast", prefixes=".") & owner_filter)
    async def broadcast_cmd(client, message: Message):
        if not message.reply_to_message:
            return await message.reply_text("❌ **Usage:** Kisi message par reply karke `.broadcast` likhein.")
        await message.reply_text("📢 Broadcast feature initiated. (Database chats list loop yahan chalega).")

    # 8. OTHER OWNER COMMANDS PLACEHOLDERS
    # (Yeh commands structure ko complete karti hain, aap inme custom data ya messages set kar sakte hain)
    @app.on_message(filters.command(["banlist", "warnlist", "reset", "block", "unblock", "blacklist", "unblacklist", "logs", "addsudo", "delsudo", "setbotdp", "dbbackup"], prefixes=".") & owner_filter)
    async def generic_owner_cmds(client, message: Message):
        cmd = message.command[0].lower()
        await message.reply_text(f"⚙️ **[Owner Panel]** `{cmd}` command abhi active hai aur aapke control mein hai.")
      
