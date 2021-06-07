import argparse
import json
from typing import List
from urllib.parse import urljoin

import requests
from vsw.commands import exit
import vsw.utils
from vsw.log import Log

vsw_config = vsw.utils.get_vsw_agent()
vsw_repo_config = vsw.utils.get_repo_host()
vsw_url_host = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}'
repo_url_host = vsw_repo_config.get("host")
client_header = {"x-api-key": vsw_config.get("seed")}
repo_header = {"x-api-key": vsw_repo_config.get("x-api-key")}
logger = Log(__name__).logger
timeout = 60


def main(args: List[str]) -> bool:
    try:
        if exit.check_vsw_is_running():
            args = parse_args(args)
            revocation_registry_id = args.rev_reg_id
            credential_revocation_id = args.cred_rev_id
            if not revocation_registry_id or not credential_revocation_id:
                print('vsw: error: the credential registry id and credential revocation id are both required.')
                print_help()
                return

            revoke(revocation_registry_id, credential_revocation_id, args.publish)
    except requests.exceptions.RequestException:
        logger.error(vsw.utils.Constant.NOT_RUNNING_MSG)
    except KeyboardInterrupt:
        print(" ==> Exit revoke!")


def print_help():
    print('Usage:')
    print('vsw revoke [options]')
    print('-reg, --rev_reg_id       Revocation registry identifier')
    print('-rev, --cred_rev_id      The Credential Revocation identifier')


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-reg", "--rev-reg-id", required=False, help="Revocation registry identifier")
    parser.add_argument("-rev", "--cred_rev_id", required=False, help="Credential revocation identifier")
    parser.add_argument("-p", "--publish", required=False, default=True,  help="If publish revocation immediately")

    return parser.parse_args(args)


def revoke(revocation_registry_id, credential_revocation_id, is_publish):
    publish = "false"
    if is_publish:
        publish = "true"
    url = f'{vsw_url_host}/issue-credential/revoke?rev_reg_id={revocation_registry_id}&cred_rev_id={credential_revocation_id}&publish={publish}'
    logger.info(f'The request revoke url: {url}')
    revocation_res = requests.post(url=url, headers=client_header)
    logger.info(revocation_res.text)
    print("Revoke successfully!")


def get_credential_record(cred_ex_id):
    url = urljoin(repo_url_host, f"/issue-credential/records/{cred_ex_id}")
    credential_response = requests.get(url=url, headers=repo_header)
    res = json.loads(credential_response.text)
    return res
