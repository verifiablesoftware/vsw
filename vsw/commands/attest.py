import argparse
import json
import socket
import time
from multiprocessing.connection import Listener
from typing import List
from urllib.parse import urljoin

import requests
import validators

import vsw.utils
from vsw.log import Log
from vsw.utils import Constant
from vsw.commands import exit
vsw_config = vsw.utils.get_vsw_agent()
vsw_url_host = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}'
client_header = {"x-api-key": vsw_config.get("seed")}
logger = Log(__name__).logger
timeout = Constant.TIMEOUT


def main(args: List[str]) -> bool:
    try:
        if exit.check_vsw_is_running():
            args = parse_args(args)
            with open(args.attest_file) as json_file:
                data = json.load(json_file)
                publish(data)
    except requests.exceptions.RequestException:
        logger.error(vsw.utils.Constant.NOT_RUNNING_MSG)
    except ValueError as ve:
        logger.error(ve)
    except KeyboardInterrupt:
        print(" ==> Exit attest!")


def publish(data):
    if "testSpecUrl" in data:
        test_spec_url = data["testSpecUrl"]
        if test_spec_url and not validators.url(test_spec_url):
            print('vsw: error: the testSpecUrl is wrong, please check')
            return
    if "testResultDetailUrl" in data:
        test_result_detail_url = data["testResultDetailUrl"]
        if test_result_detail_url and not validators.url(test_result_detail_url):
            print('vsw: error: the testResultDetailUrl is wrong, please check')
            return
    if "testSpecDid" in data or "testSpecUrl" in data:
        if "testResult" not in data:
            print("vsw: error: the testResult is mandatory if specify testSpecDid or testSpecUrl")
            return
    if "testSpecDid" not in data and "testSpecUrl" not in data and "ranking" not in data:
        print("vsw: error: the rank is mandatory if not specify testSpec")
        return
    issue_credential(data)


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--attest-file", required=True, help="The attestation credential json file path")
    return parser.parse_args(args)


def get_credential_definition_id():
    local = f'http://{vsw_config.get("admin_host")}:{str(vsw_config.get("admin_port"))}/credential-definitions/created?schema_id={vsw_config.get("test_schema_id")}'
    response = requests.get(url=local, headers=client_header)
    logger.info(response.__dict__)
    res = json.loads(response.text)
    if len(res["credential_definition_ids"]) == 0:
        raise ValueError('vsw: error: Not found attest credential definition id!')
    cred_def_id = res["credential_definition_ids"][-1]
    logger.info(f'cred_def_id: {cred_def_id}')
    return cred_def_id


def issue_credential(data):
    address = ('localhost', Constant.PORT_NUMBER)
    listener = Listener(address)
    listener._listener._socket.settimeout(Constant.TIMEOUT)
    offer_response = send_offer(data)
    credential_exchange_id = offer_response["credential_exchange_id"]
    logger.info(f'credential_exchange_id: {credential_exchange_id}')

    while True:
        try:
            conn = listener.accept()
            msg = conn.recv()
            state = msg["state"]
            logger.info(f'waiting state change, current state is: {state}')
            conn.close()
            if state == 'credential_acked':
                print("Congratulation, execute publish successfully!")
                listener.close()
                break
            else:
                time.sleep(0.5)
        except socket.timeout as e:
            print("Request timeout, there might be some issue during publishing")
            logger.error(e)
            listener.close()
            break;


def get_connection():
    vsw_connection_response = requests.get(url=f'{vsw_url_host}/connections?state=active', headers=client_header)
    res = json.loads(vsw_connection_response.text)
    connections = res["results"]
    if len(connections) > 0:
        last_connection = connections[-1]
        return last_connection
    else:
        raise ConnectionError("Not found active vsw connection! Have you executed vsw setup connection?")


def get_public_did():
    url = urljoin(vsw_url_host, "/wallet/did/public")
    response = requests.get(url=url, headers=client_header)
    res = json.loads(response.text)
    return res["result"]["did"]


def send_offer(data):
    tester_did = get_public_did()
    connection = get_connection()
    logger.info(f'holder connection_id: {connection["connection_id"]}')

    test_spec_hash = vsw.utils.generate_digest(data["testSpecUrl"])
    test_result_detail_hash = vsw.utils.generate_digest(data["testResultDetailUrl"])
    send_offer_url = f'{vsw_url_host}/issue-credential/send-offer'
    res = requests.post(url=send_offer_url, headers=client_header, json={
        "comment": "execute vsw publish cli",
        "auto_remove": False,
        "trace": True,
        "connection_id": connection["connection_id"],
        "schema_id": data["schemaID"] or vsw_config.get("test_schema_id"),
        "schema_name": data["schemaName"] or vsw_config.get("test_schema_name"),
        "schema_version": data["schemaVersion"] or vsw_config.get("test_schema_version"),
        "issuer_did": tester_did,
        "cred_def_id": get_credential_definition_id(),
        "credential_preview": {
            "@type": f"did:sov:{tester_did};spec/issue-credential/1.0/credential-preview",
            "attributes": [
                {
                    "name": "testerDid",
                    "value": tester_did
                },
                {
                    "name": "softwareDid",
                    "value": data["softwareDid"]
                },
                {
                    "name": "testSpecDid",
                    "value": data.get("testSpecDid", "")
                },
                {
                    "name": "testSpecUrl",
                    "value": data.get("testSpecUrl", "")
                },
                {
                    "name": "testSpecHash",
                    "value": test_spec_hash
                },
                {
                    "name": "testResult",
                    "value": data.get("testResult", "")
                },
                {
                    "name": "testResultDetailDid",
                    "value": data.get("testResultDetailDid", "")
                },
                {
                    "name": "testResultDetailUrl",
                    "value": data.get("testResultDetailUrl", "")
                },
                {
                    "name": "testResultDetailHash",
                    "value": test_result_detail_hash
                },
                {
                    "name": "ranking",
                    "value": data.get("ranking", "")
                },
                {
                    "name": "comments",
                    "value": data.get("comments", "")
                }
            ]
        },
    })
    logger.info(res.__dict__)
    return json.loads(res.text)
