from vsw.commands import verify


def test_main():
    verify.execute("aaa", "1.0.0", "2L1pxZWRw91c5txLXCsNpz", "https://files.pythonhosted.org/packages/9d/5e/1420669f433ca41315685fb9bdc6fe2869a6e525cb6483805f3f4c9d61ad/excel-1.0.0.tar.gz", None)


def test_retrieve_results():
    verify.retrieve_result("01168b93-ea56-452e-b7ca-e14d4be1bfca")


def test_check_credential():
    verify.check_credential("1234", "python")