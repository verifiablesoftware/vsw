from vsw.commands import setup

def test_retrieve_DID():
    setup.retrieve_DID()

def test_start_agent():
    setup.start_agent("felix", "felix")

def test_get_seed():
    setup.get_seed()

def test_provision():
    setup.provision("tr", "tr")

def test_connection_repo():
    setup.connection_repo()