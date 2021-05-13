import argparse
import datetime
import json
import time
from multiprocessing.connection import Listener
from typing import List
from urllib import parse
from urllib.parse import urljoin

import requests
import validators
from version_parser import Version
from vsw.utils import Constant
import vsw.utils
from vsw.log import Log

vsw_config = vsw.utils.get_vsw_agent()
vsw_repo_config = vsw.utils.get_repo_host()
vsw_url_host = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}'
repo_url_host = vsw_repo_config.get("host")
logger = Log(__name__).logger
timeout = Constant.TIMEOUT


def main(args: List[str]) -> bool:
    try:
        parser = argparse.ArgumentParser(prog="vsw verify")
        parser.add_argument("-p", "--proof-request", required=True, help="The software credential json file path")
        parser.add_argument("-d", "--revoke-date", required=False, help="The revoke date, %Y-%m-%d")
        parsed_args = parser.parse_args(args)
        execute(parsed_args.proof_request, parsed_args.revoke_date)
    except ConnectionError as e:
        logger.error(e)
    except KeyboardInterrupt:
        print(" ==> Exit verify!")


def execute(proof_request, revoke_date):
    with open(proof_request) as json_file:
        data = json.load(json_file)
        software_credential = data[0]
        if hasattr(software_credential, "attr::softwareversion::value"):
            software_version = software_credential["attr::softwareversion::value"]
            if check_version(software_version) is False:
                return;
        if hasattr(software_credential, "attr::softwareurl::value"):
            software_url = software_credential["attr::softwareurl::value"]
            if not validators.url(software_url):
                print('The software package url is wrong, please check')
                return

        for cred in data:
            credentials = check_credential(cred)
            if len(credentials) == 0:
                logger.error("No found matched credential, please check if the specified conditions are correct.")
                return;
        connection = get_client_connection()
        logger.info("Executing verify, please wait for response...")
        logger.info(f'issuer connection_id: {connection["connection_id"]}')
        address = ('localhost', Constant.PORT_NUMBER)
        listener = Listener(address)
        proof_response = send_request(connection["connection_id"], data, revoke_date)
        presentation_exchange_id = proof_response["presentation_exchange_id"]
        logger.info(f'presentation_exchange_id: {presentation_exchange_id}')

        times = 0
        while times <= timeout:
            conn = listener.accept()
            msg = conn.recv()
            state = msg["state"]
            conn.close()
            logger.info(f"waiting state update, current state is: {state}")
            if state == "verified":
                if msg["verified"] == "false":
                    remove_proof_request(presentation_exchange_id)
                    logger.error("Verified error, Verified result from indy is False!")
                    break;
                pres_req = msg["presentation_request"]
                is_proof_of_software_certificate = (
                        pres_req["name"] == "Proof of Software Certificate"
                )
                if is_proof_of_software_certificate:
                    logger.info('Congratulation! verified successfully!')
                else:
                    remove_proof_request(presentation_exchange_id)
                    logger.error("Verified error, the name in presentation request is wrong")
                break;
            else:
                times += 1

        if times > timeout:
            remove_proof_request(presentation_exchange_id)
            logger.error("Request timeout, Verified error!")
        listener.close()


def check_version(software_version):
    try:
        Version(software_version)
    except ValueError:
        print("The software version format is incorrect. the correct format should be 'MAJOR.MINOR.PATCH'")
        return False
    return True


def check_credential(data):
    wql = json.dumps(data)
    repo_url = f"{repo_url_host}/credentials?wql={parse.quote(wql)}"
    res = requests.get(repo_url)
    return json.loads(res.text)["results"]


def remove_proof_request(presentation_exchange_id):
    vsw_url = urljoin(vsw_url_host, f"/present-proof/records/{presentation_exchange_id}/remove")
    requests.post(vsw_url)


def retrieve_result(presentation_exchange_id):
    time.sleep(1)  # wait communicate complete automatically between agents
    presentation_proof_result = get_vsw_proof(presentation_exchange_id)
    return presentation_proof_result


def get_vsw_proof(pres_ex_id):
    vsw_url = urljoin(vsw_url_host, f"/present-proof/records/{pres_ex_id}")
    res = requests.get(vsw_url)
    return json.loads(res.text)


def send_request(client_conn_id, data, revoke_date):
    vsw_url = f'{vsw_url_host}/present-proof/send-request'
    time_from = 0
    time_to = int(time.time())
    if revoke_date:
        datetime_object = datetime.datetime.strptime(revoke_date, '%Y-%m-%d')
        time_to = datetime.datetime.timestamp(datetime_object)
    req_attr = {
        "names": ["softwarename", "softwareversion", "developerdid", "softwaredid", "softwarehash", "softwareurl",
                  "mediatype", "sourcedid", "sourceurl", "sourcehash", "buildertooldidlist", "dependencydidlist",
                  "buildlog", "builderdid", "softwaredid", "testspecdid", "testspecurl", "testresult",
                  "testresultdetaildid", "testresultdetailurl", "ranking", "comments"],
        "non_revoked": {"from": time_from, "to": time_to},
        "restrictions": data
    }

    indy_proof_request = {
        "name": "Proof of Software Certificate",
        "version": "1.0",
        "requested_attributes": {
            f"0_software_certificate_uuid": req_attr
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
