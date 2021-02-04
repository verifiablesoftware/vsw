import argparse
import json
from typing import List

import requests
import vsw
from vsw.log import Log

vsw_config = vsw.utils.get_vsw_agent()
vsw_repo_config = vsw.utils.get_repo_host()
vsw_url_host = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}'
repo_url_host = vsw_repo_config.get("host")
logger = Log(__name__).logger


def main(args: List[str]) -> bool:
    parser = argparse.ArgumentParser(prog="vsw check")
    # parser.add_argument(
    #     "dists",
    #     nargs="+",
    #     metavar="dist",
    #     help="The distribution files to check, usually dist/*",
    # )
    # parser.add_argument(
    #     "--strict",
    #     action="store_true",
    #     default=False,
    #     required=False,
    #     help="Fail on warnings",
    # )

    parsed_args = parser.parse_args(args)

    # TODO
    print('call verify method')


def send_proposal(repo_conn_id, cred_def_id):
    vsw_repo_url = f'{repo_url_host}/present-proof/send-proposal'
    res = requests.post(vsw_repo_url, json={
        {
            "connection_id": repo_conn_id,
            "auto_present": True,
            "comment": "Felix Test",  # TODO
            "presentation_proposal": {
                "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/present-proof/1.0/presentation-preview",
                "attributes": [
                    {
                        "name": "developer-did",
                        "cred_def_id": cred_def_id,
                        "value": "martini",
                        "referent": "0"
                    },
                    {
                        "name": "software-version",
                        "cred_def_id": cred_def_id,
                        "value": "martini",
                        "referent": "1"
                    },
                    {
                        "name": "software-name",
                        "cred_def_id": cred_def_id,
                        "value": "martini",
                        "referent": "2"
                    },
                    {
                        "name": "software-did",
                        "cred_def_id": cred_def_id,
                        "value": "martini",
                        "referent": "3"
                    }
                ],
                "predicates": [
                    {
                        "name": "developer-did",
                        "cred_def_id": cred_def_id,
                        "predicate": ">=",
                        "threshold": 0
                    }
                ]
            },
            "trace": False
        }
    })
    print(json.loads(res.text))
