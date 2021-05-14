import uuid

from vsw import utils

from vsw.commands import setup


def test_start_agent():
    # sub_domain = uuid.uuid4().hex
    # utils.save_endpoint(sub_domain)
    # setup.start_local_tunnel(sub_domain)
    setup.start_controller()
    setup.start_agent("publisher", "publisher", False)


def test_provision():
    setup.provision("felix", "felix")


def test_get_seed():
    setup.get_seed()


def test_provision():
    setup.provision("tr", "tr")