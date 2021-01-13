import os
from enum import Enum


class Env(Enum):
    DEV = 'dev'
    TEST = 'qa'
    PROD = 'prod'


def getenv():
    e = os.getenv('VSW_ENV')
    try:
        env = Env(e).value
    except:
        print('No environment variable "VSW_ENV", fallback env to "dev"')
        env = Env.DEV.value

    return env
