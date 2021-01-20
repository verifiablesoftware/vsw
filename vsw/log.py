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
        log_dir = log_dir or Path(__file__).parent.parent.resolve()
        if not os.path.exists(str(log_dir)+"/logs/"):
            os.makedirs(str(log_dir)+"/logs/")
        file_path = Path(log_dir).joinpath(f"logs/{name}.log").resolve()

        file_handler = logging.FileHandler(file_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

