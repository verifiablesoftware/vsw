from typing import List

import requests
from aries_cloudagent_vsw.commands import run_command

import vsw.utils
from vsw.log import Log

logger = Log(__name__).logger


def main(args: List[str]) -> bool:
    start_agent()
    retrieve_DID()


def start_agent():

    run_command('start', ['--admin', '127.0.0.1', '8021',
                          '--inbound-transport', 'http', '0.0.0.0', '8020',
                          '--outbound-transport', 'http',
                          '--endpoint', 'http://localhost:8020',
                          '--label', 'vsw-agent',
                          # '--seed', 'my_seed_000000000000000000009216',
                          # '--genesis-url', 'https://raw.githubusercontent.com/sovrin-foundation/sovrin/master/sovrin/pool_transactions_sandbox_genesis',
                          # '--webhook-url', 'http://127.0.0.1:8021/webhooks',
                          # '--wallet-type', 'indy',
                          # '--wallet-name', 'myWallet',
                          # '--wallet-key', 'walletKey',
                          # '--public-invites',
                          # '--auto-accept-invites',
                          # '--auto-accept-requests',
                          # '--auto-ping-connection',
                          # '--auto-respond-messages',
                          # '--auto-respond-credential-offer',
                          # '--auto-respond-presentation-request',
                          # '--auto-verify-presentation',
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
