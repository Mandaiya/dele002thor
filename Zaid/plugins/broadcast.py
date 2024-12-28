import asyncio
from pyromod import listen
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.enums import ChatMembersFilter

from config import SUDOERS, adminlist

app = Client("annie_bot")
IS_BROADCASTING = False

@app.on_message(filters.command("broadcast") & filters.user(SUDOERS))
async def broadcast_message(client, message):
    global IS_BROADCASTING
    if message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
    else:
        if len(message.command) < 2:
            return await message.reply_text("Please provide a message to broadcast.")
        query = message.text.split(None, 1)[1]

        # Handle flags
        pin = "-pin" in query
        loud_pin = "-pinloud" in query
        user_broadcast = "-user" in query

        query = query.replace("-pin", "").replace("-pinloud", "").replace("-user", "").strip()

        if not query:
            return await message.reply_text("Broadcast message cannot be empty.")

    IS_BROADCASTING = True
    await message.reply_text("Broadcasting... Please wait.")

    # Broadcast to chats
    sent = 0
    pin_count = 0
    async for dialog in app.get_dialogs():
        try:
            m = (
                await app.forward_messages(dialog.chat.id, y, x)
                if message.reply_to_message
                else await app.send_message(dialog.chat.id, query)
            )
            if pin or loud_pin:
                try:
                    await m.pin(disable_notification=not loud_pin)
                    pin_count += 1
                except Exception as e:
                    print(f"Failed to pin in {dialog.chat.id}: {e}")
            sent += 1
            await asyncio.sleep(0.2)
        except FloodWait as fw:
            await asyncio.sleep(fw.value)
        except Exception as e:
            print(f"Failed to send message to {dialog.chat.id}: {e}")

    await message.reply_text(f"Broadcast completed. Sent to {sent} chats. Pinned in {pin_count} chats.")
    IS_BROADCASTING = False


@app.on_message(filters.command("clean_admins") & filters.user(SUDOERS))
async def auto_clean(client, message):
    adminlist.clear()
    async for dialog in app.get_dialogs():
        try:
            async for member in app.get_chat_members(dialog.chat.id, filter=ChatMembersFilter.ADMINISTRATORS):
                if member.privileges.can_manage_video_chats:
                    if dialog.chat.id not in adminlist:
                        adminlist[dialog.chat.id] = []
                    adminlist[dialog.chat.id].append(member.user.id)
        except Exception as e:
            print(f"Failed to fetch admins for {dialog.chat.id}: {e}")
    await message.reply_text("Admin list refreshed.")


app.run()
