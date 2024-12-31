from pytgcalls import StreamType
from pytgcalls.types import Update
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from pytgcalls.types.input_stream.quality import (
    HighQualityAudio,
    HighQualityVideo,
    LowQualityVideo,
    MediumQualityVideo,
)
from telethon.tl.functions.channels import LeaveChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from pytgcalls.exceptions import (
    NoActiveGroupCall,
    NotInGroupCallError
)
from Zaid.status import *
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.messages import ExportChatInviteRequest
import telethon.utils
from telethon.tl import functions
from telethon.tl import types
from telethon.utils import get_display_name
from telethon.tl.functions.users import GetFullUserRequest
from youtubesearchpython import VideosSearch

 
fotoplay = "https://telegra.ph/file/b6402152be44d90836339.jpg"
ngantri = "https://telegra.ph/file/b6402152be44d90836339.jpg"
from Zaid import call_py, Zaid, client as Client
owner = "655594746"
from Zaid.helpers.yt_dlp import bash, ytdl
from Zaid.helpers.chattitle import CHAT_TITLE
from Zaid.helpers.queues import (
    QUEUE,
    add_to_queue,
    clear_queue,
    get_queue,
    pop_an_item,
    active,
)
from telethon import Button, events
from Config import Config

from Zaid.helpers.thumbnail import gen_thumb
from Zaid.helpers.joiner import AssistantAdd

def vcmention(user):
    full_name = get_display_name(user)
    if not isinstance(user, types.User):
        return full_name
    return f"[{full_name}](tg://user?id={user.id})"


def ytsearch(query: str):
    try:
        search = VideosSearch(query, limit=1).result()
        data = search["result"][0]
        songname = data["title"]
        url = data["link"]
        duration = data["duration"]
        thumbnail = f"https://i.ytimg.com/vi/{data['id']}/hqdefault.jpg"
        videoid = data["id"]
        return [songname, url, duration, thumbnail, videoid]
    except Exception as e:
        print(e)
        return 0


async def skip_item(chat_id: int, x: int):
    if chat_id not in QUEUE:
        return 0
    chat_queue = get_queue(chat_id)
    try:
        songname = chat_queue[x][0]
        chat_queue.pop(x)
        return songname
    except Exception as e:
        print(e)
        return 0


async def skip_current_song(chat_id: int):
    if chat_id not in QUEUE:
        return 0
    chat_queue = get_queue(chat_id)
    if len(chat_queue) == 1:
        await call_py.leave_group_call(chat_id)
        clear_queue(chat_id)
        active.remove(chat_id)
        return 1
    songname = chat_queue[1][0]
    url = chat_queue[1][1]
    link = chat_queue[1][2]
    type = chat_queue[1][3]
    RESOLUSI = chat_queue[1][4]
    if type == "Audio":
        await call_py.change_stream(
            chat_id,
            AudioPiped(
                url,
            ),
        )
    elif type == "Video":
        if RESOLUSI == 720:
            hm = HighQualityVideo()
        elif RESOLUSI == 480:
            hm = MediumQualityVideo()
        elif RESOLUSI == 360:
            hm = LowQualityVideo()
        await call_py.change_stream(
            chat_id, AudioVideoPiped(url, HighQualityAudio(), hm)
        )
    pop_an_item(chat_id)
    return [songname, link, type]


@Zaid.on(events.callbackquery.CallbackQuery(data="cls"))
async def _(event):

     await event.delete()

btnn =[[Button.inline("✯ cʟᴏꜱᴇ ✯", data="cls")]]


