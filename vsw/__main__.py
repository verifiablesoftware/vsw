#!/usr/bin/env python3
import sys
from typing import Any

from vsw import cli


def main() -> Any:
    cli.dispatch(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
