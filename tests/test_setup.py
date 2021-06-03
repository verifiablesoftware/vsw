import uuid

from vsw import utils

from vsw.commands import setup


def test_start_agent():
    # sub_domain = uuid.uuid4().hex
    # utils.save_endpoint(sub_domain)
    # setup.start_local_tunnel(sub_domain)
    setup.start_controller()
    setup.start_agent("publisher", "publisher", "d131cef5c1e74b5c83e486c55186ce3a")


def test_provision():
    setup.provision("felix", "felix")


def test_get_seed():
    setup.get_seed("w1")


def test_provision():
    setup.provision("wallet1", "wallet1")