#play
@Zaid.on(events.NewMessage(pattern="^[/?]play"))
@AssistantAdd
async def play(event):
    title = ' '.join(event.text[5:])
    replied = await event.get_reply_message()
    sender = await event.get_sender()
    chat = await event.get_chat()
    chat_id = event.chat_id
    from_user = vcmention(event.sender) 
    public = event.chat_id
    if (
        replied
        and not replied.audio
        and not replied.voice
        and not title
        or not replied
        and not title
    ):
        return await event.client.send_file(chat_id, Config.CMD_IMG, caption="**Provide some input to play your song**\n\n **Example**: `/play adiyee`", buttons=btnn)
    elif replied and not replied.audio and not replied.voice or not replied:
        botman = await event.reply("📝")
        query = event.text.split(maxsplit=1)[1]
        search = ytsearch(query)
        if search == 0:
            await botman.edit(
                "**Can't Find Song** Try searching with More Specific Title or try searching with full song name"
            )     
        else:
            songname = search[0]
            title = search[0]
            url = search[1]
            duration = search[2]
            thumbnail = search[3]
            videoid = search[4]
            userid = sender.id
            titlegc = chat.title
            ctitle = await CHAT_TITLE(titlegc)
            thumb = await gen_thumb(videoid)
            format = "best[height<=?720][width<=?1280]"
            try:
                ytlink = await ytdl(format, url)
            except:
                await botman.edit(f"Something Went Wrong, Kindly Check errors in terminal")
                return
            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                caption = f"**🌚 Requested Next Song #☱◜◝◟◡>** {pos}\n\n  **🚀 T𝐢𝐭𝐥𝐞 🚀** [{songname}]({url})\n🎧 T𝗂𝗺𝗲 𝓉𝗈 𝗛𝗲𝗮𝗋 🎧** {duration} ᴍɪɴᴜᴛᴇs\n🔹**𝒓𝑒𝓺𝓾𝑒𝓼𝓽𝑒𝒹 𝒯𝗈🔹 :\n**🌍 U𝗇𝗂𝗏𝑒𝗋𝗌𝑒 N𝑒𝓉𝗐𝗈𝗋𝗞𝗌 🌍"
                await botman.delete()
                await event.client.send_file(chat_id, thumb, caption=caption, buttons=btnn)
            else:
                try:
                    await call_py.join_group_call(
                        chat_id,
                        AudioPiped(
                            ytlink,
                        ),
                        stream_type=StreamType().pulse_stream,
                    )
                    add_to_queue(chat_id, songname, ytlink, url, "Audio", 0)
                    caption = f"</b>➜ ⚡ 𝐂Ø𝐍𝐍Ξ𝐂Ƭ𝐈Ø𝐍 | 𝙀𝙎ƬΛ𝐁𝐋Ɨ𝙎𝙃ΞĐ ⚡\n\n╌╌╌╌╌╌╌⑊◞◠◟╌╌╌></b>\n\n🌌 𝗙𝗿𝗼𝗺 𝗨𝗻𝗶𝘃𝗲𝗿𝘀𝗲 🌌\n\n✧ **Sᴏɴɢ Nᴀᴍᴇ ✦ :** [{songname}]({url})\n\n⏱ **⧖ T-Ƭᴀᴋᴇɴ ⧗ :** {duration} ᴍɪɴᴜᴛᴇs\n\n🥀 **>⚙️🧑‍💻 User :** {from_user}"
                    await botman.delete()
                    await event.client.send_file(chat_id, thumb, caption=caption, buttons=btnn)
                except Exception as ep:
                    clear_queue(chat_id)
                    await botman.edit(f"`{ep}`")

    else:
        botman = await event.reply("➕ Downloading File...")
        dl = await replied.download_media()
        link = f"https://t.me/c/{chat.id}/{event.reply_to_msg_id}"
        if replied.audio:
            songname = "Telegram Audio Note"
        elif replied.voice:
            songname = "Voice Note"
        if chat_id in QUEUE:
            pos = add_to_queue(chat_id, songname, dl, link, "Audio", 0)
            caption = f"🌚 Requested Next Song #☱◜◝◟◡> {pos}\n\n🎧 T𝗂𝗺𝗲 𝓉𝗈 𝗛𝗲𝗮𝗋 🎧 : [{songname}]({url})\n🔹**Ｓᴜɢɢᴇsᴛᴇᴅ🔹:** {from_user}"
            await event.client.send_file(chat_id, ngantri, caption=caption, buttons=btnn)
            await botman.delete()
        else:
            try:
                await call_py.join_group_call(
                    chat_id,
                    AudioPiped(
                        dl,
                    ),
                    stream_type=StreamType().pulse_stream,
                )
                add_to_queue(chat_id, songname, dl, link, "Audio", 0)
                caption = f"⚡ 𝐂Ø𝐍𝐍Ξ𝐂Ƭ𝐈Ø𝐍 | 𝙀𝙎ƬΛ𝐁𝐋Ɨ𝙎𝙃ΞĐ ⚡\n╌╌╌╌╌╌╌⑊◞◠◟╌╌╌>**\n\n✣ ✧Sᴏɴɢ Nᴀᴍᴇ ✦ :** [{songname}]({link})\n\n✣🔹**Ｓᴜɢɢᴇsᴛᴇᴅ🔹:** {from_user}"
                await event.client.send_file(chat_id, fotoplay, caption=caption, buttons=btnn)
                await botman.delete()
            except Exception as ep:
                clear_queue(chat_id)
                await botman.edit(f"`{ep}`")





