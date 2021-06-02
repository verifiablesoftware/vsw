import argparse
import configparser
import json
import os
import time
import uuid
from os.path import expanduser
from pathlib import Path
from typing import List

import requests
from aries_cloudagent_vsw.commands import run_command

from vsw import utils
from vsw.commands import init
from vsw.log import Log
from vsw.utils import get_vsw_agent

logger = Log(__name__).logger


def main(args: List[str]) -> bool:
    try:
        args = parse_args(args)
        if args.subcommand == "newwallet":
            wallet_name = args.name
            wallet_key = args.key
            if not wallet_name:
                print("The wallet name is required!")
                return
            if not wallet_key:
                print("The wallet key is required!")
                return
            provision(wallet_name, wallet_key)
        elif args.subcommand == "wallet":
            if not args.name:
                print("The wallet name is required!")
                return
            if not args.key:
                print("The wallet key is required!")
                return
            if args.ports:
                utils.set_port_number(args.ports)
            start_local_tunnel(args.name)
            start_controller()
            start_agent(args.name, args.key, get_seed(args.name))
            ready = check_status()
            if ready:
                print("success")
            else:
                print("failed")
        elif args.subcommand == "connection":
            init.connection_repo()
        elif args.subcommand == "creddef":
            init.do_credential_definition(args.schema)
        else:
            print("Incorrect sub command")
    except KeyboardInterrupt:
        print(" => Exit setup")


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--ports", required=False,
                        help="The ports number, format is (<endpoint_port>,<admin_port>,<webhook_port>)")
    subparsers = parser.add_subparsers(dest="subcommand")

    new_wallet_parser = subparsers.add_parser('newwallet')
    new_wallet_parser.add_argument('name', help='wallet name')
    new_wallet_parser.add_argument('-k', '--key', required=True, help="wallet key")

    wallet_parser = subparsers.add_parser('wallet')
    wallet_parser.add_argument('name', help='wallet name')
    wallet_parser.add_argument('-k', '--key', required=True, help="wallet key")
    wallet_parser.add_argument('-e', '--endorser', action='store_true')

    subparsers.add_parser('connection')
    creddef_parser = subparsers.add_parser('creddef')
    creddef_parser.add_argument('-s', '--schema', default="software-certificate", help='The schema name')

    return parser.parse_args(args)


def provision(wallet_name, wallet_key):
    configuration = utils.get_vsw_agent()
    config_path = Path(__file__).parent.parent.joinpath("conf/genesis.txt").resolve()
    logger.debug('genesis_file: ' + str(config_path))
    endpoint = f'{configuration.get("outbound_transport_protocol")}://{configuration.get("inbound_transport_host")}:{configuration.get("inbound_transport_port")}/'
    try:
        args = [
            '--endpoint', endpoint,
            '--seed', get_seed(wallet_name),
            '--genesis-file', str(config_path),
            '--wallet-type', 'indy',
            '--accept-taa', '1',
            '--log-config', logger.aries_config_path,
            '--log-file', logger.aries_log_file,
            '--wallet-name', wallet_name,
            '--wallet-key', wallet_key
        ]
        run_command('provision', args)
    except BaseException as e:
        logger.info(e.message)
        logger.info("please check if your public DID and verkey is registered in the ledger!")


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
    if seed is None:
        seed = uuid.uuid4().hex
        config = configparser.ConfigParser()
        if not config.has_section(wallet_name):
            config.add_section(wallet_name)
        config.set(wallet_name, "key", seed)
        with open(key_path, 'a') as configfile:
            config.write(configfile)

    return seed


def start_local_tunnel(name):
    wallet_name = 'default'
    if name:
        wallet_name = name
    sub_domain = get_seed(wallet_name)
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


def start_agent(name, key, seed):
    agent_file = Path(__file__).parent.joinpath("agent.py").resolve()
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

    return False
