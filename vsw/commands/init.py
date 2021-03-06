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
vsw_repo_config = vsw.utils.get_repo_host()
client_header = {"x-api-key": vsw_config.get("seed")}
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


def check_credential_definition(schema_id):
    cd_check_url = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}/credential-definitions/created?schema_id={schema_id}'
    resp = requests.get(url=cd_check_url, headers=client_header)
    check_res = json.loads(resp.text)
    if len(check_res["credential_definition_ids"]) > 0:
        return check_res["credential_definition_ids"][0]
    else:
        return None


def do_credential_definition(schema_name):
    if schema_name != software_certificate and schema_name != test_certificate:
        print(f"vsw: error: the schema name must be either {software_certificate} or {test_certificate}")
        return;
    schema_id = get_schema_id_by_name(vsw_config, schema_name)
    # check if created
    check_result = check_credential_definition(schema_id)
    if check_result:
        print(f'vsw: error: creddef already existed, {check_result}')
        return;
    credential_definition_url = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}/credential-definitions'
    res = requests.post(url=credential_definition_url, json={
        "revocation_registry_size": 100,
        "support_revocation": True,
        "schema_id": schema_id,
        "tag": "default"
    }, headers=client_header)
    logger.info(res.text)
    credential_definition_res = json.loads(res.text)
    logger.info(credential_definition_res)
    print(f'Created credential definition id: {credential_definition_res["credential_definition_id"]}')


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
    remove_history_connection(vsw_config)
    vsw_repo_url = f'{vsw_repo_config.get("host")}/controller/invitation'
    logger.info(f'Create invitation to: {vsw_repo_url}')
    response = requests.get(url=vsw_repo_url)
    logger.info(response.text)
    res = json.loads(response.text)
    local_url = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/connections/receive-invitation?alias={vsw_config.get("label")}'
    logger.info(f'Receive invitation {local_url}')
    invitation = res["invitation"]
    body = {
        "label": invitation["label"],
        "serviceEndpoint": invitation["serviceEndpoint"],
        "recipientKeys": invitation["recipientKeys"],
        "@id": invitation["@id"]
    }
    ss = requests.post(url=local_url, json=body, headers=client_header)
    logger.info(ss.text)
    invitation_response = json.loads(ss.text)

    connection_id = invitation_response["connection_id"]
    while True:
        try:
            conn = listener.accept()
            msg = conn.recv()
            state = msg["state"]
            conn.close()
            logger.info(f'waiting state change, current state is: {state}')
            if state == 'active':
                print("Created connection successfully!")
                listener.close()
                break
            else:
                time.sleep(0.5)
        except socket.timeout as e:
            remove_connection(connection_id, vsw_config)
            logger.error(e)
            print("vsw: error: request timeout, there might be some issue during initializing connection.")
            listener.close()
            break;


def remove_history_connection(vsw_config):
    schema_url = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}/connections'
    response = requests.get(url=schema_url, headers=client_header)
    results = json.loads(response.text)["results"]
    for result in results:
        schema_url = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}/connections/{result["connection_id"]}/remove'
        requests.post(url=schema_url, headers=client_header)
        logger.info(f"Removed history connection id: {result['connection_id']}")


def remove_connection(connection_id, vsw_config):
    schema_url = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}/connections/{connection_id}/remove'
    requests.post(url=schema_url, headers=client_header)
