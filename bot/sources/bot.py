import logging
from urllib.parse import quote

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, \
    InputMediaPhoto
from django.contrib.auth import get_user_model
from django.utils import timezone

import configs
from accounts.models import Account
from bot.sources.tools import replies, django_tools, bitcoin_tools, logging_tools, keyboards, states
from bot.sources.tools.django_tools import sync_to_async
from shop.models import Item, Order, OrderItem, ShippingPolicy
from support.models import SupportTicket
from users import models

User: models.User = get_user_model()

log = logging.getLogger('bot')
log.setLevel(logging.INFO)
logging_tools.setup()

bot = Bot(configs.BOT_TOKEN)

dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())


@dp.message_handler(state='*', commands=['start'])
async def start(msg: types.Message, state: FSMContext, *args, **kwargs):
    user, is_new = await django_tools.get_or_create_user(msg.from_user, return_tuple=True)
    user: User
    if msg.get_args().isdigit():
        if not is_new:
            await msg.reply(replies.NOT_A_NEW_USER, reply=False, reply_markup=ReplyKeyboardRemove())
            return
        if ref_user := await django_tools.user_get_if_exists(msg.get_args()):
            user.is_referral_of_user = ref_user
            await sync_to_async(user.save)()
            await msg.bot.send_message(ref_user.id,
                                       replies.REFERRAL_SUCCESS_TO_REF_USER.format(
                                           first_name=msg.from_user.first_name,
                                           last_name=msg.from_user.last_name,
                                       ))
    await state.reset_state(with_data=False)
    await msg.reply(replies.HELLO.format(network_name=configs.NETWORK), reply=False,
                    reply_markup=keyboards.start_keyboard)


@dp.callback_query_handler(lambda query: query.data == 'deposit', state='*')
@django_tools.auth_user_decorator
async def deposit(query: types.CallbackQuery, user: User, *args, **kwargs):
    await query.message.reply(replies.GENERATING_ADDRESS, reply=False)
    wallet = bitcoin_tools.create_or_open_wallet_for_user(user.id)
    address = bitcoin_tools.get_wallet_address(wallet)
    await query.message.reply(replies.DEPOSIT, reply=False)
    await query.message.reply(address, reply=False, reply_markup=ReplyKeyboardRemove())
    await query.answer()


# Adding item part
@dp.message_handler(state='*', commands=['add_item'])
@django_tools.auth_user_decorator
@django_tools.staff_account_required
async def add_item(msg: types.Message, user: User, *args, **kwargs):
    await msg.reply(replies.ASK_ITEM_NAME, reply=False, reply_markup=ReplyKeyboardRemove())
    await states.AddingItemStates.waiting_for_name.set()


@dp.message_handler(lambda msg: not msg.text.startswith('/'),
                    state=states.AddingItemStates.waiting_for_name, content_types=types.ContentTypes.TEXT)
async def add_item_name(msg: types.Message, state: FSMContext, *args, **kwargs):
    await state.update_data(name=msg.text)
    await msg.reply(replies.ASK_ITEM_DESCRIPTION, reply=False, reply_markup=ReplyKeyboardRemove())
    await states.AddingItemStates.waiting_for_description.set()


@dp.message_handler(lambda msg: not msg.text.startswith('/'),
                    state=states.AddingItemStates.waiting_for_description, content_types=types.ContentTypes.TEXT)
async def add_item_name(msg: types.Message, state: FSMContext, *args, **kwargs):
    await state.update_data(description=msg.text)
    await msg.reply(replies.ASK_ITEM_PRICE, reply=False, reply_markup=ReplyKeyboardRemove())
    await states.AddingItemStates.waiting_for_price.set()


@dp.message_handler(lambda msg: not msg.text.startswith('/'),
                    state=states.AddingItemStates.waiting_for_price, content_types=types.ContentTypes.TEXT)
async def add_item_name(msg: types.Message, state: FSMContext, *args, **kwargs):
    if not msg.text.isdigit():
        await msg.reply('Please send a digit', reply=False)
    await state.update_data(price=msg.text)
    await msg.reply(replies.ASK_ITEM_PHOTO, reply=False, reply_markup=ReplyKeyboardRemove())
    await states.AddingItemStates.waiting_for_photo.set()


