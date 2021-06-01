import configparser
import hashlib
import shutil
import tempfile
import urllib
from configparser import RawConfigParser
from pathlib import Path
from typing import Union

from multibase import encode
from multicodec import add_prefix

from vsw.log import Log

logger = Log(__name__).logger


class Constant:
    PORT_NUMBER = 49111
    TIMEOUT = 30
    NOT_RUNNING_MSG = "vsw is not running"


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


def save_endpoint(sub_domain):
    endpoint = f'https://{sub_domain}.loca.lt'  # will change to the custom domain name
    parser = configparser.ConfigParser()
    parser.read(Path(__file__).parent.joinpath("conf/vsw.ini").resolve())
    parser.set("vsw-agent", "endpoint", endpoint)
    with open(Path(__file__).parent.joinpath("conf/vsw.ini").resolve(), 'w') as configfile:
        parser.write(configfile)
    return endpoint


def set_port_number(args_ports):
    parser = configparser.ConfigParser()
    parser.read(Path(__file__).parent.joinpath("conf/vsw.ini").resolve())
    ports = args_ports.split(",")
    if len(ports) != 3:
        raise ValueError("The ports format should be (endpoint_port,admin_port,webhook_port)")
    parser.set("vsw-agent", "inbound_transport_port", ports[0])
    parser.set("vsw-agent", "endpoint", f'http://127.0.0.1:{ports[0]}/')
    parser.set("vsw-agent", "admin_port", ports[1])
    parser.set("vsw-agent", "webhook_port", ports[2])
    parser.set("vsw-agent", "webhook_url", f'http://127.0.0.1:{ports[2]}/webhooks')
    with open(Path(__file__).parent.joinpath("conf/vsw.ini").resolve(), 'w') as configfile:
        parser.write(configfile)


def get_repo_host():
    config_path = Path(__file__).parent.joinpath("conf/vsw.ini").resolve()
    config_reader = ConfigReader(config_path)
    config_dict = config_reader.to_dict('vsw-repo')
    return config_dict


def get_vsw_agent():
    config_path = Path(__file__).parent.joinpath("conf/vsw.ini").resolve()
    config_reader = ConfigReader(config_path)
    config_dict = config_reader.to_dict('vsw-agent')
    return config_dict


def get_sovrin():
    config_path = Path(__file__).parent.joinpath("conf/vsw.ini").resolve()
    config_reader = ConfigReader(config_path)
    config_dict = config_reader.to_dict('sovrin')
    return config_dict


def get_tails_server():
    config_path = Path(__file__).parent.joinpath("conf/vsw.ini").resolve()
    config_reader = ConfigReader(config_path)
    config_dict = config_reader.to_dict('tails-server')
    return config_dict


def generate_digest(url):
    if url is None:
        return ""
    with urllib.request.urlopen(url) as response:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            shutil.copyfileobj(response, tmp_file)
            sha256_hash = hashlib.sha256()
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: tmp_file.file.read(4096), b""):
                sha256_hash.update(byte_block)
            hex_digest = sha256_hash.hexdigest()
            multi_codec = add_prefix('sha2-256', str.encode(hex_digest))
            base58btc = encode('base58btc', multi_codec)
            digest = base58btc.decode()

            return digest
