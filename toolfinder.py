#!/usr/bin/env python3
import argparse
import json
import requests

import DataAccess.DataBase
import globals
from Repository import EDAMConnector, BioToolsConnector


def main():
    # read arguments from command line
    parser = argparse.ArgumentParser(prog="script")

    subparsers = parser.add_subparsers(dest="command")

    # subcommand for configuration customization
    # config_parser = subparsers.add_parser('config')
    # config_parser.add_argument('key', required=True)
    # config_parser.add_argument('value', required=True)

    # subcommand for database initialization
    dbinit_parser = subparsers.add_parser('db-init')
    dbinit_parser.add_argument('--reset', '-r', action="store_true", dest="reset_db", help="If set, the database will be reset completely")

    # subcommand for retrieval of definitions
    retrieve_parser = subparsers.add_parser('load')
    retrieve_parser.add_argument('--all', '-a', action="store_true", dest="load_all",
                                 help="Retrieve all definitions (EDAM, biotools, synbiotools)")
    retrieve_parser.add_argument('definition', nargs="?", choices=["EDAM", "biotools", "synbiotools"])
    args = parser.parse_args()

    # validate arguments and dispatch action

    # dispatch action
    if args.command == 'load':
        if not validate_load_args(args):
            retrieve_parser.print_help()
            return -1
        dispatch_load(args.load_all, args.definition)
    elif args.command == 'db-init':

        globals.db_connection.create_db()
    elif args.command == 'predecessor':
        print("Not implemented yet")
    elif args.command == 'replacement':
        print("Not implemented yet")
    else:
        print(f"Invalid command {args.command}")


def dispatch_load(load_all, definition):
    if load_all:
        EDAMConnector.load()
        BioToolsConnector.load()
        # rest of the definitions here
        return
    dispatch_map = {
        "EDAM": EDAMConnector.load,
        "biotools": BioToolsConnector.load
    }
    dispatch_map[definition]()


def validate_load_args(args):
    # load command
    if not args.load_all and args.definition is None:
        print("If --all is not set, the definition to load is required.")
        return False
    return True


if __name__ == '__main__':
    main()
