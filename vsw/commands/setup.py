from typing import List

import requests
from aries_cloudagent_vsw.commands import run_command

import vsw.utils
from vsw import utils
from vsw.log import Log

logger = Log(__name__).logger


def main(args: List[str]) -> bool:
    start_agent()
    retrieve_DID()


def start_agent():
    configuration = utils.get_vsw_agent()
    run_command('start', ['--admin', configuration.get("admin_host"), configuration.get("admin_port"),
                          '--inbound-transport', configuration.get("inbound_transport_protocol"), configuration.get("inbound_transport_host"), configuration.get("inbound_transport_port"),
                          '--outbound-transport', configuration.get('outbound_transport_protocol'),
                          '--endpoint', configuration.get("endpoint"),
                          '--label', configuration.get("label"),
                          # '--seed', configuration.get("seed"),
                          # '--genesis-url', configuration.get("genesis_url"),
                          '--webhook-url', configuration.get("webhook_url"),
                          # '--wallet-type', configuration.get("wallet_type"),
                          # '--wallet-name', configuration.get("wallet_name"),
                          # '--wallet-key', configuration.get("wallet-key"),
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
