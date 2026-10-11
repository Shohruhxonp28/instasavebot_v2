# Telegram Media Downloader Bot

A powerful and clean Telegram bot built with **Aiogram 3.x** and **universalDownloader (Node.js)** that downloads videos, photos, carousels, and audios from:
- **Instagram** (Reels, Posts, Carousel albums)
- **Pinterest** (Images, Videos)
- **TikTok & Douyin** (Watermark-free videos & photos)
- **Threads** (Photos & Videos)
- **Spotify & SoundCloud** (Audio tracks)
- **Snapchat & CapCut** (Videos)
- **TeraBox** (Direct files & videos)
- **YouTube, Facebook, Twitter (X)**
- **Reddit, Bluesky, Dailymotion, Tumblr, LinkedIn**

Also automatically recognizes background music in videos using **FFmpeg** + **ACRCloud**.

## Features

- `/start` welcome message with supported platforms
- Mandatory channel subscription (with a "✅ Check Subscription" button)
- Multi-platform media downloading (yt-dlp + universalDownloader hybrid engine)
- Music recognition via ACRCloud after each download
- Full in-Telegram admin panel (`/admin`):
  - 👥 Users (view total, search by ID, block/unblock)
  - 📊 Statistics (users, downloads per platform, recognitions)
  - 📢 Broadcast Message (text/photo/video/animation/document, with preview & confirm)
  - 📺 Required Channels (add/remove/enable/disable)
  - 👑 Admin Settings (toggle mandatory subscription, view admin IDs)

## Project Structure

```text
project/
│
├── bot/
│   ├── handlers/       # user-facing handlers (start, downloader)
│   ├── admin/          # admin panel handlers
│   ├── keyboards/      # inline keyboard builders
│   ├── services/       # yt-dlp, universalDownloader bridge, ACRCloud
│   ├── database/       # SQLite connection + queries
│   ├── utils/          # FSM states, admin filter
│   ├── config.py       # environment-based configuration
│   └── main.py         # entry point
│
├── universalDownloader/ # Node.js multi-platform downloader engine
│   ├── services/       # platform scrapers (Threads, Spotify, CapCut, etc.)
│   ├── controllers/    # API controllers
│   ├── routes/         # Express routes
│   ├── cli.js          # CLI bridge for Python integration
│   └── index.js        # standalone Express API server
│
├── downloads/          # temporary downloaded files (auto-cleaned)
├── media/              # temporary extracted audio (auto-cleaned)
├── requirements.txt
├── .env.example
└── README.md
```

## Requirements

- Python 3.11+
- FFmpeg installed and available on your system `PATH`
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- An ACRCloud account with an Identify project ([console.acrcloud.com](https://console.acrcloud.com))

## Setup

1. **Clone/copy the project** and enter its folder.

2. **Install FFmpeg** (if not already installed):
   ```bash
   # Ubuntu/Debian
   sudo apt install ffmpeg

   # macOS
   brew install ffmpeg
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and fill in:
   - `BOT_TOKEN` — from @BotFather
   - `ADMIN_IDS` — your Telegram user ID(s), comma-separated
   - `ACR_HOST`, `ACR_ACCESS_KEY`, `ACR_ACCESS_SECRET` — from your ACRCloud console

5. **Run the bot:**
   ```bash
   python -m bot.main
   ```

The SQLite database file (and its tables) will be created automatically on first run.

## Setting Up Required Channels

1. Add your bot as an **administrator** to the channel(s) you want to require.
2. In Telegram, send `/admin` to the bot (must be one of the IDs in `ADMIN_IDS`).
3. Go to **📺 Required Channels → ➕ Add channel**, then send the channel's
   `@username` or numeric ID.

If no required channels are configured (or mandatory subscription is disabled in
**Admin Settings**), any user can use the bot immediately.

## Notes

- Telegram bots can only upload files up to **50 MB** directly. Videos larger
  than `MAX_VIDEO_SIZE_MB` (set in `.env`) will not be downloaded.
- Downloaded videos and extracted audio clips are deleted right after each
  request completes — nothing is kept on disk long-term.
- Broadcast history is intentionally **not saved**, per design.
- To switch to PostgreSQL, replace the `aiosqlite` connection in
  `bot/database/db.py` with an `asyncpg`/`databases` equivalent — the query
  functions in `bot/database/requests.py` are written in plain SQL and only
  need minor placeholder syntax changes (`?` → `$1`, etc.).
