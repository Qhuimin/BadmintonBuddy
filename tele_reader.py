import os
from telethon import TelegramClient, events
from telethon.tl.types import MessageReplyHeader
from dotenv import load_dotenv
from filters import is_prime_time
from game_parser import parse_message
from database import init_db, save_games
import asyncio 
from telethon.errors import FloodWaitError

# Load variables from .env
load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
DAD_USER = os.getenv("TELEGRAM_DAD_USER", "me") # Pings your dad (or "me" for testing)

# Target configurations for topic filtering
SG_BADMINTON_ID = 1209528159       # Singapore Badminton raw ID
AVAILABLE_GAMES_TOPIC_ID = 767     # "Available games" sub-topic thread ID

WATCHED_CHATS = {
    -1001645575981,                  # Singapore Badminton East
    -1001209528159,                  # Singapore Badminton 🇸🇬🏸 (-100 prefix version)
    1209528159,                      # Singapore Badminton 🇸🇬🏸 (Raw ID version)
    -5369307920,                     # Private Test Chat
}

# Create the Telegram client
client = TelegramClient("badminton_session", api_id, api_hash)

@client.on(events.NewMessage)
async def handle_new_message(event):
    """
    Runs automatically every time a new Telegram message is received.
    """
    if event.chat_id not in WATCHED_CHATS:
        return

    # --- TOPIC FILTER ROUTER ---
    # If the message comes from the main Singapore Badminton group, enforce the topic check
    if event.chat_id in (SG_BADMINTON_ID, -1001209528159):
        reply_to = event.message.reply_to
        
        # Must be in a topic, and that topic ID must match our target thread
        if not reply_to or not isinstance(reply_to, MessageReplyHeader) or reply_to.reply_to_msg_id != AVAILABLE_GAMES_TOPIC_ID:
            return
    # ---------------------------

    if not event.raw_text:
        return

    chat = await event.get_chat()
    chat_name = getattr(chat, "title", "Private Chat")

    try:
        # 1. Parse all games in the message text
        all_games = parse_message(event.raw_text)
    except Exception as e:
        print(f"\n❌ Parser crashed: {e}")
        return

    if not all_games:
        return

    print("\n==============================")
    print(f"📥 Processing {len(all_games)} game(s) from Chat: {chat_name}")

    # 2. Filter out slots that fall within your dad's preferred 7pm - 11pm window
    prime_games = [g for g in all_games if is_prime_time(g.start_time)]
    
    if not prime_games:
        print("ℹ️ Games found, but none fall within the 7pm-11pm target window.")
        print("==============================")
        return

    # 3. Attempt to persist unique matches to SQLite database
    new_saved_count = save_games(prime_games)
    
    if new_saved_count > 0:
        print(f"🔥 Found {new_saved_count} NEW prime-time games! Forwarding alert...")
        
        try:
            # Forward the original group message cleanly
            await event.message.forward_to(DAD_USER)
            print("✉️ Source message forwarded successfully.")
            
            # Crucial: Give the Telegram API a breath to avoid flooding limits
            await asyncio.sleep(1.5)
            
        except FloodWaitError as e:
            print(f"⚠️ Telegram Rate Limit hit! Script must sleep for {e.seconds} seconds.")
            await asyncio.sleep(e.seconds)
            # Retry once after cooling down
            await event.message.forward_to(DAD_USER)
        except Exception as e:
            print(f"❌ Failed to forward message: {e}")
            
    else:
        print("🔁 Prime-time games detected, but they already exist in database. Alert skipped.")


def run():
    """
    Starts the Telegram client and keeps listening forever.
    """
    # Guarantee the DB schema exists before booting network tasks
    init_db()

    async def main():
        me = await client.get_me()
        print(f"✅ Logged in as {me.first_name}")
        print("👀 Listening for new messages...")

    with client:
        client.loop.run_until_complete(main())
        client.run_until_disconnected()