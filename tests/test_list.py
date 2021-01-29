from vsw.commands.list import get_connections
from vsw.commands.list import get_wallet
from vsw.commands.list import get_schema
from vsw.utils import get_vsw_agent


def test_get_connections():
    vsw_config = get_vsw_agent()
    get_connections(vsw_config)


def test_get_wallet():
    vsw_config = get_vsw_agent()
    get_wallet(vsw_config)


def test_get_schema():
    vsw_config = get_vsw_agent()
    get_schema(vsw_config)