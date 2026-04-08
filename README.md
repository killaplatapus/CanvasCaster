# CanvasCaster

Shows images from a Discord channel on a webpage. Simple as that.

## What You Need

- Python installed ([download here](https://www.python.org/downloads/))
- A Discord bot token
- A Discord server where you can add bots

---

## Step 1: Get Your Discord Bot Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **New Application** and give it a name (like "CanvasCaster")
3. Click **Bot** on the left sidebar
4. Click **Reset Token** and copy the token (it's a long string of letters and numbers)
5. **IMPORTANT:** Save this token somewhere safe! You'll need it later.
6. Scroll down to **Privileged Gateway Intents** section (at the bottom of the Bot page)
7. Turn ON these toggles:
   - **Message Content Intent**
   - **Server Members Intent**
   
   (If you don't see toggles, look for a text saying your bot needs verification - just scroll down more until you find them)

## Step 2: Add the Bot to Your Discord Server

1. In the Developer Portal, go to **OAuth2** > **URL Generator**
2. Check the boxes for `bot` and `applications.commands`
3. Copy the URL at the bottom
4. Paste that URL into your browser
5. Select your server and click **Authorize**

## Step 3: Get Your Channel ID

1. Open Discord
2. Click the **gear icon** (User Settings) at the bottom left
3. Go to **Advanced** and turn on **Developer Mode**
4. Right-click on the channel you want to monitor
5. Click **Copy Channel ID**

## Step 4: Set Up the Files

1. Download CanvasCaster from GitHub
2. Open the folder
3. Open a terminal in this folder:
   - **Windows:** Right-click inside the folder, select **Open in Terminal** or **Open PowerShell window here**
   - **Linux:** Right-click inside the folder, select **Open in Terminal**, or press `Ctrl + Alt + T` and `cd` to the folder
   - **Mac:** Open Terminal, type `cd `, drag the folder into the window, and press Enter
4. Type this and press Enter:
   ```
   pip install -r requirements.txt
   ```

## Step 5: Configure the Bot

1. In the CanvasCaster folder, find `config.example.json`
2. Make a copy and rename it to `config.json`:
   - **Windows:** Right-click the file, select **Copy**, then right-click and select **Paste**
   - **Linux/Mac:** Open terminal and type: `cp config.example.json config.json`
3. Open `config.json` in a text editor (like Notepad, nano, or vim)
4. Fill in your details:
   ```json
   {
       "token": "paste your bot token here",
       "channel_id": 123456789012345678,
       "port": 8765,
       "fetch_interval": 3600
   }
   ```
   - Replace the token with your bot token from Step 1
   - Replace the channel_id with the number you copied in Step 3
5. Save and close the file

## Step 6: Run It!

1. In the terminal, type:
   ```
   python canvas_caster.py
   ```
   - **Linux/Mac:** If that doesn't work, try: `python3 canvas_caster.py`
2. Press Enter
3. Wait a few seconds, then open your browser
4. Go to: `http://localhost:8765`

You should see images from your Discord channel!

---

## Troubleshooting

**"No images yet..."**
- Make sure your bot is in the server
- Make sure the channel_id in config.json is correct
- Try sending an image in that Discord channel

**"Module not found" error**
- Make sure you ran `pip install -r requirements.txt`
- **Linux/Mac:** Try `pip3 install -r requirements.txt`

**"pip" is not recognized**
- **Windows:** Use `py -m pip install -r requirements.txt`
- **Linux:** Install pip with `sudo apt install python3-pip` (Ubuntu/Debian) or `sudo dnf install python3-pip` (Fedora)

**Port already in use**
- Change `"port": 8765` to something else like `"port": 8080`
- Then visit `http://localhost:8080`

**Permission denied (Linux/Mac)**
- Make the script executable: `chmod +x canvas_caster.py`

## Need Help?

Open an issue on GitHub: https://github.com/thecosyplatypus/CanvasCaster/issues
