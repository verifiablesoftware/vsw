from vsw.commands import verify


def test_main():
    verify.execute("FF", "2mKdrR6QpmqNp8eHnkCogV", "http://images.pccoo.cn/bar/2012426/20124261343081s.jpg")


def test_retrieve_results():
    verify.retrieve_result("01168b93-ea56-452e-b7ca-e14d4be1bfca")


def test_check_credential():
    verify.check_credential("1234", "python")