@dp.message_handler(state=states.AddingItemStates.waiting_for_photo, content_types=types.ContentTypes.PHOTO)
async def add_item_photo(msg: types.Message, state: FSMContext, *args, **kwargs):
    await state.update_data(photo_file_id=msg.photo[0].file_id)
    item_data = await state.get_data()
    await msg.reply(replies.ASK_ITEM_CONFIRMATION.format(**item_data), reply=False, reply_markup=keyboards.yes_or_no)
    await states.AddingItemStates.waiting_for_confirmation.set()


@dp.message_handler(lambda msg: not msg.text.startswith('/'),
                    state=states.AddingItemStates.waiting_for_confirmation, content_types=types.ContentTypes.TEXT)
@django_tools.auth_user_decorator
@django_tools.staff_account_required
async def add_item_name(msg: types.Message, user: User, state: FSMContext, *args, **kwargs):
    if msg.text.lower() == replies.YES.lower():
        item_data = await state.get_data()
        await sync_to_async(Item.objects.create)(name=item_data.get('name'),
                                                 description=item_data.get('description'),
                                                 price=item_data.get('price'),
                                                 photo_file_id=item_data.get('photo_file_id'),
                                                 created_by_user=user)
        await msg.reply(replies.ADD_ITEM_SUCCESS, reply=False, reply_markup=ReplyKeyboardRemove())
    else:
        await msg.reply(replies.ADD_ITEM_ABORTED, reply=False, reply_markup=ReplyKeyboardRemove())
    await state.finish()


# Buying item part
@dp.callback_query_handler(lambda query: query.data == 'buy_item', state='*')
async def buy_item(query: types.CallbackQuery, state: FSMContext, *args, **kwargs):
    item = await sync_to_async((await sync_to_async(Item.objects.filter)(disabled=False)).first)()
    if not item:
        await query.answer(replies.NO_ITEMS_IN_SHOP)
        return
    message = replies.ITEM_DESCRIPTION.format(name=item.name, description=item.description,
                                              price=item.price)
    if item.photo_file_id:
        await query.message.reply_photo(item.photo_file_id, message,
                                        reply_markup=keyboards.shop_keyboard, reply=False)
    else:
        await query.message.reply(message, reply=False, reply_markup=keyboards.shop_keyboard)
    await state.update_data(item_id=item.id)
    await query.answer()


@dp.callback_query_handler(lambda query: query.data == 'previous' or query.data == 'next', state='*')
async def prev_or_next(query: types.CallbackQuery, state: FSMContext, *args, **kwargs):
    current_item_id = (await state.get_data()).get('item_id')
    first_item = await sync_to_async(Item.objects.first)()
    last_item = await sync_to_async(Item.objects.last)()
    while True:
        current_item_id = current_item_id - 1 if query.data == 'previous' else current_item_id + 1
        try:
            item = await sync_to_async(Item.objects.get)(id=current_item_id)
            if not item.disabled:
                break
        except Item.DoesNotExist:
            if (current_item_id < first_item.id and query.data == 'previous') or \
                    (current_item_id > last_item.id and query.data == 'next'):
                await query.answer('Reached the end of list')
                return

    await query.message.edit_media(InputMediaPhoto(item.photo_file_id,
                                                   caption=replies.ITEM_DESCRIPTION.format(name=item.name,
                                                                                           description=item.description,
                                                                                           price=item.price)),
                                   reply_markup=keyboards.shop_keyboard)
    await state.update_data(item_id=item.id)
    await query.answer()


@dp.callback_query_handler(lambda query: query.data == 'add_to_cart', state='*')
async def add_to_cart(query: types.CallbackQuery, state: FSMContext, *args, **kwargs):
    user_data = await state.get_data()
    await state.update_data(cart=[*user_data.pop('cart', []), user_data.pop('item_id')], **user_data)
    await query.answer(replies.BUY_ITEM_SUCCESS)


# Cart part
@dp.callback_query_handler(lambda query: query.data == 'cart', state='*')
async def get_cart(query: types.CallbackQuery, state: FSMContext, *args, **kwargs):
    user_data = await state.get_data()
    cart = user_data.get('cart', [])
    if not cart:
        await query.answer(replies.CART_IS_EMPTY)
        return
    message = f'{replies.CART_REVIEW.format(n=len(cart))}\n\n'
    for n, item_id in enumerate(cart):
        item: Item = await sync_to_async(Item.objects.get)(id=item_id)
        message += f'{replies.CARD_ITEM.format(n=n + 1, name=item.name, price=item.price)}\n'
    if message:
        await query.message.reply(message, reply=False, reply_markup=keyboards.cart_keyboard)
    await query.answer()


