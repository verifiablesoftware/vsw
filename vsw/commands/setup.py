import argparse
import configparser
import json
import os
import time
import uuid
from os.path import expanduser
from pathlib import Path
from typing import List
from vsw.commands import exit, init

import requests
from vsw.utils import get_vsw_agent

from vsw import utils
from vsw.log import Log

logger = Log(__name__).logger


def main(args: List[str]) -> bool:
    try:
        args = parse_args(args)
        if args.subcommand == "connection":
            init.connection_repo()
        elif args.subcommand == "creddef":
            init.do_credential_definition(args.schema)
        else:
            if args.ports:
                utils.set_port_number(args.ports)
            seed_dict = get_seed(args.name)
            seed = seed_dict.get("seed")

            if not args.key:
                print("The wallet key cannot be empty! please specify with -k/--key parameter")
                return
            # new wallet
            if not seed_dict.get("existed"):
                start_local_tunnel(seed)
                start_controller()
                provision(args.name, args.key, seed)
                # time.sleep(10)
            else:
                exit.kill_all()
                start_local_tunnel(seed)
                start_controller()
                start_agent(args.name, args.key, True, seed)
                ready = check_status()
                if ready:
                    print("success")
                else:
                    print("failed")
    except requests.exceptions.RequestException:
        logger.error("Please check if you have executed 'vsw setup' to start agent!")
    except KeyboardInterrupt:
        print(" => Exit setup")


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", required=False, default="default", help="The wallet name")
    parser.add_argument("-k", "--key", required=False, help="The wallet key")
    parser.add_argument("-pn", "--ports", required=False,
                        help="The ports number, format is (<endpoint_port>,<admin_port>,<webhook_port>)")
    subparsers = parser.add_subparsers(dest="subcommand")
    subparsers.add_parser('connection')
    creddef_parser = subparsers.add_parser('creddef')
    creddef_parser.add_argument('-s', '--schema', default="software-certificate", help='The schema name')
    return parser.parse_args(args)


def read_did_verkey():
    pass


def get_seed(wallet_name):
    key_folder = expanduser("~") + '/.indy_client/wallet'
    key_path = key_folder + '/key.ini'
    is_exist = os.path.exists(key_path)

    seed = None
    if is_exist:
        config = configparser.ConfigParser()
        config.read(key_path)
        try:
            seed = config[wallet_name]['key']
        except:
            logger.debug('not found seed')
    else:
        if os.path.exists(key_folder) is False:
            os.makedirs(key_folder)
    existed = True
    if seed is None:
        existed = False
        seed = uuid.uuid4().hex
        config = configparser.ConfigParser()
        if not config.has_section(wallet_name):
            config.add_section(wallet_name)
        config.set(wallet_name, "key", seed)
        with open(key_path, 'a') as configfile:
            config.write(configfile)

    logger.debug('seed:' + seed)
    return {"seed": seed, "existed": existed}


def start_local_tunnel(seed):
    sub_domain = seed
    utils.save_endpoint(sub_domain)
    configuration = utils.get_vsw_agent()
    port = configuration.get("inbound_transport_port")
    script_path = Path(__file__).parent.parent.joinpath("conf/local_tunnel.sh").resolve()
    os.system(f'chmod +x {script_path}')
    log_dir = Path(os.path.expanduser('~'))
    lt_log_file = str(Path(log_dir).joinpath("vsw_logs/lt.log").resolve())
    os.system(f'nohup {script_path} {port} {sub_domain} > {lt_log_file} 2>&1 &')


def start_controller():
    controller_file = Path(__file__).parent.parent.joinpath("controller/server.py").resolve()
    log_dir = Path(os.path.expanduser('~'))
    controller_log_file = str(Path(log_dir).joinpath("vsw_logs/vsw-controller.log").resolve())
    os.system(f'nohup python3 {controller_file} > {controller_log_file} 2>&1 &')


def start_agent(name, key, existed, seed):
    agent_file = Path(__file__).parent.joinpath("agent.py").resolve()
    log_dir = Path(os.path.expanduser('~'))
    vsw_log_file = str(Path(log_dir).joinpath("vsw_logs/vsw.log").resolve())
    os.system(f'nohup python3 {agent_file} {name} {key} {existed} {seed}> {vsw_log_file} 2>&1 &')


def provision(name, key, seed):
    agent_file = Path(__file__).parent.joinpath("provision.py").resolve()
    log_dir = Path(os.path.expanduser('~'))
    vsw_log_file = str(Path(log_dir).joinpath("vsw_logs/vsw.log").resolve())
    os.system(f'nohup python3 {agent_file} {name} {key} {seed}> {vsw_log_file} 2>&1 &')


def check_status():
    vsw_config = get_vsw_agent()
    times = 0
    while times < 30:
        try:
            local = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/status/ready'
            response = requests.get(local)
            res = json.loads(response.text)
            logger.debug(res)
            if res["ready"]:
                return True;
            else:
                return False
        except requests.exceptions.RequestException:
            time.sleep(1)
            ++times;


def get_seed(wallet_name):
    key_folder = expanduser("~") + '/.indy_client/wallet'
    key_path = key_folder + '/key.ini'
    is_exist = os.path.exists(key_path)

    seed = None
    if is_exist:
        config = configparser.ConfigParser()
        config.read(key_path)
        try:
            seed = config[wallet_name]['key']
        except:
            logger.debug('not found seed')
    else:
        if os.path.exists(key_folder) is False:
            os.makedirs(key_folder)
    existed = True
    if seed is None:
        existed = False
        seed = uuid.uuid4().hex
        config = configparser.ConfigParser()
        if not config.has_section(wallet_name):
            config.add_section(wallet_name)
        config.set(wallet_name, "key", seed)
        with open(key_path, 'a') as configfile:
            config.write(configfile)

    logger.debug('seed:' + seed)
    return {"seed": seed, "existed": existed}