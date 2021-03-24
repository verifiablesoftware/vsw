import os
import socket
import subprocess
from typing import List

from vsw.log import Log
from vsw.utils import get_vsw_agent

logger = Log(__name__).logger


def main(args: List[str]) -> bool:
    kill_lt()
    kill_vsw()
    print("Exited vsw")


def kill_vsw():
    configuration = get_vsw_agent()
    a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    location = (configuration.get("admin_host"), int(configuration.get("admin_port")))
    result_of_check = a_socket.connect_ex(location)
    if result_of_check == 0:
        subprocess.Popen(f'kill -9 $(lsof -t -i:{configuration.get("admin_port")})', stdout=subprocess.DEVNULL, shell=True)


def kill_lt():
    out = os.popen("ps aux | grep npx").read()
    for line in out.splitlines():
        if 'localtunnel' in line:
            pid = int(line.split()[1])
            subprocess.run(f'kill -9 {pid}', stdout=subprocess.DEVNULL, shell=True)
