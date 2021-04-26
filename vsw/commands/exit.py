import os
import subprocess
from pathlib import Path
from typing import List

from vsw.log import Log

logger = Log(__name__).logger


def main(args: List[str]) -> bool:
    kill_lt()
    kill_controller()
    kill_vsw()
    print("Exited vsw")


def kill_vsw():
    pid = read_pid_from_pidfile(str(Path.home())+"/aca-py")
    if pid is not None:
        subprocess.Popen(f'kill -9 {pid}', stdout=subprocess.DEVNULL, shell=True)


def read_pid_from_pidfile(pidfile_path):
    """ Read the PID recorded in the named PID file.

        Read and return the numeric PID recorded as text in the named
        PID file. If the PID file cannot be read, or if the content is
        not a valid PID, return ``None``.

        """
    pid = None
    try:
        pidfile = open(pidfile_path, 'r')
    except IOError:
        pass
    else:
        # According to the FHS 2.3 section on PID files in /var/run:
        #
        #   The file must consist of the process identifier in
        #   ASCII-encoded decimal, followed by a newline character.
        #
        #   Programs that read PID files should be somewhat flexible
        #   in what they accept; i.e., they should ignore extra
        #   whitespace, leading zeroes, absence of the trailing
        #   newline, or additional lines in the PID file.

        line = pidfile.readline().strip()
        try:
            pid = int(line)
        except ValueError:
            pass
        pidfile.close()

    return pid


def kill_lt():
    out = os.popen("ps aux | grep npx").read()
    for line in out.splitlines():
        if 'localtunnel' in line:
            pid = int(line.split()[1])
            subprocess.run(f'kill -9 {pid}', stdout=subprocess.DEVNULL, shell=True)


def kill_controller():
    out = os.popen("ps aux | grep controller/server.py").read()
    for line in out.splitlines():
        if 'python3' in line:
            pid = int(line.split()[1])
            subprocess.run(f'kill -9 {pid}', stdout=subprocess.DEVNULL, shell=True)