#end

@Zaid.on(events.NewMessage(pattern="^[/?]end"))
@is_admin
async def vc_end(event, perm):
    chat_id = event.chat_id
    from_user = vcmention(event.sender)
    try:
        await call_py.leave_group_call(chat_id)
    except Exception:
        pass
    if chat_id in QUEUE:
        clear_queue(chat_id)
        await event.reply(f"<b>➤ ѕєє үσυ ηєχт тιмє ⌛| queries contact @universe_we_are<b>")
    else:
        await event.reply("**The music/video isn’t playing, Try playing any song /play song name ~**")


@Zaid.on(events.NewMessage(pattern="^[?/]vplay"))
@AssistantAdd
async def vplay(event):
    if Config.HEROKU_MODE == "ENABLE":
        await event.reply("__Currently Heroku Mode is ENABLED so You Can't Stream Video because Video Streaming Cause of Banning Your Heroku Account__.")
        return
    title = ' '.join(event.text[6:])
    replied = await event.get_reply_message()
    sender = await event.get_sender()
    userid = sender.id
    chat = await event.get_chat()
    titlegc = chat.title
    chat_id = event.chat_id
    public = event.chat_id
    from_user = vcmention(event.sender)
    if (
        replied
        and not replied.video
        and not replied.document
        and not title
        or not replied
        and not title
    ):
        return await event.client.send_file(chat_id, Config.CMD_IMG, caption="**Provide some input to play your song**\n\n **Example**: `/play adiyee`", buttons=btnn)
    if replied and not replied.video and not replied.document:
        xnxx = await event.reply("**» Getting your request > \n\nkindly wait for the response from the Universe 😈😈😈**")
        query = event.text.split(maxsplit=1)[1]
        search = ytsearch(query)
        RESOLUSI = 720
        hmmm = HighQualityVideo()
        if search == 0:
            await xnxx.edit(
                "**Give Me Valid Inputs**"
            )
        else:
            query = event.text.split(maxsplit=1)[1]
            search = ytsearch(query)
            songname = search[0]
            title = search[0]
            url = search[1]
            duration = search[2]
            thumbnail = search[3]
            videoid = search[4]
            ctitle = await CHAT_TITLE(titlegc)
            thumb = await gen_thumb(videoid)
            format = "best[height<=?720][width<=?1280]"
            try:
                ytlink = await ytdl(format, url)
            except:
                await xnxx.edit(f"Something Went Wrong, Kindly Check errors in terminal")
                return
            if chat_id in QUEUE:
                pos = add_to_queue(
                    chat_id, songname, ytlink, url, "Video", RESOLUSI)
                caption = f"**🌚 Requested Next Song #☱◜◝◟◡> {pos}\n\n**🚀 T𝐢𝐭𝐥𝐞 🚀 :** [{songname}]({url})\n\n🎧 T𝗂𝗺𝗲 𝓉𝗈 𝗛𝗲𝗮𝗋 🎧** {duration} ᴍɪɴᴜᴛᴇs\n🍼 **🔹𝒓𝑒𝓺𝓾𝑒𝓼𝓽𝑒𝒹 𝒯𝗈🔹 :\n**🌍 U𝗇𝗂𝗏𝑒𝗋𝗌𝑒 N𝑒𝓉𝗐𝗈𝗋𝗞𝗌 🌍"
                await xnxx.delete()
                await event.client.send_file(chat_id, thumb, caption=caption, buttons=btnn)
            else:
                try:
                    await call_py.join_group_call(
                        chat_id,
                        AudioVideoPiped(ytlink, HighQualityAudio(), hmmm),
                        stream_type=StreamType().pulse_stream,
                    )
                    add_to_queue(
                        chat_id,
                        songname,
                        ytlink,
                        url,
                        "Video",
                        RESOLUSI)
                    await xnxx.delete()
                    await event.client.send_file(event.chat_id,
                        f"➜⚡ 𝐂Ø𝐍𝐍Ξ𝐂Ƭ𝐈Ø𝐍 | 𝙀𝙎ƬΛ𝐁𝐋Ɨ𝙎𝙃ΞĐ ⚡\n╌╌╌╌╌╌╌⑊◞◠◟╌╌╌>\n\n🌌 𝗙𝗿𝗼𝗺 𝗨𝗻𝗶𝘃𝗲𝗿𝘀𝗲 🌌 \n\n**✧ Sᴏɴɢ Nᴀᴍᴇ ✦** [{songname}]({url})\n\n**⧖ T-Ƭᴀᴋᴇɴ ⧗** {duration} ᴍɪɴᴜᴛᴇs\n\n>⚙️🧑‍💻 User** {from_user}",
                        link_preview=False,
                    )
                except Exception as ep:
                    clear_queue(chat_id)
                    await xnxx.edit(f"`{ep}`")

    elif replied:
        xnxx = await event.reply("➕ **Downloading Replied File**")
        dl = await replied.download_media()
        link = f"https://t.me/c/{chat.id}/{event.reply_to_msg_id}"
        if len(event.text.split()) < 2:
            RESOLUSI = 720
        else:
            pq = event.text.split(maxsplit=1)[1]
            RESOLUSI = int(pq)
        if replied.video or replied.document:
            songname = "Telegram Video Player"
        if chat_id in QUEUE:
            pos = add_to_queue(chat_id, songname, dl, link, "Video", RESOLUSI)
            caption = f"**🌚 Requested Next Song #☱◜◝◟◡>** {pos}\n\n**🚀 T𝐢𝐭𝐥𝐞 🚀 :** [{songname}]({url})\n♀ **🔹Ｓᴜɢɢᴇsᴛᴇᴅ🔹** {from_user}"
            await event.client.send_file(chat_id, ngantri, caption=caption, buttons=btnn)
            await xnxx.delete()
        else:
            if RESOLUSI == 360:
                hmmm = LowQualityVideo()
            elif RESOLUSI == 480:
                hmmm = MediumQualityVideo()
            elif RESOLUSI == 720:
                hmmm = HighQualityVideo()
            try:
                await call_py.join_group_call(
                    chat_id,
                    AudioVideoPiped(dl, HighQualityAudio(), hmmm),
                    stream_type=StreamType().pulse_stream,
                )
                add_to_queue(chat_id, songname, dl, link, "Video", RESOLUSI)
                caption = f"➜⚡ 𝐂Ø𝐍𝐍Ξ𝐂Ƭ𝐈Ø𝐍 | 𝙀𝙎ƬΛ𝐁𝐋Ɨ𝙎𝙃ΞĐ ⚡\n╌╌╌╌╌╌╌⑊◞◠◟╌╌╌>\n\n✨ **ᴛɪᴛʟᴇ :** [{songname}]({link})\n🥀 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {from_user}"
                await xnxx.delete()
                await event.client.send_file(chat_id, fotoplay, caption=caption, buttons=btnn)
            except Exception as ep:
                clear_queue(chat_id)
                await xnxx.edit(f"`{ep}`")
    else:
        xnxx = await event.reply("**» Getting your request > \n\nkindly wait for the response from the Universe 😈😈😈**")
        query = event.text.split(maxsplit=1)[1]
        search = ytsearch(query)
        RESOLUSI = 720
        hmmm = HighQualityVideo()
        if search == 0:
            await xnxx.edit("**Unable To featch Query, try playing the full name of the song**")
        else:
            songname = search[0]
            title = search[0]
            url = search[1]
            duration = search[2]
            thumbnail = search[3]
            videoid = search[4]
            ctitle = await CHAT_TITLE(titlegc)
            thumb = await gen_thumb(videoid)
            format = "best[height<=?720][width<=?1280]"
            try:
                ytlink = await ytdl(format, url)
            except:
                await xnxx.edit(f"Something Went Wrong, Kindly Check errors in terminal")
                return 
            if chat_id in QUEUE:
                pos = add_to_queue(
                    chat_id, songname, ytlink, url, "Video", RESOLUSI)
                caption = f"🌚 Requested Next Song #☱◜◝◟◡> {pos}\n\n🚀 T𝐢𝐭𝐥𝐞 🚀 :** [{songname}]({url})\n**🎧 T𝗂𝗺𝗲 𝓉𝗈 𝗛𝗲𝗮𝗋 🎧 :** {duration} ᴍɪɴᴜᴛᴇs\n🍼 **🔹𝒓𝑒𝓺𝓾𝑒𝓼𝓽𝑒𝒹 𝒯𝗈🔹:** {from_user}"
                await xnxx.delete()
                await event.client.send_file(chat_id, thumb, caption=caption, buttons=btnn)
            else:
                try:
                    await call_py.join_group_call(
                        chat_id,
                        AudioVideoPiped(ytlink, HighQualityAudio(), hmmm),
                        stream_type=StreamType().pulse_stream,
                    )
                    add_to_queue(
                        chat_id,
                        songname,
                        ytlink,
                        url,
                        "Video",
                        RESOLUSI)
                    caption = f"➜ <b>⚡ 𝐂Ø𝐍𝐍Ξ𝐂Ƭ𝐈Ø𝐍 | 𝙀𝙎ƬΛ𝐁𝐋Ɨ𝙎𝙃ΞĐ ⚡\n╌╌╌╌╌╌╌⑊◞◠◟╌╌╌>\n\n✧ Sᴏɴɢ Nᴀᴍᴇ ✦:** [{songname}]({url})\n**⧖ T-Ƭᴀᴋᴇɴ ⧗:** {duration} ᴍɪɴᴜᴛᴇs\n>⚙️🧑‍💻 User:** {from_user}"
                    await xnxx.delete()
                    await event.client.send_file(chat_id, thumb, caption=caption, buttons=btnn)
                except Exception as ep:
                    clear_queue(chat_id)
                    await xnxx.edit(f"`{ep}`")




