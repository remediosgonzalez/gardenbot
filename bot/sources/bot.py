import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from django.contrib.auth import get_user_model

import configs
from accounts.models import Account
from bot.sources.tools import replies, django_tools, bitcoin_tools, logging_tools, keyboards, states
from bot.sources.tools.django_tools import sync_to_async, sync_to_async_iterable
from bot.sources.tools.redis_storage import redis_storage
from shop.models import Item, Order
from users import models

User: models.User = get_user_model()


log = logging.getLogger('bot')
log.setLevel(logging.INFO)
logging_tools.setup()

bot = Bot(configs.BOT_TOKEN)

dp = Dispatcher(bot, storage=redis_storage)
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(commands=['start'])
async def start(msg: types.Message, *args, **kwargs):
    user, is_new = await django_tools.get_or_create_user(msg.from_user, return_tuple=True)
    user: User
    if msg.get_args().isdigit():
        if not is_new:
            await msg.reply(replies.NOT_A_NEW_USER, reply=False, reply_markup=ReplyKeyboardRemove())
            return
        if ref_user := await django_tools.user_get_if_exists(msg.get_args()):
            ref_user: User
            if user.is_referral_of_user:
                await msg.reply(replies.REFERRAL_ALREADY, reply=False, reply_markup=ReplyKeyboardRemove())
                return
            user.is_referral_of_user = ref_user
            await sync_to_async(user.save)()
            await msg.bot.send_message(ref_user.id,
                                       replies.REFERRAL_SUCCESS_TO_REF_USER.format(
                                           first_name=msg.from_user.first_name,
                                           last_name=msg.from_user.last_name,
                                       ))
    await msg.reply(replies.HELLO.format(network_name=configs.NETWORK), reply=False, reply_markup=ReplyKeyboardRemove())


@dp.message_handler(commands=['deposit'])
@django_tools.auth_user_decorator
async def deposit(msg: types.Message, user: User, *args, **kwargs):
    wallet = bitcoin_tools.create_or_open_wallet_for_user(user.id)
    address = bitcoin_tools.get_wallet_address(wallet)
    await msg.reply(replies.DEPOSIT, reply=False)
    await msg.reply(address, reply=False, reply_markup=ReplyKeyboardRemove())


# Adding item part
@dp.message_handler(state='*', commands=['add_item'])
@django_tools.auth_user_decorator
@django_tools.staff_account_required
async def add_item(msg: types.Message, user: User, *args, **kwargs):
    await msg.reply(replies.ASK_ITEM_NAME, reply=False, reply_markup=ReplyKeyboardRemove())
    await states.AddingItemStates.waiting_for_name.set()


@dp.message_handler(state=states.AddingItemStates.waiting_for_name, content_types=types.ContentTypes.TEXT)
async def add_item_name(msg: types.Message, state: FSMContext, *args, **kwargs):
    await state.update_data(name=msg.text)
    await msg.reply(replies.ASK_ITEM_DESCRIPTION, reply=False, reply_markup=ReplyKeyboardRemove())
    await states.AddingItemStates.waiting_for_description.set()


@dp.message_handler(state=states.AddingItemStates.waiting_for_description, content_types=types.ContentTypes.TEXT)
async def add_item_name(msg: types.Message, state: FSMContext, *args, **kwargs):
    await state.update_data(description=msg.text)
    await msg.reply(replies.ASK_ITEM_PRICE, reply=False, reply_markup=ReplyKeyboardRemove())
    await states.AddingItemStates.waiting_for_price.set()


@dp.message_handler(state=states.AddingItemStates.waiting_for_price, content_types=types.ContentTypes.TEXT)
async def add_item_name(msg: types.Message, state: FSMContext, *args, **kwargs):
    await state.update_data(price=msg.text)
    item_data = await state.get_data()
    await msg.reply(replies.ASK_ITEM_CONFIRMATION.format(**item_data), reply=False, reply_markup=keyboards.yes_or_no)
    await states.AddingItemStates.waiting_for_confirmation.set()


@dp.message_handler(state=states.AddingItemStates.waiting_for_confirmation, content_types=types.ContentTypes.TEXT)
@django_tools.auth_user_decorator
@django_tools.staff_account_required
async def add_item_name(msg: types.Message, user: User, state: FSMContext, *args, **kwargs):
    if msg.text.lower() == replies.YES.lower():
        item_data = await state.get_data()
        await sync_to_async(Item.objects.create)(**item_data, created_by_user=user)
        await msg.reply(replies.ADD_ITEM_SUCCESS, reply=False, reply_markup=ReplyKeyboardRemove())
    else:
        await msg.reply(replies.ADD_ITEM_ABORTED, reply=False, reply_markup=ReplyKeyboardRemove())
    await state.finish()


# Buying item part
@dp.message_handler(state='*', commands=['buy_item'])
async def buy_item(msg: types.Message, *args, **kwargs):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    async for item in sync_to_async_iterable(Item.objects.all()):
        keyboard.add(item.name)
    await msg.reply(replies.BUY_ASK_ITEM_NAME, reply=False, reply_markup=keyboard)
    await states.BuyingItemStates.waiting_for_item.set()


