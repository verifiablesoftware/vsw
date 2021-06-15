import json

import requests

import vsw

from vsw.commands import init
from vsw.commands import list
from tests import test_publish

vsw_config = vsw.utils.get_vsw_agent()


def test_do_credential_definition():
    init.do_credential_definition("softwareCertificate")


def test_connection_repo():
    # create connection with repo
    init.connection_repo()


def test_check_credential_definition():
    init.check_credential_definition("UyDtaEFuTySAV9VZDykHkh:2:softwareCertificate:0.3")


def test_list_schema():
    list.get_schema(vsw_config)
    list.get_credential_definition(vsw_config)


def test_remove_all_connection():
    schema_url = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}/connections'
    response = requests.get(schema_url)
    results = json.loads(response.text)["results"]
    for result in results:
        schema_url = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}/connections/{result["connection_id"]}/remove'
        requests.post(schema_url)
        print(f"Remove connection id: {result['connection_id']}")


# clean all history data
def test_clean_history_data():
    test_remove_all_connection()
    test_publish.test_clean_all_records()


def test_api_key():
    schema_url = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}/status/ready'
    custom_header = {"x-api-key": vsw_config.get("seed")}
    response = requests.get(schema_url, headers=custom_header)
    results = json.loads(response.text)
    print(results)