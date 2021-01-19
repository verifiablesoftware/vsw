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
