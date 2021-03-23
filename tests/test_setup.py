from vsw.commands import setup


def test_start_agent():
    setup.start_agent("default", "default")


def test_get_seed():
    setup.get_seed()


def test_provision():
    setup.provision("tr", "tr")