#playlist
@Zaid.on(events.NewMessage(pattern="^[?!/]playlist"))
@is_admin
async def vc_playlist(event, perm):
    chat_id = event.chat_id
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        if len(chat_queue) == 1:
            await event.reply(
                f"**� Music library:**\n• [{chat_queue[0][0]}]({chat_queue[0][2]}) | `{chat_queue[0][3]}`",
                link_preview=False,
            )
        else:
            PLAYLIST = f"** Music library:**\n**• [{chat_queue[0][0]}]({chat_queue[0][2]})** | `{chat_queue[0][3]}` \n\n**• Next on the live:**"
            l = len(chat_queue)
            for x in range(1, l):
                hmm = chat_queue[x][0]
                hmmm = chat_queue[x][2]
                hmmmm = chat_queue[x][3]
                PLAYLIST = PLAYLIST + "\n" + \
                    f"**#{x}** - [{hmm}]({hmmm}) | `{hmmmm}`"
            await event.reply(PLAYLIST, link_preview=False)
    else:
        await event.reply("**The music/video isn’t playing, Try playing any song /play song name ~**")






#leavevc
@Zaid.on(events.NewMessage(pattern="^[?/]leavevc"))
@is_admin
async def leavevc(event, perm):
    xnxx = await event.reply("|-𝗢n-𝗀𝗈𝗂𝗇𝗀-|")
    chat_id = event.chat_id
    from_user = vcmention(event.sender)
    if from_user:
        try:
            await call_py.leave_group_call(chat_id)
        except (NotInGroupCallError, NoActiveGroupCall):
            pass
        await xnxx.edit("**Forced from the voice chat** `{}`".format(str(event.chat_id)))
    else:
        await xnxx.edit(f"**Sorry {owner} not on Voice Chat**")



