from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

from bot.sources.tools import replies

yes_or_no = ReplyKeyboardMarkup(resize_keyboard=True)
yes_or_no.add(replies.YES, replies.NO)

start_keyboard = InlineKeyboardMarkup()
# Callback data unhandled: deposit, cart
start_keyboard.add(InlineKeyboardButton(text='Shop', callback_data='buy_item'),
                   InlineKeyboardButton(text='Referrals', callback_data='referral'))
start_keyboard.add(InlineKeyboardButton(text='Shipping', callback_data='shipping_policy'),
                   InlineKeyboardButton(text='Support', callback_data='support'))

shop_keyboard = InlineKeyboardMarkup()
shop_keyboard.add(InlineKeyboardButton(text='Previous', callback_data='previous'),
                  InlineKeyboardButton(text='Next', callback_data='next'))
shop_keyboard.add(InlineKeyboardButton(text='Add to cart', callback_data='add_to_cart'))
shop_keyboard.add(InlineKeyboardButton(text='Check my cart', callback_data='cart'))

cart_keyboard = InlineKeyboardMarkup()
cart_keyboard.add(InlineKeyboardButton(text='Buy more', callback_data='buy_item'),
                  InlineKeyboardButton(text='Empty cart', callback_data='empty_cart'))
cart_keyboard.add(InlineKeyboardButton(text='Checkout', callback_data='checkout'))
