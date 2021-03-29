import json
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


def test_publish():
    publish.send_proposal(repo_conn_id, "6NQ84mYSmD5FiBC1fVYiL7", "Fly", "0.1.0", "12121212",
                          "http://images.pccoo.cn/bar/2012426/20124261343081s.jpg",
                  "", "")

# 1 Repo Holder sends a proposal to the issuer (issuer receives proposal)
def test_send_proposal():
    print('#1 Repo Holder sends a proposal to the issuer (issuer receives proposal)')
    vsw_repo_url = f'{repo_url_host}/issue-credential/send-proposal'
    res = requests.post(vsw_repo_url, json={
        # "schema_id": "CqdPVBFnDs6uUzrrd8Prmw:2:software-certificate:1.0",  # TODO
        "comment": "Felix Debug Test",
        # "schema_issuer_did": "WgWxqztrNooG92RXvxSTWv",  # TODO
        "auto_remove": False,
        "trace": True,
        # "cred_def_id": "CqdPVBFnDs6uUzrrd8Prmw:3:CL:2918:default",  # TODO
        "connection_id": repo_conn_id,
        # "schema_name": "preferences",
        # "schema_version": "1.0",
        "credential_proposal": {
            "@type": "did:sov:CqdPVBFnDs6uUzrrd8Prmw;spec/issue-credential/1.0/credential-preview",
            "attributes": [{
                "name": "developer-did",
                "value": "M4yVd8vfSE7qo9PeRG5ArM"  # TODO
            },
                {
                    "name": "software-version",
                    "value": "1.0"
                },
                {
                    "name": "software-name",
                    "value": "HappyBirds"
                },
                {
                    "name": "software-did",
                    "value": "80da584735d94d5948bc5b450e6fdb837afae78d2a27682d095e9b9b576cf95e"
                },
                {
                    "name": "url",
                    "value": "http://images.pccoo.cn/bar/2012426/20124261343081s.jpg"
                },
                {
                    "name": "alt-url1",
                    "value": ""
                },
                {
                    "name": "alt-url2",
                    "value": ""
                },
                {
                    "name": "hash",
                    "value": "digest"
                },
                {
                    "name": "alt-hash",
                    "value": "digest"
                }
            ]
        },
        # "issuer_did": "WgWxqztrNooG92RXvxSTWv"  # TODO
    })
    print(json.loads(res.text))


# 2 Issuer sends an offer to the holder based on the proposal (holder receives offer)
def test_send_offer():
    print('#2 Issuer sends an offer to the holder based on the proposal (holder receives offer)')
    url = f'{vsw_url_host}/issue-credential/send-offer'
    res = requests.post(url, json={
        "comment": "Felix Test",
        "auto_remove": True,
        "auto_issue": True,
        "trace": False,
        "cred_def_id": credential_definition_id,
        "connection_id": local_conn_id,
        "credential_preview": {
            "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview",
            "attributes": [{
                "name": "developer-did",
                "value": "M4yVd8vfSE7qo9PeRG5ArM"  # TODO
            },
                {
                    "name": "software-version",
                    "value": "1.0"
                },
                {
                    "name": "software-name",
                    "value": "Felix Test"
                },
                {
                    "name": "software-did",
                    "value": "80da584735d94d5948bc5b450e6fdb837afae78d2a27682d095e9b9b576cf95e"
                }
            ]
        }
    })
    print(json.loads(res.text))


# 3 Issuer sends an offer to the holder based on the proposal (holder receives offer)
def test_send_offer_cred_ex_id():
    print('#3 Issuer sends an offer to the holder based on the proposal (holder receives offer)')
    url = f'{vsw_url_host}/issue-credential/records/{cred_ex_id}/send-proposal'
    res = requests.post(url)
    print(json.loads(res.text))


# 4 Repo-Holder sends a request to the issuer (issuer receives request)
def test_send_request():
    print('#4 Repo-Holder sends a request to the issuer (issuer receives request)')
    url = f'{repo_url_host}/issue-credential/records/{cred_ex_id}/send-request'
    res = requests.post(url)
    print(json.loads(res.text))


# 5 Issuer sends credential to holder (holder receives credentials)
def test_issue(cred_ex_id):
    print('#5 Issuer sends credential to holder (holder receives credentials)')
    url = f'{vsw_url_host}/issue-credential/records/{cred_ex_id}/issue'
    res = requests.post(url, json={
        "comment": "Felix Test"
    })
    print(json.loads(res.text))


# 6 Repo Holder stores credential (holder sends acknowledge to issuer)
def test_store(cred_ex_id, credential_id):
    print('#6 Repo Holder stores credential (holder sends acknowledge to issuer)')
    url = f'{repo_url_host}/issue-credential/records/{cred_ex_id}/store'
    res = requests.post(url, json={
        "credential_id": credential_id
    })
    print(json.loads(res.text))


# automatically
def create():
    url = f'{vsw_url_host}/issue-credential/create'
    res = requests.post(url, json={
        "cred_def_id": "WgWxqztrNooG92RXvxSTWv:3:CL:20:tag",
        "schema_issuer_did": "WgWxqztrNooG92RXvxSTWv",
        "auto_remove": True,
        "comment": "string",
        "issuer_did": "WgWxqztrNooG92RXvxSTWv",
        "credential_proposal": {
            "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview",
            "attributes": [{
                "name": "developer-did",
                "value": "M4yVd8vfSE7qo9PeRG5ArM"  # TODO
            },
                {
                    "name": "software-version",
                    "value": "1.0"
                },
                {
                    "name": "software-name",
                    "value": "Felix Test"
                },
                {
                    "name": "software-did",
                    "value": "80da584735d94d5948bc5b450e6fdb837afae78d2a27682d095e9b9b576cf95e"
                }
            ]
        },
        "schema_id": "WgWxqztrNooG92RXvxSTWv:2:schema_name:1.0",
        "schema_name": "preferences",
        "trace": False,
        "schema_version": "1.0"
    })
    print(res)


# automatically
def test_send():
    url = f'{vsw_url_host}/issue-credential/send'
    res = requests.post(url, json={
        "cred_def_id": "NVAbHh9DuKxFA8URWVp7Rb:3:CL:2911:default",
        "schema_issuer_did": "NVAbHh9DuKxFA8URWVp7Rb",  # TODO
        "auto_remove": True,
        "comment": "Felix Test",
        "issuer_did": "NVAbHh9DuKxFA8URWVp7Rb",  # TODO
        "credential_proposal": {
            "@type": "did:sov:BzCbsNYhMrjHiqZDTUASHg;spec/issue-credential/1.0/credential-preview",
            "attributes": [{
                "name": "developer-did",
                "value": "M4yVd8vfSE7qo9PeRG5ArM"  # TODO
            },
                {
                    "name": "software-version",
                    "value": "1.0"
                },
                {
                    "name": "software-name",
                    "value": "Felix Test"
                },
                {
                    "name": "software-did",
                    "value": "80da584735d94d5948bc5b450e6fdb837afae78d2a27682d095e9b9b576cf95e"
                }
            ]
        },
        "schema_id": "NVAbHh9DuKxFA8URWVp7Rb:2:software-certificate:1.0",
        "schema_name": "software-certificate",
        "trace": False,
        "connection_id": "08e4560d-89b0-4131-bf8b-a6e0dae9a62e",
        "schema_version": "1.0"
    })
    print(json.loads(res.text))


def test_get_public_did():
    publish.get_public_did()


def test_get_credentail_records():
    publish.get_credential_record("d073e5f4-b825-4cae-8d65-1ec62ba4d448")


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
