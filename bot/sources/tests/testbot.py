import os
import unittest

import django
from aiogram.utils import executor


class MyTestCase(unittest.TestCase):
    @staticmethod
    def test_bot():
        # Setup Django environment
        print('Setting Django environment...')
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crypto_bot.settings')
        django.setup()

        # Import necessary objects
        print('Importing modules...')
        from bot.sources.bot import dp, startup, shutdown

        # Start bot
        print('Starting bot...')
        executor.start_polling(dp, skip_updates=True, on_startup=startup, on_shutdown=shutdown)


if __name__ == '__main__':
    unittest.main()
