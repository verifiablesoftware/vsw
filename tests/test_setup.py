import os
import uuid
from pathlib import Path

from vsw import utils

from vsw.commands import setup
from vsw.log import Log
from aries_cloudagent_vsw.commands import run_command
logger = Log(__name__).logger

def test_start_agent():
    # sub_domain = uuid.uuid4().hex
    # utils.save_endpoint(sub_domain)
    # setup.start_local_tunnel(sub_domain)
    setup.start_controller()
    setup.start_agent("publisher", "publisher", False)


def test_provision():
    setup.provision("felix", "felix")


def test_get_seed():
    setup.get_seed()


def test_provision():
    wallet_name="w92"
    wallet_key="w92"
    seed = setup.get_seed(wallet_name).get("seed")
    configuration = utils.get_vsw_agent()
    config_path = Path(__file__).parent.parent.joinpath("vsw/conf/genesis.txt").resolve()
    endpoint = f'{configuration.get("outbound_transport_protocol")}://{configuration.get("inbound_transport_host")}:{configuration.get("inbound_transport_port")}/'
    log_dir = Path(os.path.expanduser('~'))
    if not os.path.exists(str(log_dir) + f"/.indy_client/wallet/{wallet_name}"):
        os.makedirs(str(log_dir) + f"/.indy_client/wallet/{wallet_name}")
    aries_log_file = str(Path(log_dir).joinpath(f"/.indy_client/wallet/{wallet_name}/{seed}.log").resolve())
    try:
        args = [
            '--endpoint', endpoint,
            '--seed', seed,
            '--genesis-file', str(config_path),
            '--wallet-type', 'indy',
            '--log-config', logger.aries_config_path,
            '--log-file', logger.aries_log_file,
            '--wallet-name', wallet_name,
            '--wallet-key', wallet_key
        ]
        run_command('provision', args)
    except BaseException as e:
        print(e.__dict__)