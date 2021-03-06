from aiogram.dispatcher.filters.state import StatesGroup, State


class AddingItemStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_photo = State()
    waiting_for_confirmation = State()


class CheckoutStates(StatesGroup):
    waiting_for_address = State()
    waiting_for_payment_confirmation = State()


class AddingToCartStates(StatesGroup):
    quantity = State()


class SupportStates(StatesGroup):
    waiting_for_ticket = State()


class ShippingPolicyChangeStates(StatesGroup):
    waiting_for_new_policy = State()
