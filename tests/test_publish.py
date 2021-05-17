import json
from urllib.parse import urljoin

import requests

from vsw.commands import publish
import vsw

vsw_config = vsw.utils.get_vsw_agent()
vsw_repo_config = vsw.utils.get_repo_host()
vsw_url_host = f'http://{vsw_config.get("admin_host")}:{vsw_config.get("admin_port")}'
repo_url_host = vsw_repo_config.get("host")
local_conn_id = "45c40084-edcb-42e9-ab39-6b7bf9c0cb2f"
repo_conn_id = "569ee27c-17b3-4629-ad40-ef2a4c6fb653"
credential_definition_id = "CqdPVBFnDs6uUzrrd8Prmw:3:CL:2950:default"
cred_ex_id = "151c7bfb-a672-4507-99eb-aabd9bb3a494"


def test_parse_args():
    publish.parse_args()


def test_generate_software_did():
    url = "https://files.pythonhosted.org/packages/9d/5e/1420669f433ca41315685fb9bdc6fe2869a6e525cb6483805f3f4c9d61ad/excel-1.0.0.tar.gz"
    publish.generate_software_did("UyDtaEFuTySAV9VZDykHkh", "Mac", "1.0.0", url)


def test_get_credential_definition_id():
    credential_definition_id = publish.get_credential_definition_id()
    print(credential_definition_id)


def test_version():
    publish.check_version("aaa")


def test_write_did():
    ledger_res = requests.post(urljoin(vsw_url_host, f"/ledger/register-nym?did=8KRWamyZXjF6MqywP7WZL2&verkey=4zKqQqhwByTYxtG9b6X9th3tGuzvb8smFMLdhXq9jS7h"))
    write_did_ledger_res = json.loads(ledger_res.text)
    print(write_did_ledger_res)


def test_publish():
    with open("/Users/Felix/development/vsw-workspace/vsw/dist/publish.json") as json_file:
        data = json.load(json_file)
        publish.issue_credential(data)


def test_get_public_did():
    publish.get_public_did()


def test_get_credentail_records():
    publish.get_credential_record("d073e5f4-b825-4cae-8d65-1ec62ba4d448")


def test_get_repo_connection():
    publish.get_repo_connection()


def test_clean_all_records():
    local = f'{vsw_url_host}/issue-credential/records'
    response = requests.get(local)
    results = json.loads(response.text)["results"]
    if len(results) > 0:
        for result in results:
            credential_exchange_id = result["credential_exchange_id"]
            url = f'{vsw_url_host}/issue-credential/records/{credential_exchange_id}/remove'
            res = requests.post(url)
            print(f'Removed credential records {credential_exchange_id}')

    local = f'{vsw_url_host}/present-proof/records'
    response = requests.get(local)
    results = json.loads(response.text)["results"]
    if len(results) > 0:
        for result in results:
            presentation_exchange_id = result["presentation_exchange_id"]
            url = f'{vsw_url_host}/present-proof/records/{presentation_exchange_id}/remove'
            res = requests.post(url)
            print(f'Removed present proof records {presentation_exchange_id}')

    repo = f'{repo_url_host}/issue-credential/records'
    response = requests.get(repo)
    results = json.loads(response.text)["results"]
    if len(results) > 0:
        for result in results:
            credential_exchange_id = result["credential_exchange_id"]
            url = f'{repo_url_host}/issue-credential/records/{credential_exchange_id}/remove'
            res = requests.post(url)
            print(f'Removed credential records {credential_exchange_id}')

    repo = f'{repo_url_host}/present-proof/records'
    response = requests.get(repo)
    results = json.loads(response.text)["results"]
    if len(results) > 0:
        for result in results:
            presentation_exchange_id = result["presentation_exchange_id"]
            url = f'{repo_url_host}/present-proof/records/{presentation_exchange_id}/remove'
            res = requests.post(url)
            print(f'Removed present proof records {presentation_exchange_id}')

    # Remove Credential
    repo = f'{repo_url_host}/credentials?count={100}'
    response = requests.get(repo)
    results = json.loads(response.text)["results"]
    if len(results) > 0:
        for result in results:
            referent = result["referent"]
            url = f'{repo_url_host}/credential/{referent}/remove'
            requests.post(url)
            print(f'Removed referent {referent}')
