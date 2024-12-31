import os
import random
import re
import textwrap
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps, ImageChops
from youtubesearchpython.__future__ import VideosSearch

YOUTUBE_IMG_URLS = []

FRIENDSHIP_QUOTES = [
    "A friend is someone who knows all about you and still loves you.",
    "Friendship is the only cement that will ever hold the world together.",
    "Friends are the siblings we choose for ourselves."
]

LOVE_QUOTES = [
    "Love is composed of a single soul inhabiting two bodies.",
    "The best thing to hold onto in life is each other.",
    "You know you're in love when you can't fall asleep because reality is finally better than your dreams."
]

MOTIVATION_QUOTES = [
    "Don't watch the clock; do what it does. Keep going.",
    "The harder you work for something, the greater you'll feel when you achieve it.",
    "Believe you can and you're halfway there."
]

COMEDY_QUOTES = [
    "I'm not arguing, I'm just explaining why I'm right.",
    "I finally realized that people are prisoners of their phones... that's why it's called a 'cell' phone.",
    "Some people graduate with honors, I am just honored to graduate."
]

RANDOM_URLS = [
    "https://telegra.ph/file/95d96663b73dbf278f28c.jpg",
    "https://telegra.ph/file/2d541313460e3e10742c3.jpg",
    "https://telegra.ph/file/5c3b30c9f2b1e6a35e0a2.jpg",
    "https://telegra.ph/file/3f5d8071a2b4b3f57d8c9.jpg"
]

YOUTUBE_IMG_URLS.extend(RANDOM_URLS)
RANDOM_QUOTES = FRIENDSHIP_QUOTES + LOVE_QUOTES + MOTIVATION_QUOTES + COMEDY_QUOTES

files = [f[:-4] for f in os.listdir("./thumbnail") if f.endswith("png")]

async def fetch_lyrics(videoid):
    lyrics = [
        "In the end, we are one.",
        "Lost in the music of time.",
        "Feel the rhythm of the night.",
        "Chasing dreams in the dark."
    ]
    return random.choice(lyrics)

async def fetch_quote():
    return random.choice(RANDOM_QUOTES)

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

async def gen_thumb(videoid):
    anime = random.choice(files)
    if os.path.isfile(f"cache/{videoid}_{anime}.png"):
        return f"cache/{videoid}_{anime}.png"
    
    url = f"https://www.youtube.com/watch?v={videoid}"
    random_img_url = random.choice(YOUTUBE_IMG_URLS)

    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            title = re.sub("\\W+", " ", result.get("title", "Unsupported Title")).title()
            duration = result.get("duration", "Unknown")
            thumbnail = result.get("thumbnails", [{}])[0].get("url", random_img_url).split("?")[0]

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
        logo = youtube.crop((Xcenter - 250, Ycenter - 250, Xcenter + 250, Ycenter + 250))
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

        for i, line in enumerate(para[:2]):
            text_w, _ = draw.textsize(line, font=font)
            draw.text(((1280 - text_w)/2, 530 + i * 50), line, fill="white", font=font)

        lyrics = await fetch_lyrics(videoid)
        text_w, _ = draw.textsize(lyrics, font=arial)
        draw.text(((1280 - text_w)/2, 700), lyrics, fill="yellow", font=arial)

        quote = await fetch_quote()
        text_w, _ = draw.textsize(quote, font=arial)
        draw.text(((1280 - text_w)/2, 750), quote, fill="cyan", font=arial)

        text_w, _ = draw.textsize(f"Duration: {duration} Mins", font=arial)
        draw.text(((1280 - text_w)/2, 660), f"Duration: {duration} Mins", fill="white", font=arial)

        background.save(f"cache/{videoid}_{anime}.png")
        return f"cache/{videoid}_{anime}.png"

    except Exception as e:
        print(e)
        return random_img_url
