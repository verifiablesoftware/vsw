import argparse
import json
from typing import List
from urllib.parse import urljoin
from rich.console import Console
import requests
from vsw.dao import vsw_dao
from vsw.log import Log
from vsw.utils import get_vsw_agent, Constant
from vsw.commands import exit
logger = Log(__name__).logger
console = Console()
vsw_config = get_vsw_agent()
client_header = {"x-api-key": vsw_config.get("seed")}


def main(argv: List[str]) -> bool:
    if exit.check_vsw_is_running():
        args = parse_args(argv)
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
                get_credentials(vsw_config)
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
    response = requests.get(url=local, headers=client_header)
    res = json.loads(response.text)
    console.print(json.dumps(res, indent=4, sort_keys=True))


def get_credentials(vsw_config):
    did = get_public_did(vsw_config)
    res = vsw_dao.get_credential_by_issuer_did(did)
    results = []
    for row in res:
        json_object = json.loads(row[0])
        results.append(json_object)

    console.print(json.dumps({
        "results": results
    }, indent=4, sort_keys=True))


def get_public_did(vsw_config):
    url = urljoin(f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}', "/wallet/did/public")
    response = requests.get(url=url, headers=client_header)
    res = json.loads(response.text)
    return res["result"]["did"]


def get_status(vsw_config):
    local = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/status'
    response = requests.get(url=local, headers=client_header)
    res = json.loads(response.text)
    console.print(json.dumps(res, indent=4, sort_keys=True))


def get_schema(vsw_config):
    schema_id = vsw_config.get("schema_id")
    local = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/schemas/{schema_id}'
    response = requests.get(url=local, headers=client_header)
    res = json.loads(response.text)
    console.print(f"======vsw software certificate schema_id: {schema_id}======")
    console.print(json.dumps(res, indent=4, sort_keys=True))

    test_schema_id = vsw_config.get("test_schema_id")
    test_local = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/schemas/{test_schema_id}'
    test_response = requests.get(url=test_local, headers=client_header)
    test_res = json.loads(test_response.text)
    console.print(f"======vsw attest schema_id: {test_schema_id}======")
    console.print(json.dumps(test_res, indent=4, sort_keys=True))


def get_wallet(vsw_config):
    local = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/wallet/did'
    response = requests.get(url=local, headers=client_header)
    res = json.loads(response.text)
    console.print(json.dumps(res, indent=4, sort_keys=True))


def get_present_proof(vsw_config):
    local = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/present-proof/records'
    response = requests.get(url=local, headers=client_header)
    res = json.loads(response.text)
    sorted_res = res["results"]
    sorted_res.sort(key=lambda p: p["created_at"])
    if len(sorted_res) > 0:
        console.print("======presentation_request========")
        console.print(json.dumps(sorted_res[-1]["presentation_request"], indent=4, sort_keys=True))
        console.print("======requested_proof========")
        console.print(json.dumps(sorted_res[-1]["presentation"]["requested_proof"], indent=4, sort_keys=True))
    else:
        console.print(json.dumps(res))


def get_connections(vsw_config):
    local = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/connections'
    response = requests.get(url=local, headers=client_header)
    res = json.loads(response.text)
    console.print(json.dumps(res, indent=4, sort_keys=True))