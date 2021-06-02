import argparse
import json
import socket
import time
from typing import List

import requests
from vsw.utils import Constant
import vsw.utils
from vsw.log import Log
from multiprocessing.connection import Listener

logger = Log(__name__).logger
timeout = Constant.TIMEOUT
vsw_config = vsw.utils.get_vsw_agent()
software_certificate = vsw_config.get("schema_name")
test_certificate = vsw_config.get("test_schema_name")


def main(args: List[str]) -> bool:
    args = parse_args(args)
    print(args)
    try:
        if args.connection:
            connection_repo()
        if args.credential_definition:
            do_credential_definition(args.schema)
    except requests.exceptions.RequestException:
        logger.error(vsw.utils.Constant.NOT_RUNNING_MSG)
    except KeyboardInterrupt:
        print(" ==> Exit init")


def get_schema_id_by_name(vsw_config, schema_name):
    if schema_name == vsw_config.get("test_schema_name"):
        return vsw_config.get("test_schema_id")
    else:
        return vsw_config.get("schema_id")


def do_credential_definition(schema_name):
    if schema_name != software_certificate and schema_name != test_certificate:
        print(f"vsw: error: the schema name must be either {software_certificate} or {test_certificate}")
        return;
    schema_id = get_schema_id_by_name(vsw_config, schema_name)

    credential_definition_url = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}/credential-definitions'
    res = requests.post(credential_definition_url, json={
        "revocation_registry_size": 100,
        "support_revocation": True,
        "schema_id": schema_id,
        "tag": "default"
    })
    credential_definition_res = json.loads(res.text)
    logger.info(f'Created credential definition id: {credential_definition_res["credential_definition_id"]}')


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-cd", "--credential-definition", action='store_true')
    parser.add_argument('-c', '--connection', action='store_true')
    parser.add_argument('-s', '--schema', default=software_certificate, help="The schema name")

    return parser.parse_args(args)


def connection_repo():
    address = ('localhost', Constant.PORT_NUMBER)
    listener = Listener(address)
    listener._listener._socket.settimeout(Constant.TIMEOUT)
    vsw_config = vsw.utils.get_vsw_agent()
    remove_history_connection(vsw_config)
    vsw_repo_config = vsw.utils.get_repo_host()
    vsw_repo_url = f'{vsw_repo_config.get("host")}/connections/create-invitation?alias={vsw_repo_config.get("label")}&auto_accept=true'
    logger.debug(f'Create invitation to: {vsw_repo_url}')
    response = requests.post(vsw_repo_url)
    res = json.loads(response.text)
    logger.debug(res)

    local_url = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/connections/receive-invitation?alias={vsw_config.get("label")}'
    logger.debug(f'Receive invitation {local_url}')
    invitation = res["invitation"]
    body = {
        "label": invitation["label"],
        "serviceEndpoint": invitation["serviceEndpoint"],
        "recipientKeys": invitation["recipientKeys"],
        "@id": invitation["@id"]
    }
    ss = requests.post(local_url, json=body)
    invitation_response = json.loads(ss.text)
    logger.debug(invitation_response)

    connection_id = invitation_response["connection_id"]
    while True:
        try:
            conn = listener.accept()
            msg = conn.recv()
            state = msg["state"]
            conn.close()
            logger.info(f'waiting state change, current state is: {state}')
            if state == 'active':
                logger.info("Created connection successfully!")
                listener.close()
                break
            else:
                time.sleep(0.5)
        except socket.timeout:
            remove_connection(connection_id, vsw_config)
            logger.error("Request timeout, there might be some issue during initializing connection.")
            listener.close()
            break;


def remove_history_connection(vsw_config):
    schema_url = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}/connections'
    response = requests.get(schema_url)
    results = json.loads(response.text)["results"]
    for result in results:
        schema_url = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}/connections/{result["connection_id"]}/remove'
        requests.post(schema_url)
        logger.debug(f"Removed history connection id: {result['connection_id']}")


def remove_connection(connection_id, vsw_config):
    schema_url = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}/connections/{connection_id}/remove'
    requests.post(schema_url)
