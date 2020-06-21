import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware

import configs
from bot.sources.tools.redis_storage import redis_storage

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(name)s |  %(levelname)s: %(message)s')
log = logging.getLogger()
log.setLevel(logging.INFO)

bot = Bot(configs.BOT_TOKEN)

dp = Dispatcher(bot, storage=redis_storage)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['start'])
async def start_downloading_books(msg: types.Message):
    await msg.reply('Simple reply')


async def startup(dispatcher: Dispatcher):
    pass


async def shutdown(dispatcher: Dispatcher):
    pass
