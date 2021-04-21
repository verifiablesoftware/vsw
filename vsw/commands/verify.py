import argparse
import datetime
import json
import time
from typing import List
from urllib.parse import urljoin
from version_parser import Version
import requests
import validators

import vsw.utils
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
        parser.add_argument("-c", "--proof-request", required=True, help="The software credential json file path")
        parsed_args = parser.parse_args(args)
        with open(parsed_args.proof_request) as json_file:
            data = json.load(json_file)
            software_name = data['software_name']
            software_version = data["software_version"]
            software_url = data["software_url"]
            software_did = data["software_did"]
            issuer_did = data["issuer_did"]
            revoke_date = data["revoke_date"]
            if not validators.url(software_url):
                print('The software package url is wrong, please check')
                return
            if check_version(software_version) is False:
                return;
            execute(software_name, software_version, issuer_did, software_url, software_did, revoke_date)
    except ConnectionError as e:
        logger.error(e)
    except KeyboardInterrupt:
        print(" ==> Exit verify!")


def execute(software_name, version, issuer_did, download_url, software_did, revoke_date):
    connection = get_client_connection()
    logger.info("Executing verify, please wait for response...")
    schema_name = vsw_config.get("schema_name")
    schema_version = vsw_config.get("schema_version")
    credentials = check_credential(issuer_did, software_name, download_url, schema_name, software_did)
    if len(credentials) == 0:
        logger.error("No found credential, please check if the specified conditions are correct.")
    else:
        hash = vsw.utils.generate_digest(download_url)
        proof_response = send_request(connection["connection_id"], software_name, version, issuer_did, schema_name,
                                      schema_version, download_url, hash, revoke_date)
        presentation_exchange_id = proof_response["presentation_exchange_id"]
        logger.info(f'presentation_exchange_id: {presentation_exchange_id}')
        times = 0
        while times <= timeout:
            presentation_proof_result = retrieve_result(presentation_exchange_id)
            state = presentation_proof_result["state"]
            print(f"waiting state update, current state is: {state}")
            if state == "verified":
                if presentation_proof_result["verified"] == "false":
                    logger.error("Verified error, the credential might be revoked!")
                    break;
                pres_req = presentation_proof_result["presentation_request"]
                is_proof_of_software_certificate = (
                        pres_req["name"] == "Proof of Software Certificate"
                )
                if is_proof_of_software_certificate:
                    logger.info('Congratulation! verified successfully!')
                else:
                    logger.error("Verified error, the name in presentation request is wrong")
                break;
            else:
                times += 1

        if times > timeout:
            logger.error("Verified error, presentation proof result is not verified!")


def check_version(software_version):
    try:
        Version(software_version)
    except ValueError:
        print("The software version format is incorrect. the correct format should be 'MAJOR.MINOR.PATCH'")
        return False
    return True


def retrieve_result(presentation_exchange_id):
    time.sleep(1)  # wait communicate complete automatically between agents
    presentation_proof_result = get_vsw_proof(presentation_exchange_id)
    return presentation_proof_result


def get_vsw_proof(pres_ex_id):
    vsw_url = urljoin(vsw_url_host, f"/present-proof/records/{pres_ex_id}")
    res = requests.get(vsw_url)
    return json.loads(res.text)


def check_credential(issuer_did, software_name, download_url, schema_name, software_did):
    wql = json.dumps({"attr::developer-did::value": issuer_did, "attr::software-name::value": software_name,
                      "attr::software-did::value": software_did,
                      "schema_name": schema_name, "attr::url::value": download_url})
    repo_url = f"{repo_url_host}/credentials?wql={wql}"
    res = requests.get(repo_url)
    return json.loads(res.text)["results"]


def send_request(client_conn_id, software_name, version, issuer_did, schema_name, schema_version, url, hash,
                 revoke_date):
    vsw_url = f'{vsw_url_host}/present-proof/send-request'
    time_from = 0
    time_to = int(time.time())
    if revoke_date:
        datetime_object = datetime.strptime(revoke_date, '%Y-%M-%d')
        time_to = datetime.timestamp(datetime_object)
    req_attr = {
        "names": ["software-name", "software-version", "developer-did", "hash", "url"],
        "non_revoked": {"from": time_from, "to": time_to},
        "restrictions": [{"schema_version": schema_version, "schema_name": schema_name, "issuer_did": issuer_did,
                          "attr::software-name::value": software_name,
                          "attr::software-version::value": version,
                          "attr::url::value": url,
                          "attr::hash::value": hash}]
    }

    indy_proof_request = {
        "name": "Proof of Software Certificate",
        "version": "1.0",
        "requested_attributes": {
            f"0_software-name_uuid": req_attr,
            f"0_software-version_uuid": req_attr,
            f"0_developer-did_uuid": req_attr,
            f"0_hash_uuid": req_attr,
            f"0_url_uuid": req_attr
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
    connection_response = requests.get(f'{vsw_url_host}/connections?state=active')
    res = json.loads(connection_response.text)
    connections = res["results"]
    if len(connections) > 0:
        return connections[-1]
    else:
        raise ConnectionError("Not found active vsw connection! Have you executed vsw init -c?")
