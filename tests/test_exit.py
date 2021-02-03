import vsw.commands.exit
import os
from vsw.utils import get_vsw_agent

def test_kill():
    vsw.commands.exit.kill()

def test_kill2():
    configuration = get_vsw_agent()
    result = os.system(f'kill $(lsof -t -i:{configuration.get("admin_port")})')
    print(result)