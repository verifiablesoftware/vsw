import argparse
import hashlib
import json
import shutil
import tempfile
import urllib
from typing import List
from multicodec import add_prefix
from multibase import encode, decode
from vsw.log import Log
import vsw.utils
import requests

vsw_config = vsw.utils.get_vsw_agent()
vsw_repo_config = vsw.utils.get_repo_host()
vsw_url_host = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}'
repo_url_host = vsw_repo_config.get("host")
logger = Log(__name__).logger


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
    connection = get_repo_connection()
    send_proposal(connection["connection_id"], connection["their_did"], software_name,
                  software_version, software_did, software_url, software_alt_url1, software_alt_url2)


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


def generate_digest(software_url):
    with urllib.request.urlopen(software_url) as response:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            shutil.copyfileobj(response, tmp_file)
            sha256_hash = hashlib.sha256()
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: tmp_file.file.read(4096), b""):
                sha256_hash.update(byte_block)
            hex_digest = sha256_hash.hexdigest()
            print(f'sha256 hash: {hex_digest}')
            multi_codec = add_prefix('sha2-256', str.encode(hex_digest))
            print(f'multi_codec:{multi_codec}')
            digest = encode('base58btc', multi_codec)
            return digest.decode()


def send_proposal(repo_conn_id, developer_did, software_name, software_version, software_did, software_url,
                  software_alt_url1, software_alt_url2):
    if software_alt_url1 is None:
        software_alt_url1 = ""
    if software_alt_url2 is None:
        software_alt_url2 = ""
    digest = generate_digest(software_url)
    print(f'digest: {digest}')
    vsw_repo_url = f'{repo_url_host}/issue-credential/send-proposal'
    res = requests.post(vsw_repo_url, json={
        "comment": "execute vsw publish cli",
        "auto_remove": False,
        "trace": True,
        "connection_id": repo_conn_id,
        "credential_proposal": {
            "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview",  # TODO
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
                }
            ]
        },
    })
    print(json.loads(res.text))
