import argparse
import json
import time
from typing import List
from vsw.log import Log
from urllib.parse import urljoin
import vsw.utils
import requests

vsw_config = vsw.utils.get_vsw_agent()
vsw_repo_config = vsw.utils.get_repo_host()
vsw_url_host = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}'
repo_url_host = vsw_repo_config.get("host")
logger = Log(__name__).logger
timeout = 60


def main(args: List[str]) -> bool:
    args = parse_args(args)
    software_name = input('Please enter software name: ')
    software_version = input('Please enter software version: ')
    software_did = input('Please enter software did: ')
    software_url = input('Please enter software package url: ')
    software_alt_url1 = args.alt_url1
    software_alt_url2 = args.alt_url2

    issue_credential(software_name, software_version, software_did, software_url, software_alt_url1, software_alt_url2)


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--alt-url1", required=False, help="The software optional package url1")
    parser.add_argument("--alt-url2", required=False, help="The software optional package url2")
    return parser.parse_args(args)


def issue_credential(software_name, software_version, software_did, software_url, software_alt_url1, software_alt_url2):
    logger.info("executing publish, please waiting for response")
    connection = get_repo_connection()
    proposal_response = send_proposal(connection["connection_id"], get_public_did(), software_name,
                                      software_version, software_did, software_url, software_alt_url1,
                                      software_alt_url2)
    credential_exchange_id = proposal_response["credential_exchange_id"]
    logger.info(f'credential_exchange_id: {credential_exchange_id}')

    times = 0
    while times <= timeout:
        res = retrieve_result(credential_exchange_id)
        print(f'waiting state update, current state: {res["state"]}')
        if res["state"] == "credential_acked":
            logger.info("Congratulation, execute publish successfully!")
            break;
        else:
            times += 1;
    if times > timeout:
        logger.error("Sorry, there might be some issue during publishing")


def retrieve_result(credential_exchange_id):
    time.sleep(1)  # wait communicate complete automatically between agents
    res = get_credential_record(credential_exchange_id)
    return res


def get_repo_connection():
    connection_response = requests.get(f'{repo_url_host}/connections')
    res = json.loads(connection_response.text)
    connections = res["results"]
    return connections[-1]


def get_public_did():
    url = urljoin(vsw_url_host, "/wallet/did/public")
    response = requests.get(url)
    res = json.loads(response.text)
    return res["result"]["did"]


def get_credential_record(cred_ex_id):
    url = urljoin(repo_url_host, f"/issue-credential/records/{cred_ex_id}")
    credential_response = requests.get(url)
    res = json.loads(credential_response.text)
    return res


def send_proposal(repo_conn_id, developer_did, software_name, software_version, software_did, software_url,
                  software_alt_url1, software_alt_url2):
    if software_alt_url1 is None:
        software_alt_url1 = ""
    if software_alt_url2 is None:
        software_alt_url2 = ""
    digest = vsw.utils.generate_digest(software_url)
    vsw_repo_url = f'{repo_url_host}/issue-credential/send-proposal'
    res = requests.post(vsw_repo_url, json={
        "comment": "execute vsw publish cli",
        "auto_remove": False,
        "trace": True,
        "connection_id": repo_conn_id,
        "credential_proposal": {
            "@type": f"did:sov:{developer_did};spec/issue-credential/1.0/credential-preview",
            "attributes": [
                {
                    "name": "developer-did",
                    "value": developer_did
                },
                {
                    "name": "software-version",
                    "value": software_version
                },
                {
                    "name": "software-name",
                    "value": software_name
                },
                {
                    "name": "software-did",
                    "value": software_did
                },
                {
                    "name": "url",
                    "value": software_url
                },
                {
                    "name": "alt-url1",
                    "value": software_alt_url1
                },
                {
                    "name": "alt-url2",
                    "value": software_alt_url2
                },
                {
                    "name": "hash",
                    "value": digest
                },
                {
                    "name": "alt-hash",
                    "value": ""
                }
            ]
        },
    })
    return json.loads(res.text)
