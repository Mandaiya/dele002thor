import asyncio
from telethon import TelegramClient, events
from telethon.errors import FloodWait
from telethon.tl.types import ChannelParticipantsAdmins
from config import Config
from dotenv import load_dotenv

try:
    ...
except errors.FloodWaitError as e:
    print('Flood wait for ', e.seconds)

load_dotenv()

# Replace these with your own values
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

client = TelegramClient('broadcast_bot', api_id, api_hash).start(bot_token=bot_token)

IS_BROADCASTING = False

@client.on(events.NewMessage(pattern='/broadcast'))
async def broadcast_message(event):
    global IS_BROADCASTING
    message = event.message
    if message.is_reply:
        x = message.reply_to_msg_id
        y = message.chat_id
    else:
        if len(message.message.split()) < 2:
            return await message.reply("Please provide a message to broadcast.")
        query = message.message.split(None, 1)[1]
        if "-pin" in query:
            query = query.replace("-pin", "")
        if "-nobot" in query:
            query = query.replace("-nobot", "")
        if "-pinloud" in query:
            query = query.replace("-pinloud", "")
        if "-assistant" in query:
            query = query.replace("-assistant", "")
        if "-user" in query:
            query = query.replace("-user", "")
        if query == "":
            return await message.reply("Broadcast message cannot be empty.")

    IS_BROADCASTING = True
    await message.reply("Broadcasting message...")

    # Broadcast to chats
    if "-nobot" not in message.message:
        sent = 0
        pin = 0
        chats = [chat_id for chat_id in await client.get_dialogs() if chat_id.is_group]
        
        for i in chats:
            try:
                m = (
                    await client.forward_messages(i, y, x)
                    if message.is_reply
                    else await client.send_message(i, query)
                )
                if "-pin" in message.message:
                    try:
                        await client.pin_message(i, m.id, notify=False)
                        pin += 1
                    except:
                        continue
                elif "-pinloud" in message.message:
                    try:
                        await client.pin_message(i, m.id, notify=True)
                        pin += 1
                    except:
                        continue
                sent += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                flood_time = int(fw.seconds)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except:
                continue
        try:
            await message.reply(f"Broadcast completed: Sent to {sent} chats, pinned in {pin} chats.")
        except:
            pass

    # Broadcast to users
    if "-user" in message.message:
        susr = 0
        for dialog in await client.get_dialogs():
            if dialog.is_user:
                try:
                    m = (
                        await client.forward_messages(dialog.id, y, x)
                        if message.is_reply
                        else await client.send_message(dialog.id, query)
                    )
                    susr += 1
                    await asyncio.sleep(0.2)
                except FloodWait as fw:
                    flood_time = int(fw.seconds)
                    if flood_time > 200:
                        continue
                    await asyncio.sleep(flood_time)
                except:
                    pass
        try:
            await message.reply(f"Broadcast completed: Sent to {susr} users.")
        except:
            pass

    # Broadcast using assistants
    if "-assistant" in message.message:
        aw = await message.reply("Broadcasting to assistants...")
        text = "Broadcast to assistants started.\n\n"
        assistants = [assistant_id]  # Define your assistant bot IDs here

        for num in assistants:
            sent = 0
            assistant_client = await client.clone(num)
            async for dialog in assistant_client.iter_dialogs():
                try:
                    await assistant_client.forward_messages(
                        dialog.id, y, x
                    ) if message.is_reply else await assistant_client.send_message(
                        dialog.id, query
                    )
                    sent += 1
                    await asyncio.sleep(3)
                except FloodWait as fw:
                    flood_time = int(fw.seconds)
                    if flood_time > 200:
                        continue
                    await asyncio.sleep(flood_time)
                except:
                    continue
            text += f"Assistant {num}: Sent to {sent} chats.\n"
        try:
            await aw.edit(text)
        except:
            pass
    IS_BROADCASTING = False

async def auto_clean():
    while not await asyncio.sleep(10):
        try:
            adminlist = {}
            async for dialog in client.get_dialogs():
                if dialog.is_group:
                    adminlist[dialog.id] = []
                    async for user in client.iter_participants(dialog.id, filter=ChannelParticipantsAdmins):
                        if user.admin_rights and user.admin_rights.manage_call:
                            adminlist[dialog.id].append(user.id)
        except:
            continue

client.loop.create_task(auto_clean())
client.start()
client.run_until_disconnected()
