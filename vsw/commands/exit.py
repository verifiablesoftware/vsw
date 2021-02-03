import os
from typing import List
from vsw.utils import get_vsw_agent

from vsw.log import Log

logger = Log(__name__).logger

def main(args: List[str]) -> bool:
    kill()

def kill():
    configuration = get_vsw_agent()
    os.system(f'kill $(lsof -t -i:{configuration.get("admin_port")})')