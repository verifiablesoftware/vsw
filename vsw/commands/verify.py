import argparse
import calendar
from datetime import datetime, timezone
import json
import socket
import time
from multiprocessing.connection import Listener
from typing import List
from urllib import parse
from urllib.parse import urljoin

import requests
import validators
from aries_cloudagent_vsw.messaging.util import str_to_epoch
from version_parser import Version
from vsw.utils import Constant
import vsw.utils
from vsw.log import Log
from vsw.commands import attest

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
    except requests.exceptions.RequestException:
        logger.error(vsw.utils.Constant.NOT_RUNNING_MSG)
    except KeyboardInterrupt:
        print(" ==> Exit verify!")


def execute(proof_request, revoke_date):
    with open(proof_request) as json_file:
        data = json.load(json_file)
        software_credential = get_software_credential(data["requested_attributes"])
        test_credential = get_test_credential(data["requested_attributes"])
        if software_credential:
            if "attr::softwareversion::value" in software_credential:
                software_version = software_credential["attr::softwareversion::value"]
                if check_version(software_version) is False:
                    return;
            if "attr::softwareurl::value" in software_credential:
                software_url = software_credential["attr::softwareurl::value"]
                if not validators.url(software_url):
                    print('vsw: error: the software package url is wrong, please check')
                    return
            credentials = check_credential(software_credential)
            if len(credentials) == 0:
                print("vsw: error: No found matched credential, please check if the specified conditions are correct.")
                return;
        if test_credential:
            credentials = check_credential(test_credential)
            if len(credentials) == 0:
                print("vsw: error: No found matched attest credential, please check if the specified conditions are correct.")
                return;
        requested_predicates = {}
        if "requested_predicates" in data:
            requested_predicates = data["requested_predicates"]
        connection = get_client_connection()
        logger.info("Executing verify, please wait for response...")
        logger.debug(f'issuer connection_id: {connection["connection_id"]}')
        address = ('localhost', Constant.PORT_NUMBER)
        listener = Listener(address)
        listener._listener._socket.settimeout(Constant.TIMEOUT)
        proof_response = send_request(connection["connection_id"], software_credential, test_credential, requested_predicates, revoke_date)
        presentation_exchange_id = proof_response["presentation_exchange_id"]
        logger.info(f'presentation_exchange_id: {presentation_exchange_id}')

        while True:
            try:
                conn = listener.accept()
                msg = conn.recv()
                state = msg["state"]
                conn.close()
                logger.info(f"waiting state update, current state is: {state}")
                if state == "verified":
                    if msg["verified"] == "false":
                        remove_proof_request(presentation_exchange_id)
                        logger.info("Verified error, Verified result from indy is False!")
                        listener.close()
                        break;
                    pres_req = msg["presentation_request"]
                    is_proof_of_software_certificate = (
                            pres_req["name"] == "Proof of Software Certificate"
                    )
                    if is_proof_of_software_certificate:
                        logger.info('Congratulation! verified successfully!')
                    else:
                        remove_proof_request(presentation_exchange_id)
                        logger.info("Verified error, the name in presentation request is wrong")
                    listener.close()
                    break;
                else:
                    time.sleep(0.5)
            except socket.timeout:
                remove_proof_request(presentation_exchange_id)
                logger.error("Request timeout, Verified error!")
                listener.close()
                break;


def get_software_credential(data):
    for cred in data:
        if cred["schema_id"] == vsw_config.get("schema_id"):
            return cred
    return None


def get_test_credential(data):
    for cred in data:
        if cred["schema_id"] == vsw_config.get("test_schema_id"):
            return cred
    return None


def check_version(software_version):
    try:
        Version(software_version)
    except ValueError:
        print("vsw: error: the software version format is incorrect. the correct format should be 'MAJOR.MINOR.PATCH'")
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


def send_request(client_conn_id, software_credential, test_credential, requested_predicates, revoke_date):
    vsw_url = f'{vsw_url_host}/present-proof/send-request'
    NOW_8601 = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(" ", "seconds")
    NOW_EPOCH = str_to_epoch(NOW_8601)
    time_from = 0
    time_to = NOW_EPOCH

    if revoke_date:
        time_to = calendar.timegm(datetime.strptime(revoke_date, '%Y-%m-%d').timetuple())
    req_attr = {
        "names": ["softwarename", "softwareversion", "developerdid", "softwaredid", "softwarehash", "softwareurl",
                  "mediatype", "sourcedid", "sourceurl", "sourcehash", "buildertooldidlist", "dependencydidlist",
                  "buildlog", "builderdid"],
        "non_revoked": {"from": time_from, "to": time_to},
        "restrictions": [software_credential]
    }
    test_names = ["testerdid", "testspecdid", "testspecurl", "testspechash", "testresult","testresultdetaildid",
                  "testresultdetailurl", "testresultdetailhash", "comments", "softwaredid"]
    if not requested_predicates or len(requested_predicates.values()) == 0:
        test_names.append("ranking")
    req_test_attr = {
        "names": test_names,
        "non_revoked": {"from": time_from, "to": time_to},
        "restrictions": [test_credential]
    }

    request_attributes = {}
    if software_credential:
        request_attributes["0_software_certificate_uuid"] = req_attr
    if test_credential:
        request_attributes["1_test_certificate_uuid"] = req_test_attr
    if requested_predicates:
        for p in requested_predicates.values():
            p["restrictions"] = [{"cred_def_id": attest.get_credential_definition_id()}]
            p["non_revoked"] = {"from": time_from, "to": time_to}

    indy_proof_request = {
        "name": "Proof of Software Certificate",
        "version": "1.0",
        "requested_attributes": request_attributes,
        "requested_predicates": requested_predicates
    }
    proof_request_web_request = {
        "connection_id": client_conn_id,
        "proof_request": indy_proof_request
    }
    logger.debug(proof_request_web_request)
    res = requests.post(vsw_url, json=proof_request_web_request)
    return json.loads(res.text)


def get_client_connection():
    connection_response = requests.get(f'{vsw_url_host}/connections?state=active')
    res = json.loads(connection_response.text)
    connections = res["results"]
    if len(connections) > 0:
        return connections[-1]
    else:
        raise ConnectionError("vsw: error: Not found active vsw connection! Have you executed vsw init -c?")
