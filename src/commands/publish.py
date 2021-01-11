import argparse
from typing import List


def main(args: List[str]) -> bool:
    parser = argparse.ArgumentParser(prog="vsw check")
    # parser.add_argument(
    #     "dists",
    #     nargs="+",
    #     metavar="dist",
    #     help="The distribution files to check, usually dist/*",
    # )
    # parser.add_argument(
    #     "--strict",
    #     action="store_true",
    #     default=False,
    #     required=False,
    #     help="Fail on warnings",
    # )

    parsed_args = parser.parse_args(args)

    # TODO
    print('call publish method')
