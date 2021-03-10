import argparse
import json
from typing import List
from rich.console import Console
from terminaltables import AsciiTable
import requests
from urllib3.exceptions import NewConnectionError

from vsw.log import Log
from vsw.utils import get_vsw_agent

logger = Log(__name__).logger
console = Console()


def main(argv: List[str]) -> bool:
    args = parse_args(argv)
    vsw_config = get_vsw_agent()
    try:
        if args.connection:
            get_connections(vsw_config)
        elif args.wallet:
            get_wallet(vsw_config)
        elif args.schema:
            get_schema(vsw_config)
        elif args.status:
            get_status(vsw_config)
        elif args.issue_credential_records:
            get_issue_credential_records(vsw_config)
        elif args.credentials:
            get_credentials(vsw_config)
        elif args.credential_definition:
            get_credential_definition(vsw_config)
        elif args.present_proof:
            get_present_proof(vsw_config)
        else:
            console.print('Usage:')
            console.print('vsw list [options]')
            console.print('-c: list all the connections')
            console.print('-w: list all wallet dids')
            console.print('-sc: list all the schema')
            console.print('-s: see agent status')
            console.print('-i: list all the issue credential records')
            console.print('-p: list all present proof records')
            console.print('-cs: list all the credentials')
            console.print('-cd: list all the credential definitions')
    except NewConnectionError as ce:
        logger.error(str(ce))
        logger.error("Please check if you have executed 'vsw setup' to start agent!")
    except Exception as e:
        logger.error("Failed to execute list: " + str(e))


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--connection', action='store_true')
    parser.add_argument('-w', '--wallet', action='store_true')
    parser.add_argument('-sc', '--schema', action='store_true')
    parser.add_argument('-s', '--status', action='store_true')
    parser.add_argument('-i', '--issue_credential_records', action='store_true')
    parser.add_argument('-p', '--present_proof', action='store_true')
    parser.add_argument('-cs', '--credentials', action='store_true')
    parser.add_argument('-cd', '--credential_definition', action='store_true')
    return parser.parse_args(args)


def get_credential_definition(vsw_config):
    local = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/credential-definitions/created'
    response = requests.get(local)
    res = json.loads(response.text)
    print(res)


def get_credentials(vsw_config):
    local = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/credentials'
    response = requests.get(local)
    res = json.loads(response.text)
    console.log(res)


def get_issue_credential_records(vsw_config):
    local = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/issue-credential/records'
    response = requests.get(local)
    res = json.loads(response.text)
    console.log(res)


def get_status(vsw_config):
    local = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/status'
    response = requests.get(local)
    res = json.loads(response.text)
    console.log(res)


def get_schema(vsw_config):
    local = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/schemas/created'
    response = requests.get(local)
    res = json.loads(response.text)
    print(res)


def get_wallet(vsw_config):
    local = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/wallet/did'
    response = requests.get(local)
    res = json.loads(response.text)
    print_wallet_info(res["results"])


def get_present_proof(vsw_config):
    local = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/present-proof/records'
    response = requests.get(local)
    res = json.loads(response.text)
    console.log(res)


def print_wallet_info(results):
    data = [["public", "did", "verkey"]]
    for row in results:
        data.append(
            [row["public"], row["did"], row["verkey"]]
        )
    table = AsciiTable(data)
    table.title = "Wallet Records"
    print(table.table)


def get_connections(vsw_config):
    local = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/connections'
    response = requests.get(local)
    res = json.loads(response.text)
    print_connection_table(res["results"])


def print_connection_table(results):
    data = [["their_label", "my_did", "connection_id", "created_at", "state"]]
    for row in results:
        data.append(
            [row["their_label"], row["my_did"],
             row["connection_id"], row["created_at"], row["state"]]
        )
    table = AsciiTable(data)
    table.title = "Connection Records"
    print(table.table)
