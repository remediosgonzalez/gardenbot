import os

try:
    from configs.configs import *
except ImportError:
    def __getattr__(item):
        if item == 'DEBUG':
            return True if locals().get('DEBUG') == 'True' else False
        elif value := locals().get(item):
            return value
        elif value := os.environ.get(item):
            return value
        else:
            raise NotImplementedError(f'YOU MUST CONFIGURE configs.py FILE BEFORE CONTINUING. '
                                      f'TEMPLATE CAN BE FOUND AS configs_base.py'
                                      f'SET VALUE FOR {item} IN configs.py OR IN AS AN ENVIRONMENT VARIABLE.')
