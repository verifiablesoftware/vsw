import configparser
import hashlib
import shutil
import tempfile
import urllib
from configparser import RawConfigParser
from pathlib import Path
from typing import Union

from multicodec import add_prefix
from multibase import encode

from vsw.log import Log

logger = Log(__name__).logger


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


def save_endpoint(endpoint):
    if endpoint:
        parser = configparser.ConfigParser()
        parser.read(Path(__file__).parent.joinpath("conf/vsw.ini").resolve())
        parser.set("vsw-agent", "endpoint", endpoint)
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


def generate_digest(software_url):
    with urllib.request.urlopen(software_url) as response:
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
            print(f'digest: {digest}')

            return digest
