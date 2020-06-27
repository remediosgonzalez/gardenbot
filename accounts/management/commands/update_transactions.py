import asyncio
import logging
import os

import bitcoinlib
import django
from django.core.management import BaseCommand

import configs
from bot.sources.tools import replies, logging_tools

log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
logging_tools.setup()


class Command(BaseCommand):
    help = 'Updates transactions from users and adds funds to accounts'

    # Django BaseCommand methods
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        log.info('Importing modules...')
        from users.models import User
        from accounts.models import Account
        from bot.sources.bot import bot
        log.info('Modules imported.')

        log.info('Getting users...')
        users = list(User.objects.all())
        log.info('Success.')

        loop = asyncio.get_event_loop()

        for user in users:
            log.info(f'Getting wallet for user {user.id}')
            wallet = bitcoinlib.wallets.wallet_create_or_open(f'wallet-{user.id}', db_uri=configs.JAWSDB_URL)
            log.info('Success.')

            if wallet.network.name == configs.NETWORK:
                # TODO: [6/26/2020 by Mykola] Create a better algorithm
                log.info('Checking for new transactions...')
                if n := wallet.transactions_update():
                    log.info(f'User {user.id} has {n} new transactions. Getting the latest...')
                    transaction = wallet.transactions()[-1]
                    if transaction.status == 'confirmed':
                        for output in transaction.outputs:
                            if output.address == wallet.get_key().address:
                                output: bitcoinlib.wallets.Output

                                string_value = wallet.network.print_value(output.value)
                                log.info(f'Adding {string_value} to account of user {user.id}')
                                log.info('Getting account...')
                                account = Account.objects.get(user=user)
                                log.info('Successful.')
                                account.balance = output.value
                                log.info('Saving...')
                                account.save()
                                log.info('Successful.')

                                log.info('Sending notification...')
                                # noinspection StrFormat
                                loop.run_until_complete(
                                    bot.send_message(user.id, replies.FUNDS_ADDED.format(string_value))
                                )
                                log.info('Successful.')
                                print(f'Successfully added {string_value} to user ID{user.id} balance')
                    else:
                        log.error(f'Transaction {transaction.rawtx} is not confirmed.')
                        loop.run_until_complete(
                            bot.send_message(configs.TG_ADMIN_ID,
                                             f'Transaction {transaction.rawtx} is not confirmed for user {user.id}')
                        )
                else:
                    log.info(f'Found no new transactions for user {user.id}')
            else:
                log.error(f'Wallet has network {wallet.network.name} when current network is {configs.NETWORK}')
        log.info('Script ended.')


if __name__ == '__main__':
    # Setup Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crypto_bot.settings')
    django.setup()

    # Execute command
    c = Command()
    c.handle()
