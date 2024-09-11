import asyncio
from command_handlers import ch_router
from callback_handlers import cb_router
from start_menu import set_main_menu
from bot_instance import bot, bot_storage_key, scheduler, dp
from postgress_table import init_models



async def main():
    await init_models()

    dp.startup.register(set_main_menu)
    await dp.storage.set_data(key=bot_storage_key, data={})
    await set_main_menu(bot)
    dp.include_router(ch_router)
    dp.include_router(cb_router)

    scheduler.start()
    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


asyncio.run(main())