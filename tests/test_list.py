from vsw.commands.list import get_connections
from vsw.commands.list import get_wallet
from vsw.commands.list import get_schema
from vsw.commands.list import get_credential_definition
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


def test_get_credential_definition():
    vsw_config = get_vsw_agent()
    get_credential_definition(vsw_config)