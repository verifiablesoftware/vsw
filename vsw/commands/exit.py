import asyncio
from typing import List
import psutil

from vsw.log import Log

logger = Log(__name__).logger

def main(args: List[str]) -> bool:
    asyncio.get_event_loop().stop()
    kill()


def kill():
    for proc in psutil.process_iter():
        if 'python' in proc.name():
            proc.kill()