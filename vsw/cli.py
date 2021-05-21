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
    parser.add_argument("-v", "--version", action="version",
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
