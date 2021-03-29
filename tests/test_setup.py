from vsw.commands import setup


def test_start_agent():
    setup.start_agent("test9", "test9")


def test_get_seed():
    setup.get_seed()


def test_provision():
    setup.provision("tr", "tr")