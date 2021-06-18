import argparse
import calendar
import json
import socket
import time
from datetime import datetime, timezone
from multiprocessing.connection import Listener
from typing import List
from urllib.parse import urljoin

from rich.console import Console

console = Console()
import requests
import validators
from aries_cloudagent_vsw.messaging.util import str_to_epoch
from version_parser import Version
from vsw.utils import Constant
import vsw.utils
from vsw.log import Log
from vsw.commands import exit

vsw_config = vsw.utils.get_vsw_agent()
vsw_url_host = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}'
client_header = {"x-api-key": vsw_config.get("seed")}
logger = Log(__name__).logger
timeout = Constant.TIMEOUT
TITLE = "Proof of Test Certificate"


def main(args: List[str]) -> bool:
    try:
        if exit.check_vsw_is_running():
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
        requested_attributes = data["requested_attributes"]
        software_request_attribute = get_software_requested_attribute(requested_attributes)
        test_request_attribute = get_test_request_attribute(requested_attributes)
        software_request_attribute = arrange_request_attribute(software_request_attribute)
        test_request_attribute = arrange_request_attribute(test_request_attribute)

        if software_request_attribute and software_request_attribute.get("restrictions"):
            for restriction in software_request_attribute.get("restrictions"):
                if "attr::softwareversion::value" in restriction:
                    software_version = restriction["attr::softwareversion::value"]
                    if check_version(software_version) is False:
                        return;
                if "attr::softwareurl::value" in restriction:
                    software_url = restriction["attr::softwareurl::value"]
                    if not validators.url(software_url):
                        print('vsw: error: the software package url is wrong, please check')
                        return

        requested_predicates = {}
        if "requested_predicates" in data:
            requested_predicates = data["requested_predicates"]
        connection = get_client_connection()
        logger.info(f'issuer connection_id: {connection["connection_id"]}')
        address = ('localhost', Constant.PORT_NUMBER)
        listener = Listener(address)
        listener._listener._socket.settimeout(Constant.TIMEOUT)
        proof_response = send_request(connection["connection_id"], software_request_attribute, test_request_attribute,
                                      requested_predicates, revoke_date)
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
                    console.print("======presentation_request========")
                    console.print(json.dumps(msg["presentation_request"], indent=4, sort_keys=True))
                    console.print("======requested_proof========")
                    console.print(json.dumps(msg["presentation"]["requested_proof"], indent=4, sort_keys=True))
                    if msg["verified"] == "false":
                        remove_proof_request(presentation_exchange_id)
                        print("Verified error, Verified result from indy is False!")
                        listener.close()
                        break;
                    pres_req = msg["presentation_request"]
                    is_proof_of_software_certificate = (
                            pres_req["name"] == TITLE
                    )
                    if is_proof_of_software_certificate:
                        print('Congratulation! verified successfully!')
                    else:
                        remove_proof_request(presentation_exchange_id)
                        print("Verified error, the name in presentation request is wrong")
                    listener.close()
                    break;
                else:
                    time.sleep(0.5)
            except socket.timeout as e:
                remove_proof_request(presentation_exchange_id)
                print("Request timeout, Verified error!")
                logger.error(e)
                listener.close()
                break;


def arrange_request_attribute(request_attribute):
    if not request_attribute:
        return None
    restrictions = request_attribute.get("restrictions")
    arranged_restrictions = []
    for restriction in restrictions:
        restriction = remove_empty_from_dict(restriction)
        restriction = replace_attr_fields(restriction)
        arranged_restrictions.append(restriction)
    request_attribute["restrictions"] = arranged_restrictions
    return request_attribute


def remove_empty_from_dict(d):
    if type(d) is dict:
        return dict((k, remove_empty_from_dict(v)) for k, v in d.items() if v and remove_empty_from_dict(v))
    elif type(d) is list:
        return [remove_empty_from_dict(v) for v in d if v and remove_empty_from_dict(v)]
    else:
        return d


