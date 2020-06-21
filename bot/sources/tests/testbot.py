import os
import unittest

import django
from aiogram.utils import executor

from bot.sources.bot import dp, startup, shutdown


class MyTestCase(unittest.TestCase):
    def test_bot(self):
        # Setup Django environment
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crypto_bot.settings')
        django.setup()

        # Start bot
        executor.start_polling(dp, skip_updates=True, on_startup=startup, on_shutdown=shutdown)


if __name__ == '__main__':
    unittest.main()
