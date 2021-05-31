import sys
from pathlib import Path

from aries_cloudagent_vsw.commands import run_command

from vsw import utils
from vsw.log import Log

logger = Log(__name__).logger


def start_agent(argv):
    wallet_name = argv[1]
    wallet_key = argv[2]
    seed = argv[3]
    configuration = utils.get_vsw_agent()
    config_path = Path(__file__).parent.parent.joinpath("conf/genesis.txt").resolve()
    admin_port = configuration.get("admin_port")
    transport_port = configuration.get("inbound_transport_port")
    logger.debug('genesis_file: ' + str(config_path))
    try:
        args = ['--admin', configuration.get("admin_host"), admin_port,
                '--inbound-transport', configuration.get("inbound_transport_protocol"),
                configuration.get("inbound_transport_host"), transport_port,
                '--outbound-transport', configuration.get('outbound_transport_protocol'),
                '--endpoint', configuration.get("endpoint"),
                '--label', configuration.get("label"),
                '--seed', seed,
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
        run_command('start', args)
    except BaseException as error:
        logger.error("started vsw failed.")
        print('An exception occurred: {}'.format(error))


if __name__ == '__main__':
    start_agent(sys.argv)