import pkg_resources
import pretend

from src import cli
from src.commands import publish

class Resouce:
    def __init__(self, version):
        self.version = version

def mock_resove(reqs, env, installer, extra):
    return None
def test_dispatch(monkeypatch):
    demoUrl = "https://6665-felix-dev-z5nuv-1258995345.tcb.qcloud.la/7c3e03d0-54a8-11eb-99ce-61c802d429b9.jpg"
    replaced_main = pretend.call_recorder(lambda args: None)
    monkeypatch.setattr(publish, "main", replaced_main)
    monkeypatch.setattr(pkg_resources, "require", lambda x: [Resouce('1.0.0')])
    monkeypatch.setattr(pkg_resources.working_set, "resolve", mock_resove)

    cli.dispatch(["publish", demoUrl])

    assert replaced_main.calls == [pretend.call([demoUrl])]
