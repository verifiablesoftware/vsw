import argparse
import json
import time
from typing import List
from vsw.log import Log
from urllib.parse import urljoin
import vsw.utils
import requests
import validators
from version_parser import Version

vsw_config = vsw.utils.get_vsw_agent()
vsw_repo_config = vsw.utils.get_repo_host()
vsw_url_host = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}'
repo_url_host = vsw_repo_config.get("host")
logger = Log(__name__).logger
timeout = 60


def main(args: List[str]) -> bool:
    try:
        args = parse_args(args)
        with open(args.cred) as json_file:
            data = json.load(json_file)
            software_name = data['software_name']
            software_version = data["software_version"]
            software_url = data["software_url"]
            if check_version(software_version) is False:
                return;
            if software_url and not validators.url(software_url):
                print('The software package url is wrong, please check')
                return
            developer_did = get_public_did()
            issue_credential(developer_did, software_name, software_version, software_url)
    except KeyboardInterrupt:
        print(" ==> Exit publish!")


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--cred", required=True, help="The software credential json file path")
    return parser.parse_args(args)


def check_version(software_version):
    try:
        Version(software_version)
    except ValueError:
        print("The software version format is incorrect. the correct format should be 'MAJOR.MINOR.PATCH'")
        return False
    return True


def issue_credential(developer_did, software_name, software_version, software_url):
    logger.info("executing publish, please waiting for response")
    connection = get_repo_connection()
    proposal_response = send_proposal(connection["connection_id"], developer_did, software_name,
                                      software_version, software_url)
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


def get_credential(developer_did, software_name):
    wql = json.dumps({"attr::developer-did::value": developer_did, "attr::software-name::value": software_name})
    repo_url = f"{repo_url_host}/credentials?wql={wql}"
    res = requests.get(repo_url)
    try:
        return json.loads(res.text)["results"][0]["attrs"]
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


def generate_software_did(developer_did, software_name, software_version, download_url, hash):

    credential = get_credential(developer_did, software_name)
    same_version = False
    if credential:
        same_version = is_same_version(software_version, credential["software-version"])
    if same_version:
        logger.info(f'Existed software-did: {credential["software-did"]}')
        return credential["software-did"]
    else:
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
        requests.post(urljoin(vsw_url_host, f"/wallet/set-did-endpoint"), json={
            "did": did,
            "endpoint_type": "Endpoint",
            "endpoint": f'{download_url}:h1?{hash}'
        })
        logger.info(f'Created new software-did: {did}')
        return did


def send_proposal(repo_conn_id, developer_did, software_name, software_version, software_url):
    digest = vsw.utils.generate_digest(software_url)
    software_did = generate_software_did(developer_did, software_name, software_version, software_url, digest)
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
                    "value": ''
                },
                {
                    "name": "alt-url2",
                    "value": ''
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
