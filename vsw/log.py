import logging
import os
import sys
from pathlib import Path


class Log:

    def __init__(self, name: str = 'vsw', log_dir: str = None, level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False

        formatter = logging.Formatter(
            fmt="%(asctime)s %(name)s %(levelname)s %(pathname)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        log_dir = log_dir or Path(os.path.expanduser('~'))
        aries_config_path = str(Path(__file__).parent.joinpath("conf/aries_logging_config.ini").resolve())
        if not os.path.exists(str(log_dir)+"/vsw_logs/"):
            os.makedirs(str(log_dir)+"/vsw_logs/")
        file_path = Path(log_dir).joinpath(f"vsw_logs/vsw.log").resolve()
        aries_log_file = str(Path(log_dir).joinpath("vsw_logs/aries-cloud-agent.log").resolve())

        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)
        aries_handler = logging.FileHandler(aries_config_path)
        aries_log_handler = logging.FileHandler(aries_log_file)
        streams = [file_handler.stream, stream_handler.stream, aries_handler.stream, aries_log_handler.stream]
        self.logger.streams = streams
        self.logger.aries_config_path = aries_config_path
        self.logger.aries_log_file = aries_log_file


