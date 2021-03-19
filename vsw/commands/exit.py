import os
import signal
import socket
from typing import List
from vsw.utils import get_vsw_agent

from vsw.log import Log

logger = Log(__name__).logger


def main(args: List[str]) -> bool:
    kill_lt()
    kill_vsw()


def kill_vsw():
    configuration = get_vsw_agent()
    a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    location = (configuration.get("admin_host"), int(configuration.get("admin_port")))
    result_of_check = a_socket.connect_ex(location)
    if result_of_check == 0:
        os.system(f'kill $(lsof -t -i:{configuration.get("admin_port")})')


def kill_lt():
    out = os.popen("ps aux | grep npx").read()
    for line in out.splitlines():
        if 'localtunnel' in line:
            pid = int(line.split()[1])
            kill_pid(pid)
            print('Closed local tunnel')


def kill_pid(pid):
    try:
        os.kill(pid, signal.SIGKILL)
    except OSError as e:
        pass
