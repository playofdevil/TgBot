from pyrogram import filters
from pyrogram.types import Message
import database

def setup_user_commands(app):

    # 1. START COMMAND
    @app.on_message(filters.command("start", prefixes="."))
    async def start_cmd(client, message: Message):
        await message.reply_text(
            "Hello! Main ek powerful Group Management Bot hoon.\n"
            "Mujhe apne group mein add karke Admin banayein taaki main aapke group ko safe aur clean rakh sakoon.\n\n"
            "Saari commands dekhne ke liye `.help` type karein."
        )

    # 2. HELP COMMAND
    @app.on_message(filters.command("help", prefixes="."))
    async def help_cmd(client, message: Message):
        help_text = (
            "**📌 Normal User Commands List:**\n\n"
            "`.start` - Bot ko shuru karne ke liye.\n"
            "`.help` - Yeh help menu dekhne ke liye.\n"
            "`.id` - Apni ya chal rahe chat ki Telegram ID janne ke liye.\n"
            "`.info` - Apni ya kisi aur user ki profile details dekhne ke liye.\n"
            "`.rules` - Group ke rules dekhne ke liye.\n"
            "`.report` - Kisi spam/galat message par reply karke admins ko alert karne ke liye."
        )
        await message.reply_text(help_text)

    # 3. ID COMMAND
    @app.on_message(filters.command("id", prefixes="."))
    async def id_cmd(client, message: Message):
        text = f"👤 **Aapki ID:** `{message.from_user.id}`\n"
        if message.chat.type != message.chat.type.PRIVATE:
            text += f"👥 **Group ID:** `{message.chat.id}`"
        await message.reply_text(text)

    # 4. INFO COMMAND
    @app.on_message(filters.command("info", prefixes="."))
    async def info_cmd(client, message: Message):
        # Agar kisi ke message par reply kiya hai toh uski info dikhayega, nahi toh khud ki
        user = message.from_user
        if message.reply_to_message and message.reply_to_message.from_user:
            user = message.reply_to_message.from_user
            
        info_text = (
            f"ℹ️ **User Information:**\n\n"
            f"**First Name:** {user.first_name}\n"
            f"**Last Name:** {user.last_name or 'None'}\n"
            f"**Username:** @{user.username or 'None'}\n"
            f"**User ID:** `{user.id}`\n"
            f"**User Link:** [Click Here](tg://user?id={user.id})"
        )
        await message.reply_text(info_text)

    # 5. RULES COMMAND
    @app.on_message(filters.command("rules", prefixes="."))
    async def rules_cmd(client, message: Message):
        if message.chat.type == message.chat.type.PRIVATE:
            return await message.reply_text("Rules command sirf groups mein kaam karti hai.")
        
        rules = await database.get_rules(message.chat.id)
        if rules:
            await message.reply_text(f"📋 **Group Rules:**\n\n{rules}")
        else:
            await message.reply_text("Is group mein abhi tak koi rules set nahi kiye gaye hain.")

    # 6. REPORT COMMAND
    @app.on_message(filters.command("report", prefixes="."))
    async def report_cmd(client, message: Message):
        if message.chat.type == message.chat.type.PRIVATE:
            return await message.reply_text("Report command sirf groups mein kaam karti hai.")
        
        if not message.reply_to_message:
            return await message.reply_text("❌ **Galti:** Kisi galat message par reply karke `.report` likhein taaki admins ko alert kiya ja sake.")
        
        reported_user = message.reply_to_message.from_user
        reporter = message.from_user
        
        if not reported_user:
            return await message.reply_text("Main is user ko track nahi kar paa raha hoon.")

        alert_text = (
            f"⚠️ **[REPORT ALERT]**\n\n"
            f"👤 **Reporter:** {reporter.mention} (`{reporter.id}`)\n"
            f"🚫 **Reported Spammer:** {reported_user.mention} (`{reported_user.id}`)\n"
            f"🔗 **Message Link:** [Yahan Dekhein]({message.reply_to_message.link})\n\n"
            f"Admins please check karein aur action lein!"
        )
        await message.reply_text(alert_text)
      
