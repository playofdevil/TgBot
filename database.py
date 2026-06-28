import motor.motor_asyncio
import config

# MongoDB Client Setup
# Agar MONGO_URL nahi milti toh local ya dummy URL check karega, par Render par hum real URL dalenge.
client = motor.motor_asyncio.AsyncIOMotorClient(config.MONGO_URL)
db = client["rose_management_bot"]

# Database Collections
filters_db = db["filters"]
welcome_db = db["welcome"]
warns_db = db["warns"]
gban_db = db["gban"]
rules_db = db["rules"]

# --- FILTERS LOGIC ---
async def add_filter(chat_id: int, keyword: str, reply_text: str):
    keyword = keyword.lower()
    await filters_db.update_one(
        {"chat_id": chat_id, "keyword": keyword},
        {"$set": {"reply_text": reply_text}},
        upsert=True
    )

async def get_filter(chat_id: int, keyword: str):
    keyword = keyword.lower()
    res = await filters_db.find_one({"chat_id": chat_id, "keyword": keyword})
    return res["reply_text"] if res else None

async def del_filter(chat_id: int, keyword: str):
    keyword = keyword.lower()
    res = await filters_db.delete_one({"chat_id": chat_id, "keyword": keyword})
    return res.deleted_count > 0

async def get_all_filters(chat_id: int):
    cursor = filters_db.find({"chat_id": chat_id})
    filters_list = []
    async for doc in cursor:
        filters_list.append(doc["keyword"])
    return filters_list


# --- WELCOME LOGIC ---
async def set_welcome(chat_id: int, welcome_text: str):
    await welcome_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"welcome_text": welcome_text}},
        upsert=True
    )

async def get_welcome(chat_id: int):
    res = await welcome_db.find_one({"chat_id": chat_id})
    return res["welcome_text"] if res else None

async def del_welcome(chat_id: int):
    res = await welcome_db.delete_one({"chat_id": chat_id})
    return res.deleted_count > 0


# --- RULES LOGIC ---
async def set_rules(chat_id: int, rules_text: str):
    await rules_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"rules_text": rules_text}},
        upsert=True
    )

async def get_rules(chat_id: int):
    res = await rules_db.find_one({"chat_id": chat_id})
    return res["rules_text"] if res else None


# --- WARNS LOGIC ---
async def add_warn(chat_id: int, user_id: int):
    res = await warns_db.find_one({"chat_id": chat_id, "user_id": user_id})
    count = (res["count"] if res else 0) + 1
    await warns_db.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"count": count}},
        upsert=True
    )
    return count

async def get_warns(chat_id: int, user_id: int):
    res = await warns_db.find_one({"chat_id": chat_id, "user_id": user_id})
    return res["count"] if res else 0

async def reset_warns(chat_id: int, user_id: int):
    await warns_db.delete_one({"chat_id": chat_id, "user_id": user_id})


# --- GLOBAL BAN (GBAN) LOGIC ---
async def add_gban(user_id: int):
    await gban_db.update_one(
        {"user_id": user_id},
        {"$set": {"gbanned": True}},
        upsert=True
    )

async def remove_gban(user_id: int):
    res = await gban_db.delete_one({"user_id": user_id})
    return res.deleted_count > 0

async def is_gbanned(user_id: int):
    res = await gban_db.find_one({"user_id": user_id})
    return True if res else False
  
