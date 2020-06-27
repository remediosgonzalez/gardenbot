from aiogram.types import ReplyKeyboardMarkup

from bot.sources.tools import replies

yes_or_no = ReplyKeyboardMarkup(resize_keyboard=True)
yes_or_no.add(replies.YES, replies.NO)
