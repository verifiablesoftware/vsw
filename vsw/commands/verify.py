import argparse
import json
from typing import List
from uuid import uuid4
from urllib.parse import urljoin
import validators
import requests
import vsw.utils
import time
from vsw.log import Log

vsw_config = vsw.utils.get_vsw_agent()
vsw_repo_config = vsw.utils.get_repo_host()
vsw_url_host = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}'
repo_url_host = vsw_repo_config.get("host")
logger = Log(__name__).logger
timeout = 60


def main(args: List[str]) -> bool:
    try:
        parser = argparse.ArgumentParser(prog="vsw verify")
        parser.add_argument("-s", "--software-name", required=True, help="The software name")
        parser.add_argument("-u", "--url", required=True, help="The software download url")
        parser.add_argument("-i", "--issuer-did", required=True, help="The issuer did")
        parsed_args = parser.parse_args(args)
        if not validators.url(parsed_args.url):
            print('The software package url is wrong, please check')
            return
        execute(parsed_args.software_name, parsed_args.issuer_did, parsed_args.url)
    except KeyboardInterrupt:
        print(" ==> Exit verify!")


def execute(software_name, issuer_did, download_url):
    connection = get_client_connection()
    logger.info("Executing verify, please wait for response...")
    credentials = check_credential(issuer_did, software_name, download_url)
    if len(credentials) == 0:
        logger.error("No found credential, please check if the specified conditions are correct.")
    else:
        proof_response = send_request(connection["connection_id"], software_name, issuer_did)
        presentation_exchange_id = proof_response["presentation_exchange_id"]
        logger.info(f'presentation_exchange_id: {presentation_exchange_id}')
        times = 0
        while times <= timeout:
            presentation_proof_result = retrieve_result(presentation_exchange_id)
            state = presentation_proof_result["state"]
            print(f"waiting state update, current state is: {state}")
            if state == "verified":
                pres_req = presentation_proof_result["presentation_request"]
                pres = presentation_proof_result["presentation"]
                is_proof_of_software_certificate = (
                        pres_req["name"] == "Proof of Software Certificate"
                )
                if is_proof_of_software_certificate:
                    # check claims
                    proof_dict = {}
                    for (referent, attr_spec) in pres_req["requested_attributes"].items():
                        proof_dict[attr_spec['name']] = pres['requested_proof']['revealed_attrs'][referent]['raw']
                        logger.info(
                            f"{attr_spec['name']}: "
                            f"{pres['requested_proof']['revealed_attrs'][referent]['raw']}"
                        )
                    credential_hash = proof_dict['hash']
                    url = proof_dict['url']
                    if credential_hash is None or url is None:
                        logger.error("Verified error, hash or url in request proof is None")
                    elif url != download_url:
                        logger.error("Verified error, the url is not matched")
                    elif vsw.utils.generate_digest(download_url) != credential_hash:
                        logger.error("Verified error, the digest is not matched")
                    else:
                        logger.info('Congratulation! verified successfully!')
                else:
                    logger.error("Verified error, the name in presentation request is wrong")
                break;
            else:
                times += 1

        if times > timeout:
            logger.error("verified error, presentation proof result is not verified!")


def retrieve_result(presentation_exchange_id):
    time.sleep(1)  # wait communicate complete automatically between agents
    presentation_proof_result = get_vsw_proof(presentation_exchange_id)
    return presentation_proof_result


def get_vsw_proof(pres_ex_id):
    vsw_url = urljoin(vsw_url_host, f"/present-proof/records/{pres_ex_id}")
    res = requests.get(vsw_url)
    return json.loads(res.text)


def check_credential(issuer_did, software_name, download_url):
    wql = json.dumps({"attr::developer-did::value": issuer_did, "attr::software-name::value": software_name,
                      "schema_name": "software-certificate", "attr::url::value": download_url})
    repo_url = f"{repo_url_host}/credentials?wql={wql}"
    res = requests.get(repo_url)
    return json.loads(res.text)["results"]


def send_request(client_conn_id, software_name, issuer_did):
    """
    Verifier sends request (prover receives request)
    Request Proof (from verifier to prover, required)
    """
    vsw_url = f'{vsw_url_host}/present-proof/send-request'
    req_attrs = [
        {
            "name": "software-name",
            "restrictions": [{"schema_name": "software-certificate", "attr::developer-did::value": issuer_did, "attr::software-name::value": software_name}]
        },
        {
            "name": "software-version",
            "restrictions": [{"schema_name": "software-certificate", "attr::developer-did::value": issuer_did, "attr::software-name::value": software_name}]
        },
        {
            "name": "developer-did",
            "restrictions": [{"schema_name": "software-certificate", "attr::developer-did::value": issuer_did, "attr::software-name::value": software_name}]
        },
        {
            "name": "hash",
            "restrictions": [{"schema_name": "software-certificate", "attr::developer-did::value": issuer_did, "attr::software-name::value": software_name}]
        },
        {
            "name": "url",
            "restrictions": [{"schema_name": "software-certificate", "attr::developer-did::value": issuer_did, "attr::software-name::value": software_name}]
        }
    ]

    indy_proof_request = {
        "name": "Proof of Software Certificate",
        "version": "1.0",
        "nonce": str(uuid4().int),
        "requested_attributes": {
            f"0_{req_attr['name']}_uuid": req_attr
            for req_attr in req_attrs
        },
        "requested_predicates": {}
    }
    proof_request_web_request = {
        "connection_id": client_conn_id,
        "proof_request": indy_proof_request
    }
    res = requests.post(vsw_url, json=proof_request_web_request)
    return json.loads(res.text)


def get_client_connection():
    connection_response = requests.get(f'{vsw_url_host}/connections')
    res = json.loads(connection_response.text)
    connections = res["results"]
    return connections[-1]
