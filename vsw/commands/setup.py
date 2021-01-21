import argparse
import os
import uuid
import getpass
from pathlib import Path
from typing import List
from os.path import expanduser
import configparser

import requests
from aries_cloudagent_vsw.commands import run_command
from pip._vendor.distlib.compat import raw_input

import vsw.utils
from vsw import utils
from vsw.log import Log

logger = Log(__name__).logger


def main(args: List[str]) -> bool:
    wallet_key = getpass.getpass('Please enter wallet key: ')
    logger.info(wallet_key)
    args = parse_args(args)
    start_agent(wallet_key, args)
    retrieve_DID()


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=False, help="The wallet name")
    return parser.parse_args(args)


def start_agent(wallet_key, args):
    configuration = utils.get_vsw_agent()
    config_path = Path(__file__).parent.parent.joinpath("conf/genesis.txt").resolve()
    wallet_name = 'default'
    logger.info('genesis_file: ' + str(config_path))
    if args.name:
        wallet_name = args.name
    run_command('start', ['--admin', configuration.get("admin_host"), configuration.get("admin_port"),
                          '--inbound-transport', configuration.get("inbound_transport_protocol"),
                          configuration.get("inbound_transport_host"), configuration.get("inbound_transport_port"),
                          '--outbound-transport', configuration.get('outbound_transport_protocol'),
                          '--endpoint', configuration.get("endpoint"),
                          '--label', configuration.get("label"),
                          '--seed', get_seed(),
                          '--genesis-file', str(config_path),
                          '--webhook-url', configuration.get("webhook_url"),
                          # '--wallet-type', 'indy',
                          # '--wallet-name', wallet_name,
                          # '--wallet-key', wallet_key,
                          '--public-invites',
                          '--auto-accept-invites',
                          '--auto-accept-requests',
                          '--auto-ping-connection',
                          '--auto-respond-messages',
                          '--auto-respond-credential-offer',
                          '--auto-respond-presentation-request',
                          '--auto-verify-presentation',
                          '--admin-insecure-mode'])


def retrieve_DID():
    try:
        vsw_agent_host = vsw.utils.get_vsw_agent_host()
        response = requests.post(vsw_agent_host + "/wallet/did/create")
        logger.info(response.text)
    except:
        logger.error('init failed')
    else:
        logger.info('init successfully!')


def get_seed():
    key_folder = expanduser("~") + '/.indy-client/wallet'
    key_path = key_folder + '/key.ini'
    is_exist = os.path.exists(key_path)
    if is_exist:
        config = configparser.ConfigParser()
        config.read(key_path)
        key = config['INFO']['key']
        return key
    else:
        uuid_str = uuid.uuid4().hex
        os.makedirs(key_folder)
        config = configparser.ConfigParser()
        if not config.has_section("INFO"):
            config.add_section("INFO")
        config.set("INFO", "key", uuid_str)
        with open(key_path, 'w') as configfile:
            config.write(configfile)
        return uuid_str
