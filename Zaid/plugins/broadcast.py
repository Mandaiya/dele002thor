import asyncio
from hydrogram import Client, filters
from hydrogram.errors import FloodWait
from dotenv import load_dotenv
from config import API_ID, API_HASH, BOT_TOKEN

client = Client('broadcast_bot', api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

IS_BROADCASTING = False

@client.on_message(filters.command("broadcast") & filters.user(SUDOERS))
async def broadcast_message(client, message):
    global IS_BROADCASTING
    if IS_BROADCASTING:
        return await message.reply("A broadcast is already in progress.")
    
    if message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
        query = None
    else:
        if len(message.command) < 2:
            return await message.reply("Please provide a message to broadcast.")
        query = message.text.split(None, 1)[1]
        x = None
        y = None

    IS_BROADCASTING = True
    await message.reply("Starting broadcast...")

    sent_chats = 0
    sent_users = 0

    if "-nobot" not in message.text:
        schats = [dialog.chat.id for dialog in await client.get_dialogs() if dialog.chat.type in ["group", "supergroup", "channel"]]
        for chat_id in schats:
            try:
                if x:
                    await client.forward_messages(chat_id, y, [x], as_copy=True)
                else:
                    await client.send_message(chat_id, query)
                sent_chats += 1
                await asyncio.sleep(0.2)
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                print(f"Failed to send message to chat {chat_id}: {e}")

    if "-user" in message.text:
        susers = [dialog.chat.id for dialog in await client.get_dialogs() if dialog.chat.type == "private"]
        for user_id in susers:
            try:
                if x:
                    await client.forward_messages(user_id, y, [x], as_copy=True)
                else:
                    await client.send_message(user_id, query)
                sent_users += 1
                await asyncio.sleep(0.2)
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception as e:
                print(f"Failed to send message to user {user_id}: {e}")

    await message.reply(f"Broadcast completed: Sent to {sent_chats} chats and {sent_users} users.")
    IS_BROADCASTING = False

async def main():
    await client.start()
    await client.idle()

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
