from telethon import TelegramClient
from dotenv import load_dotenv
import os

# Load variables from .env
load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

# Create a Telegram session
client = TelegramClient("badminton_session", api_id, api_hash)

async def main():
    me = await client.get_me()
    print(f"✅ Logged in as {me.first_name}")

with client:
    client.loop.run_until_complete(main())