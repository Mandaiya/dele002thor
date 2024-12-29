from Zaid import Zaid, BOT_USERNAME
from Config import Config
from telethon import events, Button

PM_START_TEXT = """
Hello! {}

❂ I am a simple music bot on Telegram, here to play your favorite tunes!.
🏎 Just let me know what song you want, and I’ll play it for you!.
🏎 This bot is just for listening to music; there are no additional management features
🏎 I can do a lot of things, but I’m still in development. Please handle me with care!.

  We are the Universe People – initially a network for selling VPS, we have since evolved into providing bots for user use.

 ✾ Having queries - | Contact the Universe - Networks -☯- \n| @universe_we_are | -☯-


☣ **ᴄʟɪᴄᴋ ᴏɴ SAVE  ʙᴜᴛᴛᴏɴ ꜰᴏʀ ᴍᴏʀᴇ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ**.
"""

@Zaid.on(events.NewMessage(pattern="^[?/]start$"))
async def start(event):
    if Config.MANAGEMENT_MODE == "ENABLE":
        return
    if event.is_private:
       await event.client.send_file(event.chat_id,
             Config.START_IMG,
             caption=PM_START_TEXT.format(event.sender.first_name), 
             buttons=[
        [Button.url("☢ Kidnap Me ", f"https://t.me/{BOT_USERNAME}?startgroup=true"), Button.inline("🚁​ save ", data="help")]])
       return

    if event.is_group:
       await event.reply("🌠 **ʜᴇʏ! ɪ'ᴍ ꜱᴛɪʟʟ ᴀʟɪᴠᴇ! and working fine ! Thank you for checking up!**")
       return



@Zaid.on(events.callbackquery.CallbackQuery(data="start"))
async def _(event):
    if Config.MANAGEMENT_MODE == "ENABLE":
        return
    if event.is_private:
       await event.edit(PM_START_TEXT.format(event.sender.first_name), buttons=[
        [Button.url("➿ ᴀᴅᴅ ᴍᴇ", f"https://t.me/{BOT_USERNAME}?startgroup=true"), Button.inline("☏ ʜᴇʟᴘ", data="help")]])
       return
