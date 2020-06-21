import dj_redis_url
from aiogram.contrib.fsm_storage.redis import RedisStorage2

import configs

redis_config: dict = dj_redis_url.config(default=configs.REDIS_URL)


def parse_config(config_to_parse: dict) -> dict:
    """
    Parses redis_config for RedisStorage2 by lowering keys

    Structure of redis_config:
        >>> redis_config.keys()
        dict_keys(['DB', 'PASSWORD', 'HOST', 'PORT'])

    :return: dict
    """

    return dict((k.lower(), v) for k, v in config_to_parse.items())


# Following to the structure above it's better to write this expression
redis_storage = RedisStorage2(**parse_config(redis_config))
