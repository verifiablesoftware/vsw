import argparse
import json
from typing import List

import requests

import vsw.utils
from vsw.log import Log

logger = Log(__name__).logger


def main(args: List[str]) -> bool:
    args = parse_args(args)
    if args.connection:
        connection_repo()
    if args.schema:
        do_schema(args.schema)


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--schema", required=False, help="The schema name")
    parser.add_argument('-c', '--connection', action='store_true')
    return parser.parse_args(args)


def do_schema(schema):
    vsw_config = vsw.utils.get_vsw_agent()
    schema_url = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}/schemas'
    response = requests.post(schema_url, json={
        "schema_version": "0.2",
        "attributes": ["developer-did","software-version","software-name","software-did", "hash",
                       "alt-hash", "url", "alt-url1", "alt-url2"],
        "schema_name": schema
    })
    schema_res = json.loads(response.text)
    schema_id = schema_res["schema_id"]
    logger.info(f'Created schema_id: {schema_id}')

    credential_definition_url = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}/credential-definitions'
    res = requests.post(credential_definition_url, json={
        "revocation_registry_size": 0,
        "support_revocation": False,
        "schema_id": schema_id,
        "tag": "default"
    })
    credential_definition_res = json.loads(res.text)
    logger.info(f'Created credential_definition_id: {credential_definition_res["credential_definition_id"]}')


def connection_repo():
    try:
        vsw_config = vsw.utils.get_vsw_agent()
        vsw_repo_config = vsw.utils.get_repo_host()
        vsw_repo_url = f'{vsw_repo_config.get("host")}/connections/create-invitation'
        logger.info(f'Create invitation to: {vsw_repo_url}')
        response = requests.post(vsw_repo_url, {
            "alias": vsw_config.get("label"),
            "auto_accept": True,
            "public": True
            # "multi_use": True
        })
        res = json.loads(response.text)
        print(res)

        local_url = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/connections/receive-invitation?alias={vsw_config.get("label")}'
        logger.info(f'Receive invitation {local_url}')
        invitation = res["invitation"]
        body = {
            "label": invitation["label"],
            "serviceEndpoint": invitation["serviceEndpoint"],
            "recipientKeys": invitation["recipientKeys"],
            "@id": invitation["@id"]
        }
        ss = requests.post(local_url, json=body)
        print(ss)
        logger.info('Created connection with Repo')
    except Exception as err:
        logger.error('connection vsw-repo failed', err)
