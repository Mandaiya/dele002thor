import os
import re
import textwrap
 
import random
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps, ImageChops
from youtubesearchpython.__future__ import VideosSearch
 
MUSIC_BOT_NAME = "S-V-D Music"
YOUTUBE_IMG_URLS = [
    "https://telegra.ph/file/8e5a832da78d9cdc5472f.jpg",
    "https://telegra.ph/file/6db754de9707eee737345.mp4",
    "https://telegra.ph/file/ecc9233d3f09286fa560a.mp4",
    "https://telegra.ph/file/0bc40f80a86e4d5e4927c.mp4"
]
files = [] 

for filename in os.listdir("./thumbnail"): 
     if filename.endswith("png"): 
         files.append(filename[:-4])
 
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage
 
 
def add_corners(im):
    bigsize = (im.size[0] * 3, im.size[1] * 3)
    mask = Image.new('L', bigsize, 0)
    ImageDraw.Draw(mask).ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(im.size, Image.ANTIALIAS)
    mask = ImageChops.darker(mask, im.split()[-1])
    im.putalpha(mask)
 
 
async def fetch_lyrics(videoid):
    # Mock lyrics for demonstration
    lyrics = [
        "In the end, we are one.",
        "Lost in the music of time.",
        "Feel the rhythm of the night.",
        "Chasing dreams in the dark."
    ]
    return random.choice(lyrics)

async def gen_thumb(videoid):
    anime = random.choice(files)
    if os.path.isfile(f"cache/{videoid}_{anime}.png"):
        return f"cache/{videoid}_{anime}.png"
    
    url = f"https://www.youtube.com/watch?v={videoid}"
    random_img_url = random.choice(YOUTUBE_IMG_URLS)  # Randomly select a YouTube image

    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            try:
                title = result["title"]
                title = re.sub("\\W+", " ", title)
                title = title.title()
            except:
                title = "Unsupported Title"
            try:
                duration = result["duration"]
            except:
                duration = "Unknown"
            
            try:
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            except:
                thumbnail = random_img_url  # Fallback to random URL if no thumbnail found

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()
                else:
                    async with session.get(random_img_url) as resp:
                        if resp.status == 200:
                            f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                            await f.write(await resp.read())
                            await f.close()

        youtube = Image.open(f"cache/thumb{videoid}.png")
        bg = Image.open(f"thumbnail/{anime}.png")
        image1 = changeImageSize(1280, 720, youtube)
        image2 = image1.convert("RGBA")
        background = image2.filter(filter=ImageFilter.BoxBlur(30))
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(1.5)
        cir = Image.open(f"thumbnail/IMG_20221129_201846_195.png") 
        image3 = changeImageSize(1280, 720, bg)
        circle = changeImageSize(1280, 720, cir)
        image5 = image3.convert("RGBA")
        Image.alpha_composite(background, image5).save(f"cache/temp{videoid}.png")

        Xcenter = youtube.width / 2
        Ycenter = youtube.height / 2
        x1 = Xcenter - 250
        y1 = Ycenter - 250
        x2 = Xcenter + 250
        y2 = Ycenter + 250
        logo = youtube.crop((x1, y1, x2, y2))
        logo.thumbnail((520, 520), Image.ANTIALIAS)
        logo.save(f"cache/chop{videoid}.png")

        if not os.path.isfile(f"cache/cropped{videoid}.png"):
            im = Image.open(f"cache/chop{videoid}.png").convert('RGBA')
            add_corners(im)
            im.save(f"cache/cropped{videoid}.png")

        crop_img = Image.open(f"cache/cropped{videoid}.png")
        logo = crop_img.convert("RGBA")
        logo.thumbnail((365, 365), Image.ANTIALIAS)
        width = int((1280 - 365)/ 2)
        background = Image.open(f"cache/temp{videoid}.png")
        background.paste(logo, (width + 2, 134), mask=logo)
        background.paste(circle, mask=circle)
        draw = ImageDraw.Draw(background)
        font = ImageFont.truetype("thumbnail/font2.ttf", 45)
        arial = ImageFont.truetype("thumbnail/font2.ttf", 30)
        para = textwrap.wrap(title, width=32)

        try:
            if para[0]:
                text_w, text_h = draw.textsize(f"{para[0]}", font=font)
                draw.text(((1280 - text_w)/2, 530), f"{para[0]}", fill="white", font=font)
            if para[1]:
                text_w, text_h = draw.textsize(f"{para[1]}", font=font)
                draw.text(((1280 - text_w)/2, 580), f"{para[1]}", fill="white", font=font)
        except:
            pass

        # Add lyrics
        lyrics = await fetch_lyrics(videoid)
        text_w, text_h = draw.textsize(lyrics, font=arial)
        draw.text(((1280 - text_w)/2, 700), lyrics, fill="yellow", font=arial)

        text_w, text_h = draw.textsize(f"Duration: {duration} Mins", font=arial)
        draw.text(((1280 - text_w)/2, 660), f"Duration: {duration} Mins", fill="white", font=arial)

        background.save(f"cache/{videoid}_{anime}.png")
        return f"cache/{videoid}_{anime}.png"

    except Exception as e:
        print(e)
        return random_img_url

