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
    parser.add_argument("--schema", required=False, help="The schema")
    parser.add_argument('-c', '--connection', action='store_true')
    return parser.parse_args(args)


def do_schema(schema):
    vsw_config = vsw.utils.get_vsw_agent()
    schema_url = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}/schemas'
    response = requests.post(schema_url, json={
        "schema_version": "1.0",
        "attributes": ["score"],
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

        local = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/connections/create-invitation'
        logger.info(f'Create invitation to: {local}')
        response = requests.post(local, {
            "alias": vsw_config.get("label"),
            "auto_accept": True,
            # "public": True,
            # "multi_use": False
        })
        res = json.loads(response.text)
        logger.info(res)

        vsw_repo_config = vsw.utils.get_repo_host()
        vsw_repo_url = f'{vsw_repo_config.get("host")}/connections/receive-invitation?alias={vsw_config.get("label")}'
        logger.info(f'Receive invitation {vsw_repo_url}')
        invitation = res["invitation"]
        body = {
            "label": invitation["label"],
            "serviceEndpoint": invitation["serviceEndpoint"],
            "recipientKeys": invitation["recipientKeys"],
            "@id": invitation["@id"]
        }
        receive_res = requests.post(vsw_repo_url, json=body)
        print('receive_res:', receive_res.__dict__)
        logger.info(receive_res)
    except Exception as err:
        logger.error('connection vsw-repo failed', err)
