import argparse
import json
import time
from typing import List

import requests
from vsw.utils import Constant
import vsw.utils
from vsw.log import Log
from multiprocessing.connection import Listener

logger = Log(__name__).logger
timeout = Constant.TIMEOUT


def main(args: List[str]) -> bool:
    args = parse_args(args)
    print(args)
    try:
        if args.connection:
            connection_repo()
        if args.credential_definition:
            do_credential_definition(args.test_schema)

    except KeyboardInterrupt:
        print(" ==> Exit init")


def do_credential_definition(test_schema):
    vsw_config = vsw.utils.get_vsw_agent()
    schema_id = vsw_config.get("schema_id")
    support_revocation = True
    if test_schema:
        schema_id = vsw_config.get("test_schema_id")
        support_revocation = False

    credential_definition_url = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}/credential-definitions'
    res = requests.post(credential_definition_url, json={
        "revocation_registry_size": 100,
        "support_revocation": support_revocation,
        "schema_id": schema_id,
        "tag": "default"
    })
    logger.info(res.text)
    credential_definition_res = json.loads(res.text)
    logger.info(f'Created credential_definition_id: {credential_definition_res["credential_definition_id"]}')


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-cd", "--credential-definition", action='store_true')
    parser.add_argument('-c', '--connection', action='store_true')
    parser.add_argument('-t', '--test-schema', action='store_true')

    return parser.parse_args(args)


def connection_repo():
    address = ('localhost', Constant.PORT_NUMBER)
    listener = Listener(address)
    vsw_config = vsw.utils.get_vsw_agent()
    remove_history_connection(vsw_config)
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

    times = 0
    connection_id = invitation_response["connection_id"]
    while times <= timeout:
        conn = listener.accept()
        msg = conn.recv()
        state = msg["state"]
        conn.close()
        logger.info(f'waiting state change, current state is: {state}')
        if state == 'active':
            logger.info("Created connection successfully!")
            break
        else:
            times += 1;
    if times > timeout:
        remove_connection(connection_id, vsw_config)
        logger.error("Request timeout, there might be some issue during initializing connection.")
    listener.close()


def get_connection(connection_id, vsw_config):
    time.sleep(1)  # wait communicate complete automatically between agents
    url = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/connections/{connection_id}'
    connection_response = requests.get(url)
    res = json.loads(connection_response.text)
    return res


def remove_history_connection(vsw_config):
    schema_url = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}/connections'
    response = requests.get(schema_url)
    results = json.loads(response.text)["results"]
    for result in results:
        schema_url = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}/connections/{result["connection_id"]}/remove'
        requests.post(schema_url)
        logger.info(f"Removed history connection id: {result['connection_id']}")


def remove_connection(connection_id, vsw_config):
    schema_url = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}/connections/{connection_id}/remove'
    requests.post(schema_url)
