import argparse
import json
import os
import uuid
import getpass
from pathlib import Path
from typing import List
from os.path import expanduser
import configparser

import requests
from aries_cloudagent_vsw.commands import run_command

import vsw.utils
from vsw import utils
from vsw.log import Log

logger = Log(__name__).logger


def main(args: List[str]) -> bool:
    wallet_key = getpass.getpass('Please enter wallet key: ')
    logger.info(wallet_key)
    args = parse_args(args)
    if(args.provision):
        logger.info('provision agent')
        provision(wallet_key, args.name)
    else:
        logger.info("start agent")
        start_agent(wallet_key, args.name)

    connection_repo()


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=False, help="The wallet name")
    parser.add_argument("--schema", required=False, help="The schema")
    parser.add_argument('-p', '--provision', action='store_true')
    return parser.parse_args(args)

def provision(wallet_key, name):
    wallet_name = 'default'
    if name:
        wallet_name = name
    configuration = utils.get_vsw_agent()
    config_path = Path(__file__).parent.parent.joinpath("conf/genesis.txt").resolve()
    logger.info('genesis_file: ' + str(config_path))
    run_command('provision', [
                          '--endpoint', configuration.get("endpoint"),
                          '--seed', get_seed(wallet_name),
                          '--genesis-file', str(config_path),
                          '--accept-taa', '1',
                          '--wallet-type', 'indy',
                          '--wallet-name', wallet_name,
                          '--wallet-key', wallet_key
                          ])

def start_agent(wallet_key, name):
    configuration = utils.get_vsw_agent()
    config_path = Path(__file__).parent.parent.joinpath("conf/genesis.txt").resolve()
    wallet_name = 'default'
    logger.info('genesis_file: ' + str(config_path))
    if name:
        wallet_name = name
    run_command('start', ['--admin', configuration.get("admin_host"), configuration.get("admin_port"),
                          '--inbound-transport', configuration.get("inbound_transport_protocol"),
                          configuration.get("inbound_transport_host"), configuration.get("inbound_transport_port"),
                          '--outbound-transport', configuration.get('outbound_transport_protocol'),
                          '--endpoint', configuration.get("endpoint"),
                          '--label', configuration.get("label"),
                          '--seed', get_seed(wallet_name),
                          '--genesis-file', str(config_path),
                          '--webhook-url', configuration.get("webhook_url"),
                          '--accept-taa', '1',
                          '--wallet-type', 'indy',
                          '--wallet-name', wallet_name,
                          '--wallet-key', wallet_key,
                          '--public-invites',
                          '--debug',
                          '--auto-accept-invites',
                          '--auto-accept-requests',
                          '--auto-ping-connection',
                          '--auto-respond-messages',
                          '--auto-respond-credential-offer',
                          '--auto-respond-presentation-request',
                          '--auto-verify-presentation',
                          '--admin-insecure-mode'])


def connection_repo():
    try:
        vsw_config = vsw.utils.get_vsw_agent()

        local= f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/connections/create-invitation'
        response = requests.post(local, {
            "alias": vsw_config.get("label"),
            "auto_accept": True,
            # "public": True,
            # "multi_use": False
        })
        res = json.loads(response.text)
        logger.info(res)

        vsw_repo_config = vsw.utils.get_repo_host()
        vsw_repo_url = f'http://{vsw_repo_config.get("host")}/connections/receive-invitation)'
        receive_res = requests.post(vsw_repo_url, res["invitation"])
        logger.info(json.loads(receive_res.text))
    except Exception as err:
        logger.error('connection vsw-repo failed', err)


def get_seed(wallet_name):
    key_folder = expanduser("~") + '/.indy_client/wallet'
    key_path = key_folder + '/key.ini'
    is_exist = os.path.exists(key_path)

    seed=None
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

    logger.info('seed:' +seed)
    return seed
