import argparse
import getpass
import json
from typing import List

from vsw.log import Log
import vsw.utils
import requests

vsw_config = vsw.utils.get_vsw_agent()
vsw_repo_config = vsw.utils.get_repo_host()
vsw_url_host = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}'
repo_url_host = vsw_repo_config.get("host")
logger = Log(__name__).logger


def main(args: List[str]) -> bool:
    software_name = input('Please enter software name: ')
    software_version = input('Please enter software version: ')
    software_did = input('Please enter software did: ')
    # download_url = getpass.getpass('Please enter software download url: ')
    args = parse_args(args)
    issue_credential(software_name, software_version, software_did)

def parse_args(args):
    parser = argparse.ArgumentParser()
    # parser.add_argument("--url", required=True, help="The uploaded file url")
    return parser.parse_args(args)


def issue_credential(software_name, software_version, software_did):
    connection = get_repo_connection()
    send_proposal(connection["connection_id"], connection["their_did"], software_name,
                  software_version, software_did)


def get_repo_connection():
    connection_response = requests.get(f'{repo_url_host}/connections')
    res = json.loads(connection_response.text)
    connections = res["results"]
    return connections[-1]


def get_credential_definition():
    local_agent = vsw.utils.get_vsw_agent()
    local_url = f'http://{local_agent.get("admin_host")}:{local_agent.get("admin_port")}'
    credential_definitions_response = requests.get(f'{local_url}/credential-definitions/created')
    res = json.loads(credential_definitions_response.text)
    credential_definition_ids = res["credential_definition_ids"]
    cred_def_id = credential_definition_ids[-1]
    cred_def_response = requests.get(f'{local_url}/credential-definitions/{cred_def_id}')
    res2 = json.loads(cred_def_response.text)
    return res2["credential_definition"]


def send_proposal(repo_conn_id, developer_did, software_name, software_version, software_did):
    vsw_repo_url = f'{repo_url_host}/issue-credential/send-proposal'
    res = requests.post(vsw_repo_url, json={
        "comment": "Felix Test",
        "auto_remove": False,
        "trace": True,
        "connection_id": repo_conn_id,
        "credential_proposal": {
            "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview",  # TODO
            "attributes": [{
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
                }
            ]
        },
    })
    print(json.loads(res.text))
