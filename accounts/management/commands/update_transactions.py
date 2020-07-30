import asyncio
import logging
import os

import bitcoinlib
import django
from django.core.management import BaseCommand

import configs
from bot.sources.tools import replies, logging_tools, bitcoin_tools

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
        from accounts.models import WalletSweep
        from bot.sources.bot import bot
        log.info('Modules imported.')

        log.info('Getting users...')
        users = list(User.objects.all())
        log.info('Success.')

        loop = asyncio.get_event_loop()

        for user in users:
            log.info(f'Getting wallet for user {user.id}')
            wallet = bitcoinlib.wallets.wallet_create_or_open(f'{configs.NETWORK}-wallet-{user.id}',
                                                              db_uri=configs.JAWSDB_URL)
            log.info('Success.')
            if wallet.network.name == configs.NETWORK:
                log.info('Checking the wallet\'s balance...')
                wallet.utxos_update()
                balance = wallet.balance()
                log.info(f'The balance of the wallet {wallet.name} is {balance}.')
                if balance:
                    sweep_wallet_address = bitcoin_tools.get_address_sweep()
                    log.info(f'Sweeping to the wallet {sweep_wallet_address}')
                    log.info(f'Creating {WalletSweep.__name__} instance')
                    w = WalletSweep.objects.create(user=user, from_wallet=wallet.name, amount=balance)
                    log.info(f'Success. {WalletSweep.__name__} instance created with id {w.id}')
                    transaction = wallet.sweep(sweep_wallet_address)
                    log.info(f'Transaction is made. TXID is {transaction.txid}')
                    log.info(f'Transaction info is {transaction.info()}')

                    log.info(f'Adding {balance} to account of user {user.id}')
                    log.info('Getting account...')
                    account = user.account
                    log.info('Successful.')
                    account.balance = balance
                    log.info('Saving...')
                    account.save()
                    log.info('Successful.')
                    if referral_user := user.is_referral_of_user:
                        referral_account = referral_user.account
                        log.info(f'Adding {balance/10} to referral account {referral_user.id}')
                        referral_account.balance = balance/10
                        referral_account.save()
                        log.info('Referral funds added.')

                    log.info('Sending notification...')
                    loop.run_until_complete(
                        bot.send_message(user.id, replies.FUNDS_ADDED.format(balance=balance))
                    )
                    log.info('Successful.')
                    print(f'Successfully added {balance} to user ID {user.id} balance')
                else:
                    log.info(f'User {user.id} has zero balance.')
            else:
                log.error(f'Wallet has network {wallet.network.name} when current network is {configs.NETWORK}')
            # noinspection PyProtectedMember
            wallet._session.close()
        log.info('Script ended.')


if __name__ == '__main__':
    # Setup Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crypto_bot.settings')
    django.setup()

    # Execute command
    c = Command()
    c.handle()
