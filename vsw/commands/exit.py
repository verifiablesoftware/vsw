import os
import subprocess
from typing import List

from vsw.log import Log

logger = Log(__name__).logger


def main(args: List[str]) -> bool:
    kill_lt()
    kill_controller()
    kill_vsw()


def kill_all():
    kill_lt()
    kill_controller()
    kill_vsw()


def kill_vsw():
    out = os.popen("ps aux | grep agent.py").read()
    for line in out.splitlines():
        if 'python3' in line:
            pid = int(line.split()[1])
            subprocess.run(f'kill -9 {pid}', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)


def kill_lt():
    out = os.popen("ps aux | grep npx").read()
    for line in out.splitlines():
        if 'localtunnel' in line:
            pid = int(line.split()[1])
            subprocess.run(f'kill -9 {pid}', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)


def kill_controller():
    out = os.popen("ps aux | grep controller/server.py").read()
    for line in out.splitlines():
        if 'python3' in line:
            pid = int(line.split()[1])
            subprocess.run(f'kill -9 {pid}', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True)