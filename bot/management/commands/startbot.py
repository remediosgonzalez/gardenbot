from aiogram.utils import executor
from django.core.management import BaseCommand

from bot.sources.bot import dp, startup, shutdown


class Command(BaseCommand):
    help = 'Starts Telegram bot'

    # Django BaseCommand methods
    def add_arguments(self, parser):
        # TODO: [6/21/2020 by Mykola] Implement the argument
        parser.add_argument('--skip-updates',
                            dest='skip_updates',
                            default=True,
                            help='Designates whether to skip updates ot not'
                            )

    def handle(self, *args, **options):
        executor.start_polling(dp, skip_updates=True, on_startup=startup, on_shutdown=shutdown)
