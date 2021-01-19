import os

from vsw.env import Env, getenv


def test_getenv():
    assert getenv() == Env.DEV.value
    os.environ['VSW_ENV'] = Env.PROD.value
    assert getenv() == Env.PROD.value