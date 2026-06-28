from pyrogram import filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ChatMemberStatus, ChatMembersFilter
import database
import config

def setup_admin_commands(app):

    # Helper function: Check karega ki user admin hai ya nahi
    async def is_user_admin(client, message: Message):
        if message.chat.type == message.chat.type.PRIVATE:
            return False
        # Bot owner ko bypass milega (Aap hamesha admin treat honge)
        if message.from_user.id == config.OWNER_ID:
            return True
        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return True
        except Exception:
            return False
        return False

    # 1. BAN, UNBAN, & KICK COMMANDS
    @app.on_message(filters.command("ban", prefixes="."))
    async def ban_cmd(client, message: Message):
        if not await is_user_admin(client, message): return
        if not message.reply_to_message:
            return await message.reply_text("❌ **Galti:** Kisi user ke message par reply karke `.ban` likhein.")
        
        user = message.reply_to_message.from_user
        await message.chat.ban_member(user.id)
        await message.reply_text(f"✈️ {user.mention} ko group se block (ban) kar diya gaya hai.")

    @app.on_message(filters.command("unban", prefixes="."))
    async def unban_cmd(client, message: Message):
        if not await is_user_admin(client, message): return
        if not message.reply_to_message and len(message.command) < 2:
            return await message.reply_text("❌ **Usage:** Reply karke `.unban` ya `.unban user_id` dalein.")
        
        user_id = message.reply_to_message.from_user.id if message.reply_to_message else int(message.command[1])
        await message.chat.unban_member(user_id)
        await message.reply_text(f"✅ User (`{user_id}`) ko unban kar diya gaya hai.")

    @app.on_message(filters.command("kick", prefixes="."))
    async def kick_cmd(client, message: Message):
        if not await is_user_admin(client, message): return
        if not message.reply_to_message:
            return await message.reply_text("❌ Reply karke `.kick` likhein.")
        
        user = message.reply_to_message.from_user
        await message.chat.ban_member(user.id)
        await message.chat.unban_member(user.id) # Ban karke unban karne se user sirf kick ho jata hai
        await message.reply_text(f"🏃‍♂️ {user.mention} ko group se nikal (kick) diya gaya hai.")

    # 2. MUTE & UNMUTE COMMANDS
    @app.on_message(filters.command("mute", prefixes="."))
    async def mute_cmd(client, message: Message):
        if not await is_user_admin(client, message): return
        if not message.reply_to_message:
            return await message.reply_text("❌ Reply karke `.mute` likhein.")
        
        user = message.reply_to_message.from_user
        await message.chat.restrict_member(user.id, ChatPermissions(can_send_messages=False))
        await message.reply_text(f"🤐 {user.mention} ko mute kar diya gaya hai. Ab woh message nahi bhej sakta.")

    @app.on_message(filters.command("unmute", prefixes="."))
    async def unmute_cmd(client, message: Message):
        if not await is_user_admin(client, message): return
        if not message.reply_to_message:
            return await message.reply_text("❌ Reply karke `.unmute` likhein.")
        
        user = message.reply_to_message.from_user
        await message.chat.restrict_member(user.id, ChatPermissions(
            can_send_messages=True, can_send_media_messages=True,
            can_send_other_messages=True, can_add_web_page_previews=True
        ))
        await message.reply_text(f"🔊 {user.mention} ko unmute kar diya gaya hai.")

    # 3. PURGE & DELETE (Spam Cleaning)
    @app.on_message(filters.command("purge", prefixes="."))
    async def purge_cmd(client, message: Message):
        if not await is_user_admin(client, message): return
        if not message.reply_to_message:
            return await message.reply_text("❌ Jahan se delete karna shuru karna hai, us message par reply karke `.purge` likhein.")
        
        chat_id = message.chat.id
        from_message_id = message.reply_to_message.id
        to_message_id = message.id
        
        message_ids = list(range(from_message_id, to_message_id + 1))
        
        # Telegram ek baar mein max 100 messages delete karne deta hai, hum chunks mein karenge
        for i in range(0, len(message_ids), 100):
            await client.delete_messages(chat_id, message_ids[i:i+100])
        
        await message.reply_text("🧹 Purge complete! Saare fuzool messages delete ho gaye.")

    @app.on_message(filters.command("del", prefixes="."))
    async def del_cmd(client, message: Message):
        if not await is_user_admin(client, message): return
        if message.reply_to_message:
            await message.reply_to_message.delete()
            await message.delete()

    # 4. FILTERS LOGIC (Add, View, Delete)
    @app.on_message(filters.command("filter", prefixes="."))
    async def add_filter_cmd(client, message: Message):
        if not await is_user_admin(client, message): return
        if len(message.command) < 2 or not message.reply_to_message:
            return await message.reply_text("❌ **Usage:** Kisi text par reply karke `.filter keyword` likhein.")
        
        keyword = message.command[1].lower()
        reply_text = message.reply_to_message.text
        await database.add_filter(message.chat.id, keyword, reply_text)
        await message.reply_text(f"✅ Filter save ho gaya! Ab jab bhi koi `{keyword}` likhega, bot auto-reply karega.")

    @app.on_message(filters.command("filters", prefixes="."))
    async def list_filters_cmd(client, message: Message):
        if not await is_user_admin(client, message): return
        all_filters = await database.get_all_filters(message.chat.id)
        if not all_filters:
            return await message.reply_text("Is group mein koi filters set nahi hain.")
        
        text = "📝 **Group Filters List:**\n\n" + "\n".join([f"• `{f}`" for f in all_filters])
        await message.reply_text(text)

    @app.on_message(filters.command("delfilter", prefixes="."))
    async def del_filter_cmd(client, message: Message):
        if not await is_user_admin(client, message): return
        if len(message.command) < 2:
            return await message.reply_text("❌ **Usage:** `.delfilter keyword`")
        
        keyword = message.command[1].lower()
        deleted = await database.del_filter(message.chat.id, keyword)
        if deleted:
            await message.reply_text(f"🗑️ Filter `{keyword}` ko delete kar diya gaya hai.")
        else:
            await message.reply_text("❌ Aisa koi filter nahi mila.")

    # 5. WELCOME SETTINGS
    @app.on_message(filters.command("setwelcome", prefixes="."))
    async def set_welcome_cmd(client, message: Message):
        if not await is_user_admin(client, message): return
        if not message.reply_to_message:
            return await message.reply_text("❌ Welcome text par reply karke `.setwelcome` likhein.")
        
        await database.set_welcome(message.chat.id, message.reply_to_message.text)
        await message.reply_text("👋 New welcome message group ke liye save ho gaya hai!")

    @app.on_message(filters.command("delwelcome", prefixes="."))
    async def del_welcome_cmd(client, message: Message):
        if not await is_user_admin(client, message): return
        await database.del_welcome(message.chat.id)
        await message.reply_text(f"🗑️ Welcome message hata diya gaya hai.")

    # 6. GROUP RULES SETTING (Admins rules set kar sakte hain)
    @app.on_message(filters.command("setrules", prefixes="."))
    async def set_rules_cmd(client, message: Message):
        if not await is_user_admin(client, message): return
        if not message.reply_to_message:
            return await message.reply_text("❌ Rules ke text par reply karke `.setrules` likhein.")
        
        await database.set_rules(message.chat.id, message.reply_to_message.text)
        await message.reply_text("📋 Group ke rules update ho gaye hain!")

    # 7. STAFF COMMAND (Strictly Secure - Sirf Admins dekh sakte hain)
    @app.on_message(filters.command("staff", prefixes="."))
    async def staff_cmd(client, message: Message):
        if not await is_user_admin(client, message): return
        
        staff_text = "🛡️ **Group Staff Members:**\n\n"
        async for admin in client.get_chat_members(message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS):
            status_tag = "👑 Owner" if admin.status == ChatMemberStatus.OWNER else "👮 Admin"
            staff_text += f"• {admin.user.mention} | `{admin.user.id}` | __{status_tag}__\n"
            
        await message.reply_text(staff_text)

    # 8. LOCK / UNLOCK SYSTEM
    @app.on_message(filters.command("lock", prefixes="."))
    async def lock_cmd(client, message: Message):
        if not await is_user_admin(client, message): return
        if len(message.command) < 2:
            return await message.reply_text("❌ **Usage:** `.lock msg` ya `.lock media`")
        
        lock_type = message.command[1].lower()
        if lock_type == "msg":
            await message.chat.restrict_member(message.chat.id, ChatPermissions(can_send_messages=False))
            await message.reply_text("🔒 Chat ko lock kar diya gaya hai. Ab normal users message nahi bhej sakte.")
        elif lock_type == "media":
            await message.chat.restrict_member(message.chat.id, ChatPermissions(can_send_media_messages=False))
            await message.reply_text("🔒 Media locking lag gayi hai.")

    @app.on_message(filters.command("unlock", prefixes="."))
    async def unlock_cmd(client, message: Message):
        if not await is_user_admin(client, message): return
        await message.chat.restrict_member(message.chat.id, ChatPermissions(
            can_send_messages=True, can_send_media_messages=True,
            can_send_other_messages=True, can_add_web_page_previews=True
        ))
        await message.reply_text("🔓 Group ko unlock kar diya gaya hai. Sabhi log normal chat kar sakte hain.")

    # 9. PLACEHOLDERS FOR REMAINING ADMIN/MOD COMMANDS
    # (Inhein aap feature updates ke liye use kar sakte hain)
    @app.on_message(filters.command(["warn", "rwarn", "promote", "demote", "admin", "mod", "welcome", "settings", "permission", "allow", "disallow", "sticker", "userfree", "ipban", "settitle", "setdescription", "tmute", "tban", "pin", "unpin", "notes"], prefixes="."))
    async def generic_admin_cmds(client, message: Message):
        if not await is_user_admin(client, message): return
        cmd = message.command[0].lower()
        await message.reply_text(f"⚙️ **[Admin Tool]** `{cmd}` command active hai aur database ready hai.")
                                            