@dp.message_handler(state=states.BuyingItemStates.waiting_for_item, content_types=types.ContentTypes.TEXT)
async def confirm_buy_item(msg: types.Message, state: FSMContext, *args, **kwargs):
    if item := await sync_to_async(Item.objects.get)(name=msg.text):
        await msg.reply(replies.BUY_ITEM_CONFIRMATION.format(name=item.name, price=item.price),
                        reply=False, reply_markup=keyboards.yes_or_no)
        await state.update_data(item_id=item.id)
        await states.BuyingItemStates.waiting_for_confirmation.set()
    else:
        await msg.reply(replies.BUY_ITEM_NOT_FOUND.format(name=msg.text),
                        reply=False, reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state=states.BuyingItemStates.waiting_for_confirmation, content_types=types.ContentTypes.TEXT)
async def add_item_to_cart(msg: types.Message, state: FSMContext, *args, **kwargs):
    if msg.text.lower() == replies.YES.lower():
        user_data = await state.get_data()
        await state.update_data(cart=[*user_data.pop('cart', []), user_data.pop('item_id')], **user_data)
        await msg.reply(replies.BUY_ITEM_SUCCESS, reply=False, reply_markup=ReplyKeyboardRemove())
        await state.reset_state(with_data=False)
    else:
        await state.reset_state(with_data=False)
        await msg.reply(replies.BUY_ITEM_ABORTED, reply=False, reply_markup=ReplyKeyboardRemove())


# Cart part
@dp.message_handler(state='*', commands=['cart'])
async def get_cart(msg: types.Message, state: FSMContext, *args, **kwargs):
    user_data = await state.get_data()
    cart = user_data.get('cart', [])
    message = f'{replies.CART_REVIEW.format(n=len(cart))}\n\n'
    for n, item_id in enumerate(cart):
        item: Item = await sync_to_async(Item.objects.get)(id=item_id)
        message += f'{replies.CARD_ITEM.format(n=n+1, name=item.name, price=item.price)}\n'
    if message:
        await msg.reply(message, reply=False)
    await msg.reply(replies.EMPTY_CART_OR_CHECKOUT, reply=False, reply_markup=ReplyKeyboardRemove())


@dp.message_handler(state='*', commands=['empty_cart'])
async def empty_cart(msg: types.Message, state: FSMContext, *args, **kwargs):
    await state.update_data(cart=[])
    await msg.reply(replies.EMPTY_CART_SUCCESS, reply=False, reply_markup=ReplyKeyboardRemove())


# Checkout part
@dp.message_handler(state='*', commands=['checkout'])
async def checkout(msg: types.Message, state: FSMContext, *args, **kwargs):
    user_data = await state.get_data()
    cart = user_data.get('cart', [])
    if not cart:
        await msg.reply(replies.CART_IS_EMPTY, reply=False, reply_markup=ReplyKeyboardRemove())
        return
    await msg.reply(replies.ASK_FOR_ADDRESS, reply=False, reply_markup=ReplyKeyboardRemove())
    await states.CheckoutStates.waiting_for_address.set()


@dp.message_handler(state=states.CheckoutStates.waiting_for_address, content_types=types.ContentTypes.TEXT)
@django_tools.auth_user_decorator
async def set_address(msg: types.Message, user: User, state: FSMContext, *args, **kwargs):
    user_data = await state.get_data()
    cart = user_data.get('cart', [])
    n = 0
    total_price = 0
    for item_id in cart:
        item: Item = await sync_to_async(Item.objects.get)(id=item_id)
        n += 1
        total_price += item.price
    account = await sync_to_async(Account.objects.get)(user=user)
    await state.update_data(address=msg.text)
    await msg.reply(replies.ADDRESS_SET_ASK_PAYMENT_CONFIRM.format(total_price=total_price,
                                                                   n=n, balance=account.balance),
                    reply=False, reply_markup=keyboards.yes_or_no)
    await states.CheckoutStates.waiting_for_payment_confirmation.set()


@dp.message_handler(state=states.CheckoutStates.waiting_for_payment_confirmation, content_types=types.ContentTypes.TEXT)
@django_tools.auth_user_decorator
async def make_order(msg: types.Message, user: User, state: FSMContext, *args, **kwargs):
    user_data = await state.get_data()
    cart = user_data.get('cart', [])

    items = []
    total_price = 0
    for item_id in cart:
        item: Item = await sync_to_async(Item.objects.get)(id=item_id)
        items.append(item)
        total_price += item.price
    account = await sync_to_async(Account.objects.get)(user=user)
    if account.balance >= total_price:
        order = await sync_to_async(Order.objects.create)(user=user, items=items, address=user_data.get('address'))
        await msg.reply(replies.ORDER_SUCCESS.format(id=order.id), reply=False, reply_markup=ReplyKeyboardRemove())
        await state.finish()
    else:
        await msg.reply(replies.NOT_SUFFICIENT_FUNDS, reply=False, reply_markup=ReplyKeyboardRemove())
        await state.reset_state(with_data=False)


# Referral part
@dp.message_handler(state='*', commands=['referral'])
async def referral(msg: types.Message, *args, **kwargs):
    breakpoint()
    link = f'https://t.me/{(await bot.get_me()).username}?start={msg.from_user.id}'
    await msg.reply(replies.REFERRAL_LINK.format(link=link), reply=False, reply_markup=ReplyKeyboardRemove())


async def startup(dispatcher: Dispatcher):
    pass


async def shutdown(dispatcher: Dispatcher):
    pass
