import json

import requests

import vsw

from vsw.commands import init
from vsw.commands import list

vsw_config = vsw.utils.get_vsw_agent()
vsw_repo_config = vsw.utils.get_repo_host()

def test_do_schema():
    init.do_schema("software-certificate")


def test_publish():
    # create connection with repo
    init.connection_repo()


def test_remove_connection():
    schema_url = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}/connections/cb640af3-8d6c-4d2c-81c5-6dbb5ec66e7c/remove'
    response = requests.post(schema_url)
    print(json.loads(response.text))

    vsw_repo_url = f'{vsw_repo_config.get("host")}/connections/5472fe5e-cccd-45bd-98c7-6630aa1ac8fc/remove'
    response2 = requests.post(vsw_repo_url)
    print(json.loads(response2.text))


def test_list_schema():
    list.get_schema(vsw_config)
    list.get_credential_definition(vsw_config)