@dp.callback_query_handler(lambda query: query.data == 'empty_cart', state='*')
async def empty_cart(query: types.CallbackQuery, state: FSMContext, *args, **kwargs):
    await state.update_data(cart=[])
    await query.answer(replies.EMPTY_CART_SUCCESS)


# Checkout part
@dp.callback_query_handler(lambda query: query.data == 'checkout', state='*')
async def checkout(query: types.CallbackQuery, state: FSMContext, *args, **kwargs):
    user_data = await state.get_data()
    cart = user_data.get('cart', [])
    if not cart:
        await query.message.reply(replies.CART_IS_EMPTY, reply=False, reply_markup=ReplyKeyboardRemove())
        await query.answer()
        return
    await query.message.reply(replies.ASK_FOR_ADDRESS, reply=False, reply_markup=ReplyKeyboardRemove())
    await states.CheckoutStates.waiting_for_address.set()
    await query.answer()


@dp.message_handler(lambda msg: not msg.text.startswith('/'),
                    state=states.CheckoutStates.waiting_for_address, content_types=types.ContentTypes.TEXT)
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


@dp.message_handler(lambda msg: not msg.text.startswith('/'),
                    state=states.CheckoutStates.waiting_for_payment_confirmation, content_types=types.ContentTypes.TEXT)
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
        account.balance -= total_price
        await sync_to_async(account.save)()
        order = await sync_to_async(Order.objects.create)(user=user,
                                                          address=user_data.get('address'),
                                                          price=total_price)
        await sync_to_async(order.save)()
        for item in items:
            await sync_to_async(OrderItem.objects.create)(order=order, item=item)
        await msg.reply(replies.ORDER_SUCCESS.format(id=order.id), reply=False, reply_markup=ReplyKeyboardRemove())
        await state.finish()

        # Notify manager
        username_with_space = f'@{msg.from_user.username} ' if msg.from_user.username else ''
        message = replies.NOTIFY_MANAGER_NEW_ORDER.format(
            first_name=msg.from_user.first_name,
            last_name=msg.from_user.last_name,
            username_with_space=username_with_space,
            user_id=msg.from_user.id,
            order_id=order.id,
            address=order.address,
            items_text=str(*list(f'{n}. {item.name} (ID: {item.id})\n' for n, item in enumerate(items)))
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(text='Mark completed', callback_data=f'complete-order-{order.id}'))
        await msg.bot.send_message(configs.TG_MANAGER_ID, message, reply_markup=markup)

    else:
        await msg.reply(replies.NOT_SUFFICIENT_FUNDS, reply=False, reply_markup=keyboards.not_sufficient_funds_keyboard)
        await state.reset_state(with_data=False)


@dp.callback_query_handler(lambda query: query.data.startswith('complete-order-'), state='*')
async def complete_order(query: types.CallbackQuery):
    data = query.data
    order_id = data[len('complete-order-'):]
    order = await sync_to_async(Order.objects.get)(id=order_id)
    order.status = 'completed'
    order.is_completed = True
    order.date_completed = timezone.now()
    await sync_to_async(order.save)()
    await query.bot.send_message(query.from_user.id, replies.ORDER_COMPLETED.format(order_id=order.id))
    await query.answer()

    # Notify user
    user = await sync_to_async(User.objects.get)(id=order.user_id)
    await query.bot.send_message(user.id, replies.ORDER_DELIVERED.format(order_id=order.id))


# Referral part
@dp.callback_query_handler(lambda query: query.data == 'referral', state='*')
async def referral(query: types.CallbackQuery, *args, **kwargs):
    link = f'https://t.me/{(await bot.get_me()).username}?start={query.from_user.id}'
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='Share with friend!',
                                    url=f'https://t.me/share/url?url={link}&'
                                        f'text={quote("Check this bot out!")}'))
    await query.message.reply(replies.REFERRAL_LINK.format(link=link), reply=False, reply_markup=markup)
    await query.answer()


# Support part
@dp.callback_query_handler(lambda query: query.data == 'support', state='*')
async def support(query: types.CallbackQuery, *args, **kwargs):
    await query.message.reply(replies.SUPPORT_MESSAGE, reply=False, reply_markup=ReplyKeyboardRemove())
    await states.SupportStates.waiting_for_ticket.set()
    await query.answer()


