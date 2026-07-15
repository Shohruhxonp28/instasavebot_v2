import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.config import BOT_TOKEN
from bot.database.db import init_db, close_db

from bot.handlers import start as start_handler
from bot.handlers import downloader as downloader_handler

from bot.admin import panel as admin_panel
from bot.admin import users as admin_users
from bot.admin import stats as admin_stats
from bot.admin import broadcast as admin_broadcast
from bot.admin import channels as admin_channels
from bot.admin import settings as admin_settings

logging.basicConfig(level=logging.INFO)


async def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not set. Please configure it in your .env file.")

    await init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Admin routers first so admin-only commands/callbacks take priority
    dp.include_router(admin_panel.router)
    dp.include_router(admin_users.router)
    dp.include_router(admin_stats.router)
    dp.include_router(admin_broadcast.router)
    dp.include_router(admin_channels.router)
    dp.include_router(admin_settings.router)

    # User-facing routers
    dp.include_router(start_handler.router)
    dp.include_router(downloader_handler.router)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Start bot polling as a background task
        polling_task = asyncio.create_task(dp.start_polling(bot))
        
        # Start dummy web server for Render Free Web Service
        from aiohttp import web
        import os
        
        async def health_check(request):
            return web.Response(text="Bot is running!")
            
        app = web.Application()
        app.router.add_get('/', health_check)
        runner = web.AppRunner(app)
        await runner.setup()
        port = int(os.environ.get("PORT", 10000))
        site = web.TCPSite(runner, '0.0.0.0', port)
        await site.start()
        
        logging.info(f"Dummy web server started on port {port}")
        
        # Wait for the bot polling task
        await polling_task
    finally:
        await close_db()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
