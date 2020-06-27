import inspect
from functools import wraps

from aiogram import types
from asgiref.sync import sync_to_async as _sync_to_async
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounts.models import Account
from bot.sources.tools import replies
from users import models

User: models.User = get_user_model()


# Start of the block of code from Django issue (https://github.com/django/asgiref/issues/142)
def sync_to_async(sync_fn):
    is_gen = inspect.isgeneratorfunction(sync_fn)
    async_fn = _sync_to_async(sync_fn)

    if is_gen:

        @wraps(sync_fn)
        async def wrapper(*args, **kwargs):
            sync_iterable = await async_fn(*args, **kwargs)
            sync_iterator = await iter_async(sync_iterable)

            while True:
                try:
                    yield await next_async(sync_iterator)
                except StopAsyncIteration:
                    return

    else:

        @wraps(sync_fn)
        async def wrapper(*args, **kwargs):
            return await async_fn(*args, **kwargs)

    return wrapper


iter_async = sync_to_async(iter)


async def sync_to_async_iterable(sync_iterable):
    sync_iterator = await iter_async(sync_iterable)
    while True:
        try:
            yield await next_async(sync_iterator)
        except StopAsyncIteration:
            return
# End of the block of code from Django issue (https://github.com/django/asgiref/issues/142)


@sync_to_async
def next_async(it):
    try:
        return next(it)
    except StopIteration:
        raise StopAsyncIteration


@sync_to_async
def get_or_create_user(user: types.User) -> User:
    try:
        return User.objects.get(id=user.id)
    except User.DoesNotExist:
        return User.objects.create_user(**dict(user))


def auth_user_decorator(func):
    async def wrapper(msg: types.Message, *args, **kwargs):
        user = await sync_to_async(User.objects.get)(id=msg.from_user.id)
        return await func(msg, user, *args, **kwargs)
    return wrapper


def staff_account_required(func):
    """
    Decorator for accepting only staff members

    :param func:
    :return:
    """
    async def wrapper(msg: types.Message, user, *args, **kwargs):
        if user.is_staff or user.is_superuser:
            return await func(msg, user, *args, **kwargs)
        else:
            await msg.reply(replies.NOT_AUTHENTICATED, reply=False)
    return wrapper


@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        Account.objects.create(user=instance)
