import argparse
import json
import time
from typing import List
from vsw.log import Log
from urllib.parse import urljoin
import vsw.utils
from urllib import parse
import requests
import validators
from vsw.utils import Constant
from version_parser import Version
from multiprocessing.connection import Listener
from vsw.commands import attest

vsw_config = vsw.utils.get_vsw_agent()
vsw_repo_config = vsw.utils.get_repo_host()
vsw_url_host = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}'
repo_url_host = vsw_repo_config.get("host")
logger = Log(__name__).logger
timeout = Constant.TIMEOUT


def main(args: List[str]) -> bool:
    try:
        args = parse_args(args)
        with open(args.cred_file) as json_file:
            data = json.load(json_file)
            if args.schema == vsw_config.get("test_schema_name"):
                attest.publish(data)
            else:
                software_version = data["softwareVersion"]
                software_url = data["softwareUrl"]
                if check_version(software_version) is False:
                    return;
                if software_url and not validators.url(software_url):
                    print('The software package url is wrong, please check')
                    return
                issue_credential(data)
    except ConnectionError as e:
        logger.error(str(e))
    except KeyboardInterrupt:
        print(" ==> Exit publish!")


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cred-file", required=True, help="The software credential json file path")
    parser.add_argument('-s', '--schema', default='software-certificate',
                        required=True, help="The schema name")
    return parser.parse_args(args)


def check_version(software_version):
    try:
        Version(software_version)
    except ValueError:
        print("The software version format is incorrect. the correct format should be 'MAJOR.MINOR.PATCH'")
        return False
    return True


def issue_credential(data):
    logger.info("executing publish, please waiting for response")
    address = ('localhost', Constant.PORT_NUMBER)
    listener = Listener(address)
    proposal_response = send_proposal(data)
    credential_exchange_id = proposal_response["credential_exchange_id"]
    logger.info(f'credential_exchange_id: {credential_exchange_id}')

    times = 0
    while times <= timeout:
        conn = listener.accept()
        msg = conn.recv()
        state = msg["state"]
        logger.info(f'waiting state change, current state is: {state}')
        conn.close()
        if state == 'credential_acked':
            logger.info("Congratulation, execute publish successfully!")
            break
        else:
            times += 1;
    listener.close()
    if times > timeout:
        remove_credential(credential_exchange_id)
        logger.error("Request timeout, there might be some issue during publishing")


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


def get_credential(developer_did, software_name):
    wql = json.dumps({"attr::developerdid::value": developer_did, "attr::softwarename::value": software_name})
    repo_url = f"{repo_url_host}/credentials?wql={parse.quote(wql)}"
    res = requests.get(repo_url)
    try:
        return json.loads(res.text)["results"]
    except BaseException:
        return None


def is_same_version(software_version, exist_software_version):
    if exist_software_version is None:
        return False
    v1 = Version(software_version)
    v2 = Version(exist_software_version)
    if v1.get_major_version() == v2.get_major_version() and v1.get_minor_version() == v2.get_minor_version():
        return True
    else:
        return False


def generate_software_did(developer_did, software_name, software_version, download_url):
    credentials = get_credential(developer_did, software_name)
    if len(credentials) > 0:
        logger.info(f'The software name {software_name} is existed.')
        same_version = False
        for credential in credentials:
            attrs = credential["attrs"]
            same_version = is_same_version(software_version, attrs["softwareVersion"])
            if same_version:
                logger.info(f'Existed softwareDid: {attrs["softwareDid"]}')
                return attrs["softwareDid"]
        if same_version is False:
            return generate_new_did(download_url)
    else:
        return generate_new_did(download_url)


def generate_new_did(download_url):
    # Create a DID
    create_did_res = requests.post(urljoin(vsw_url_host, "/wallet/did/create"))
    res = json.loads(create_did_res.text)
    did = res["result"]["did"]
    verkey = res["result"]["verkey"]
    # Write DID to ledger by NYM
    ledger_res = requests.post(urljoin(vsw_url_host, f"/ledger/register-nym?did={did}&verkey={verkey}"))
    write_did_ledger_res = json.loads(ledger_res.text)
    if write_did_ledger_res["success"] is False:
        logger.err("write did to ledger failed!")
        raise Exception('write did to ledger failed!')
    # Set DID Endpoint
    did_endpoint_res = requests.post(urljoin(vsw_url_host, f"/wallet/set-did-endpoint"), json={
        "did": did,
        "endpoint_type": "Endpoint",
        "endpoint": download_url  # not support :h1 format
    })
    logger.info(f'Created new software-did: {did}')
    return did


def send_proposal(data):
    developer_did = get_public_did()
    connection = get_repo_connection()
    logger.info(f'holder connection_id: {connection["connection_id"]}')

    digest = vsw.utils.generate_digest(data["softwareUrl"])
    software_did = generate_software_did(developer_did, data["softwareName"], data["softwareVersion"], data["softwareUrl"])
    vsw_repo_url = f'{repo_url_host}/issue-credential/send-proposal'
    res = requests.post(vsw_repo_url, json={
        "comment": "execute vsw publish cli",
        "auto_remove": False,
        "trace": True,
        "connection_id": connection["connection_id"],
        "schema_id": data["schemaID"] or vsw_config.get("schema_id"),
        "schema_name": data["schemaName"] or vsw_config.get("schema_name"),
        "schema_version": data["schemaVersion"] or vsw_config.get("schema_version"),
        "issuer_did": developer_did,
        "credential_proposal": {
            "@type": f"did:sov:{developer_did};spec/issue-credential/1.0/credential-preview",
            "attributes": [
                {
                    "name": "developerDid",
                    "value": developer_did
                },
                {
                    "name": "softwareName",
                    "value": data["softwareName"]
                },
                {
                    "name": "softwareVersion",
                    "value": data["softwareVersion"]
                },
                {
                    "name": "softwareDid",
                    "value": software_did
                },
                {
                    "name": "softwareUrl",
                    "value": data["softwareUrl"]
                },
                {
                    "name": "softwareHash",
                    "value": digest
                },
                {
                    "name": "mediaType",
                    "value": data["mediaType"]
                },
                {
                    "name": "sourceDid",
                    "value": data["sourceDid"]
                },
                {
                    "name": "sourceUrl",
                    "value": data["sourceUrl"]
                },
                {
                    "name": "sourceHash",
                    "value": data["sourceHash"]
                },
                {
                    "name": "builderToolDidList",
                    "value": data["builderToolDidList"]
                },
                {
                    "name": "dependencyDidList",
                    "value": data["dependencyDidList"]
                },
                {
                    "name": "buildLog",
                    "value": data["buildLog"]
                },
                {
                    "name": "builderDid",
                    "value": data["builderDid"]
                }
            ]
        },
    })
    return json.loads(res.text)