@dp.message_handler(lambda msg: not msg.text.startswith('/'),
                    state=states.SupportStates.waiting_for_ticket, content_types=types.ContentTypes.TEXT)
@django_tools.auth_user_decorator
async def create_support_ticket(msg: types.Message, user: User, state: FSMContext, *args, **kwargs):
    ticket: SupportTicket = await sync_to_async(SupportTicket.objects.create)(from_user=user,
                                                                              text=msg.text,
                                                                              user_message_id=msg.message_id)
    await msg.reply(replies.TICKET_CREATED, reply=False, reply_markup=ReplyKeyboardRemove())
    await state.reset_state(with_data=False)

    # Notify manager
    username_with_space = f'@{msg.from_user.username} ' if msg.from_user.username else ''
    message = replies.NOTIFY_MANAGER_NEW_TICKET.format(
        first_name=msg.from_user.first_name,
        last_name=msg.from_user.last_name,
        username_with_space=username_with_space,
        user_id=msg.from_user.id,
        ticket_id=ticket.id,
        ticket_text=ticket.text,
    )
    msg_bot = await msg.bot.send_message(configs.TG_MANAGER_ID, message, reply_markup=ReplyKeyboardRemove())
    ticket.manager_message_id = msg_bot.message_id
    await sync_to_async(ticket.save)()


@dp.message_handler(lambda msg: msg.from_user.id == int(configs.TG_MANAGER_ID),
                    lambda msg: bool(msg.reply_to_message),
                    content_types=types.ContentTypes.TEXT, state='*')
async def reply_to_ticket(msg: types.Message, *args, **kwargs):
    try:
        ticket: SupportTicket = await sync_to_async(SupportTicket.objects.get)(
            manager_message_id=msg.reply_to_message.message_id,
        )
    except SupportTicket.DoesNotExist:
        return
    ticket.is_resolved = True
    ticket.date_resolved = timezone.now()
    await sync_to_async(ticket.save)()

    # Send notify to user
    # noinspection PyTypeChecker
    await msg.bot.send_message(ticket.from_user_id,
                               replies.TICKET_RESOLVED.format(text=msg.text),
                               reply_to_message_id=ticket.user_message_id)


# Shipping policy part
@dp.callback_query_handler(lambda query: query.data == 'shipping_policy', state='*')
async def shipping_policy(query: types.CallbackQuery, state: FSMContext, *args, **kwargs):
    policy: ShippingPolicy = await sync_to_async(ShippingPolicy.objects.get)(id=1)
    await query.message.reply(replies.SHIPPING_POLICY.format(text=policy.text, updated=policy.updated.date()),
                              reply=False, reply_markup=ReplyKeyboardRemove())
    await query.answer()


@dp.message_handler(state='*', commands=['change_policy'])
@django_tools.auth_user_decorator
@django_tools.staff_account_required
async def change_policy(msg: types.Message, user: User, state: FSMContext, *args, **kwargs):
    await msg.reply(replies.ASK_NEW_POLICY, reply=False, reply_markup=ReplyKeyboardMarkup())
    await states.ShippingPolicyChangeStates.waiting_for_new_policy.set()


@dp.message_handler(lambda msg: not msg.text.startswith('/'),
                    state=states.ShippingPolicyChangeStates.waiting_for_new_policy,
                    content_types=types.ContentTypes.TEXT)
async def set_policy(msg: types.Message, state: FSMContext, *args, **kwargs):
    policy: ShippingPolicy = await sync_to_async(ShippingPolicy.objects.get)(id=1)
    policy.text = msg.text
    policy.updated = timezone.now()
    await sync_to_async(policy.save)()
    await msg.reply(replies.SHIPPING_POLICY_CHANGED, reply=False, reply_markup=ReplyKeyboardRemove())
    await state.reset_state(with_data=False)


# Deleting item part
@dp.message_handler(state='*', commands=['delete_item'])
@django_tools.auth_user_decorator
@django_tools.staff_account_required
async def delete_item(msg: types.Message, user: User, state: FSMContext, *args, **kwargs):
    user_data = await state.get_data()
    item = await sync_to_async(Item.objects.get)(id=user_data.get('item_id'))
    item.disabled = True
    await sync_to_async(item.save)()
    await msg.reply(replies.ITEM_DELETED, reply=False, reply_markup=ReplyKeyboardRemove())


async def startup(dispatcher: Dispatcher):
    pass


async def shutdown(dispatcher: Dispatcher):
    pass
