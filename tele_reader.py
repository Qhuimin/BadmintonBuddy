from telethon import TelegramClient, events
from dotenv import load_dotenv
import os

# Load variables from .env
load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

# Create the Telegram client
client = TelegramClient("badminton_session", api_id, api_hash)


@client.on(events.NewMessage)
async def handle_new_message(event):
    """
    Runs automatically every time a new Telegram message is received.
    """

    chat = await event.get_chat()

    chat_name = getattr(chat, "title", "Private Chat")

    print("\n==============================")
    print(f"Chat: {chat_name}")
    print("Message:")
    print(event.raw_text)
    print("==============================")


def run():
    """
    Starts the Telegram client and keeps listening forever.
    """

    async def main():
        me = await client.get_me()

        print(f"✅ Logged in as {me.first_name}")
        print("👀 Listening for new messages...")

    with client:
        client.loop.run_until_complete(main())
        client.run_until_disconnected()