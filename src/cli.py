# Copyright 2013 Donald Stufft
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import argparse
from typing import Any, Dict, List

import pkg_resources

args = argparse.Namespace()


def _registered_commands(
    group: str = "vsw.registered_commands",
) -> Dict[str, pkg_resources.EntryPoint]:
    registered_commands = pkg_resources.iter_entry_points(group=group)
    return {c.name: c for c in registered_commands}

def dispatch(argv: List[str]) -> Any:
    registered_commands = _registered_commands()
    parser = argparse.ArgumentParser(prog="vsw")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s version {}".format(pkg_resources.require("vsw")[0].version),
    )
    parser.add_argument(
        "command",
        choices=registered_commands.keys(),
    )
    parser.add_argument(
        "args",
        help=argparse.SUPPRESS,
        nargs=argparse.REMAINDER,
    )

    parser.parse_args(argv, namespace=args)

    main = registered_commands[args.command].load()

    return main(args.args)
