import os
import sys
from pathlib import Path

from aries_cloudagent_vsw.commands import run_command

from vsw import utils
from vsw.log import Log

logger = Log(__name__).logger


def provision(argv):
    wallet_name = argv[1]
    wallet_key = argv[2]
    seed = argv[3]
    configuration = utils.get_vsw_agent()
    config_path = Path(__file__).parent.parent.joinpath("conf/genesis.txt").resolve()
    logger.debug('genesis_file: ' + str(config_path))
    endpoint = f'{configuration.get("outbound_transport_protocol")}://{configuration.get("inbound_transport_host")}:{configuration.get("inbound_transport_port")}/'
    log_dir = Path(os.path.expanduser('~'))
    if not os.path.exists(str(log_dir) + f"/.indy_client/wallet/{wallet_name}"):
        os.makedirs(str(log_dir) + f"/.indy_client/wallet/{wallet_name}")
    aries_log_file = str(Path(log_dir).joinpath(f"/.indy_client/wallet/{wallet_name}/{seed}.log").resolve())
    try:
        args = [
            '--endpoint', endpoint,
            '--seed', seed,
            '--accept-taa', '1',
            '--genesis-file', str(config_path),
            '--wallet-type', 'indy',
            '--log-config', logger.aries_config_path,
            '--log-file', aries_log_file,
            '--wallet-name', wallet_name,
            '--wallet-key', wallet_key
        ]
        run_command('provision', args)
    except BaseException:
        pass


if __name__ == '__main__':
    provision(sys.argv)