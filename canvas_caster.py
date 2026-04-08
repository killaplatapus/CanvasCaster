import json
import discord
import datetime
import re
import asyncio
import random
from aiohttp import web

with open('config.json', 'r') as f:
    config = json.load(f)

TOKEN = config['token']
CHANNEL_ID = config['channel_id']
PORT = config['port']
FETCH_INTERVAL = config['fetch_interval']
IMAGE_DURATION = config.get('image_duration', 10)

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
client = discord.Client(intents=intents)
image_queue = []
current_index = 0
last_fetch_time = None


async def fetch_channel_images():
    global image_queue, last_fetch_time
    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        print("Channel not found")
        return

    images = []
    async for message in channel.history(limit=100):
        if message.attachments:
            images.extend([att.url for att in message.attachments if att.content_type and 'image' in att.content_type])
        images.extend(extract_images(message.content))

    image_queue = list(dict.fromkeys(images))
    last_fetch_time = datetime.datetime.now()
    print(f"Found {len(image_queue)} images in channel")


def extract_images(content):
    pattern = r"https?://[^\s<>\"']+(?:\.jpg|\.png|\.jpeg|\.gif|\.webp)"
    return re.findall(pattern, content, re.IGNORECASE)


async def rotate_image():
    global current_index
    if not image_queue:
        return
    current_index = (current_index + 1) % len(image_queue)
    print(f"Displaying image {current_index + 1}/{len(image_queue)}: {image_queue[current_index]}")


async def handler(request):
    global image_queue, current_index

    if not image_queue:
        html = """<!DOCTYPE html>
<html><head><title>Spelly Art</title></head>
<body style="margin:0;display:flex;justify-content:center;align-items:center;height:100vh;background:#000;color:#fff;font-family:sans-serif;">
<h1>No images yet...</h1>
</body></html>"""
    else:
        image_url = image_queue[current_index]
        html = f"""<!DOCTYPE html>
<html>
<head>
<title>CanvasCaster</title>
<meta http-equiv="refresh" content="600">
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ display: flex; justify-content: center; align-items: center; min-height: 100vh; background: #000; }}
    img {{ max-width: 1920px; max-height: 1080px; object-fit: contain; }}
</style>
</head>
<body><img src="{image_url}" alt="CanvasCaster"></body>
</html>"""

    return web.Response(text=html, content_type='text/html')


async def start_server():
    app = web.Application()
    app.router.add_get('/', handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', PORT)
    await site.start()
    print(f"Server running at http://localhost:{PORT}")


def reload_config():
    with open('config.json', 'r') as f:
        return json.load(f)


async def rotation_loop():
    global last_fetch_time
    while True:
        config = reload_config()
        image_duration = config.get('image_duration', 10)
        await asyncio.sleep(image_duration)
        current_time = datetime.datetime.now()
        fetch_interval = config.get('fetch_interval', 300)
        if last_fetch_time and (current_time - last_fetch_time).total_seconds() >= fetch_interval:
            await fetch_channel_images()
        if image_queue:
            await rotate_image()


@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    await fetch_channel_images()
    await start_server()
    asyncio.create_task(rotation_loop())


@client.event
async def on_message(message):
    if message.channel.id == CHANNEL_ID:
        images = []
        if message.attachments:
            images.extend([att.url for att in message.attachments if att.content_type and 'image' in att.content_type])
        images.extend(extract_images(message.content))

        for img in images:
            if img not in image_queue:
                image_queue.insert(0, img)
                print(f"New image added: {img}")


client.run(TOKEN)
