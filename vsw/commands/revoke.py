import argparse
import json
from typing import List
from urllib.parse import urljoin

import requests

import vsw.utils
from vsw.log import Log

vsw_config = vsw.utils.get_vsw_agent()
vsw_repo_config = vsw.utils.get_repo_host()
vsw_url_host = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}'
repo_url_host = vsw_repo_config.get("host")
logger = Log(__name__).logger
timeout = 60


def main(args: List[str]) -> bool:
    try:
        args = parse_args(args)
        credential_exchange_id = args.credential_exchange_id
        credential_registry_id = args.credential_registry_id
        credential_revocation_id = args.credential_revocation_id
        if not credential_exchange_id and not credential_registry_id and not credential_revocation_id:
            print('vsw: error: either the credential exchange id, or credential registry id and credential '
                  'revocation id are required.')
            print_help()
            return
        elif not credential_exchange_id:
            if not credential_registry_id or not credential_revocation_id:
                print('vsw: error: the credential registry id and credential revocation id are both required.')
                print_help()
                return

        revoke(credential_exchange_id, credential_registry_id, credential_revocation_id, args.publish)
    except requests.exceptions.RequestException:
        logger.error(vsw.utils.Constant.NOT_RUNNING_MSG)
    except KeyboardInterrupt:
        print(" ==> Exit revoke!")


def print_help():
    print('Usage:')
    print('vsw revoke [options]')
    print('-cei, --credential-exchange-id         The Credential Exchange Id')
    print('-reg, --credential-registry-id         The Credential Registry ID')
    print('-rev, --credential-revocation-id       The Credential Revocation ID')


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-cei", "--credential-exchange-id", required=False, help="The credential Exchange ID")
    parser.add_argument("-reg", "--credential-registry-id", required=False, help="The Credential Registry ID ")
    parser.add_argument("-rev", "--credential-revocation-id", required=False, help="The Credential Revocation ID")
    parser.add_argument("-p", "--publish", required=False, default=True,  help="If publish revocation immediately")

    return parser.parse_args(args)


def revoke(credential_exchange_id, credential_registry_id, credential_revocation_id, is_publish):
    logger.info("executing revoke, please waiting for response")
    if credential_exchange_id:
        res = get_credential_record(credential_exchange_id)
        credential_registry_id = res["revoc_reg_id"]
        credential_revocation_id = res["revocation_id"]
    publish = "false"
    if is_publish:
        publish = "true"
    url = f'{vsw_url_host}/issue-credential/revoke?rev_reg_id={credential_registry_id}&cred_rev_id={credential_revocation_id}&publish={publish}'
    logger.debug(f'The request revoke url: {url}')
    revocation_res = requests.post(url)
    json.loads(revocation_res.text)
    logger.info("Revoke successfully!")


def get_credential_record(cred_ex_id):
    url = urljoin(repo_url_host, f"/issue-credential/records/{cred_ex_id}")
    credential_response = requests.get(url)
    res = json.loads(credential_response.text)
    return res
