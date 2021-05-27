import argparse
import configparser
import getpass
import os
import uuid
from os.path import expanduser
from pathlib import Path
from typing import List
import sys
from aries_cloudagent_vsw.commands import run_command
import daemon
from vsw import utils
from vsw.log import Log

logger = Log(__name__).logger


def main(args: List[str]) -> bool:
    try:
        wallet_key = getpass.getpass('Please enter wallet key: ')
        args = parse_args(args)
        if args.ports:
            utils.set_port_number(args.ports)
        start_local_tunnel(args.name)
        start_controller()
        with daemon.DaemonContext(stdout=sys.stdout, stderr=sys.stderr, files_preserve=logger.streams):
            start_aca_py(wallet_key, args)
    except KeyboardInterrupt:
        print(" => Exit setup")


def start_aca_py(wallet_key, args):
    if args.provision:
        provision(wallet_key, args.name, args.non_endorser)
    else:
        start_agent(wallet_key, args.name, args.non_endorser)


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", required=False, help="The wallet name")
    parser.add_argument('-p', '--provision', action='store_true')
    parser.add_argument("-pn", "--ports", required=False,
                        help="The ports number, format is (<endpoint_port>,<admin_port>,<webhook_port>)")
    parser.add_argument("-ne", "--non-endorser", action='store_true')
    return parser.parse_args(args)


def provision(wallet_key, name, non_endorser):
    wallet_name = 'default'
    if name:
        wallet_name = name
    configuration = utils.get_vsw_agent()
    config_path = Path(__file__).parent.parent.joinpath("conf/genesis.txt").resolve()
    logger.info('genesis_file: ' + str(config_path))
    endpoint = f'{configuration.get("outbound_transport_protocol")}://{configuration.get("inbound_transport_host")}:{configuration.get("inbound_transport_port")}/'
    try:
        args = [
            '--endpoint', endpoint,
            '--seed', get_seed(wallet_name),
            '--genesis-file', str(config_path),
            '--accept-taa', '1',
            '--wallet-type', 'indy',
            '--log-config', logger.aries_config_path,
            '--log-file', logger.aries_log_file,
            '--wallet-name', wallet_name,
            '--wallet-key', wallet_key
        ]
        if non_endorser:
            args.append('--wallet-local-did')
        run_command('provision', args)
    except BaseException as e:
        logger.error(e.message)
        logger.error("please check if your public DID and verkey is registered in the ledger!")
        pass


def start_agent(wallet_key, name, non_endorser):
    configuration = utils.get_vsw_agent()
    config_path = Path(__file__).parent.parent.joinpath("conf/genesis.txt").resolve()
    wallet_name = 'default'
    admin_port = configuration.get("admin_port")
    transport_port = configuration.get("inbound_transport_port")
    logger.info('genesis_file: ' + str(config_path))

    if name:
        wallet_name = name
    try:
        args = ['--admin', configuration.get("admin_host"), admin_port,
                '--inbound-transport', configuration.get("inbound_transport_protocol"),
                configuration.get("inbound_transport_host"), transport_port,
                '--outbound-transport', configuration.get('outbound_transport_protocol'),
                '--endpoint', configuration.get("endpoint"),
                '--label', configuration.get("label"),
                '--seed', get_seed(wallet_name),
                '--webhook-url', configuration.get("webhook_url"),
                '--tails-server-base-url', utils.get_tails_server().get("host"),
                '--genesis-file', str(config_path),
                '--accept-taa', '1',
                '--wallet-type', 'indy',
                '--wallet-name', wallet_name,
                '--wallet-key', wallet_key,
                '--log-config', logger.aries_config_path,
                '--log-file', logger.aries_log_file,
                '--auto-accept-invites',
                '--preserve-exchange-records',
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
                '--admin-insecure-mode']
        if non_endorser:
            args.append('--wallet-local-did')
        run_command('start', args)
    except BaseException as error:
        logger.error("started vsw failed.")
        print('An exception occurred: {}'.format(error))


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
