import argparse
import json
from typing import List
from uuid import uuid4

import requests
import vsw
from vsw.log import Log

vsw_config = vsw.utils.get_vsw_agent()
vsw_repo_config = vsw.utils.get_repo_host()
vsw_url_host = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}'
repo_url_host = vsw_repo_config.get("host")
logger = Log(__name__).logger


def main(args: List[str]) -> bool:
    parser = argparse.ArgumentParser(prog="vsw verify")
    parser.add_argument("--software-name", required=True, help="The software name")
    parser.add_argument("--software-did", required=True, help="The software did")
    parser.add_argument("--issuer-did", required=True, help="The issuer did")
    parser.add_argument("--developer-did", required=True, help="The developer did")
    parsed_args = parser.parse_args(args)
    connection = get_repo_connection()
    # 1. Request Proof
    proof_response = send_request(connection["connection_id"], parsed_args.software_name, parsed_args.issuer_did)
    # 2. Present Proof
    present_proof_response = send_presentation_proof(proof_response)
    # 3. Verify Proof
    verify_presentation_proof(present_proof_response)


def send_request(repo_conn_id, software_name, issuer_did):
    """
    Verifier sends request (prover receives request)
    Request Proof (from verifier to prover, required)
    """
    vsw_url = f'{vsw_url_host}/present-proof/send-request'
    req_attrs = [
        {
            "name": "software-name",
            "restrictions": [
                {"schema_name": "software-certificate"},
                {"issuer_did": issuer_did},
                {"attr::software-name::value": software_name}]
        },
        {
            "name": "software-version",
            "restrictions": [
                {"schema_name": "software-certificate"},
                {"issuer_did": issuer_did},
                {"attr::software-name::value": software_name}]
        },
        {
            "name": "developer-did",
            "restrictions": [
                {"schema_name": "software-certificate"},
                {"issuer_did": issuer_did},
                {"attr::software-name::value": software_name}]
        },
        {
            "name": "hash",
            "restrictions": [
                {"schema_name": "software-certificate"},
                {"issuer_did": issuer_did},
                {"attr::software-name::value": software_name}]
        },
        {
            "name": "url",
            "restrictions": [
                {"schema_name": "software-certificate"},
                {"issuer_did": issuer_did},
                {"attr::software-name::value": software_name}]
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
        "connection_id": repo_conn_id,
        "proof_request": indy_proof_request
    }
    res = requests.post(vsw_url, proof_request_web_request)
    return json.loads(res.text)


def send_presentation_proof(message):
    """Prover sends presentation proof (verifier receives presentation proof)"""
    state = message["state"]
    presentation_exchange_id = message["presentation_exchange_id"]
    presentation_request = message["presentation_request"]
    present_proof_response = {}

    if state == "request_received":
        # include self-attested attributes (not included in credentials)
        credentials_by_reft = {}
        revealed = {}
        self_attested = {}
        predicates = {}

        # select credentials to provide for the proof
        credentials = requests.get(f"{repo_url_host}/present-proof/records/{presentation_exchange_id}/credentials")
        if credentials:
            for row in sorted(
                    credentials,
                    key=lambda c: int(c["cred_info"]["attrs"]["timestamp"]),
                    reverse=True,
            ):
                for referent in row["presentation_referents"]:
                    if referent not in credentials_by_reft:
                        credentials_by_reft[referent] = row

        for referent in presentation_request["requested_attributes"]:
            if referent in credentials_by_reft:
                revealed[referent] = {
                    "cred_id": credentials_by_reft[referent]["cred_info"][
                        "referent"
                    ],
                    "revealed": True,
                }
            else:
                self_attested[referent] = "my self-attested value"

        for referent in presentation_request["requested_predicates"]:
            if referent in credentials_by_reft:
                predicates[referent] = {
                    "cred_id": credentials_by_reft[referent]["cred_info"][
                        "referent"
                    ]
                }

        request = {
            "requested_predicates": predicates,
            "requested_attributes": revealed,
            "self_attested_attributes": self_attested,
        }
        res = requests.post(f"{repo_url_host}/present-proof/records/{presentation_exchange_id}/send-presentation", request)
        present_proof_response = json.loads(res.text)

    return present_proof_response


def verify_presentation_proof(message):
    """
    Verify Proof
    Verifier verifies presentation proof
    """
    state = message["state"]

    presentation_exchange_id = message["presentation_exchange_id"]
    if state == "presentation_received":
        response = requests.post(f"{vsw_url_host}/present-proof/records/{presentation_exchange_id}/verify-presentation")
        msg = json.loads(response.text)
        pres_req = msg["presentation_request"]
        pres = msg["presentation"]
        is_proof_of_software_certificate = (
                pres_req["name"] == "Proof of Software Certificate"
        )
        if is_proof_of_software_certificate:
            # check claims
            for (referent, attr_spec) in pres_req["requested_attributes"].items():
                logger.info(
                    f"{attr_spec['name']}: "
                    f"{pres['requested_proof']['revealed_attrs'][referent]['raw']}"
                )


def get_repo_connection():
    connection_response = requests.get(f'{repo_url_host}/connections')
    res = json.loads(connection_response.text)
    connections = res["results"]
    return connections[-1]
