import argparse
from typing import List


def main(args: List[str]) -> bool:
    print('Usage:')
    print('vsw <command> [options]')
    print('')
    print('')
    print('Commands:')
    print('init               Initialize for the first time, or restarts. If this is the first, it inits sqlite, creates a wallet, a new DID, connects with the blockchain, connects with vsw-repo (hello-like exchange), and prints out new DID/verkey. If it is a restart, it re-initializes with the existing wallet and blockchain and vsw-repo. The controller+agent will run in the background as daemons')
    print('register           Register credential definitions of a schema')
    print('publish            Publish a sw pkg and its credential to the vsw-repo, or a credential for an existing sw pkg')
    print('verify             Verify a sw pkg credential - if passes, download the sw pkg')
    print('list               List of various useful info')
    print('exit               This will terminate both controller and agent and smoothly exit')
    print('')
    print('')
    print('General Options:')
    print('-h, --help         Show help')