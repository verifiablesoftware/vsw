import argparse
import json
from typing import List
from urllib.parse import urljoin
from rich.console import Console
import requests

from vsw.log import Log
from vsw.utils import get_vsw_agent, get_repo_host, Constant

logger = Log(__name__).logger
console = Console()


def main(argv: List[str]) -> bool:
    args = parse_args(argv)
    vsw_config = get_vsw_agent()
    vsw_repo_config = get_repo_host()
    repo_url_host = vsw_repo_config.get("host")
    try:
        if args.connection:
            get_connections(vsw_config)
        elif args.wallet:
            get_wallet(vsw_config)
        elif args.schema:
            get_schema(vsw_config)
        elif args.status:
            get_status(vsw_config)
        elif args.credentials:
            get_credentials(repo_url_host, vsw_config)
        elif args.credential_definition:
            get_credential_definition(vsw_config)
        elif args.present_proof:
            get_present_proof(vsw_config)
        else:
            console.print('Usage:')
            console.print('vsw list [options]')
            console.print('-c: list all connections')
            console.print('-w: list all DIDs in the wallet')
            console.print('-sc: list all supported schema')
            console.print('-s: show agent status')
            console.print('-p: list all presentation proof records')
            console.print('-cs: list all credentials issued by the current DID')
            console.print('-cd: list all credential definitions registered by the current DID')
    except KeyboardInterrupt:
        print(" ==> Exit list!")
    except requests.exceptions.RequestException:
        logger.error(Constant.NOT_RUNNING_MSG)
    except Exception as e:
        logger.error("Failed to execute list: " + str(e))


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--connection', action='store_true')
    parser.add_argument('-w', '--wallet', action='store_true')
    parser.add_argument('-sc', '--schema', action='store_true')
    parser.add_argument('-s', '--status', action='store_true')
    parser.add_argument('-p', '--present_proof', action='store_true')
    parser.add_argument('-cs', '--credentials', action='store_true')
    parser.add_argument('-cd', '--credential_definition', action='store_true')
    return parser.parse_args(args)


def get_credential_definition(vsw_config):
    did = get_public_did(vsw_config)
    local = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/credential-definitions/created?issuer_did={did}'
    response = requests.get(local)
    res = json.loads(response.text)
    console.print(res)


def get_credentials(repo_url_host, vsw_config):
    did = get_public_did(vsw_config)
    repo = urljoin(f'{repo_url_host}', '/credentials?wql={"issuer_did":"'+did+'"}')
    response = requests.get(repo)
    res = json.loads(response.text)
    console.print(res)


def get_public_did(vsw_config):
    url = urljoin(f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}', "/wallet/did/public")
    response = requests.get(url)
    res = json.loads(response.text)
    return res["result"]["did"]


def get_status(vsw_config):
    local = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/status'
    response = requests.get(local)
    res = json.loads(response.text)
    console.print(res)


def get_schema(vsw_config):
    schema_id = vsw_config.get("schema_id")
    local = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/schemas/{schema_id}'
    response = requests.get(local)
    res = json.loads(response.text)
    console.print(f"======vsw software certificate schema_id: {schema_id}======")
    console.print(res)

    test_schema_id = vsw_config.get("test_schema_id")
    test_local = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/schemas/{test_schema_id}'
    test_response = requests.get(test_local)
    test_res = json.loads(test_response.text)
    console.print(f"======vsw attest schema_id: {test_schema_id}======")
    console.print(test_res)


def get_wallet(vsw_config):
    local = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/wallet/did'
    response = requests.get(local)
    res = json.loads(response.text)
    console.print(res)


def get_present_proof(vsw_config):
    local = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/present-proof/records'
    response = requests.get(local)
    res = json.loads(response.text)
    console.print(res)


def get_connections(vsw_config):
    local = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/connections'
    response = requests.get(local)
    res = json.loads(response.text)
    console.print(res)

