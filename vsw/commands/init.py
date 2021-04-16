import argparse
import json
import time
from typing import List

import requests

import vsw.utils
from vsw.log import Log

logger = Log(__name__).logger
timeout = 60


def main(args: List[str]) -> bool:
    args = parse_args(args)
    try:
        if args.connection:
            connection_repo()
        if args.credential_definition:
            do_credential_definition()

    except KeyboardInterrupt:
        print(" ==> Exit init")


def do_credential_definition():
    vsw_config = vsw.utils.get_vsw_agent()
    credential_definition_url = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}/credential-definitions'
    res = requests.post(credential_definition_url, json={
        "revocation_registry_size": 100,
        "support_revocation": True,
        "schema_id": vsw_config.get("schema_id"),
        "tag": "default"
    })
    logger.info(res.text)
    credential_definition_res = json.loads(res.text)
    logger.info(f'Created credential_definition_id: {credential_definition_res["credential_definition_id"]}')


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-cd", "--credential-definition", action='store_true')
    parser.add_argument('-c', '--connection', action='store_true')
    return parser.parse_args(args)


def connection_repo():
    try:
        vsw_config = vsw.utils.get_vsw_agent()
        vsw_repo_config = vsw.utils.get_repo_host()
        vsw_repo_url = f'{vsw_repo_config.get("host")}/connections/create-invitation?alias={vsw_repo_config.get("label")}&auto_accept=true'
        logger.info(f'Create invitation to: {vsw_repo_url}')
        response = requests.post(vsw_repo_url)
        res = json.loads(response.text)
        logger.info(res)

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
        invitation_response = json.loads(ss.text)
        logger.info(invitation_response)
        connection_id = invitation_response["connection_id"]
        times = 0
        while times <= timeout:
            connection_res = get_connection(connection_id, vsw_config)
            logger.info(f'waiting state update, current state: {connection_res["state"]}')
            if connection_res["state"] == "active":
                logger.info('Created connection with Repo')
                break;
            else:
                times += 1;
        if times > timeout:
            logger.error("Sorry, there might be some issue during initializing connection.")

    except BaseException:
        logger.error('connection vsw-repo failed')


def get_connection(connection_id, vsw_config):
    time.sleep(1)  # wait communicate complete automatically between agents
    url = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/connections/{connection_id}'
    connection_response = requests.get(url)
    res = json.loads(connection_response.text)
    return res