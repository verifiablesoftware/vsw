import json

from vsw.commands import verify


def test_main():
    verify.execute("/Users/Felix/development/vsw-workspace/vsw/dist/verify.json")


def test_retrieve_results():
    verify.retrieve_result("01168b93-ea56-452e-b7ca-e14d4be1bfca")


def test_check_credential():
    verify.check_credential("1234", "python")


def test_get_software_credential():
    with open("/Users/Felix/development/vsw-workspace/vsw/dist/verify.json") as json_file:
        data = json.load(json_file)
        credential = verify.get_test_credential(data)
        print(credential)
        soft_credential = verify.get_software_credential(data)
        print(soft_credential)