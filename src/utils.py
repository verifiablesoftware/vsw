from configparser import RawConfigParser
from pathlib import Path
from typing import Union
from src import env
from src.log import Log

logger = Log().logger


class ConfigReader:

    def __init__(self, file_path: Union[str, Path]):
        self.configparser = RawConfigParser()
        self.configparser.read(file_path)

    def to_dict(self, section: str = None):
        if section is None:
            configs = {}
            for sec in self.configparser.sections():
                configs[sec] = dict(self.configparser.items(sec))
            return configs
        else:
            configs = self.configparser.items(section)
            return dict(configs)


def get_repo_host():
    environment = env.getenv()
    config_path = Path(__file__).parent.joinpath("conf/vsw-" + environment + ".ini").resolve()
    config_reader = ConfigReader(config_path)
    config_dict = config_reader.to_dict('vsw-repo')
    repo_endpoint = config_dict.get("host")
    logger.info("repo_endpoint: " + repo_endpoint)
    return repo_endpoint


def get_vsw_agent_host():
    environment = env.getenv()
    config_path = Path(__file__).parent.joinpath("conf/vsw-" + environment + ".ini").resolve()
    config_reader = ConfigReader(config_path)
    config_dict = config_reader.to_dict('vsw-agent')
    vsw_agent_endpoint = config_dict.get("host")
    logger.info("vsw_agent_endpoint: " + vsw_agent_endpoint)
    return vsw_agent_endpoint
