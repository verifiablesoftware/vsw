from typing import List


def main(args: List[str]) -> bool:
    print('Usage:')
    print('vsw <command> [options]')
    print('')
    print('')
    print('Commands:')
    print('init               Initialize schema, connection for the first time.')
    print('publish            Publish a software credential to the vsw-repo')
    print('verify             Verify if a software credential is correct')
    print('list               List of various useful info')
    print('exit               This will terminate aca-py agent')
    print('')
    print('')
    print('General Options:')
    print('-h, --help         Show help')