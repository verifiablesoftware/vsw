from vsw.commands import setup
from vsw import utils


def test_retrieve_DID():
    setup.retrieve_DID()


def test_start_agent():
    endpoint = utils.save_endpoint(None)
    setup.start_agent("default", "default", endpoint)


def test_get_seed():
    setup.get_seed()


def test_provision():
    setup.provision("tr", "tr")


def test_connection_repo():
    setup.connection_repo()


def test_save_specified_port():
    utils.save_ports("9021", "9022", "9023")