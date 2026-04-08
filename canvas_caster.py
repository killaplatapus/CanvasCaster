import json
import discord
import datetime
import re
import asyncio
from aiohttp import web

IMAGE_PATTERN = re.compile(r"https?://[^\s<>\"']+(?:\.jpg|\.png|\.jpeg|\.gif|\.webp)", re.IGNORECASE)
ARTIST_PATTERN = re.compile(r"artist:\s*(\S+)", re.IGNORECASE)

with open('config.json', 'r') as f:
    config = json.load(f)

TOKEN = config['token']
CHANNEL_ID = config['channel_id']
PORT = config['port']

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
client = discord.Client(intents=intents)
image_queue = []
artist_names = {}
current_index = 0
last_fetch_time = None
_cached_html = None
_cached_html_index = -1
_cached_config = None
_cached_config_time = None


def get_config():
    global _cached_config, _cached_config_time
    current_time = datetime.datetime.now()
    if _cached_config is None or _cached_config_time is None or (current_time - _cached_config_time).total_seconds() > 60:
        with open('config.json', 'r') as f:
            _cached_config = json.load(f)
        _cached_config_time = current_time
    return _cached_config


def extract_artist_name(content):
    match = ARTIST_PATTERN.search(content)
    return match.group(1) if match else None


async def fetch_channel_images():
    global image_queue, last_fetch_time, artist_names
    channel = client.get_channel(CHANNEL_ID)
    if not channel:
        print("Channel not found")
        return

    images = []
    async for message in channel.history(limit=100):
        artist_name = extract_artist_name(message.content)
        if message.attachments:
            for att in message.attachments:
                if att.content_type and 'image' in att.content_type:
                    img_url = att.url
                    images.append(img_url)
                    if artist_name:
                        artist_names[img_url] = artist_name
        for img in IMAGE_PATTERN.findall(message.content):
            if img not in images:
                images.append(img)
                if artist_name:
                    artist_names[img] = artist_name

    image_queue = list(dict.fromkeys(images))
    last_fetch_time = datetime.datetime.now()
    print(f"Found {len(image_queue)} images in channel")


async def rotate_image():
    global current_index
    if not image_queue:
        return
    current_index = (current_index + 1) % len(image_queue)
    print(f"Displaying image {current_index + 1}/{len(image_queue)}: {image_queue[current_index]}")


async def handler(request):
    global image_queue, current_index, artist_names, _cached_html, _cached_html_index

    config = get_config()
    width = config.get('width', 1920)
    height = config.get('height', 1080)
    text_size = config.get('text_size', 40)
    text_color = config.get('text_color', '#fff')

    if not image_queue:
        return web.Response(text="""<!DOCTYPE html>
<html><head><title>Spelly Art</title></head>
<body style="margin:0;display:flex;justify-content:center;align-items:center;height:100vh;background:#000;color:#fff;font-family:sans-serif;">
<h1>No images yet...</h1>
</body></html>""", content_type='text/html')

    if _cached_html_index != current_index:
        current_image = image_queue[current_index]
        current_artist = artist_names.get(current_image)
        artist_text = f"CREATED BY: {current_artist}" if current_artist else ""
        artist_html = f'<div id="artist-name">{artist_text}</div>' if current_artist else ''
        _cached_html = f"""<!DOCTYPE html>
<html>
<head>
<title>CanvasCaster</title>
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ display: flex; justify-content: center; align-items: center; width: {width}px; height: {height}px; background: #000; position: relative; overflow: hidden; }}
    img {{ max-width: {width}px; max-height: {height}px; object-fit: contain; }}
    #artist-name {{
        position: absolute;
        bottom: 20px;
        right: 20px;
        background: rgba(0, 0, 0, 0.7);
        color: {text_color};
        padding: 8px 16px;
        font-family: 'Roboto', sans-serif;
        font-size: {text_size}px;
        border-radius: 4px;
        text-transform: uppercase;
    }}
</style>
</head>
<body>
<img id="canvas-img" alt="CanvasCaster">
{artist_html}
<script>
    async function update() {{
        try {{
            const res = await fetch('/status');
            const data = await res.json();
            const img = document.getElementById('canvas-img');
            const artistDiv = document.getElementById('artist-name');
            if (data.image && data.image + '?t=' + Date.now() !== img.src) {{
                img.src = data.image + '?t=' + Date.now();
                if (artistDiv && data.artist) {{
                    artistDiv.textContent = data.artist;
                    artistDiv.style.display = 'block';
                }} else if (artistDiv) {{
                    artistDiv.style.display = 'none';
                }}
            }}
            setTimeout(update, 5000);
        }} catch (e) {{
            setTimeout(update, 10000);
        }}
    }}
    update();
</script>
</body>
</html>"""
        _cached_html_index = current_index

    return web.Response(text=_cached_html, content_type='text/html')


async def status_handler(request):
    global image_queue, current_index, artist_names
    config = get_config()
    current_image = image_queue[current_index] if image_queue else None
    current_artist = artist_names.get(current_image)
    data = {
        'image': current_image,
        'artist': f"CREATED BY: {current_artist}" if current_artist else None,
        'image_duration': config.get('image_duration', 600)
    }
    return web.json_response(data)


async def start_server():
    app = web.Application()
    app.router.add_get('/', handler)
    app.router.add_get('/status', status_handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', PORT)
    await site.start()
    print(f"Server running at http://localhost:{PORT}")


async def rotation_loop():
    while True:
        config = get_config()
        cycle_time = config.get('image_duration', 600)
        await asyncio.sleep(cycle_time)
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
        artist_name = extract_artist_name(message.content)
        images = []
        if message.attachments:
            images.extend([att.url for att in message.attachments if att.content_type and 'image' in att.content_type])
        images.extend(IMAGE_PATTERN.findall(message.content))

        for img in images:
            if img not in image_queue:
                image_queue.insert(0, img)
                if artist_name:
                    artist_names[img] = artist_name
                print(f"New image added: {img}")


client.run(TOKEN)
