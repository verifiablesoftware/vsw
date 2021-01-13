import argparse
from typing import List

from src.log import Log
import src.utils
import requests

logger = Log().logger


def main(args: List[str]) -> bool:
    logger.info('##### start publish method #########')
    args = parse_args(args)
    upload_url = args.url
    logger.info('url: '+ upload_url)
    repo_endpoint = src.utils.get_repo_host()
    requests.get(repo_endpoint)
    logger.info('######  end to call publish method ##########')


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="The uploaded file url")
    return parser.parse_args(args)
