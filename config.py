import os

# Telegram API Details (my.telegram.org se milti hain)
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")

# Bot Token (Jo @BotFather se mila hai)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Bot Owner ki Telegram User ID (Sirf aapki ID)
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))

# MongoDB Database URL (Data save karne ke liye)
MONGO_URL = os.environ.get("MONGO_URL", "")
