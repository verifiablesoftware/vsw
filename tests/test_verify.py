from vsw.commands import verify


def test_main():
    verify.execute("test9", "6NQ84mYSmD5FiBC1fVYiL7", "https://files.pythonhosted.org/packages/75/90/3fe7d9bf7b5794cdd344682fa2cbc050a4d8f9d86e9d56d30538b15aa461/urllib-3-0.1.tar.gz", "software-certificate", None)


def test_retrieve_results():
    verify.retrieve_result("01168b93-ea56-452e-b7ca-e14d4be1bfca")


def test_check_credential():
    verify.check_credential("1234", "python")