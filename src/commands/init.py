from typing import List

import requests

import src.utils
from src.log import Log

logger = Log().logger


def main(args: List[str]) -> bool:
    retrieve_DID()


def retrieve_DID():
    try:
        vsw_agent_host = src.utils.get_vsw_agent_host()
        response = requests.post(vsw_agent_host + "/wallet/did/create")
        logger.info(response.text)
    except:
        logger.error('init failed')
    else:
        logger.info('init successfully!')
