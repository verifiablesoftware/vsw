import argparse
import os
import subprocess
import sys
import uuid
import getpass
from pathlib import Path
from typing import List
from vsw.commands.exit import kill
from os.path import expanduser
import configparser
import daemon

from aries_cloudagent_vsw.commands import run_command

from vsw import utils
from vsw.log import Log

logger = Log(__name__).logger


def main(args: List[str]) -> bool:
    try:
        # kill()
        wallet_key = getpass.getpass('Please enter wallet key: ')
        args = parse_args(args)
        utils.save_endpoint(args.endpoint)
        if args.provision:
            provision(wallet_key, args.name)
        else:
            with daemon.DaemonContext(stdout=sys.stdout, stderr=sys.stderr, files_preserve=logger.streams):
                start_agent(wallet_key, args.name, args.endpoint)
    except KeyboardInterrupt:
        print(" => Exit setup")


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=False, help="The wallet name")
    parser.add_argument("--endpoint", required=True, help="The endpoint url, please get it with 'vsw register -e'")
    parser.add_argument('-p', '--provision', action='store_true')
    return parser.parse_args(args)


def provision(wallet_key, name):
    wallet_name = 'default'
    if name:
        wallet_name = name
    configuration = utils.get_vsw_agent()
    config_path = Path(__file__).parent.parent.joinpath("conf/genesis.txt").resolve()
    logger.info('genesis_file: ' + str(config_path))
    endpoint = f'{configuration.get("outbound_transport_protocol")}://{configuration.get("inbound_transport_host")}:{configuration.get("inbound_transport_port")}/'
    run_command('provision', [
        '--endpoint', endpoint,
        '--seed', get_seed(wallet_name),
        '--genesis-file', str(config_path),
        '--accept-taa', '1',
        '--wallet-type', 'indy',
        '--wallet-name', wallet_name,
        '--wallet-key', wallet_key
    ])


def start_agent(wallet_key, name, endpoint):
    configuration = utils.get_vsw_agent()
    config_path = Path(__file__).parent.parent.joinpath("conf/genesis.txt").resolve()
    wallet_name = 'default'
    admin_port = configuration.get("admin_port")
    transport_port = configuration.get("inbound_transport_port")
    logger.info('genesis_file: ' + str(config_path))

    if endpoint is None:
        endpoint = configuration.get("endpoint")
    if name:
        wallet_name = name
    run_command('start', ['--admin', configuration.get("admin_host"), admin_port,
                          '--inbound-transport', configuration.get("inbound_transport_protocol"),
                          configuration.get("inbound_transport_host"), transport_port,
                          '--outbound-transport', configuration.get('outbound_transport_protocol'),
                          '--endpoint', endpoint,
                          '--label', configuration.get("label"),
                          '--seed', get_seed(wallet_name),
                          '--genesis-file', str(config_path),
                          '--webhook-url', configuration.get("webhook_url"),
                          '--accept-taa', '1',
                          '--wallet-type', 'indy',
                          '--wallet-name', wallet_name,
                          '--wallet-key', wallet_key,
                          '--public-invites',
                          '--log-config', logger.aries_config_path,
                          '--log-file', logger.aries_log_file,
                          '--auto-accept-invites',
                          '--auto-accept-requests',
                          '--auto-ping-connection',
                          '--auto-respond-messages',
                          '--auto-respond-credential-proposal',
                          '--auto-respond-credential-offer',
                          '--auto-respond-credential-request',
                          '--auto-store-credential',
                          '--auto-respond-presentation-request',
                          '--auto-verify-presentation',
                          '--auto-respond-presentation-proposal',
                          '--admin-insecure-mode'])


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
            logger.warn('not found seed')
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

    logger.info('seed:' + seed)
    return seed