def replace_attr_fields(restriction : dict):
    new_restriction = {}
    for key, value in restriction.items():
        if key not in ["schema_id", "schema_issuer_did", "schema_name", "schema_version",
                       "cred_def_id", "issuer_did"]:
            new_restriction[f'attr::{key.lower()}::value'] = value
        else:
            new_restriction[key] = value
    return new_restriction


def get_software_requested_attribute(requested_attributes):
    for req_attr in requested_attributes:
        restrictions = req_attr["restrictions"]
        for restriction in restrictions:
            if restriction["schema_id"] == vsw_config.get("schema_id"):
                return req_attr
    return None


def get_test_request_attribute(requested_attributes):
    for req_attr in requested_attributes:
        restrictions = req_attr["restrictions"]
        for restriction in restrictions:
            if restriction["schema_id"] == vsw_config.get("test_schema_id"):
                return req_attr
    return None


def check_version(software_version):
    try:
        Version(software_version)
    except ValueError:
        print("vsw: error: the software version format is incorrect. the correct format should be 'MAJOR.MINOR.PATCH'")
        return False
    return True


def remove_proof_request(presentation_exchange_id):
    vsw_url = urljoin(vsw_url_host, f"/present-proof/records/{presentation_exchange_id}/remove")
    requests.post(url=vsw_url, headers=client_header)


def retrieve_result(presentation_exchange_id):
    time.sleep(1)  # wait communicate complete automatically between agents
    presentation_proof_result = get_vsw_proof(presentation_exchange_id)
    return presentation_proof_result


def get_vsw_proof(pres_ex_id):
    vsw_url = urljoin(vsw_url_host, f"/present-proof/records/{pres_ex_id}")
    res = requests.get(url=vsw_url, headers=client_header)
    return json.loads(res.text)


def send_request(client_conn_id, software_request_attribute, test_request_attribute, requested_predicates, revoke_date):
    vsw_url = f'{vsw_url_host}/present-proof/send-request'
    NOW_8601 = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(" ", "seconds")
    NOW_EPOCH = str_to_epoch(NOW_8601)
    time_from = 0
    time_to = NOW_EPOCH

    if revoke_date:
        time_to = calendar.timegm(datetime.strptime(revoke_date, '%Y-%m-%d').timetuple())

    request_attributes = {}
    if software_request_attribute:
        request_attributes["0_software_certificate_uuid"] = {
            "names": list(map(str.lower,software_request_attribute["names"])),
            "non_revoked": {"from": time_from, "to": time_to},
            "restrictions": software_request_attribute["restrictions"]
        }
    if test_request_attribute:
        request_attributes["1_test_certificate_uuid"] = {
            "names": list(map(str.lower,test_request_attribute["names"])),
            "non_revoked": {"from": time_from, "to": time_to},
            "restrictions": test_request_attribute["restrictions"]
        }
    if requested_predicates:
        for p in requested_predicates.values():
            for key, value in p.items():
                if key == "restrictions":
                    arranged_restrictions = []
                    for rp_restriction in value:
                        arranged_restrictions.append(replace_attr_fields(rp_restriction))
                    p["restrictions"] = arranged_restrictions
                    break;
            p["non_revoked"] = {"from": time_from, "to": time_to}

    indy_proof_request = {
        "name": TITLE,
        "version": "1.0",
        "requested_attributes": request_attributes,
        "requested_predicates": requested_predicates
    }
    proof_request_web_request = {
        "connection_id": client_conn_id,
        "proof_request": indy_proof_request
    }
    logger.info(json.dumps(proof_request_web_request))
    res = requests.post(url=vsw_url, json=proof_request_web_request, headers=client_header)
    logger.info(res)
    return json.loads(res.text)


def get_client_connection():
    connection_response = requests.get(url=f'{vsw_url_host}/connections?state=active', headers=client_header)
    res = json.loads(connection_response.text)
    logger.info(res)
    connections = res["results"]
    if len(connections) > 0:
        return connections[-1]
    else:
        raise ConnectionError("vsw: error: Not found active vsw connection! Have you executed vsw setup connection?")
