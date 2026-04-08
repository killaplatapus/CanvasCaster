# Spelly Art Bot

A Discord bot that displays images from a channel on a local web server, rotating through them automatically.

## Setup

### 1. Create a Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and name it
3. Go to "Bot" and click "Reset Token" to get your token
4. Enable these intents under "Privileged Gateway Intents":
   - **Message Content Intent**
   - **Server Members Intent**

### 2. Add Bot to Your Server

1. Go to "OAuth2" > "OAuth2 URL Generator"
2. Select scopes: `bot` and `applications.commands`
3. Copy the generated URL
4. Visit the URL and select your server

### 3. Configure the Bot

```bash
# Install dependencies
pip install discord aiohttp

# Copy the example config
copy config.example.json config.json
```

Edit `config.json`:
```json
{
    "token": "YOUR_BOT_TOKEN_HERE",
    "channel_id": 123456789012345678,
    "port": 8765,
    "fetch_interval": 3600
}
```

**Find your Channel ID:** Enable Developer Mode in Discord settings, then right-click your channel and select "Copy Channel ID"

### 4. Run the Bot

```bash
python spellyart.py
```

The web server will be available at `http://localhost:8765`

## Configuration Options

| Setting | Description | Default |
|---------|-------------|---------|
| `token` | Your Discord bot token | Required |
| `channel_id` | Discord channel to monitor | Required |
| `port` | Web server port | 8765 |
| `fetch_interval` | Seconds between channel fetches | 3600 |

## Features

- Monitors a Discord channel for images
- Displays images on a local web page
- Auto-rotates through images every 10 seconds
- Supports image attachments and image URLs in messages
