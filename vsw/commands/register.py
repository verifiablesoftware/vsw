import argparse
import subprocess
from pathlib import Path
from typing import List
from vsw.log import Log
from vsw import utils
import os

logger = Log(__name__).logger


def main(args: List[str]) -> bool:
    args = parse_args(args)
    try:
        if args.endpoint:
            port = utils.get_vsw_agent().get("inbound_transport_port")
            if args.merchant == "lhr":
                start_localhost_run(port)
            else:
                start_local_tunnel(port)
        else:
            print('Nothing to do, one parameter at least is required. eg: -e means register your endpoint url')
    except KeyboardInterrupt:
        print(" ==> Exit init")


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--endpoint', action='store_true')
    parser.add_argument("-m", "--merchant", required=False, default="lt",
                        help="The merchant name, eg: lhr, lt. lhr means localhost.run, lt means localtunnel")
    return parser.parse_args(args)


def start_localhost_run(port):
    subprocess.Popen(f"ssh -tt -R 80:localhost:{port} localhost.run &", shell=True)


def start_local_tunnel(port):
    script_path = Path(__file__).parent.parent.joinpath("conf/local_tunnel.sh").resolve()
    os.system(f'chmod +x {script_path}')
    rc = os.system(f'{script_path} {port}')
    print(rc)