@Zaid.on(events.NewMessage(pattern="^[?/]skip"))
@is_admin
async def vc_skip(event, perm):
    chat_id = event.chat_id
    if len(event.text.split()) < 2:
        op = await skip_current_song(chat_id)
        if op == 0:
            await event.reply("<b>**➤ ѕєє үσυ ηєχт тιмє ⌛| queries contact @universe_we_are**<b>")
        elif op == 1:
            await event.reply("empty queue, leaving you | Byee-buyee 😒")
        else:
            await event.reply(
                f"**♬ Bypass**\n**🎧 Now streaming** - [{op[0]}]({op[1]})",
                link_preview=False,
            )
    else:
        skip = event.text.split(maxsplit=1)[1]
        DELQUE = "**deleting respected music From requested:**"
        if chat_id in QUEUE:
            items = [int(x) for x in skip.split(" ") if x.isdigit()]
            items.sort(reverse=True)
            for x in items:
                if x != 0:
                    hm = await skip_item(chat_id, x)
                    if hm != 0:
                        DELQUE = DELQUE + "\n" + f"**#{x}** - {hm}"
            await event.reply(DELQUE)


@Zaid.on(events.NewMessage(pattern="^[?/]pause"))
@is_admin
async def vc_pause(event, perm):
    chat_id = event.chat_id
    if chat_id in QUEUE:
        try:
            await call_py.pause_stream(chat_id)
            await event.reply("**| Stream frozen |**")
        except Exception as e:
            await event.reply(f"**ERROR:AREA51 - alert!!!** `{e}`")
    else:
        await event.reply("****The music/video isn’t playing, Try playing any song /play song name ~****")



@Zaid.on(events.NewMessage(pattern="^[?/]resume"))
@is_admin
async def vc_resume(event, perm):
    chat_id = event.chat_id
    if chat_id in QUEUE:
        try:
            await call_py.resume_stream(chat_id)
            await event.reply("**Streaming Started | on track**")
        except Exception as e:
            await event.reply(f"**ERROR:AREA51 - alert!!!** `{e}`")
    else:
        await event.reply("**The music/video isn’t playing, Try playing any song /play song name ~**")


@call_py.on_stream_end()
async def stream_end_handler(_, u: Update):
    chat_id = u.chat_id
    print(chat_id)
    await skip_current_song(chat_id)


@call_py.on_closed_voice_chat()
async def closedvc(_, chat_id: int):
    if chat_id in QUEUE:
        clear_queue(chat_id)
    if chat_id in active:
        active.remove(chat_id)


@call_py.on_left()
async def leftvc(_, chat_id: int):
    if chat_id in QUEUE:
        clear_queue(chat_id)
    if chat_id in active:
        active.remove(chat_id)


@call_py.on_kicked()
async def kickedvc(_, chat_id: int):
    if chat_id in QUEUE:
        clear_queue(chat_id)
    if chat_id in active:
        active.remove(chat_id)
