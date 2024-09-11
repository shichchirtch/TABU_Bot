from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.redis import RedisStorage, Redis, StorageKey
from config import settings

using_redis = Redis(host=settings.REDIS_HOST)
redis_storage = RedisStorage(redis=using_redis)

class FSM_ST(StatesGroup):
    after_start = State()
    alone = State()
    zusamm = State()
    admin = State()

scheduler = AsyncIOScheduler()

bot = Bot(token=settings.BOT_TOKEN,
              default=DefaultBotProperties(parse_mode=ParseMode.HTML))

bot_storage_key = StorageKey(bot_id=bot.id, user_id=bot.id, chat_id=bot.id)

dp = Dispatcher(storage=redis_storage)


