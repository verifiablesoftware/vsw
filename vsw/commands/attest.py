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

vsw_config = vsw.utils.get_vsw_agent()
vsw_repo_config = vsw.utils.get_repo_host()
vsw_url_host = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}'
repo_url_host = vsw_repo_config.get("host")
logger = Log(__name__).logger
timeout = Constant.TIMEOUT


def main(args: List[str]) -> bool:
    try:
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
    response = requests.get(local)
    res = json.loads(response.text)
    if len(res["credential_definition_ids"]) == 0:
        raise ValueError('Not found attest credential definition id!')
    cred_def_id = res["credential_definition_ids"][-1]
    logger.info(f'cred_def_id: {cred_def_id}')
    return cred_def_id


def issue_credential(data):
    logger.info("executing publish, please waiting for response")
    address = ('localhost', Constant.PORT_NUMBER)
    listener = Listener(address)
    listener._listener._socket.settimeout(Constant.TIMEOUT)
    proposal_response = send_proposal(data)
    credential_exchange_id = proposal_response["credential_exchange_id"]
    logger.info(f'credential_exchange_id: {credential_exchange_id}')

    while True:
        try:
            conn = listener.accept()
            msg = conn.recv()
            state = msg["state"]
            logger.info(f'waiting state change, current state is: {state}')
            conn.close()
            if state == 'credential_acked':
                logger.info("Congratulation, execute publish successfully!")
                listener.close()
                break
            else:
                time.sleep(0.5)
        except socket.timeout:
            remove_credential(credential_exchange_id)
            logger.error("Request timeout, there might be some issue during publishing")
            listener.close()
            break;


def remove_credential(credential_exchange_id):
    url = urljoin(repo_url_host, f"/issue-credential/records/{credential_exchange_id}/remove")
    requests.post(url)


def get_repo_connection():
    vsw_connection_response = requests.get(f'{vsw_url_host}/connections?state=active')
    res = json.loads(vsw_connection_response.text)
    connections = res["results"]
    if len(connections) > 0:
        last_connection = connections[-1]
        repo_connection_response = requests.get(
            f'{repo_url_host}/connections?state=active&my_did={last_connection["their_did"]}&their_did={last_connection["my_did"]}')
        repo_res = json.loads(repo_connection_response.text)
        repo_connections = repo_res["results"]
        if len(repo_connections) > 0:
            return repo_connections[-1]
        else:
            raise ConnectionError("Not found related repo active connection!")
    else:
        raise ConnectionError("Not found active vsw connection! Have you executed vsw init -c?")


def get_public_did():
    url = urljoin(vsw_url_host, "/wallet/did/public")
    response = requests.get(url)
    res = json.loads(response.text)
    return res["result"]["did"]


def send_proposal(data):
    tester_did = get_public_did()
    connection = get_repo_connection()
    logger.info(f'holder connection_id: {connection["connection_id"]}')

    test_spec_hash = vsw.utils.generate_digest(data["testSpecUrl"])
    test_result_detail_hash = vsw.utils.generate_digest(data["testResultDetailUrl"])
    vsw_repo_url = f'{repo_url_host}/issue-credential/send-proposal'
    res = requests.post(vsw_repo_url, json={
        "comment": "execute vsw publish cli",
        "auto_remove": False,
        "trace": True,
        "connection_id": connection["connection_id"],
        "schema_id": data["schemaID"] or vsw_config.get("test_schema_id"),
        "schema_name": data["schemaName"] or vsw_config.get("test_schema_name"),
        "schema_version": data["schemaVersion"] or vsw_config.get("test_schema_version"),
        "issuer_did": tester_did,
        "cred_def_id": get_credential_definition_id(),
        "credential_proposal": {
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
                    "value": data["testSpecDid"]
                },
                {
                    "name": "testSpecUrl",
                    "value": data["testSpecUrl"]
                },
                {
                    "name": "testSpecHash",
                    "value": test_spec_hash
                },
                {
                    "name": "testResult",
                    "value": data["testResult"]
                },
                {
                    "name": "testResultDetailDid",
                    "value": data["testResultDetailDid"]
                },
                {
                    "name": "testResultDetailUrl",
                    "value": data["testResultDetailUrl"]
                },
                {
                    "name": "testResultDetailHash",
                    "value": test_result_detail_hash
                },
                {
                    "name": "ranking",
                    "value": data["ranking"]
                },
                {
                    "name": "comments",
                    "value": data["comments"]
                }
            ]
        },
    })
    return json.loads(res.text)
