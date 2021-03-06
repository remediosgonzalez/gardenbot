import bitcoinlib

import configs


def create_or_open_wallet_for_user(user_id: int, db_uri=None, network=None) -> bitcoinlib.wallets.HDWallet:
    wallet = bitcoinlib.wallets.wallet_create_or_open(f'{(network or configs.NETWORK)}-wallet-{user_id}',
                                                      db_uri=(db_uri or configs.JAWSDB_URL),
                                                      network=(network or configs.NETWORK))
    return wallet


def get_wallet_address(wallet: bitcoinlib.wallets.HDWallet) -> str:
    address = wallet.get_key().address
    return address


def get_address_sweep():
    if configs.NETWORK == 'bitcoin':
        return configs.ADDRESS_bitcoin
    elif configs.NETWORK == 'testnet':
        return configs.ADDRESS_testnet
